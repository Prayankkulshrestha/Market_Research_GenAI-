from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import GoogleGenerativeAI
from langchain_tavily import TavilySearch
from typing import List, Dict, Any, Union
import asyncio
import logging
from dotenv import load_dotenv
import os

# Local Imports
from graph_state import AgentState
import config
from utils import *
from cache_utils import *

# --- Set up logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Getting Env variables ---
load_dotenv()
os.environ["TAVILY_API_KEY"] = os.getenv("TRAVILY_KEY")
os.environ["GOOGLE_API_KEY"]  = os.getenv("GOOGLE_API_KEY")

# --- Initialization ---
Prompts_list = load_prompts(config.prompt_file_name)
llm = GoogleGenerativeAI(model=config.llm_model_name_lite)
search_tool = TavilySearch(**config.search_tool_params)


def node_cache(node_name:str):
    """
    Decorator that provides
        - Node level caching
        - on-execption : return last cache value merged with error message
    Work with for both sync and async node functions

    """

    def decorator(func):
        if is_async(func=func):
            async def wrapper(state:dict,*args, **kwargs):
                category,start_date,end_date = get_cat_and_date_from_states(state)
                cache = get_from_cache(node=node_name,category=category,start_date=start_date,
                                       end_date=end_date)
                if cache is not None:
                    logger.info(f"[CACHE HIT] {node_name} for {category} | {start_date} - {end_date}")
                    return cache
                
                logger.info(f"[CACHE MISS] {node_name} for {category} | {start_date} - {end_date}") 
                try:
                    res = await func(state, *args, **kwargs)
                    set_to_cache(node_name,category,start_date,end_date,res)
                    logger.info(f"[CACHE SAVE] {node_name} for {category} | {start_date} - {end_date}")
                    return res
                except Exception as e:
                    logger.exception(f"Node {node_name} failed:{e}")
                    if cache is not None:
                    #return cache data with error field
                        out = dict(cache) if isinstance(cache,dict) else {"value":cache}
                        out["_node_error"] = str(e)
                        logger.warning(f"{node_name} failed,returning previous output")
                        return out
                raise
            return wrapper
        else:
            def wrapper(state, *args, **kwargs):
                category,start_date,end_date = get_cat_and_date_from_states(state)
                cache = get_from_cache(node=node_name,category=category,start_date=start_date,
                                       end_date=end_date)
                if cache is not None:
                    logger.info(f"[CACHE HIT] {node_name} for {category} | {start_date} - {end_date}")
                    return cache
                
                logger.info(f"[CACHE MISS] {node_name} for {category} | {start_date} - {end_date}") 
                try:
                 res =  func(state, *args, **kwargs)
                 set_to_cache(node_name,category,start_date,end_date,res)
                 logger.info(f"[CACHE SAVE] {node_name} for {category} | {start_date} - {end_date}")
                 return res
                except Exception as e:
                    logger.exception(f"Node {node_name} failed:{e}")
                    if cache is not None:
                        out = dict(cache) if isinstance(cache,dict) else {"value":cache}
                        out["_node_error"] = str(e)
                        logger.warning(f"{node_name} failed,returning previous output")
                        return out
                raise
            return wrapper
    return decorator

# --- Node 1 : Search Query Generation ---
@node_cache("generate_search_query")
def generate_search_query(state: Any) -> Dict[str, Union[str, List[str]]]:
    """Uses llm to generate a search query."""
    query_template = Prompts_list['chat_templates']['search_query_prompts']
    query_prompt = ChatPromptTemplate.from_messages(query_template)
    query_chain = query_prompt | llm
    
    category = state.category if hasattr(state, "category") else state["category"]
    out = query_chain.invoke({"category":category})
    final_query = safe_content(out)
    logger.info(f"Generated Search Query: {final_query}")
    return {"query": final_query, "messages": [f"Query Generated: {final_query}"]}

# --- Node 2 : Web Search ----
@node_cache("perfrom_web_search")
def perfrom_web_search(state: Any) -> Dict[str, List[Dict[str, Any]]]:
    """Performs Tavily Search for the generated Query."""
    query = getattr(state, "query", None) or (state["query"] if isinstance(state, dict) else None)
    if not query:
        raise ValueError("No search query available in cache or state")
        
    # Tavily's invoke for web search
    raw_search_results = search_tool.invoke({"query": query})
    clean_results = get_structure_search_results(raw_search_results)
    logger.info(f"Web search return {len(clean_results)} items.")
    return {"search_result": clean_results}

# Node 3 : Product Extraction
async def _extract_products_name_async(state: Any) -> Dict[str,Any]:
    """
    Extract product names from search results using LLM
    """
    extract_template = Prompts_list["chat_templates"]["identify_products"]
    extraction_prompt = ChatPromptTemplate.from_messages(extract_template)
    extraction_chain = extraction_prompt | llm
    raw_search_result = getattr(state, "search_result", None) or (state["search_result"] if isinstance(state, dict) else None)
    category = state.category if hasattr(state, "category") else state["category"]

    logging.info(f"[Retrieve] Search results for {category} === total Items {len(raw_search_result)}")
    
    if not raw_search_result:
        raise ValueError("Please do web search first before extracting products.")
    if not category:
        raise ValueError("Please provide category to Extract the product names")
    
    #product_list: List[Dict[int,Union[str,None]]] = []
    sem = asyncio.Semaphore(3)

    async def process_page(page):
        async with sem:
            try:
                web_text = get_web_content(page=page)
                out = await extraction_chain.ainvoke({
                    "text": web_text,
                    "category": category
                })
                content = safe_content(out)
                return content
            except Exception as e:
                print("Extraction error page: %s", e)
                # produce None so we preserve page index
                return None

            except Exception as e:
                logger.exception("Error in extracting for page: %s",e)
    
    tasks = [process_page(p) for p in raw_search_result]
    page_results = await asyncio.gather(*tasks, return_exceptions=False)
    mapped = {i: page_results[i] for i in range(len(page_results))}
    print("Extracted products for %d pages", len(page_results))
    return {"products": mapped}

