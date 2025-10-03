import streamlit as st
from graph_state import AgentState
from workflow import build_workflow
import datetime,calendar
from workflow import run_graph
from cache_utils import *
import asyncio
import config
from utils import *
from datetime import date
import pandas as pd

CATGORIES = config.category_selection

#market insight
def market_insights_page(report_data,all_product_df):
    """get market insight and product summary"""
    st.header("🔍 Market Insights & Product Evidence")
    st.markdown(f"**{len(extract_market_insights(report_data))}** Key Insights. Click to view details.")
    insights_list = extract_market_insights(report_data)


    for i, insight_item in enumerate(insights_list):
        insight_text = insight_item.get('Insight')
        product_evidence = insight_item.get('Product_Evidence')
        if isinstance(product_evidence,dict):
            products_data = []
            for product in product_evidence:
                products_data.append({
                    'Product_Name': product.get('Product_Name'),
                    'Key_Feature': product.get('Key_Feature', 'N/A'),
                    'Trending_Driver': product.get('Trending_Driver')
                })
        
            products_df = pd.DataFrame(products_data)
            with st.expander(f"📌 **Insight {i+1}:** {insight_text}", expanded=False):
                products_df.rename(columns={
                    'Product_Name': 'Product/Flavor',
                    'Key_Feature': 'Key Feature/Note',
                    'Trending_Driver': 'Market Trend Driver'
                }, inplace=True)
                
                st.subheader(f"Product Evidence ({len(products_df)} Items)")
                st.dataframe(
                        products_df[['Product/Flavor', 'Key Feature/Note', 'Market Trend Driver']],
                        use_container_width=True,
                        hide_index=True
                    )
        elif isinstance(product_evidence,list):
             with st.expander(f"📌 **Insight {i+1}:** {insight_text}", expanded=False):
                 st.markdown(product_evidence)
        else:
            st.markdown("OOps, Error occured...")
                 

def actionable_strategy_page(report_data):
    """Show actionable strategy data"""
    st.header("💡 Actionable Strategies")
    tab1, tab2 = st.tabs(["Brand/Industry Perspective", "Store Owner Placement"])
     # A. Brand/Industry Perspective
    with tab1:
        st.subheader("Recommended Actions for Brands/Producers")
        try:
            brand_actions = (report_data['Actionable_Strategy']['Recommended_Actions']['Industry_Brand_Perspective']) or (report_data['Actionable_Strategy']['Recommended_Actions']['Industry_Strategy'])
        
            st.markdown(
            "\n".join([f"- **{action.split(':')[0]}**{': ' + ':'.join(action.split(':')[1:]) if len(action.split(':')) > 1 else ''}" for action in brand_actions]))
        except:
            st.error("OOps error Occured..")

    # B. Store Owner Placement Strategy
    with tab2:
        st.subheader("Placement Strategies for Store Owners")
        store_strategy = extract_store_strategy(report_data)
        
        for strategy in store_strategy:
            expanded_state = (strategy['Focus'] == 'Core Sales Volume')
            with st.expander(f"⭐ **Focus: {strategy['Focus']}**", expanded=expanded_state):
                st.markdown(f"**Action:** {strategy['Action']}")
                st.markdown(f"**Target Products:** {', '.join(strategy['Products'])}")

def product_summary_page(full_data):
    """Generates the Product Level Summary tab content clustered by semantic theme."""
    st.header("📦 Product Level Summary")
    df_base = extract_product_summaries(full_data)

    st.subheader("Product Details by Trend Cluster")
    df_base.rename(columns={
        'Product_Name': 'Product/Flavor',
        'Key_Feature': 'Key Feature/Note',
        'Trending_Driver': 'Raw Trend Driver'
    }, inplace=True)
    
    st.dataframe(
        # Only display relevant columns
        df_base[['Product/Flavor', 'Raw Trend Driver', 'Key Feature/Note']],
        use_container_width=True,
        hide_index=True
    )

def user_input_config():
    """set user input configuration and page heading"""
    #--- Streamlit app UI
    st.set_page_config(page_title="Market Insights Dashboard", layout="wide")
    st.title("📊 Market Insights Dashboard")
    st.markdown("---")

    categories = config.category_selection
    category = st.sidebar.selectbox("Select Category", categories)
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Month-Year", value=date.today().replace(day=1), key="start_date")
    with col2:
        end_date = st.date_input("End Month-Year", value=date.today().replace(day=1), key="end_date")

    # Clear cache button
    st.sidebar.markdown("---")
    if st.sidebar.button("⚠️ Clear Cache"):
        if st.sidebar.confirm("Are you sure? This will remove cached results for all categories and dates."):
            clear_cache()
            st.success("Cache cleared! Refreshing app...")
            st.experimental_rerun()

    #setting the date for result 
    key_start = start_date.strftime("%Y-%m-%d")
    key_end = end_date.strftime("%Y-%m-%d")
    config.set_date_range(key_start,key_end)
    
    st.write(f" Fetch Insights **{category}** from **{key_start}** to **{key_end}**")
    run_btn = st.button("🏃‍♂️Run")
    return category,run_btn

def get_data_output(category,run_btn):
    """
    return output either from cache or by running pipeline
    """
    state = {"category": category}
    # If final cached, present immediately
    final_cached = get_from_cache("create_final_summary", category, config.START_DATE, config.END_DATE)
    product_summary_cache = get_from_cache("clean_products",category,config.START_DATE,config.END_DATE)
    if final_cached:
        st.info("Final summary retrieved from cache (fast).")
        final_report = final_cached.get("final_report") if isinstance(final_cached, dict) else final_cached
        product_summaries = product_summary_cache.get("final_product_summaries") or final_cached.get("final_product_summaries")
    else:
        st.info("No Result Retrive from cache.. Please hit run button to get Insight")
        # If Run pressed, run pipeline
        if run_btn:
            with st.spinner("Running pipeline — this may take 20–60s ...Please wait 🫷🫷"):
                try:
                    result = run_graph(state)
                except Exception:
                    result = asyncio.run(run_graph(state))
                final_report = result.get("final_report") or result.get("final_report") or final_report["final_report"]
                product_summaries = result.get("final_product_summaries") or result.get("final_product_summaries") or result["final_product_summaries"]

    return final_report,product_summaries



def main():
    category,run_btn = user_input_config()
    final_report, product_summary = get_data_output(category=category,run_btn=run_btn)
    tab_insights, tab_strategy, tab_product_summary = st.tabs(
        ["Market Insights & Evidence", "Actionable Strategy", "Product Level Summary (Semantic)"])
    
    with tab_insights:
        if final_report is None or product_summary is None:
            st.container("🫙🫙🫙🫙 Data to show")
        else:
            market_insights_page(final_report, product_summary)

    with tab_strategy:
        actionable_strategy_page(final_report)
        
    with tab_product_summary:
        product_summary_page(product_summary)

if __name__ =="__main__":
    main()