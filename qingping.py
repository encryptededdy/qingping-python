import json
import requests
import time
import base64

# e.g. {"appKey" : "xxxx", "appSecret" : "xxxxx" } from https://developer.qingping.co/personal/permissionApply
config = json.load(open('qp_config.json', 'r'))

access_token = ""
expiry = 0

def get_access_token():
    global access_token
    global expiry
    # If current token is valid, return that
    if (expiry > int(time.time())) and access_token:
        print("Using cached access token")
        return access_token

    # If current token is invalid...
    print("Using getting new access token")
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
    print("Got access token")
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

# Pretty-print the device info for an air quality monitor
def airquality_pretty(device_info, markdown = False):
    temp = device_info["temperature"]
    humidity = device_info["humidity"]
    tvoc = device_info["tvoc"]/1000 # ppm
    co2 = device_info["co2"]
    pm25 = device_info["pm25"]
    pm10 = device_info["pm10"]

    if markdown:
        return f"*Temperature:* {temp:.1f}°C\n*Humidity:* {humidity:.1f}%\n*tVOC:* {tvoc:.3f}ppm\n*CO₂:* {co2}ppm\n*PM2.5:* {pm25}µg/m3\n*PM10*: {pm10}µg/m3"
    else:
        return f"Temperature: {temp:.1f}°C\nHumidity: {humidity:.1f}%\ntVOC: {tvoc:.3f}ppm\nCO₂: {co2}ppm\nPM2.5: {pm25}µg/m3\nPM10: {pm10}µg/m3"
