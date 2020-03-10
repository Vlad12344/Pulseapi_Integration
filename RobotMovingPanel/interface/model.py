import os
from RobotMovingPanel.logger import file_existing_check, append_list_as_row
from pulseapi_integration import NewRobotPulse, jog

def runCodeFromTextEditor(program: str, path: str) -> None:
    if program != '':
        saveProgramFromTextEditor(program, path)
        exec(open(path).read())
    pass

def saveProgramFromTextEditor(program: str, path: str) -> None:
    """Save program to the special folder"""
    filesave = os.path.join(path)

    with open(filesave, 'w') as fid:
        fid.write(program)

def appendPositionToCSV(robot, path) -> None:
    XYZ = robot.get_position()['point'].values()
    RPW = robot.get_position()['rotation'].values()

    append_list_as_row(path, [*XYZ, *RPW])

def read(path: str) -> str:
    if path != '':
        with open(path, 'r') as f:
            text = f.read()
        return text
    else:
        raise AssertionError('Govno file')

