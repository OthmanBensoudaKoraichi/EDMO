import streamlit as st
import requests
import base64
import pandas as pd

def get_image_base64(image_path):
    if image_path.startswith(('http://', 'https://')):
        # For URLs: download the image first
        response = requests.get(image_path)
        response.raise_for_status()  # Raise an exception for bad status codes
        image_content = response.content
    else:
        # For local files: read directly
        with open(image_path, "rb") as image_file:
            image_content = image_file.read()

    return base64.b64encode(image_content).decode()



def set_bg_image(image_path, opacity=0.9, deploy=False):
    """
    Set a background image for the Streamlit app with optional opacity overlay.

    Parameters:
    - image_path (str): Path to the image file.
    - opacity (float): Opacity level for the white overlay on the background (0 to 1).
    - deploy (bool): Set to True when deploying the app to use direct URL for the image.
    """
    if not deploy:
        # Convert the image to base64 for local deployment
        base64_image = get_image_base64(image_path)
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255, 255, 255, {opacity}), rgba(255, 255, 255, {opacity})), 
                url("data:image/png;base64,{base64_image}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Use the direct URL of the image for deployment
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: linear-gradient(rgba(255, 255, 255, {opacity}), rgba(255, 255, 255, {opacity})), 
                url("{image_path}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
            }}
            </style>
            """,
            unsafe_allow_html=True,
        )
def set_button_style():
    """
    Sets custom style for Streamlit buttons with a pinkish-red theme.
    Returns the CSS as a string.
    """
    button_style = """
        <style>
            .stButton > button {
                background-color: #CB3A5F;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
            }
            .stButton > button:hover {
                background-color: #A32E4B;
            }
        </style>
    """
    return button_style

def set_container_style_midyear_endofsession():
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
            .location-title {
                font-size: 1.7em;
                font-weight: bold;
                color: #F5C042;
            }
            .rating {
                font-size: 1.2em;
                color: #6BD0C3;
                font-weight: bold;
            }
            .sentiment {
                font-size: 1em;
                color: #555555;
            }
            h3 {
                color: #03045A;
                font-size: 1.6em;
                font-weight: bold;
                margin-top: 15px;
            }
        </style>
    """
    return container_style

def set_container_style_endofyear():
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

def configure_page_style_endofyear():
    """Configures the style settings for the Streamlit page."""
    pd.set_option('future.no_silent_downcasting', True)
    set_bg_image(
        image_path="https://raw.githubusercontent.com/OthmanBensoudaKoraichi/EDMO/refs/heads/main/images/colorkit.png",
        opacity=0.3
    )
    st.markdown(set_button_style(), unsafe_allow_html=True)
    st.markdown(set_container_style_endofyear(), unsafe_allow_html=True)


def display_dimensions_scores_endofyear(feedback_df, dimensions, response_encoding, satisfaction_indices):
    """Displays the dimensions, questions, and scores based on user feedback data."""
    feedback_encoded = feedback_df.replace(response_encoding).apply(pd.to_numeric, errors='coerce')

    dimension_means = {
        dimension: feedback_encoded.iloc[:, details["indices"]].mean(axis=1).mean()
        for dimension, details in dimensions.items()
    }

    sorted_dimensions = sorted(dimension_means.items(), key=lambda x: x[1], reverse=True)
    satisfaction_scores = feedback_encoded.iloc[:, satisfaction_indices]
    satisfaction_scores.iloc[:, 1] = satisfaction_scores.iloc[:, 1] / 2  # Normalize 10-point scale
    combined_satisfaction_mean = satisfaction_scores.mean(axis=1).mean()

    # Display each dimension's score
    st.markdown("<div class='section-title'>Dimensions and Questions</div>", unsafe_allow_html=True)
    for dimension, mean_score in sorted_dimensions:
        details = dimensions[dimension]
        questions_html = "".join([f"<li>{q}</li>" for q in details["questions"]])

        container_html = f"""
        <div class="container">
            <div class="location-title">{dimension} <span class="rating">(Score: {mean_score:.2f})</span></div>
            <div class="sentiment">{details["summary"]}</div>
            <ul>{questions_html}</ul>
        </div>
        """
        st.markdown(container_html, unsafe_allow_html=True)

    # Display overall satisfaction score
    st.markdown("<div class='section-title'>Combined Satisfaction Score</div>", unsafe_allow_html=True)
    overall_satisfaction_html = f"""
    <div class="container">
        <div class="location-title">Overall Satisfaction <span class="rating">(Score: {combined_satisfaction_mean:.2f})</span></div>
        <div class="sentiment">Measures general satisfaction with EDMO and likelihood of recommending it to others.</div>
    </div>
    """
    st.markdown(overall_satisfaction_html, unsafe_allow_html=True)