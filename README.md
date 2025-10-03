# Market_Research_GenAI
📊 Trending Product Insights with LangGraph + Streamlit

This project extracts trending product insights from the web using LangGraph, caches results for reproducibility, and provides an interactive Streamlit dashboard for analysis.

It is designed for retail & CPG use cases where business users need actionable insights about categories like Energy Drinks, Salty Snacks, Cigarettes, Beer, Wine, Carbonated Drinks, and Water.

## components
1. LangGraph Workflow Enabled with travily Search
2. 6 modular nodes (Query Generation, web search, Product extract, summarize, report, etc.)
3. Each node cached individually for reliability
4. Cache reuse when category + timeframe match
5. Hash-based keys (SHA256) for category + start/end date
6. Streamlit Dashboard(Tabs for Final Report and Product Insights)

# Testing
Unit tests for nodes and cache utilities
Integration tests for full workflow

# 📂 Project Structure

.
├── cache_utils.py  
├── config.py       
├── task_nodes.py        
├── workflow.py           
├── app.py            
├── tests/
│   ├── test_cache_utils.py
│   ├── test_nodes.py
│   └── test_integration.py
├── cache.json            # Cache storage (auto-generated)
└── README.md

⚙️ Installation
# Create virtual environment
python -m venv venv
source venv/bin/activate   # on Linux/Mac
venv\Scripts\activate      # on Windows

# Install dependencies
pip install -r requirements.txt

🏃 Usage
1. Run Streamlit Dashboard
streamlit run app.py

**Select Category from dropdown**

**Choose Start Date and End Date (month/year only, day defaults to 01)**
 **Results are cached automatically**
**If cache key matches, previous insights are returned instantly**

2. Run LangGraph Workflow Independently
python main.py (Make sure, Enter date correctly)

🧪 Testing

Run all tests:

pytest -v
Run async tests (requires pytest-asyncio):
pytest -v --asyncio-mode=auto

🔑 Cache System Details

Key format → SHA256(category + start_date + end_date)

Lookup → Retrieve original category + dates from hex key

🛠️ Requirements

Python 3.10+

Streamlit

LangChain / LangGraph

Add authentication to dashboard

Add support for multi-category workflows

Deploy Streamlit app to cloud (e.g., Streamlit Cloud, Azure, or GCP)

Would you like me to also include a Quick Start example with a sample workflow run and screenshot of
