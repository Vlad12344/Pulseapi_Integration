from typing import Tuple
from RobotMovingPanel.features import tcp
from RobotMovingPanel.model import robotModel
from RobotMovingPanel.config import PATH_2_TOOL_JSON
from RobotMovingPanel.utils.jsonWorker import writeJson, openJson
from ptc_cli import cli

point6f = Tuple[float, float, float,
                float, float, float]

def addTool(
    toolNum: int = 0,
    toolName: str = 'TCP_',
    tcpCoordinates: list = point6f,
    calibratedPoints: dict = {}
    ) -> str:
    "Add tool with default name like TCP_0"
    toolName = f'{toolName}{toolNum-1}'

    tcpInfo = {
        f"{toolName}":
        {
        "calibrated_points": calibratedPoints,
        "TCP_coordinates": tcpCoordinates
        }
    }
    data = openJson(PATH_2_TOOL_JSON)
    data.update(tcpInfo)
    writeJson(PATH_2_TOOL_JSON, data)
    return toolName

def getToolsNames() -> str:
    toolsNames = openJson(PATH_2_TOOL_JSON).keys()
    return toolsNames

def delTool(toolName: str) -> None:
    resetTool(toolName)
    data = openJson(PATH_2_TOOL_JSON)
    data.pop(toolName)
    writeJson(PATH_2_TOOL_JSON, data)

def resetTool(toolName: str) -> None:
    data = openJson(PATH_2_TOOL_JSON)
    data[toolName]['TCP_coordinates'] = [0.0,0.0,0.0,0.0,0.0,0.0]
    data[toolName]['calibrated_points'].clear()
    writeJson(PATH_2_TOOL_JSON, data)

    robotModel.setTool(
        toolName=toolName,
        tcpCoordinates=data[toolName]['TCP_coordinates'],
        )

def updateTCPCoordinates(
    toolName: str,
    tcpCoordinates: list = point6f,
    calibratedPoints: dict = {}##################################
    ) -> None:
    if toolName != 'default':
        data = openJson(PATH_2_TOOL_JSON)
        data[toolName]['TCP_coordinates'] = tcpCoordinates
        data[toolName]['calibrated_points'] = calibratedPoints
        writeJson(PATH_2_TOOL_JSON, data)

        robotModel.setTool(
            toolName=toolName,
            tcpCoordinates=tcpCoordinates,
        )
    else: pass

def updateToolName(newName: str, currentName: str) -> None:
    data = openJson(PATH_2_TOOL_JSON)
    data[newName] = data.pop(currentName)
    writeJson(PATH_2_TOOL_JSON, data)

def getTCPCoordinates(toolName: str) -> list:
    if toolName != 'default':
        tools = openJson(PATH_2_TOOL_JSON)
        return tools[toolName]['TCP_coordinates']
    else: return [0.0,0.0,0.0,0.0,0.0,0.0]

def checkSimilarity(toolName: str) -> bool:
    toolsNames = openJson(PATH_2_TOOL_JSON).keys()
    if toolName in toolsNames:
        return True
    return False

def updateCalibratedPoints(toolName: str, key: str, value: list):
    data = openJson(PATH_2_TOOL_JSON)
    data[toolName]['calibrated_points'].update({key: value})
    writeJson(PATH_2_TOOL_JSON, data)

def calculateTCP(toolName: str) -> list:
    data = openJson(PATH_2_TOOL_JSON)
    points = data[toolName]['calibrated_points'].values()
    tcpCoordinates = cli.main(points)
    data[toolName]['TCP_coordinates'][:3] = tcpCoordinates
    writeJson(PATH_2_TOOL_JSON, data)