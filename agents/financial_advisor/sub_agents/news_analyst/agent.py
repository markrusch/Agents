from google.adk.agents import LlmAgent
from google.adk.tools import google_search, ToolContext
from .prompt import NEWS_ANALYST_PROMPT

def before_tool_callback(tool_context: ToolContext):
    print(f"[NewsAnalyst] About to call tool: {tool_context.tool_name} with args: {tool_context.args}")
    return None

news_analyst_agent = LlmAgent(
    name="news_analyst_agent",
    model="gemini-1.5-flash",
    description="Summarizes current important news trends relevant to the strategy at hand using Google Search.",
    instruction=NEWS_ANALYST_PROMPT,
    tools=[google_search],
    before_tool_callback=before_tool_callback,
)
