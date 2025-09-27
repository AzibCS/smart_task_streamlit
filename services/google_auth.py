import os
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CRED_DIR = os.path.join(BASE_DIR, "credentials")
CRED_PATH = os.path.join(CRED_DIR, "credentials.json")

def ensure_credentials_file():
    """Writes credentials.json from Streamlit secrets if running in cloud"""
    os.makedirs(CRED_DIR, exist_ok=True)
    if "google" in st.secrets and "client_secrets" in st.secrets["google"]:
        with open(CRED_PATH, "w", encoding="utf-8") as f:
            f.write(st.secrets["google"]["client_secrets"])
    return CRED_PATH

def get_google_credentials():
    creds = None

    # Ensure credentials.json exists
    cred_file = ensure_credentials_file()

    flow = InstalledAppFlow.from_client_secrets_file(cred_file, SCOPES)

    if os.environ.get("OAUTH_FLOW", "local") == "console":
        # Use console flow on Streamlit Cloud
        auth_url, _ = flow.authorization_url(prompt="consent")
        st.write("👉 [Click here to authorize Google access](" + auth_url + ")")

        auth_code = st.text_input("Paste the Google authorization code here:")
        if st.button("Submit Code"):
            creds = flow.fetch_token(code=auth_code)
    else:
        # Local dev
        creds = flow.run_local_server(port=0)

    return creds
