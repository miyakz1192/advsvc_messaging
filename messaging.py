# -*- coding: utf-8 -*-

import pika


class MessagingBase:
    def __init__(self):
        self.ip = os.environ["LLM_SVC_QUEUE_SERVER_IP"]
        self.port = os.environ["LLM_SVC_QUEUE_SERVER_PORT"]
        self.path = os.environ["LLM_SVC_QUEUE_SERVER_PATH"]
        self.user = os.environ["LLM_SVC_QUEUE_SERVER_USER"]
        self.passwd = os.environ["LLM_SVC_QUEUE_SERVER_PASSWD"]
        self.credentials = pika.PlainCredentials(user, passwd)
        self.queue = None

    def connect(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(self.ip, self.port,
                                      self.path, self.credentials)
        )
        self.channel = connection.channel()

    def connect_and_basic_publish(self, message, queue=self.queue):
        self.connect()
        self.channel.queue_declare(queue=queue)
        self.channel.basic_publish(exchange='', routing_key=queue, body=data)
        self.connection.close()

    def connect_and_basic_get(self, queue=self.queue):
        self.connect()
        # basic_getを使用してメッセージを一度だけ取り出す
        method_frame, header_frame, body = channel.basic_get(queue=queue)

        if method_frame:
            # メッセージが存在する場合はコールバックを呼び出す
            self.basic_get_callback(channel, method_frame, None, body)
        else:
            print("No message in the queue")

    def basic_get_callback(self, channel, method, properties, body):
        # conclete class must overwride this method
        pass


class RecoderServiceMessaging(MessagingBase):
    def __init__(self):
        super().__init()__
        self.queue = "recorder"
