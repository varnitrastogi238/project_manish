import json
from datetime import datetime
import random
from requests import delete
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
import sys
import pyotp
from datetime import time, datetime

# import telepot
# bot = telepot.Bot("5448843199:AAEKjMn2zwAyZ5tu8hsLIgsakxoLf980BoY")
# bot.getMe()
import logging
try:
    import telepot
    bot = telepot.Bot('5764368331:AAGrun4IEIUf75APRxcp_IXZmUz_oeavUGo')
    bot.getMe()
except:
    pass
logger = logging.getLogger("dev_log")


class run_strategy:
    def __init__(self, strategy):
        self.parameters = strategy
        self.list = {"open": 0, "high": 0, "low": 99999999, "close": 0}
        self.prev_high = 0
        self.prev_low = 9999999
        self.stoploss = 0
        self.invested = int(self.parameters.amount_invested)
        self.position = "off"
        self.parameters.stoploss = int(self.parameters.stoploss)
        self.max_stoploss=self.parameters.max_stoploss
        self.max_stoploss/=100.0
        self.ltp_prices = {}

    def ltp_nifty_options(self):
        # print()
        self.list["close"] = self.obj.ltpData(
            "NSE", self.parameters.symbol, str(self.parameters.token)
        )["data"]["ltp"]
        if self.list["close"] > self.list["high"]:
            self.list["high"] = self.list["close"]
        if self.list["close"] < self.list["low"]:
            self.list["low"] = self.list["close"]
        
    def main(self):
        
        if (
            (
                ((self.list["high"] - self.list["low"]) * 100)
                > (float(self.parameters.range) * self.list["close"])
            )
            and (self.list["close"] < self.list["open"])
            and self.parameters.sell == "on"
            and self.position == "off"
        ):
            self.add_positions(
                self.parameters.symbol, "SELL", self.list["close"], 00, 00
            )
            # stoploss
            b=self.parameters.symbol[:-3]+".NS"
            df = yf.download(b, period='2d', interval="5m")
            aa=df['High'][-1]
            aaa=df['High'][-2]
            self.stoploss = min(
                max(aa,aaa),
                self.list["close"] + (self.max_stoploss * self.list["close"]),
            )
            self.position = "on"

        if (
            (
                ((self.list["high"] - self.list["low"]) * 100)
                > (float(self.parameters.range) * self.list["close"])
            )
            and self.list["close"] > self.list["open"]
            and self.parameters.buy == "on"
            and self.position == "off"
        ):
            self.add_positions(
                self.parameters.symbol, "BUY", self.list["close"], 00, 00
            )
            b=self.parameters.symbol[:-3]+".NS"
            df = yf.download(b, period='2d', interval="5m")
            aa=df['Low'][-1]
            aaa=df['Low'][-2]
            self.stoploss = min(
                min(aa,aaa),
                self.list["close"] - (self.max_stoploss * self.list["close"]),
            )
            self.position = "on"

        if (
            self.stoploss != 0
            and self.list["close"] < self.stoploss
            and self.parameters.stoploss > 0
            and self.parameters.buy == "on"
            and self.position == "on"
        ):
            self.current_position.status = "CLOSED"
            self.current_position.pnl=self.list['close']-self.current_position.price_in
            self.current_position.price_out = self.list["close"]
            self.current_position.time_out = datetime.now(timezone("Asia/Kolkata"))
            self.current_position.save()
            self.close_position(
                self.parameters.symbol, "SELL", self.current_position.quantity
            )
            self.position = "off"
            self.invested = self.invested + (
                (self.invested * float(self.parameters.position_increase)) / 100
            )
            self.parameters.stoploss -= 1

        if (
            self.stoploss != 0
            and self.list["close"] > self.stoploss
            and self.parameters.stoploss > 0
            and self.parameters.sell == "on"
            and self.position == "on"
        ):
            self.current_position.status = "CLOSED"
            self.current_position.price_out = self.list["close"]
            self.current_position.pnl=self.current_position.price_in-self.list['close']
            self.current_position.time_out = datetime.now(timezone("Asia/Kolkata"))
            self.current_position.save()
            self.close_position(
                self.parameters.symbol, "BUY", self.current_position.quantity
            )
            self.position = "off"
            self.invested = self.invested + (
                (self.invested * float(self.parameters.position_increase)) / 100
            )
            self.parameters.stoploss -= 1

    def login(self):
        try:
            self.obj = SmartConnect(api_key=self.parameters.angel_api_keys)
            data = self.obj.generateSession(
                self.parameters.angel_client_id,
                self.parameters.angel_password,
                pyotp.TOTP(self.parameters.totp).now(),
            )
            refreshToken = data["data"]["refreshToken"]
            self.feedToken = self.obj.getfeedToken()
        except:
            print(traceback.format_exc())
            logger.info(str(traceback.format_exc()))

    def websocket(self):

        self.login()
        start = 0
        start_of_candle = -1
        while True:
            try:
                if (
                    start == 0
                    and datetime.now(timezone("Asia/Kolkata")).minute % 5 == 0
                ):
                    start = 1
                if time(15, 20) <= datetime.now(timezone("Asia/Kolkata")).time():
                    if self.position=="on" and self.parameters.buy=="on":
                        self.current_position.status = "CLOSED"
                        self.current_position.price_out = self.list["close"]
                        self.current_position.pnl=self.list['close']-self.current_position.price_in
                        self.current_position.time_out = datetime.now(timezone("Asia/Kolkata"))
                        self.current_position.save()
                        self.close_position(
                            self.parameters.symbol, "SELL", self.current_position.quantity
                        )
                    if self.position=="on" and self.parameters.sell=="on":
                        self.current_position.status = "CLOSED"
                        self.current_position.price_out = self.list["close"]
                        self.current_position.pnl=self.current_position.price_in-self.list['close']
                        self.current_position.time_out = datetime.now(timezone("Asia/Kolkata"))
                        self.current_position.save()
                        self.close_position(
                            self.parameters.symbol, "BUY", self.current_position.quantity
                        )
                    return "done_fire_fire"
                temp = strategy.objects.get(username="testing")
                if temp.stop == "on":
                    return "done_double_fire"
                
                if self.position=="on":
                    self.current_position.current_price=self.list['close']
                    if self.parameters.buy=="on":
                        self.current_position.pnl=self.list['close']-self.current_position.price_in
                        self.current_position.save()
                    else:
                        self.current_position.pnl=self.current_position.price_in-self.list['close']
                        self.current_position.save()
                    temp2 = stop_symboll.objects.filter(symbol=self.current_position.symbol)
                    if temp2 :
                        self.position="off"
                        self.current_position.status = "CLOSED"
                        self.current_position.price_out = self.list["close"]
                        self.current_position.time_out = datetime.now(timezone("Asia/Kolkata"))
                        self.current_position.save()
                        stop_symboll.objects.all().delete()
                        return "done_double_fire"
                if self.parameters.stoploss == 0:
                    return "triple_fire_fire"
                if start == 1:
                    if (
                        start_of_candle != datetime.now(timezone("Asia/Kolkata")).minute
                        and datetime.now(timezone("Asia/Kolkata")).minute % 5== 0
                    ):
                        start_of_candle = datetime.now(timezone("Asia/Kolkata")).minute
                        self.list["open"] = self.obj.ltpData(
                            "NSE", self.parameters.symbol, str(self.parameters.token)
                        )["data"]["ltp"]
                        
                        self.prev_high = self.list["high"]
                        self.prev_low = self.list["low"]
                    self.ltp_nifty_options()
                    self.main()
            except Exception as e:
                print(traceback.format_exc())
                try:
                     bot.sendMessage(
                            1190128536, f"Manish sir ka exception{e}")
                except:
                    pass
                logger.info(str(traceback.format_exc()))
                self.login()

    def real_orders(self, symbol, side):

        if self.parameters.paper == "off":
            if side == "LONG":
                side = "BUY"

            else:
                side = "SELL"
            try:
                orderparams = {
                    "variety": "NORMAL",
                    "tradingsymbol": str(symbol),
                    "symboltoken": str(self.parameters.token),
                    "transactiontype": str(side),
                    "exchange": "NSE",
                    "ordertype": "MARKET",
                    "producttype": "INTRADAY",
                    "duration": "DAY",
                    "quantity": str(int(self.invested / self.list["close"])),
                }

                orderId = self.obj.placeOrder(orderparams)
                print("The order id is: {}".format(orderId))
            except Exception as e:
                print("Order placement failed: {}".format(e.message))

    def close_position(self, symbol, side, quantity):
        if self.parameters.paper == "off":
            if side == "LONG":
                side = "BUY"

            else:
                side = "SELL"
            try:
                orderparams = {
                    "variety": "NORMAL",
                    "tradingsymbol": str(symbol),
                    "symboltoken": str(self.parameters.token),
                    "transactiontype": str(side),
                    "exchange": "NSE",
                    "ordertype": "MARKET",
                    "producttype": "INTRADAY",
                    "duration": "DAY",
                    "quantity": str(quantity),
                }

                orderId = self.obj.placeOrder(orderparams)
                print("The order id is: {}".format(orderId))
            except Exception as e:
                print("Order placement failed: {}".format(e.message))

    def add_positions(self, symbol, side, price_in, time_out, price_out):
        strategy1 = positions(
            symbol=symbol,
            time_in=datetime.now(timezone("Asia/Kolkata")),
            side=str(side),
            price_in=float(price_in),
            quantity=int(float(self.invested) / self.list["close"]),
            time_out=datetime.now(timezone("Asia/Kolkata")),
            price_out=float(price_out),
            status="OPEN",
            token=str(self.parameters.token),
        )
        self.current_position = strategy1
        strategy1.save()
        self.real_orders(symbol, side)


    def run(self):
        try:
            value = self.websocket()
            return value
        except Exception:
            print(traceback.format_exc())
            logger.info(str(traceback.format_exc()))
