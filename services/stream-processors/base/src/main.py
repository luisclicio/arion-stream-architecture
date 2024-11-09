import os
import socket

from src.helpers.exceptions import SigIntException, SigTermException
from src.helpers.logger import get_logger
from src.libs.stream import StreamProcessorController, StreamReceiver, StreamSender
from src.services.broker import BROKER_CONNECTION_URI, get_broker_connection
from src.services.handler import StreamHandler

if __name__ == '__main__':
    SENDER_URI = os.getenv(
        'SENDER_URI'
    )  # URI of one stream adapter or another stream processor

    PORT = int(
        os.getenv('SENDER_PORT', 5000)
    )  # Port for the stream sending from this stream processor
    SENDER_ID = (
        socket.gethostname()
    )  # ID for the stream sending from this stream processor

    logger = get_logger('Main')

    logger.info('Starting stream processor...')

    broker_connection = get_broker_connection(BROKER_CONNECTION_URI)

    stream_receiver = StreamReceiver(SENDER_URI).start()
    stream_handler = StreamHandler(broker_connection)
    stream_sender = StreamSender(PORT, SENDER_ID)
    stream_processor_controller = StreamProcessorController(
        stream_receiver, stream_handler, stream_sender
    )

    try:
        stream_processor_controller.start()
    except (KeyboardInterrupt, SystemExit, SigTermException, SigIntException):
        logger.error('Exiting due to interrupt...')
    except Exception as error:
        logger.error('Error with no exception handler:', error)
    finally:
        stream_processor_controller.stop()

        if broker_connection.is_open:
            broker_connection.close()

        logger.info('Stream processor stopped')
