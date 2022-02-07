"""Holds the tracking behavior for the fan"""

#TODO: Change timer behavior to work on actual clock time rather than on ticks

class Fan:
    '''Manages the position of the fan

    Attributes:
        position: current x-position of fan
        movement: current x-velocity
        ticks: a timer for internal use
        current_track: cluster that's currently being tracked
    '''
    def __init__(self, start_pos, Trackers):
        self.position = start_pos
        self.movement = 0
        self.ticks = 0
        self.Trackers = Trackers

    def print_info(self):
        '''For debugging'''
        print(self.Trackers.timer)

    def update_movement(self, track_ids, cluster_labels, m, centers, ticks):
        '''Update the movement of the fan.
        Args:
            centers: cluster centers.
            ticks: number of ticks between each update. For timing purposes
        '''
        self.print_info()
        # Exit the function if nothing to do
        if len(track_ids) == 0:
            self._rotate_stop()
            return None
        
        # Iterate through the currently tracked boxes and find the first one whose fan time is still > 0
        for track_id, cluster_label in zip(track_ids, cluster_labels):
            if self.Trackers.timer[track_id][0] > 0:
                current_track = track_id
                current_cluster = cluster_label
                break
        else: #If all tracked boxes have had their fan time, then reset all timers
            # Timers stored in info[track_ids][0]
            for track_id in track_ids:
                    self.Trackers.timer[track_id][0] = 7
            current_track = track_ids[0]
            current_cluster = cluster_labels[0]

        # Count down the timer for all trackers in the current cluster, but more slowly if there are more people in it
        cluster_size = 0
        for cl in cluster_labels:
            if cl == current_cluster:
                cluster_size += 1

        for track_id, cluster in zip(track_ids, cluster_labels):
            if cluster == current_cluster:
                self.Trackers.timer[track_id][0] -= ticks * (0.5 + 0.5/cluster_size)

        # If fan not aligned with the cluster center it's currently following, move it
        if self.position - centers[current_cluster, 0] > 1:
            self._rotate_left()
        elif self.position - centers[current_cluster,0] < -1:
            self._rotate_right()
        else:
            self._rotate_stop()

        self.position += self.movement
        self.ticks += ticks

        return current_cluster

    def get_position(self):
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

    def rotate_right(self):
        '''Begin rotating the fan base to the right'''
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

    def rotate_left(self):
        '''Begin rotating the fan base to the left'''
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

    def rotate_stop(self):
        '''Stop angular rotation of the fan base'''
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

class Fan_Simulation(Fan):
    '''Simulates the position of the fan for testing without hardware'''

    def __init__(self, start_pos, Trackers):
        super().__init__(start_pos, Trackers)

    def get_position(self):
        '''Get the current x-position of where the fan is pointing at'''
        return self.position

    def _rotate_right(self):
        '''Begin rotating the fan base to the right'''
        self.movement = 5

    def _rotate_left(self):
        '''Begin rotating the fan base to the left'''
        self.movement = -5

    def _rotate_stop(self):
        '''Stop angular rotation of the fan base'''
        self.movement = 0

class FanRPi(Fan):
    '''Uses RPi.GPIO to control the physical fan'''
    def __init__(self, start_pos, Trackers):
        super().__init__(start_pos, Trackers)

    def get_position(self):
        '''Get the current x-position of where the fan is pointing at'''
        pass

    def _rotate_right(self):
        '''Begin rotating the fan base to the right'''
        pass

    def _rotate_left(self):
        '''Begin rotating the fan base to the left'''
        pass

    def _rotate_stop(self):
        '''Stop angular rotation of the fan base'''
        pass