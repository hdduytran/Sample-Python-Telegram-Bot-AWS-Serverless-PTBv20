import requests
import json
import os


def get_captcha():

    url = "https://autocaptcha.pro/apiv3/process"

    payload = json.dumps({
        "key": os.getenv("CAPTCHA_SECRET"),
        "type": "hcaptcha",
        "websitekey": os.getenv("websitekey"),
        "pageurl": "https://stealthwriter.ai"
    })
    headers = {
        'Content-Type': 'application/json',
        'Cookie': 'ASP.NET_SessionId=oj0j0bzkampzc1mz4umf52q3'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    obj = response.json()
    if not obj.get("success"):
        print("Failed to get captcha")
        print(obj)
        return None

    return obj.get("captcha")


def get_token(captcha):

    url = "https://vqdtifewupwhdypyimkf.supabase.co/auth/v1/token?grant_type=password"

    payload = json.dumps({
        "email": os.getenv("EMAIL"),
        "password": os.getenv("PASSWORD"),
        "gotrue_meta_security": {
            "captcha_token": captcha,
        }
    })
    headers = {
        'Content-Type': 'application/json',
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxZHRpZmV3dXB3aGR5cHlpbWtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDg1MTM1OTMsImV4cCI6MjAyNDA4OTU5M30.rbjRooZeTqJm0hNd94ys84aPwGtneOId_qvwK-9kM8E'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    obj = response.json()
    print(obj)
    
    if obj.get("code") == 400:
        print("Failed to get token")
        print(obj)
        return None
    
    if not obj.get("access_token"):
        print("Failed to get token")
        print(obj)
        return None
    
    return f"supabase-auth-token=%5B%22{obj.get('access_token')}%22%2C%22{obj.get('refresh_token')}%22%2Cnull%2Cnull%2Cnull%5D"

def lambda_handler(event, context):
    captcha = get_captcha()
    if not captcha:
        return {
            'statusCode': 500,
            'body': 'Failure'
        }
    token = get_token(captcha)
    if not token:
        return {
            'statusCode': 500,
            'body': 'Failure'
        }
    return {
        'statusCode': 200,
        'body': token
    }
    
if __name__ == "__main__":
    res = lambda_handler(None, None)
    print(res)
    