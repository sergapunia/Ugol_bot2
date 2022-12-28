import requests
import pandas as pd
from pandas import DataFrame
import datetime
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
#from aiogram import Bot, Dispatcher, executor, types
import copy
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from binance.client import Client

# TOKEN = '5653486266:AAEXoa-iM1pAY5N9eDEwbXJ6-aLGCyEgR5k'
# CHAT = '624736798'

pd.set_option('display.max_columns', 500)  # приводим в порядок отображение колонок 1-отобразить все колонки
pd.set_option('display.max_rows', 500)  # 2 - ряды
pd.set_option('display.width', 1000)  # 3-ширина
# bot = Bot(TOKEN)
# dp = Dispatcher(bot)


KEY = 'L41IDD7sjzsoCOzkboH6EPL4PThTLIUEwHvpFq4rhb8IZ5coCQs3yv1NCXjJrkiL'
SECRET = 'hrUpyoWaLiQwLlMjmJwQta0PHKZz5qTAXUj1GusS1rLTFbhvkFhLYg4cq2qJVe0u'

#client = Spot(key=api_key, secret=sicret_key, base_url="https://testnet.binance.vision")
client = Client(KEY, SECRET, tld='https://testnet.binancefuture.com', testnet=True)

def candals(symbol,interval, limit=500):
    x = requests.get('https://binance.com/fapi/v1/klines?symbol=' + symbol + '&limit=' + str(limit) + '&interval='+ str(interval))
    df = pd.DataFrame(x.json())
    df.columns = ['open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'd1', 'd2', 'd3', 'd4', 'd5']
    df = df.drop(['d1', 'd2', 'd3', 'd4', 'd5'], axis=1)
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return (df)


# print(DataFrame(candals('BTCUSDT', '5m', 30)))

# --------------------------------------------------------------------------

def indSlope(series, n):  # определяет угол наклона
    array_sl = [j * 0 for j in range(n - 1)]
    for j in range(n, len(series) + 1):
        y = series[j - n:j]
        x = np.array(range(n))
        x_sc = (x - x.min()) / (x.max() - x.min())
        y_sc = (y - y.min()) / (y.max() - y.min())
        x_sc = sm.add_constant(x_sc)
        model = sm.OLS(y_sc, x_sc)
        results = model.fit()
        array_sl.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(array_sl))))
    return np.array(slope_angle)


