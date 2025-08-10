import os
import sys
import logging
import psycopg2
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

logging.basicConfig(level=logging.INFO)
load_dotenv()

mcp = FastMCP("Postgres Explorer")

def connect(db_name: str):
    return psycopg2.connect(
        dbname=db_name,
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASS", "your_password"),
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432")
    )


@mcp.tool(name="list_tables", description="List all public tables in the given PostgreSQL database")
def list_tables(db_name: str) -> str:
    try:
        conn = connect(db_name)
        cur = conn.cursor()
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        tables = cur.fetchall()
        return "\n".join(table[0] for table in tables) if tables else f"No public tables found in database '{db_name}'."
    except Exception as e:
        logging.error(f"Error listing tables from {db_name}: {e}")
        return f"Error: {str(e)}"
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()


@mcp.tool(name="table_schema", description="Get the schema of a table in the specified database")
def table_schema(db_name: str, table: str) -> str:
    try:
        conn = connect(db_name)
        cur = conn.cursor()
        cur.execute(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s",
            (table,)
        )
        schema = cur.fetchall()
        return "\n".join(f"{col}: {dtype}" for col, dtype in schema) if schema else f"No schema found for table '{table}' in '{db_name}'."
    except Exception as e:
        logging.error(f"Error retrieving schema from {db_name}: {e}")
        return f"Error: {str(e)}"
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()


@mcp.tool(name="view_table", description="View first 10 rows of a table from the specified database")
def view_table(db_name: str, table: str) -> str:
    try:
        conn = connect(db_name)
        cur = conn.cursor()
        cur.execute(f'SELECT * FROM "{table}" LIMIT 10')
        rows = cur.fetchall()
        colnames = [desc[0] for desc in cur.description]
        return "\n".join(str(dict(zip(colnames, row))) for row in rows) if rows else f"No rows found in '{table}' from '{db_name}'."
    except Exception as e:
        logging.error(f"Error viewing table {table} from {db_name}: {e}")
        return f"Error: {str(e)}"
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()
        
@mcp.tool(name="list_databases", description="List all PostgreSQL databases")
def list_databases() -> str:
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASS", "your_password"),
            host=os.getenv("PG_HOST", "localhost"),
            port=os.getenv("PG_PORT", "5432")
        )
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cur.fetchall()
        return "\n".join(db[0] for db in databases) if databases else "No databases found."
    except Exception as e:
        logging.error(f"Error listing databases: {e}")
        return f"Error: {str(e)}"
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

@mcp.tool(name="hello_postgres", description="Test tool for Postgres server")
def hello_postgres(name: str = "World") -> str:
    return f"Hello from the Postgres Explorer, {name}!"

if __name__ == "__main__":
    print("Starting Postgres MCP server...")
    if "mcp dev" in " ".join(sys.argv):
        mcp.serve(host="127.0.0.1", port=5000)
    else:
        mcp.serve()
