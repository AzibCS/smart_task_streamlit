
import os
from google_auth_oauthlib.flow import InstalledAppFlow
import streamlit as st

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CRED_DIR = os.path.join(BASE_DIR, "credentials")
CRED_PATH = os.path.join(CRED_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CRED_DIR, "token.json")

def ensure_client_secrets_from_st_secrets():
    # If you stored Google client JSON in Streamlit secrets, write it to credentials.json at runtime
    try:
        if "google" in st.secrets and "client_secrets" in st.secrets["google"]:
            os.makedirs(CRED_DIR, exist_ok=True)
            with open(CRED_PATH, "w", encoding="utf-8") as fh:
                fh.write(st.secrets["google"]["client_secrets"])
            return True
    except Exception as e:
        st.error(e, "an erorr occured while writing to credentials.json")
    return False

def get_google_credentials():
    """
    Use run_local_server locally (default) and run_console on deployed host if env OAUTH_FLOW=console.
    Credentials are stored in st.session_state for the session.
    """
    # reuse in-session
    if "google_creds" in st.session_state:
        return st.session_state.google_creds

    # If deployed and you placed client JSON in st.secrets, write it to credentials path
    if "google" in st.secrets and "client_secrets" in st.secrets["google"]:
        ensure_client_secrets_from_st_secrets()

    if not os.path.exists(CRED_PATH):
        raise FileNotFoundError(f"Missing credentials.json at {CRED_PATH}. For deployment, add google.client_secrets to Streamlit secrets.")

    flow = InstalledAppFlow.from_client_secrets_file(CRED_PATH, SCOPES)

    oauth_flow = os.environ.get("OAUTH_FLOW", "local").lower()
    if oauth_flow == "console":
        # Hosted environment: user follows URL and pastes auth code
        creds = flow.run_console()
    else:
        # Local development: open a local port (let OS pick free port)
        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        # Save token locally for convenience only when developing
        try:
            os.makedirs(CRED_DIR, exist_ok=True)
            with open(TOKEN_PATH, "w", encoding="utf-8") as f:
                f.write(creds.to_json())
        except Exception:
            pass

    st.session_state.google_creds = creds
    return creds
