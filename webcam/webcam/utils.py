import cv2
import numpy as np
from time import time


def shift_img(img, dx, dy):
  img = np.roll(img, dy, axis=0)
  img = np.roll(img, dx, axis=1)

  if dy > 0:
    img[:dy, :] = 0
  elif dy < 0:
    img[dy:, :] = 0

  if dx > 0:
    img[:, :dx] = 0
  elif dx < 0:
    img[:, dx:] = 0

  return img


def smoothen_mask(mask):
  mask = cv2.dilate(mask, np.ones((10,10), np.uint8) , iterations=1)
  mask = cv2.blur(mask.astype(float), (30,30))
  return mask


def hologram(frame):
  holo = cv2.applyColorMap(frame, cv2.COLORMAP_WINTER)

  bandLength, bandGap = 2, 3
  for y in range(holo.shape[0]):
    if y % (bandLength+bandGap) < bandLength:
      holo[y,:,:] = holo[y,:,:] * np.random.uniform(0.1, 0.3)

  t = time() * 10 % 4

  holo2 = cv2.addWeighted(holo, 0.2, shift_img(holo.copy(), 5, int(5*t)), 0.8, 0)
  holo2 = cv2.addWeighted(holo2, 0.4, shift_img(holo.copy(), -5, -5), 0.6, 0)

  holo_done = cv2.addWeighted(frame, 0.5, holo2, 0.6, 0)

  return holo_done