@node_cache("extract_products_name")
def extract_products_name(state: Any) -> Dict[str, Any]:
    """Sync wrapper around async function."""
    return asyncio.run(_extract_products_name_async(state))

# --- Node 4 : Summarize each product -----
async def _product_summary_async(state: Any) -> Dict[str,Any]:
    """
    Summarize trending products using search results and product names
    """
    summary_template = Prompts_list["chat_templates"]["summarize_product"]
    summary_prompt = ChatPromptTemplate.from_messages(summary_template)
    summary_chain = summary_prompt | llm

    products_map = getattr(state, "products", None) or (state["products"] if isinstance(state, dict) else None)
    raw_search_result = getattr(state, "search_result", None) or (state["search_result"] if isinstance(state, dict) else None)
    category = state.category if hasattr(state, "category") else state["category"]
    logging.info(f"[Summary] Recevied Product map and web results for {category} ==== items {len(products_map)} ")

    #raise exception for missing input
    if not products_map:
        logging.exception("[NOT FOUND] No products in state to summarize.")
    if not raw_search_result:
        logging.exception("[NOT FOUND] No web search found")
    if not category:
        logging.exception("[NOT FOUND] Please provide category to provide summary")
    
    summaries = []
    #set number of thread async process
    sem = asyncio.Semaphore(config.NO_OF_THREADS)

    async def summarize_one(prod_name: str,page: str):
        async with sem:
            try:
                out = await summary_chain.ainvoke({
                    "data": page,
                    "product": prod_name,
                    "category": category
                })
                content = safe_content(out)
                parsed = parse_llm_json_output(content)

                # try to extract Product_Analysis if present
                analysis = parsed["Product_Analysis"] if isinstance(parsed, dict) and "Product_Analysis" in parsed else parsed
                return {"analysis": analysis}
            except Exception as e:
                print("Summary error for product=%s: %s", prod_name, e)
                return {"analysis": None, "_error": str(e)}
    
    pages = [get_web_content(p) for p in raw_search_result]
    product_items = [products_map[k] for k,v in products_map.items()]

    tasks = [summarize_one(prod,page) 
                    for prod,page in zip(product_items,pages)]
    
    results = await asyncio.gather(*tasks, return_exceptions=False)
    summaries.extend(results)
    logging.info("Generated %d product summaries", len(summaries))
    return {"product_summaries": summaries}

@node_cache("product_summary")
def product_summary(state: Any) -> Dict[str, Any]:
    """Sync wrapper around async function."""
    return asyncio.run(_product_summary_async(state))

### Node 5 ==== Clean the product names 
@node_cache("clean_products")
def clean_products(state:Any):
    """
    clean the product input product list
    """
    summaries = getattr(state, "product_summaries", None) or (state["product_summaries"] if isinstance(state, dict) else None)
    category = state.category if hasattr(state, "category") else state["category"]

    #Raise exception
    if not summaries:
        logging.exception("No product_summaries present to clean.")
    if not category:
        logging.exception("Please provide cateogry to perform cleaning of products")
    
     # Extract analysis part if present, else stringify
    names = []
    for item in summaries:
        if isinstance(item, dict) and item["analysis"]:
            names.append(item["analysis"])
        else:
            names.append(item)
    
    logger.info(f"[Product Clean] removing duplicate items name ==== total item {len(names)}")

    duplicate_removal_prompt = Prompts_list["chat_templates"]["duplicate_removal"]
    dup_clean_template = ChatPromptTemplate.from_messages(duplicate_removal_prompt)
    dup_clean_chain = dup_clean_template | llm

    final_product_list = dup_clean_chain.invoke({"category": category,"product":names})
    # get the final Product list
    try:
        clean_products = parse_llm_json_output(safe_content(final_product_list))
    except Exception as e:
        logger.exception(f"[clean Product] Error in Parsing output=={e}")
        clean_products = final_product_list
    return {"final_product_summaries":clean_products}

### Node 6 ====== Clean and Final Summary
@node_cache("create_final_summary")
def create_final_summary(state:Any):
    """Get the final summary of products"""
    
    final_products = getattr(state, "final_product_summaries", None) or (state["final_product_summaries"] if isinstance(state, dict) else None)
    category = state.category if hasattr(state, "category") else state["category"]

    if not final_products:
        logger.exception("No final_product_summaries to create final summary.")
    if not category:
        logger.exception("please provide category for final summary")
 
    final_summary_prompt = Prompts_list["chat_templates"]["final_summary"]
    summary_template = ChatPromptTemplate.from_messages(final_summary_prompt)
    summary_chain = summary_template | llm 
    out = summary_chain.invoke({"category": category, "data": final_products})
    try:
        final_report = parse_llm_json_output(safe_content(out))
    except Exception as e:
        logger.exception("[final Summary] Error in parsing {e}")
        final_report = out

    print("Final summary created.")
    return {"final_report": final_report}

