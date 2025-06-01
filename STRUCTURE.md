# Project Structure Overview

```
AI/
├── .env.example
├── .env
├── README.md
├── requirements.txt
├── configs/
│   └── settings.py
├── agents/
│   └── financial_advisor/
│       ├── __init__.py
│       ├── agent.py                # Root orchestrator agent (financial_coordinator)
│       ├── main.py                 # Entrypoint for running/testing the agent
│       ├── prompt.py               # Prompt for the financial coordinator
│       └── sub_agents/
│           ├── __init__.py         # Imports all sub-agents and orchestrator agent
│           ├── agent.py            # Sub-agents orchestrator (handles transfer, fallback, context, artifacts)
│           ├── data_analyst.py     # Data analyst agent (with yfinance and data pipeline tools)
│           ├── trading_analyst.py  # Trading analyst agent
│           ├── execution_analyst.py# Execution analyst agent
│           ├── risk_analyst.py     # Risk analyst agent
│           └── news_analyst.py     # News analyst agent (uses google_search tool)
```

**Key Points:**
- All sub-agents are in a flat structure under `sub_agents/` for simplicity.
- Each sub-agent is a single file (e.g., `data_analyst.py`, `trading_analyst.py`).
- `sub_agents/agent.py` is the orchestrator for sub-agents, handling transfer, fallback, and context tools.
- The root agent (`agent.py` in `financial_advisor/`) orchestrates the entire workflow and delegates to sub-agents.
- `main.py` can be used for local testing or as an entrypoint.
- `.env` and `.env.example` hold environment variables (API keys, etc).
- `requirements.txt` lists all Python dependencies.
- `README.md` contains setup and usage instructions.

**How to run:**
- Use `adk web agents/financial_advisor` from the project root to start the ADK web server.

