# Market Research GenAI 📊

**Trending Product Insights with LangGraph + Streamlit**

This project provides actionable market research insights by analyzing web data for trending products. It uses a robust **LangGraph** workflow to search, extract, and summarize information, presenting the final report in an interactive **Streamlit** dashboard.

It is designed for business users in the **Retail & CPG** industries who need timely intelligence on categories like Energy Drinks, Salty Snacks, Beer, Wine, and more.



---

## Features

* **Automated LangGraph Workflow**: A modular, 6-node graph that handles query generation, web searching (using Tavily), product extraction, summarization, and final report generation.
* **Interactive Dashboard**: A user-friendly Streamlit interface with separate tabs for the final summary report and detailed product insights.
* **Intelligent Caching**: Each node's output is individually cached. The system automatically reuses cached results when the product category and timeframe match, ensuring fast and reproducible insights.
* **Reliable Cache Keys**: Cache keys are generated using SHA256 hashes of the category and date range, preventing data collisions.
* **Comprehensive Testing**: Includes unit tests for individual nodes and cache utilities, plus integration tests for the end-to-end workflow.

---

## Project Structure

```
.
├── app.py              # Main Streamlit dashboard application
├── workflow.py         # Defines the LangGraph workflow
├── task_nodes.py       # Contains the logic for each node in the graph
├── config.py           # Configuration settings (API keys, etc.)
├── cache_utils.py      # Utility functions for the caching system
├── cache.json          # The cache file (can be .gitignore'd)
├── requirements.txt    # Project dependencies
├── tests/
│   ├── test_nodes.py
│   ├── test_cache_utils.py
│   └── test_integration.py
└── README.md
```

---

## Installation

1.  **Clone the repository:**

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on macOS/Linux
    source venv/bin/activate

    # Activate on Windows
    venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

##  Usage

### 1. Run the Streamlit Dashboard

This is the primary way to use the application.

1.  **Launch the app:**
    ```bash
    streamlit run app.py
    ```
2.  **Select a product category** from the dropdown menu.
3.  **Choose a start and end date** for the analysis.
4.  The results will be generated and displayed. If a previous analysis exists for the same criteria, the cached results will be returned instantly.

### 2. Run the LangGraph Workflow Independently

You can also run the data processing workflow directly from the command line.

```bash
python main.py --category "Energy Drinks" --start_date "2025-01-01" --end_date "2025-03-31"
```

---

## Testing

This project uses `pytest`. To run the test suite:

```bash
# Run all tests in verbose mode
pytest -v

# If you have async tests, run with the asyncio plugin
pytest -v --asyncio-mode=auto
```

---

## Future Work

* **User Authentication**: Add a login system to the Streamlit dashboard.
* **Multi-Category Analysis**: Add support for comparing multiple product categories in a single workflow run.
* **Cloud Deployment**: Deploy the Streamlit application to a cloud service like Streamlit Cloud, Azure, or GCP.
