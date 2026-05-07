from core import AgentState
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
load_dotenv()


SYSTEM_PROMPT = """You are a research planning agent. Your job is to decompose a 
research question into 4-6 distinct sub-queries that together provide full coverage 
of the topic.

Each sub-query should target a different facet:
- Core methodology / technical approach
- Specific applications or use cases
- Comparisons with alternative approaches
- Known limitations or failure modes
- Open problems or future directions
- Empirical results / benchmarks

Rules:
- Sub-queries must be SHORT keyword strings suitable for arXiv search (5-8 words max)
- No full sentences or question format
- No two sub-queries should overlap significantly
- Return ONLY a JSON array of strings, no preamble, no markdown fences
"""

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])   
def planner_node (state: AgentState):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        messages=[
            {"role":"system","content":SYSTEM_PROMPT},
            {"role": "user", "content": f"Break this question into sub-queries: {state['question']}"}
        ]
    )

    content = response.choices[0].message.content.strip()
    content = content.replace("```json","").replace("```","").strip()
    sub_queries = json.loads(content)

    print(f"[planner] decomposed into {len(sub_queries)} sub-queries:")
    for i, q in enumerate(sub_queries, 1):
        print(f"  {i}. {q}")

    return {
        **state,
        "sub_queries":sub_queries
    }

