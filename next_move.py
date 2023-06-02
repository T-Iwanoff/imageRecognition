
import json


class NextMove:
    def __init__(self, next_ball=None, robot_coords=None, robot_angle=None):
        self.next_ball = next_ball if next_ball is not None else []
        self.robot_coords = robot_coords if robot_coords is not None else []
        self.robot_angle = robot_angle if robot_angle is not None else []


    def encode(self):
        return json.dumps(self.__dict__)
        

