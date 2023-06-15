
import json


class NextMove:
    def __init__(self, next_ball=None, move_type=None, robot_coords=None, robot_heading=None):
        self.next_ball = next_ball if next_ball is not None else []
        self.move_type = move_type if move_type is not None else ""
        self.robot_coords = robot_coords if robot_coords is not None else []
        self.robot_heading = robot_heading if robot_heading is not None else []

    def to_json(self):
        return json.dumps(self.__dict__)
