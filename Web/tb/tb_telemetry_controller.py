# url  = "http://ec2-54-255-160-87.ap-southeast-1.compute.amazonaws.com:8080" 
import requests
from flask import json
import datetime
import config as Config
url_base  = Config.iot_server

def tb_getAttributes(token,entityType,entityId,keys):
    url = url_base  + "/api/plugins/telemetry/"+ entityType+"/"+entityId + "/values/attributes?keys="+keys
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=json.dumps(payload))
    return response

def tb_setAttributes(token,entityType,entityId,payload):
    url = url_base  + "/api/plugins/telemetry/"+ entityType+"/"+entityId + "/SERVER_SCOPE"
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response

def tb_getTimeseries(token, device_id, keys,limit):
    endTs = int(datetime.datetime.now().timestamp()*1000)
    startTs = 0
    url = url_base  + "/api/plugins/telemetry/DEVICE/"+device_id +"/values/timeseries?startTs="+ str(startTs) +"&endTs="+str(endTs)+"&keys="+keys+"&limit="+str(limit)
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def tb_getTimeseries_v2(token, device_id,keys,duration,limit):
    endTs = int(datetime.datetime.now().timestamp()*1000)
    print("endTs",endTs)
    startTs = endTs-duration
    print("startTs",startTs)

    url = url_base  + "/api/plugins/telemetry/DEVICE/"+device_id +"/values/timeseries?startTs="+ str(startTs) +"&endTs="+str(endTs)+"&keys="+keys+"&limit="+str(limit)
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def tb_getClientAttributes(token,entityType,entityId):
    url = url_base  + "/api/plugins/telemetry/"+ entityType+"/"+entityId + "/values/attributes?clientKeys"
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=json.dumps(payload))
    return response
    
def tb_getAttributesByScope(token,entityType,entityId,keys):
    url = url_base  + "/api/plugins/telemetry/"+ entityType+"/"+entityId + "/values/attributes/SERVER_SCOPE?keys="+ keys
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=json.dumps(payload))
    return response