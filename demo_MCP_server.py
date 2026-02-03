

from fastMCP import FastMCP
import time
from datetime import datetime, timezone
from typing import Optional, Annotated
from pydantic import BaseModel, Field

#MCP server setup

mcp = FastMCP(
    server_name="tutorial-documentacion-mcp",
    version="1.0.0",
    description="A simple MCP server for demonstration purposes",
)

counter = 0

# Tools
@mcp.tool(
    # Decorator arguments
    name="increment_counter",
    description="Increments a given counter by a specified value",
    tags={"example", "counter"},
)
async def increment_counter(
    # Function arguments

    increment: Annotated[int, Field(ge=1, le=1000, description="The value to increment the counter by")]=1
) -> int:
    # Function implementation
    counter += increment

    return{
        "previous_value": counter,
        "increment": increment,
        "new_value": counter + increment,
    }
 
@mcp.tool(
    name="Reset_counter",
    description="Resets the counter to zero",
    tags={"example", "counter"},
)
async def reset_counter() -> int:
    # Function implementation
    counter = 0

    return {
        "old_value": counter,
        "new_value": 0,
    }

@mcp.tool(
    name="get_counter",
    description="Gets the current value of the counter",
    tags={"example", "counter"})
async def get_counter() -> int:
    # Function implementation
    return f"Current counter value is {counter}"


def main():
    print("Hello from tutorial-documentacion-mcp!")


if __name__ == "__main__":
    mcp.run(transport="http", host="localhost", port=8000)


