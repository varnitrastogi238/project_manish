from django.db import models
from django.db.models.fields import DateField, IntegerField
from django.contrib.auth.models import User
# Create your models here.

class strategy(models.Model):
    username=models.CharField(max_length=20,default="NONE")
    angel_api_keys=models.CharField(max_length=100,default='NONE')
    angel_client_id=models.CharField(max_length=50,default='NONE')
    angel_password=models.CharField(max_length=50,default='NONE')
    totp=models.CharField(max_length=50,default='NONE')
    symbol=models.CharField(max_length=100,default='NONE')
    token=models.IntegerField(default=1)
    range=models.DecimalField(default=1,max_digits=5, decimal_places=2)
    stoploss=models.IntegerField(default=0)
    position_increase=models.FloatField(default=0)
    max_stoploss=models.FloatField(default=0)
    amount_invested=models.IntegerField(default=1)
    paper=models.CharField(default="off",max_length=4)
    stop=models.CharField(default="off",max_length=4)
    sell=models.CharField(default="off",max_length=4)
    buy=models.CharField(default="off",max_length=4)
    weekly_expiry=models.CharField(default="NONE",max_length=10)
    bots_started=models.IntegerField(default=0)

class stop_symboll(models.Model):
    symbol=models.CharField(max_length=25,default="NONE")

class positions(models.Model):
    symbol=models.CharField(max_length=50,default='NA')
    time_in=models.DateTimeField(default="_")
    price_in=models.FloatField(default=0)
    side = models.CharField(max_length=20,default='NA')
    current_price=models.FloatField(default=0)
    quantity=models.IntegerField(default=0)
    time_out=models.DateTimeField(default="_")
    price_out=models.FloatField(default=0)
    status=models.CharField(max_length=20,default='NA')
    token=models.CharField(max_length=20,default='NA')
    pnl=models.FloatField(default=0)