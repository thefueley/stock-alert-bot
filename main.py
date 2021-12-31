import os
import requests
from twilio.rest import Client

STOCK = "HCP"
COMPANY_NAME = "Hashicorp"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
STOCK_API_KEY = os.environ['STOCK_API_KEY']
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = os.environ['NEWS_API_KEY']

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_service_num = os.environ['TWILIO_PHONE']
twilio_subscriber = os.environ['TWILIO_SUBSCRIBER']

# Alpha Vantage API
stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": STOCK_API_KEY
}

response = requests.get(STOCK_ENDPOINT, params=stock_params)
data = response.json()['Time Series (Daily)']

# Get yesterday's closing price, or today's if after market closes
data_list = [value for (key, value) in data.items()]
ultimate_closing_price = data_list[0]["4. close"]

# get the day-before-yesterday's closing price
penultimate_closing_price = data_list[1]["4. close"]

# closing price diff
difference = abs(float(ultimate_closing_price) -  float(penultimate_closing_price))
up_down = None
if difference > 0:
    up_down = "🔺"
else:
    up_down = "🔻"

# find % diff
diff_percent = round((difference / float(ultimate_closing_price)) * 100)

if abs(diff_percent) > 5:
    # news API
    news_params = {
        "apiKey": NEWS_API_KEY,
        "qInTitle": COMPANY_NAME,
    }

    news_response = requests.get(NEWS_ENDPOINT, params=news_params)
    articles = news_response.json()["articles"]
    
    # print first three news articles
    three_articles = articles[:3]
    
    # format articles
    formatted_articles = [f"{STOCK}: {up_down}{diff_percent}%\nHeadline: {article['title']}. \nBrief: {article['description']}" for article in three_articles]

    # send sms
    client = Client(account_sid, auth_token)

    for article in formatted_articles:
        message = client.messages.create(
            body = article,
            from_ = twilio_service_num,
            to = twilio_subscriber
        )
        print(message.status)
