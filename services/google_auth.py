import os
import pickle
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def get_google_credentials():
    creds = None

    # Path inside secrets (string JSON)
    client_secrets_json = st.secrets["google"]["client_secrets"]

    # Load flow type from secrets
    oauth_flow = st.secrets["google"].get("oauth_flow", "local")

    # Try to load token from session_state
    if "google_token" in st.session_state:
        creds = Credentials.from_authorized_user_info(st.session_state["google_token"], SCOPES)

    # If no valid creds available, let user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_config(
                eval(client_secrets_json),  # Parse JSON string
                SCOPES
            )

            if oauth_flow == "console":
                creds = flow.run_console()
            else:
                creds = flow.run_local_server(port=0)

        # Save the credentials to session_state
        st.session_state["google_token"] = creds.to_json()

    return creds
