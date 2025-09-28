# services/google_auth.py
import json
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# requested scopes
SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def _get_client_config():
    """
    Load client_secrets JSON from Streamlit secrets.
    """
    if "google" not in st.secrets or "client_secrets" not in st.secrets["google"]:
        raise FileNotFoundError("Google client_secrets not found in Streamlit secrets.")
    return json.loads(st.secrets["google"]["client_secrets"])

def _get_redirect_uri():
    # prefer explicit redirect_uri in secrets, otherwise fallback to first redirect in client config
    if "redirect_uri" in st.secrets["google"]:
        return st.secrets["google"]["redirect_uri"]
    cfg = _get_client_config()
    web = cfg.get("web") or cfg.get("installed") or {}
    uris = web.get("redirect_uris", [])
    return uris[0] if uris else None

def get_google_credentials():

    # Returns google.oauth2.credentials.Credentials for the currently signed-in user.
    
    # 1) reuse session
    if "google_creds" in st.session_state:
        creds = Credentials.from_authorized_user_info(
            json.loads(st.session_state["google_creds"]), SCOPES
        )
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            st.session_state["google_creds"] = creds.to_json()
        return creds

    # 2) check stored token in secrets (optional admin step)
    if "google" in st.secrets and "stored_token" in st.secrets["google"]:
        try:
            token_info = json.loads(st.secrets["google"]["stored_token"])
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
            st.session_state["google_creds"] = creds.to_json()
            return creds
        except Exception:
            pass

    # 3) check for 'code' in the current URL (user was redirected back from Google)
    params = st.query_params
    if "code" in params:
        code = params.get("code")
        client_config = _get_client_config()
        redirect_uri = _get_redirect_uri()
        flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri)
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            st.session_state["google_creds"] = creds.to_json()
            # Clear query params
            st.query_params.clear()
            return creds
        except Exception as e:
            st.query_params.clear()
            return None

    return None

def get_authorization_url():
    """
    Returns (auth_url, state) to send user to Google for consent.
    """
    client_config = _get_client_config()
    redirect_uri = _get_redirect_uri()
    st.write("DEBUG redirect_uri:", redirect_uri)
    flow = Flow.from_client_config(client_config, scopes=SCOPES, redirect_uri=redirect_uri)
    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )
    return auth_url, state

def sign_out():
    if "google_creds" in st.session_state:
        del st.session_state["google_creds"]
    st.rerun()
