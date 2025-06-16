import requests,time
from typing import Literal

class SolverError(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class Capsolver():
    def __init__(self,apikey:str):
        self.apikey = apikey
        self.baseURL = "https://api.capsolver.com"
    def getBalance(self):
        response = requests.post(f'{self.baseURL}/getBalance',json={
            "clientKey":self.apikey
        }).json()
        if response["balance"]:
            return {
                "success":True,
                "balance":response["balance"]
            }
        else:
            return {
                "success":False,
            }
    def createTask(
        self,
        type:Literal["AntiTurnstileTaskProxyLess","ReCaptchaV2TaskProxyLess"],
        websiteURL:str,
        websiteKey:str
    ):
        self.taskId = ""
        self.start_time = 0
        self.start_time = time.time()
        try:
            response = requests.post(f'{self.baseURL}/createTask',json={
                "clientKey": self.apikey,
                "task": {
                    "type": type,
                    "websiteURL": websiteURL,
                    "websiteKey": websiteKey,
                    "pageAction": "submit",
                    "isInvisible": True
                }
            },timeout=30).json()
        except TimeoutError:
            raise SolverError("Timed out")
        if response["taskId"]:
            self.taskId = f"{response["taskId"]}"
            return {
                "success": True,
                "taskId": response["taskId"]
            }
        else:
            return {
                "succes": False,
                "message": response
            }
    def getTaskResult(self,type:Literal["AntiTurnstileTaskProxyLess","ReCaptchaV2TaskProxyLess"]="AntiTurnstileTaskProxyLess"):
        while True:
            try:
                response = requests.post(f'{self.baseURL}/getTaskResult',json={
                    "clientKey":self.apikey,
                    "taskId":self.taskId
                },timeout=30).json()
            except TimeoutError:
                raise SolverError("Timed out")
            if type == "AntiTurnstileTaskProxyLess" and response["status"] == "ready" and response["solution"]["token"]:
                solved_time = time.time() - self.start_time
                return {
                    "success":True,
                    "solution":{
                        "token":response["solution"]["token"],
                        "userAgent":response.get("solution",{}).get("userAgent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
                        "solved_time":solved_time
                    }
                }
            if type == "ReCaptchaV2TaskProxyLess" and response["status"] == "ready" and response["solution"]["gRecaptchaResponse"]:
                solved_time = time.time() - self.start_time
                return {
                    "success":True,
                    "solution":{
                        "token":response["solution"]["gRecaptchaResponse"],
                        "userAgent":response.get("solution",{}).get("userAgent","Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"),
                        "solved_time":solved_time
                    }
                }
            elif response["status"] == "idle" or response["status"] == "processing":
                time.sleep(1)
                continue
            else:
                return {
                    "success":False,
                    "message":response
                }