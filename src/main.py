#import tracemalloc
#tracemalloc.start()

import cv2
import time
import numpy as np

thres = 0.60 # Threshold to detect object

from Fan_Simulation import Fan_Simulation
from Double_fan import Double_Fan_Simulation
from Trackers import Trackers

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 540

#@profile
def main():
    cv2.namedWindow('Output', cv2.WINDOW_NORMAL)
    #cap = cv2.VideoCapture('../test1.mp4')
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)

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

    trackers = Trackers(200)
    fan = Double_Fan_Simulation(480, trackers)

    tick = 0

    while True:
        start = time.time()
        #img = cv2.imread("Tests/group.jpg")
        success,img = cap.read()

        if tick % 8 == 0:
            classIds, confs, bbox = net.detect(img,confThreshold=thres)
            # Keep boxes of people only, classIds == 1
            if len(classIds) > 0:
                bbox=bbox.astype(np.int16)
                bbox = bbox[classIds==1]
            #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            trackers.begin_track(img, bbox)
        else:
            #img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            bbox = trackers.update(img)
        
        if len(bbox) != 0:
            track_ids, cluster_labels, m, cluster_centers = trackers.cluster()

            for boxID, box, cluster in zip(trackers.bbox.keys(),trackers.bbox.values(),cluster_labels):
                cv2.rectangle(img, box,color=colors_list[cluster].tolist(),thickness=2)
                cv2.putText(img, "Person {}".format(boxID), (box[0]+10,box[1]+30),
                            cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)

                for c, center in enumerate(cluster_centers):
                    cv2.circle(img, center.astype(np.int16), 5, colors_list[c].tolist(), -1)

            # simulated fan's movement
            A_cluster, B_cluster = fan.update_movement(track_ids, cluster_labels, m, cluster_centers, 1)

            if A_cluster != None:
                cv2.circle(img, (fan.A_pos, 200), 25, (0,255,255), 2)
                cv2.circle(img, (fan.A_pos, 200), 23, colors_list[A_cluster].tolist(), 2)
            if B_cluster != None:
                cv2.circle(img, (fan.B_pos, 340), 25, (0,255,255), 2)
                cv2.circle(img, (fan.B_pos, 340), 23, colors_list[B_cluster].tolist(), 2)

        #imS = cv2.resize(img,(960, 540))
        cv2.imshow('Output',img)
        
        key_press = cv2.waitKey(5)
        if key_press == ord('q'):
            break
        if key_press == ord('s'):
            cv2.imwrite('test_img.jpg', imS)

        tick += 1
        #if (tick==10):
        #    break
        #print(time.time()-start)

    cap.release()
    cv2.destroyAllWindows()

main()

#print(tracemalloc.get_traced_memory())
#tracemalloc.stop()