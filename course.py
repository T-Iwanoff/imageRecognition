

class Course:
    def __init__(self, ball_coords=None, obstacle_coords=None, wall_coords=None, robot_coords=None, robot_angle=None):
        self.ball_coords = ball_coords if ball_coords is not None else [[]]
        self.obstacle_coords = obstacle_coords if obstacle_coords is not None else [[]]
        self.wall_coords = wall_coords if wall_coords is not None else []
        self.robot_coords = robot_coords if robot_coords is not None else []
        self.robot_angle = robot_angle if robot_angle is not None else []
        


