# File System Explorer MCP

A powerful file system management tool built with FastMCP that provides common file operations through a simple API.

## Features

- 📁 Directory Operations
  - List directory contents
  - Create folders
  - View directory tree structure
  
- 📄 File Operations
  - Create, read, and append to files
  - Copy and move files
  - Delete files
  - Clear file contents
  - Get file metadata
  
- 🔍 Search Capabilities
  - Search for files in directory tree
  - View detailed file information

## Installation

1. Install the required dependencies:
```bash
pip install mcp-core
```

2. Clone this repository:
```bash
git clone <repository-url>
cd file-system-explorer
```

## Usage

There are two versions of the tool:

### Standard Version (file.py)
Run with default configuration:
```bash
python file.py
```

For local development:
```bash
mcp dev
```

### Claude Version (fileclaude.py)
Run with stdio transport:
```bash
python fileclaude.py
```

## Available Tools

| Tool Name | Description | Parameters |
|-----------|-------------|------------|
| `list_directory` | List files and folders | `path` (optional, default: ".") |
| `read_file` | Read file contents | `path` |
| `file_metadata` | Get file information | `path` |
| `create_file` | Create new text file | `path`, `content` (optional) |
| `append_file` | Append to existing file | `path`, `content` |
| `clear_file` | Clear file contents | `path` |
| `delete_file` | Delete a file | `path` |
| `create_folder` | Create new directory | `path` |
| `rename_item` | Rename file/folder | `old_path`, `new_path` |
| `copy_file` | Copy file | `source`, `destination` |
| `move_file` | Move file | `source`, `destination` |
| `search_file` | Search for file | `name`, `start_path` (optional) |
| `view_tree` | Display directory structure | `path` (optional), `depth` (optional) |

## Error Handling

- The Claude version includes comprehensive error handling with try-except blocks
- All operations return meaningful error messages if something goes wrong
- File operations validate paths before execution
