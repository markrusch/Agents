# C:\Users\markr\OneDrive\Documents\Mark Rusch\AI\logs\logger.py
import logging
import os
import importlib
import json
from datetime import datetime

def _get_agent_logs_dir(agent_name: str) -> str:
    # Place logs inside the agent's own folder: <agent_module>/logs/
    try:
        agent_module = importlib.import_module(agent_name)
        agent_dir = os.path.dirname(agent_module.__file__)
    except Exception:
        # fallback: use cwd
        agent_dir = os.path.join(os.getcwd(), agent_name)
    agent_logs_dir = os.path.join(agent_dir, "logs")
    os.makedirs(agent_logs_dir, exist_ok=True)
    return agent_logs_dir

def _get_file_logger(logger_name: str, log_file_path: str, level: int = logging.INFO, include_stream_handler: bool = True):
    """
    Helper function to create and configure a logger.
    - logger_name: The name for logging.getLogger()
    - log_file_path: The full path to the log file.
    - level: The logging level.
    - include_stream_handler: Whether to also log to console.
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)
    logger.propagate = False # Prevents logs from being passed to the root logger

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # File Handler
    # Avoid duplicate file handlers for the same logger and file
    has_file_handler = any(
        isinstance(h, logging.FileHandler) and
        getattr(h, "baseFilename", None) == os.path.abspath(log_file_path)
        for h in logger.handlers
    )
    if not has_file_handler:
        file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Stream Handler (Console)
    if include_stream_handler:
        # Avoid duplicate stream handlers for the same logger
        has_stream_handler = any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
        if not has_stream_handler:
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

    return logger

def setup_logger(agent_name: str, level: int = logging.INFO, include_stream_handler: bool = True):
    """
    Sets up the main logger for an agent.
    Logs to logs/<agent_name>/<agent_name>.log and optionally to console.
    """
    agent_logs_dir = _get_agent_logs_dir(agent_name)
    log_file = os.path.join(agent_logs_dir, f"{agent_name}.log")
    return _get_file_logger(logger_name=agent_name, log_file_path=log_file, level=level, include_stream_handler=include_stream_handler)


# Only use the main logger for all logging purposes.


def log_agent_event(
    logger,
    *,
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
    Log a structured agent event with all required fields.
    """
    event = {
        "event_type": event_type,
        "agent": agent,
        "model": model,
        "model_capabilities": model_capabilities,
        "tool_used": tool_used,
        "input_prompt": input_prompt,
        "output": output,
        "output_type": output_type,
        "time_stamp_input": time_stamp_input,
        "time_stamp_output": time_stamp_output,
        "token_input": token_input,
        "token_output": token_output,
    }
    if context_files:
        event["context_files"] = context_files
    if extra:
        event.update(extra)
    # Log as JSON for traceability
    logger.info(json.dumps(event, default=str))

# Request logging
LOG_FILE = os.path.join(os.path.dirname(__file__), "request.log")

def log_request(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")