import os
import socket

from src.helpers.exceptions import SigIntException, SigTermException
from src.helpers.logger import get_logger
from src.libs.stream import Stream, StreamSender

if __name__ == '__main__':
    PORT = int(os.getenv('SENDER_PORT', 5000))
    SOURCE_URI = os.getenv('SOURCE_URI')
    SENDER_ID = socket.gethostname()

    logger = get_logger('Main')

    stream = Stream(SOURCE_URI)
    stream_sender = StreamSender(stream, PORT, SENDER_ID)

    try:
        stream.start()
        stream_sender.start()
    except (KeyboardInterrupt, SystemExit, SigTermException, SigIntException):
        logger.error('Exiting due to interrupt...')
    except Exception as error:
        logger.error('Error with no exception handler:', error)
    finally:
        stream_sender.stop()
        stream.stop()
        logger.info('Stream adapter stopped')
