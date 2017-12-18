import datetime
import json
import os
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import boto3
import requests

TOKEN = os.environ['TELEGRAM_TOKEN']
STAGE = os.environ['PROVIDER_STAGE']
SERVICE = os.environ['SERVICE']
BASE_URL = "https://api.telegram.org/bot{}".format(TOKEN)
events = [
    "omloop",
]

# Get the service resource.
dynamodb = boto3.resource('dynamodb')
t_subscriptions = dynamodb.Table("{}-{}-subscriptions".format(SERVICE, STAGE))


def send_message(response, chat_id):
    data = {
        "text": response.encode("utf8"),
        "chat_id": chat_id
    }

    url = BASE_URL + "/sendMessage"
    requests.post(url, data)


def unsubscribe_event(message, command, user_id):
    print("Command: " + command)

    if message == command:
        event_text = ""
        for event in events:
            event_text = event_text + "  {}\n".format(event)

        response = (
            "You can '/unsubscribe <event>' to the following events:\n"
            "{}\n"
            "Once you are unsubscribed, you will no longer get a daily message about the event."
            .format(event_text)
        )
    else:
        print("Message: " + message)
        event = message.replace("{} ".format(command), "", 1)
        print("Event: " + event)

        if event in events:
            subscribed = check_subscribed(user_id, event)

            if subscribed:
                t_subscriptions.delete_item(
                    Item={
                        'user': user_id,
                        'event': event,
                    }
                )
                response = "You are now unsubscribed to '{}'.".format(event)
            else:
                response = "You are not subscribed to '{}'!".format(event)
        else:
            response = "'{}' is not a valid unsubscription option.".format(event)

    return response


def subscribe_event(message, command, user_id):
    print("Command: " + command)

    if message == command:
        event_text = ""
        for event in events:
            event_text = event_text + "  {}\n".format(event)

        response = (
            "You can '/subscribe <event>' to the following events:\n"
            "{}\n"
            "Once you are subscribed, you will get a daily message about the event."
            .format(event_text)
        )
    else:
        print("Message: " + message)
        event = message.replace("{} ".format(command), "", 1)
        print("Event: " + event)

        if event in events:
            subscribed = check_subscribed(user_id, event)

            if subscribed:
                response = "You are already subscribed to '{}'!".format(event)
            else:
                t_subscriptions.put_item(
                    Item={
                        'user': user_id,
                        'event': event,
                        'subscribed': True,
                    }
                )
                response = "You are now subscribed to '{}'.".format(event)
        else:
            response = "'{}' is not a valid subscription option.".format(event)

    return response


def check_subscribed(user_id, event):
    response = t_subscriptions.get_item(
        Key={
            'user': user_id,
            'event': event,
        }
    )

    try:
        subscribed = response['Item']['subscribed']
    except:
        subscribed = False

    return subscribed


def hello(event, context):
    try:
        data = json.loads(event["body"])
        response = False

        # Exit when there is no message text. Join events, and such.
        try:
            data["message"]["text"]
        except:
            print(data)
            return {"statusCode": 200}
        else:
            message = str(data["message"]["text"])

        # Exit when a message is form a bot.
        if data["message"]["from"]["is_bot"]:
            print(data)
            return {"statusCode": 200}

        chat_id = data["message"]["chat"]["id"]
        first_name = data["message"]["from"]["first_name"]
        user_id = data["message"]["from"]["id"]

        if "start" in message:
            response = (
                "Hello {}! I support  the following commands:\n"
                "/omloop for number of days to the start of the season\n"
                "/subscribe for a number of events you can subscribe to\n"
                "/unsubscribe for events you have subscribed to\n"
                .format(first_name)
            )

        command = "/omloop"
        if command in message:
            print("Command: " + command)
            omloop = datetime.date(2018, 2, 28)
            response = "Omloop is in {} days!".format((omloop - datetime.date.today()).days)

        command = "/subscribe"
        if command in message:
            response = subscribe_event(message, command, user_id)

        command = "/unsubscribe"
        if command in message:
            response = unsubscribe_event(message, command, user_id)

        if response:
            print("Message: {}, Response: {}".format(message, response))
            send_message(response, chat_id)

    except Exception as e:
        print(e)

    return {"statusCode": 200}
