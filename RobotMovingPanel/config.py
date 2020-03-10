import os
from pulseapi_integration import *

host = '127.0.0.1'
robot = NewRobotPulse(host)

PATH_2_CSV = os.path.join(os.path.dirname(__file__), 'data/points/points.scv')
PATH_2_TOOL_JSON = os.path.join(os.path.dirname(__file__), 'data/tools/tools.json')