# financial_advisor/sub_agents/__init__.py
# Ensure PROJECT_ROOT_GUESS logic or similar is present if running this standalone
# or if 'logs' isn't directly findable from here.
# Typically, this __init__.py is imported by agent.py, which would have already set up sys.path.

# If this file might be the first point of import for logging for sub-agents,
# consider adding the sys.path modification here too, or ensure it's done by a higher-level entry point.
import sys
import os
PROJECT_ROOT_GUESS = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
# This assumes __init__.py is in AI/agents/financial_advisor/sub_agents/__init__.py
# So, PROJECT_ROOT_GUESS will be AI/
if PROJECT_ROOT_GUESS not in sys.path:
    sys.path.insert(0, PROJECT_ROOT_GUESS)

from logs.logger import setup_logger, log_agent_event

AGENT_NAME = "financial_advisor"

subagent_general_logger = setup_logger(AGENT_NAME, include_stream_handler=False)

import datetime

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
    subagent_general_logger.info(f"ADK_EVENT: {event}")

def log_subagent_activity(subagent_name, message: str, **kwargs):
    emit_event("subagent_activity", subagent_name, {"message": message, **kwargs})

def log_event(event_message, subagent_name="unknown", **kwargs):
    emit_event("event", subagent_name, {"message": event_message, **kwargs})

def log_request(request_message, subagent_name="unknown", **kwargs):
    emit_event("request", subagent_name, {"message": request_message, **kwargs})
    subagent_general_logger.info(f"REQUEST: {request_message}")

def log_response(response_message, subagent_name="unknown", **kwargs):
    emit_event("response", subagent_name, {"message": response_message, **kwargs})
    subagent_general_logger.info(f"RESPONSE: {response_message}")

def log_agent_call_event(
    event_type,
    agent,
    model,
    model_capabilities,
    tool_used,
    input_prompt,
    output,
    output_type,
    time_stamp_input,
    time_stamp_output,
    token_input=None,
    token_output=None,
    context_files=None,
    extra=None
):
    """
    Log agent call event for sub-agents.
    """
    log_agent_event(
        subagent_general_logger,
        event_type=event_type,
        agent=agent,
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
        context_files=context_files,
        extra=extra,
    )