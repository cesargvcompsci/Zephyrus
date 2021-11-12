import imutils
import cv2
import time

import cv2
import time
thres = 0.60 # Threshold to detect object

import numpy as np
from Tests.clustering_test import box_centers, cluster_boxes
from Tests.fan_position_sim import Fan_Simulation

class Trackers:
    '''A class to hold multiple trackers'''
    def __init__(self, frame, bboxes):
        self.bboxes = bboxes
        self.trackers = tuple(cv2.TrackerKCF_create() for b in bboxes)
        for i in range(len(self.trackers)):
            self.trackers[i].init(frame, bboxes[i])

    def update(self, frame):
        success = np.zeros(len(self.trackers))
        bboxes = self.bboxes
        for i,tracker in enumerate(self.trackers):
            success[i], bboxes[i] = tracker.update(frame)
        
        return success, bboxes


cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
#cap = cv2.VideoCapture('test1.mp4')
cap = cv2.VideoCapture(0)

# KCF looks like a good one
#tracker = cv2.TrackerKCF_create()

classNames= []
classFile = 'coco.names'
with open(classFile,'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

configPath = 'ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
weightsPath = 'frozen_inference_graph.pb'

net = cv2.dnn_DetectionModel(weightsPath,configPath)
net.setInputSize(320,320)
net.setInputScale(1.0/ 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# Generate a lot of different colors for testing
colors_list = np.random.randint(25,255,(30,3))

Fan_sim = Fan_Simulation(480)

while True:
    success,img = cap.read()
    classIds, confs, bbox = net.detect(img,confThreshold=thres)

    trackers = Trackers(img, bbox[classIds==1]) #All boxes with humans

    if len(classIds) != 0:
        clabels, m, ccenters, cboxes = cluster_boxes(bbox, 150)

        for classId, confidence,box, cluster in zip(classIds.flatten(),confs.flatten(),bbox,clabels):
            if classId == 1:
                cv2.rectangle(img,box,color=colors_list[cluster].tolist(),thickness=2)
                cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

                for c, center in enumerate(ccenters):
                    cv2.circle(img, center.astype(np.int16), 5, colors_list[c].tolist(), -1)
    imS = cv2.resize(img,(960, 540))
    cv2.imshow('Output',imS)

    # Initial test for the simulated fan's movement
    ccounts = np.zeros(m)
    for c in clabels:
        ccounts[c] += 1
    Fan_sim.init_oscillation(ccounts)

    # Track for 2000 frames = 5ms*1000 = 10 seconds
    for f in range(2000):
        success,img = cap.read()
        
        track_successes, bbox = trackers.update(img)
        clabels, m, ccenters, cboxes = cluster_boxes(bbox, 150)

        for classId, confidence,box, cluster in zip(classIds.flatten(),confs.flatten(),bbox,clabels):
            if classId == 1:
                cv2.rectangle(img,box,color=colors_list[cluster].tolist(),thickness=2)
                cv2.putText(img,classNames[classId-1].upper()+" (TRACKING)",(box[0]+10,box[1]+30),
                cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

                for c, center in enumerate(ccenters):
                    cv2.circle(img, center.astype(np.int16), 5, colors_list[c].tolist(), -1)
        
        Fan_sim.update_movement(ccenters, 5)
        cv2.circle(img, (Fan_sim.position, 270), 25, (0,255,255), 2)

        imS = cv2.resize(img,(960, 540))
        cv2.imshow('Output',imS)

        key_press = cv2.waitKey(5)
        if key_press == ord('q'):
            break
    
    if key_press == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

