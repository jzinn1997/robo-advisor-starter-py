from dotenv import load_dotenv
import json
import os
import requests
import csv
import datetime 


load_dotenv() # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable

# see: https://www.alphavantage.co/support/#api-key
api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS! Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."


# adapted from https://github.com/hiepnguyen034/robo-stock/blob/master/robo_advisor.py
while True:
	user_input = input("PLEASE CHOOSE A STOCK NAME TO ANALYZE: ") 
	if not user_input.isalpha():
		print("Please be sure to enter the name of a stock.")
	else:
		data=requests.get('https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+user_input+'&apikey='+api_key)

		if 'Error' in data.text:
			print("Oops! This stock name was not found. Please check your stock name and try again.")
		else:
			break

symbol = user_input #> "MSFT"

request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
response = requests.get(request_url)

parsed_response = json.loads(response.text)

last_refreshed = parsed_response["Meta Data"]["3. Last Refreshed"]

#breakpoint()


# TODO: use the "requests" package to issue a "GET" request to the specified url, and store the JSON response in a variable...

# TODO: further parse the JSON response...

# TODO: traverse the nested response data structure to find the latest closing price and other values of interest...

tsd = parsed_response["Time Series (Daily)"]

dates = list(tsd.keys())
latest_day= dates[0] #assuming that the first day is at the front of the list, consider sorting to ensure this
latest_close = tsd[latest_day]["4. close"]

def to_usd(my_price):
    return "${0:,.2f}".format(my_price)


#maximum of all the high and low prices
high_prices = []
low_prices = []

for date in dates:
    high_price=tsd[date]["2. high"]
    low_price = tsd[date]["3. low"]
    high_prices.append(float(high_price))
    low_prices.append(float(low_price))

recent_high = max(high_prices)
average_of_highs = np.mean(high_prices)
recent_low = min(low_prices)
average_of_lows = np.mean(low_prices)


#
# INFO OUTPUTS
#

# TODO: write response data to a CSV file

#csv_file_path = "data/prices.csv" # a relative filepath
#csv_file_path = os.path.join(os.path.dirname(__file__), "..", "data", "monthly_sales.csv")

csv_file_path = os.path.join(os.path.dirname(__file__), "../data/prices.csv")

csv_headers = ["timestamp", "open", "high", "low", "close", "volume"]

with open(csv_file_path, "w") as csv_file: # "w" means "open the file for writing"
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader() # uses fieldnames set above
    for date in dates:
        daily_prices = tsd[date]
        writer.writerow({
            "timestamp": date,
            "open": daily_prices["1. open"],
            "high": daily_prices["2. high"] ,
            "low": daily_prices["3. low"],
            "close": daily_prices["4. close"],
            "volume": daily_prices["5. volume"]
        })

# TODO: further revise the example outputs below to reflect real information

#from shopping cart project
now = datetime.datetime.strptime(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"),"%Y-%m-%d %H:%M:%S")

print("-----------------")
print("SELECTED STOCK SYMBOL: " + user_input)
print("-----------------")
print("REQUESTING STOCK MARKET DATA...")
print("REQUEST AT: " + (str(now)))  #use datetime module like in previous exercises
print("-----------------")
print(f"LATEST DAY OF AVAILABLE DATA: {last_refreshed}")
print(f"LATEST DAILY CLOSING PRICE: {to_usd(float(latest_close))}")
print(f"RECENT HIGH: {to_usd(float(recent_high))}")
print(f"RECENT LOW: {to_usd(float(recent_low))}")
print("-----------------")
# adapted from https://github.com/hiepnguyen034/robo-stock/blob/master/robo_advisor.py and https://stackoverflow.com/questions/9039961/finding-the-average-of-a-list
if float(latest_close)< float(average_of_highs):
	print ("RECOMMENDATION: BUY! Because...buy low, sell high). The stock's current closing price is less than the avg closing price!")
elif float(latest_close)> float(average_of_highs):
    print("RECOMMENDATION: SELL! (Because...buy low, sell high. The stock's current closing price is greater than the avg closing price!")
else: 
	print ("RECOMMENDATION: DO NOT BUY! The stock's current closing price is the avg of previous closing prices.")
print("-----------------")
print(f"WRITING DATA TO CSV: {csv_file_path}...")
print("-------------------------")
print("HAPPY INVESTING!")
print("-------------------------")
