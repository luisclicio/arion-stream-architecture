import os

import pika

BROKER_CONNECTION_URI = os.getenv('BROKER_RABBITMQ_CONNECTION_URI')
BROKER_EXCHANGE_NAME = os.getenv('BROKER_RABBITMQ_EXCHANGE_NAME')


def get_broker_connection(broker_connection_uri: str) -> pika.BlockingConnection:
    return pika.BlockingConnection(pika.URLParameters(broker_connection_uri))
