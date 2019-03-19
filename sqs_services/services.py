import boto3
from django.conf import settings
from rest_framework.utils import json


class SqsService:
    def __init__(self, json_data):
        self.json_data = json_data

    def push(self, queue_name):
        sqs = boto3.resource('sqs',
                             region_name=settings.AWS_REGION_NAME,
                             aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                             aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        url = f"{settings.TREASURY_SQS_URL}{queue_name}"
        msg = json.dumps(self.json_data)
        print("SQS Services MSG!!!!")
        print(msg)
        queue = sqs.get_queue_by_name(QueueName=queue_name)

        try:
            queue.send_message(QueueUrl=url, MessageBody=msg)
            return True

        except Exception as exp:
            raise ValueError('Could not send message to SQS')
