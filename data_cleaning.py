import pandas as pd
from collections import defaultdict


# Function to clean and prepare data
def clean_data(df):
    """
    Cleans the initial DataFrame by selecting relevant columns, renaming them,
    handling missing values, and converting specific columns to numeric.

    Parameters:
    - init_mid (DataFrame): The initial DataFrame containing survey data.

    Returns:
    - DataFrame: A cleaned DataFrame with necessary columns processed.
    """
    # Select necessary columns and rename them
    cleaned_mid = df.iloc[:, 4:8]
    cleaned_mid.columns = ['Location', 'Kid Camp Experience Rating', 'Recommendation Likelihood', 'Additional Comments']

    # Replace empty or NaN values in the "Location" column with "No Location Specified"
    cleaned_mid["Location"] = cleaned_mid["Location"].replace('', pd.NA).fillna("No Location")

    # Convert 'Kid Camp Experience Rating' and 'Recommendation Likelihood' to numeric, handling non-numeric values
    cleaned_mid['Kid Camp Experience Rating'] = pd.to_numeric(cleaned_mid['Kid Camp Experience Rating'],
                                                              errors='coerce')
    cleaned_mid['Recommendation Likelihood'] = pd.to_numeric(cleaned_mid['Recommendation Likelihood'], errors='coerce')

    return cleaned_mid


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

