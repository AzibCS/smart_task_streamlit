# main.py
import streamlit as st
import pandas as pd
from services.calendar_manager import CalendarManager
from services.email_manager import EmailManager
from services.task_manager import TaskManager
from services.logger_manager import Logger  # make sure your Logger file is renamed

# -----------------------------
# Initialize Logger
# -----------------------------
logger = Logger()

# -----------------------------
# Sidebar / Tabs
# -----------------------------
st.sidebar.title("Smart Task Automation Dashboard")
tab = st.sidebar.radio("Select Tab", ["Configuration", "Calendar", "Emails", "Tasks", "Logs"])

# -----------------------------
# Configuration Tab
# -----------------------------
if tab == "Configuration":
    st.header("API Configuration")
    
    if "creds" not in st.session_state:
        st.session_state.creds = {}

    st.session_state.creds['trello_key'] = st.text_input("Trello API Key", type="password")
    st.session_state.creds['trello_token'] = st.text_input("Trello API Token", type="password")
    
    st.success("Enter Trello credentails and proceed to Task tab")

# -----------------------------
# Calendar Tab
# -----------------------------
elif tab == "Calendar":
    st.header("Upcoming Events")
    try:
        cm = CalendarManager()
        events = cm.fetch_events(days_ahead=7)
        st.dataframe(events)

        # Log action
        logger.log_action("fetch_events", f"Fetched {len(events)} events")
        
        # Optional: chart of events per day
        if not events.empty:
            events['Start Time'] = pd.to_datetime(events['Start Time'], errors='coerce')
            chart_data = events.groupby(events['Start Time'].dt.date).size()
            st.bar_chart(chart_data)

    except Exception as e:
        st.error(f"Error fetching calendar events: {e}")

# -----------------------------
# Emails Tab
# -----------------------------
elif tab == "Emails":
    st.header("Inbox Summary")
    try:
        em = EmailManager()
        emails = em.fetch_emails(max_results=50)
        st.dataframe(emails)

        # Optional: chart by sender
        if not emails.empty:
            sender_count = emails['from'].value_counts()
            st.bar_chart(sender_count)

        # --- Add sorting section ---
        st.subheader("Email Sorting")
        keyword = st.text_input("Keyword to search in sender/subject")
        label = st.text_input("Label to apply")
        archive = st.checkbox("Archive emails after labeling")

        if st.button("Apply Sorting"):
            rules = [{"keyword": keyword, "label": label, "archive": archive}]
            results = em.sort_emails(rules=rules)
            st.write("Sorted Emails:", results)

    except Exception as e:
        st.error(f"Error fetching emails: {e}")


# -----------------------------
# Tasks Tab
# -----------------------------

elif tab == "Tasks":
    st.header("Trello Tasks")
    try:
        if "creds" not in st.session_state or not st.session_state.creds.get("trello_key") or not st.session_state.creds.get("trello_token"):
            st.warning("Please enter your Trello API Key & Token in the Configuration tab.")
        else:
            tm = TaskManager(
                api_key=st.session_state.creds.get("trello_key"),
                token=st.session_state.creds.get("trello_token")
            )
            tasks = tm.fetch_all_tasks()
            st.dataframe(tasks)

            report = tm.generate_report()
            st.write(f"Total Tasks: {report['total']}, Completed: {report['completed']}, Pending: {report['pending']}")

            if not tasks.empty:
                status_count = tasks['status'].value_counts()
                st.bar_chart(status_count)

            logger.log_action("fetch_tasks", f"Fetched {len(tasks)} tasks")
    except Exception as e:
        st.error(f"Error fetching tasks: {e}")


# -----------------------------
# Logs Tab
# -----------------------------
elif tab == "Logs":
    st.header("Automation Logs")
    try:
        logs_df = logger.get_logs()
        st.dataframe(logs_df)

        # Download logs as CSV
        st.download_button(
            label="Download Logs CSV",
            data=logger.export_logs("csv"),
            file_name="automation_logs.csv"
        )

        # Optional: Download logs as JSON
        st.download_button(
            label="Download Logs JSON",
            data=logger.export_logs("json"),
            file_name="automation_logs.json"
        )

    except Exception as e:
        st.error(f"Error displaying logs: {e}")
