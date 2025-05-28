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
from .prompt import EXECUTION_ANALYST_PROMPT

execution_analyst_agent = LlmAgent(
    name="execution_analyst_agent",
    model="gemini-1.5-flash",
    description="Develops and evaluates execution plans for trading strategies.",
    instruction=EXECUTION_ANALYST_PROMPT,
    tools=[],
)
