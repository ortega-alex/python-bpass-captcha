import cv2, time
import numpy as np
from pwn import *


p1 = log.progress("IMG")
p1.status("cargando la imagen")


img = cv2.imread('./captcha.jpg', 0)
_, blackAndWhite = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY_INV)

p1.success("imagen cargada")
time.sleep(1)

nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(blackAndWhite, None, None, None, 8, cv2.CV_32S)
sizes = stats[1:, -1] #get CC_STAT_AREA component
img2 = np.zeros((labels.shape), np.uint8)

p2 = log.progress("Remplasar puntos")
p2.status("Buscando y remplasando todos los puntos de la imagen")

for i in range(0, nlabels - 1):
    if sizes[i] >= 50:   #filter small dotted regions
        img2[labels == i + 1] = 255

p2.success("Finalizo el proseso de remplasar los puntos")
time.sleep(1)

res = cv2.bitwise_not(img2)
cv2.imwrite('captcha.jpg', res)