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

"""Execution_analyst_agent for finding the ideal execution strategy"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from ..data_analyst.agent import data_analyst_agent
from ..news_analyst.agent import news_analyst_agent
from .prompt import TRADING_ANALYST_PROMPT

MODEL="gemini-1.5-flash"

# Trading analyst agent
trading_analyst_agent = LlmAgent(
    name="trading_analyst_agent",
    model=MODEL,
    description="Develops trading strategies based on market data and user preferences.",
    instruction=TRADING_ANALYST_PROMPT,
    tools=[
        AgentTool(agent=data_analyst_agent),
        AgentTool(agent=news_analyst_agent),
        # Add more tools as needed (e.g., FunctionTool for custom logic)
    ],
)
