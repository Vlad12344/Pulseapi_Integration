from .typess import points3f, points6f
from RobotMovingPanel.config import PATH_2_TOOL_JSON
from RobotMovingPanel.utils.jsonWorker import emptyJson, writeJson, openJson, checkExisting

class TCP:
    def __init__(self, name: str, tcpCoordinates: list = [0,0,0,0,0,0]):
        self.name: str = name
        self.calibrated_points: list = []
        self.TCP_coordinates: list = tcpCoordinates
        self.PATH_2_JSON = PATH_2_TOOL_JSON

    def add_calibrate_point(self, point: points6f) -> None:
        self.calibrated_points.append(self.calibrated_point)

    def change_calibrate_point(self, num: int, point: points6f) -> None:
        if num >= len(self.calibrated_points):
            raise AssertionError(f'Incorrect num of point {num}')
        self.calibrated_points[num] = point

    # def saveTCP(self) -> None:
    #     tcp_info = {
    #         f"{self.name}":
    #         {
    #         "calibrated_points": self.calibrated_points,
    #         "TCP_coordinates": self.TCP_coordinates
    #         }
    #     }
    #     data = openJson(self.PATH_2_JSON)
    #     data.update(tcp_info)
    #     writeJson(self.PATH_2_JSON, data)

    def resetTCP(self) -> None:
        self.TCP_coordinates = [0,0,0,0,0,0]
        self.calibrated_points = []
        saveTCP()

    def deleteTCP(self) -> None:
        data = openJson(self.PATH_2_JSON)
        data.pop(self.name)
        writeJson(self.PATH_2_JSON, data)

    # def getToolfromJson(self):
    #     return openJson(self.PATH_2_TOOL_JSON)
