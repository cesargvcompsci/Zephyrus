class Fan_Simulation:
    '''Simulates the position of the fan for testing without hardware
    
    Attributes:
        position: current x-position of fan
        movement: current x-velocity
        ticks: a timer for internal use
        current_track: cluster that's currently being tracked
    '''
    def __init__(self, start_pos):
        self.position = start_pos
        self.movement = 0
        self.ticks = 0
        self.current_track = 0

    def update_movement(self, ccounts, centers, ticks):
        '''Update the movement of the fan.
        Args:
            centers: cluster centers.
            ticks: number of ticks between each update. For timing purposes
        '''
        ###TODO: modify for continuity of clusters
        self.follow_times = (ccounts*0.5 + 1) * 200

        if len(centers)==0:
            self._rotate_stop()
        else:
            if self.current_track >= len(centers):
                self.current_track = 0

            elif self.ticks > self.follow_times[self.current_track]:
                self.current_track = (self.current_track+1) % len(centers)
                self.ticks = 0

            # If fan not aligned with the cluster center it's currently following, move it
            if self.position - centers[self.current_track, 0] > 1:
                self._rotate_left()
            elif self.position - centers[self.current_track,0] < -1:
                self._rotate_right()
            else:
                self._rotate_stop()

            self.position += self.movement
            self.ticks += ticks

    def _rotate_right(self):
        '''Begin rotating the fan base to the right'''
        self.movement = 5

    def _rotate_left(self):
        '''Begin rotating the fan base to the left'''
        self.movement = -5

    def _rotate_stop(self):
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