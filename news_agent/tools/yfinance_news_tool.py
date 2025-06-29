# yfinance_news_tool.py
"""
A FunctionTool for fetching news headlines from Yahoo Finance using LangChain's YahooFinanceNewsTool.
"""
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from google.adk.tools.function_tool import FunctionTool

# Define the function to wrap the LangChain tool

def fetch_yahoo_finance_news(ticker: str, num_articles: int = 5):
    """
    Fetches recent news headlines for a given ticker using YahooFinanceNewsTool.
    Args:
        ticker (str): The ticker symbol (e.g., 'AAPL', 'GOOGL').
        num_articles (int): Number of news articles to fetch.
    Returns:
        list: List of news headlines and URLs.
    """
    tool = YahooFinanceNewsTool()
    return tool.run({"symbol": ticker, "num_articles": num_articles})

# Register as a FunctionTool for ADK

yahoo_finance_news_tool = FunctionTool(fetch_yahoo_finance_news)
