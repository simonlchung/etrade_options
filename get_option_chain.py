from __future__ import print_function
import webbrowser
import json
import logging
import configparser
import os
import sys
import os.path
import pathlib
import requests
from requests_oauthlib import OAuth1Session
from tabulate import tabulate
from datetime import datetime,date
from pytz import timezone
import argparse

# loading configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# argparse
# Parse Arguments
parser = argparse.ArgumentParser(description='Example:  %(prog)s -t TSLA -s 800 -c Put ')
parser.add_argument('-t', '--ticker', default='TSLA',
                    help='Stock Ticker')
parser.add_argument('-s', '--strike', default=800,
                    help='strike price')
parser.add_argument('-n', '--number_of_strike', default=1,
                    help='Number of strike prices to pull for a given option expiry')
parser.add_argument('-e', '--number_of_expiry', default=5,
                    help='Number of expiry to pull for a given option')
parser.add_argument('-c', '--chain', default='Put',
                    help='Option Type Call or Put')
args = parser.parse_args()

def get_oauth_session():
    # Init
    base_url_prod = r"https://api.etrade.com"
    base_url_dev = r"https://apisb.etrade.com"
    req_token_url = r"https://api.etrade.com/oauth/request_token"
    auth_token_url = r"https://us.etrade.com/e/t/etws/authorize"
    access_token_url = r"https://api.etrade.com/oauth/access_token"
    client_key = config["DEFAULT"]["CONSUMER_KEY"]
    renew_access_token_url = r"https://api.etrade.com/oauth/renew_access_token"

    # Check if file is older than today, token expires at midnight US Eastern, remove file if it's old so that we can re-auth session
    if (os.path.exists('access_token.json')):
        fname = pathlib.Path('access_token.json')
        tz = timezone('US/Eastern')
        create_time = datetime.fromtimestamp(fname.stat().st_ctime,tz)
        today_time = datetime.now(tz)
        if not (today_time.date() == create_time.date()):
            os.remove("access_token.json")

    # Check if access_token is saved and still valid
    if (os.path.exists('access_token.json')):
        try:
            #load access_token
            with open('access_token.json') as json_file:
                access_token = json.load(json_file)

            session = OAuth1Session(
                client_key = config["DEFAULT"]["CONSUMER_KEY"],
                client_secret = config["DEFAULT"]["CONSUMER_SECRET"],
                resource_owner_key = access_token['oauth_token'],
                resource_owner_secret = access_token['oauth_token_secret'],
                signature_type="AUTH_HEADER",
            )
            #test to make sure session works by renewing token
            session.get(renew_access_token_url)
        except:
            print("Unable to get authenticated session, removing access_token.json")
            print("Please try running command again.")
            #os.remove("access_token.json")
            sys.exit(1)
    else:
        try:
            # Set up session
            session = OAuth1Session(
                client_key = config["DEFAULT"]["CONSUMER_KEY"],
                client_secret = config["DEFAULT"]["CONSUMER_SECRET"],
                callback_uri="oob",
                signature_type="AUTH_HEADER",
            )
            session.fetch_request_token(req_token_url)
            authorization_url = session.authorization_url(auth_token_url)
            akey = session.parse_authorization_response(authorization_url)
            resource_owner_key = akey["oauth_token"]
            formated_auth_url = "%s?key=%s&token=%s" % (
                    auth_token_url,
                    client_key,
                    resource_owner_key,
                )
            #Open webbrowser to get text code from E*Trade
            webbrowser.open(formated_auth_url)
            text_code = input("Please accept agreement and enter text code from browser: ")
            session._client.client.verifier = text_code
            #Get access_token
            access_token = session.fetch_access_token(access_token_url)
            #Save access_token to cache
            with open('access_token.json', 'w') as json_file:
                json.dump(access_token, json_file)
            os.chmod("access_token.json", 0o600)

        except:
            print("Unable to get authenticated session, check config.ini for correct consumer_key and consumer_secret")
            sys.exit(1)

    return session

def get_option_quote_detail(url):
    response = session.get(url)
    print(json.dumps(response.json(), indent=4, sort_keys=True))


def get_quote(base_url, session, symbol):
    url = base_url + "/v1/market/quote/" + symbol + ".json"
    response = session.get(url)
    #print(response.json())
    print(json.dumps(response.json(), indent=4, sort_keys=True))

def get_stock_price(base_url, session, symbol):
    url = base_url + "/v1/market/quote/" + symbol + ".json"
    response = session.get(url)
    #print(json.dumps(response.json(), indent=4, sort_keys=True))
    data = response.json()
    for index in data['QuoteResponse']['QuoteData']:
       lastTrade = index['All']['lastTrade']

    return(lastTrade)

def get_option_expiredate(base_url, session, symbol):
    url = base_url + "/v1/market/optionexpiredate.json?symbol=" + symbol
    response = session.get(url)
    data = response.json()
    return(data['OptionExpireDateResponse']['ExpirationDate'])

