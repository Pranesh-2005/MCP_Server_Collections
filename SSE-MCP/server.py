import os
import subprocess
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("terminal")

DEFAULT_WORKSPACE = os.path.join(os.getcwd(), "workspace")

# define tool - llm will create code/ command and pass to this fn
@mcp.tool()
async def run_server_command(command: str) -> str:
    """
    Run a terminal command in workspace.
    Args:
        command: The shell command to run on windows

    Returns:
        The command output or an error message.
    """
    # try catch to handle exception
    try:
        result = subprocess.run(command, cwd= DEFAULT_WORKSPACE, shell=True, capture_output=True, text=True)
        return result.stdout or result.stderr
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    mcp.run(transport="stdio")
