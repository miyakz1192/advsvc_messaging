# -*- coding: utf-8 -*-

import pika
import sys
import os
from record import *


class MessagingBase:
    def __init__(self):
        self.ip = os.environ["LLM_SVC_QUEUE_SERVER_IP"]
        self.port = os.environ["LLM_SVC_QUEUE_SERVER_PORT"]
        self.path = os.environ["LLM_SVC_QUEUE_SERVER_PATH"]
        self.user = os.environ["LLM_SVC_QUEUE_SERVER_USER"]
        self.passwd = os.environ["LLM_SVC_QUEUE_SERVER_PASSWD"]
        self.credentials = pika.PlainCredentials(self.user, self.passwd)
        self.queue = None

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.ip, self.port,
                                      self.path, self.credentials)
        )
        self.channel = self.connection.channel()

    def connect_and_basic_publish_record(self, record):
        self.connect_and_basic_publish(RecordBase.to_byte(record))

    def connect_and_basic_publish(self, message):
        queue = self.queue
        self.connect()
        self.channel.queue_declare(queue=queue)
        self.channel.basic_publish(exchange='',
                                   routing_key=queue, body=message)
        self.connection.close()

    def connect_and_basic_get(self):
        queue = self.queue
        self.connect()
        # basic_getを使用してメッセージを一度だけ取り出す
        method_frame, header_frame, body = self.channel.basic_get(queue=queue)

        if method_frame:
            # メッセージが存在する場合はコールバックを呼び出す
            return self.basic_get_callback(self.channel, method_frame,
                                           None, body)
        else:
            print("No message in the queue")
            return None

    def connect_and_basic_get_record(self):
        byte_data = self.connect_and_basic_get()
        return RecordBase.from_byte(byte_data)

    def basic_get_callback(self, channel, method, properties, body):
        channel.basic_ack(delivery_tag=method.delivery_tag)
        return body


class RecoderServiceMessaging(MessagingBase):
    def __init__(self):
        super().__init__()
        self.queue = "recorder"
