#Http
from fastapi import FastAPI
from fastapi_mcp import FastApiMCP

app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/add/{a}/{b}")
def add(a: float, b: float):
    """Adds two numbers."""
    return {"Result_add": a + b}

@app.post("/subtract/{a}/{b}")
def subtract(a: float, b: float):

    """Subtracts the second number from the first."""
    return {"Result_subtract": a - b}

@app.post("/multiply/{a}/{b}")
def multiply(a: float, b: float):
    """Multiplies two numbers."""
    return {"Result_multiply": a * b}

@app.post("/divide/{a}/{b}")
def divide(a: float, b: float):
    """Divides two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return {"Result_divide": a / b}

mcp = FastApiMCP(app, name="Calculator MCP")
mcp.mount_http()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)

