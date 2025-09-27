import os, json, requests, pandas as pd, streamlit as st

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCAL_TRELLO_JSON = os.path.join(BASE_DIR, "credentials", "trello.json")

class TaskManager:
    def __init__(self, api_key=None, token=None):
        # 1) prefer passed in (from UI)
        self.api_key = api_key
        self.token = token
        # 2) fallback to st.secrets (deployed)
        try:
            if (not self.api_key or not self.token) and "trello" in st.secrets:
                self.api_key = self.api_key or st.secrets["trello"].get("api_key")
                self.token   = self.token   or st.secrets["trello"].get("api_token")
        except Exception:
            pass
        # 3) fallback to local file for dev
        if (not self.api_key or not self.token) and os.path.exists(LOCAL_TRELLO_JSON):
            with open(LOCAL_TRELLO_JSON, "r", encoding="utf-8") as f:
                creds = json.load(f)
                self.api_key = self.api_key or creds.get("api_key")
                self.token   = self.token   or creds.get("token")

        if not self.api_key or not self.token:
            raise ValueError("Missing Trello API key/token. Provide via UI, st.secrets, or credentials/trello.json (dev).")
        self.base_url = "https://api.trello.com/1"

    def fetch_boards(self):
        url = f"{self.base_url}/members/me/boards"
        params = {"key": self.api_key, "token": self.token, "fields": "name,url"}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return []
        return response.json()

    def fetch_tasks(self, board_id=None):
        if not board_id:
            boards = self.fetch_boards()
            if not boards:
                return pd.DataFrame([{"task": "No boards found", "status": "N/A"}])
            board_id = boards[0]["id"]

        url = f"{self.base_url}/boards/{board_id}/cards"
        params = {"key": self.api_key, "token": self.token, "fields": "name,due,closed"}
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return pd.DataFrame([{"task": "Error fetching cards", "status": response.text}])

        cards = response.json()
        tasks = []
        for c in cards:
            tasks.append({
                "task": c.get("name"),
                "due": c.get("due", "No due date"),
                "status": "Completed" if c.get("closed") else "Pending"
            })
        return pd.DataFrame(tasks)

    def fetch_all_tasks(self):
        """Fetch tasks from all boards"""
        boards = self.fetch_boards()
        if not boards:
            return pd.DataFrame([{"task": "No boards found", "status": "N/A"}])

        all_tasks = pd.DataFrame()
        for b in boards:
            df = self.fetch_tasks(board_id=b["id"])
            df["board_name"] = b["name"]
            all_tasks = pd.concat([all_tasks, df], ignore_index=True)

        return all_tasks

    def generate_report(self, board_id=None):
        df = self.fetch_tasks(board_id)
        if df.empty or "status" not in df.columns:
            return {"total": 0, "completed": 0, "pending": 0}

        total = len(df)
        completed = (df["status"] == "Completed").sum()
        pending = (df["status"] == "Pending").sum()

        return {"total": total, "completed": completed, "pending": pending}
