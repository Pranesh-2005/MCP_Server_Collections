# 🚀 GitHub MCP Tools

A powerful set of tools built using the **Model Context Protocol (MCP)** framework to allow AI assistants and agents to interact directly with GitHub. Perfect for automating developer workflows via AI integration.

## ✨ Features

- 👤 Fetch detailed GitHub user profiles
- 📁 Create new repositories
- ❌ Delete repositories (with appropriate permissions)
- 🔄 Create and merge pull requests
- 📋 List repositories (authenticated or by username)
- 👋 Simple Hello World test tool

## ⚙️ Tech Stack

- Python 3.8+
- FastMCP (Model Context Protocol server)
- GitHub REST API
- `requests`, `python-dotenv` for API integration and environment handling

## 📦 Installation

1. **Clone the repository**:

```bash
git clone https://github.com/Pranesh-2005/UsingMcp.git
cd UsingMcp
```

2. **Create Github PAT**
Go to your Github Profile -> Settings -> Developer Setting -> Personal Access Token(PAT) -> Token (Classic) -> Generate New Token (Classic)

3. **Create a .env file**
    - Create a .env file
    - Add GITHUB_PAT=ghp_********************* in the .env file

4. **Run the python file**

```bash
mcp dev github_server.py
```
