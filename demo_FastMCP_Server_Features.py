# Backround Tasks
""" 
For operations that take seconds or minutes, this creates a poor user experience.
 The MCP background task protocol solves this by letting clients::

    Start an operation and receive a task ID immediately
    Track progress as the operation runs
    Retrieve the result when ready

FastMCP handles all of this for you. Add task=True to your decorator, and your function gains full background execution with progress reporting, distributed processing, and horizontal scaling.
"""
"""Add task=True to any tool, resource, resource template, or prompt decorator. This marks the component as capable of background execution.
"""

@mcp.tool(task=True)
async def long_running_operation(param: str, ctx: Context) -> str:
    total_steps = 10
    for step in range(total_steps):
        # Simulate work
        await asyncio.sleep(1)
        # Report progress
        ctx.report_progress((step + 1) / total_steps * 100, f"Step {step + 1} of {total_steps} completed")
    return f"Operation completed with param: {param}"

"""Execution modes allows control ver task execution behavior.
using TaskConfig

required
forbiden
optional
"""
from fastmcp import FastMCP
from fastmcp.server.task import TaskConfig

mcp = FastMCP("Server demo" )

@mcp.tool(task=TaskConfig(mode="optional"))
async def flexible_task() -> str:
    return "Works either way"

@mcp.tool(task=TaskConfig(mode="required"))
async def must_be_background() -> str:
    return "Only runs as a background task"

@mcp.tool(task=TaskConfig(mode="forbidden"))
async def sync_only() -> str:
    return "Never runs as background task"

""" To enable backround task support for all components by default, set the default_task_mode parameter when creating the FastMCP server instance.

If your server defines any synchronous tools, resources, or prompts, 
you will need to explicitly set task=False on their decorators to avoid an error.

"""
mcp = FastMCP("Server demo", default_task_mode="optional")


"""Progress Reporting
Tools running as background tasks can report progress to clients using the Context.report_progress method.
This allows clients to provide feedback to users on long-running operations."""

from fastmcp import FastMCP
from fastmcp.dependencies import Progress

mcp = FastMCP("MyServer")

@mcp.tool(task=True)
async def process_files(files: list[str], progress: Progress = Progress()) -> str:
    await progress.set_total(len(files))

    for file in files:
        await progress.set_message(f"Processing {file}")
        # ... do work ...
        await progress.increment()

    return f"Processed {len(files)} files"

"""
Progress API

await progress.set_total(n) — Set the total number of steps
await progress.increment(amount=1) — Increment progress
await progress.set_message(text)


"""
### Dependency Injection
# Inject runtime values like HTTP requests, access tokens, and custom dependencies into your MCP components.

""" TODO: Complete Dependency Injection section """

""" Elicitation
request structured input from users during tool execution using FastMCP's elicitation features.

Elicitation enables tools to pause execution and request specific information from users:

    Missing parameters: Ask for required information not provided initially
    Clarification requests: Get user confirmation or choices for ambiguous scenarios
    Progressive disclosure: Collect complex information step-by-step
    Dynamic workflows: Adapt tool behavior based on user responses

    For example, a file management tool might ask “Which directory should I create?” or a data analysis tool might request “What date range should I analyze?”
    
"""

from fastmcp import FastMCP, Context
from dataclasses import dataclass

mcp = FastMCP("Elicitation Demo")

@dataclass
class UserInfo:
    name: str
    age: int

@mcp.tool
async def gather_user_info(ctx: Context) -> str:

    result = await ctx.elicit(
        message="Please provide your name and age.",
        response_type=UserInfo)
    if result.action == "Accept":
        user_info: UserInfo = result.data
        return f"Hello {user_info.name}, you are {user_info.age} years old."
    elif result.action == "DDecline":
        return "Operation cancelled by user."
    else:
        return "No response received."
    
""" The elicitation result contains an action field indicating how the user responded:

accept	User provided valid input—data is available in the data field
decline	User chose not to provide the requested information
cancel	User cancelled the entire operation"""

# LifeSpans

""" Lifespans let you manage stateful resources that persist across multiple tool invocations within a session.
For example, you might use a lifespan to maintain a database connection, cache data, or store user preferences during a session.
Lifespans are defined using the @mcp.lifespan decorator. You can specify setup and teardown functions that run when the lifespan starts and ends, respectively.
"""

"For Example, You do not wanto to reconnect to a Machine learning model for every tool call, "
"so you create a lifespan to manage the connection."
""

### MIddleWare

""" Middleware allows you to intercept and modify requests and responses as they pass through the FastMCP server.
You can use middleware to implement cross-cutting concerns like logging, authentication, rate limiting, and request/response transformation.
"""

from fastmcp import FastMCP
from fastmcp.server.middleware import Middleware, MiddlewareContext

class LoggingMiddleware(Middleware):
    async def on_message(self, context: MiddlewareContext, call_next):
        print(f"→ {context.method}")
        result = await call_next(context)
        print(f"← {context.method}")
        return result

mcp = FastMCP("MyServer")
mcp.add_middleware(LoggingMiddleware())

from fastmcp import FastMCP
from fastmcp.server.middleware.logging import LoggingMiddleware

parent = FastMCP("Parent")
parent.add_middleware(AuthMiddleware())  # Runs for ALL requests

child = FastMCP("Child")
child.add_middleware(LoggingMiddleware())  # Only runs for child's tools

parent.mount(child, namespace="child")

""" FastMCP includes production ready middleware for logging, authentication, rate limiting, and more."""

# Pagination

""" 
When a server exposes many tools, resources, or prompts,
return them all in a single response can be inefficient and overwhelming for clients.
FastMCP supports pagination to help clients navigate large sets of components.

Consider enabling it when:

    Your server dynamically generates many components (e.g., from a database or file system)
    Memory usage is a concern for clients
    You want to reduce initial response latency

    For servers with a fixed, modest number of components (fewer than 100), pagination adds complexity without meaningful benef

    
    """
# Progress Reporting

"""Update clients on long-running operations using the Context.report_progress method within background tasks."""

"""Progress reporting allows MCP tools to notify clients about the progress of long-running operations. 
Clients can display progress indicators and provide better user experience during time-consuming tasks.
"""
"""Progess Patterns
PErcentage: 0-100
Absolute: steps by completed/total
Indeterminate= no specific progress, just activity
"""

### Samplig

""" A tool can call a llm with sampling parameters to get varied outputs.
Usuario → LLM → Tool → (Tool llama OTRO LLM) → Resultado
"""

#result = await ctx.sample("Resume this")
#return result.text


### Storage Backend

""" FastMCP supports various storage backends to persist data such as tool definitions, user sessions, and logs."""