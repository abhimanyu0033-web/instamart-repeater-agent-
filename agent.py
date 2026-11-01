import asyncio
import json
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

SWIGGY_IM_ENDPOINT = "https://mcp.swiggy.com/im"

async def test_connection():
    print("1. Loading inventory.json...")
    try:
        with open("inventory.json") as f:
            inventory = json.load(f)
        print(f"Loaded {len(inventory.get('items', []))} repeat items.")
    except Exception as e:
        print(f"Failed to read inventory.json: {e}")
        return

    print(f"\n2. Testing direct HTTP reachability to {SWIGGY_IM_ENDPOINT}...")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Swiggy MCP responds to POST or GET ping
            res = await client.get(SWIGGY_IM_ENDPOINT)
            print(f"Endpoint HTTP Status: {res.status_code}")
        except Exception as e:
            print(f"HTTP ping info: {e}")

    print("\n3. Connecting via MCP Streamable HTTP Client...")
    try:
        async with streamable_http_client(SWIGGY_IM_ENDPOINT) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Successfully initialized Swiggy MCP Session!")

                tools = await session.list_tools()
                print(f"\nFound {len(tools.tools)} Swiggy Instamart Tools:")
                for tool in tools.tools:
                    print(f"  • {tool.name}")
    except Exception as mcp_err:
        print(f"\nMCP Handshake Details: {type(mcp_err).__name__} -> {mcp_err}")

if __name__ == "__main__":
    asyncio.run(test_connection())
