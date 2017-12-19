import datetime
import json
import os
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

def get_chat_ids(event):
    response = t_subscriptions.batch_get_item(
        RequestItems={
            'users': {
                'Keys': [
                    {
                        'event': event
                    },
                ],
                #'ConsistentRead': True
            }
        },
        #ReturnConsumedCapacity='TOTAL'
    )

    print (response)
    print (response['Responses'])

    return []


def send_daily_messages():
    chat_ids = get_chat_ids("omloop")

    for chat_id in chat_ids:
        send_message(omloop(), chat_id)

def main(event, context):
    send_daily_messages()

if __name__ == "__main__":
    main(False, False)
