"""Prompts"""

"""Prompts are reusable message templates that help LLMs generate structured, purposeful responses. FastMCP simplifies defining these templates, primarily using the @mcp.prompt decorator."""

"""
Prompts provide parameterized message templates for LLMs. When a client requests a prompt:

    FastMCP finds the corresponding prompt definition.
    If it has parameters, they are validated against your function signature.
    Your function executes with the validated inputs.
    The generated message(s) are returned to the LLM to guide its response.

This allows you to define consistent, reusable templates that LLMs can use across different clients and contexts.
"""


""" To define a prompt, use the @mcp.prompt decorator on a function
"""


# Basic prompt

@mcp.prompt
def ask_about_topic(topic: str) -> str:
    """Generates a user message asking for an explanation of a topic."""
    return f"Can you please explain the concept of '{topic}'?"

# Prompt returning multiple messages
@mcp.prompt
def generate_code_request(language: str, task_description: str) -> list[Message]:
    """Generates a conversation for code generation."""
    return [
        Message(f"Write a {language} function that performs the following task: {task_description}"),
        Message("I'll help you write that function.", role="assistant"),
    ]

""" Prompt arguments are infered from the function signature. It can be overriden using the
    parameters argument to @mcp.prompt"""

""

"""
name
title
description
tags
enable
"""
#Example
@mcp.prompt(
    name="detailed_explanation_prompt",
    title="Detailed Explanation Prompt",
    description="Generates a detailed explanation for a given topic.",
    tags=["explanation", "detailed"],
    enable=True
)
def detailed_explanation(topic: str, detail_level: int = 5) -> str:
    """Generates a detailed explanation of a topic."""
    return f"Please provide a detailed explanation of '{topic}' with a detail level of {detail_level}."

""" MCP specificationn requiers that all prompt arguments be passed as strings, FastMCPP allow the use
of typed annotations"""

""" FastMCP automatically converts prompt arguments to the specified types

, FastMCP:

    Automatically converts string arguments from MCP clients to the expected types
    Generates helpful descriptions showing the exact JSON string format needed
    Preserves direct usage - you can still call prompts with properly typed arguments

    
"""
"""################################################################"""
"""#### Keep your type annotations simple when using this feature.
 Complex nested types or custom classes may not convert reliably from JSON strings.
   The automatically generated schema descriptions are the only guidance users receive 
   about the expected format.
   Good choices: list[int], dict[str, str], float, bool Avoid: Complex Pydantic models, deeply nested structures, custom classes
#################################################################"
"""

"""Promto funcionts must return  one of these types:
"List[Message]", "str"]
str
PromptResult
"""

"""Message 

provides a user-friendly wrapper for prompt messages with automatic serialization

"""

from fastmcp.prompts import Message

# String content (user role by default)
Message("Hello, world!")

# Explicit role
Message("I can help with that.", role="assistant")

# Auto-serialized to JSON text
Message({"key": "value"})
Message(["item1", "item2"])

"""Prompt Result
gives explicit control over the prompt responses, multiple messages, roles, metadata, and more."""


@mcp.prompt
def code_review(code: str) -> PromptResult:
    """Returns a code review prompt with metadata."""
    return PromptResult(
        messages=[
            Message(f"Please review this code:\n\n```\n{code}\n```"),
            Message("I'll analyze this code for issues.", role="assistant"),
        ],
        description="Code review prompt",
        meta={"review_type": "security", "priority": "high"}
    )

""" Required vs optional parameters
By default, all prompt parameters are required. 
You can make parameters optional by providing default values in"""

@mcp.prompt
def data_analysis_prompt(data_uri:str, analysis_type: str = "summary") -> str:
    """Generates a data analysis prompt."""
    prompt = f"Please perform a '{analysis_type}' analysis on the data found at {data_uri}."
    return prompt

""" Component Visibility

You can control which prompts are enabled for clients using server-level enabled control. 
Disabled prompts don’t appear in list_prompts and can’t be called.
 """

from fastmcp import FastMCP

mcp = FastMCP("MyServer")

@mcp.prompt(tags={"public"})
def public_prompt(topic: str) -> str:
    return f"Discuss about: {topic}"

@mcp.prompt(tags={"internal"})
def internal_prompt() -> str:
    return "Internal system prompt"

# Disable specific prompts by key
mcp.disable(keys={"prompt:internal_prompt"})

# Disable prompts by tag
mcp.disable(tags={"internal"})

# Or use allowlist mode - only enable prompts with specific tags
mcp.enable(tags={"public"}, only=True)

"""Async Prompts
FastMCP supports async def and def functions as prompts

"""

@mcp.prompt
async def async_prompt(topic: str) -> str:
    return f"Async discussion about: {topic}"

@mcp.prompt
def sync_prompt(topic: str) -> str:
    return f"Sync discussion about: {topic}"

""" FastMCP allows MCP Context to be passed to prompts for advanced use cases."""
