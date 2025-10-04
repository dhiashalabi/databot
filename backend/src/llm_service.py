"""LLM Service for handling OpenAI API interactions."""

from datetime import datetime
import json
import logging
from typing import Any

from openai import AsyncOpenAI

from src.config import settings


class LLMService:
	"""Service for handling OpenAI API calls and tool interactions."""

	def __init__(self):
		"""Initialize the LLM service with OpenAI client."""
		self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

	async def create_chat_completion(
		self,
		messages: list[dict[str, Any]],
		tools: list[dict[str, Any]] | None = None,
		tool_choice: str = "auto",
		model: str | None = None,
	) -> Any:
		"""Create a chat completion with optional tools.

		Args:
			messages: list of message objects for the conversation
			tools: list of tools to make available
			tool_choice: how to handle tool calls ("auto", "none", or specific tool)
			model: OpenAI model to use (defaults to settings.OPENAI_MODEL)

		Returns:
			OpenAI chat completion response

		"""
		selected_model = model or settings.OPENAI_MODEL

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
	) -> dict[str, Any]:
		"""Process a user query with MCP tools.

		Args:
			user_query: The user's natural language query
			mcp_tools: List of MCP tools available
			mcp_client: MCP client instance for tool execution
			model: OpenAI model to use (defaults to settings.OPENAI_MODEL)

		Returns:
			Dictionary with answer, data, and query

		"""
		current_date = datetime.now().strftime("%Y-%m-%d")
		system_message = f"""You are an advanced AI business analyst with access to comprehensive MCP tools. Today's date is {current_date}.

You have access to enhanced business analytics including:
- Advanced sales analytics with AI-powered insights
- Customer behavior analysis and segmentation
- Product performance analysis with recommendations
- Business trend analysis and forecasting
- Anomaly detection and risk assessment
- Period comparisons with detailed analysis
- Chart Generation and Visualization Tools

When users ask about time periods like "last month" or "this month", calculate the appropriate dates.
Use the available MCP tools to query the database and provide accurate, insightful answers with AI-powered analysis.

For requests involving trends, comparisons, or data visualization (like "show me", "create a chart", "visualize"), ALWAYS use the available chart tools to provide visual representations of the data. The chart tools will generate PNG images that will be displayed in the frontend.

Available chart tools:
- create_sales_trend_chart - For sales trends over time
- create_top_products_chart - For top products by revenue/quantity  
- create_customer_analysis_chart - For customer analysis
- create_sales_comparison_chart - For comparing two time periods
- create_custom_query_chart - For custom SQL-based charts

When a user asks for "trends", "show me sales trends", "visualize data", or similar requests, use these chart tools instead of just returning tabular data.
Always include specific numbers, percentages, trends, and actionable recommendations.
Be proactive in offering relevant insights and business intelligence based on the data.

IMPORTANT: When presenting data, always format it as a well-structured markdown table with:
- Clear, descriptive column headers
- Properly aligned data (numbers right-aligned, text left-aligned)
- Consistent formatting for currency, percentages, and numbers
- Use proper markdown table syntax with pipes (|) and alignment
- Include summary rows when appropriate (totals, averages, etc.)
- Ensure tables are readable and professional

Example format:
| Metric | Value | Change | Change % |
|--------|-------|--------|----------|
| Sales  | $1,234| +$100  | +8.8%    |

Return the data from the database as a properly formatted markdown table.
"""

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

		return {
			"answer": final_response.choices[0].message.content,
			"data": data,
			"query": user_query,
		}

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
