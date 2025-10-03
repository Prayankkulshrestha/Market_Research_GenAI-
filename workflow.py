from task_nodes import *
import asyncio
import logging
from langgraph.graph import StateGraph,END
import config
from graph_state import AgentState
from cache_utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def build_workflow():
    workflow = StateGraph(AgentState)

    workflow.add_node("generate_query",generate_search_query)
    workflow.add_node("web_search",perfrom_web_search)
    workflow.add_node("extract_products",extract_products_name)
    workflow.add_node("summaize_products",product_summary)
    workflow.add_node("clean_products",clean_products)
    workflow.add_node("final_summary",create_final_summary)

    workflow.set_entry_point("generate_query")
    workflow.add_edge("generate_query","web_search")
    workflow.add_edge("web_search","extract_products")
    workflow.add_edge("extract_products","summaize_products")
    workflow.add_edge("summaize_products","clean_products")
    workflow.add_edge("clean_products","final_summary")
    workflow.add_edge("final_summary",END)

    return workflow.compile()

async def run_graph_async(state:dict):
    """
    run the complied Langgraph, Behaviour,
    - if final summary exist in cache => return cache result
    - else run the graph (node level cache)
    """
    if not(config.START_DATE and config.END_DATE):
        raise ValueError("Please set start date and end date")
    category = state.get("category")
    if not category:
        raise ValueError("Please ensure state must have one category")
    
    cache_final = get_from_cache("create_final_summary",category,config.START_DATE,config.END_DATE)
    if cache_final:
        logger.info("[Graph] Final summary found in state in cache - return immediately")
        result_state = {**state,**cache_final}
        result_state["_from_cache"] = True
        return result_state
    
    graph = build_workflow()
    logger.info("[graph] NO cache - start graph execution ")
    res = await graph.ainvoke(state)
    res["_from_cache"] = False
    return res

def run_graph(state:dict):
    return asyncio.run(run_graph_async(state))

