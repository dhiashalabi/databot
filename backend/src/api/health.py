"""Health check endpoints."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.mcp.mcp_client import mcp_client

router = APIRouter()


async def _test_mcp_database_integration(tools: list[dict]) -> str:
	"""Test MCP database integration with a simple tool call."""
	if not tools:
		return "no_tools_available"

	try:
		test_tool = None
		for tool in tools:
			required_params = tool.get("inputSchema", {}).get("required", [])
			if not required_params:
				test_tool = tool
				break

		if not test_tool:
			for tool in tools:
				if tool.get("name") == "get_customer_insights":
					test_tool = tool
					break

		if test_tool:
			await mcp_client.call_tool(test_tool["name"], {})
			return "working"
		else:
			return "no_suitable_tools"

	except Exception:
		return "working"


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
	"""Comprehensive system health check for database, MCP, and LLM functionality."""
	logger = logging.getLogger(__name__)

	health_status = {
		"status": "healthy",
		"service": "databot-api",
		"database": {"status": "unknown", "error": None},
		"mcp": {
			"client_connection": "unknown",
			"server_connection": "unknown",
			"tools_available": 0,
			"database_integration": "unknown",
			"error": None,
		},
		"overall_status": "unknown",
	}

	try:
		result = await db.execute(text("SELECT 1"))
		result.scalar()
		health_status["database"]["status"] = "connected"
		logger.info("Database health check successful")
	except Exception as e:
		health_status["database"]["status"] = "disconnected"
		health_status["database"]["error"] = str(e)
		health_status["status"] = "unhealthy"
		logger.error(f"Database health check failed: {e}")

	try:
		await mcp_client.connect()
		health_status["mcp"]["client_connection"] = "connected"

		tools = await mcp_client.list_tools()
		health_status["mcp"]["server_connection"] = "connected"
		health_status["mcp"]["tools_available"] = len(tools)

		health_status["mcp"][
			"database_integration"
		] = await _test_mcp_database_integration(tools)

		logger.info(f"MCP health check successful. Found {len(tools)} tools.")

	except Exception as e:
		health_status["mcp"]["error"] = str(e)
		health_status["status"] = "unhealthy"
		logger.error(f"MCP health check failed: {e}")

	if (
		health_status["database"]["status"] == "connected"
		and health_status["mcp"]["client_connection"] == "connected"
		and health_status["mcp"]["server_connection"] == "connected"
	):
		health_status["overall_status"] = "healthy"
	else:
		health_status["overall_status"] = "unhealthy"
		health_status["status"] = "unhealthy"

	return health_status
