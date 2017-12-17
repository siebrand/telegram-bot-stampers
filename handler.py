import datetime
import json
import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import requests

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def hello(event, context):
    try:
        os.environ['TZ'] = 'Europe/Amsterdam'

        data = json.loads(event["body"])

        # print (data)

        message = str(data["message"]["text"])

        chat_id = data["message"]["chat"]["id"]
        first_name = data["message"]["from"]["first_name"]

        response = "Please /start, {}".format(first_name)

        if "start" in message:
            response = "Hallo {}! Typ '/omloop' als je wilt weten wanneer het seizoen weer begint! ".format(first_name)

        if "omloop" in message:
            omloop = datetime.date(2018, 2, 28)
            response = "Omloop is over {} dagen!".format((omloop - datetime.date.today()).days)

        print (message, response)

        data = {
            "text": response.encode("utf8"),
            "chat_id": chat_id
        }
        url = BASE_URL + "/sendMessage"
        requests.post(url, data)

    except Exception as e:
        print(e)

    return {"statusCode": 200}
