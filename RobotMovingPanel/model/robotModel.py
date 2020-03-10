from pulseapi_integration import *
from RobotMovingPanel.config import robot

def __jogMove(
    axis: str,
    speed: float = 1,
    ):
    axises = {
                'x': 0,
                'y': 0,
                'z': 0,
                'rx': 0,
                'ry': 0,
                'rz': 0,
            }

    if axis in axises:
        axises.update({axis: speed})

    accelerations_values = list(axises.values())
    robot.jogging(jog(*accelerations_values))

def __stepMove(
    axis: str,
    speed: float = 1,
    linearStep: float = 1,
    ):
    # print(linearStep)
    robot.move_along_axis(
        axis=axis,
        distance=linearStep,
        velocity=speed)

def move(
    state: bool,
    axis: str,
    speed: float = 1,
    moveStep: float = 1,
    direction: float = 1
    ):
    if direction not in [1, -1]:
        raise AssertionError(f'Incorrect input direction {direction}. Must be 1 or -1')

    if state == True:
        __jogMove(axis, speed*direction)
    elif state == False:
        __stepMove(axis=axis, linearStep=moveStep*direction, speed=speed)

def stopJog():
    # robot.jogging(jog())
    robot.freeze()

def relax():
    robot.relax()

def goHome(speed):
    robot.go_home(tcp_max_velocity=speed)

def freeze():
    robot.freeze()

def setTool(
    tcpCoordinates: list = [0,0,0,0,0,0],
    toolName: str = 'default'
    ) -> None:
    toolInfo = tool_info(position([*tcpCoordinates[:3]], [*tcpCoordinates[3:]]), name=toolName)
    robot.change_tool_info(toolInfo)

def getPosition():
    # return {'point': [1,2,3], 'rotation': [2,3,4]}
    return robot.get_position()
