"""
Provudesr become importan when 
your compoenentes come from multiple sources

Other FastMC server, remote servers, etc


The provider abstraction solver a common problem
 of how to manage and organize resources and tools
that may come from different sources or have different characteristics.


Composition: Break a larger server into smaller,
 focused providers that can be developed and maintained independently

Dynamic sources
"""
"""Built in providers

LocalProvider: The default provider for resources and tools defined directly in the server code.
FastMCPProovider: Wraps another FASTMCP server as a provider,
 allowing you to integrate resources and tools from that server into your own.

"""

""" Tranforms

Modify components as they flow from providers to clients.
Each transform sits in a chain
"""

"""
Namespace: Prefixes names to avoid conflicts
ToolTransform: Modify tool schemas
"""



"""Provider Order

When a client requests a tool, FasMCP queries providers in registration order
The first provider to return a matching tool is used to handle the request

LOCALPROVIDER is always first, so decorator-defined tools take precedence

"""

# local Provider
"""Local Provider

The default provider for decorator-register components"""

""" Every FastMCP server has a local provider as first provider"""


from fastMCP import FastMCP

mcp = FastMCP()

"""These tools are registered in the local provider by default"""
@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"

"""Decorators
@mcp.tool, @mcp.resourcer, @mcp.provider"""

"""Direct method"""

from fastMCP.tools import Tool

""" Create a tool instance and register it directly with the provider"""

my_tool= Tool.from_function(greet, name="greet_tool", description="A tool that greets a person by name")

mcp.add_tool(my_tool)


""" Remove componenets"""

mcp.remove_tool("my_tool")

""" Duplicate handling

 the behavior depends on the on_duplicate setting:
 
 error
 warn
 replace
 ignore
 """
mcp = FastMCP("MyServer", on_duplicate="warn")


"""Standalone localprovider
It's posible to create a local provider independently and attach it to multiple servers"""

from fastMCP import FastMCP
from fastMCP.server.providers import LocalProvider

# Create a reusable local provider

shared_tools = LocalProvider()

@shared_tools.tool
def shared_greet(name: str) -> str:
    return f"Hello from the shared provider, {name}!"

@shared_tools.tool
def shared_farewell(name: str) -> str:
    return f"Goodbye from the shared provider, {name}!"

# Attach the shared provider to multiple servers
server_a = FastMCP("ServerA", providers=[shared_tools])
server_b = FastMCP("ServerB", providers=[shared_tools])




# Filesystem provider

"""
FileSystemProvider 
scans a directory for Python files and automatically registers functions decorated with
 @tool, @resource, or @prompt
"""

from pathlib import Path
from fastMCP.server.providers import FileSystemProvider

mcp = FastMCP("FileSystemServer", providers=[FileSystemProvider(Path(__file__).parent / "mcp")])

### Other file

from fastmcp.tools import Tool

@Tool
def greet(name: str) -> str:
    return f"Hello, {name}!"


""" Decorators

​
Decorators
FastMCP provides standalone decorators that mark functions for discovery

The decorator supports all standard tool options

@tool from fastmcp.tools, 
@resource from fastmcp.resources,
@prompt from fastmcp.prompts


"""

""" Directory structure

The provider recursively scans the specified directory for Python files.

for example
mcp/
    tools/
        greet_tool.py
        math_tools.py
    resources/
        config_resource.py
        data_resource.py
    prompts/
        welcome_prompt.py
        farewell_prompt.py
"""

"""Discovery rules

file extension: Only .py files are scanned for components.
__init__.py: Files named __init__.py are ignored to allow for package structuring without registering components.
__pycache__: Skipped
Private Functions: Functions starting with an underscore (_) are ignored
No decorator: Only functions decorated with @tool, @resource, or @prompt are registered as components.
Mutliple components: A single file can contain multiple decorated functions, and all will be registered.
"""


"""Example Project 
    Shows recommeded project structure when using FileSystemProvider
"""


### Skills Providers

