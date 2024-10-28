import os
import socket

from src.helpers.exceptions import SigIntException, SigTermException
from src.helpers.logger import get_logger
from src.libs.stream import StreamSender

if __name__ == '__main__':
    PORT = int(os.getenv('SENDER_PORT', 5000))
    SOURCE_URI = os.getenv('SOURCE_URI')
    SENDER_ID = socket.gethostname()

    logger = get_logger('Main')

    stream_sender = StreamSender(SOURCE_URI, PORT, SENDER_ID)

    try:
        stream_sender.start()
    except (KeyboardInterrupt, SystemExit, SigTermException, SigIntException):
        logger.error('Exiting due to interrupt...')
    except Exception as error:
        logger.error('Error with no exception handler:', error)
    finally:
        stream_sender.stop()
        logger.info('Stream processor stopped')
