import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf

class technical_indicator():
    def __init__(self, path):
        self.MA=None
        self.KD=None
        self.hammer=None
        self.path = path
    def MA_graph(self, short_term, long_term, company_id, start, freq='Days', end=None):
        Width=0.7
        df=yf.download(company_id,start,end, progress = False)
        if df.shape[0] == 0:
            print("No data")
            print(company_id, start, end)
            return None
        price = df.Close.iloc[-1]
        
        # standardize the volume
        df.Volume = (df.Volume - df.Volume.mean())/df.Volume.std()
        data = df.copy()
        CLOSE = ((data.Close - data.Close.shift(1))/data.Close.shift(1)).to_numpy() + 1
        CLOSE[0] = 1
        df.Close = np.cumprod(CLOSE)
        df.Open = (data.Open/data.Close) * df.Close
        df.High = (data.High/data.Close) * df.Close
        df.Low = (data.Low/data.Close) * df.Close        
        
        if freq in ['Months' , 'months' , 'Month' , 'month' , 'm' , 'M']:
            df=df.resample('M',closed='right' ,label='right').agg(dict(zip(df.columns,["first", "max", "min", "last", "last", "sum"])))
            Width=10
        if freq in ['Weeks', 'Week' , 'weeks' , 'week' , 'w' , 'W' ]:
            df=df.resample('W-FRI', closed='right' ,label='right').agg(dict(zip(df.columns,["first", "max", "min", "last", "last", "sum"])))
            Width=3
        
        plt.ioff()
        plt.figure(figsize=(24,12))
        plt.subplot(211)
        plt.grid(True)
        low=df['Close'].min()-0.5*(df['Close'].max()-df['Close'].min())
        df['New Open']=df['Open']-low
        df['New Close']=df['Close']-low
        df['New High']=df['High']-low
        df['New Low']=df['Low']-low
        
        plt.bar(df.index[df['Close']>df['Open']],df['New Close'][df['Close']>df['Open']],color='#E80707',width=Width,bottom=low)
        plt.bar(df.index[df['Close']>df['Open']],df['New Open'][df['Close']>df['Open']],color='#FFFFFF',width=Width,bottom=low)

        plt.bar(df.index[df['Close']<df['Open']],df['New Open'][df['Close']<df['Open']],color='#178C14',width=Width,bottom=low)
        plt.bar(df.index[df['Close']<df['Open']],df['New Close'][df['Close']<df['Open']],color='#FFFFFF',width=Width,bottom=low)

        plt.bar(df.index[df['Close']==df['Open']],df['New Open'][df['Close']==df['Open']],color='#969696',width=Width,bottom=low)
        plt.bar(df.index[df['Close']==df['Open']],(df['New Open']-0.1)[df['Close']==df['Open']],color='#FFFFFF',width=Width,bottom=low)

        plt.bar(df.index[df['Close']>df['Open']],df['New High'][df['Close']>df['Open']],color='#E80707',width=0.05,bottom=low)
        plt.bar(df.index[df['Close']<df['Open']],df['New High'][df['Close']<df['Open']],color='#178C14',width=0.05,bottom=low)
        plt.bar(df.index[df['Close']==df['Open']],df['New High'][df['Close']==df['Open']],color='#969696',width=0.05,bottom=low)
        plt.bar(df.index,df['New Low'],color='#FFFFFF',width=Width,bottom=low)

        plt.plot(df['Close'].rolling(short_term).mean(),label='%dMA'%short_term)
        plt.plot(df['Close'].rolling(long_term).mean(),label='%dMA'%long_term)
        plt.legend()
        plt.subplot(212)
        plt.grid(True)
        plt.bar(df.index[df['Close']>df['Open']],df['Volume'][df['Close']>df['Open']],color='#E80707',width=Width)
        plt.bar(df.index[df['Close']<df['Open']],df['Volume'][df['Close']<df['Open']],color='#178C14',width=Width)
        plt.savefig(f"./{self.path}/{company_id}_{start}_{end}.png")
        plt.close()
        df['%dMA'%short_term]=df['Adj Close'].rolling(short_term).mean()
        df['%dMA'%long_term]=df['Adj Close'].rolling(long_term).mean()
        self.MA=df.filter(items=['%dMA'%short_term,'%dMA'%long_term])
        return price
        
    