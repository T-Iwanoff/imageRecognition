

class Course:
    def __init__(self, ball_coords=None, obstacle_coords=None, wall_coords=None):
        self.ball_coordinates = ball_coords if ball_coords is not None else [
            []]
        self.obstacle_coordinates = obstacle_coords if obstacle_coords is not None else [
            []]
        self.wall_coordinates = wall_coords if wall_coords is not None else []
