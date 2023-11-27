import requests
from alpha_vantage.fundamentaldata import FundamentalData
import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px

st.title("STOCK DASHBOARD")
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start Date')
end_date = st.sidebar.date_input('End Date')

data = yf.download(ticker, start=start_date, end=end_date)
fig = px.line(data, x=data.index, y=data['Adj Close'], title=ticker)
st.plotly_chart(fig)

pricing_data, fundamental_data, news, company_data = st.tabs(
    ["Pricing Data", "Fundamental Data", "Top 10 News", "Company Data"])


with pricing_data:
    st.header('Price Movements')
    data2 = data
    data2['% Change'] = data['Adj Close']/data['Adj Close'].shift(1)-1
    data2.dropna(inplace=True)
    st.write(data2)
    annual_return = data2['% Change'].mean()*252*100
    st.write('Annual Return is ', annual_return, '%')
    stdev = np.std(data2['% Change'])*np.sqrt(252)
    st.write('Standard Deviation is ', stdev*100, '%')
    st.write('Risk Adj. Return is', annual_return/(stdev*100))

with company_data:
    st.header('Company Data from CSV')
    try:
        csv_data = pd.read_csv('list.csv')
        st.write(csv_data)
    except FileNotFoundError:
        st.write('CSV file not found.')
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

with news:
    st.header(f'News from News API')

    api_key = "2add6454cc4b437faa0119d10ae90237"
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "in",
        "category": "business",
        "apiKey": api_key,
        "pageSize": 10  # Set the number of articles to fetch
    }
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            articles = response.json()["articles"]
            if articles:
                for i, article in enumerate(articles):
                    st.subheader(f'News {i+1}')
                    st.image(article['urlToImage'], caption=article['title'], width=200, use_column_width=True)
                    st.write(article['publishedAt'])
                    st.write(article['title'])
                    st.write(article['description'])
                    if st.button(f"Read More {i+1}"):
                        st.markdown(f"[Redirecting to: {article['url']}]({article['url']})")
            else:
                st.write("No news available for the specified criteria.")
        else:
            st.write("Failed to fetch news. Please try again later.")
    except Exception as e:
        st.error(f"An error occurred while fetching news: {str(e)}")

with fundamental_data:
    key = 'W4L3FFHUZ0ZUTTAX'
    fd = FundamentalData(key, output_format='pandas')
    st.subheader('Balance Sheet')
    balance_sheet = fd.get_balance_sheet_annual(ticker)[0]
    bs = balance_sheet.T[2:]
    bs.columns = list(balance_sheet.T.iloc[0])
    st.write(bs)
    st.subheader('Income Statement')
    income_statement = fd.get_income_statement_annual(ticker)[0]
    is1 = income_statement.T[2:]
    is1.columns = list(income_statement.T.iloc[0])
    st.write(is1)
    st.subheader('Cash Flow Statement')
    cash_flow = fd.get_cash_flow_annual(ticker)[0]
    cf = cash_flow.T[2:]
    cf.columns = list(cash_flow.T.iloc[0])
    st.write(cf)



