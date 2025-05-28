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

"""data_analyst_agent for finding information using google search"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import ToolContext, FunctionTool

from .prompt import DATA_ANALYST_PROMPT
from .data_processing_pipeline.agent import data_processing_pipeline_agent
from .yfinance_fetcher.agent import yfinance_fetcher_agent

# Quant agent for trading strategy suggestions
QUANT_PROMPT = """
You are a quant analyst. Based on the provided data and prompt, suggest optimized trading strategies using quantitative methods.
"""

quant_agent = LlmAgent(
    name="quant_agent",
    model="gemini-1.5-flash",
    description="Suggests trading strategies using quantitative analysis.",
    instruction=QUANT_PROMPT,
    tools=[],
)

# Example: Only allow free-tier tickers (guardrail)
FREE_TIER_TICKERS = {"AAPL", "MSFT", "0700.HK", "BABA", "TSLA", "GOOG", "META"}

def before_tool_callback(tool_context: ToolContext):
    # Log every tool call
    print(f"[Callback] About to call tool: {tool_context.tool_name} with args: {tool_context.args}")
    # Guardrail: Only allow certain tickers for yfinance
    if tool_context.tool_name == "yfinance_fetcher_agent":
        ticker = tool_context.args.get("ticker", "")
        if ticker and ticker.upper() not in FREE_TIER_TICKERS:
            print(f"[Callback] Blocked ticker: {ticker}")
            return {"status": "error", "error_message": f"Ticker '{ticker}' is not allowed on free tier."}
    return None

def after_tool_callback(tool_context: ToolContext, result):
    # Log tool result
    print(f"[Callback] Tool {tool_context.tool_name} returned: {result}")
    return None

class DataAnalystOrchestrator(LlmAgent):
    def __init__(self):
        super().__init__(
            name="data_analyst_agent",
            model="gemini-1.5-flash",
            description="Performs data analysis on financial datasets and coordinates with quant, yfinance, and data pipeline agents.",
            instruction=DATA_ANALYST_PROMPT,
            sub_agents=[
                quant_agent,
                yfinance_fetcher_agent,
                data_processing_pipeline_agent,
            ],
            tools=[
                AgentTool(agent=yfinance_fetcher_agent),
                AgentTool(agent=data_processing_pipeline_agent),
                FunctionTool(func=self.greet_user),
            ],
            before_tool_callback=before_tool_callback,
            after_tool_callback=after_tool_callback,
        )

    def fetch_market_data(self, ticker: str, period: str = "1mo", interval: str = "1d"):
        yfin_result = yfinance_fetcher_agent.execute(ticker, period=period, interval=interval)
        if isinstance(yfin_result, dict) and "error" in yfin_result:
            return {"error": f"yfinance failed: {yfin_result['error']}"}
        return {"source": "yfinance", "data": yfin_result}

    def greet_user(self, name: str) -> dict:
        """Greets the user by name."""
        return {"status": "success", "greeting": f"Hello, {name}!"}

data_analyst_agent = DataAnalystOrchestrator()
