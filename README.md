# Market_Research_GenAI-
📊 Trending Product Insights with LangGraph + Streamlit

This project extracts trending product insights from the web using LangGraph, caches results for reproducibility, and provides an interactive Streamlit dashboard for analysis.

It is designed for retail & CPG use cases where business users need actionable insights about categories like Energy Drinks, Salty Snacks, Cigarettes, Beer, Wine, Carbonated Drinks, and Water.

🚀 ### Features

LangGraph Agent Workflow

6 modular nodes (search, extract, summarize, report, etc.)

Each node cached individually for reliability

Cache reuse when category + timeframe match

Caching

JSON-based cache with atomic writes

Hash-based keys (SHA256) for category + start/end date

Lookup API to fetch previous results

Streamlit Dashboard

Tabs for Final Report and Product Insights

Interactive cards, charts, and filters

Option to clear cache and regenerate results

#Testing

Unit tests for nodes and cache utilities

Integration tests for full workflow

📂 Project Structure
.
├── cache_utils.py        # Cache save/load/lookup helpers
├── config.py             # Config & prompts
├── task_nodes.py         # LangGraph node implementations
├── workflow.py           # LangGraph workflow orchestration
├── app.py                # Streamlit dashboard
├── tests/
│   ├── test_cache_utils.py
│   ├── test_nodes.py
│   └── test_integration.py
├── cache.json            # Cache storage (auto-generated)
└── README.md

⚙️ Installation
# Clone repository
git clone https://github.com/your-username/trending-product-insights.git
cd trending-product-insights

# Create virtual environment
python -m venv venv
source venv/bin/activate   # on Linux/Mac
venv\Scripts\activate      # on Windows

# Install dependencies
pip install -r requirements.txt

🏃 Usage
1. Run Streamlit Dashboard
streamlit run app.py


Select Category from dropdown

Choose Start Date and End Date (month/year only, day defaults to 01)

Results are cached automatically

If cache key matches, previous insights are returned instantly

2. Run LangGraph Workflow Independently
python workflow.py

🧪 Testing

Run all tests:

pytest -v


Run async tests (requires pytest-asyncio):

pytest -v --asyncio-mode=auto

🔑 Cache System Details

Key format → SHA256(category + start_date + end_date)

Lookup → Retrieve original category + dates from hex key

Storage → cache.json with atomic write/rename

🛠️ Requirements

Python 3.10+

Streamlit

LangChain / LangGraph

Prometheus client

Pytest (for testing)

📌 Next Steps

Add authentication to dashboard

Add support for multi-category workflows

Deploy Streamlit app to cloud (e.g., Streamlit Cloud, Azure, or GCP)

Would you like me to also include a Quick Start example with a sample workflow run and screenshot of
