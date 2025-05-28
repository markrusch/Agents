import pandas as pd
import numpy as np
from google.adk.agents import LlmAgent, BaseAgent

class DataProcessingPipelineAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="data_processing_pipeline_agent", description="Cleans and analyzes financial data.")

    def execute(self, data: list, operation: str = "mean"):
        arr = np.array(data)
        if operation == "mean":
            return float(np.mean(arr))
        elif operation == "sum":
            return float(np.sum(arr))
        elif operation == "std":
            return float(np.std(arr))
        else:
            return {"error": f"Unknown operation: {operation}"}

data_processing_pipeline_agent = DataProcessingPipelineAgent()
