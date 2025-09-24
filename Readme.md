# 🗂️ MCP_Server_Collections

**MCP_Server_Collections** is a curated collection of Model Context Protocol (MCP) servers and clients designed to facilitate AI agent and assistant interactions with various external services and systems. This repository provides robust, extensible MCP-based tools for tasks such as HTTP streaming, Google Calendar management, file system operations, Azure OpenAI integration, and GitHub automation.

---

## 🚀 Introduction

MCP_Server_Collections brings together multiple MCP server implementations, sample clients, and integrations to demonstrate the versatility and power of MCP. Whether you're building AI agents, automating workflows, or prototyping new tools, this repository provides ready-to-use examples and starting points.

---

## ✨ Features

- **Streamable HTTP MCP Server**  
  Easily create and use MCP servers with HTTP streaming capabilities.

- **Google Calendar Integration**  
  List, create, delete, and update calendar events via MCP.

- **File System Explorer**  
  Perform file and directory operations through a simple API.

- **Azure OpenAI Client**  
  Connect MCP clients to Azure OpenAI endpoints.

- **GitHub Automation Tools**  
  Enable AI agents to interact with GitHub for user profiles and repository management.

- **Ready-to-Use Examples**  
  Sample scripts and server implementations for fast integration and learning.

---

## ⚡ Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/Pranesh-2005/MCP_Server_Collections.git
   cd MCP_Server_Collections
   ```

2. **Install Requirements**

   Each MCP server/client may have its own requirements. For example:
   - Python 3.8+
   - See individual subfolders (`requirements.txt` or README.md)

   Example (for FastMCP and Google API):
   ```bash
   pip install fastmcp google-auth google-auth-oauthlib google-api-python-client python-dotenv openai
   ```

---

## 🚦 Usage

### Streamable HTTP MCP Server

- **Start the Server**
  ```bash
  python HTTP-MCP/server.py
  ```
- **Run the Client**
  ```bash
  python HTTP-MCP/client.py
  ```

### Google Calendar MCP Server

- **Read the documentation**
  See `MCP-Calendar/Readme.md`
- **Run the Server**
  ```bash
  python MCP-Calendar/calendar_mcp_server.py
  ```

### File System Explorer MCP

- **Read the documentation**
  See `MCP-File_System/Readme.md.md`
- **Run the Server**
  ```bash
  python MCP-File_System/filesystem_mcp_server.py
  ```

### Azure OpenAI MCP Client

- **Configure your `.env` file** with `AZURE_OPENAI_ENDPOINT` and `AZURE_OPENAI_API_KEY`
- **Run the Client**
  ```bash
  python MCP-Client-Azure/client.py
  ```

### GitHub MCP Tools

- **Read the documentation**
  See `MCP-GITHUB/README.md`

---

## 🤝 Contributing

We welcome contributions! To contribute:

1. Fork this repository.
2. Create a new branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add new feature'`
4. Push to your branch: `git push origin feature/your-feature`
5. Open a pull request.

Please follow the style and structure of existing modules. Document any new features clearly.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 📚 Repository Structure

```
MCP_Server_Collections/
├── HTTP-MCP/
│   ├── client.py
│   └── server.py
├── MCP-Calendar/
│   ├── Readme.md
│   ├── calendar_mcp_server.py
│   └── calendar_mcp_server_for_claude.py
├── MCP-Client-Azure/
│   └── client.py
├── MCP-File_System/
│   ├── Readme.md.md
│   ├── filesystem_mcp_server.py
│   └── filesystem_mcp_server_for_claude.py
├── MCP-GITHUB/
│   └── README.md
└── LICENSE
```

---

## 💬 Questions & Support

For issues, suggestions, or help, please open a [GitHub Issue](https://github.com/Pranesh-2005/MCP_Server_Collections/issues).

---

Happy hacking! 👩‍💻👨‍💻

## License
This project is licensed under the **MIT** License.

---
🔗 GitHub Repo: https://github.com/Pranesh-2005/MCP_Server_Collections
