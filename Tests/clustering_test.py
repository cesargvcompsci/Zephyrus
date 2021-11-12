import numpy as np
import cv2 as cv
import sys
import numpy as np
import imutils

def box_centers(boxes):
    '''Args:
        boxes: array of [x,y,w,h], where (x,y) is the
        top left corner and w and h are the width and length'''
    return np.array([[x+w/2, y+h/2] for [x,y,w,h] in boxes])

def cluster_boxes(boxes, distance_threshold, max_width=None):
    '''Performs a simple clustering algorithm based
    on distance between points. Inspired by hierarchical clustering and DBScan.
    Args:
        centers: array of shape (n, 2), where each row is a point (x,y)
        distance_threshold: float, maximum distance between cluster points
        max_width: integer or None, split clusters if box size larger than this width, or do nothing if None.
    Returns:
        cluster_labels: array of shape (n,) labels each point with a number from 0 to m.
        num_clusters: number of clusters
        cluster_centers'''

    centers = box_centers(boxes)
    n = centers.shape[0] # number of points
    m = 0 # number of clusters so far
    cluster_labels = np.full(n,-1,dtype=np.int16)
    for i in range(n):
        # If not already in a cluster, make a new one
        if cluster_labels[i] == -1:
            cluster_labels[i] = m
            m += 1

        # Add nearby points to this points cluster
        for j in range(i+1, n):
            if np.linalg.norm(centers[i]-centers[j]) <= distance_threshold:
                cluster_labels[j] = cluster_labels[i]
            # alternatively, if the boxes overlap:
            elif boxes[i,0] >= boxes[j,0] and boxes[i,0]-boxes[j,0] <= boxes[j,2] \
                or boxes[j,0] >= boxes[i,0] >= 0 and boxes[i,0]-boxes[j,0] <= boxes[j,2]:
                cluster_labels[j] = cluster_labels[i]

    #Give boxes of clusters
    cluster_boxes = np.zeros((m,4),dtype=np.int16)
    top_left_corner = boxes[:,:2] # x and y
    bot_right_corner = top_left_corner + boxes[:,2:4] # x+w and y+h
    
    for c in range(m):
        mask = (cluster_labels==c).nonzero() #Choose elements from particular cluster
        cluster_boxes[c,0:2] = np.amin(top_left_corner[mask], axis=0) 
        cluster_boxes[c,2:4] = np.amax(bot_right_corner[mask], axis=0) - cluster_boxes[c,0:2]

    if max_width is not None:
        # Break apart large clusters
        for (c, (x,y,w,h)) in enumerate(cluster_boxes):
            if w > max_width:
                to_check = set([c])

                while to_check:
                    c = to_check.pop()
                    if cluster_boxes[c, 2] > max_width and len(cluster_labels==c) > 1: #width
                        # Find units in the cluster to the right of the cluster box center
                        (x,y,w,h) = cluster_boxes[c,:]
                        mask = np.logical_and(cluster_labels == c, centers[:,0] > np.average(centers[:,0][cluster_labels==c], axis=0))
                        mask = mask.nonzero()[0]

                        if len(mask) > 0:
                            # Give them a new cluster
                            cluster_labels[mask] = m
                            cluster_boxes = np.vstack((cluster_boxes, [0, 0, 0, 0]))
                            # Redo the boxes for the new left and right clusters

                            for k in (c, m):
                                mask = (cluster_labels==k).nonzero()
                                cluster_boxes[k,0:2] = np.amin(top_left_corner[mask], axis=0) 
                                cluster_boxes[k,2:4] = np.amax(bot_right_corner[mask], axis=0) - cluster_boxes[k,0:2]

                            # check that the new clusters aren't also too wide
                            to_check.add(c)
                            to_check.add(m)
                            
                            m = m+1

    cluster_centers = np.zeros((m,2))
    for c in range(m):
        # Take all points in cluster c and average each coordinate
        cluster_centers[c] = np.average(centers[cluster_labels==c], axis=0)

    return cluster_labels, m, cluster_centers, cluster_boxes

if __name__ == "__main__":
    hog = cv.HOGDescriptor()
    hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())

    img = cv.imread("group.jpg")
    img = imutils.resize(img, width=img.shape[0]//4)

    #cv.imshow('pano', pano)
    cv.waitKey(0)

    boxes, weights = hog.detectMultiScale(img, winStride=(8,8))

    clabels, m, ccenters, cboxes = cluster_boxes(boxes, 1000, 20)
    print("Number of clusters:", m)

    # Generate m different colors for testing
    colors_list = np.random.randint(25,255,(m,3))

    for ((x, y, w, h), cluster) in zip(boxes, clabels):
        cv.rectangle(img, (x, y, w, h), colors_list[cluster].tolist(), 2)

    for (x,y,w,h) in cboxes:
        cv.rectangle(img, (x, y, w, h), (0,0,0), 1)

    for c, center in enumerate(ccenters):
        cv.circle(img, center.astype(np.int16), 5, colors_list[c].tolist(), -1)

    #display frame
    cv.imshow('frame', img)
    #cv2.imwrite('test_img.jpg', pano)
    cv.waitKey(0)

    cv.destroyAllWindows()