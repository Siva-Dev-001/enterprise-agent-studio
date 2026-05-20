from langgraph.graph import StateGraph
from agents.planner import planner
from agents.rag_agent import rag_agent
from agents.supervisor import supervise

class State(dict):
    pass


def build_graph():
    g = StateGraph(State)

    def plan_node(s):
        s["plan"] = planner(s["task"])
        return s
    def rag_node(s):
        s["context"] = rag_agent(s["task"])
        return s

    def supervise_node(s):
        s["final"] = supervise(s)
        return s

    g.add_node("planner", plan_node)
    g.add_node("rag", rag_node)
    g.add_node("supervisor", supervise_node)

    g.set_entry_point("planner")
    g.add_edge("planner", "rag")
    g.add_edge("rag", "supervisor")

    return g.compile()