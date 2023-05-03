

class Course:
    def __init__(self, ball_coords=None, obstacle_coords=None, wall_coords=None):
        if ball_coords is None:
            self.ball_coords = []
        if obstacle_coords is None:
            self.obstacle_coords = []
        if wall_coords is None:
            self.wall_coords = []
