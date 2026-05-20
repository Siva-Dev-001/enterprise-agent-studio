import requests

MCP_URL = "http://localhost:8001/run-tool"

def run_tool(tool, data):
    return requests.post(MCP_URL, json={
        "tool": tool,
        "input": data
    }).json()