"""LLM Service for handling OpenAI API interactions."""

from datetime import datetime
import json
import logging
import time
import traceback
from typing import Any
from uuid import UUID

from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.errors.exceptions import TokenLimitExceeded
from src.services.ai_permission_middleware import AIPermissionMiddleware
from src.services.token_management_service import TokenManagementService


class LLMService:
	"""Service for handling OpenAI API calls and tool interactions."""

	def __init__(
		self,
		ai_permission_middleware: AIPermissionMiddleware | None = None,
		db_session: AsyncSession | None = None,
	):
		"""Initialize the LLM service with OpenAI client."""
		self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
		self.permission_middleware = ai_permission_middleware
		self.db_session = db_session
		self.token_service = TokenManagementService(db_session) if db_session else None
		self.logger = logging.getLogger(__name__)

	async def create_chat_completion(
		self,
		messages: list[dict[str, Any]],
		tools: list[dict[str, Any]] | None = None,
		tool_choice: str = "auto",
		model: str | None = None,
		user_id: UUID | None = None,
		track_usage: bool = True,
		user_query: str | None = None,
	) -> Any:
		"""Create a chat completion with optional tools.

		Args:
			messages: list of message objects for the conversation
			tools: list of tools to make available
			tool_choice: how to handle tool calls ("auto", "none", or specific tool)
			model: OpenAI model to use (defaults to settings.OPENAI_MODEL)
			user_id: UUID of the user making the request (for permission checking)
			track_usage: Whether to track token usage
			user_query: The original user query for logging

		Returns:
			OpenAI chat completion response

		Raises:
			PermissionError: If user doesn't have permission to use the specified model

		"""
		selected_model = model or settings.OPENAI_MODEL
		start_time = time.time()

		if self.token_service and user_id:
			if not await self.token_service.check_user_ai_enabled(user_id):
				raise PermissionError("AI is disabled for this user")

		if self.permission_middleware and user_id:
			if not await self.permission_middleware.check_model_permission(
				user_id, selected_model, messages
			):
				raise PermissionError(
					f"Permission denied: Cannot use model '{selected_model}'"
				)

		if self.token_service and user_id and track_usage:
			estimated_input_tokens = (
				sum(len(str(msg.get("content", ""))) for msg in messages) // 4
			)

			limits_check = await self.token_service.check_token_limits(
				user_id, selected_model, estimated_input_tokens
			)

			if not limits_check["allowed"]:
				raise TokenLimitExceeded(
					message=limits_check["reason"],
					limit_type=limits_check.get("exceeded_periods", ["unknown"])[0]
					if limits_check.get("exceeded_periods")
					else "unknown",
				)

		kwargs = {
			"model": selected_model,
			"messages": messages,
		}

		if tools:
			kwargs["tools"] = tools
			kwargs["tool_choice"] = tool_choice

		try:
			response = await self.client.chat.completions.create(**kwargs)

			if self.token_service and user_id and track_usage:
				response_time_ms = int((time.time() - start_time) * 1000)

				usage = response.usage
				if usage:
					await self.token_service.record_token_usage(
						user_id=user_id,
						model_name=selected_model,
						input_tokens=usage.prompt_tokens,
						output_tokens=usage.completion_tokens,
						request_type="chat",
						user_query=user_query,
						response_summary=response.choices[0].message.content[:500]
						if response.choices
						else None,
						response_time_ms=response_time_ms,
						success=True,
					)

					if user_query:
						try:
							ai_response = (
								response.choices[0].message.content
								if response.choices
								else None
							)
							chat_history = await self.token_service.create_chat_history(
								user_id=user_id,
								user_query=user_query,
								model_used=selected_model,
								ai_response=ai_response,
								response_time_ms=response_time_ms,
								input_tokens=usage.prompt_tokens,
								output_tokens=usage.completion_tokens,
								request_type="chat",
								success=True,
							)
							self.logger.info(
								f"Successfully created chat history with ID: {chat_history.id}"
							)
						except Exception as e:
							self.logger.error(
								f"Failed to create chat history in create_chat_completion: {e}"
							)
							self.logger.error(
								f"Chat history creation traceback: {traceback.format_exc()}"
							)

			return response

		except Exception as e:
			if self.token_service and user_id and track_usage:
				response_time_ms = int((time.time() - start_time) * 1000)

				await self.token_service.record_token_usage(
					user_id=user_id,
					model_name=selected_model,
					input_tokens=0,
					output_tokens=0,
					request_type="chat",
					user_query=user_query,
					response_time_ms=response_time_ms,
					success=False,
					error_message=str(e),
				)

				if user_query:
					try:
						chat_history = await self.token_service.create_chat_history(
							user_id=user_id,
							user_query=user_query,
							model_used=selected_model,
							ai_response=None,
							response_time_ms=response_time_ms,
							input_tokens=0,
							output_tokens=0,
							request_type="chat",
							success=False,
							error_message=str(e),
						)
						self.logger.info(
							f"Created chat history for failed request with ID: {chat_history.id}"
						)
					except Exception as chat_error:
						self.logger.error(
							f"Failed to create chat history for failed request: {chat_error}"
						)
			raise

	async def process_with_tools(
		self,
		user_query: str,
		mcp_tools: list[dict[str, Any]],
		mcp_client,
		model: str | None = None,
		user_id: UUID | None = None,
		session_id: str | None = None,
	) -> dict[str, Any]:
		"""Process a user query with MCP tools.

		Args:
			user_query: The user's natural language query
			mcp_tools: List of MCP tools available
			mcp_client: MCP client instance for tool execution
			model: OpenAI model to use (defaults to settings.OPENAI_MODEL)
			user_id: UUID of the user making the request (for permission and tracking)
			session_id: Optional session ID for conversation tracking

		Returns:
			Dictionary with answer, data, and query

		"""
		current_date = datetime.now().strftime("%Y-%m-%d")
		system_message = f"""You are an AI business analyst with comprehensive MCP tools. Today's date is {current_date}.

Core capabilities: sales analytics, customer analysis, product insights, trend forecasting, anomaly detection, and period comparisons.

For visualization requests ("show me", "create chart", "visualize"), use chart tools:
- create_sales_trend_chart, create_top_products_chart, create_customer_analysis_chart
- create_sales_comparison_chart, create_custom_query_chart

For file requests ("export", "download", "generate report"), use export tools:
- export_sales_to_csv, export_customers_to_csv, export_products_to_excel
- export_sales_report_to_pdf, export_custom_query_to_excel

Guidelines:
- Calculate dates for relative time queries ("last month", "this month")
- Use visualization tools for trend/comparison requests instead of tables only
- Provide specific numbers, percentages, and actionable insights
- Format data as professional markdown tables with proper alignment
- Include totals/averages when appropriate

Table format: | Metric | Value | Change % | with right-aligned numbers."""

		openai_tools = []
		for tool_info in mcp_tools:
			openai_tools.append(
				{
					"type": "function",
					"function": {
						"name": tool_info["name"],
						"description": tool_info["description"],
						"parameters": tool_info["inputSchema"],
					},
				}
			)

		messages = [
			{"role": "system", "content": system_message},
			{"role": "user", "content": user_query},
		]

		start_time = time.time()
		selected_model = model or settings.OPENAI_MODEL
		total_input_tokens = 0
		total_output_tokens = 0

		try:
			response = await self.create_chat_completion(
				messages=messages,
				tools=openai_tools,
				tool_choice="auto",
				model=model,
				user_id=user_id,
				user_query=user_query,
			)

			if response.usage:
				total_input_tokens += response.usage.prompt_tokens
				total_output_tokens += response.usage.completion_tokens
		except TokenLimitExceeded:
			raise
		except Exception as e:
			logger = logging.getLogger(__name__)
			logger.error(f"Failed to create chat completion: {e}")
			return {
				"answer": "I'm experiencing technical difficulties. Please try again in a moment.",
				"data": None,
				"query": user_query,
				"error": "OpenAI API unavailable",
			}

		message = response.choices[0].message
		tool_calls = message.tool_calls

		if not tool_calls:
			return {
				"answer": message.content
				or "I couldn't process your query. Please try rephrasing it.",
				"data": None,
				"query": user_query,
			}

		messages.append(message)
		tool_results = []

		for tool_call in tool_calls:
			function_name = tool_call.function.name
			function_args = json.loads(tool_call.function.arguments)

			try:
				result = await mcp_client.call_tool(function_name, function_args)
				tool_results.append(result)

				messages.append(
					{
						"role": "tool",
						"tool_call_id": tool_call.id,
						"content": json.dumps(result),
					}
				)
			except Exception as e:
				logger = logging.getLogger(__name__)
				logger.error(f"Tool execution failed: {str(e)}")
				raise

		try:
			final_response = await self.create_chat_completion(
				messages=messages,
				model=model,
				user_id=user_id,
				user_query=user_query,
			)

			if final_response.usage:
				total_input_tokens += final_response.usage.prompt_tokens
				total_output_tokens += final_response.usage.completion_tokens
		except TokenLimitExceeded:
			raise
		except Exception as e:
			logger = logging.getLogger(__name__)
			logger.error(f"Failed to generate final response: {e}")
			return {
				"answer": "I've gathered the data you requested, but I'm having trouble generating a complete analysis. Here's what I found:",
				"data": tool_results[0] if len(tool_results) == 1 else tool_results,
				"query": user_query,
				"error": "Response generation failed",
			}

		if len(tool_results) == 1:
			data = tool_results[0]
		else:
			data = tool_results

		files = self._extract_file_info(tool_results)

		ai_response = final_response.choices[0].message.content
		response_time_ms = int((time.time() - start_time) * 1000)

		if self.token_service and user_id:
			try:
				tools_used = (
					[tool_info["name"] for tool_info in mcp_tools]
					if mcp_tools
					else None
				)
				chat_history = await self.token_service.create_chat_history(
					user_id=user_id,
					user_query=user_query,
					model_used=selected_model,
					ai_response=ai_response,
					response_time_ms=response_time_ms,
					input_tokens=total_input_tokens,
					output_tokens=total_output_tokens,
					request_type="mcp_tools",
					tools_used=json.dumps(tools_used) if tools_used else None,
					success=True,
					session_id=session_id,
					conversation_context=json.dumps(
						{"tool_results_count": len(tool_results)}
					),
				)
				self.logger.info(
					f"Successfully created chat history with ID: {chat_history.id}"
				)
			except Exception as e:
				self.logger.error(f"Failed to create chat history: {e}")

				self.logger.error(
					f"Chat history creation traceback: {traceback.format_exc()}"
				)

		response = {
			"answer": ai_response,
			"data": data,
			"query": user_query,
		}

		if files:
			response["files"] = files

		return response

	async def simple_chat_completion(
		self,
		user_query: str,
		system_message: str | None = None,
		model: str | None = None,
	) -> str:
		"""Create a simple chat completion without tools.

		Args:
			user_query: The user's query
			system_message: system message
			model: OpenAI model to use (defaults to settings.OPENAI_MODEL)

		Returns:
			The assistant's response content

		"""
		messages = []

		if system_message:
			messages.append({"role": "system", "content": system_message})

		messages.append({"role": "user", "content": user_query})

		response = await self.create_chat_completion(
			messages=messages,
			model=model,
		)

		return response.choices[0].message.content or "I couldn't process your query."

	def _extract_file_info(
		self, tool_results: list[dict[str, Any]]
	) -> list[dict[str, Any]] | None:
		"""Extract file information from tool results.

		Args:
			tool_results: List of tool execution results

		Returns:
			List of file information if any files were generated, None otherwise
		"""
		files = []

		for result in tool_results:
			if isinstance(result, dict):
				if (result.get("file_url") and result.get("filename")) or (
					result.get("success") is False
					and "export" in str(result.get("message", "")).lower()
				):
					file_info = {
						"url": result.get("file_url"),
						"filename": result.get("filename"),
						"type": self._get_file_type_from_url(
							result.get("file_url", "")
						),
						"success": result.get("success", True),
						"message": result.get("message", ""),
					}

					if "record_count" in result:
						file_info["record_count"] = result["record_count"]
					if "sheets" in result:
						file_info["sheets"] = result["sheets"]
					if "columns" in result:
						file_info["columns"] = result["columns"]
					if "summary" in result:
						file_info["summary"] = result["summary"]

					files.append(file_info)

		return files if files else None

	def _get_file_type_from_url(self, url: str) -> str:
		"""Extract file type from URL.

		Args:
			url: File URL

		Returns:
			File type (csv, pdf, xlsx, etc.)
		"""
		if not url:
			return "unknown"
		if url.endswith(".csv"):
			return "csv"
		elif url.endswith(".pdf"):
			return "pdf"
		elif url.endswith(".xlsx"):
			return "xlsx"
		elif url.endswith(".png"):
			return "png"
		else:
			return "unknown"
