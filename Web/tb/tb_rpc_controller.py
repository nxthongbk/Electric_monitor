# url  = "http://ec2-54-255-160-87.ap-southeast-1.compute.amazonaws.com:8080" 
import requests
from flask import json

import config as Config
url_base  = Config.iot_server


def tb_rpc(token, rpc_type, device_id, payload):
    url = url_base  + "/api/plugins/rpc/" + rpc_type + "/"+device_id
    headers = {'Content-Type': 'application/json','X-Authorization':'Bearer  '+token}
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    return response

