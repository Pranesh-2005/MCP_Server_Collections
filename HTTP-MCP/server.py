from fastmcp import FastMCP, tools

mcp = FastMCP("Streamable HTTP MCP Server")

@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8080)
