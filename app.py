import streamlit as st
import pandas as pd
import asyncio
from datetime import date

# Assuming these are your custom modules
import config
from graph_state import AgentState
from workflow import build_workflow, run_graph
from cache_utils import *
from utils import *


# --- Page Rendering Functions ---

def market_insights_page(report_data):
    """Render the Market Insights and Product Evidence section."""
    st.header("🔍 Market Insights & Product Evidence")

    try:
        insights_list = extract_market_insights(report_data)
        st.markdown(f"**{len(insights_list)}** Key Insights. Click to view details.")

        for i, insight_item in enumerate(insights_list):
            insight_text = insight_item.get('Insight', 'No insight text available.')
            product_evidence = insight_item.get('Product_Evidence')

            with st.expander(f"📌 **Insight {i+1}:** {insight_text}", expanded=False):
                # CORRECTED: Check if product_evidence is a list of dictionaries
                if product_evidence and isinstance(product_evidence, list) and isinstance(product_evidence[0], dict):
                    products_df = pd.DataFrame(product_evidence)
                    products_df.rename(columns={
                        'Product_Name': 'Product/Flavor',
                        'Key_Feature': 'Key Feature/Note',
                        'Trending_Driver': 'Market Trend Driver'
                    }, inplace=True)
                    
                    st.subheader(f"Product Evidence ({len(products_df)} Items)")
                    st.dataframe(
                        products_df,
                        use_container_width=True,
                        hide_index=True
                    )
                # CORRECTED: Handles the case where product_evidence is a simple list of strings
                elif isinstance(product_evidence, list):
                    st.markdown("- " + "\n- ".join(product_evidence))
                else:
                    st.warning("Product evidence data is not in a recognized format.")

    except (TypeError, KeyError, IndexError) as e:
        st.error(f"An error occurred while displaying market insights. Please check the data format. Error: {e}")


def actionable_strategy_page(report_data):
    """Show actionable strategy data."""
    st.header("💡 Actionable Strategies")
    tab1, tab2 = st.tabs(["Brand/Industry Perspective", "Store Owner Placement"])
    
    with tab1:
        st.subheader("Recommended Actions for Brands/Producers")
        try:
            actions = report_data.get('Actionable_Strategy', {}).get('Recommended_Actions', {})
            if isinstance(actions,dict) and (len(actions)>=0):
                brand_actions = (report_data.get('Actionable_Strategy', {}).get('Recommended_Actions', {}).get('Industry_Brand_Perspective') or
                             report_data.get('Actionable_Strategy', {}).get('Recommended_Actions', {}).get('Industry_Strategy'))
            else:
                brand_actions = actions


        
            
            if brand_actions:
                 st.markdown(
                    "\n".join([f"- {action}" for action in brand_actions])
                )
            else:
                st.info("No brand/industry perspective actions found.")
        except Exception as e:
            st.error(f"Oops, an error occurred while loading brand strategies: {e}")

    with tab2:
        st.subheader("Placement Strategies for Store Owners")
        try:
            store_strategy = extract_store_strategy(report_data)
            if store_strategy:
                for strategy in store_strategy:
                    expanded_state = (strategy.get('Focus') == 'Core Sales Volume')
                    with st.expander(f"⭐ **Focus: {strategy.get('Focus', 'N/A')}**", expanded=expanded_state):
                        st.markdown(f"**Action:** {strategy.get('Action', 'N/A')}")
                        products = strategy.get('Products', [])
                        if products:
                            st.markdown(f"**Target Products:** {', '.join(products)}")
            else:
                st.info("No store owner placement strategies found.")
        except Exception as e:
            st.error(f"Oops, an error occurred while loading store strategies: {e}")


