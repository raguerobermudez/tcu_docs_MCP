import json
from pathlib import Path
from fastMCP import FastMCP
from fastMCP.exceptions import ToolError

import time
from datetime import datetime, timezone
from typing import Optional, Annotated
from pydantic import BaseModel, Field

"""Resorces represent data or files that can be utilized by tools within the FastMCP framework"""

"""Resources provide ****Read only" access to data or files for tools to utilize within the FastMCP framework.

    When a client request a resource URI
    FastMCP finds the correspondig source definition
    if it's dynamic (defined by a function) it calls the function to get the data
    The context (Text, JSON, File, etc) is then passed to the tclient tool that requested it.

    Allows LLM to access files, databases content, configuration, etc,
    """

"""Resource decorator"""

""" URI the first argument to @mcp.resource is the unique identifier for the resource. The client uses to request data

    Lazy Loading " The decorated funcion is only executed when a client specifically requests the resource URI.

    Infered Metadata, Resource Name, resource description
"""

""" Decorator arguments

    uri unique identifier for the resource
    name optional human readable name
    description optional description of the resource
    mime_type optional mime type of the resource (text/plain, application/json, etc) Explicitly setting mime type helps clients interpret the data correctly
    tags optional set of tags for categorizing and searching resources
    ***Enable*** is deprecated in V3 use mcp.enable / mcp.disable instead to enable or disable resources globally or per tool
    annotations
    """

""" Using resources with methods"""
""" Return values
    str: Send as texstResourcesContents with mine_type="text/plain"
    bytes: Base64 encoded and sent as BlobResourceContents.
        You should specify an appropriate mime_type (e.g., "image/png", "application/octet-stream").
    ResourceResult: Allows full control over the resource content and metadata.

    TO return structured data use JSON serialization using json.dumps()
     to convert your data to a JSON string and return it with the appropriate mime_type.

    ***ResourceResult*** is new in V3


"""
"""Component Visibility New in V3

    You can control which resources are enable for clients using sever-level enable/disable contro

    Disable resources do not apper in the resource list and cannot be requested by clients

"""
"""

    FastMCP supports async and def resource functions.
"""

"""Resources classes
    You can directly registrer predefined resource classes using mcp.add_resource() and concrete Resource subclasses.
    

"""
""" MCP Context """
import json
import fastMCP from FastMCP

"""Basic dynamic resource returning text data"""

@mpc.resource("resource://greeeting")
def greeting_resource() -> str:
    return "Hello world!"

@mcp.resource("data://config")
def get_config() -> str:
    return json.dumps({
        "dark_theme": True,
        "version": "1.2.3",
        "features": "tools, resources, annotations"
    })

@mcp.resource("data://public",tags={"public"})
def get_public_data() -> str:
    return "This is public data accessible to all clients."

@mcp.resource("data://secret", tags={"internal"})
def get_secret_data() -> str:
    return "This is secret data accessible only to internal clients."

# Disable specific resources by key
mcp.disable(keys={"resource:data//secret"})

# Disable resources by tag
mcp.disable(tags={"internal"})

mcp.enable(tags={"public"}, only=True)


""" Resource classes

    TextResource: For simple string content.
    BinaryResource: For raw bytes content.
    FileResource: Reads content from a local file path. Handles text/binary modes and lazy reading.
    HttpResource: Fetches content from an HTTP(S) URL (requires httpx).
    DirectoryResource: Lists files in a local directory (returns JSON).
    (FunctionResource: Internal class used by @mcp.resource).

    Use then whe the content is static or when you need more control over metadata like mime type, tags, etc.

"""
# Exposing a static file directly
from pathlib import Path
from fastMCP.resources.file_resource import FileResource, TextResource, DirectoryResource

readme_path = Path("./README.md").resolve()
if readme_path.exists():
    # Use a file://uri scheme to indicate it's a file resource
    readme_resource = FileResource(
        uri=f"file://{readme_path.as_posix()}",
        path=readme_path,
        name="Project README",
        description="The README file for the project",
        mime_type="text/markdown",
        tags={"documentation", "public"}
    )
    mcp.add_resource(readme_resource)

# Exposing simple, predefined text resource

simple_text_resource = TextResource(
    uri="text://simple-note",
    name="important-note",
    description="A simple text note resource",
    tags={"note"}
)
mcp.add_resource(simple_text_resource)

