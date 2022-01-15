# url  = "http://ec2-54-255-160-87.ap-southeast-1.compute.amazonaws.com:8080" 
import time
import requests
from flask import json
import datetime

import config as Config
url_base  = Config.iot_server

sub_url_devices1 ="/devices?"
sub_url_user = "/api/auth/user"
sub_url_getTenantDeviceInfos = "/api/tenant/deviceInfos?"

sub_url_timeseries_device_last_telemetry ="/api/plugins/telemetry/DEVICE/"
sub_url_timeseries_device_last_telemetry1 ="api/plugins/telemetry/DEVICE"

def tb_getCustomerDevices(token,customer_id,page,page_size):
    url = url_base  + "/api/customer/"+ customer_id+"/devices?" + "pageSize=%d&page=%d"%(page_size,page)
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=json.dumps(payload))
    return response

def tb_assignDeviceToCustomer(token,customer_id,device_id):
    url = url_base  + sub_url_devices +customer_id +"/device/"+device_id
   
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response

def tb_get_timeseries_device_last_telemetry(token, device_id, keys):
    url = url_base  + sub_url_timeseries_device_last_telemetry +device_id +"/values/timeseries?keys=" + keys
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def tb_getTimeseries(token, device_id, key, delta):

    #current-time
    endTs = int(datetime.datetime.now().timestamp()*1000)
    startTs = endTs-delta
    url = url_base  + sub_url_timeseries_device_last_telemetry +device_id +"/values/timeseries?keys=" + key + "&orderBy=ASC&limit=1000&startTs=%d&endTs=%d"%(startTs,endTs)
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    # print(response.json())
   
    return response

def tb_getTenantDeviceInfos(token, page, page_size):
    url = url_base  + sub_url_getTenantDeviceInfos +"pageSize=%d&page=%d"%(page_size,page)
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def tb_getDeviceInfoById(token, device_id):
    url = url_base  + "/api/device/info/"+ device_id 
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response

def tb_getTenantDevices(token,device_id):
    url = url_base  + "/api/tenant/devices?deviceName="+ device_id
    payload={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=json.dumps(payload))
    return response