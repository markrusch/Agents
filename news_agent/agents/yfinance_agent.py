import json
import datetime
import yfinance as yf
import logging
from adk.agent import Agent
from configs.settings import RESULTS_DIR

class YFinanceTool:
    """
    Simple tool to fetch price, historical data, and news for a ticker using yfinance.
    """
    def __init__(self):
        pass

    def execute(self, function_name, api_params):
        ticker = api_params.get("symbol") or api_params.get("ticker")
        if not ticker:
            return {"error": "No ticker provided."}
        try:
            stock = yf.Ticker(ticker)
            if function_name == "price":
                price = stock.info.get("regularMarketPrice")
                return {"price": price}
            elif function_name == "history":
                period = api_params.get("period", "5d")
                interval = api_params.get("interval", "1d")
                hist = stock.history(period=period, interval=interval)
                return hist.reset_index().to_dict(orient="records")
            elif function_name == "news":
                num_articles = api_params.get("num_articles", 5)
                news = stock.news[:num_articles]
                return [
                    {
                        "title": item.get("title"),
                        "link": item.get("link"),
                        "publisher": item.get("publisher"),
                        "providerPublishTime": item.get("providerPublishTime"),
                        "summary": item.get("summary", "")
                    }
                    for item in news
                ]
            else:
                return {"error": f"Unknown function: {function_name}"}
        except Exception as e:
            return {"error": str(e)}

class YFinanceAgent(Agent):
    def __init__(self):
        self.logger = logging.getLogger("YFinanceAgent")
        self.results_dir = RESULTS_DIR
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Results directory ensured at: {self.results_dir}")
        yfinance_tool = YFinanceTool()
        super().__init__(name="YFinanceAgent", llm_model=None, tools=[yfinance_tool])

    def _extract_parameters(self, query: str):
        # Simple extraction: expects queries like "price AAPL", "history TSLA 1mo 1d", "news MSFT 10"
        tokens = query.strip().split()
        if not tokens:
            return {"error": "Empty query."}
        function = tokens[0].lower()
        if function not in ("price", "history", "news"):
            return {"error": f"Unknown function: {function}"}
        params = {}
        if len(tokens) > 1:
            params["symbol"] = tokens[1].upper()
        if function == "history":
            if len(tokens) > 2:
                params["period"] = tokens[2]
            if len(tokens) > 3:
                params["interval"] = tokens[3]
        if function == "news":
            if len(tokens) > 2:
                try:
                    params["num_articles"] = int(tokens[2])
                except Exception:
                    params["num_articles"] = 5
        return {"function": function, "params": params}

    def process(self, query: str, **kwargs):
        self.logger.info(f"Processing query: {query}")
        extracted = self._extract_parameters(query)
        if "error" in extracted:
            return {"status": "error", "message": extracted["error"]}
        function = extracted["function"]
        params = extracted["params"]
        tool = self.get_tool("YFinanceTool")
        if not tool:
            return {"status": "error", "message": "YFinanceTool not found."}
        result = tool.execute(function, params)
        # Optionally save result
        try:
            filename = f"{function}_{params.get('symbol','unknown')}_{datetime.datetime.now().strftime('%Y%m%d')}.json"
            filepath = self.results_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
            self.logger.info(f"Saved result to {filepath}")
        except Exception as e:
            self.logger.warning(f"Could not save result: {e}")
        return {"status": "success", "result": result}

# For ADK agent loader
root_agent = YFinanceAgent()
