### MCP Transforms

""" Modify components as they flow through the server

Tranformers modify components as they flow from providers to clients. 
Transforms ban be see it as filters in a pipeline



"""


"""Built in Transforms
Namespace: Prefixes names to avoid conflicts
Tool transformation: Rename tools, modify descriptions
Enable: Control which tools are visible to clients
Resources as tools: Expose resources to tool only clients
Propts as tools: Expose prompts as tools for tool-only clients
"""

"""Server vs Provider Transforms

Provider level transforms: Provider transorms 
Modify components from a specific provider

Server level transforms: } They run after provider transforms, seeing the already-transformed names.

"""

"""Transform order

Transforms stack in the order they are registered.

"""

### Namespcace Transform"""

"""THe namespace transform prefixes component names with a specified namespace.


"""

from fastMCP import FastMCP
from fastmcp.server.transforms import Namespace

weather = FastMCP("WeatherServer")
calendar = FastMCP("CalendarServer") 

@weather.tool
def get_data(location: str) -> str:
    return f"The weather in {location} is sunny with a high of 25°C."

@calendar.tool
def get_data(date: str) -> str:
    return f"You have a meeting on {date} at 3 PM."

weather.add_transform(Namespace("weather"))


### Tool tranformation

""" Tool transformation lets modigy tool schemas, 
renaming tools, changing descriptions, etc

"""

""" Defered transforms

Apply modifications when tools frow through a tranfirn chain, useful when
is needed to modify tools from other providers or tools that are generated dynamically
as Servers, proxis,etc

"""

"""Inmmediate transforms

creates a modified tool object righ ways
Is useful when direcct access to the tool object is posible.

"""

### ToolTransform

from fastmcp import FastMCP
from fastmcp.server.transforms import ToolTransform
from fast.tools.tool_transform import ToolTransformConfig

mcp = FastMCP("Server")

@mpc.tool
def verbose_internal_data_fetcher(query: str) -> str:
    return f"This tool fetches internal data and has a verbose name and description. Results {query}"


# rename tool

mcp.add_transform(ToolTransform{
    name="verbose_internal_data_fetcher": ToolTransformConfig(
        name="search",
        description="Searches for data based on a query string",)})

# clients see "search" instead of "verbose_internal_data_fetcher" with the new description

# Tool.from_tool()
# Use Tool.from_tool() 


from fastmcp import FastMCP
from fastmcp.tools import Tool, tool
from fastmcp.tools.tool_transform import ArgTransform

@tool
def add_numbers(a: int, b: int) -> int:
    return a + b

# transform it before registering

add_numbers_tool = Tool.from_tool(add_numbers, name="add_numbers", description="Adds two numbers",
                                  
                                  transform_args={
                                      "q": ArgTransform(
                                          name="number_a_b", description="The two numbers to add, separated by an underscore")
                                  })

                    
mco = FastMCP("MathServer")
mco.add_tool(add_numbers_tool)

"""Rename arguments, see Modification Options 

Tool-level options
name, descriptions, tags, title, annotations, meta, enbale


argument-level options
name, description, type, default, required, etc

"""

"""Custom transform functions

For advanced scenarios, provide a transform_fn that intercepts tool execution

"""

### Component Visibility

"""
enabl/disable
"""
from fastmcp import FastMCP

mcp = FastMCP("Server")

@mcp.tool(tags={"admin"})
def delete_everything() -> str:
    """Delete all data."""
    return "Deleted"

@mcp.tool(tags={"admin"})
def reset_system() -> str:
    """Reset the system."""
    return "Reset"

@mcp.tool
def get_status() -> str:
    """Get system status."""
    return "OK"

# Disable admin tools
mcp.disable(tags={"admin"})

# Clients only see: get_status}


""" Keys and tags"""

# Disable a specific tool
mcp.disable(keys={"tool:delete_everything"})

# Disable multiple specific components
mcp.disable(keys={"tool:reset_system", "resource:data://secrets"})

### Resources as tools

"""Some MCP clients only support tools. 
They cannot list or read resources directly because they lack resource protocol support.
"""

### Propts as Tools

"""Some MCP clients only support tools.
They cannot list or read resources directly because they lack resource protocol support.
"""