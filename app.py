import streamlit as st
import pandas as pd
import google_services
import data_cleaning
import openai_functions
import style

# Set the page configuration to wide mode
st.set_page_config(layout="wide", page_title="EDMO Feedback Dashboard")

# Mapping display names to worksheet names
worksheet_mapping = {
    "Mid-year": "feedback_midyear",
    "End of Year": "feedback_endofyear",
    "End of Session": "feedback_endofsession"
}


def load_and_prepare_data(sheet_name):
    """
    Load, clean, and process data for the selected worksheet.
    """
    # Load all dataframes
    dataframes = google_services.load_google_sheets_data("edmo_dashboard")
    df_midyear, df_endofyear_eng, df_endofyear_spa, df_endofsession, feedback_midyear, feedback_endofyear, feedback_endofsession = dataframes

    # Select the appropriate feedback and cleaning based on the worksheet selected
    if sheet_name == "feedback_midyear":
        cleaned_df = data_cleaning.clean_data(df_midyear)
        df_combined_mean = data_cleaning.create_grouped_df(cleaned_df)
        dic_comments = data_cleaning.create_comments_dict(cleaned_df)
        feedback = feedback_midyear
    elif sheet_name == "feedback_endofyear":
        cleaned_df = data_cleaning.clean_data(df_endofyear_eng)
        df_combined_mean = data_cleaning.create_grouped_df(cleaned_df)
        dic_comments = data_cleaning.create_comments_dict(cleaned_df)
        feedback = feedback_endofyear
    elif sheet_name == "feedback_endofsession":
        cleaned_df = data_cleaning.clean_data(df_endofsession)
        df_combined_mean = data_cleaning.create_grouped_df(cleaned_df)
        dic_comments = data_cleaning.create_comments_dict(cleaned_df)
        feedback = feedback_endofsession
    else:
        st.error("Invalid worksheet selection")
        return None, None, None

    # Check if 'Location' exists in both DataFrames
    if 'Location' not in feedback.columns:
        st.warning("The 'Location' column is missing in the feedback data.")
        st.write("Columns in feedback data:", feedback.columns)
        return None, None, dic_comments  # Returning None for feedback and df_combined_mean if 'Location' is missing

    if 'Location' not in df_combined_mean.columns:
        st.warning("The 'Location' column is missing in the combined mean data.")
        st.write("Columns in combined mean data:", df_combined_mean.columns)
        return None, None, dic_comments  # Returning None for feedback and df_combined_mean if 'Location' is missing

    # Merge feedback with combined mean to add the rating for each location
    feedback = feedback.merge(df_combined_mean[['Location', 'Combined Mean']], on='Location', how='left')
    feedback = feedback.sort_values(by='Combined Mean', ascending=False)

    return feedback, df_combined_mean, dic_comments


def main():
    style.set_bg_image(image_path="/Users/othmanbensouda/PycharmProjects/EDMO/images/colorkit.png", opacity=0.3)

    # Sidebar for worksheet selection with display names
    display_name = st.sidebar.selectbox("Select Worksheet", list(worksheet_mapping.keys()))
    sheet_name = worksheet_mapping[display_name]  # Get the actual worksheet name

    # Load and prepare data based on selected worksheet
    feedback, df_combined_mean, dic_comments = load_and_prepare_data(sheet_name)

    # Check if feedback or df_combined_mean is None due to missing 'Location' column, and if so, trigger update functions
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
        return  # Exit the main function as there's no need to display further

    # Display dynamic title with selected worksheet type in teal color
    st.markdown(f"<h1 style='color: #6BD0C3;'>EDMO {display_name} Feedback Analysis Dashboard</h1>",
                unsafe_allow_html=True)

    # Custom CSS for primary button color in pinkish-red
    custom_button_style = """
        <style>
            .stButton > button {
                background-color: #CB3A5F; /* Pinkish-red */
                color: white; /* White text */
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            .stButton > button:hover {
                background-color: #A32E4B; /* Slightly darker on hover */
            }
        </style>
    """
    st.markdown(custom_button_style, unsafe_allow_html=True)

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

    # Custom style for the containers with updated colors
    # Custom style for the containers with updated colors
    container_style = """
        <style>
            .container {
                background-color: #F9F9F9;
                padding: 20px;
                margin: 10px 0;
                border-radius: 8px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                border-left: 5px solid #CB3A5F; /* Match button color */
            }
            .location-title {
                font-size: 1.7em;
                font-weight: bold;
                color: #F5C042; /* Golden Yellow */
            }
            .rating {
                font-size: 1.2em;
                color: #6BD0C3; /* Teal */
                font-weight: bold;
            }
            .sentiment {
                font-size: 1em;
                color: #555555;
            }
            /* Change the color of all h3 headers */
            h3 {
                color: #03045A; /* Dark Blue for Recommendations */
                font-size: 1.6em;
                font-weight: bold;
                margin-top: 15px;
            }
        </style>
    """
    st.markdown(container_style, unsafe_allow_html=True)

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
