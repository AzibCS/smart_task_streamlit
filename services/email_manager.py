from googleapiclient.discovery import build
from .google_auth import get_google_credentials
import pandas as pd

class EmailManager:
    def __init__(self):
        self.creds = get_google_credentials()
        if not self.creds:
            raise Exception("Usser not signed in")

        self.service = build("gmail", "v1", credentials=self.creds)

    def fetch_emails(self, max_results=20):
        """
        Gmail via service account will only work with domain-wide delegation.
        For personal accounts, this will raise an error.
        """
        try:
            results = self.service.users().messages().list(
                userId="me",
                labelIds=["INBOX"],
                q="in:inbox -category:promotions -category:social",
                maxResults=max_results
            ).execute()
            messages = results.get("messages", [])

            emails = []
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId="me", id=msg["id"]
                ).execute()

                headers = msg_data.get("payload", {}).get("headers", [])
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), "No Subject")
                sender = next((h["value"] for h in headers if h["name"] == "From"), "Unknown Sender")

                emails.append({
                    "Id": msg["id"],
                    "Subject": subject,
                    "From": sender,
                })

            return pd.DataFrame(emails)

        except Exception as e:
            # If service account cannot access Gmail, return friendly error
            return pd.DataFrame([{"Subject": "Error fetching emails", "From": str(e)}])


    def sort_emails(self, rules=None):
        """
        Apply simple rules to label or archive emails.
        rules: list of dicts [{"keyword": "urgent", "label": "Important", "archive": True}]
        """
        if rules is None:
            rules = []

        results = []
        for rule in rules:
            keyword = rule.get("keyword", "").lower()
            label_name = rule.get("label")
            archive = rule.get("archive", False)

            # 1️⃣ Check if label exists, create if not
            label_id = None
            if label_name:
                labels = self.service.users().labels().list(userId="me").execute().get("labels", [])
                for l in labels:
                    if l["name"] == label_name:
                        label_id = l["id"]
                        break
                if not label_id:
                    label = self.service.users().labels().create(
                        userId="me", body={"name": label_name, "labelListVisibility": "labelShow", "messageListVisibility": "show"}
                    ).execute()
                    label_id = label["id"]

            # 2️⃣ Fetch inbox emails
            emails = self.fetch_emails(max_results=50)
            for idx, row in emails.iterrows():
                if keyword in row["Subject"].lower() or keyword in row["From"].lower():
                    mods = {}
                    if label_id:
                        mods["addLabelIds"] = [label_id]
                    if archive:
                        mods["removeLabelIds"] = ["INBOX"]

                    if mods:
                        self.service.users().messages().modify(
                            userId="me", id=row["id"], body=mods
                        ).execute()
                        results.append({"email_id": row["id"], "action": f"Labeled: {label_name}, Archived: {archive}"})

        return results
