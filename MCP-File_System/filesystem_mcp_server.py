import os
import shutil
import sys
import logging
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("filesystem-mcp")

mcp = FastMCP("File System Explorer")

@mcp.tool(name="list_directory", description="List files and folders in a directory")
def list_directory(path: str = ".") -> str:
    if not os.path.exists(path):
        return f"Directory '{path}' does not exist."
    items = os.listdir(path)
    return "\n".join(items) if items else f"No files or folders in '{path}'."

@mcp.tool(name="read_file", description="Read the contents of a text file")
def read_file(path: str) -> str:
    if not os.path.isfile(path):
        return f"'{path}' is not a file."
    with open(path, "r", encoding="utf-8") as f:
        return f.read(1000)

@mcp.tool(name="file_metadata", description="Get metadata for a file")
def file_metadata(path: str) -> str:
    if not os.path.exists(path):
        return f"File or directory '{path}' does not exist."
    stat = os.stat(path)
    return (
        f"Path: {path}\n"
        f"Size: {stat.st_size} bytes\n"
        f"Modified: {stat.st_mtime}\n"
        f"Created: {stat.st_ctime}\n"
        f"Is Directory: {os.path.isdir(path)}"
    )

@mcp.tool(name="create_file", description="Create a new text file with content")
def create_file(path: str, content: str = "") -> str:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return f"File '{path}' created successfully."

@mcp.tool(name="append_file", description="Append content to an existing file")
def append_file(path: str, content: str) -> str:
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)
    return f"Appended to '{path}'."

@mcp.tool(name="clear_file", description="Clear the contents of a file")
def clear_file(path: str) -> str:
    open(path, 'w').close()
    return f"Cleared content of '{path}'."

@mcp.tool(name="delete_file", description="Delete a file")
def delete_file(path: str) -> str:
    if os.path.isfile(path):
        os.remove(path)
        return f"File '{path}' deleted."
    return f"'{path}' is not a file."

@mcp.tool(name="create_folder", description="Create a new directory")
def create_folder(path: str) -> str:
    os.makedirs(path, exist_ok=True)
    return f"Directory '{path}' created."

@mcp.tool(name="rename_item", description="Rename a file or folder")
def rename_item(old_path: str, new_path: str) -> str:
    os.rename(old_path, new_path)
    return f"Renamed '{old_path}' to '{new_path}'."

@mcp.tool(name="copy_file", description="Copy a file to a new location")
def copy_file(source: str, destination: str) -> str:
    shutil.copy(source, destination)
    return f"Copied '{source}' to '{destination}'."

@mcp.tool(name="move_file", description="Move a file to a new location")
def move_file(source: str, destination: str) -> str:
    shutil.move(source, destination)
    return f"Moved '{source}' to '{destination}'."

@mcp.tool(name="search_file", description="Search for a file in a directory tree")
def search_file(name: str, start_path: str = ".") -> str:
    for root, dirs, files in os.walk(start_path):
        if name in files or name in dirs:
            return os.path.join(root, name)
    return f"'{name}' not found from '{start_path}'."

@mcp.tool(name="view_tree", description="Display directory structure")
def view_tree(path: str = ".", depth: int = 2) -> str:
    output = []

    def walk(p, d):
        if d > depth:
            return
        items = os.listdir(p)
        for item in items:
            full = os.path.join(p, item)
            output.append("  " * d + "- " + item)
            if os.path.isdir(full):
                walk(full, d + 1)

    walk(path, 0)
    return "\n".join(output) if output else f"No files in '{path}'"

@mcp.tool(name="hello_filesystem", description="Simple test tool for File System")
def hello_filesystem(name: str = "World") -> str:
    return f"Hello from the File System Explorer, {name}!"

if __name__ == "__main__":
    # For local development with `mcp dev`
    print("Starting GitHub MCP server...")
    
    # With proper host and port configuration to avoid conflicts
    if "mcp dev" in " ".join(sys.argv):
        mcp.serve(host="127.0.0.1", port=5000)
    else:
        # Standard serve for regular use
        mcp.serve()
