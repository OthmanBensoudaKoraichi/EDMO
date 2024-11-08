import streamlit as st
import base64
import streamlit as st

def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/jpeg;base64,{encoded_string}"


import streamlit as st
import base64


def get_image_base64(image_path):
    """
    Convert an image file to base64 format.
    """
    with open(image_path, "rb") as image_file:
        base64_bytes = base64.b64encode(image_file.read())
        base64_string = base64_bytes.decode("utf-8")
    return base64_string


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
