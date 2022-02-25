import cv2
import numpy as np

from clustering import cluster_boxes

tracker_create = cv2.TrackerCSRT_create

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
    print(max_correlation)
    
    return max_correlation > 0.15

class Trackers:
    '''A class to hold multiple trackers and manage clusters.

    Attributes:
        trackers(dict{int, cv2.Tracker}): holds all Trackers, indexed by a specific ID
        bboxes (dict{int : numpy array of shape (4,)}): bboxes for each tracked object, indexed by ID
    '''

    def __init__(self, cluster_dist_threshold):
        self._ID_count = 0 #Assign unique IDs to new objects
        self.cluster_dist_threshold = cluster_dist_threshold
        self.trackers = {}
        self.timer = {} # Contains 0:time_left and 1:preserve
        self.bbox = {}

    def del_tracker(self, t_id):
        del self.trackers[t_id]
        del self.timer[t_id]
        del self.bbox[t_id]

    #@profile
    def begin_track(self, frame, new_bbox):
        '''Matches bboxes to current trackers or create new ones if not already tracked'''
        n = len(new_bbox)
        # Match up old trackers to bboxes
        for t_id in list(self.trackers):
            # iterate through new bboxes
            for i in range(n):
                if same_object(frame, self.bbox[t_id], new_bbox[i]):
                    self.bbox[t_id] = new_bbox[i]
                    new_bbox[i] = new_bbox[n-1]
                    n -= 1
                    break
            # Can't find match for existing tracker, either preserve for another round or delete
            else:
                if self.timer[t_id][1]:# == True
                    self.timer[t_id][1] = False
                else: #self.timer[t_id][preserve] == False
                    self.del_tracker(t_id)

        # Process remaining bboxes into new trackers
        for i in range(n):
            self.trackers[self._ID_count] = tracker_create()
            self.trackers[self._ID_count].init(frame, new_bbox[i])
            self.timer[self._ID_count] = [7, True] #[Time left=7, Preserve=True]
            self.bbox[self._ID_count] = new_bbox[i]
            self._ID_count += 1

    def update(self, frame):
        '''Updates current trackers'''
        
        for t_id, tracker in self.trackers.items():
            success, new_box = tracker.update(frame)
            if success:
                self.bbox[t_id] = new_box
 
        return np.array(list(self.bbox.values())).reshape(-1,4)

    def cluster(self):
        '''Returns tracker_ids, cluster_labels, m, and cluster_centers,
        where tracker_ids and cluster_labels are parallel lists, m is the number of clusters,
        and cluster_centers is the center of each cluster from 0 to m-1'''

        ids, boxes = list(self.bbox.keys()), list(self.bbox.values())
        return [ids] + list(cluster_boxes(np.array(boxes), self.cluster_dist_threshold))