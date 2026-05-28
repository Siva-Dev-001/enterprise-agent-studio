# def supervise(output):
#     if not output:
#         return "FAILED"
#     return output

from llm.gemini import call_llm

def supervise(state):

    prompt = f"""
    Generate a professional business summary.

    TASK:
    {state.get('task')}

    PLAN:
    {state.get('plan')}

    RAG CONTEXT:
    {state.get('context')}
    """

    return call_llm(prompt)