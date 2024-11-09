from collections import defaultdict
import pandas as pd
from datetime import datetime
import streamlit as st
from utils import data_cleaning, google_services, openai_functions

def load_feedback_summary_column(dataframe, column_name, default_value=""):
    """
    Loads a summary from a specific column in a DataFrame, defaulting to a value if the column or data is missing.

    Parameters:
    - dataframe (pd.DataFrame): The DataFrame from which to load data.
    - column_name (str): The column name to fetch.
    - default_value (str): Default value if the data is missing.

    Returns:
    - str: The summary or the default value.
    """
    return dataframe.get(column_name, [default_value])[0]

def load_feedback_summaries(dataframe):
    """
    Loads all relevant summaries and dates from the feedback DataFrame.

    Parameters:
    - dataframe (pd.DataFrame): The feedback_endofyear DataFrame.

    Returns:
    - dict: Dictionary with keys 'positive_summary', 'improvement_summary', and 'last_update_date'.
    """
    return {
        "positive_summary": load_feedback_summary_column(dataframe, "Positive Feedback Summary"),
        "improvement_summary": load_feedback_summary_column(dataframe, "Improvement Feedback Summary"),
        "last_update_date": load_feedback_summary_column(dataframe, "Date Sent", "No previous updates")
    }

def create_comments_dict(cleaned_mid):
    """
    Creates a dictionary to store comments for each location.

    Parameters:
    - cleaned_mid (pd.DataFrame): DataFrame with 'Location' and 'Additional Comments' columns.

    Returns:
    - dict: A dictionary where each key is a location, and each value is a list of comments.
    """
    dic_comments_mid = defaultdict(list)
    for location, comment in cleaned_mid[['Location', 'Additional Comments']].itertuples(index=False):
        if pd.notna(comment):
            dic_comments_mid[location].append(comment)
    return dic_comments_mid

def create_grouped_df(cleaned_mid):
    """
    Groups a DataFrame by 'Location' and calculates the mean ratings.

    Parameters:
    - cleaned_mid (pd.DataFrame): DataFrame with relevant columns.

    Returns:
    - pd.DataFrame: Sorted DataFrame by 'Combined Mean'.
    """
    grouped_df = cleaned_mid.groupby('Location', as_index=False)[
        ['Kid Camp Experience Rating', 'Recommendation Likelihood']
    ].mean().round(2)
    grouped_df['Combined Mean'] = grouped_df[['Kid Camp Experience Rating', 'Recommendation Likelihood']].mean(axis=1).round(2)
    return grouped_df.sort_values(by='Combined Mean', ascending=False)

def get_feedback_data():
    """
    Returns dictionaries and indices related to feedback data.

    Returns:
    - tuple: A tuple containing response encoding, dimensions, and satisfaction indices.
    """
    response_encoding = {
        "Strongly Agree": 5,
        "Agree": 4,
        "Not Sure": 3,
        "Disagree": 2,
        "Strongly Disagree": 1
    }
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
        },"Program Satisfaction": {
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

    satisfaction_indices = [21, 22]  # Assuming these are the last two columns
    return response_encoding, dimensions, satisfaction_indices

def get_feedback_lists_by_indices(df, positive_feedback_index, improvement_feedback_index):
    """
    Extracts lists of positive and improvement feedback based on specified column indices.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing feedback data.
    - positive_feedback_index (int): Index or column position for positive feedback.
    - improvement_feedback_index (int): Index or column position for improvement feedback.

    Returns:
    - dict: A dictionary with 'positive_feedback' and 'improvement_feedback' as keys, containing lists of feedback comments.
    """
    # Retrieve positive and improvement feedback lists by column indices
    positive_feedback = df.iloc[:, positive_feedback_index].dropna().tolist()
    improvement_feedback = df.iloc[:, improvement_feedback_index].dropna().tolist()

    return {
        "positive_feedback": positive_feedback,
        "improvement_feedback": improvement_feedback
    }



def update_feedback_summaries_endofyear(dataframes):
    """
    Updates feedback summaries with new OpenAI-generated summaries if necessary.

    Parameters:
    - dataframes (list): List of DataFrames with feedback data.

    Returns:
    - tuple: Updated positive and improvement summaries along with the timestamp.
    """
    feedback_df = pd.concat([dataframes[1], dataframes[2]], ignore_index=True)
    feedback_dict = get_feedback_lists_by_indices(
        feedback_df, positive_feedback_index=23, improvement_feedback_index=24
    )
    positive_summary = openai_functions.summarize_positive_feedback(feedback_dict["positive_feedback"])
    improvement_summary = openai_functions.summarize_improvement_feedback(feedback_dict["improvement_feedback"])

    google_services.send_feedback_to_google_sheet(positive_summary, improvement_summary)
    st.success("Dashboard updated successfully with feedback summaries!")
    return positive_summary, improvement_summary, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
