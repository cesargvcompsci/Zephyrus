import cv2 as cv
import sys
import numpy as np

hog = cv.HOGDescriptor()
hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())

cap = cv.VideoCapture(0)
if not cap.isOpened():
    print("Cannot open camera")
    exit()
while True:
    ret, frame = cap.read()
    if not ret:
        print("can't receive frame, exiting")
        break
    
    frame = cv.resize(frame, (640,480))
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    boxes, weights = hog.detectMultiScale(frame, winStride=(8,8))
    boxes = np.array([[x,y,x+w,y+h] for (x,y,w,h) in boxes])

    for (x1, y2, x1, y2) in boxes:
        cv.rectangle(frame, (x1, y1), (x1, y2), (0,255,0), 2)

    #display frame
    cv.imshow('frame', frame)
    if cv.waitKey(5) == ord('q'):
        break

cap.release()
cv.destroyAllWindows()