""" Agent skills are directories that contain instrucctions
 and supporting files that teach an AI assistant how to perform specefic tasks"""

"""The Skills Provider exposes these skill directories as MCP resources,
making skills discoverable and sharable across different AI tools and clients"""

""" The skills provider expose each skill as a set of MCP resoucers"""


from pathlib import Path

from fastmcp import FastMCP

from fastmcp.server.providers.skills import SkillsDirectoryProvider

mcp = FastMCP("SkillsServer")
mcp.add_provider(SkillsDirectoryProvider(roots=Path.home() / ".claude" / "skills"))


""" Skill structure

A skill is a directory containing a main instruction file (default SKILL.md) and any number of supporting files

The directory name becomes the skill identifier.


"""

""" Vendor Providesr

FASMCP includes pre configured providers for popular AU coding tools.
"""

""" Custom Providers

Custom providers let source components from anywhere, like databases, APIs, or other servers.

If its possible to write Python code to fetch or generate a component, its possible to wrape it in a custom provider.
"""

"""
Custom providers are useful when Database-backed tool
API-Backed resouces
Configuration-driver compoents
multi-tenant systems
plugins systems
"""

### Providers vs middleware

"""Providers are objets that source components

Middleware intercepts individual requests, its more focused on logging, rate limiting, auth, etc"""

### Provider interface

from collections.abc import Callable, Sequence
from fastmcp.server.providers import Provider
from fastmcp.tools import Tool
from fastmcp.resources import Resource
from fastmcp.prompts import Prompt

class MyProvider(Provider):
    async def _list_tools(self) -> Sequence[Tool]:
        """ Return all tools this provider offers."""
        return []

    async def _list_resources(self) -> Sequence[Resource]:
        """ Return all resources this provider offers."""
        return []

    async def _list_prompts(self) -> Sequence[Prompt]:
        """Return all prompts this provider offers."""
        return []
    


### Simple Provider

class DictProvider(Provider):
    def __init__(self, tools: dict[str, Callable]):
        super().__init__()
        self._tools = [Tool.from_function(func, name=name) for name, func in tools.items()]

    async def _list_tools(self) -> Sequence[Tool]:
        return self._tools

def add(x: int, y: int) -> int:
    " Return the sum of x and y"
    return x + y

def multiply(x: int, y: int) -> int:
    " Return the product of x and y"
    return x * y

mcp = FastMCP("Calculator", providers=[DictProvider({"add": add, "multiply": multiply})])

#### Mounting servers

"""Mouting  allows to combine multiple FASTMCP servers into one,

Large Applications benefit from modular organization.

Modularity: Each server can focus on a specific domain or set of functionalities, making it easier to develop and maintain.
Reusability: Servers can be reused across different projects or contexts by mounting them into new servers.
Teamwork: Different teams can work on separate servers and then combine their work by mounting, reducing conflicts and improving collaboration.
Organization: Mounting helps keep the overall architecture organized by grouping related tools, resources, and prompts together within their respective servers.
"""

### Basic Mounting

from fastmcp import FastMCP

# create focused subserver

math_server = FastMCP("MathServer")

@math_server.tool
def add(x: int, y: int) -> int:
    return x + y
@math_server.tool
def multiply(x: int, y: int) -> int:
    return x * y

main_server = FastMCP("MainServer")
main_server.mount(math_server)

## Namespacing

""" To avoid name conflicts when mounting servers, you can use namespaces"""
weather = FastMCP("Weather")
calendar = FastMCP("Calendar")

@weather.tool
def get_data() -> str:
    return "Weather data"

@calendar.tool
def get_data() -> str:
    return "Calendar data"

main = FastMCP("Main")
main.mount(weather, namespace="weather")
main.mount(calendar, namespace="calendar")

""" Tag filtering
Parent Server tag filers apply recursively to mounted servers"
"""

""" When mounting multiple servers, with the same namespace the most recently mounted server 
takes precedence for conflicting components names:"""

