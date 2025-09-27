import json
import streamlit as st
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow

# -------------------------------
# SCOPES
# -------------------------------
CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# -------------------------------
# Calendar → Service Account
# -------------------------------
def get_calendar_credentials():
    try:
        service_account_info = json.loads(st.secrets["google"]["service_account"])
        creds = service_account.Credentials.from_service_account_info(
            service_account_info, scopes=CALENDAR_SCOPES
        )
        return creds
    except Exception as e:
        st.error(f"Error loading Calendar service account: {e}")
        return None

# -------------------------------
# Gmail → OAuth Flow
# -------------------------------
def get_gmail_credentials():
    creds = None
    client_secrets_json = st.secrets["google"]["client_secrets"]

    # Try to reuse token
    if "gmail_token" in st.session_state:
        creds = Credentials.from_authorized_user_info(
            st.session_state["gmail_token"], GMAIL_SCOPES
        )

    # If no valid creds, refresh or login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                json.loads(client_secrets_json),  # safer than eval
                GMAIL_SCOPES,
            )
            # ⚠️ Works locally, but fails on Streamlit Cloud without browser
            creds = flow.run_local_server(port=0)

        # Save in session_state
        st.session_state["gmail_token"] = json.loads(creds.to_json())

    return creds
