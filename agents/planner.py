from llm.azure_openai import call_llm

def planner(task):
    prompt = f"Break task into steps:\n{task}"
    return call_llm(prompt)