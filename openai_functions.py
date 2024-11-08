import streamlit as st
from openai import OpenAI


def analyze_comment(dic_comments):
    """
    Analyzes customer feedback for each location in the dictionary, providing
    sentiment analysis, overall feedback, and summarized recommendations if they exist.

    Parameters:
    - dic_comments (dict): Dictionary where keys are locations and values are lists of comments.

    Returns:
    - dict: A dictionary with each location as the key, and analysis as the value.
    """
    # Initialize OpenAI client with API key
    client = OpenAI(api_key=st.secrets["openai"]['openai_key'])
    analysis_dict = {}  # Dictionary to store analysis for each location

    for location, comments in dic_comments.items():
        # Join comments for the location into a single string for context
        comments_text = " ".join([comment for comment in comments if comment])

        try:
            # Use the OpenAI Chat API to analyze comments for each location with few-shot examples
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system",
                     "content": "You are an assistant that analyzes customer feedback and provides sentiment analysis and recommendations."},

                    # Few-shot example with feedback
                    {"role": "user",
                     "content": "Analyze the feedback for the location 'Sample Location A'. Provide the overall sentiment in a few sentences and summarize any customer recommendations if they are relevant: ['Pick up process needs to be improved.', 'More activities for kids.', 'Kids were bored.']"},
                    {"role": "assistant", "content": """
The overall sentiment for 'Sample Location A' is mixed. While there is appreciation for the existing program, there are concerns about the pick-up process and the level of engagement for children. Parents noted that children were sometimes bored and recommended having a more structured schedule with varied activities.

### Recommendations:
1. **Improve Pick-Up Process**: Streamline the pick-up process to reduce waiting times for parents.
2. **Increase Engagement Activities**: Add more structured activities to keep children engaged and prevent boredom.
                    """},

                    # Few-shot example with no comments
                    {"role": "user",
                     "content": "Analyze the feedback for the location 'Sample Location B'. Provide the overall sentiment in a few sentences and summarize any customer recommendations if they are relevant: []"},
                    {"role": "assistant", "content": """
There is no customer feedback available for 'Sample Location B' at this time.
                    """},

                    # Actual prompt for the current location
                    {"role": "user",
                     "content": f"Analyze the feedback for the location '{location}'. Provide the overall sentiment in a few sentences and summarize any customer recommendations if they are relevant: {comments_text or '[]'}"}
                ]
            )

            # Extract and clean the response content
            analysis = response.choices[0].message.content.strip()
            # Store the analysis in the dictionary with location as key
            analysis_dict[location] = analysis

        except Exception as e:
            print(f"Error in API call for location '{location}': {e}")
            analysis_dict[location] = "Error analyzing feedback."

    return analysis_dict
