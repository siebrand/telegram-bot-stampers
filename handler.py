import datetime
import json
import os
import sys

import requests

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

TOKEN = os.environ['TELEGRAM_TOKEN']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)


def hello(event, context):
    try:
        data = json.loads(event["body"])

        # print (data)

        message = str(data["message"]["text"])

        chat_id = data["message"]["chat"]["id"]
        first_name = data["message"]["from"]["first_name"]

        response = "Use /start to begin, {}".format(first_name)

        if "start" in message:
            response = (
                "Hello {}! I support  the following commands:\n"
                "/omloop for number of days to the start of the season\n"
                "/subscribe for a number of events you can subscribe to!\n"
                .format(first_name)
            )

        if "omloop" in message:
            omloop = datetime.date(2018, 2, 28)
            response = "Omloop is in {} days!".format((omloop - datetime.date.today()).days)

        if "subscribe" in message:
            command = "/subscribe"
            if message == command:
                response = (
                    "You can '/subscribe <event>' to the following events:\n"
                    "  omloop\n\n"
                    "Once you are subscribed, you will get a daily message about this event."
                )
            else:
                argument = str.replace(message, command + " ", 1)
                print(argument)

                if argument == "omloop":
                    response = (
                        "You are now subscribed to omloop."
                    )
                else:
                    response = (
                        "'{}' is not a valid subscription option.".format(argument)
                    )

        print(message, response)

        data = {
            "text": response.encode("utf8"),
            "chat_id": chat_id
        }
        url = BASE_URL + "/sendMessage"
        requests.post(url, data)

    except Exception as e:
        print(e)

    return {"statusCode": 200}
