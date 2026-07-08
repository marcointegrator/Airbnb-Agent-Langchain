from pathlib import Path

from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
import os

load_dotenv(Path(__file__).parent.parent.parent / ".env")
HOSPITABLE_MCP_URL = "https://mcp.hospitable.com/mcp"

ALLOWED_TOOLS = {
    "get-property-calendar",
    "search-properties",
    "create-quote",
    "send-reservation-message",
    "get-reservation-messages",
    "get-reservation",
    "get-reservations",
    "get-properties",
    "get-property",
}


def _build_client() -> MultiServerMCPClient:
    token = os.getenv("HOSPITABLE_MCP_TOKEN")
    if not token:
        raise RuntimeError(
            "HOSPITABLE_MCP_TOKEN mancante nel .env. "
        )

    return MultiServerMCPClient(
        {
            "hospitable": {
                "transport": "streamable_http",
                "url": HOSPITABLE_MCP_URL,
                "headers": {"Authorization": f"Bearer {token}"},
            }
        }
    )


async def get_hospitable_tools(only_allowed: bool = True):
    """Carica i tool dal server MCP di Hospitable e li converte in tool LangChain.

    only_allowed=False restituisce TUTTI i tool (utile per ispezione/debug).
    """
    client = _build_client()
    tools = await client.get_tools()

    if only_allowed:
        tools = [tool for tool in tools if tool.name in ALLOWED_TOOLS]

    return tools
