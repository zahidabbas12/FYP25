# performance_analytics/utils.py
from textblob import TextBlob  # You can also use other libraries for sentiment analysis

# Function to analyze sentiment and return a polarity score
def analyze_sentiment(feedback_content):
    blob = TextBlob(feedback_content)
    return blob.sentiment.polarity  # Returns sentiment score (-1 to 1)