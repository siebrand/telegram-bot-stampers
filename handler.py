import json
import os
import re
import sys

here = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(here, "./vendored"))

import boto3
import requests
from omloop import omloop

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


def get_event_from_message(message, command):
    event_filters = [
        "@{}".format(SERVICE),
        "{}".format(command),
    ]

    # print (event_filters)

    for filter in event_filters:
        # print (message)
        message = message.replace(filter, "", 1).strip()

    return message


def send_message(response, chat_id):
    data = {
        "text": response.encode("utf8"),
        "chat_id": chat_id
    }

    url = BASE_URL + "/sendMessage"
    requests.post(url, data)


def unsubscribe_event(message, command, user_id, user_name):
    event = get_event_from_message(message, command)

    if event == "":
        event_text = ""
        for event in events:
            event_text = event_text + "  {} {}\n".format(command, event)

        response = (
            "You can '{} <event>' to the following events:\n"
            "{}\n"
            "Once you are unsubscribed, you will no longer get a daily message about the event."
                .format(command, event_text)
        )
    else:
        print("Message: " + message)

        if event in events:
            subscribed = check_subscribed(user_id, event)

            if subscribed["subscribed"]:
                subscriptions = subscribed["subscriptions"]
                del subscriptions[user_id]
                print(subscriptions)

                t_subscriptions.delete_item(
                    Key={
                        "dummy": 1,
                        "event": event,
                        "subscriptions": subscriptions,
                    }
                )

                response = "You are now unsubscribed from '{}', {}.".format(event, user_name)
            else:
                response = "You are not subscribed to '{}', {}!".format(event, user_name)
        else:
            response = "'{}' is not a valid unsubscription option.".format(event)

    return {
        "response": response,
        "subscribed": subscribed,
    }


def subscribe_event(message, command, user_id, user_name, chat_id):
    event = get_event_from_message(message, command)

    if event == "":
        event_text = ""
        for event in events:
            event_text = event_text + "  {} {}\n".format(command, event)

        response = (
            "You can '{} <event>' to the following events:\n"
            "{}\n"
            "Once you are subscribed, you will get a daily message about the event."
                .format(command, event_text)
        )
    else:
        print("Message: " + message)

        if event in events:
            subscribed = check_subscribed(user_id, event)

            if subscribed["subscribed"]:
                response = "You are already subscribed to '{}', {}!".format(event, user_name)
            else:
                subscriptions = subscribed["subscriptions"]
                subscriptions[user_id] = chat_id
                t_subscriptions.update_item(
                    Item={
                        "dummy": 1,
                        "event": event,
                        "subscriptions": subscriptions,
                    }
                )
                response = "You are now subscribed to '{}', {}.".format(event, user_name)
        else:
            response = "'{}' is not a valid subscription option.".format(event)

    return response


def check_subscribed(user_id, event):
    response = t_subscriptions.get_item(
        Key={
            'event': event,
        }
    )

    try:
        subscribed = user_id in response['Item']['subscribed'].keys()
        print(response['Item'])
    except:
        subscribed = False

    return {
        "subscribed": subscribed,
        "subscriptions": response['Item']['subscribed'],
    }


def incoming(event, context):
    try:
        data = json.loads(event["body"])
        response = False

        print(data)

        # Exit when there is no message text. Join events, and such.
        try:
            data["message"]["text"]
        except:
            print(data)
            return {"statusCode": 200}
        else:
            message = str(data["message"]["text"]).strip()

        # Exit when a message is form a bot.
        if data["message"]["from"]["is_bot"]:
            print(data)
            return {"statusCode": 200}

        chat_id = data["message"]["chat"]["id"]
        chat_type = data["message"]["chat"]["type"]
        first_name = data["message"]["from"]["first_name"]
        user_id = data["message"]["from"]["id"]

        if "start" in message:
            response = (
                "Hello {}! I support  the following commands:\n"
                "/omloop for number of days until Omloop Het Nieuwsblad\n"
                "/subscribe for a number of events you can subscribe to (only in private chat)\n"
                "/unsubscribe for events you have subscribed to (only in private chat)\n"
                .format(first_name)
            )

        command = "/omloop"
        pattern = re.compile("^{}".format(command))
        if pattern.match(message):
            print("Command: " + command)
            response = omloop()

        command = "/subscribe"
        pattern = re.compile("^{}".format(command))
        if pattern.match(message):
            if chat_type == "private":
                response = subscribe_event(message, command, user_id, first_name, chat_id)
            else:
                response = "This command is only available in a private chat."

        command = "/unsubscribe"
        pattern = re.compile("^{}".format(command))
        if pattern.match(message):
            if chat_type == "private":
                response = unsubscribe_event(message, command, user_id, first_name)
            else:
                response = "This command is only available in a private chat."

        if response:
            print("Message: {}, Response: {}".format(message, response))
            send_message(response, chat_id)

    except Exception as e:
        print(e)

    return {"statusCode": 200}
