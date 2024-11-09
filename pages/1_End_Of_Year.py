import streamlit as st
import pandas as pd
import openai_functions
import style
import google_services
import data_cleaning
from datetime import datetime

# Set the page configuration to wide mode
st.set_page_config(layout="wide", page_title="EDMO End of Year Feedback Dashboard")

def load_feedback_summaries(dataframe):
    """
    Load feedback summaries for positive and improvement feedback from Google Sheets, including the last update date.

    Parameters:
    - Dataframe : feedback_endofyear

    Returns:
    - dict: Dictionary with keys 'positive_summary', 'improvement_summary', and 'last_update_date'.
    """
    # Retrieve summaries and date sent, default to empty strings if not found
    positive_summary = dataframe.get("Positive Feedback Summary", [""])[0]
    improvement_summary = dataframe.get("Improvement Feedback Summary", [""])[0]
    last_update_date = dataframe.get("Date Sent", ["No previous updates"])[0]

    return {
        "positive_summary": positive_summary,
        "improvement_summary": improvement_summary,
        "last_update_date": last_update_date
    }



# Encoding dictionary for responses
response_encoding = {
    "Strongly Agree": 5,
    "Agree": 4,
    "Not Sure": 3,
    "Disagree": 2,
    "Strongly Disagree": 1
}

# Dimensions with indices, corresponding summaries, and questions
dimensions = {
    "Program Accessibility": {
        "indices": [1, 2],
        "summary": "Measures ease of enrollment and support provided to parents.",
        "questions": [
            "Enrolling my kid(s) in EDMO was easy.",
            "Because my kid attends EDMO, I can go to school or work."
        ]
    },
    "Program Organization": {
        "indices": [3, 4, 5, 6],
        "summary": "Evaluates organization, safety, and staff communication with families.",
        "questions": [
            "EDMO is well organized.",
            "I felt EDMO provided my kid(s) with a physically and emotionally safe environment.",
            "EDMO staff makes my family feel welcome.",
            "EDMO staff keeps me informed about my kid’s participation in the program as necessary."
        ]
    },
    "Program Satisfaction": {
        "indices": [7, 8, 9],
        "summary": "Assesses overall satisfaction and likelihood of returning to EDMO.",
        "questions": [
            "If I had the opportunity, I would send my kid(s) to EDMO next year.",
            "General - My kid likes going to EDMO each day.",
            "General - My kid has fun at EDMO."
        ]
    },
    "Social-Emotional Learning (SEL)": {
        "indices": [10, 11, 12, 13, 14],
        "summary": "Reflects development in social skills, empathy, and self-awareness.",
        "questions": [
            "SEL: Collaboration - Since attending EDMO, my kid seems to be more comfortable working with others.",
            "SEL: Advocacy - Since attending EDMO, my kid seems more willing to speak up when something is unfair or people are being excluded.",
            "SEL: Problem-Solving - Since attending EDMO, my kid seems more able to solve problems on their own.",
            "SEL: Empathy - Since attending EDMO, my kid seems to understand that everyone’s feelings matter.",
            "SEL: Self-Awareness - Since attending EDMO, my kid seems to better understand the impact of their actions."
        ]
    },
    "STEAM Skills": {
        "indices": [15, 16, 17, 18],
        "summary": "Measures growth in science, technology, engineering, art, and resilience.",
        "questions": [
            "STEAM: Knowledge + Skills - Since attending EDMO, my kid seems to have learned more about science, technology, engineering, and/or art.",
            "STEAM: Curiosity - Since attending EDMO, my kid seems more curious about exploring science, technology, engineering, and/or art.",
            "STEAM: Identity - Since attending EDMO, my kid seems to be more confident in doing science, technology, engineering, and/or art.",
            "STEAM: Resilience - Since attending EDMO, my kid seems more willing to try new things, even if they are hard."
        ]
    },
    "School Engagement": {
        "indices": [19, 20],
        "summary": "Indicates impact on school enthusiasm and homework completion.",
        "questions": [
            "EDMO helps my kid feel more excited about going to school.",
            "EDMO helps my kid get their homework done on time."
        ]
    }
}


# Satisfaction columns using indices
satisfaction_indices = [21, 22]  # Assuming these are the last two columns

