
# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""market_data_agent: ADK-compliant agent for market data lookup and analysis"""


from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools import FunctionTool
from logs.logger import setup_logger, log_agent_event
import MODELS
from tools.yfinance_tool import query_yfinance

AGENT_NAME = "market_data_agent"
logger = setup_logger(AGENT_NAME)

# Register yfinance as a tool
yfinance_tool = FunctionTool(
    name="yfinance_query",
    description="Query real-time market data from Yahoo Finance for any ticker (e.g. AAPL, CL=F, BTC-USD)",
    func=query_yfinance,
    input_schema={
        "ticker_or_term": "The asset symbol or keyword (e.g. 'CL=F' for oil futures, 'AAPL' for Apple)",
        "period": "(Optional) Period of historical data to fetch (e.g., '7d', '1mo')",
        "interval": "(Optional) Interval between data points (e.g., '1d', '1h')"
    },
)

# The market_data_agent can use both yfinance and google_search as tools
MARKET_AGENT_PROMPT = """
You are a financial data analysis agent.

You are given a financial topic (e.g., 'OIL', 'APPLE', 'BITCOIN') and your task is to:
1. Identify the correct Yahoo Finance ticker (e.g. CL=F for oil futures, AAPL for Apple)
2. Use the `yfinance_query` tool to pull:
    - Current price and volume
    - Last 5 days of historical data
    - Most recent news headlines and links
    - Sentiment score (positive/neutral/negative) for each headline
3. Use the `google_search` tool to supplement with recent news and market commentary if needed.
4. Interpret the combined output:
    - What does the price and volume trend suggest?
    - What is the market sentiment based on the news?
    - Are there actionable insights or risks?

Structure your output with:
- 📈 Market Summary
- 📊 Historical Trend
- 📰 News Highlights
- 😐 Sentiment Overview
- 🔍 Agent Insight
"""

market_data_agent = LlmAgent(
    name=AGENT_NAME,
    model=MODELS.REASONING_MODEL if hasattr(MODELS, "REASONING_MODEL") else "gpt-4",
    description="A financial data lookup agent using yfinance and google_search to pull live price, volume, and news data.",
    instruction=MARKET_AGENT_PROMPT,
    output_key="market_data_output",
    tools=[yfinance_tool, google_search],
)

# Expose root_agent for ADK compatibility
root_agent = market_data_agent
