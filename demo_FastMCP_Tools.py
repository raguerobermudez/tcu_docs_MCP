# Tools

"""Optional Arguments from FastMCP documentation:
FastMCP follows Python’s standard function parameter conventions.
Parameters without default values are required, while those with default values are optionals"""

"""
FastMCP uses Pydantic's flexible data validation system to define and validate tool arguments.
Example: "3.14" is automatically converted to a float, and an error is raised if the conversion fails.

"""

"""Simple string Descriptions, Annotated and Field can be used for more complex metadata
    Example:
        image_url: Annotated[str, Field(description="URL of the image to process")],
        resize: Annotated[bool, Field(description="Whether to resize the image")] = False,
"""

"""
    To inject values at runtimme, without exposiong them to the LLM, use dependency injections with
    Depends()
    Example:
        def get_user_details(user_id: str = Depends(get_user_id)) -> str:
"""
"""
    Return Values 
    FastMCP Tools can return data in two formats: Traditional Content blocks (Text, images) or
    Structured Data (JSON objects). 
    FastMCP automatically generate output schemas
    The return type is automatically inferred from the function's
"""

"""
    Typed Models
    Dataclasss and Pydantic models are useful because FastMCP extracts field names and types to generate
    detailed tool schemas.
    Example:
        class ImageProcessingResult(BaseModel):
            processed_image_url: str
            width: int
            height: int 

             
"""

"""
    To Override the automatic schema generation, you can explicitly define the output schema providing
    a custom output_schema argument to the @mcp.tool decorator.
    Example:
        @mcp.tool(output_schema={
            "type": "object", 
            "properties": {
                "data": {"type": "string"},
                "metadata": {"type": "object"}
            }
        })
        def custom_schema_tool() -> dict:
            return {"data": "Hello", "metadata": {"version": "1.0"}}

Important Constraints:

    Output schemas must be object types ("type": "object")
    If you provide an output schema, your tool must return structured output that matches it
    However, you can provide structured output without an output schema (using ToolResult)
Schema generation works for most common types including basic types, collections, union types, Pydantic models, TypedDict structures, and dataclasses.

"""

"""ToolResult

    Tool Result gives you more control over the tool's output, allowing you to specify both content and structured data.
    Example:
    from fastmcp.tools.tool import ToolResult
    from mcp.types import TextContent

    @mcp.tool
    def advanced_tool() -> ToolResult:
        return ToolResult(
            content=[TextContent(type="text", text="Human-readable summary")],
            structured_content={"data": "value", "count": 42},
            meta={"execution_time_ms": 145}
        )
"""


""" 
    When a tool crashes, a normal Python exception is raised. 
    FastMCP catches these exceptions and returns a structured error response.
    ValueError
    TypeError
    FileNotFoundError
    
    FastMCP ToolError

    By Default all exceptions details are sent back to the client
    Is not good for security
"""

"""

    Hidding internal error details
    1. Global Masking
    mcp = FastMCP(mask_error_details=True)
    "Client gest a generic error message

    2. ToolError: Controled Messages
    raise ToolError("A specific error occurred")
    "Client gets the specific error message

    Messages from ToolError are ALWAYS shown to the client, even if masking is on.

    Use normal exceptions for system errors, and ToolError for messages you want the client to see. 
"""

"""

TimeOuts
Tools can specify a timeout parameter to limit their execution time.
If a tool exceeds this time, it is terminated and a timeout error is returned to the client

@mcp.tool(timeout=5)  # Timeout after 5 seconds (float)

sync and async tools are supported
"""

"""Component visibility ##### Version 3#####
By default, all tools are public and can be invoked by any client.
You can restrict access to certain tools using the visibility parameter in the @mcp.tool decorator.


# Disable specific tools by key
mcp.disable(keys={"tool:admin_action"})

# Disable tools by tag
mcp.disable(tags={"admin"})

# Or use allowlist mode - only enable tools with specific tags
mcp.enable(tags={"public"}, only=True)



@mcp.tool(tags={"admin"})
def admin_action() -> str:
   
    return "Done"

@mcp.tool(tags={"public"})
def public_action() -> str:
    return "Done"

# Disable specific tools by key
mcp.disable(keys={"tool:admin_action"})

# Disable tools by tag
mcp.disable(tags={"admin"})

# Or use allowlist mode - only enable tools with specific tags
mcp.enable(tags={"public"}, only=True)


"""
"""
MCP Annotations
FastMCP provides several annotations to enhance tool definitions:
  annotations={
readOnlyHint	boolean	false	Indicates if the tool only reads without making changes
destructiveHint	boolean	true	For non-readonly tools, signals if changes are destructive
idempotentHint	boolean	false	Indicates if repeated identical calls have the same effect as a single call
openWorldHint	boolean	true	Specifies if the tool interacts with external systems

"""

"""Accessing MCP Context inside tools.

Tools can access MCP features like logging, reading resources, or reporting progress through the Context object. To use it, add a parameter to your tool function with the type hint Context.

"""

from fastMCP import FastMCP
from fastMCP.exceptions import ToolError

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




@mcp.tool(
    # Decorator arguments
    name="increment_counter",
    description="Increments a given counter by a specified value",
    tags={"example", "counter"},
    timeout=10,  # Timeout after 10 seconds
)
async def increment_counter(
    # Function arguments
    increment: Annotated[int, Field(ge=1, le=1000,
    description="The value to increment the counter by")]=1 #Argument  Optional - has default value (1)
) -> dict:
    # Function implementation
    global counter
    previous_value = counter
    counter += increment
    # ToolError example
    if counter > 10000:
        raise ToolError("Counter value exceeded the maximum limit of 100000.")

    return{
        "previous_value": previous_value,
        "increment": increment,
        "new_value": counter,
    }
 
@mcp.tool(
    name="Reset_counter",
    description="Resets the counter to zero",
    tags={"example", "counter"},
)
async def reset_counter() -> dict:
    # Function implementation
    global counter
    old = counter
    counter = 0  

    return {
        "old_value": old,
        "new_value": counter,
    }

@mcp.tool(
    name="get_counter",
    description="Gets the current value of the counter",
    tags={"example", "counter"},
    # "Indicates if the tool only reads without making changes
    annotations={
        "readOnlyHint": True}
)
    
async def get_counter() -> str:
    # Function implementation
    return f"Current counter value is {counter}"


def main():
    print("Hello from tutorial-documentacion-mcp!")


if __name__ == "__main__":
    mcp.run(transport="http", host="localhost", port=8000)


