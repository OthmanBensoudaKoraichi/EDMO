import streamlit as st
import pandas as pd
from utils import data_cleaning, google_services, openai_functions, style, data_processing
from datetime import datetime

# Set the page configuration to wide mode
st.set_page_config(layout="wide", page_title="EDMO End of Year Feedback Dashboard")



def main():
    # Title
    st.markdown("<h1 style='color: #6BD0C3;'>EDMO End of Year Feedback Analysis Dashboard</h1>", unsafe_allow_html=True)
    # Get all feedback data
    response_encoding, dimensions, satisfaction_indices = data_processing.get_feedback_data()

    style.configure_page_style_endofyear()

    # Load data from Google Sheets
    dataframes = google_services.load_google_sheets_data("edmo_dashboard")
    feedback_endofyear_df = dataframes[5]  # Assuming feedback_endofyear is the 6th sheet

    # Load feedback summaries from Google Sheets
    feedback_summaries = data_processing.load_feedback_summaries(feedback_endofyear_df)
    last_update_date = feedback_summaries.get("last_update_date", "No previous updates")
    positive_feedback_summary = feedback_summaries["positive_summary"]
    improvement_feedback_summary = feedback_summaries["improvement_summary"]

    # Check if summaries need to be generated
    should_generate_feedback = not positive_feedback_summary or not improvement_feedback_summary

    # Update dashboard if needed
    col1, _ = st.columns([1, 9])
    with col1:
        if st.button("Update Dashboard") or should_generate_feedback:
            with st.spinner("Updating dashboard..."):
                positive_feedback_summary, improvement_feedback_summary, last_update_date = data_processing.update_feedback_summaries_endofyear(
                    dataframes)

    # Display last update date
    st.write(f"**Last updated:** {last_update_date}")

    # Display dimensions and scores
    feedback_df = pd.concat([dataframes[1], dataframes[2]], ignore_index=True)
    style.display_dimensions_scores_endofyear(feedback_df, dimensions, response_encoding, satisfaction_indices)

    # Display feedback summaries
    st.markdown("<div class='section-title'>Feedback & Recommendations</div>", unsafe_allow_html=True)
    feedback_container_html = f"""
    <div class="container">
        <h3>Positive Aspects</h3>
        <p>{positive_feedback_summary}</p>
        <h3>Areas for Improvement</h3>
        <p>{improvement_feedback_summary}</p>
    </div>
    """
    st.markdown(feedback_container_html, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
