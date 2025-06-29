# News Agent

A standalone AI agent for searching and summarizing the latest news and information using Google Search.

## Features
- Uses the built-in `google_search` tool from ADK
- Summarizes news and provides sources on request
- Simple, factual, and up-to-date

## Usage
- Place your API keys in the `.env` file as with other agents
- Register this agent with your ADK server or run it as a module

## Example Prompt
```
What are the latest developments in AI regulation?
Show me news about Tesla's recent earnings.
Find articles about the 2025 Olympics.
```

## Logging
- Uses the shared logging system in `logs/logger.py`
- All logs are written to `logs/news_agent/news_agent.log`
