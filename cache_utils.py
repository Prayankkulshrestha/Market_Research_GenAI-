"""
Cache_utils.py
Objective : Implementation of CURD operations for Cache files
Remember : Cache should be store in Reddis or some other DB, for example we store in JSON object
"""


import json
import os
from typing import Any,Dict,Optional
import config
import hashlib
from atomicwrites import atomic_write

CACHE_FILE = config.CACHE_FILE

if not os.path.exists(CACHE_FILE):
    with open(CACHE_FILE,"w",encoding="utf-8") as f:
        json.dump({},f)

def _make_key(node:str, category: str, start_date: str, end_date: str) ->str:
    """
    return cache keys based on category and time
    """
    raw_key = f"{node}:{category}:{start_date}:{end_date}"
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

def _load_all() -> Dict[str,Any]:
    """
    load the cache file if file exist for query
    this reduce no LLM API calls, Hence the save cost
    """
    try:
        with open(CACHE_FILE,"r",encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_all(cache: Dict[str,Any]) -> None:
    """
    saving file with atomic write, Do as follow
    1. Create temp JSON file and write 
    2. Replace main JSON file with temp JSON File
    """
    with atomic_write(CACHE_FILE, overwrite=True, encoding="utf-8") as f:
        json.dump(cache, f, indent=2)


def get_from_cache(node:str, category:str, start_date: str, end_date: str) -> Optional[Any]:
    """
    Get the data from cache if we have same query
    """
    cache = _load_all()
    key = _make_key(node,category,start_date,end_date)
    print(key)
    return cache.get(key)

def set_to_cache(node: str, category: str, start_date: str, end_date: str, value:Any) -> None:
    """
    setting value of cache for node
    """
    cache = _load_all()
    key = _make_key(node, category,start_date,end_date)
    cache[key] = value
    _save_all(cache)

def clear_cache() -> None:
    "remove cache file from local dir"
    if os.path.exists(config.CACHE_FILE):
        os.remove(config.CACHE_FILE)






    
