import requests
import json
from core.ssm_handler import get_parameter, update_parameter
import time

url = "https://stealthwriter.ai/api/rewrite-text"


def humanizer(text, level=10, model="ninja"):
    cookies = get_parameter('/steath_writer_cookies')

    payload = json.dumps({
        "text": text,
        "method": "humanizer",
        "fingerprint": "k2V6kxFsaqVVcjdZL8Yk3VDbnl1q1Lq0UuC5RFXIqvdY4659ySi6rpWXcs423XV/+DDVNsmBl1VoOsryLv7aA3P2GOlFf4ySROn6RBCdqGFqIH+yKCfiVC16JjNfJdv9SX9rqTKPjrdJNfHFfQOqhSN02LBH3xCXZQLiEPYqI1db91/IawC0qAUJ7NwS6Y9Cii6odhIAxxveh2/75UgCd2l9JW3dH3PjH7IWhO+3t65I3U0kywQ6okdQSjGwv4nDi7JDo3TYvS49r36NA/vOM8FEcNAPLMYZH4v2+FJeX35M4FV9kMjhLnz76mKVIbBeO1k4qULgzhQxcdKH7vKTgih+4Kr2AI+rSo1gtkiDlYML4rgCWF9lZ+VP727P8+F8VM2acp0mrKtO12jLkI33ptCxuQz3uDpr+jmYqujkwhI=",
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

    taskId = obj.get('taskId')
    print(f"Task ID: {taskId}")

    if not taskId:
        return ["Error: Error in processing the text. Please try again"]

    new_cookies = response.cookies.get_dict()

    # update the cookies as string

    cookies = "; ".join([f"{k}={v}" for k, v in new_cookies.items()])
    # print(f"New Cookies: {cookies}")
    update_parameter('/steath_writer_cookies', cookies)

    for i in range(10):
        time.sleep(1)
        print(f"Checking status of task: {taskId}")
        result = get_result(taskId)
        print(result)
        if result.get('status') == 'completed':
            print("Task Completed")
            sentences = result.get('json').get('sentences')
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
        'apikey': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZxZHRpZmV3dXB3aGR5cHlpbWtmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MDY2MTkwMzUsImV4cCI6MjAyMjE5NTAzNX0.u9ckg_ZijAOjTSitoOev1PzvH6MhfXp3-97FAYajg-E',
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
