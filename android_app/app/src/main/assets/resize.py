import cv2
from utilsm import helpers as H
img = H.cv2_resize_image(cv2.imread("test1_full.jpg"), 0.25)
cv2.imwrite("test1.jpg", img)

img = H.cv2_resize_image(cv2.imread("test2_full.jpg"), 0.25)
cv2.imwrite("test2.jpg", img)

img = H.cv2_resize_image(cv2.imread("test3_full.jpg"), 0.25)
cv2.imwrite("test3.jpg", img)