def indATR(source_DF, n):  # истинный дневной деапазон
    df = source_DF.copy()
    df['H-L'] = abs(df['high'] - df['low'])
    df['H-PC'] = abs(df['high'] - df['close'].shift(1))
    df['L-PC'] = abs(df['low'] - df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df_temp = df.drop(['H-L', 'H-PC', 'L-PC'], axis=1)
    return df_temp


def PrepareDF(DF):
    ohlc = DF.iloc[:, [0, 1, 2, 3, 4, 5]]
    ohlc.columns = ["date", "open", "high", "low", "close", "volume"]
    ohlc = ohlc.set_index('date')
    df = indATR(ohlc, 14).reset_index()
    df['slope'] = indSlope(df['close'], 5)
    df['channel_max'] = df['high'].rolling(10).max()
    df['channel_min'] = df['low'].rolling(10).min()
    df['position_in_channel'] = (df['close'] - df['channel_min']) / (df['channel_max'] - df['channel_min'])
    df = df.set_index('date')
    df = df.reset_index()
    return (df)


# MIN
def isLCC(DF, i):
    df = DF.copy()
    LCC = 0

    if df['close'][i] <= df['close'][i + 1] and df['close'][i] <= df['close'][i - 1] and df['close'][i + 1] > \
            df['close'][i - 1]:
        # найдено Дно
        LCC = i - 1;
    return LCC


# MAX
def isHCC(DF, i):
    df = DF.copy()
    HCC = 0
    if df['close'][i] >= df['close'][i + 1] and df['close'][i] >= df['close'][i - 1] and df['close'][i + 1] < \
            df['close'][i - 1]:
        # найдена вершина
        HCC = i;
    return HCC


def getMaxMinChannel(DF, n):  # ыерхний и нижний уровень канала
    maxx = 0
    minn = 0
    for i in range(0, n - 1):
        if maxx < DF['high'][len(DF) - i]:
            maxx = DF['high'][len(DF) - i]
        if minn > DF['low'][len(DF) - i]:
            minn = DF['low'][len(DF) - i]
    return (maxx, minn)


df = DataFrame(candals('ETHUSDT', '5m', 500)) #=============================================================
df = df[::-1]  # можно убрать
prepared_df = PrepareDF(df)
lend = len(prepared_df)
prepared_df['hcc'] = [None] * lend
prepared_df['lcc'] = [None] * lend
# print(prepared_df)

for i in range(4, lend - 1):
    if isHCC(prepared_df, i) > 0:
        prepared_df.at[i, 'hcc'] = prepared_df['close'][i]
    if isLCC(prepared_df, i) > 0:
        prepared_df.at[i, 'lcc'] = prepared_df['close'][i]

position = 0
deal = 0
eth_proffit_array = [[20, 1], [40, 1], [60, 2], [80, 2], [100, 2], [150, 1], [200, 1],
                     [200, 0]]  # пункты и кол.контрактов по ним
prepared_df['deal_o'] = [None] * lend
prepared_df['deal_c'] = [None] * lend
prepared_df['earn'] = [None] * lend

for i in range(4, lend - 1):
    prepared_df.at[i, 'earn'] = deal

    if position > 0:
        # add profit/loss for long
        if (prepared_df['close'][i] < stop_price):
            # stop loss
            deal = deal + (prepared_df['close'][i] - open_price) * position
            prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
            position = 0
        else:
            temp_arr = copy.copy(proffit_array)
            for j in range(0, len(temp_arr) - 1):
                delta = temp_arr[j][0]
                contracts = temp_arr[j][1]
                if (prepared_df['close'][i] > (open_price + delta)):
                    # take profit
                    prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
                    deal = deal + (prepared_df['close'][i] - open_price) * contracts
                    position = position - contracts
                    del proffit_array[0]

    elif position < 0:
        # add profit/loss for short
        if (prepared_df['close'][i] > stop_price):
            # stop loss
            deal = deal + (open_price - prepared_df['close'][i]) * position
            prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
            position = 0
        else:
            temp_arr = copy.copy(proffit_array)
            for j in range(0, len(temp_arr) - 1):
                delta = temp_arr[j][0]
                contracts = temp_arr[j][1]
                if ((open_price - prepared_df['close'][i]) > delta):
                    # take profit
                    prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
                    deal = deal + (open_price - prepared_df['close'][i]) * contracts
                    position = position + contracts
                    del proffit_array[0]

    else:
        # try to find enter point
        if prepared_df['lcc'][i - 1] != None:
            # found bottom - OPEN LONG
            if prepared_df['position_in_channel'][
                i - 1] < 0.4:  # близость прижатия к каналу.можно поменять и сделать ближе(0.2)
                # close to top of channel
                if prepared_df['slope'][i - 1] < -10:  # уровень наклона -меньше для боковиков
                    # found a good enter point
                    if position == 0:
                        proffit_array = copy.copy(eth_proffit_array)
                        position = 10
                        open_price = prepared_df['close'][i]
                        stop_price = prepared_df['close'][i] * 0.99  # стоп лосс на 1%,97-это 3%
                        prepared_df.at[i, 'deal_o'] = prepared_df['close'][i]
        if prepared_df['hcc'][i - 1] != None:
            # found top - OPEN SHORT
            if prepared_df['position_in_channel'][i - 1] > 0.4:  # близость прижатия к каналу
                # close to top of channel
                if prepared_df['slope'][i - 1] > 10:  # уровень наклона
                    # found a good enter point
                    if position == 0:
                        proffit_array = copy.copy(eth_proffit_array)
                        position = -10
                        open_price = prepared_df['close'][i]
                        stop_price = prepared_df['close'][i] * 1.01  # стоп лосс в 1% можно поменять,1.03- 3%
                        prepared_df.at[i, 'deal_o'] = prepared_df['close'][i]

hours = round(lend * 5 / 60, 0)
print('Total erned in ', hours, ' hours =', int(deal), '$')


def graphic():
    ### рисовалка

    aa = prepared_df[0:999]
    aa = aa.reset_index()

    # labels = ['close',"deal_o","deal_c"]
    labels = ['close', "deal_o", "deal_c", "channel_max", "channel_min"]

    labels_line = ['--', "*-", "*-", "g-", "r-"]

    j = 0
    x = pd.DataFrame()
    y = pd.DataFrame()
    for i in labels:
        x[j] = aa['index']
        y[j] = aa[i]
        j = j + 1

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

    fig.suptitle('Deals')
    fig.set_size_inches(20, 10)

    for j in range(0, len(labels)):
        ax1.plot(x[j], y[j], labels_line[j])

    ax1.set_ylabel('Price')
    ax1.grid(True)

    ax2.plot(x[0], aa['earn'], 'g-')  # EMA
    ax3.plot(x[0], aa['position_in_channel'], '.-')  # EMA

    ax2.grid(True)
    ax3.grid(True)

    plt.show()
#print(graphic())