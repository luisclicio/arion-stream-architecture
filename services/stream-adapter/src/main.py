import os
import socket
import time

import imagezmq
from vidgear.gears import VideoGear

# from vidgear.gears.helper import reducer

PORT = int(os.getenv('SENDER_PORT', 5000))

stream = VideoGear(source=os.getenv('SOURCE_URI')).start()
sender = imagezmq.ImageSender(connect_to=f'tcp://*:{PORT}', REQ_REP=False)
sender_id = socket.gethostname()

print('Sender ready to transmit images')

while True:
    frame = stream.read()

    if frame is None:
        break

    # frame = reducer(frame, percentage=30)
    sender.send_image(sender_id, frame)
    time.sleep(0.1)

stream.stop()
sender.close()
