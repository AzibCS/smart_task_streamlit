import csv
import json
import pandas as pd
from datetime import datetime
import os

class Logger:
    def __init__(self, log_file="logs.csv"):
        self.log_file = log_file
        # If file doesn't exist, create it with header
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "action", "details"])
    
    def log_action(self, action, details):
        """Log an action with timestamp"""
        with open(self.log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), action, details])
    
    def get_logs(self):
        """Return logs as a pandas DataFrame"""
        try:
            df = pd.read_csv(self.log_file)
            return df
        except Exception as e:
            return pd.DataFrame([{"timestamp": "", "action": "Error", "details": str(e)}])
    
    def export_logs(self, fmt="csv"):
        """Return logs as CSV or JSON string"""
        df = self.get_logs()
        if fmt.lower() == "csv":
            return df.to_csv(index=False)
        elif fmt.lower() == "json":
            return df.to_json(orient="records", indent=4)
        else:
            raise ValueError("Format must be 'csv' or 'json'")
