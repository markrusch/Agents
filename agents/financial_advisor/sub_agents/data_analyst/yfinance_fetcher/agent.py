import yfinance as yf
from google.adk.agents import BaseAgent

class YFinanceFetcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="yfinance_fetcher_agent", description="Fetches data from Yahoo Finance using yfinance.")

    def execute(self, ticker: str, period: str = "1mo", interval: str = "1d") -> dict:
        """
        Fetch historical market data for a ticker from Yahoo Finance.

        Args:
            ticker (str): The ticker symbol (e.g. 'AAPL', 'MSFT', '0700.HK').
            period (str): Data period (e.g. '1mo', '3mo', '1y', 'max').
            interval (str): Data interval (e.g. '1d', '1wk', '1mo').

        Returns:
            dict: List of OHLCV records as dicts, or an error message.
        """
        try:
            data = yf.download(ticker, period=period, interval=interval)
            if data.empty:
                return {"error": "No data found for ticker."}
            # Convert index to string for JSON serialization
            data = data.reset_index()
            data['Date'] = data['Date'].astype(str)
            return data.to_dict(orient="records")
        except Exception as e:
            return {"error": str(e)}

yfinance_fetcher_agent = YFinanceFetcherAgent()
