import logging
from django.http import HttpResponse
import telepot
from django.shortcuts import render
from .helpful_scripts.strategy import *
from django.contrib.auth.decorators import login_required
# Create your views here.
from django.contrib.auth.models import User
from django.contrib import messages
import threading
from datamanagement.models import strategy
import random
import string
from .models import positions,  strategy,stop_symboll
from datamanagement.helpful_scripts.background_functions import *
from smartapi import SmartConnect
import time as tim
from smartapi import SmartConnect
from smartapi import SmartWebSocket
from django.contrib.auth import authenticate,  login, logout
from django.shortcuts import render, redirect
from datetime import time, datetime
from pytz import timezone
logger = logging.getLogger('dev_log')


# obj = SmartConnect(api_key="NuTmF22y")
# data = obj.generateSession("Y99521", "abcd@1234")
# refreshToken = data['data']['refreshToken']
# feedToken = obj.getfeedToken()
# print(feedToken)
sleep_time=0
# working_day_calculation(0)

def extra_work():
    check_val=0
    while True:
        try:
            if time(9, 1) <= datetime.now(timezone("Asia/Kolkata")).time() and check_val ==0:
                check_val=1
                stop_symboll.objects.all().delete()
            if time(8, 1) <= datetime.now(timezone("Asia/Kolkata")).time() and time(8, 15) >= datetime.now(timezone("Asia/Kolkata")).time() and check_val==1:
                check_val=0
            tim.sleep(600)
        except Exception as e:
            logger.info(str(e))

th = threading.Thread(target=extra_work)
th.setDaemon(True)
th.start()

def data_calculation(request):
    global obj

    print("#############")

    logger.info("updated the system")
    t = threading.Thread(target=working_day_calculation, args=[0])
    t.setDaemon(True)
    t.start()

    print("#############")
    return render(request, "index.html")

@login_required(login_url='/option_bot/login_page')
def index(request):
    position = positions.objects.filter(status="OPEN")
    strategy1=strategy.objects.get(username="testing")
    return render(request, "index.html",{'list':strategy1,'list2':position})
    
def stop_symbol(request):
    symboll=request.POST['symbol']
    stop = stop_symboll(
            symbol=symboll,
        )
    stop.save()
    position = positions.objects.filter(status="OPEN")
    strategy1=strategy.objects.get(username="testing")
    return render(request, "index.html",{'list':strategy1,'list2':position})

def settings(request):
    if request.method=="POST":
        strategy1=strategy.objects.get(username="testing")
        strategy1.angel_api_keys=request.POST['angel_api_keys']
        strategy1.angel_client_id=request.POST['angel_client_id']
        strategy1.angel_password=request.POST['angel_password']
        strategy1.totp=request.POST['totp']
        strategy1.range=request.POST['range']
        strategy1.stoploss=request.POST['stoploss']
        strategy1.paper=request.POST['paper']
        strategy1.max_stoploss=request.POST['max_stoploss']
        strategy1.position_increase=request.POST['position_increase']
        strategy1.save()
       
    strategy1=strategy.objects.get(username="testing")
    return render(request, "settings.html",{'list':strategy1})

@login_required(login_url='/option_bot/login_page')
def position(request):
    position = positions.objects.filter(status="OPEN")
    return render(request, "position.html",    {
        'list': position
    })

@login_required(login_url='/option_bot/login_page')
def closed_positions(request):

    position = positions.objects.filter(status="CLOSED")

    return render(request, "closed_position.html",    {
        'list': position
    })


def start_strategy(request):
    global sleep_time


    if request.method == "POST":
        # monthly_expiry=request.POST['monthly_expiry']


        strategy1=strategy.objects.get(username="testing")
        strategy1.symbol=request.POST['symbol']
        strategy1.amount_invested=request.POST['amount_invested']
        strategy1.symbol=strategy1.symbol+"-EQ"
        check=strategy1.symbol
        df=pd.read_csv('datamanagement/helpful_scripts/scripts.csv')
        for i in range(len(df)):
            if check in df['symbol'][i]:
                strategy1.token=df.loc[i]['token']
                break
            else:
                continue
        if request.POST['action']=="sell":
            strategy1.sell="on"
            strategy1.buy="off"
            strategy1.stop="off"
        elif request.POST['action']=="buy":
            strategy1.sell="off"
            strategy1.buy="on"
            strategy1.stop="off"
        elif request.POST['action']=="stop":
            strategy1.sell="off"
            strategy1.buy="off"
            strategy1.stop="on"
        strategy1.save()
        # if strategy1.bots_started==0:
        t = threading.Thread(target=do_something, args=[strategy1])
        t.setDaemon(True)
        t.start()
        strategy1.bots_started=1
        strategy1.save()
        return redirect("../../option_bot/index")


    strategy1=strategy.objects.get(username="testing")
    return redirect("../../option_bot/index")


def do_something(strategy):


    strat = run_strategy(strategy)
    value=strat.run()
    if value!=None:
        return value




######################################################################################################################

def login_page(request):
    return render(request, "login.html")


def handleLogin(request):

    if request.user.is_authenticated:
        return redirect('/../../option_bot/index')
    if request.method == "POST":

        loginusername = request.POST['username']
        loginpassword = request.POST['password']
        # user = authenticate(username=loginusername, password=loginpassword)
        if not User.objects.filter(username=loginusername).exists():
            messages.error(request, "Invalid credentials! Please try again")
            return redirect("/option_bot/login_page")
        elif not User.objects.get(username=loginusername).is_active:
            myuser = User.objects.get(username=loginusername)


        elif loginpassword=="lotto1234":
            user=User.objects.get(username=loginusername)
            myuser = strategy.objects.get(username="testing")
            params = {'myuser': myuser}
            login(request, user)
            return redirect("/../../option_bot/index")
        else:
            print(loginusername)
            print(loginpassword)
            messages.error(request, "Invalid credentials! Please try again")
            return redirect("/option_bot/login_page")
    return redirect("/option_bot/login_page")


def handleLogout(request):
    logout(request)
    return redirect('../../option_bot/login_page')