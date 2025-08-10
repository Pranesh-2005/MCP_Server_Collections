import os
import sys
import logging
import asyncpg
from typing import Any, List, Dict
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("postgres-mcp")

# Load environment variables
load_dotenv()

# Initialize FastMCP
mcp = FastMCP("Postgres Explorer")

# Helper function to connect to the database
async def connect(db_name: str) -> asyncpg.Connection:
    try:
        conn = await asyncpg.connect(
            database=db_name,
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASS", "your_password"),
            host=os.getenv("PG_HOST", "localhost"),
            port=os.getenv("PG_PORT", "5432")
        )
        logger.info(f"Connected to database: {db_name}")
        return conn
    except Exception as e:
        logger.error(f"Connection error: {e}")
        raise

@mcp.tool(name="list_databases", description="List all PostgreSQL databases")
async def list_databases() -> str:
    """List all available PostgreSQL databases."""
    try:
        conn = await connect("postgres")
        rows = await conn.fetch("SELECT datname FROM pg_database WHERE datistemplate = false;")
        await conn.close()
        return "\n".join(row["datname"] for row in rows) if rows else "No databases found."
    except Exception as e:
        logger.error(f"Error listing databases: {e}")
        return f"Error: {str(e)}"

@mcp.tool(name="list_tables", description="List all public tables in a PostgreSQL database")
async def list_tables(db_name: str) -> str:
    """List all tables in the specified database."""
    try:
        conn = await connect(db_name)
        rows = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        await conn.close()
        return "\n".join(row["table_name"] for row in rows) if rows else f"No public tables found in '{db_name}'."
    except Exception as e:
        logger.error(f"Error listing tables: {e}")
        return f"Error: {str(e)}"

@mcp.tool(name="table_schema", description="Get column names and types of a table")
async def table_schema(db_name: str, table: str) -> str:
    """Get schema information for a specific table."""
    try:
        conn = await connect(db_name)
        rows = await conn.fetch(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = $1;",
            table
        )
        await conn.close()
        return "\n".join(f"{row['column_name']}: {row['data_type']}" for row in rows) if rows else f"No schema found for table '{table}'."
    except Exception as e:
        logger.error(f"Error retrieving schema: {e}")
        return f"Error: {str(e)}"

@mcp.tool(name="view_table", description="Show first 10 rows of a table")
async def view_table(db_name: str, table: str) -> str:
    """View the first 10 rows of a table."""
    try:
        conn = await connect(db_name)
        # Use proper identifier quoting
        rows = await conn.fetch(f'SELECT * FROM "{table}" LIMIT 10;')
        await conn.close()
        
        if not rows:
            return f"No rows found in '{table}'."
        
        # Format results nicely
        result_lines = []
        for row in rows:
            row_dict = dict(row)
            result_lines.append(str(row_dict))
            
        return "\n".join(result_lines)
    except Exception as e:
        logger.error(f"Error viewing table '{table}': {e}")
        return f"Error: {str(e)}"

@mcp.tool(name="execute_query", description="Execute a custom SQL query")
async def execute_query(db_name: str, query: str) -> str:
    """Execute a custom SQL query and return results."""
    try:
        conn = await connect(db_name)
        
        # Determine if this is a query that returns results
        query_type = query.strip().upper().split()[0]
        
        if query_type in ("SELECT", "WITH", "SHOW", "EXPLAIN"):
            rows = await conn.fetch(query)
            await conn.close()
            
            if not rows:
                return "Query executed successfully. No results returned."
            
            # Format results
            result_lines = []
            for row in rows:
                row_dict = dict(row)
                result_lines.append(str(row_dict))
                
            return "\n".join(result_lines)
        else:
            # For non-SELECT queries
            status = await conn.execute(query)
            await conn.close()
            return f"Query executed successfully. Status: {status}"
            
    except Exception as e:
        logger.error(f"Query execution error: {e}")
        return f"Error executing query: {str(e)}"

@mcp.tool(name="hello_postgres", description="Test connection to the server")
async def hello_postgres(name: str = "World") -> str:
    """Simple test function."""
    logger.info(f"Hello function called with name: {name}")
    return f"Hello from the Postgres Explorer, {name}!"

if __name__ == "__main__":
    print("Starting Postgres Explorer with stdio transport...")
    # Use stdio transport for Claude integration
    mcp.run(transport="stdio")