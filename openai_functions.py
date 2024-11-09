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


from openai import OpenAI
import streamlit as st


def summarize_positive_feedback(feedback_list):
    """
    Summarizes positive feedback comments using OpenAI Chat API.

    Parameters:
    - feedback_list (list): List of positive feedback comments.

    Returns:
    - str: A summary of positive feedback.
    """
    # Initialize OpenAI client with API key
    client = OpenAI(api_key=st.secrets["openai"]['openai_key'])

    # Join comments into a single string for context
    comments_text = " ".join([comment for comment in feedback_list if comment])

    try:
        # Use the OpenAI Chat API to summarize positive feedback
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "You are an assistant that summarizes positive aspects of feedback from customers."},

                # Few-shot example with feedback
                {"role": "user",
                 "content": "Summarize the positive feedback about EDMO based on these comments: ['The staff is amazing.', 'My child loves the activities.', 'Great overall experience.']"},
                {"role": "assistant", "content": """
Parents appreciate the positive environment and the engaging activities at EDMO. Many noted that the staff is friendly and helpful, and children enjoy attending the program. Overall, the feedback highlights a strong sense of satisfaction with the program.
                """},

                # Few-shot example with no comments
                {"role": "user",
                 "content": "Summarize the positive feedback about EDMO based on these comments: []"},
                {"role": "assistant", "content": """
There is no positive feedback available at this time.
                """},

                # Actual prompt for the current list of positive feedback
                {"role": "user",
                 "content": f"Summarize the positive feedback about EDMO based on these comments: {comments_text or '[]'}"}
            ]
        )

        # Extract and clean the response content
        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"Error in API call for positive feedback: {e}")
        return "Error generating summary for positive feedback."


def summarize_improvement_feedback(feedback_list):
    """
    Summarizes improvement feedback comments using OpenAI Chat API.

    Parameters:
    - feedback_list (list): List of feedback comments about areas for improvement.

    Returns:
    - str: A summary of improvement feedback.
    """
    # Initialize OpenAI client with API key
    client = OpenAI(api_key=st.secrets["openai"]['openai_key'])

    # Join comments into a single string for context
    comments_text = " ".join([comment for comment in feedback_list if comment])

    try:
        # Use the OpenAI Chat API to summarize improvement feedback
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system",
                 "content": "You are an assistant that summarizes areas for improvement based on customer feedback."},

                # Few-shot example with feedback
                {"role": "user",
                 "content": "Summarize the areas for improvement in EDMO based on these comments: ['The pick-up process could be smoother.', 'More structured activities for kids.', 'Kids sometimes seemed bored.']"},
                {"role": "assistant", "content": """
Areas for improvement include refining the pick-up process to make it more efficient, adding more structured activities to maintain engagement, and addressing occasional boredom reported by children. These changes could enhance the overall experience.
                """},

                # Few-shot example with no comments
                {"role": "user",
                 "content": "Summarize the areas for improvement in EDMO based on these comments: []"},
                {"role": "assistant", "content": """
There are no specific areas for improvement mentioned at this time.
                """},

                # Actual prompt for the current list of improvement feedback
                {"role": "user",
                 "content": f"Summarize the areas for improvement in EDMO based on these comments: {comments_text or '[]'}"}
            ]
        )

        # Extract and clean the response content
        summary = response.choices[0].message.content.strip()
        return summary

    except Exception as e:
        print(f"Error in API call for improvement feedback: {e}")
        return "Error generating summary for improvement feedback."
