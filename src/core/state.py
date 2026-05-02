from typing_extensions import TypedDict
from typing import Optional, Any

class ClaimObject(TypedDict):
    paper_id: str
    title:str
    core_claims:list[str]
    methodology:str
    key_findings:list[str]
    limitations:str


class ConstextSummary(TypedDict):
    findings:list[str]
    gaps:list[str]
    ruled_out: list[str]
    follow_up_queries: list[str]

class MemoryContext(TypedDict):

    type: str
    content: str
    source: str

class AgentState(TypedDict):

    question: str
    sub_questions: list[str]
    papers: list[dict[str,Any]]
    claims: list[ClaimObject]
    reposrt: Optional[str]

    iteration: int
    max_iterations: int
    context_summary: Optional[ConstextSummary]
    needs_more_info: bool
    searched_queries: list[str]

    memory_context: list[MemoryContext]
    compresses_summary: Optional[str]