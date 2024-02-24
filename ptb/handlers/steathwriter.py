import requests
import json
from core.ssm_handler import get_parameter, update_parameter
from core.lambda_handler import invoke_lambda
import time
import os

url = "https://stealthwriter.ai/api/rewrite-text"


def humanizer(text, level=10, model="ninja", retry=0):
    cookies = get_parameter('/steath_writer_cookies')

    payload = json.dumps({
        "text": text,
        "method": "humanizer",
        "fingerprint": "k2V6kxFsaqVVcjdZL8Yk3VDbnl1q1Lq0UuC5RFXIqvfqd20CLeTnC79UK0acksVmiRcHU0Y/SWsu6rEjVV4ZRxnFXLXzElligcE0DP6rzMQUViEmgO0yXZCA1BEnCbOtrpnUiw25FUJl8bdxgPqRfxbemjtBeyRokexzr4Ff2pYMdYPtCMmdoyT8wbhtgmSTKXm/PtfS1NkqdpWT2o394Q/zKNNbKNAyp9unqCnQKuR7bG0CRkMieZyRCU5SxNJzmKlAMvg9e1Gyd/F4DmlqX7yJIpA2o6BJC2W9sD+8MkCaKCcD6yRkQWkAG67UWKNiNJBb7IF9uDkd+iKrvhYMRLzDNcIvsCCVnC7t//9Jk+yLbM6xs2eqegeBo9i3UntG",
        "level": level,
        "model": "ninja"
    })
    headers = {
        'authority': 'stealthwriter.ai',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'cookie': cookies,
        'origin': 'https://stealthwriter.ai',
        'pragma': 'no-cache',
        'referer': 'https://stealthwriter.ai/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    obj = json.loads(response.text)

    taskId = obj.get('sentences')
    print(f"Task ID: {taskId}")

    if not taskId:
        print(obj)
        if retry > 0:
            return None
        # if "signed in" in obj.get("error") or "":
        print("Need to sign in")
        response = invoke_lambda(os.getenv("TOKEN_LAMBDA"), {})
        if response.get("statusCode") == 200:
            cookies = response.get("body")
            update_parameter('/steath_writer_cookies', cookies)
            return humanizer(text, level, model, retry+1)
        return None

    else:
        new_cookies = response.cookies.get_dict()
        cookies = "; ".join([f"{k}={v}" for k, v in new_cookies.items()])
        # print(f"New Cookies: {cookies}")
    update_parameter('/steath_writer_cookies', cookies)

    # for i in range(30):
    #     time.sleep(1)
    #     print(f"Checking status of task: {taskId}")
    #     result = get_result(taskId)
    #     # print(result.get("status"))
    #     print(result)
    #     if result.get('status') == 'completed':
    #         print("Task Completed")
    sentences = obj.get('sentences')
    text_list = {}
    for sentence in sentences:
        alternatives = sentence.get("alternatives")
        if not alternatives:
            for key in text_list:
                text_list[key] += "\n"
        for i in range(len(alternatives)):
            if not text_list.get(i):
                text_list[i] = ""
            else:
                text_list[i] += " "
            text_list[i] += alternatives[i]
    return list(text_list.values())


def get_result(taskId):

    cookies = get_parameter('/steath_writer_cookies')
    authorization = "Bearer " + cookies.split("%22")[1]

    url = "https://vqdtifewupwhdypyimkf.supabase.co/rest/v1/rpc/get_task_by_id"

    payload = json.dumps({
        "task_id": taskId
    })
    headers = {
        'authority': 'vqdtifewupwhdypyimkf.supabase.co',
        'accept': '*/*',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxZHRpZmV3dXB3aGR5cHlpbWtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDg1MTM1OTMsImV4cCI6MjAyNDA4OTU5M30.rbjRooZeTqJm0hNd94ys84aPwGtneOId_qvwK-9kM8E',
        'authorization': authorization,
        'cache-control': 'no-cache',
        'content-profile': 'public',
        'content-type': 'application/json',
        'origin': 'https://stealthwriter.ai',
        'pragma': 'no-cache',
        'referer': 'https://stealthwriter.ai/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Microsoft Edge";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
        'x-client-info': '@supabase/auth-helpers-nextjs@0.5.6'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return response.json()


if __name__ == "__main__":
    text = "This is a test text"
    res = humanizer(text)
    print(res)
