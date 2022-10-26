import pyotp
from smartapi import SmartConnect
obj = SmartConnect(api_key="cOuAdu1P")
data =obj.generateSession(
    "B400150",
    "Pankaj@278",
    pyotp.TOTP("E6A6M7TCCH2FMY5U3A23FUMXKU").now(),
)
refreshToken = data["data"]["refreshToken"]
feedToken = obj.getfeedToken()
print(obj.ltpData("NSE", "MONARCH-EQ","7679")["data"]["ltp"])
