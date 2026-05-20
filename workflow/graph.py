from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END


# ── Bug 1 fixed: TypedDict instead of plain dict ─────────────────────────────
class State(TypedDict, total=False):
    task:    str
    plan:    Optional[str]
    context: Optional[str]
    final:   Optional[str]
    error:   Optional[str]


# ── Safe agent imports with fallback ─────────────────────────────────────────
try:
    from agents.planner    import planner
    from agents.rag_agent  import rag_agent
    from agents.supervisor import supervise
except ImportError as e:
    raise ImportError(
        f"Failed to import agents: {e}\n"
        "Ensure agents/planner.py, agents/rag_agent.py, "
        "agents/supervisor.py exist and agents/__init__.py is present."
    )


# ── Nodes: return new dict, don't mutate in place (Bug 4 fixed) ──────────────
def plan_node(state: State) -> State:
    try:
        return {**state, "plan": planner(state["task"])}   # Bug 4: spread into new dict
    except Exception as e:
        return {**state, "error": f"planner failed: {e}"}  # Bug 5: catch and propagate


def rag_node(state: State) -> State:
    try:
        return {**state, "context": rag_agent(state["task"])}
    except Exception as e:
        return {**state, "error": f"rag_agent failed: {e}"}


def supervise_node(state: State) -> State:
    try:
        return {**state, "final": supervise(state)}
    except Exception as e:
        return {**state, "error": f"supervisor failed: {e}"}


# ── Conditional routing: skip to END if error occurred ───────────────────────
def should_continue(state: State) -> str:
    return "end" if state.get("error") else "continue"


# ── Graph builder ─────────────────────────────────────────────────────────────
def build_graph():
    g = StateGraph(State)

    g.add_node("planner",    plan_node)
    g.add_node("rag",        rag_node)
    g.add_node("supervisor", supervise_node)

    g.set_entry_point("planner")

    # planner → check error → rag or END
    g.add_conditional_edges(
        "planner",
        should_continue,
        {"continue": "rag", "end": END}     # Bug 2 fixed: END edge added
    )

    # rag → check error → supervisor or END
    g.add_conditional_edges(
        "rag",
        should_continue,
        {"continue": "supervisor", "end": END}
    )

    # supervisor always exits to END
    g.add_edge("supervisor", END)            # Bug 2 fixed

    return g.compile()


# ── Entry point ───────────────────────────────────────────────────────────────
# if __name__ == "__main__":
#     graph = build_graph()
#     result = graph.invoke({"task": "Explain transformer models"})

#     if result.get("error"):
#         print(f"Graph failed: {result['error']}")
#     else:
#         print(f"Final output: {result['final']}")