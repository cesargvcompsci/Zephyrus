"""Holds the tracking behavior for the fan"""

#TODO: Change timer behavior to work on actual clock time rather than on ticks

class Double_Fan:
    '''Manages the position of the fan

    Attributes:
        position: current x-position of fan
        movement: current x-velocity
        ticks: a timer for internal use
        current_track: cluster that's currently being tracked
    '''
    def __init__(self, start_pos, Trackers):
        self.A_pos = start_pos
        self.B_pos = start_pos
        self.A_move = 0
        self.B_move = 0
        self.ticks = 0
        self.Trackers = Trackers
        self.A_timer = -1
        self.B_timer = -1
        self.A_target = None
        self.B_target = None

    def print_info(self):
        '''For debugging'''
        print(self.Trackers.timer)

    def update_movement(self, track_ids, cluster_labels, m, centers, ticks):
        '''Update the movement of the fan.
        Args:
            centers: cluster centers.
            ticks: number of ticks between each update. For timing purposes
        '''
        # Exit the function if nothing to do
        if len(track_ids) == 0:
            self._rotate_stop()
            return None
        
        id_to_cluster = dict(zip(track_ids, cluster_labels))
        A_cluster = id_to_cluster.get(self.A_target,-1)
        B_cluster = id_to_cluster.get(self.B_target,-1)
        if centers.shape[0] > 1 and B_cluster == A_cluster:
            B_cluster = -1
        
        # New, faster algo: keep the timer in this func, count down for all in cluster when done
        if self.A_timer <= 0 or A_cluster == -1:
            # Set timers of trackers in same cluster to 0
            if A_cluster != -1:
                try:
                    A_cluster = id_to_cluster[self.A_target]
                    for track_id, cluster in id_to_cluster.items():
                        if cluster == A_cluster:
                            self.Trackers.timer[track_id] = 0
                except:
                    pass
            # Iterate through the currently tracked boxes and find the first one whose fan time is still > 0
            for track_id, cluster_label in zip(track_ids, cluster_labels):
                if self.Trackers.timer[track_id] > 0 and cluster_label != B_cluster:
                    self.A_target = track_id
                    A_cluster = cluster_label
                    break
            else: #If all tracked boxes have had their fan time, then reset all timers
                for track_id in track_ids:
                    self.Trackers.timer[track_id] = 7
                # If more than 1 cluster, find the cluster not tracked by B
                if centers.shape[0] > 1:
                    i = 0
                    while cluster_labels[i] == B_cluster:
                        i += 1
                    self.A_target = track_ids[i]
                    A_cluster = cluster_labels[i]
                else:
                    self.A_target = track_ids[0]
                    A_cluster = cluster_labels[0]  
            self.A_timer = 5.5
        
        # Repeat for fan B    
        if self.B_timer <= 0 or B_cluster == -1:
            # Set timers of trackers in same cluster to 0
            if B_cluster != -1:
                try:
                    B_cluster = id_to_cluster[self.B_target]
                    for track_id, cluster in id_to_cluster.items():
                        if cluster == B_cluster:
                            self.Trackers.timer[track_id] = 0
                except:
                    pass
            # Iterate through the currently tracked boxes and find the first one whose fan time is still > 0
            for track_id, cluster_label in zip(track_ids, cluster_labels):
                if self.Trackers.timer[track_id] > 0 and cluster_label != A_cluster:
                    self.B_target = track_id
                    B_cluster = cluster_label
                    break
            else: #If all tracked boxes have had their fan time, then reset all timers
                for track_id in track_ids:
                    self.Trackers.timer[track_id] = 7
                # If more than 1 cluster, find the cluster not tracked by B
                if centers.shape[0] > 1:
                    i = 0
                    while cluster_labels[i] == A_cluster:
                        i += 1
                    self.B_target = track_ids[i]
                    B_cluster = cluster_labels[i]
                else:
                    self.B_target = track_ids[0]
                    B_cluster = cluster_labels[0]  
            self.B_timer = 5.5
        
        self.A_timer -= 0.5
        self.B_timer -= 0.5

        # If fan not aligned with the cluster center it's currently following, move it
        if self.A_pos - centers[A_cluster, 0] > 20:
            self.A_left()
        elif self.A_pos - centers[A_cluster,0] < -20:
            self.A_right()
        else:
            self.A_stop()
        if self.B_pos - centers[B_cluster, 0] > 20:
            self.B_left()
        elif self.B_pos - centers[B_cluster,0] < -20:
            self.B_right()
        else:
            self.B_stop()

        self.A_pos += self.A_move
        self.B_pos += self.B_move

        return A_cluster, B_cluster

    def get_A_pos(self):
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

    def A_right(self):
        '''Begin rotating the fan base to the right'''
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

    def A_left(self):
        '''Begin rotating the fan base to the left'''
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

    def A_stop(self):
        '''Stop angular rotation of the fan base'''
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")
    
    ######################

    def get_B_pos(self):
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

    def B_right(self):
        '''Begin rotating the fan base to the right'''
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

    def B_left(self):
        '''Begin rotating the fan base to the left'''
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

    def B_stop(self):
        '''Stop angular rotation of the fan base'''
        raise NotImplementedError("Please instantiate Fan_Simulation or Fan_RPi")

class Double_Fan_Simulation(Double_Fan):
    '''Simulates the position of the fan for testing without hardware'''

    def __init__(self, start_pos, Trackers):
        super().__init__(start_pos, Trackers)

    def get_A_pos(self):
        '''Get the current x-position of where the fan is pointing at'''
        return self.A_pos

    def A_right(self):
        '''Begin rotating the fan base to the right'''
        self.A_move = 10

    def A_left(self):
        '''Begin rotating the fan base to the left'''
        self.A_move = -10

    def A_stop(self):
        '''Stop the fan's rotation'''
        self.A_move = 0

    def get_B_pos(self):
        '''Get the current x-position of where the fan is pointing at'''
        return self.B_pos

    def B_right(self):
        '''Begin rotating the fan base to the right'''
        self.B_move = 10

    def B_left(self):
        '''Begin rotating the fan base to the left'''
        self.B_move = -10

    def B_stop(self):
        '''Stop the fan's rotation'''
        self.B_move = 0

class Double_FanRPi(Double_Fan):
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