import imutils
import cv2
#import dlib
import numpy as np

tracker_create = cv2.TrackerCSRT_create

def same_object(frame, A, B):
    '''Given two bounding boxes A and B, tuples [x,y,w,h],
    determine whether they are the same object'''
    #TODO
    # ideas: check overlap of bounding boxes, and also check similarity of image
    return False

class Trackers:
    '''A class to hold multiple trackers.

    Attributes:
        trackers(dict{int, cv2.Tracker}): holds all Trackers, indexed by a specific ID
        bboxes (dict{int : numpy array of shape (4,)}): bboxes for each tracked object, indexed by ID
    '''

    def __init__(self):
        self._ID_count = 0 #Assign unique IDs to new objects
        self.bboxes = {}
        self.trackers = {}

    #TODO: Make tracking more robust to failure in 1 or 2 frames of object tracking
    def begin_track(self, frame, bbox):
        '''Matches bboxes to current trackers or create new ones if not already tracked'''
        new_trackers = {}
        new_bboxes = {}
        #TODO add robustness to items randomly failing to be detected
        for new_box in bbox:
            # Iterate through currently tracked bboxes
            for i, box in self.bboxes.items():
                if i not in new_trackers and same_object(frame, box, new_box):
                    # Item already being tracked
                    new_trackers[i] = tracker_create()
                    new_trackers[i].init(frame, new_box)
                    new_bboxes[i] = new_box
                    break
            else: #Note: else clause of a for loop is taken if you do not 'break' from the for loop
                # New item
                new_trackers[self._ID_count] = tracker_create()
                new_trackers[self._ID_count].init(frame, new_box)
                new_bboxes[self._ID_count] = new_box
                self._ID_count +=1
        self.trackers = new_trackers
        print(new_bboxes)
        self.bboxes = new_bboxes

    def update(self, frame):
        '''Updates current trackers'''
        
        '''success = np.zeros(len(self.trackers))
        bboxes = self.bboxes
        for i,tracker in self.trackers.:
            success[i], new_box = tracker.update(frame)
            if success:
                success[i], bboxes[i] = tracker.update(frame)

        return bboxes'''
        for ind, tracker in self.trackers.items():
            success, new_box = tracker.update(frame)
            if success:
                self.bboxes[ind] = new_box
        
        return np.array(list(self.bboxes.values())).reshape(-1,4)