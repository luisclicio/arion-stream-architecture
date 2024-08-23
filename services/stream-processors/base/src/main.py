import os

from src.helpers.logger import get_logger
from src.libs.stream import StreamReceiver

if __name__ == '__main__':
    SENDER_URI = os.getenv('SENDER_URI')

    stream_receiver = StreamReceiver(SENDER_URI).start()
    logger = get_logger('Main')

    try:
        while True:
            sender_id, image = stream_receiver.receive()

            if image is None:
                break

            # Process the image
            print('Received image from sender:', sender_id)
    except (KeyboardInterrupt, SystemExit):
        logger.error('Exit due to interrupt')
    except Exception as error:
        logger.error('Error with no exception handler:', error)
    finally:
        stream_receiver.stop()
