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
        self.print_info()

        A_cluster = None
        B_cluster = None
        # Exit the function if nothing to do
        if len(track_ids) == 0:
            self.A_stop()
            self.B_stop()
            return None
        
        # If already have a target, find the cluster label
        if self.A_target != None:
            for track_id, cluster_label in zip(track_ids, cluster_labels):
                if track_id == self.A_target:
                    A_cluster = cluster_label
                    break
            else:
                self.A_target = None
        #If no target, find one: iterate through the tracked boxes and find a fan whose timer is > 0
        if self.A_target == None:
            for track_id, cluster_label in zip(track_ids, cluster_labels):
                if self.Trackers.timer[track_id][0] > 0 and track_id != self.B_target:
                    self.A_target = track_id
                    A_cluster = cluster_label
                    break
            #If 'break', then no tracked fans have time > 0, and reset the rest
            else:
                # Timers stored in info[track_ids][0]
                for track_id in track_ids:
                        # Make sure not to mess with fan B
                        if track_id != self.B_target:
                            self.Trackers.timer[track_id][0] = 7
        
        #Repeat for Fan B
        if self.B_target != None:
            for track_id, cluster_label in zip(track_ids, cluster_labels):
                if track_id == self.B_target:
                    B_cluster = cluster_label
                    break
            else:
                self.B_target = None
        #If no target, find one: iterate through the tracked boxes and find a fan whose timer is > 0
        if self.B_target == None:
            for track_id, cluster_label in zip(track_ids, cluster_labels):
                if self.Trackers.timer[track_id][0] > 0 and track_id != self.A_target:
                    self.B_target = track_id
                    B_cluster = cluster_label
                    break
            #If 'break', then no tracked fans have time > 0, and reset the rest
            else:
                # Timers stored in info[track_ids][0]
                for track_id in track_ids:
                        # Make sure not to mess with fan B
                        if track_id != self.A_target:
                            self.Trackers.timer[track_id][0] = 7
            
        # Count down the timer for all trackers in the current cluster, but more slowly if there are more people in it
        A_cluster_size = 0
        B_cluster_size = 0
        for cl in cluster_labels:
            if cl == A_cluster:
                A_cluster_size += 1
            elif cl == B_cluster:
                B_cluster_size += 1
            
        for track_id, cluster in zip(track_ids, cluster_labels):
            if cluster == A_cluster:
                self.Trackers.timer[track_id][0] -= ticks * (0.5 + 0.5/A_cluster_size)
            elif cluster == B_cluster:
                self.Trackers.timer[track_id][0] -= ticks * (0.5 + 0.5/B_cluster_size)

        # Stop following if currently tracked fans reach 0
        # If fan not aligned with the cluster center it's currently following, move it
        if self.A_target != None:
            if self.Trackers.timer[self.A_target][0] <= 0:
                self.A_target = None
                self.A_stop()

            elif self.get_A_pos() - centers[A_cluster, 0] > 1:
                self.A_left()
            elif self.get_A_pos() - centers[A_cluster,0] < -1:
                self.A_right()
            else:
                self.A_stop()
        
        if self.B_target != None:
            if self.Trackers.timer[self.B_target][0] <= 0:
                self.B_target = None
                self.B_stop()
            elif self.get_B_pos() - centers[B_cluster, 0] > 1:
                self.B_left()
            elif self.get_B_pos() - centers[B_cluster,0] < -1:
                self.B_right()
            else:
                self.B_stop()

        self.A_pos += self.A_move
        self.B_pos += self.B_move
        self.ticks += ticks

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
        self.A_move = 5

    def A_left(self):
        '''Begin rotating the fan base to the left'''
        self.A_move = -5

    def A_stop(self):
        '''Stop the fan's rotation'''
        self.A_move = 0

    def get_B_pos(self):
        '''Get the current x-position of where the fan is pointing at'''
        return self.B_pos

    def B_right(self):
        '''Begin rotating the fan base to the right'''
        self.B_move = 5

    def B_left(self):
        '''Begin rotating the fan base to the left'''
        self.B_move = -5

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