import json
from datetime import datetime
import random
from sympy import div
from datamanagement.models import *
import yfinance as yf
import math
import pandas as pd
import time as tim
from smartapi import SmartConnect
from smartapi import SmartWebSocket
from .background_functions import *
from pytz import timezone
import traceback
from datetime import time, datetime
# import telepot
# bot = telepot.Bot("5448843199:AAEKjMn2zwAyZ5tu8hsLIgsakxoLf980BoY")
# bot.getMe()
import logging
logger = logging.getLogger('dev_log')


class run_strategy():

    def __init__(self, strategy):
        self.parameters = strategy
        self.ltp_prices = {}
        self.difference=200
        self.trigger_at=800
        self.dicts={}
        self.market="undone"
        self.shifted=0
        self.time=tim.time()

    def ltp_nifty_options(self):
        
        

        position_opened = positions.objects.filter(
           status='OPEN')
        
        self.nifty_price = self.obj.ltpData("NSE", 'NIFTY', "26000")['data']['ltp']

        position_opened = positions.objects.filter(
             status='OPEN')
        print(position_opened.all())
        for i in range(len(position_opened)):
            try:

                self.ltp_prices[position_opened[i].token] = self.obj.ltpData("NFO", position_opened[i].symbol, str(position_opened[i].token))['data']['ltp']
                position_opened[i].current_price = float(
                    self.ltp_prices[position_opened[i].token])

                if position_opened[i].side=="LONG":
                    position_opened[i].pnl= (position_opened[i].current_price-position_opened[i].price_in)

                if position_opened[i].side=="SHORT":
                    position_opened[i].pnl= (position_opened[i].price_in-position_opened[i].current_price)

                position_opened[i].save()

            except Exception:
                print(traceback.format_exc())
                logger.info(str(traceback.format_exc()))


    def shift_position(self):

        self.shifted=self.shifted+1
        position_opened = positions.objects.filter(status='OPEN')
        print(position_opened.all())
        pnl=10000
        
        for i in range(len(position_opened)):
            if position_opened[i].pnl<pnl:
                pnl=position_opened[i].pnl
                close_position_val=i



        # for i in range(len(position_opened)):
        position_opened[close_position_val].status = "CLOSED"
        position_opened[close_position_val].time_out = datetime.now(timezone("Asia/Kolkata"))
        position_opened[close_position_val].price_out = float(
            self.ltp_prices[position_opened[close_position_val].token])
        position_opened[close_position_val].save()



        strike_price = round(self.nifty_price/50, 0)*50
        self.last_market_order=self.nifty_price
        

        symbol_pe = "NIFTY"+self.parameters.weekly_expiry +str(int(strike_price))+'PE'
        symbol_ce = "NIFTY"+self.parameters.weekly_expiry +str(int(strike_price))+'CE'

        df=pd.read_csv("datamanagement/helpful_scripts/scripts.csv")

        for i in range(len(df)):
            if df['symbol'][i]==symbol_pe:
                self.dicts[df['symbol'][i]]=df['token'][i]

            elif df['symbol'][i]==symbol_ce:
                self.dicts[df['symbol'][i]]=df['token'][i]

        sell_price_put=self.obj.ltpData("NFO", symbol_pe, str(self.dicts[symbol_pe]))['data']['ltp']
        sell_price_call=self.obj.ltpData("NFO", symbol_ce, str(self.dicts[symbol_ce]))['data']['ltp']


        p = self.add_positions(symbol_pe, 'SHORT', sell_price_put, 0, 0)
        p = self.add_positions(symbol_ce, 'SHORT', sell_price_call, 0, 0)

        if self.shifted==1:
            if self.total_premium/2>400:
                self.total_premium=self.total_premium/2

            else:
                self.total_premium=400

        if self.shifted==4:
            self.close_all_positions()


    def close_all_positions(self):

        position_opened = positions.objects.filter(status='OPEN')

        for i in range(len(position_opened)):
            position_opened[i].status = "CLOSED"
            position_opened[i].time_out = datetime.now(timezone("Asia/Kolkata"))
            position_opened[i].price_out = float(
                self.ltp_prices[position_opened[i].token])
            position_opened[i].save()

        return None

    def main(self):


        if (float(self.nifty_price) >= self.last_market_order+50):
            self.shift_position()


        if (float(self.nifty_price) <= self.last_market_order-50):
            # bot.sendMessage(1039725953,"closing position")
            self.shift_position()

        if time(15, 20) <= datetime.now(timezone("Asia/Kolkata")).time():

            # bot.sendMessage(1039725953,"closing position")
            self.close_all_positions()
            self.parameters.bots_started=0
            self.parameters.save()
            return "complete"


    def login(self):
        for i in range(10):
            try:
                self.obj = SmartConnect(api_key=self.parameters.angel_api_keys)
                data = self.obj.generateSession(self.parameters.angel_client_id, self.parameters.angel_password)
                refreshToken = data['data']['refreshToken']
                self.feedToken = self.obj.getfeedToken()
                break
            except:
                tim.sleep(1)
                i+=1

    def websocket(self):

        while True:
            try:




                if time(10, 30) <= datetime.now(timezone("Asia/Kolkata")).time() and self.market=="undone":
                    self.time=tim.time()

                    self.login()
                    self.nifty_price=self.obj.ltpData("NSE", 'NIFTY', "26000")['data']['ltp']
                    data = self.market_order()
                    self.market="done"

                if self.market=="done" and tim.time()>=self.time+300:
                    self.time=tim.time()
                    self.ltp_nifty_options()
                    data = self.main()
                    if data == "complete":
                        return None

            except Exception:
                print(traceback.format_exc())
                logger.info(str(traceback.format_exc()))




    def add_positions(self, symbol, side, price_in, time_out, price_out):
        print(datetime.now(timezone("Asia/Kolkata")))
        strategy1 = positions(


            symbol=symbol,
            time_in=datetime.now(timezone("Asia/Kolkata")),
            side=str(side),
            price_in=float(price_in),
            time_out=datetime.now(timezone("Asia/Kolkata")),
            price_out=float(price_out),
            status="OPEN",
            token=str(self.dicts[symbol])
        )

        strategy1.save()

    def market_order(self):
        nifty_price = round(self.nifty_price/50, 0)*50

        self.last_market_order=self.nifty_price

        symbol_sell_put = 'NIFTY'+self.parameters.weekly_expiry+str(int(nifty_price))+'PE'
        symbol_sell_call = 'NIFTY'+self.parameters.weekly_expiry+str(int(nifty_price))+'CE'

        df=pd.read_csv("datamanagement/helpful_scripts/scripts.csv")


        for i in range(len(df)):
            if df['symbol'][i]==symbol_sell_put:
                self.dicts[df['symbol'][i]]=df['token'][i]

            elif df['symbol'][i]==symbol_sell_call:
                self.dicts[df['symbol'][i]]=df['token'][i]


        sell_price_put=self.obj.ltpData("NFO", symbol_sell_put, str(self.dicts[symbol_sell_put]))['data']['ltp']
        sell_price_call=self.obj.ltpData("NFO", symbol_sell_call, str(self.dicts[symbol_sell_call]))['data']['ltp']



        symbol_buy_call='NIFTY'+self.parameters.weekly_expiry+str(int(nifty_price+500))+'CE'
        symbol_buy_put='NIFTY'+self.parameters.weekly_expiry+str(int(nifty_price-500))+'PE'

        for i in range(len(df)):
            if df['symbol'][i]==symbol_buy_put:
                self.dicts[df['symbol'][i]]=df['token'][i]

            elif df['symbol'][i]==symbol_buy_call:
                self.dicts[df['symbol'][i]]=df['token'][i]


        buy_price_put=self.obj.ltpData("NFO", symbol_buy_put, str(self.dicts[symbol_buy_put]))['data']['ltp']
        buy_price_call=self.obj.ltpData("NFO", symbol_buy_call, str(self.dicts[symbol_buy_call]))['data']['ltp']



        p = self.add_positions(
            symbol_buy_put, "LONG", buy_price_put, 0, 0)
        p = self.add_positions(
            symbol_buy_call, "LONG", buy_price_call, 0, 0)
        p = self.add_positions(
            symbol_sell_put, "SHORT", sell_price_put, 0, 0)
        p = self.add_positions(
            symbol_sell_call, "SHORT", sell_price_call, 0, 0)

    def run(self):
        try:
            this_scripts()
            positions.objects.all().delete()
            value = self.websocket()
            return value
        except Exception:
            print(traceback.format_exc())
            logger.info(str(traceback.format_exc()))
