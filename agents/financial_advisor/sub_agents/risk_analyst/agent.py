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

"""Risk Analysis Agent for providing the final risk evaluation"""

from google.adk import Agent
from google.adk.agents import LlmAgent
from .prompt import RISK_ANALYST_PROMPT

risk_analyst_agent = LlmAgent(
    name="risk_analyst_agent",
    model="gemini-1.5-flash",
    description="Assesses risk of trading strategies and provides mitigation recommendations.",
    instruction=RISK_ANALYST_PROMPT,
    tools=[
        # Add any custom tool classes/functions here if needed
    ],
)