def get_option_chains(base_url, session, symbol, strike_price_near, no_of_strikes = 3, no_of_expiry = 5, chain_type="Call"):
    #get option expiry
    expiry_dates = get_option_expiredate(base_url, session, symbol)
    stock_price = get_stock_price(base_url, session, symbol)

    #table header
    table = [['Option','% from strike','ITM','dte','roi / annual roi','breakeven','lastPrice','bid x ask', 'bid x ask Size', 'volume', 'openInterest', 'delta / (% chance worthless)', 'theta', 'IV']]

    for index, expiry_date in enumerate(expiry_dates,start=1):
        #get options chains for each expiry
        url = base_url + "/v1/market/optionchains.json?expiryDay=" + str(expiry_date['day']) + "&expiryMonth=" + str(expiry_date['month']) + "&expiryYear=" + str(expiry_date['year']) + "&symbol=" + symbol + \
              "&strikePriceNear=" + str(strike_price_near) + "&noOfStrikes=" + str(no_of_strikes) + "&includeWeekly=true" + "&chainType=" + chain_type + "&skipAdjusted=false"
        response = session.get(url)
        #print(json.dumps(response.json(), indent=4, sort_keys=True))
        #gather data to generate a table
        data = response.json()

        #work out days to expiration
        #print(data['OptionChainResponse']['SelectedED']['day'], data['OptionChainResponse']['SelectedED']['month'], data['OptionChainResponse']['SelectedED']['year'])
        today = date.today()
        future = date(data['OptionChainResponse']['SelectedED']['year'],data['OptionChainResponse']['SelectedED']['month'],data['OptionChainResponse']['SelectedED']['day'])
        days_to_expiration = future - today
        if days_to_expiration.days == 0:
            dte = 1
        else:
            dte = days_to_expiration.days

        for option in data['OptionChainResponse']['OptionPair']:
            #calculate stuff
            option_contract = option[chain_type]['displaySymbol']
            percent_distance_from_strike = "{:.2%}".format((option[chain_type]['strikePrice'] - stock_price) / stock_price)
            itm = option[chain_type]['inTheMoney']

            transaction_roi = "{:.2%}".format(option[chain_type]['bid'] / option[chain_type]['strikePrice'])
            annual_roi = "{:.2%}".format((option[chain_type]['bid'] / option[chain_type]['strikePrice']) / dte * 365)
            roi = "{} / {}".format(transaction_roi,annual_roi)
            if (chain_type == 'Call'):
                breakeven = stock_price - option[chain_type]['bid']
            else:
                breakeven = option[chain_type]['strikePrice'] - option[chain_type]['bid']

            last_price = option[chain_type]['lastPrice']
            bid_ask = "{:.2f} / {:.2f}".format(option[chain_type]['bid'], option[chain_type]['ask'])
            bid_ask_size = "{} / {}".format(option[chain_type]['bidSize'], option[chain_type]['askSize'])
            volume = option[chain_type]['volume']
            open_interest = option[chain_type]['openInterest']

            if (option[chain_type]['OptionGreeks']['delta'] < 0):
                percent_expire_worthless = "{:.2f} / ({:.0%})".format(option[chain_type]['OptionGreeks']['delta'],1 + option[chain_type]['OptionGreeks']['delta'])
            else:
                percent_expire_worthless = "{:.2f} / ({:.0%})".format(option[chain_type]['OptionGreeks']['delta'],1 - option[chain_type]['OptionGreeks']['delta'])

            theta = option[chain_type]['OptionGreeks']['theta']
            iv_percentage = "{:.2%}".format(option[chain_type]['OptionGreeks']['iv'])

            table.append([option_contract, percent_distance_from_strike, itm ,days_to_expiration.days, roi, breakeven, last_price,  \
                          bid_ask, bid_ask_size, volume, open_interest, percent_expire_worthless, theta, iv_percentage])
            #get_option_quote_detail(option[chain_type]['quoteDetail'])
        if (no_of_strikes > 1):
            table.append(['-------------------------'])

        if index >= no_of_expiry:
            break

    #print table
    print("Current Stock Price: {}".format(stock_price))
    print(tabulate(table, floatfmt=".2f", headers="firstrow", colalign=("left","center","center","decimal","center","decimal","decimal","center","center","right","right","center","decimal","decimal")))

if __name__ == "__main__":
    base_url = "https://api.etrade.com"
    stock = args.ticker
    strike_price_near = float(args.strike)
    no_of_strikes = int(args.number_of_strike)
    no_of_expiry = int(args.number_of_expiry)
    chain_type = args.chain
    session = get_oauth_session()

    get_option_chains(base_url = base_url, session = session, symbol = stock, strike_price_near = strike_price_near, no_of_strikes = no_of_strikes, no_of_expiry = no_of_expiry, chain_type = chain_type)
