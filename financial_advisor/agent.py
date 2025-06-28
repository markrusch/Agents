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

"""Financial coordinator: provide reasonable investment strategies"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
import MODELS
from . import prompt
from .sub_agents.data_analyst import data_analyst_agent
from .sub_agents.execution_analyst import execution_analyst_agent
from .sub_agents.risk_analyst import risk_analyst_agent
from .sub_agents.trading_analyst import trading_analyst_agent
from logs.logger import setup_logger, log_agent_event

AGENT_NAME = "financial_advisor"
logger = setup_logger(AGENT_NAME)

import datetime
import time

def get_time_str():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def emit_event(event_type, subagent_name, details=None, **kwargs):
    """
    Emit a structured ADK-style event.
    """
    event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "subagent": subagent_name,
        "details": details or {},
    }
    if kwargs:
        event["details"].update(kwargs)
    logger.info(f"ADK_EVENT: {event}")

def log_subagent_call(subagent_name, **kwargs):
    emit_event("subagent_call", subagent_name, {"args": kwargs})

def log_event(event, subagent_name="financial_coordinator", **kwargs):
    emit_event("event", subagent_name, {"message": event, **kwargs})

def log_request(request, subagent_name="financial_coordinator", **kwargs):
    emit_event("request", subagent_name, {"message": request, **kwargs})
    logger.info(f"REQUEST: {request}")

def log_response(response, subagent_name="financial_coordinator", **kwargs):
    emit_event("response", subagent_name, {"message": response, **kwargs})
    logger.info(f"RESPONSE: {response}")

MODEL = MODELS.REASONING_MODEL


financial_coordinator = LlmAgent(
    name="financial_coordinator",
    model=MODEL,
    description=(
        "guide users through a structured process to receive financial "
        "advice by orchestrating a series of expert subagents. help them "
        "analyze a market ticker, develop trading strategies, define "
        "execution plans, and evaluate the overall risk."
    ),
    instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
    output_key="financial_coordinator_output",
    tools=[
        AgentTool(agent=data_analyst_agent),
        AgentTool(agent=trading_analyst_agent),
        AgentTool(agent=execution_analyst_agent),
        AgentTool(agent=risk_analyst_agent),
    ],
)

root_agent = financial_coordinator

def agent_call_with_logging(agent, input_prompt, **kwargs):
    """
    Wraps an agent call, logs all required fields before and after execution.
    """
    model = getattr(agent, "model", "unknown")
    model_capabilities = getattr(agent, "capabilities", "unknown")
    agent_name = getattr(agent, "name", "unknown")
    tool_used = getattr(agent, "tools", None)
    if tool_used:
        tool_used = [getattr(t, "name", str(t)) for t in tool_used]
    else:
        tool_used = []
    time_stamp_input = get_time_str()
    token_input = len(input_prompt.split()) if isinstance(input_prompt, str) else None

    # Log input event
    log_agent_event(
        logger,
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

    # Call the agent
    output = agent(input_prompt, **kwargs) if callable(agent) else None
    time_stamp_output = get_time_str()
    output_type = type(output).__name__
    token_output = len(str(output).split()) if output else None

    # Log output event
    log_agent_event(
        logger,
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
