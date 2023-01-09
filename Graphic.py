import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests
from binance.client import Client
import time


symbol = 'XRPUSDT'
KEY = '6ba95e7ed67fff7357a6a9fdca47e350852a2d62668d1db9570e5ae9db99e9c3'
SECRET = '793aebcbcff748c0350cd24979964541e28cbe8491e2005853c52bec0cd4473f'
client = Client(KEY, SECRET, tld='https://testnet.binancefuture.com', testnet=True)

TOKEN = '5653486266:AAEXoa-iM1pAY5N9eDEwbXJ6-aLGCyEgR5k'
CHAT = '624736798'


def get_futures_klines(symbol, limit=500):
    x = requests.get('https://binance.com/fapi/v1/klines?symbol=' + symbol + '&limit=' + str(
        limit) + '&interval=5m')  # ===================СВЕЧА=======================
    df = pd.DataFrame(x.json())
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'd1', 'd2', 'd3', 'd4', 'd5']
    df = df.drop(['d1', 'd2', 'd3', 'd4', 'd5'], axis=1)
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return (df)

def graphik(symbol=symbol):
    df = get_futures_klines(symbol=symbol, limit=50)

    up = df[df. close >=df. open ]
    down = df[df. close <df. open ]

    width = .4 #.4 стандарт.-ширина свечей
    width2 = .05 #.05 -вторая ширина

    col1 = 'green'
    col2 = 'red'
    fig, ax = plt.subplots(facecolor='grey',edgecolor='black')
    ax.set_facecolor('black')
    ax.set_xlim(0,55)
    #время
    a = time.ctime()
    a = a.split()
    times = a[3][0:5]

    #свечи вверх
    plt.plot(df.index,df.close,color='white',alpha=0.6,linestyle='-.')
    plt.bar (up. index ,up. close -up. open ,width,bottom=up. open ,color=col1)
    plt.bar (up. index ,up. high -up. close ,width2,bottom=up. close ,color=col1)
    plt.bar (up. index ,up. low -up. open ,width2,bottom=up. open ,color=col1)
    #свечи вниз
    plt.bar (down. index ,down. close -down. open ,width,bottom=down. open ,color=col2)
    plt.bar (down. index ,down. high -down. open ,width2,bottom=down. open ,color=col2)
    plt.bar (down. index ,down. low -down. close ,width2,bottom=down. close ,color=col2)
    plt.grid(color='turquoise',linewidth=0.2,linestyle='--')
    prices = client.futures_mark_price()
    df = pd.DataFrame(prices)
    price=float(df[df['symbol'] == symbol]['markPrice'])

    ax.set_title(f'{symbol}   {times}',fontsize=20,color='blue')

    x = [0, 55]
    y = [price, price]
    plt.plot(x,y,label=f'Price {price}',color='white',linestyle='--',marker='',linewidth=0.5)
    plt.legend(loc='best')

    #наклон галочек
    plt.xticks (np.arange(0,55,5),rotation= 45 , ha='right')

    fig.savefig(f'C:/Users/Admin/Desktop/talib./graph')

    # отправка фото
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendPhoto';
    files = {'photo': open(r"C:\Users\Admin\Desktop\talib\graph.png", 'rb')}
    data = {'chat_id': "624736798"}
    r = requests.post(url, files=files, data=data)
    return r.json()