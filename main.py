import requests
from twilio.rest import Client
from datetime import datetime, timedelta

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

now = datetime.now().date()
yesterday = (now - timedelta(days=1))
day_before = (now - timedelta(days=2))

# ******************************APIs******************************
# Getting stock info
stock_key = 'key'
stock_url = 'https://www.alphavantage.co/query?'
stock_params = {
    'function': 'TIME_SERIES_DAILY_ADJUSTED',
    'symbol': STOCK,
    'apikey': stock_key,
}
stock_response = requests.get(url=stock_url, params=stock_params)
stock_response.raise_for_status()
stock_data = stock_response.json()

yesterday_close = float(stock_data['Time Series (Daily)'][str(yesterday)]['4. close'])
day_before_close = float(stock_data['Time Series (Daily)'][str(day_before)]['4. close'])

gain_loss = ''
if yesterday_close > day_before_close:
    gain_loss = '🔺'
else:
    gain_loss = '🔻'

# Getting news articles
newsapi_key = 'key'
news_url = 'https://newsapi.org/v2/everything?'
news_params = {
    'q': f'{COMPANY_NAME},{STOCK}',
    'apiKey': newsapi_key,
}
news_response = requests.get(url=news_url, params=news_params)
news_response.raise_for_status()
news_data = news_response.json()
news_articles = news_data['articles'][0:3]
print(len(news_articles))

# Sending SMS messages
twilio_phone_number = '+phonenumber'
twilio_auth_token = 'authtoken'
twilio_account_sid = 'account sid'


# Checking if stock change is +/- 5%
def get_change(current, previous):
    if current == previous:
        return 100.0
    try:
        return (abs(current - previous) / previous) * 100.0
    except ZeroDivisionError:
        return 0


change = get_change(yesterday_close, day_before_close)

if change >= 5:
    # Sending three texts
    for x in range(0, len(news_articles)):
        client = Client(twilio_account_sid, twilio_auth_token)
        message = client.messages \
            .create(
            body=f"{STOCK}: {gain_loss}{change}%\n"
                 f"Headline: {news_articles[x]['title']}\n"
                 f"Brief: {news_articles[x]['description']}\n"
                 f"Read More: {news_articles[x]['url']}",
            from_=twilio_phone_number,
            to='+phonenumber'
        )
        print(message.status)
