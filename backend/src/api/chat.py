"""Chat API endpoints - AI-powered natural language interface for business data."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_current_active_user
from src.database import get_db
from src.errors.error_handler import ErrorHandler
from src.errors.exceptions import DataBotException, ValidationError
from src.mcp.agent import DataBotAgent
from src.models.user import User
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.permission_service import PermissionService

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
	message: ChatRequest,
	db: AsyncSession = Depends(get_db),
	current_user: User = Depends(get_current_active_user),
):
	"""Chat with AI assistant about your business data.

	This endpoint uses MCP (Model Context Protocol) with AI-powered insights to understand
	your message and provide comprehensive business analytics across all data:
	- Sales data and revenue
	- Customer information and analytics
	- Product catalog and inventory
	- Invoices and payments

	Example Queries:
		Sales:
		- "Compare my sales last month and this month"
		- "What are my top 5 products by revenue?"
		- "Show me sales by category"
		- "Total revenue from online vs in-store sales"

		Customers:
		- "Who are my top 10 customers by spending?"
		- "Show me details for customer John Smith"
		- "List all corporate customers"

		Products:
		- "Which products are low in stock?"
		- "Show me products under $50"

		Invoices:
		- "How many pending invoices do I have?"
		- "Total value of unpaid invoices"
		- "Invoice summary for this month"

	Args:
		query: Natural language query
		db: Database session

	Returns:
		Query response with natural language answer and structured data

	"""
	error_handler = ErrorHandler()

	try:
		permission_service = PermissionService(db)
		if not await permission_service.user_has_permission(current_user.id, "ai.use"):
			raise HTTPException(
				status_code=403, detail="You don't have permission to use AI chat"
			)

		if message.model:
			if not await permission_service.check_ai_model_permission(
				current_user.id, message.model
			):
				raise HTTPException(
					status_code=403,
					detail=f"You don't have permission to use model '{message.model}'",
				)

		agent = DataBotAgent(db)
		result = await agent.process_query(
			message.message, message.model, user_id=current_user.id
		)
		return result
	except HTTPException:
		raise
	except DataBotException as e:
		error_response = error_handler.handle_error(e, {"query": message.message})
		raise HTTPException(
			status_code=400 if isinstance(e, ValidationError) else 500,
			detail=error_response,
		) from e
	except Exception as e:
		error_response = error_handler.handle_error(e, {"query": message.message})
		raise HTTPException(status_code=500, detail=error_response) from e
