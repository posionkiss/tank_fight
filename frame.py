import cv2
import numpy as np

img = cv2.imread('source/kamui.png')
# imgGray = cv2.imread('source/gun.png', 0)
# img = cv2.resize(img, (20, 20))
img = cv2.cvtColor(img, cv2.COLOR_BGR2BGRA)
channel1 = img[:, :, 0]
channel2 = img[:, :, 1]
channel3 = img[:, :, 2]
channel4 = img[:, :, 3]

channel4[channel1>240] = 0  # 设置透明度

# channel1[:, :] = 255
# channel2[:, :] = 255
# channel3[:, :] = 255
# img[:, :, 0] = channel1
# img[:, :, 1] = channel2
# img[:, :, 2] = channel3
img[:, :, 3] = channel4
# img[0, :] = 0
# img[33, :] = 0
# img[:, 0, :] = 0
# img[:, 13, :] = 0
cv2.imwrite('source/kamui2.png', img)

# img = cv2.imread('source/gun1.png')
# img[0, :] = 0
# img[33, :] = 0
# img[:, 0, :] = 0
# img[:, 13, :] = 0
# cv2.imwrite('source/gun1.png', img)
