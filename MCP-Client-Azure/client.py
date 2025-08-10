import os
import asyncio
from dotenv import load_dotenv
from openai import AzureOpenAI

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-12-01-preview")

client_azure = AzureOpenAI(
    api_key=AZURE_API_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    api_version=API_VERSION
)

async def run_loop(session: ClientSession):
    # List the available tools
    tools_list = await session.list_tools()
    print("✅ Discovered tools:", [tool.name for tool in tools_list.tools])

    while True:
        user_text = input("\n>> ").strip()
        if user_text.lower() in ("exit", "quit"):
            print("Bye 👋")
            return

        messages = [
            {"role": "user", "content": user_text}
        ]

        response = await client_azure.chat.completions.acreate(
            deployment_id=DEPLOYMENT_NAME,
            input=messages,
            tools=[tool.to_dict() for tool in tools_list.tools],
            tool_choice="auto",
            temperature=0.1
        )

        msg = response.choices[0].message
        if msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.function.name
                args = tc.function.arguments or {}
                print(f"👉 Calling tool: {name} with args {args}")
                result = await session.call_tool(name, args)
                print("← Tool returned:", result.content)
        else:
            print("💬 Assistant:", msg.content)

async def main(server_script: str):
    server_params = StdioServerParameters(
        command="python",
        args=[server_script],
        env=None
    )

    async with stdio_client(server_params) as (r, w):
        async with ClientSession(r, w) as session:
            await session.initialize()
            await run_loop(session)

if __name__ == "__main__":
    import sys
    script = sys.argv[1] if len(sys.argv) > 1 else "weather.py"
    asyncio.run(main(script))