# Exposing a diretory lsiting

data_dir_path = Path("./data").resolve()
if data_dir_path.exists() and data_dir_path.is_dir():
    data_listing_resource = DirectoryResource(
        uri="dir://data-files",
        path=data_dir_path,
        name="Data Files",
        description="A directory listing of data files",
        recursive=False)
    mcp.add_resource(data_listing_resource)

""" Annotations

 FastMCP allows you to add specialized metadata to your resources through annotations.
 These annotations communicate how resources behave to client applications without consuming token context in LLM prompts.

"""

""" Resource Templates

Resources templates allow clients to request resources whose content depends on parameters embbedd in the URI

Resources templates share most configuration options with regular resources, but add the ability to define URI patterns
that map to function parameters"""

""" Clients can request resource URIs with specific values substituted into the template placeholders.
When a client requests a resource URI that matches a template, FastMCP extracts the parameter values from the URI
and calls the decorated function with those values to generate the resource content dynamically.
This allows for flexible and dynamic resource generation based on client requests."""


""" RFC 6570 - URI Template Syntax
    Simple string expansion {var}
    Reserved expansion {+var}
    Fragment expansion {#var}
    Label expansion with dot-prefix {.var}
    Path segment expansion {/var}
    Path-style parameter expansion {;var}
    Form-style query expansion {?var}
    Form-style query continuation {&var}

    """
# Template uri includes {city}
@mcp.resourcer("weather://{city}/current")
def get_weather_resource(city: str) -> str:
    return jdson.dumps({
        "city": city.capitalize(),
        "temperature_celsius": 22,
        "condition": "Sunny",
        "unit": "celsius"})

# Template with multiple parameters and annotations
@mcp.resource("repos://{owner}/{repo}/info", annotations={"readOnlyHint": True})
def get_repo_info(owner: str, repo: str) -> str:
    return json.dumps({
        "owner": owner,
        "repo": repo,
        "full_name": f"{owner}/{repo}",
        "stars": 150,
        "forks": 30,
        "open_issues": 5
    })


"""Wildcard Parameters"""

""" Resource templates supong wildcard parameters thath can match multiple segments in a URI path.

    Wildcards paremetes are useful when
    working with file paths, hierarchical data
    Creating APIs that need to capture variable-length path segments
    Building URL-like patterns similar to REST APIs
"""
# Standard parameter matches a single segment
@mcp.resource("files://{filename")
def get_file_resource(filename: str) -> str:
    return f"Requested file: {filename}"

# Wildcard parameter matches multiple segments
@mcp.resource("files://{filepath*}")
def get_full_file_resource(filepath: str) -> str:
    return f"Requested full file path: {filepath}"

# Mixing standard and wildcard parameters
@mcp.resource("projects://{owner}/{project_path*}/template.py")
def get_project_template(owner: str, project_path: str) -> dict:
    return {
        "owner": owner,
        "path": project_path + "/template.py",
        "content": f"File at {project_path}/template.py in {owner}'s repository"
    }

""" Query Parameters

Query paramets must be optiional funcion parameters with default values.
while path parameters map to required function parameters"""

from fastmcp import FastMCP

#Basic query parameter
@mcp.resource("data://{id}{?format}")
def get_data_resource(id: str, format: str = "json") -> str:
    if format == "xml":
        return f"<data id='{id}'>This is XML data</data>"
    else:
        return json.dumps({"id": id, "data": "This is JSON data"})
    
# Error Handling
""" Standard Python exceptions raised within resource functions are caught by FastMCP.
All exeptions are loggged and converted into MCP error

"mas_erro_details=True

use ResourceError to explicitly control what error information is sent to clients:"""

@mcp.resource("resource://safe-error")
def fail_with_detailed_error() -> str:
    raise ResourceError("Detailed error message for clients")

@mcp.resource("resource://masked-error")
def fail_with_masked_error() -> str:
     # This message would be masked if mask_error_details=True
     raise ValueError("Sensitive internal file path: /etc/secrets.conf")
@mcp.resource("data://{id}")
def get_data_by_id(id: str) -> str:
    if id == "secure":
       raise ValueError("Access to secure data is forbidden")
    elif id == "missing":
        raise ResourceError(f"Data with ID {id} not found")
    return json.dumps({"id": id, "data": "Here is your data"})