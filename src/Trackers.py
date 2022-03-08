import cv2
import numpy as np

from clustering import cluster_boxes

tracker_create = cv2.TrackerKCF_create

def same_object(frame, A, B):
    '''Given two bounding boxes A and B, tuples [x,y,w,h],
    determine if they bound the same object'''

    # Are centers more than a third a width/length apart? If so, not same object
    xA, yA = [A[0]+A[2]/2, A[1]+A[3]/2] # center of A
    xB, yB = [B[0]+B[2]/2, B[1]+B[3]/2] # center of B
    if abs(xA-xB) >= min(A[2]/3, B[2]/3) or abs(yA-yB) >= min(A[3]/3, B[3]/3):
        return False

    # Do the images match?
    # Make sure coordinates are not out of bounds
    A = [max(0, A[0]), max(0, A[1]), A[2], A[3]]
    B = [max(0, B[0]), max(0, B[1]), A[2], A[3]]

    imgA = frame[A[1]:A[1]+A[3],A[0]:A[0]+A[2]]
    imgB = frame[B[1]:B[1]+B[3],B[0]:B[0]+B[2]]
    # Make imgA the smaller one
    if A[2]*A[3] > B[2]*B[3]:
        imgA,imgB = imgB,imgA

    # enforce imgA.height <= imgB.height and imgA.width <= imgB.width
    if imgA.shape[0] > imgB.shape[0]:
        # double negative sign gives "ceiling division"
        cut = (-imgA.shape[0] + imgB.shape[0])//2 * -1
        imgA = imgA[cut:-cut, :]
    if imgA.shape[1] > imgB.shape[1]:
        cut = (-imgA.shape[1] + imgB.shape[1])//2 * -1
        imgA = imgA[:,cut:-cut]
    
    # Repurpose template matching for this
    res = cv2.matchTemplate(imgA, imgB, cv2.TM_CCOEFF_NORMED)
    max_correlation = cv2.minMaxLoc(res)[1]
    
    return max_correlation > 0.15

class Trackers:
    '''A class to hold multiple trackers.

    Attributes:
        trackers(dict{int, cv2.Tracker}): holds all Trackers, indexed by a specific ID
        bboxes (dict{int : numpy array of shape (4,)}): bboxes for each tracked object, indexed by ID'''

    def __init__(self, cluster_dist_threshold):
        self._ID_count = 0 #Assign unique IDs to new objects
        self.cluster_dist_threshold = cluster_dist_threshold
        self.bboxes = {}
        self.timer = {}
        self.trackers = {}
        self.preserve = {} # For robustness to detection failing in one round

    #@profile
    def begin_track(self, frame, bbox):
        '''Matches bboxes to current trackers or create new ones if not already tracked'''
        new_trackers = {}
        new_bboxes = {}
        for new_box in bbox:
            # 1) Items already being tracked
            for i, box in self.bboxes.items():
                same_object(frame, box, new_box)
                if i not in new_trackers and same_object(frame, box, new_box):
                    new_trackers[i] = tracker_create()
                    new_trackers[i].init(frame, new_box)
                    new_bboxes[i] = new_box
                    self.preserve[i] = True
                    break
            
            # 2) New items with new ID, do if you do not 'break' from the for loop
            else:
                new_trackers[self._ID_count] = tracker_create()
                new_trackers[self._ID_count].init(frame, new_box)
                new_bboxes[self._ID_count] = new_box
                self.timer[self._ID_count] = 7
                self.preserve[self._ID_count] = True
                self._ID_count +=1
        
        # 3) Old items that failed to be detected are "safe" for one round
        for i in list(self.preserve.keys()):
            if i not in new_trackers:
                if self.preserve[i]:
                    new_trackers[i] = tracker_create()
                    new_trackers[i].init(frame, self.bboxes[i])
                    new_bboxes[i] = self.bboxes[i]
                    self.preserve[i] = False
                else:
                    del self.preserve[i]
                    del self.timer[i]
        
        self.trackers = new_trackers
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

    def cluster(self):
        '''Returns tracker_ids, cluster_labels, m, and cluster_centers,
        where tracker_ids and cluster_labels are parallel lists, m is the number of clusters,
        and cluster_centers is the center of each cluster from 0 to m-1'''

        ids, boxes = list(self.bboxes.keys()), list(self.bboxes.values())
        return (ids, *cluster_boxes(np.array(boxes), self.cluster_dist_threshold))