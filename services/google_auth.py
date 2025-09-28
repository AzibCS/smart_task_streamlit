import os
import json
import base64
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Scopes for Calendar and Gmail read-only access
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def get_google_credentials():
    """
    Load Google credentials from service account stored in Streamlit secrets.
    Returns service account credentials for Calendar/Gmail API.
    """
    if "google_creds" in st.session_state:
        return st.session_state.google_creds

    try:
        # Decode Base64 service account JSON
        service_b64 = st.secrets["google"]["service_account_b64"]
        service_json = base64.b64decode(service_b64)
        credentials_info = json.loads(service_json)

        # Create service account credentials
        creds = service_account.Credentials.from_service_account_info(
            credentials_info,
            scopes=SCOPES
        )

        # Store in session_state
        st.session_state.google_creds = creds
        return creds

    except Exception as e:
        st.error(f"Error loading Calendar service account: {e}")
        return None

def get_calendar_credentials():
    creds = get_google_credentials()
    if not creds:
        return None
    return build("calendar", "v3", credentials=creds)

def get_gmail_credentials():
    creds = get_google_credentials()
    if not creds:
        return None
    return build("gmail", "v1", credentials=creds)
