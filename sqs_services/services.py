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
        # import ipdb
        # ipdb.set_trace()
        try:
            queue.send_message(QueueUrl=url, MessageBody=msg)
            return True

        except Exception as exp:
            raise ValueError('Could not send message to SQS')


class SnsService:
    def __init__(self, json_data):
        self.json_data = json_data

    def push(self, arn, attribute):
        sns = boto3.client('sns',
                           region_name=settings.AWS_REGION_VIRGINIA,
                           aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)

        msg = json.dumps(self.json_data)
        try:
            if attribute is None:
                sns.publish(TopicArn=arn,
                            Message=msg
                            )
            else:

                sns.publish(TopicArn=arn,
                            Message=msg,
                            MessageAttributes=attribute)

            return True

        except Exception as exp:
            raise ValueError(str(exp))

    def make_attributes(self, entity=None, type=None, status=None):

        attributes = {}
        if entity:
            attributes["entity"] = {
                "DataType": "String",
                "StringValue": entity
            }
        if type:
            attributes["type"] = {
                "DataType": "String",
                "StringValue": type
            }
        if status:
            attributes["status"] = {
                "DataType": "String",
                "StringValue": status
            }
        return attributes