

class Course:
    def __init__(self, ball_coords=None, orange_ball=None, obstacle_coords=None, wall_coords=None, robot_coords=None, robot_heading=None):
        self.ball_coords = ball_coords if ball_coords is not None else [[]]
        self.orange_ball = orange_ball if orange_ball is not None else []
        self.obstacle_coords = obstacle_coords if obstacle_coords is not None else [[]]
        self.wall_coords = wall_coords if wall_coords is not None else []
        self.robot_coords = robot_coords if robot_coords is not None else []
        self.robot_heading = robot_heading if robot_heading is not None else []
        


