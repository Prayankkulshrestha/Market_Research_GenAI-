import os

llm_model_name = "gemini-2.5-flash"
llm_model_name_lite = "gemini-2.5-flash-lite"

START_DATE = None
END_DATE = None
def set_date_range(start_date:str,end_date:str):
    global START_DATE,END_DATE
    START_DATE = start_date
    END_DATE = end_date

# thread no 
NO_OF_THREADS = 2

#Search configurations
search_tool_params = {
    "include_answer": "advanced",
    "search_depth":"advanced",
    "max_results": 10, # Maximum 20 
    "time_range": "year",
    "start_date": START_DATE,
    "end_date": END_DATE,
    "include_raw_content": "text",
    "chunks_per_source": 5,
    "country": "united states"
}

prompt_file_name = os.path.join(os.getcwd(),"prompt_manager.yml")

CACHE_FILE = "cache.json"

category_selection = [
    "Energy Drinks",
    "Salty Snacks",
    "Cigarettes",
    "Beer",
    "Wine",
    "Flavour and sparking water",
    "Carbonated Drinks"
]

