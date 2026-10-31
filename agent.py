import asyncio
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

SWIGGY_IM_ENDPOINT = "https://mcp.swiggy.com/im"

async def main():
    print("Loading repeat items from inventory.json...")
    with open("inventory.json") as f:
        inventory = json.load(f)
    print(f"Loaded {len(inventory['items'])} items to monitor.")

    print("\nConnecting to Swiggy Instamart MCP server...")
    async with sse_client(SWIGGY_IM_ENDPOINT) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Connected to Swiggy Instamart MCP!")

            # 1. Fetch available tools
            tools_list = await session.list_tools()
            print(f"Total available Instamart tools: {len(tools_list.tools)}")
            for t in tools_list.tools[:5]:
                print(f"  - {t.name}")

            # 2. Check saved delivery addresses
            print("\nFetching saved addresses...")
            try:
                addresses = await session.call_tool("get_addresses", arguments={})
                print("Address Response:", addresses)
            except Exception as e:
                print(f"Address check returned: {e}")

if __name__ == "__main__":
    asyncio.run(main())
