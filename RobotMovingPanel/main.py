import sys

from RobotMovingPanel import config
from PyQt5.QtWidgets import QApplication
from RobotMovingPanel.interface.interfaceLogic import MovingPanel

def main(host):
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = MovingPanel()
    window.show()
    app.exec_()