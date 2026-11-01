import os
import sys
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
REDIRECT_URI = "http://localhost:8000/callback"

def generate_pkce_pair():
    verifier = secrets.token_urlsafe(32)
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    challenge = base64.urlsafe_b64encode(digest).decode('utf-8').replace('=', '')
    return verifier, challenge

async def main():
    token = os.environ.get("SWIGGY_TOKEN")
    auth_code = os.environ.get("AUTH_CODE")
    code_verifier = os.environ.get("CODE_VERIFIER")

    # Flow A: We have an Auth Code to exchange into a Bearer Token
    if auth_code and code_verifier:
        print("🔄 Exchanging Auth Code for Swiggy Bearer Token...")
        payload = {
            "grant_type": "authorization_code",
            "code": auth_code.strip(),
            "code_verifier": code_verifier.strip(),
            "redirect_uri": REDIRECT_URI
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(SWIGGY_TOKEN_URL, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                print("\n🎉 SUCCESS! Token acquired.")
                print(f"YOUR_ACCESS_TOKEN: {data.get('access_token')}")
            else:
                print(f"❌ Exchange Failed ({resp.status_code}): {resp.text}")
        return

    # Flow B: We already have the Access Token (Ready to run agent)
    if token:
        print("✅ Bearer token found. Connecting to Instamart MCP...")
        headers = {"Authorization": f"Bearer {token}"}
        async with streamable_http_client(SWIGGY_IM_ENDPOINT, headers=headers) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("Connected! Fetching delivery addresses...")
                addresses = await session.call_tool("get_addresses", arguments={})
                print("Address Data:", json.dumps(addresses.data, indent=2))
        return

    # Flow C: Initial login URL generation
    verifier, challenge = generate_pkce_pair()
    state = secrets.token_hex(8)
    login_url = (
        f"{SWIGGY_AUTH_URL}?"
        f"response_type=code&"
        f"client_id=instamart-repeater-agent&"
        f"redirect_uri={REDIRECT_URI}&"
        f"code_challenge={challenge}&"
        f"code_challenge_method=S256&"
        f"state={state}&"
        f"scope=mcp:tools"
    )
    print("\n🔑 --- STEP 1: OPEN THIS SIGN-IN LINK ---")
    print(login_url)
    print(f"\n🔑 --- STEP 2: COPY THIS VERIFIER IMMEDIATELY ---\n{verifier}\n")

if __name__ == "__main__":
    asyncio.run(main())
