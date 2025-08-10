# Postgres Explorer MCP

**Postgres Explorer MCP** is an async Python server that lets you interact with your PostgreSQL databases using [Claude Desktop](https://www.anthropic.com/claude) or any MCP-compatible client. It provides tools to list databases, view tables, inspect schemas, run queries, and more—all securely and efficiently.

---

## Features

- **Async**: Built with [`asyncpg`](https://github.com/MagicStack/asyncpg) for fast, non-blocking database access.
- **Claude Desktop Ready**: Works out-of-the-box with Claude Desktop via the MCP protocol and stdio transport.
- **Easy to Extend**: Add your own tools for custom database operations.
- **Secure**: Uses parameterized queries to help prevent SQL injection.

---

## Requirements

- Python 3.9+
- [asyncpg](https://pypi.org/project/asyncpg/)
- [python-dotenv](https://pypi.org/project/python-dotenv/)
- [mcp](https://pypi.org/project/mcp/) (Model Context Protocol)
- A running PostgreSQL server

---

## Installation

1. **Clone this repository** (or copy the files to your project folder):

    ```sh
    git clone https://github.com/yourusername/psqlMcp.git
    cd psqlMcp
    ```

2. **Install dependencies** (using [uv](https://github.com/astral-sh/uv) or pip):

    ```sh
    uv pip install asyncpg python-dotenv mcp
    # or
    pip install asyncpg python-dotenv mcp
    ```

3. **Set up your `.env` file** with your PostgreSQL credentials refer `.env.example`:

    ```
    PG_USER=your_postgres_user
    PG_PASS=your_postgres_password
    PG_HOST=localhost
    PG_PORT=5432
    ```

---

## Usage

### Standalone (for testing)

You can run the server directly:

```sh
uv run pgclaude.py
```

### With Claude Desktop

1. Make sure your `claude_desktop_config.json` includes an entry like:

    ```json
    "mypostgres": {
      "command": "uv",
      "args": [
        "--directory",
        "Path to your Directory consisting pgcalude.py file",
        "run",
        "pgclaude.py"
      ]
    }
    ```

2. Start Claude Desktop. It will automatically launch the server and connect via stdio.

3. In Claude, you can now use tools like:
    - `list_databases`
    - `list_tables`
    - `table_schema`
    - `view_table`
    - `execute_query`
    - `hello_postgres`

---

## Example Prompts

- **List all databases:**  
  `Use the mypostgres tool to list all databases.`

- **Show tables in a database:**  
  `List all tables in the database "mydb".`

- **Get schema for a table:**  
  `Show the schema for the table "users" in "mydb".`

- **View table rows:**  
  `Show the first 10 rows of the "orders" table in "mydb".`

- **Run a custom query:**  
  `Execute the query "SELECT COUNT(*) FROM users;" on "mydb".`

---

## Adding Your Own Tools

You can add more tools by defining new async functions and decorating them with `@mcp.tool`. For example:

```python
@mcp.tool(name="count_rows", description="Count rows in a table")
async def count_rows(db_name: str, table: str) -> str:
    conn = await connect(db_name)
    row = await conn.fetchrow(f'SELECT COUNT(*) AS count FROM "{table}";')
    await conn.close()
    return f"Row count: {row['count']}"
```

---

## Troubleshooting

- **Connection errors:**  
  Double-check your `.env` file and ensure your PostgreSQL server is running and accessible.

- **Missing dependencies:**  
  Run `pip install asyncpg python-dotenv mcp` to install requirements.

- **Claude can't find the tool:**  
  Make sure your config path and filenames match, and that `mcp.run(transport="stdio")` is at the end of your script.

---

## Credits

- [asyncpg](https://github.com/MagicStack/asyncpg)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [mcp](https://github.com/modelcontextprotocol/mcp)
- [Anthropic Claude](https://www.anthropic.com/claude)

---
