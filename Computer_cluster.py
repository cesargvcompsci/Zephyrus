import cv2
import time
thres = 0.60 # Threshold to detect object

import numpy as np
from Tests.clustering_test import box_centers, cluster_by_distance

cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
#cap = cv2.VideoCapture('test1.mp4')
cap = cv2.VideoCapture(0)


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

while True:
    success,img = cap.read()
    classIds, confs, bbox = net.detect(img,confThreshold=thres)
    #print(classIds,bbox)

    if len(classIds) != 0:
        cluster_labels, m = cluster_by_distance(box_centers(bbox), 150)
        print("Number of clusters:", m)

        for classId, confidence,box, cluster in zip(classIds.flatten(),confs.flatten(),bbox,cluster_labels):
            if True:#classId == 1:
                cv2.rectangle(img,box,color=colors_list[cluster-1].tolist(),thickness=2)
                cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30),
                cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
    imS = cv2.resize(img,(960, 540))
    cv2.imshow('Output',imS)
    if cv2.waitKey(5) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
