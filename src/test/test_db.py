# test_db.py — run this file to test each piece

import sys
from pathlib import Path

# Allow `python test/test_db.py` from `src/` without PYTHONPATH=.
_src = Path(__file__).resolve().parent.parent
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from db.vector import (
    init_db,
    get_embedding,
    get_batch_embedding,
    upsert_papers,
    vector_search,
)
# Test 1 — database connection and table creation
print("Testing init_db...")
init_db()
print("✓ init_db passed")

# Test 2 — single embedding
print("Testing embed...")
vec = get_embedding("hello world")
assert len(vec) == 1536, "Wrong embedding size"
assert isinstance(vec[0], float), "Embedding should be floats"
print(f"✓ embed passed — got {len(vec)} dimensions")

# Test 3 — batch embedding
print("Testing embed_batch...")
vecs = get_batch_embedding(["hello", "world", "transformers"])
assert len(vecs) == 3, "Should get 3 embeddings"
assert len(vecs[0]) == 1536
print(f"✓ embed_batch passed — got {len(vecs)} embeddings")

# Test 4 — insert papers
print("Testing upsert_papers...")
fake_papers = [
    {
        "id": "test-001",
        "title": "Test Paper on Transformers",
        "abstract": "We study transformer architectures and attention mechanisms.",
        "authors": ["Alice", "Bob"],
        "published": "2024-01-01",
        "categories": ["cs.LG"]
    }
]
upsert_papers(fake_papers)
print("✓ upsert_papers passed")

# Test 5 — search
print("Testing vector_search...")
results = vector_search("attention mechanism transformers", top_k=5)
assert len(results) > 0, "Should find at least the test paper"
assert "title" in results[0], "Result should have title"
assert "similarity" in results[0], "Result should have similarity score"
print(f"✓ vector_search passed — found {len(results)} results")
print(f"  Top result: {results[0]['title']} (similarity: {results[0]['similarity']:.3f})")