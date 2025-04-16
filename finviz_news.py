# -*- coding: utf-8 -*-
"""finviz_news.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1DYCijzxKXIvFP3Zwx72cS1sdTA2lOSEe
"""

pip install openai

import streamlit as st
import requests
import csv
import openai
import os
from openai import OpenAI

# Fetch latest stock news and save to CSV
def fetch_stock_news():
    URL = "https://elite.finviz.com/news_export.ashx?v=3&auth=2ab1c101-1f70-4086-b4bd-37d237a73406"
    response = requests.get(URL)
    if response.status_code == 200:
        with open("export.csv", "wb") as file:
            file.write(response.content)
        return "✅ News data successfully saved to export.csv"
    else:
        return "❌ Failed to fetch news data."

# Analyze a single news article with OpenAI
def analyze_news_article(title, stock, api_key):
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a financial analyst."},
            {"role": "user", "content": f"Analyze the article titled: '{title}'. Give a clear, concise dashboard recommendation for {stock} on whether to buy, sell, or hold."}
        ]
    )

    return response.choices[0].message.content.strip()

# Process all news data and return analysis
def process_news_data(api_key):
    recommendations = []
    try:
        with open("export.csv", "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                title = row[0]
                stock = row[1]
                recommendation = analyze_news_article(title, stock, api_key)
                recommendations.append((title, stock, recommendation))
        return recommendations
    except FileNotFoundError:
        st.error("⚠️ export.csv not found. Please fetch stock news first.")
        return []

# ---------------------- Streamlit UI ----------------------

st.set_page_config(page_title="Stock News Dashboard", layout="wide")
st.title("📈 AI-Powered Stock News Dashboard")

api_key = st.text_input("🔑 Enter your OpenAI API Key", type="password")

if api_key:
    col1, col2 = st.columns([1, 2])

    with col1:
        if st.button("📥 Fetch Latest News"):
            result = fetch_stock_news()
            st.success(result)

        if st.button("📊 Generate Recommendations"):
            st.info("Analyzing news with GPT-4o... Please wait.")
            recommendations = process_news_data(api_key)

            if recommendations:
                with col2:
                    for title, stock, recommendation in recommendations:
                        with st.expander(f"{stock} - {title}"):
                            st.markdown(f"**Recommendation:**\n{recommendation}")
else:
    st.warning("🔐 Please enter your OpenAI API key to proceed.")
