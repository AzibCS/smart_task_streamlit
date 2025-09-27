from google_auth_oauthlib.flow import InstalledAppFlow
import os, streamlit as st

SCOPES = [
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/gmail.readonly"
]

def get_google_credentials():
    if "google_creds" in st.session_state:
        return st.session_state.google_creds

    flow = InstalledAppFlow.from_client_secrets_file("credentials/credentials.json", SCOPES)

    oauth_flow = os.environ.get("OAUTH_FLOW", "console").lower()

    if oauth_flow == "console":
        # Manual flow for headless servers
        auth_url, _ = flow.authorization_url(prompt="consent")
        st.warning("Google Authentication Required")
        st.write("Click the link below, sign in, then paste the code here:")
        st.markdown(f"[Authenticate here]({auth_url})")

        auth_code = st.text_input("Enter the authorization code:")

        if st.button("Submit Code"):
            try:
                flow.fetch_token(code=auth_code)
                creds = flow.credentials
                st.session_state.google_creds = creds
                st.success("Authentication successful!")
                return creds
            except Exception as e:
                st.error(f"Failed to fetch token: {e}")
                return None
    else:
        # Local dev flow with browser
        creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")
        st.session_state.google_creds = creds
        return creds
