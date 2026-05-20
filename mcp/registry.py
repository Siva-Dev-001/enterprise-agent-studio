TOOL_REGISTRY = {}

def register_tool(name):
    def wrapper(func):
        TOOL_REGISTRY[name] = func
        return func
    return wrapper