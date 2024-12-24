import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import ollama
import tempfile
import base64
import os

# Set up Streamlit app
st.set_page_config(layout="wide")
st.title("Stock-I 📈")  # Title with stock chart emoji

# Initialize session state variables to manage description visibility
if "description_hidden" not in st.session_state:
    st.session_state["description_hidden"] = False

# Sidebar configuration
st.sidebar.header("🔧 Configuration 🛠️")

# Section for Single Stock Insights
st.sidebar.subheader("📈 Single Stock Insights")
ticker = st.sidebar.text_input("🗂️ Enter Stock Ticker (e.g., RELIANCE.NS):", "RELIANCE.NS")
start_date = st.sidebar.date_input("📅 Start Date", value=pd.to_datetime("2024-10-23"))
end_date = st.sidebar.date_input("📅 End Date", value=pd.to_datetime("2024-12-23"))

# Button for Fetching Data (placed after End Date option)
fetch_data_button = st.sidebar.button("🔍 Fetch Data")

# Section for Favorites List
st.sidebar.header("Favorites List")
favorite_stocks = st.sidebar.multiselect("Add Stocks to view Insights together",
                                         ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"],
                                         default=["RELIANCE.NS"])

# Button for Viewing Favorites Insights (placed after Add Stocks to Favorites option)
view_favorites_button = st.sidebar.button("📚 View Favorites Insights")

# If either button is pressed, hide the description
if fetch_data_button or view_favorites_button:
    st.session_state["description_hidden"] = True  # Hide the description

# Display app description if not hidden
if not st.session_state["description_hidden"]:
    st.markdown(
        """
        ## Welcome to Stock-I! 🚀
        Stock-I is a stock analysis tool that helps you track and analyze stock prices. With this, you can:
        - 📈 View detailed insights of a single stock by entering the stock ticker and selecting a date range.
        - 🌟 Add multiple stocks to your favorites list and view their insights in one place.
        - 📊 Analyze stock price movements with various technical indicators like Moving Averages, Bollinger Bands, and VWAP.
        - 🤖 Get AI-powered recommendations based on technical analysis to help guide your stock decisions.

        ### How to use:
        1. 🏷️ Enter a stock ticker (e.g., `RELIANCE.NS`)
        2. 📅 Choose the start and end dates for the stock analysis.
        3. 🔍 Click **Fetch Data** to view detailed stock insights.
        4. Alternatively, you can add multiple stocks to your **Favorites List** and view their insights collectively.

        **Stock Ticker Suffixes Guide**:
        - `.NS` for Indian stocks listed on the National Stock Exchange (e.g., `RELIANCE.NS`).
        - `.AX` for stocks listed on the Australian Securities Exchange (e.g., `BHP.AX`).
        - No suffix is required for US stocks (e.g., `AAPL`, `TSLA`).
        """
    )

# Fetch stock data when the button is clicked
if fetch_data_button:
    data = yf.download(ticker, start=start_date, end=end_date)
    data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
    stock_name = ticker.split(".")[0]
    start_price = data['Close'].iloc[0]
    end_price = data['Close'].iloc[-1]
    price_change = ((end_price - start_price) / start_price) * 100
    summary_data = {
        "Stock": [stock_name],
        "Start Date": [start_date],
        "Start Price": [start_price],
        "End Date": [end_date],
        "End Price": [end_price],
        "Percentage Change (%)": [round(price_change, 2)]
    }
    summary_df = pd.DataFrame(summary_data)
    summary_df = summary_df.loc[:, summary_df.columns.notna()]
    st.subheader(f" {stock_name} Insights ")
    st.dataframe(summary_df)

    required_columns = ['Open', 'High', 'Low', 'Close']
    if all(col in data.columns for col in required_columns):
        fig = go.Figure(data=[
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Candlestick"
            )
        ])
        st.plotly_chart(fig)
        st.subheader(" AI-Powered Analysis 🤖")
        if st.button("Run AI Analysis"):
            with st.spinner("🔄 Analyzing the chart, please wait..."):
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
                    fig.write_image(tmpfile.name)
                    tmpfile_path = tmpfile.name
                with open(tmpfile_path, "rb") as image_file:
                    image_data = base64.b64encode(image_file.read()).decode('utf-8')
                messages = [{
                    'role': 'user',
                    'content': """You are a Stock Trader specializing in Technical Analysis at a top financial institution.
                                Analyze the stock chart's technical indicators and provide a buy/hold/sell recommendation.
                                Base your recommendation only on the candlestick chart and the displayed technical indicators.
                                First, provide the recommendation, then, provide your detailed reasoning."""
                }]
                response = ollama.chat(model='llama3.2-vision', messages=messages)
                st.write("**AI Analysis Results:**")
                st.write(response["message"]["content"])
                os.remove(tmpfile_path)
    else:
        st.error(" Missing one or more of the essential columns.")

# If "View Favorites Insights" is clicked
if view_favorites_button:
    for stock_ticker in favorite_stocks:
        data = yf.download(stock_ticker, start=start_date, end=end_date)
        data.columns = [col[0] if isinstance(col, tuple) else col for col in data.columns]
        stock_name = stock_ticker.split(".")[0]
        start_price = data['Close'].iloc[0]
        end_price = data['Close'].iloc[-1]
        price_change = ((end_price - start_price) / start_price) * 100
        summary_data = {
            "Stock": [stock_name],
            "Start Date": [start_date],
            "Start Price": [start_price],
            "End Date": [end_date],
            "End Price": [end_price],
            "Percentage Change (%)": [round(price_change, 2)]
        }
        summary_df = pd.DataFrame(summary_data)
        summary_df = summary_df.loc[:, summary_df.columns.notna()]
        st.subheader(f" {stock_name} Insights ")
        st.dataframe(summary_df)
