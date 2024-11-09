import streamlit as st
from utils import data_cleaning, google_services, openai_functions, style

# Set page configuration with favicon and collapsed sidebar
st.set_page_config(
    layout="wide",
    page_title="EDMO End of Year Feedback Dashboard",
    page_icon="https://raw.githubusercontent.com/OthmanBensoudaKoraichi/EDMO/refs/heads/main/images/edmo_logo.png",
    initial_sidebar_state="expanded"
)

def main():
    # Display the logo in the sidebar using the GitHub URL
    logo_url = "https://raw.githubusercontent.com/OthmanBensoudaKoraichi/EDMO/refs/heads/main/images/edmo_logo.png"
    st.sidebar.image(logo_url, use_column_width=True)
    # Set background image from style module
    style.set_bg_image(image_path="https://raw.githubusercontent.com/OthmanBensoudaKoraichi/EDMO/refs/heads/main/images/colorkit.png", opacity=0.3)

    # Load and prepare data for the End of Session worksheet
    feedback, df_combined_mean, dic_comments = data_cleaning.load_and_prepare_data("feedback_endofsession")

    # Check if feedback or df_combined_mean is None due to missing 'Location' column
    if feedback is None or df_combined_mean is None:
        st.warning("The 'Location' column is missing. Running the update functions automatically.")

        # Run OpenAI analysis and update Google Sheets
        with st.spinner("Running analysis and updating Google Sheets..."):
            analysis_dict = openai_functions.analyze_comment(dic_comments)
            google_services.send_to_google_sheet(
                analysis_dict=analysis_dict,
                sheet_name="edmo_dashboard",
                worksheet_name="feedback_endofsession"
            )
        st.success("Dashboard updated successfully!")
        return

    # Display title for the End of Session Feedback Analysis Dashboard
    st.markdown("<h1 style='color: #6BD0C3;'>EDMO End of Session Feedback Analysis Dashboard</h1>",
                unsafe_allow_html=True)

    # Apply button and container styles from style module
    st.markdown(style.set_button_style(), unsafe_allow_html=True)
    st.markdown(style.set_container_style_midyear_endofsession(), unsafe_allow_html=True)

    # Primary Update Dashboard button
    if st.button("Update Dashboard"):
        with st.spinner("Updating dashboard..."):
            # Run the OpenAI analysis
            analysis_dict = openai_functions.analyze_comment(dic_comments)
            # Send the analysis results to Google Sheets
            google_services.send_to_google_sheet(
                analysis_dict=analysis_dict,
                sheet_name="edmo_dashboard",
                worksheet_name="feedback_endofsession"
            )
        st.success("Dashboard updated successfully!")

    # Display the date of last update
    if not feedback.empty:
        date_sent = feedback["Date Sent"].iloc[0]
        st.markdown(f"**Last updated:** {date_sent}")

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
