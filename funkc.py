import requests
import numpy as np
import pandas as pd

from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.client import Client
from futures_sign import send_signed_request, send_public_request
from cred import KEY, SECRET

symbol='BTCUSDT'

client = Client(KEY,SECRET,tld='https://testnet.binancefuture.com',testnet=True)

# Get last 500 kandels 5 minutes for Symbol

def get_futures_klines(symbol,limit=500):
    x = requests.get('https://binance.com/fapi/v1/klines?symbol='+symbol+'&limit='+str(limit)+'&interval=5m')
    df=pd.DataFrame(x.json())
    df.columns=['open_time','open','high','low','close','volume','close_time','d1','d2','d3','d4','d5']
    df=df.drop(['d1','d2','d3','d4','d5'],axis=1)
    df['open']=df['open'].astype(float)
    df['high']=df['high'].astype(float)
    df['low']=df['low'].astype(float)
    df['close']=df['close'].astype(float)
    df['volume']=df['volume'].astype(float)
    return(df)


# Open position for Sybol with

def open_position(symbol, s_l, quantity_l):
    sprice = get_symbol_price(symbol)

    if (s_l == 'long'):
        close_price = str(round(sprice * (1 + 0.01), 2))
        responce = client.futures_create_order(symbol=symbol,
                                               side='BUY',
                                               type='LIMIT',
                                               quantity=str(quantity_l),
                                               timeInForce='GTC',
                                               prise= close_price)

    if (s_l == 'short'):
        close_price = str(round(sprice * (1 - 0.01), 2))
        responce = client.futures_create_order(symbol=symbol,
                                               side='SELL',
                                               type='LIMIT',
                                               quantity=str(quantity_l),
                                               timeInForce='GTC',
                                               prise= close_price)


# Open position for Sybol with

def open_position(symbol, s_l, quantity_l):
    sprice = get_symbol_price(symbol)

    if (s_l == 'long'):
        close_price = str(round(sprice * (1 + 0.01), 2))
        params = {
                    "symbol": symbol,
                    "side": "BUY",
                    "type": "LIMIT",
                    "quantity": str(quantity_l),
                    "timeInForce": "GTC",
                    "price": close_price

                }
        client.futures_create_order(**params)

    if (s_l == 'short'):
        close_price = str(round(sprice * (1 - 0.01), 2))
        params = {
                    "symbol": symbol,
                    "side": "SELL",
                    "type": "LIMIT",
                    "quantity": str(quantity_l),
                    "timeInForce": "GTC",
                    "price": close_price
                }
        client.futures_create_order(**params)


# Close position for symbol with quantity

def close_position(symbol, s_l, quantity_l):
    sprice = get_symbol_price(symbol)

    if (s_l == 'long'):
        close_price = str(round(sprice * (1 - 0.01), 2))
        params = {
            "symbol": symbol,
            "side": "SELL",
            "type": "LIMIT",
            "quantity": str(quantity_l),
            "timeInForce": "GTC",
            "price": close_price
        }
        client.futures_create_order(**params)
    if (s_l == 'short'):
        close_price = str(round(sprice * (1 + 0.01), 2))
        params = {

            "symbol": symbol,
            "side": "BUY",
            "type": "LIMIT",
            "quantity": str(quantity_l),
            "timeInForce": "GTC",
            "price": close_price
        }
        client.futures_create_order(**params)


# Find all opened positions

def get_opened_positions(symbol):
    status = client.futures_account()
    positions=pd.DataFrame(status['positions'])
    a = positions[positions['symbol']==symbol]['positionAmt'].astype(float).tolist()[0]
    leverage = int(positions[positions['symbol']==symbol]['leverage'])
    entryprice = positions[positions['symbol']==symbol]['entryPrice']
    profit = float(status['totalUnrealizedProfit'])
    balance = round(float(status['totalWalletBalance']),2)
    if a>0:
        pos = "long"
    elif a<0:
        pos = "short"
    else:
        pos = ""
    return([pos,a,profit,leverage,balance,round(float(entryprice),3),0])


# Close all orders

def check_and_close_orders(symbol):
    global isStop
    a=client.futures_get_open_orders(symbol=symbol)
    if len(a)>0:
        isStop = False
        client.futures_cancel_all_open_orders(symbol=symbol)


def get_symbol_price(symbol):
    prices = client.get_all_tickers()
    df=pd.DataFrame(prices)
    return float(df[ df['symbol']==symbol]['price'])