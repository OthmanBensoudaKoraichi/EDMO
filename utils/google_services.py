import pandas as pd
import gspread
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime


def load_credentials():
    # Define scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

    # Access credentials from Streamlit secrets
    credentials_info = {
        "type": st.secrets["gcp_service_account"]["type"],
        "project_id": st.secrets["gcp_service_account"]["project_id"],
        "private_key_id": st.secrets["gcp_service_account"]["private_key_id"],
        "private_key": st.secrets["gcp_service_account"]["private_key"].replace("\\n", "\n"),
        "client_email": st.secrets["gcp_service_account"]["client_email"],
        "client_id": st.secrets["gcp_service_account"]["client_id"],
        "auth_uri": st.secrets["gcp_service_account"]["auth_uri"],
        "token_uri": st.secrets["gcp_service_account"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["gcp_service_account"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["gcp_service_account"]["client_x509_cert_url"]
    }

    return [scope,credentials_info]
def load_google_sheets_data(sheet_name):
    """
    Load data from Google Sheets and return DataFrames for each sheet.

    Parameters:
    - sheet_name (str): The name of the Google Sheets file.

    Returns:
    - List of DataFrames for each sheet within the Google Sheets file.
    """
    # Load credentials
    scope,credentials_info = load_credentials()

    # Authorize the client
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    client = gspread.authorize(creds)

    # Access each sheet and convert to DataFrames
    spreadsheet = client.open(sheet_name)
    dataframes = [pd.DataFrame(spreadsheet.get_worksheet(i).get_all_records()) for i in range(7)]

    return dataframes

def send_to_google_sheet(analysis_dict, sheet_name="edmo_dashboard", worksheet_name="feedback_midyear"):
    """
    Sends the analysis dictionary to a Google Sheet.

    Parameters:
    - analysis_dict (dict): A dictionary where each key is a location, and each value is the analysis string for that location.
    - sheet_name (str): The name of the Google Sheets file to update.
    - worksheet_name (str): The name of the specific worksheet/tab to update within the Google Sheet.

    Returns:
    - None
    """
    # Load credentials
    scope, credentials_info = load_credentials()

    # Authorize the client
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet by name and access the specified worksheet
    sheet = client.open(sheet_name).worksheet(worksheet_name)

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Prepare the data for insertion (convert dictionary to list of rows)
    data_to_insert = [["Location", "Analysis", "Date Sent"]]  # Header row
    for location, analysis in analysis_dict.items():
        data_to_insert.append([location, analysis, current_date])

    # Clear any existing data in the sheet and insert new data
    sheet.clear()
    sheet.update("A1", data_to_insert)  # Starting from cell A1


def send_feedback_to_google_sheet(positive_summary, improvement_summary, sheet_name="edmo_dashboard",
                                  worksheet_name="feedback_endofyear"):
    """
    Sends the summarized positive and improvement feedback to the specified Google Sheet and worksheet.

    Parameters:
    - positive_summary (str): Summary of positive feedback.
    - improvement_summary (str): Summary of improvement feedback.
    - sheet_name (str): Name of the Google Sheet.
    - worksheet_name (str): Name of the worksheet in the Google Sheet.
    """
    # Load credentials
    scope, credentials_info = load_credentials()

    # Authorize the client
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_info, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet and access the specified worksheet
    sheet = client.open(sheet_name).worksheet(worksheet_name)

    # Get the current date
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Prepare the data for insertion as a list of lists for Google Sheets
    data_to_insert = [
        ["Positive Feedback Summary", "Improvement Feedback Summary", "Date Sent"],  # Header row
        [positive_summary, improvement_summary, current_date]
    ]

    # Clear existing data and insert the new data
    sheet.clear()
    sheet.update("A1", data_to_insert)  # Starting from cell A1