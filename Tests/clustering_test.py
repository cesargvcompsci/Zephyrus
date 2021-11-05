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

def cluster_by_distance(centers, distance_threshold):
    '''Performs a simple clustering algorithm based
    on distance between points. Inspired by DBScan, but every point will be assigned a cluster.
    Args:
        centers: array of shape (n, 2), where each row is a point (x,y)
        distance_threshold: float, maximum distance between cluster points

    Returns:
        cluster_labels: array of shape (n,) labels each point with a number from 0 to m.
        num_clusters: number of clusters
        cluster_centers'''

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

    cluster_centers = np.zeros((m,2))
    for c in range(m):
        # Take all points in cluster c and average each coordinate
        cluster_centers[c] = np.average(centers[cluster_labels==c], axis=0)

    return (cluster_labels, m, cluster_centers)



if __name__ == "__main__":
    hog = cv.HOGDescriptor()
    hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())

    img = cv.imread("group.jpg")
    img = imutils.resize(img, width=img.shape[0]//4)

    #cv.imshow('pano', pano)
    cv.waitKey(0)

    boxes, weights = hog.detectMultiScale(img, winStride=(8,8))

    cluster_labels, m, cluster_centers = cluster_by_distance(box_centers(boxes), 150)
    print("Number of clusters:", m)

    # Generate m different colors for testing
    colors_list = np.random.randint(25,255,(m,3))

    for ((x, y, w, h), cluster) in zip(boxes, cluster_labels):
        cv.rectangle(img, (x, y, w, h), colors_list[cluster].tolist(), 2)

    for c, center in enumerate(cluster_centers):
        cv.circle(img, center.astype(np.int16), 5, colors_list[c].tolist(), -1)

    #display frame
    cv.imshow('frame', img)
    #cv2.imwrite('test_img.jpg', pano)
    cv.waitKey(0)

    cv.destroyAllWindows()