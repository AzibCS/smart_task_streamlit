from googleapiclient.discovery import build
from .google_auth import get_calendar_credentials
from datetime import datetime, timedelta
import pandas as pd

class CalendarManager:
    def __init__(self, creds=None):
        self.creds = creds or get_calendar_credentials()
        self.service = build("calendar", "v3", credentials=self.creds)

    def fetch_events(self, days_ahead=7, max_results=20, calendar_id="primary"):
        try:
            now = datetime.utcnow().isoformat() + "Z"
            future = (datetime.utcnow() + timedelta(days=days_ahead)).isoformat() + "Z"

            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=now,
                timeMax=future,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

            items = events_result.get("items", [])
            if not items:
                return pd.DataFrame(columns=["Title", "Start Time"])

            out = []
            for e in items:
                start = e["start"].get("dateTime", e["start"].get("date"))
                if "T" in start:
                    start = datetime.fromisoformat(start.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
                out.append({
                    "Title": e.get("summary", "(no title)"),
                    "Start Time": start,
                    "Description": e.get("description", ""),
                    "Link": e.get("htmlLink", "")
                })

            return pd.DataFrame(out)

        except Exception as ex:
            return pd.DataFrame([{"Title": f"Error: {ex}", "Start Time": ""}])
