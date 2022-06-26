import json
import requests
import time
import base64

# e.g. {"appKey" : "xxxx", "appSecret" : "xxxxx" } from https://developer.qingping.co/personal/permissionApply
config = json.load(open('config.json', 'r'))

access_token = ""
expiry = 0

def get_access_token():
    global access_token
    global expiry
    # If current token is valid, return that
    if (expiry > int(time.time())) and access_token:
        return access_token

    # If current token is invalid...
    url = "https://oauth.cleargrass.com/oauth2/token"
    auth_string = base64.b64encode((config["appKey"] + ":" + config["appSecret"]).encode('ascii')).decode('ascii')
    payload = "grant_type=client_credentials&scope=device_full_access"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {auth_string}"
    }

    response = requests.request("POST", url, data=payload, headers=headers)
    parsed_response = json.loads(response.content)
    access_token = parsed_response["access_token"]
    expiry = parsed_response["expires_in"] + int(time.time()) # expiry time
    return access_token

def parse_data(data):
    return {i[0]:i[1]["value"] for i in data.items()}


def get_device_info():
    url = "https://apis.cleargrass.com/v1/apis/devices"
    querystring = {"timestamp":int(time.time()*1000)}
    headers = {"Authorization": f"Bearer {get_access_token()}"}
    response = requests.request("GET", url, headers=headers, params=querystring)
    parsed_response = json.loads(response.content)
    return {e["info"]["name"]:parse_data(e["data"]) for e in parsed_response["devices"]}