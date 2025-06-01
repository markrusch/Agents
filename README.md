## Database Setup & Usage


Important links:
- https://google.github.io/adk-docs/
- https://ai.google.dev/gemini-api/docs/pricing  #API Pricing
- https://python.langchain.com/docs/integrations/tools/ #All LangChain Tools


### 1. Prerequisites

- Ensure you have a supported database installed (e.g., PostgreSQL, MySQL, SQLite).
- Install required Python dependencies:
  ```
  pip install -r requirements.txt
  ```

### 2. Configuration

- Copy `.env.example` to `.env` and add your database credentials. For example:
  ```
  GOOGLE_API_KEY=your-google-api-key-here
  ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key-here
  ```
- **Never commit your real `.env` file to git.**

### 3. Database Initialization

- If migrations are used, run the migration tool (e.g., Alembic, Django, Flask-Migrate) to create tables:
  ```
  # Example for Alembic
  alembic upgrade head
  ```

- Alternatively, run the provided initialization script if available:
  ```
  python scripts/init_db.py
  ```

### 4. Usage in the Project

- The application will automatically connect to the database using the credentials from your `.env` file.
- Database models and queries are managed in the `models/` or `database/` directory (adjust as per your project structure).
- Example usage in code:
  ```python
  from configs.settings import get_db_session

  session = get_db_session()
  result = session.execute("SELECT 1")
  ```

### 5. Troubleshooting

- Ensure your database server is running and accessible.
- Double-check your `.env` configuration for typos.
- Check logs for connection errors.

---

For more details, see the [configs](configs/) directory and any database-related scripts in the project.

### 6. Running the agents

To run your agent using the ADK web server, use the following command from your project root:

```
adk web agents/financial_advisor
```

- This will start a local web server (default: http://localhost:8000).
- You can interact with your agent via the web UI or API.
- Replace `agents/financial_advisor` with the path to your agent module if different.

### 7. Streaming and Hot Reload

**Streaming:**  
- ADK web UI and API support streaming responses by default. When you interact with your agent via the web interface (http://localhost:8000), responses are streamed as they are generated.

**Hot Reload (Auto-reload):**  
- By default, `adk web` will **not** automatically reload your agent when you change the source code.
- To enable auto-reload (hot reload) during development, use the `--reload` flag:

```
adk web agents/financial_advisor_google --reload
```

- With `--reload`, the server will watch your source files and automatically restart when you make changes. This allows you to edit your code and see changes without manually stopping and starting the server.

**Note:**  
- Some changes (like adding new dependencies) may still require a manual restart.
- For production, do **not** use `--reload`.

## Project Folder Structure

```
AI/
├── MODELS.py
├── __init__.py
├── .env
├── README.md
├── financial_advisor/
│   ├── __init__.py
│   ├── agent.py
│   ├── prompt.py
│   ├── test.py
│   └── sub_agents/
│       ├── __init__.py
│       ├── data_analyst.py
│       ├── trading_analyst.py
│       ├── execution_analyst.py
│       ├── risk_analyst.py
│       └── news_analyst.py
```

- `MODELS.py`: Central location for all model names/IDs.
- `financial_advisor/`: Main agent package.
  - `agent.py`: Root orchestrator agent.
  - `sub_agents/`: All sub-agent implementations.
  - `test.py`: Example/test script for agent and model import.
- `__init__.py`: Ensures `MODELS` is importable as `from .. import MODELS` within the package.

## How `financial_advisor` imports and prints `MODELS`

- In `financial_advisor/__init__.py`:
  ```python
  from . import agent
  from .. import MODELS
  ```
- In `financial_advisor/agent.py` (or any submodule):
  ```python
  from .. import MODELS
  ```
- In `financial_advisor/test.py`:
  ```python
  from .. import MODELS
  print("Financial Advisor Agent initialized with models:", MODELS)
  ```

**This setup ensures that `MODELS` is always available to your agent and sub-agents, and you can print or use it anywhere in the `financial_advisor` package.**