def product_summary_page(full_data):
    """
    Generates the Product Level Summary tab, intelligently handling
    different possible data structures from the cache.
    """
    st.header("📦 Product Level Summary")
    st.subheader("Product Details by Trend Cluster")
    
    if not full_data or not isinstance(full_data, list):
        st.warning("Product summary data is unavailable or in an incorrect format.")
        return

    flat_product_list = []
    # Check for the nested structure: [{"analysis": [{"Product_Name": ...}]}]
    if isinstance(full_data[0], dict) and "analysis" in full_data[0]:
        for item in full_data:
            if "analysis" in item and isinstance(item["analysis"], list):
                flat_product_list.extend(item["analysis"])
    # Assume the flat structure: [{"Product_Name": ...}]
    else:
        flat_product_list = full_data

    if not flat_product_list:
        st.info("No product details to display.")
        return

    try:
        df_base = pd.DataFrame(flat_product_list)
        df_base.rename(columns={
            'Product_Name': 'Product/Flavor',
            'Key_Feature': 'Key Feature/Note',
            'Trending_Driver': 'Raw Trend Driver'
        }, inplace=True)
        
        # Ensure essential columns exist to prevent KeyErrors
        display_cols = ['Product/Flavor', 'Raw Trend Driver', 'Key Feature/Note']
        for col in display_cols:
            if col not in df_base.columns:
                df_base[col] = "N/A"

        st.dataframe(
            df_base[display_cols],
            use_container_width=True,
            hide_index=True
        )
    except Exception as e:
        st.error(f"Could not generate product summary table. An error occurred: {e}")


# --- UI and Data Loading ---

def user_input_config():
    """Set user input configuration and page heading."""
    st.set_page_config(page_title="Market Insights Dashboard", layout="wide")
    st.title("📊 Market Insights Dashboard")
    st.markdown("---")

    category = st.sidebar.selectbox("Select Category", config.category_selection)
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Month-Year", value=date.today().replace(day=1), key="start_date")
    with col2:
        end_date = st.date_input("End Month-Year", value=date.today().replace(day=1), key="end_date")

    st.sidebar.markdown("---")
    if st.sidebar.button("⚠️ Clear Cache"):
        if st.sidebar.confirm("Are you sure? This will remove all cached results."):
            clear_cache()
            st.success("Cache cleared! Refreshing app...")
            st.rerun()

    key_start = start_date.strftime("%Y-%m-%d")
    key_end = end_date.strftime("%Y-%m-%d")
    config.set_date_range(key_start, key_end)
    
    st.write(f"Displaying insights for **{category}** from **{key_start}** to **{key_end}**.")
    run_btn = st.button("🏃‍♂️ Run Analysis")
    return category, run_btn


def get_data_output(category, run_btn):
    """Return output either from cache or by running the pipeline."""
    final_report, product_summaries = None, None
    state = {"category": category}

    final_cached = get_from_cache("create_final_summary", category, config.START_DATE, config.END_DATE)
    product_summary_cache = get_from_cache("clean_products", category, config.START_DATE, config.END_DATE)

    if final_cached:
        st.info("Final summary retrieved from cache.")
        final_report = final_cached.get("final_report")
        # Product summaries can be in two different structures across two cache entries
        if product_summary_cache:
            # Handle both possible keys for product summaries
            product_summaries = product_summary_cache.get("final_product_summaries") or product_summary_cache.get("product_summaries")
        if not product_summaries:
            product_summaries = final_cached.get("final_product_summaries") or final_cached.get("product_summaries")

    elif run_btn:
        with st.spinner("Running pipeline — this may take 20–60s... Please wait 🙏"):
            try:
                result = run_graph(state)
                if result:
                    final_report = result.get("final_report")
                    product_summaries = result.get("final_product_summaries") or result.get("product_summaries")
                else:
                    st.error("Pipeline did not return any results.")
            except Exception as e:
                st.error(f"An error occurred during the pipeline execution: {e}")
    
    else:
        st.info("No cached result found. Click the 'Run Analysis' button to generate insights.")

    return final_report, product_summaries


def main():
    """Main function to run the Streamlit app."""
    category, run_btn = user_input_config()
    final_report, product_summary = get_data_output(category=category, run_btn=run_btn)

    if final_report and product_summary:
        tab_insights, tab_strategy, tab_product_summary = st.tabs(
            ["Market Insights & Evidence", "Actionable Strategy", "Product Level Summary"])
        
        with tab_insights:
            market_insights_page(final_report)

        with tab_strategy:
            actionable_strategy_page(final_report)
            
        with tab_product_summary:
            product_summary_page(product_summary)
    else:
        st.markdown("---")
        if not run_btn:
            st.warning("Click the 'Run Analysis' button to begin.")

if __name__ == "__main__":
    main()