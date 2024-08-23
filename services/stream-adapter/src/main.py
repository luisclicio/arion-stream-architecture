import os
import socket

from src.libs.stream import StreamSender

if __name__ == '__main__':
    PORT = int(os.getenv('SENDER_PORT', 5000))
    SOURCE_URI = os.getenv('SOURCE_URI')
    SENDER_ID = socket.gethostname()

    stream_sender = StreamSender(SOURCE_URI, PORT, SENDER_ID)
    stream_sender.start()
