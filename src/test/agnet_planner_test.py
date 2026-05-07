# test_planner.py
from agents.planner import planner_node

state = {
    "question": "how does attention work in transformers?",
    "sub_queries": [],
    "searched_queries": [],
    "context_summary": None,
    "iteration": 1,
    "max_iterations": 3,
    "papers": [],
    "claims": [],
    "report": None,
    "memory_context": [],
    "compressed_summary": None,
    "needs_more_info": False,
}

result = planner_node(state)
print(result["sub_queries"])