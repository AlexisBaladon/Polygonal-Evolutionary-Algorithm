import cv2
import numpy as np

img = cv2.imread("img/womhd.jpg")
blurred_img = cv2.GaussianBlur(img, (21, 21), 0)
#detects the background and creates mask from rgb image
backSub = cv2.createBackgroundSubtractorMOG2()
mask = backSub.apply(blurred_img)

masked_img = cv2.bitwise_and(img, img, mask=mask)


#mask = np.zeros((512, 512, 3), dtype=np.uint8)
#mask = cv2.circle(mask, (258, 258), 100, (255, 255,255), -1)
#


#out = np.where(mask==(255, 255, 255), img, blurred_img)
cv2.imwrite("./out.png", mask)
cv2.imwrite("./out2.png", masked_img)