def main():
    # Set behavior for future pandas versions
    pd.set_option('future.no_silent_downcasting', True)

    # Set background image
    style.set_bg_image(
        image_path="https://raw.githubusercontent.com/OthmanBensoudaKoraichi/EDMO/refs/heads/main/images/colorkit.png",
        opacity=0.3
    )

    # Apply button styling
    st.markdown(style.set_button_style(), unsafe_allow_html=True)

    # Load data from Google Sheets
    dataframes = google_services.load_google_sheets_data("edmo_dashboard")
    feedback_endofyear_df = dataframes[5]  # Assuming feedback_endofyear is the 6th sheet

    # Retrieve last update date and existing summaries from Google Sheets
    feedback_summaries = load_feedback_summaries(feedback_endofyear_df)
    last_update_date = feedback_summaries.get("last_update_date", "No previous updates")

    # Extract positive and improvement summaries from the loaded data
    positive_feedback_summary = feedback_summaries["positive_summary"]
    improvement_feedback_summary = feedback_summaries["improvement_summary"]

    # Check if existing summaries are empty to determine if OpenAI functions should run
    should_generate_feedback = not positive_feedback_summary or not improvement_feedback_summary

    # Display "Update Dashboard" button at the top left
    col1, _ = st.columns([1, 9])
    with col1:
        if st.button("Update Dashboard") or should_generate_feedback:
            with st.spinner("Updating dashboard..."):
                # Combine English and Spanish feedback data
                feedback_df = pd.concat([dataframes[1], dataframes[2]], ignore_index=True)

                # Extract feedback lists by indices
                feedback_dict = data_cleaning.get_feedback_lists_by_indices(
                    feedback_df, positive_feedback_index=23, improvement_feedback_index=24
                )

                # Generate summaries with OpenAI functions
                positive_feedback_summary = openai_functions.summarize_positive_feedback(feedback_dict["positive_feedback"])
                improvement_feedback_summary = openai_functions.summarize_improvement_feedback(
                    feedback_dict["improvement_feedback"]
                )

                # Send new summaries to Google Sheets
                google_services.send_feedback_to_google_sheet(positive_feedback_summary, improvement_feedback_summary)
                st.success("Dashboard updated successfully with feedback summaries!")

                # Update last update date
                last_update_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Display last update date
    st.write(f"**Last updated:** {last_update_date}")

    # Apply custom container styles
    st.markdown(set_container_style(), unsafe_allow_html=True)

    # Combine English and Spanish data for displaying dimensions and scores
    feedback_df = pd.concat([dataframes[1], dataframes[2]], ignore_index=True)

    # Encode responses and select numeric columns
    feedback_encoded = feedback_df.replace(response_encoding).apply(pd.to_numeric, errors='coerce')

    # Calculate mean for each dimension using question indices
    dimension_means = {}
    for dimension, details in dimensions.items():
        indices = details["indices"]
        questions = feedback_encoded.iloc[:, indices]
        dimension_means[dimension] = questions.mean(axis=1).mean()

    # Sort dimensions by score in descending order
    sorted_dimensions = sorted(dimension_means.items(), key=lambda x: x[1], reverse=True)

    # Calculate combined satisfaction score
    satisfaction_scores = feedback_encoded.iloc[:, satisfaction_indices]
    satisfaction_scores.iloc[:, 1] = satisfaction_scores.iloc[:, 1] / 2  # Normalize 10-point scale to 5-point scale
    combined_satisfaction_mean = satisfaction_scores.mean(axis=1).mean()

    # Display title for the End of Year Feedback Analysis Dashboard
    st.markdown("<h1 style='color: #6BD0C3;'>EDMO End of Year Feedback Analysis Dashboard</h1>", unsafe_allow_html=True)

    # Section for Dimensions with Questions and Scores
    st.markdown("<div class='section-title'>Dimensions and Questions</div>", unsafe_allow_html=True)
    for dimension, mean_score in sorted_dimensions:
        details = dimensions[dimension]
        summary = details["summary"]
        questions_html = "".join([f"<li>{q}</li>" for q in details["questions"]])

        container_html = f"""
        <div class="container">
            <div class="location-title">{dimension} <span class="rating">(Score: {mean_score:.2f})</span></div>
            <div class="sentiment">{summary}</div>
            <ul>{questions_html}</ul>
        </div>
        """
        st.markdown(container_html, unsafe_allow_html=True)

    # Section for Combined Satisfaction Score
    st.markdown("<div class='section-title'>Combined Satisfaction Score</div>", unsafe_allow_html=True)
    container_html = f"""
    <div class="container">
        <div class="location-title">Overall Satisfaction <span class="rating">(Score: {combined_satisfaction_mean:.2f})</span></div>
        <div class="sentiment">Measures general satisfaction with EDMO and likelihood of recommending it to others.</div>
    </div>
    """
    st.markdown(container_html, unsafe_allow_html=True)

    # Display the "Feedback & Recommendations" section with summaries
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

def set_container_style():
    """
    Sets custom style for containers with teal and golden yellow accents.
    Returns the CSS as a string.
    """
    container_style = """
        <style>
            .container {
                background-color: #F9F9F9;
                padding: 20px;
                margin: 10px 0;
                border-radius: 8px;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
                border-left: 5px solid #CB3A5F;
            }
            .section-title {
                background-color: #F5C042;
                padding: 10px 20px;
                margin: 20px 0;
                border-radius: 8px;
                font-size: 1.6em;
                font-weight: bold;
                color: #FFFFFF;
                text-align: center;
                box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            }
            .location-title {
                font-size: 1.2em;
                font-weight: bold;
                color: #F5C042;
            }
            .rating {
                font-size: 1.0em;
                color: #6BD0C3;
                font-weight: bold;
            }
            .sentiment {
                font-size: 0.9em;
                color: #555555;
                margin-bottom: 10px;
            }
            ul {
                margin: 0;
                padding-left: 20px;
                color: #555555;
            }
            ul li {
                font-size: 0.85em;
            }
            h3, h2 {
                color: #03045A;
                font-size: 1.6em;
                font-weight: bold;
                margin-top: 15px;
            }
        </style>
    """
    return container_style


if __name__ == '__main__':
    main()
