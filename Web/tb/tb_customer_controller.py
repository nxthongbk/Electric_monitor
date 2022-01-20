# url  = "http://ec2-54-255-160-87.ap-southeast-1.compute.amazonaws.com:8080" 
import requests
from flask import json
import datetime

import config as Config
url_base  = Config.iot_server

#Customer
sub_url_customer_info = "/api/tenant/customers"
sub_url_customer = "/api/customer/"
sub_url_customers = "/api/customers?"

def tb_saveCustomer(token,customer):
    url = url_base  + sub_url_customer
    payload =json.dumps(customer)
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("POST", url, headers=headers, data=payload)
    return response

def tb_deleteCustomer(token,customer_id):
    print(customer_id)
    url = url_base  + sub_url_customer+str(customer_id)
    print(url)
    payload ={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("DELETE", url, headers=headers, data=payload)
    return response

def tb_getCustomers(token,page,page_size):
    url = url_base  + sub_url_customers+ "pageSize=%d&page=%d"%(page_size,page)
    payload ={}
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("GET", url, headers=headers, data=payload)
    return response
