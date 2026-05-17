# test_retrieval.py

import sys
from pathlib import Path

# Add src to path so imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.retrieval import retrieval_node
state = {
    "question": "how do transformers work?",
    "sub_queries": ["self attention transformers", "transformer architecture"],
    "searched_queries": [],
    "papers": [],
    "claims": [],
    "report": None,
    "iteration": 1,
    "max_iterations": 3,
    "context_summary": None,
    "memory_context": [],
    "compressed_summary": None,
    "needs_more_info": False,
}

result = retrieval_node(state)
print(f"\n✓ Found {len(result['papers'])} papers")
print(f"✓ Searched: {result['searched_queries']}")