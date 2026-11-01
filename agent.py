import os
import json
import base64
import hashlib
import secrets
import asyncio
import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

SWIGGY_AUTH_URL = "https://mcp.swiggy.com/auth/authorize"
SWIGGY_TOKEN_URL = "https://mcp.swiggy.com/auth/token"
SWIGGY_IM_ENDPOINT = "https://mcp.swiggy.com/im"

def generate_pkce_pair():
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    challenge = base64.urlsafe_b64encode(digest).decode('utf-8').replace('=', '')
    return verifier, challenge

async def main():
    token = os.environ.get("SWIGGY_TOKEN")

    # If no token is present, generate the authorization link
    if not token:
        verifier, challenge = generate_pkce_pair()
        state = secrets.token_hex(8)
        
        # Swiggy MCP local/dev OAuth redirect
        redirect_uri = "http://localhost:8000/callback"
        client_id = "instamart-repeater-agent"

        login_url = (
            f"{SWIGGY_AUTH_URL}?"
            f"response_type=code&"
            f"client_id={client_id}&"
            f"redirect_uri={redirect_uri}&"
            f"code_challenge={challenge}&"
            f"code_challenge_method=S256&"
            f"state={state}&"
            f"scope=mcp:tools"
        )

        print("\n🔑 --- SWIGGY OAUTH LOGIN NEEDED ---")
        print("Because this is running headlessly, open this URL on your phone browser to sign in:")
        print(f"\n{login_url}\n")
        print(f"SAVE THIS VERIFIER: {verifier}")
        print("------------------------------------\n")
        return

    # If token exists, connect to Instamart MCP
    print("✅ Found Swiggy Bearer Token. Connecting to Instamart MCP...")
    headers = {"Authorization": f"Bearer {token}"}
    
    async with streamable_http_client(SWIGGY_IM_ENDPOINT, headers=headers) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Successfully initialized authenticated session!")
            
            # Fetch saved delivery addresses
            addresses = await session.call_tool("get_addresses", arguments={})
            print("\nSaved Addresses:", json.dumps(addresses.data, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
