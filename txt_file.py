import requests
import json
import streamlit as st
import matplotlib.pyplot as plt

# Set your Azure Language resource details
endpoint = "https://language-health-ai.cognitiveservices.azure.com/"  # Replace with your endpoint
key = "4G5RSjcltxYodAo2RmqG7kCuO3AvUh5o2wOaT2YTMwggSNY2c2wtJQQJ99BDACYeBjFXJ3w3AAAaACOGmUcR"  # Replace with your subscription key

# Inject custom CSS for background colors
st.markdown("""
    <style>
        /* Main screen background color */
        .css-18e3th9 {
            background-color: #f4f7fc !important;  /* Light Blue */
        }
        
        /* Sidebar background color */
        .css-1d391kg {
            background-color: #2a3c54 !important;  /* Dark Blue */
            color: white !important;
        }

        /* Button background color */
        .stButton button {
            background-color: #4CAF50 !important;
            color: white !important;
        }

        /* Text area background color */
        .stTextArea textarea {
            background-color: #f1f1f1 !important;
        }

        /* Heading styles */
        .css-1v3fvcr {
            color: #333 !important;
        }

        /* Footer background color (if needed) */
        .css-1d391kg footer {
            background-color: #2a3c54 !important;
        }
    </style>
""", unsafe_allow_html=True)
# Sample text (can be replaced by Streamlit input)
st.title("Sentiment Analysis")
text_input = st.text_area("Enter text:", "I love using Azure AI!", height=200, help="Type a sentence to analyze its sentiment.")

# Sidebar Instructions
st.sidebar.title("Sentiment Analysis Tool")
st.sidebar.markdown("""
    **How to use**: 
    1. Enter any text you want to analyze.
    2. Press "Analyze Sentiment" to get the sentiment analysis result.
    3. View the result below along with a confidence score breakdown.
    4. Use the "Clear Text" button to reset.
""")

if st.button("Analyze Sentiment"):
    with st.spinner('Analyzing...'):
        headers = {
            "Ocp-Apim-Subscription-Key": key,
            "Content-Type": "application/json"
        }

        body = {
            "documents": [
                {
                    "language": "en",
                    "id": "1",
                    "text": text_input
                }
            ]
        }

        url = endpoint + "text/analytics/v3.1/sentiment"
        response = requests.post(url, headers=headers, json=body)
        result = response.json()

    if "documents" in result:
        sentiment = result["documents"][0]["sentiment"]
        confidence_scores = result['documents'][0]['confidenceScores']
        
        st.markdown("### Sentiment Analysis Result")
        st.markdown(f"**Sentiment**: {sentiment}")
        st.markdown(f"**Confidence Scores**:")
        st.markdown(f" - **Positive**: {confidence_scores['positive']:.2f}")
        st.markdown(f" - **Neutral**: {confidence_scores['neutral']:.2f}")
        st.markdown(f" - **Negative**: {confidence_scores['negative']:.2f}")

        # Display bar chart
        st.subheader("Confidence Scores Chart")
        fig, ax = plt.subplots()
        ax.bar(['Positive', 'Neutral', 'Negative'], 
               [confidence_scores['positive'], confidence_scores['neutral'], confidence_scores['negative']],
               color=['green', 'blue', 'red'])
        ax.set_ylabel("Confidence")
        ax.set_title("Sentiment Confidence Scores")
        st.pyplot(fig)
    else:
        st.error("Error analyzing the text.")

    # Clear text button
    if st.button("Clear Text"):
        text_input = ""  # Reset the text area
        st.text_area("Enter text:", value=text_input)
