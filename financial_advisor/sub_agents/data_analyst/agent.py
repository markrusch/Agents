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

from google.adk import Agent
from google.adk.tools import google_search
import MODELS

from . import prompt
from .. import log_agent_call_event
import datetime

MODEL = MODELS.REASONING_MODEL

data_analyst_agent = Agent(
    model=MODEL,
    name="data_analyst_agent",
    instruction=prompt.DATA_ANALYST_PROMPT,
    output_key="market_data_analysis_output",
    tools=[google_search],
)

def get_time_str():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def call_data_analyst_agent(input_prompt, **kwargs):
    model = MODEL
    model_capabilities = "search"
    agent_name = "data_analyst_agent"
    tool_used = ["google_search"]
    time_stamp_input = get_time_str()
    token_input = len(input_prompt.split()) if isinstance(input_prompt, str) else None

    log_agent_call_event(
        event_type="agent_call_input",
        agent=agent_name,
        model=model,
        model_capabilities=model_capabilities,
        tool_used=tool_used,
        input_prompt=input_prompt,
        output=None,
        output_type=None,
        time_stamp_input=time_stamp_input,
        time_stamp_output=None,
        token_input=token_input,
        token_output=None,
        context_files=kwargs.get("context_files"),
        extra=None,
    )

    output = data_analyst_agent(input_prompt, **kwargs)
    time_stamp_output = get_time_str()
    output_type = type(output).__name__
    token_output = len(str(output).split()) if output else None

    log_agent_call_event(
        event_type="agent_call_output",
        agent=agent_name,
        model=model,
        model_capabilities=model_capabilities,
        tool_used=tool_used,
        input_prompt=input_prompt,
        output=output,
        output_type=output_type,
        time_stamp_input=time_stamp_input,
        time_stamp_output=time_stamp_output,
        token_input=token_input,
        token_output=token_output,
        context_files=kwargs.get("context_files"),
        extra=None,
    )
    return output
