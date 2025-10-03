from typing import Optional,Any,Dict
from pydantic import BaseModel


class AgentState(BaseModel):
    """
    Represent the state of agent workflow

    Attributes
        meta : A list of messages that reprsenent conversation history and tool output
        query : initial query from user
        search_results : the raw results from the web search
        products: A list of identified trending products
        product_summaries : A dict mapping product name and summary
        final_product_summaries : final dict mapping to product name and summary
        final_report: Final Report generation and based on extract product and summary
    """

    category: str
    query : Optional[str] = None
    search_result : Optional[Any] = None
    products : Optional[Any] = None
    product_summaries: Optional[Any] = None
    final_product_summaries: Optional[Any] = None
    final_report: Optional[Any] = None

    #addition free form of data
    meta : Dict[str,Any] = {}



