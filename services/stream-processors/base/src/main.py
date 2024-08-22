import os

import imagezmq

SENDER_URI = os.getenv('SENDER_URI')

image_hub = imagezmq.ImageHub(open_port=f'tcp://{SENDER_URI}', REQ_REP=False)

while True:
    sender_id, frame = image_hub.recv_image()

    if frame is None:
        break

    print('Received data from sender:', sender_id)

image_hub.close()
