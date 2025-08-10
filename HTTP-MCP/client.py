from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
import asyncio

transport = StreamableHttpTransport(url="http://127.0.0.1:8080/mcp")
client = Client(transport)

async def main():
    async with client:
        tools = await client.list_tools()
        print(f"Available tools: {tools}")

        response = await client.call_tool("greet", {"name": "Pranesh"})
        print(f"Response: {response}")

asyncio.run(main())
