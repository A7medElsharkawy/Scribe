from ntpath import exists
from time import sleep
from  core.state import AgentState
from db.vector import vector_search,upsert_papers
from concurrent.futures import ThreadPoolExecutor, as_completed
import arxiv
import time



def fetch_arxiv_papers(query:str, max_results:int=10)->list[dict]:

    print(f"[arxiv] fetching: {query[:50]}...")
    client = arxiv.Client(delay_seconds=1, num_retries=2)
    search = arxiv.Search(
        query = query,
        max_results = 20,
        sort_by = arxiv.SortCriterion.Relevance,
        sort_order = arxiv.SortOrder.Descending,
    )
    papers = []
    try:
        for result in client.results(search):
            papers.append({
                'id': result.entry_id.split("/")[-1],
                'title': result.title,
                'abstract': result.summary,
                'authors': [author.name for author in result.authors],
                'published': result.published.date(),
                'categories': result.categories,           
            })
    except Exception as e:
        print(f"[arxiv] error fetching: {query[:50]}: {e}")
        return []
    print(f"[arxiv] found {len(papers)} papers for: {query[:50]}")
    return papers


def deduplicate(papers:list[dict]):
    seen = set()
    out = []
    for p in papers:
        v = p['id'].split('v')[0]
        if v not in seen:
            seen.add(v)
            out.append(p)
    return out


def retrieval_node(state: AgentState) -> dict:

    sub_queries = state.get('sub_queries',[])
    searched_queries = state.get('searched_queries',[])
    existing_papers = state.get('papers',[])

    new_queries  =[ q for q in sub_queries if q not in searched_queries]

    if not new_queries:
        print("[retrieval] no new queries to search")
        return state

    existing_id = {p['id'].split('v')[0] for p in existing_papers}
    all_papers = list(existing_papers)
    for query in new_queries:
        papers= fetch_arxiv_papers(query)
        for p in papers :
            if p['id'].split('v')[0] not in existing_id:
                all_papers.append(p)
        time.sleep(3)
    new_papers = deduplicate([ p for p in all_papers if p['id'].split('v')[0] not in existing_id])

    if new_papers:
        upsert_papers(new_papers)
        print(f"[retrieval] saved {len(new_papers)} new papers to database")
    
    return {
    **state,
    "papers": all_papers,
    "searched_queries": searched_queries + new_queries,
    }



        
