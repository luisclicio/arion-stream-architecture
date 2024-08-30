import os

from src.helpers.exceptions import SigIntException, SigTermException
from src.helpers.logger import get_logger
from src.libs.stream import StreamReceiver, StreamReceiverController
from src.services.handler import StreamHandler

if __name__ == '__main__':
    SENDER_URI = os.getenv('SENDER_URI')

    logger = get_logger('Main')

    logger.info('Starting stream processor...')

    stream_receiver = StreamReceiver(SENDER_URI).start()
    stream_handler = StreamHandler()
    stream_receiver_controller = StreamReceiverController(
        stream_receiver, stream_handler
    )

    try:
        stream_receiver_controller.start()
    except (KeyboardInterrupt, SystemExit, SigTermException, SigIntException):
        logger.error('Exiting due to interrupt...')
    except Exception as error:
        logger.error('Error with no exception handler:', error)
    finally:
        stream_receiver_controller.stop()
        logger.info('Stream processor stopped')
