class Cluster_manager:
    '''Manages clusters and allocates time for each fan to them'''
    
    def __init__(distance_threshold, max_width=None):
        self.distance_threshold = distance_threshold
        self.max_width = max_width

    def update(self, cluster_labels, m, cluster_centers, cluster_boxes):
        self.clabels = cluster_labels
        self.m = m
        self.ccenters = cluster_centers
        self.cboxes = cluster_boxes

        # Count how many people are in each cluster
        self.ccounts = np.zeros(m)
        for c in cluster_labels:
            self.ccounts[c] += 1

class Fan_Simulation:
    '''Simulates the position of the fan for testing without hardware'''
    def __init__(self, start_pos):
        self.position = start_pos
        self.movement = 0
        self.oscillating = False

    def init_oscillation(self,ccounts):
        '''Register the amount of time the fan will follow each cluster center'''
        # For this sim, follow a cluster with n people for 1+0.5n seconds
        self.ticks = 0
        self.follow_times = (ccounts*0.5 + 1) * 1000
        self.current_track = 0

        self.oscillating = True

    def update_movement(self, centers, ticks):
        '''Update the movement of the fan.
        Args:
            centers: cluster centers.
            ticks: number of ticks between each update. For timing purposes
        '''

        if len(centers)==0:
            pass
        elif self.oscillating:
            if self.ticks > self.follow_times[self.current_track]:
                self.current_track += 1

            if self.current_track > len(centers):
                            self.current_track = 0

            # If fan not aligned with the cluster center it's currently following, move it
            if self.position - centers[self.current_track, 0] > 1:
                self.rotate_left()
            elif self.position - centers[self.current_track,0] < -1:
                self.rotate_right()
            else:
                self.rotate_stop()

            self.position += self.movement
            self.ticks += ticks
        else:
            print("You need to run init_oscillation first to calculate follow times.")

    def rotate_right(self):
        '''Begin rotating the fan base to the right'''
        self.movement = 5

    def rotate_left(self):
        '''Begin rotating the fan base to the left'''
        self.movement = -5

    def rotate_stop(self):
        '''Stop angular rotation of the fan base'''
        self.movement = 0

class Fan:
    '''Manages the position of the fan'''

    def __init__():
        self.position = self.get_position()

    def get_position(self):
        '''Get the current x-position of where the fan is pointing at'''
        pass

    def rotate_right(self):
        '''Begin rotating the fan base to the right'''
        pass

    def rotate_left(self):
        '''Begin rotating the fan base to the left'''
        pass

    def rotate_stop(self):
        '''Stop angular rotation of the fan base'''
        pass