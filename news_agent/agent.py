
# ADK Free Tier does NOT support function-calling tools (FunctionTool/AgentTool) with Gemini models.
# To ensure compatibility, only use tools natively supported by the free tier (e.g., google_search).
# See financial_advisor/data_analyst_agent for reference: it only uses google_search as a tool.

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from logs.logger import setup_logger, log_agent_event
from .prompt import NEWS_AGENT_PROMPT
import MODELS

AGENT_NAME = "news_agent"
logger = setup_logger(AGENT_NAME)

news_agent = LlmAgent(
    name=AGENT_NAME,
    model=MODELS.REASONING_MODEL,
    description="An agent that answers user questions by searching the web for the latest news and information.",
    instruction=NEWS_AGENT_PROMPT,
    output_key="news_agent_output",
    tools=[google_search],
)

root_agent = news_agent


