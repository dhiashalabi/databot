"""LLM Service for handling OpenAI API interactions."""

from datetime import datetime
import json
import logging
from typing import Any
from uuid import UUID

from openai import AsyncOpenAI

from src.config import settings
from src.services.ai_permission_middleware import AIPermissionMiddleware


class LLMService:
	"""Service for handling OpenAI API calls and tool interactions."""

	def __init__(self, ai_permission_middleware: AIPermissionMiddleware | None = None):
		"""Initialize the LLM service with OpenAI client."""
		self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
		self.permission_middleware = ai_permission_middleware

	async def create_chat_completion(
		self,
		messages: list[dict[str, Any]],
		tools: list[dict[str, Any]] | None = None,
		tool_choice: str = "auto",
		model: str | None = None,
		user_id: UUID | None = None,
	) -> Any:
		"""Create a chat completion with optional tools.

		Args:
			messages: list of message objects for the conversation
			tools: list of tools to make available
			tool_choice: how to handle tool calls ("auto", "none", or specific tool)
			model: OpenAI model to use (defaults to settings.OPENAI_MODEL)
			user_id: UUID of the user making the request (for permission checking)

		Returns:
			OpenAI chat completion response

		Raises:
			PermissionError: If user doesn't have permission to use the specified model

		"""
		selected_model = model or settings.OPENAI_MODEL

		if self.permission_middleware and user_id:
			if not await self.permission_middleware.check_model_permission(
				user_id, selected_model, messages
			):
				raise PermissionError(
					f"Permission denied: Cannot use model '{selected_model}'"
				)

		kwargs = {
			"model": selected_model,
			"messages": messages,
		}

		if tools:
			kwargs["tools"] = tools
			kwargs["tool_choice"] = tool_choice

		return await self.client.chat.completions.create(**kwargs)

	async def process_with_tools(
		self,
		user_query: str,
		mcp_tools: list[dict[str, Any]],
		mcp_client,
		model: str | None = None,
		user_id: UUID | None = None,
	) -> dict[str, Any]:
		"""Process a user query with MCP tools.

		Args:
			user_query: The user's natural language query
			mcp_tools: List of MCP tools available
			mcp_client: MCP client instance for tool execution
			model: OpenAI model to use (defaults to settings.OPENAI_MODEL)
			user_id: UUID of the user making the request (for permission checking)

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

		try:
			response = await self.create_chat_completion(
				messages=messages,
				tools=openai_tools,
				tool_choice="auto",
				model=model,
				user_id=user_id,
			)
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
			)
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

		response = {
			"answer": final_response.choices[0].message.content,
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
