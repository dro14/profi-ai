import requests
import asyncio
import time
import os


SECRET_KEY = os.environ["SECRET_KEY"]
BASE_URL = "https://profitraininguz.getcourse.ru/pl/api/account"
USERS_URL = BASE_URL + "/users?status=active&key=" + SECRET_KEY
EXPORTS_URL = BASE_URL + "/exports/{}?key=" + SECRET_KEY

users = {}


async def update_users():
    while True:
        try:
            response = requests.get(USERS_URL).json()
            export_id = response["info"]["export_id"]
            exports_url = EXPORTS_URL.format(export_id)
        except:
            time.sleep(10)
            continue

        while True:
            response = requests.get(exports_url).json()
            if response["success"]:
                for item in response["info"]["items"]:
                    key = f"{item[5]} {item[6]}".strip()
                    try:
                        users[key].append({"id": item[0], "email": item[1]})
                    except KeyError:
                        users[key] = [{"id": item[0], "email": item[1]}]
                break
            else:
                print(response)
                time.sleep(10)


asyncio.run(update_users())

for key, value in users.items():
    print(key, value)
