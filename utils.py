import yaml
import json
from typing import Any
import config
import asyncio
import datetime 
import pandas as pd

def load_prompts(file_path):
    """Loads and return prompts from Yaml file"""
    try:
        with open(file_path,"r",encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error ! file {file_path} not found")
        return None
    except yaml.YAMLError as e:
        print(f"Error in parsing yaml file: {e}")
        return None

def get_structure_search_results(results):
    """saving results in pandas dataframe"""
    try:
        if isinstance(results,dict) and "results" in results.keys():
            return results["results"]     
    except ValueError as Ve:
        print(f"error in parsing results :{Ve}")
        return results
    
def get_web_content(page):
    """
    get final content for summary and extraction
    """
    try:

        content = page["content"]
        raw_content = page["raw_content"]
        #checking conditions
        if isinstance(raw_content,str) and not isinstance(content,str):
            web_text = content
        elif not isinstance(raw_content,str) and isinstance(content,str):
            web_text = raw_content
        elif isinstance(raw_content,str) and isinstance(content,str):
            web_text = content +" "+ raw_content
        else:
            web_text = None
        return web_text
    except ValueError as ve:
        print("invalid format of page",ve)
        return None

def parse_llm_json_output(llm_string):
    """
    Cleans an LLM output string containing a JSON code block and parses it into a Python dictionary.
    """
    try:
        # 1. Strip the starting delimiter (```json\n)
        cleaned_string = llm_string.strip()
        if cleaned_string.startswith("```json") or cleaned_string.startswith("```") :
            cleaned_string = cleaned_string[len("```json"):].strip()
        
        # 2. Strip the ending delimiter (\n```)
        if cleaned_string.endswith("```"):
            cleaned_string = cleaned_string[:-len("```")].strip()
        
        # 3. Use the json library to load the string into a Python dictionary
        data = json.loads(cleaned_string)
        return data
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Problematic string (first 500 chars):\n{cleaned_string[:500]}")
        return None

def safe_content(llm_out: Any) ->Any:
    if hasattr(llm_out,"content"):
        return llm_out.content
    return llm_out

def get_cat_and_date_from_states(state:Any):
    if hasattr(state,"category"):
        category = state.category
    elif isinstance(state,dict):
        category = state.get("category")
    else:
        category = None
    
    start_date = config.START_DATE
    end_date = config.END_DATE

    if not(category and start_date and end_date):
        missing = [k for k,v in (("category", category), ("start_date", start_date), ("end_date", end_date)) if not v]
        raise ValueError(f"missing require value for caching: {missing}")
    return category,start_date,end_date

def is_async(func):
    return asyncio.iscoroutinefunction(func=func)


def month_year_to_dates(m_name: str, y: int,months):
    m = months.index(m_name) + 1
    start = datetime.date(y, m, 1)
    end = datetime.date(y, m, 1)
    return start, end

def extract_market_insights(report_data):
    """Returns the raw list of key insights."""
    return report_data.get('Market_Summary', {}).get('Key_Insights', [])

def extract_store_strategy(report_data):
    """Extracts the store owner placement strategy into a list of dictionaries."""
    return report_data.get('Actionable_Strategy', {}).get('Store_Owner_Placement_Strategy', [])

def extract_product_summaries(full_data):
    """Extracts the final product summaries into a DataFrame."""
    df = pd.DataFrame(full_data.get('final_product_summaries', []))
    return df
    
