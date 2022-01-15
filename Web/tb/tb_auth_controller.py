# url  = "http://ec2-54-255-160-87.ap-southeast-1.compute.amazonaws.com:8080" 
import requests
from flask import json
import config as Config
url_base  = Config.iot_server
SUB_URL = "/api/auth/"

def tb_login(username,password):
    url = url_base  + SUB_URL +"login"
    payload={"username":username,"password":password}
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response


def tb_changePassword(token,old_password,new_password):
    url = url_base  + "/api/auth/changePassword"
    payload ={"currentPassword":old_password,"newPassword":new_password}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response

def tb_getUser(token):
    # print(token)
    url = url_base  + SUB_URL +"user"
    payload={}
    # print(token)
    headers = {'X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    # print(response.text)
    return response

