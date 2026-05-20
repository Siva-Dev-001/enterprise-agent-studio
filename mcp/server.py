from fastapi import FastAPI
from mcp.tools import run_tool

app = FastAPI()

@app.post("/run-tool")
def execute_tool(payload: dict):
    tool_name = payload["tool"]
    input_data = payload["input"]
    return run_tool(tool_name, input_data)