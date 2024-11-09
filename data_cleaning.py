import pandas as pd
from collections import defaultdict
import streamlit as st
import google_services

# Function to clean and prepare data
def clean_data_midyear_endofession(df):
    """
    Cleans the initial DataFrame by selecting relevant columns, renaming them,
    handling missing values, and converting specific columns to numeric.

    Parameters:
    - init_mid (DataFrame): The initial DataFrame containing survey data.

    Returns:
    - DataFrame: A cleaned DataFrame with necessary columns processed.
    """
    # Select necessary columns and rename them
    cleaned_df = df.iloc[:, 4:8]
    cleaned_df.columns = ['Location', 'Kid Camp Experience Rating', 'Recommendation Likelihood', 'Additional Comments']

    # Replace empty or NaN values in the "Location" column with "No Location Specified"
    cleaned_df["Location"] = cleaned_df["Location"].replace('', pd.NA).fillna("No Location")

    # Convert 'Kid Camp Experience Rating' and 'Recommendation Likelihood' to numeric, handling non-numeric values
    cleaned_df['Kid Camp Experience Rating'] = pd.to_numeric(cleaned_df['Kid Camp Experience Rating'],
                                                              errors='coerce')
    cleaned_df['Recommendation Likelihood'] = pd.to_numeric(cleaned_df['Recommendation Likelihood'], errors='coerce')

    return cleaned_df






# Function to group data and calculate mean values
def create_grouped_df(cleaned_mid):
    """
    Groups the cleaned DataFrame by 'Location' and calculates the mean ratings
    for 'Kid Camp Experience Rating' and 'Recommendation Likelihood'.

    Parameters:
    - cleaned_mid (DataFrame): The cleaned DataFrame with relevant columns.

    Returns:
    - DataFrame: A DataFrame with 'Location', mean ratings per Location, combined mean, and sorted by combined mean.
    """
    # Calculate the mean of 'Kid Camp Experience Rating' and 'Recommendation Likelihood' per location
    grouped_df = cleaned_mid.groupby('Location', as_index=False)[
        ['Kid Camp Experience Rating', 'Recommendation Likelihood']
    ].mean().round(2)

    # Calculate the combined mean of both columns per Location
    grouped_df['Combined Mean'] = grouped_df[['Kid Camp Experience Rating', 'Recommendation Likelihood']].mean(axis=1).round(2)

    # Sort the DataFrame by Combined Mean in descending order (best to worst)
    grouped_df = grouped_df.sort_values(by='Combined Mean', ascending=False)

    return grouped_df


# Function to create a dictionary of comments per location
def create_comments_dict(cleaned_mid):
    """
    Creates a dictionary to store comments for each location, ensuring each key holds a list of comments.

    Parameters:
    - cleaned_mid (DataFrame): The cleaned DataFrame with relevant columns.

    Returns:
    - dict: A dictionary where each key is a location, and each value is a list of comments.
    """
    # Initialize the dictionary to store comments per location
    dic_comments_mid = defaultdict(list)

    # Collect comments per location
    for location, comment in cleaned_mid[['Location', 'Additional Comments']].itertuples(index=False):
        if pd.notna(comment):  # Check if comment is not NaN
            dic_comments_mid[location].append(comment)

    return dic_comments_mid

def load_and_prepare_data(worksheet_name, sheet_name="edmo_dashboard"):
    """
    Load, clean, and process data for the selected worksheet.
    """
    # Load all dataframes
    dataframes = google_services.load_google_sheets_data(sheet_name)
    df_midyear, df_endofyear_eng, df_endofyear_spa, df_endofsession, feedback_midyear, feedback_endofyear, feedback_endofsession = dataframes

    # Select the appropriate feedback and cleaning based on the worksheet selected
    if worksheet_name == "feedback_midyear":
        cleaned_df = clean_data_midyear_endofession(df_midyear)
        df_combined_mean = create_grouped_df(cleaned_df)
        dic_comments = create_comments_dict(cleaned_df)
        feedback = feedback_midyear
    elif worksheet_name == "feedback_endofsession":
        cleaned_df = clean_data_midyear_endofession(df_endofsession)
        df_combined_mean = create_grouped_df(cleaned_df)
        dic_comments = create_comments_dict(cleaned_df)
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




def process_end_of_year_data():
    """
    Unique processing logic for End of Year feedback data.
    """
    # Load data specific to End of Year (you can customize this to load specific data for end of year)
    dataframes = google_services.load_google_sheets_data("edmo_dashboard")
    df_endofyear_eng, df_endofyear_spa, feedback_endofyear = dataframes[1:4]

    # Combine English and Spanish end-of-year data
    combined_df = pd.concat([df_endofyear_eng, df_endofyear_spa], ignore_index=True)

    # Perform any specific cleaning and processing
    cleaned_df = clean_data_endofyear(combined_df)
    df_combined_mean = create_grouped_df(cleaned_df)
    dic_comments = create_comments_dict(cleaned_df)

    feedback = feedback_endofyear

    return feedback, df_combined_mean, dic_comments
