import cv2
import socket
import numpy as np
import pyfakewebcam
from time import sleep
import signal
import webcam.utils as utils

WIDTH = 1600
HEIGHT = 900
SCALE = 3

EXIT_REQUESTED = False

def close(a=None, b=None):
  global EXIT_REQUESTED
  EXIT_REQUESTED = True

signal.signal(signal.SIGINT, close)
signal.signal(signal.SIGTERM, close)

SOCKET_FILE = '/tmp/partitioner.sock'
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

vc = cv2.VideoCapture(0)
vc.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH // SCALE)
vc.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT // SCALE)

width = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))

camera = pyfakewebcam.FakeWebcam('/dev/video2', SCALE*width, SCALE*height)

for i in range(5):
  if vc.isOpened():
    break
  print(f'\rWaiting for webcam, {4-i}...', end='')
  sleep(2)
else:
  print('Couldn\'t open webcam.')
  exit(2)

try:
  cv2.namedWindow('mask')
  bg = cv2.imread('./assets/star-destroyer.jpg')
  bg = cv2.resize(bg, (SCALE*width, SCALE*height))
  sock.connect(SOCKET_FILE)

  while not EXIT_REQUESTED:
    rval, frame = vc.read()
    _, data = cv2.imencode('.jpg', frame)

    sock.sendall(data.tobytes())

    recv = []
    accumulated = 0
    while accumulated < width*height:
      r = sock.recv(4096)
      accumulated += len(r)
      recv.append(r)

    mask = np.frombuffer(b''.join(recv), dtype=np.uint8)
    mask = mask.reshape((height, width))
    mask = cv2.resize(mask, (SCALE*width, SCALE*height))
    mask = utils.smoothen_mask(mask)

    frame = cv2.resize(frame, (SCALE*width, SCALE*height))
    frame = utils.hologram(frame)

    transparency = 0.9
    for c in range(frame.shape[2]):
      frame[:, :, c] = mask*frame[:, :, c] + (1-transparency*mask)*bg[:, :, c]

    cv2.imshow('mask', frame)

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    camera.schedule_frame(frame)

    cv2.waitKey(3)
finally:
  cv2.destroyWindow('mask')
  sock.close()
