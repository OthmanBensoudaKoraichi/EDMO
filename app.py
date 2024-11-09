import streamlit as st
import pandas as pd
import openai_functions
import style
import data_cleaning
import google_services

# Set the page configuration to wide mode
st.set_page_config(layout="wide", page_title="EDMO Feedback Dashboard")

# Mapping display names to worksheet names, keeping "End of Year" with unique processing
worksheet_mapping = {
    "Mid-year": "feedback_midyear",
    "End of Year": "feedback_endofyear",
    "End of Session": "feedback_endofsession"
}

def main():
    # Set background image from style module
    style.set_bg_image(image_path="https://raw.githubusercontent.com/OthmanBensoudaKoraichi/EDMO/refs/heads/main/images/colorkit.png", opacity=0.3)

    # Sidebar for worksheet selection with display names
    display_name = st.sidebar.selectbox("Select Worksheet", list(worksheet_mapping.keys()))
    sheet_name = worksheet_mapping[display_name]  # Get the actual worksheet name

    # Load and prepare data based on selected worksheet
    if sheet_name == "feedback_endofyear":
        # Unique processing for End of Year data
        feedback, df_combined_mean, dic_comments = data_cleaning.process_end_of_year_data()
    else:
        # Standard processing for Mid-year and End of Session
        feedback, df_combined_mean, dic_comments = data_cleaning.load_and_prepare_data(sheet_name)

    # Check if feedback or df_combined_mean is None due to missing 'Location' column
    if feedback is None or df_combined_mean is None:
        st.warning("The 'Location' column is missing. Running the update functions automatically.")

        # Run OpenAI analysis and update Google Sheets
        with st.spinner("Running analysis and updating Google Sheets..."):
            analysis_dict = openai_functions.analyze_comment(dic_comments)
            google_services.send_to_google_sheet(
                analysis_dict=analysis_dict,
                sheet_name="edmo_dashboard",
                worksheet_name=sheet_name
            )
        st.success("Dashboard updated successfully!")
        return

    # Display dynamic title with selected worksheet type in teal color
    st.markdown(f"<h1 style='color: #6BD0C3;'>EDMO {display_name} Feedback Analysis Dashboard</h1>",
                unsafe_allow_html=True)

    # Apply button and container styles from style module
    st.markdown(style.set_button_style(), unsafe_allow_html=True)
    st.markdown(style.set_container_style(), unsafe_allow_html=True)

    # Primary Update Dashboard button
    if st.button("Update Dashboard"):
        with st.spinner("Updating dashboard..."):
            # Run the OpenAI analysis
            analysis_dict = openai_functions.analyze_comment(dic_comments)
            # Send the analysis results to Google Sheets
            google_services.send_to_google_sheet(
                analysis_dict=analysis_dict,
                sheet_name="edmo_dashboard",
                worksheet_name=sheet_name
            )
        st.success("Dashboard updated successfully!")

    # Display the date of last update
    if not feedback.empty:
        date_sent = feedback["Date Sent"].iloc[0]
        st.markdown(f"**Data updated on:** {date_sent}")

    # Display each location in a styled container
    for _, row in feedback.iterrows():
        location = row["Location"]
        analysis = row["Analysis"]
        rating = row["Combined Mean"]

        # Container with custom HTML and CSS
        container_html = f"""
        <div class="container">
            <div class="location-title">{location} <span class="rating">(Rating: {rating})</span></div>
            <div class="sentiment"><strong>Overall Sentiment:</strong> {analysis}</div>
        </div>
        """
        st.markdown(container_html, unsafe_allow_html=True)


if __name__ == '__main__':
    main()

