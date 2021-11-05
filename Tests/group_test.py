import cv2 as cv
import sys
import numpy as np
import imutils

def box_centers(boxes):
    '''Args:
        boxes: array of [x1,y1,x2,y2], where [x1,y1] is the
        top left corner and x2, y2] is the bottom right corner'''
    return np.array([[(x1+x2)/2, (y1+y2)/2] for [x1,y1,x2,y2] in boxes])

# tests stitching two people and checking for people

hog = cv.HOGDescriptor()
hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())

img_a = cv.imread("group_a.jpg")
#img_a = cv.cvtColor(img_a, cv.COLOR_BGR2GRAY)
img_a = imutils.resize(img_a, width=img_a.shape[0]//2)
#cv.imshow('img_a', img_a)
#cv.waitKey(0)
img_b = cv.imread("group_b.jpg")
#img_b = cv.cvtColor(img_b, cv.COLOR_BGR2GRAY)
img_a = imutils.resize(img_a, width=img_b.shape[0]//2)

stitcher = cv.Stitcher.create()
result, pano = stitcher.stitch([img_a,img_b])
pano = imutils.resize(pano, width=pano.shape[0]//4)

#cv.imshow('pano', pano)
cv.waitKey(0)

boxes, weights = hog.detectMultiScale(pano, winStride=(8,8))

for (x, y, w, h) in boxes:
    cv.rectangle(pano, (x, y, w, h), (0,255,0), 2)

#display frame
cv.imshow('frame', pano)
#cv2.imwrite('test_img.jpg', pano)
cv.waitKey(0)

cv.destroyAllWindows()