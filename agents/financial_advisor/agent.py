import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file at the project root
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

from .prompt import FINANCIAL_COORDINATOR_PROMPT

# Import sub-agent instances
from .sub_agents.data_analyst.agent import data_analyst_agent
from .sub_agents.execution_analyst.agent import execution_analyst_agent
from .sub_agents.risk_analyst.agent import risk_analyst_agent
from .sub_agents.trading_analyst.agent import trading_analyst_agent
from .sub_agents.news_analyst.agent import news_analyst_agent

from google.adk.agents import LlmAgent

logger = logging.getLogger(__name__)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

MODEL_COORDINATOR = os.getenv("COORDINATOR_MODEL", "gemini-1.5-flash")

financial_coordinator = LlmAgent(
    name="financial_coordinator",
    model=MODEL_COORDINATOR,
    description=(
        "Guides users through a structured process to receive financial advice "
        "by orchestrating expert subagents. Helps analyze market tickers, "
        "fetch specific data, process datasets, develop trading strategies, "
        "define execution plans, and evaluate overall risk."
    ),
    instruction=FINANCIAL_COORDINATOR_PROMPT,
    sub_agents=[
        data_analyst_agent,
        trading_analyst_agent,
        execution_analyst_agent,
        risk_analyst_agent,
        news_analyst_agent,  # Add the news analyst agent here
    ],
)

root_agent = financial_coordinator

def create_agent(*args, **kwargs):
    logger.info("Creating financial_coordinator (root_agent) via factory.")
    return root_agent

logger.info(f"Financial Coordinator root_agent initialized with tools: {[tool.agent.name for tool in root_agent.tools]}")
