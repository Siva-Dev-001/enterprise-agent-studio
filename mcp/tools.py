from mcp.registry import TOOL_REGISTRY

@TOOL_REGISTRY.get("csv_summary", lambda x: None)
def csv_summary(data):
    return {"rows": len(data)}


def run_tool(name, input_data):
    return TOOL_REGISTRY[name](input_data)