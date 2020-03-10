import os
import sys
import time

from math import radians
from PyQt5 import QtWidgets, QtCore, QtGui
# from RobotMovingPanel.features import tcp
from pulseapi_integration import NewRobotPulse, jog, PulseApiException
from pulseapi_integration.utils import position_2_xyzrpw
from pulseapi import tool_info, tool_shape, position, pose
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

from .interface import Ui_Dialog
from RobotMovingPanel import config
from RobotMovingPanel.logger import file_existing_check, append_list_as_row
from RobotMovingPanel.utils.jsonWorker import openJson

from RobotMovingPanel.interface import model
from RobotMovingPanel.model import tcpmodel
from RobotMovingPanel.model import robotModel
from RobotMovingPanel.model.treewidgetmodel import selectTreeItem


class PositionChenger(QtCore.QThread):
    def __init__(self, mainwindow, parent=None):
        super().__init__()
        self.mainwindow = mainwindow

    def run(self):
        while True:
            XYZ = self.mainwindow.robot.get_position()['point'].values()
            RPW = self.mainwindow.robot.get_position()['rotation'].values()

            for lineEdit, value in zip(self.mainwindow.lineEdit_position_mapping, [*XYZ, *RPW]):
                lineEdit.setText(str(round(value, 4)))
            time.sleep(0.2)

class MovingPanel(QtWidgets.QMainWindow, Ui_Dialog):

    def __init__(self):
        super().__init__()

        self.PROG: str = ''
        self.PROG_PATH: str = ''

        self.NUMBER_OF_TOOL_CALIBRATION_POINTS = set()
        self.CURRENT_TOOL_CALIBRATION_NAME = ''

        self.setupUi(self)

        self.lineEdit.setVisible(False)
        self.pushButton_2.setVisible(False)
        self.pushButton_3.setVisible(False)

        file_existing_check(config.PATH_2_CSV)

        # self.move_buttons_maping = [
        #     (self.button_xUp,       {'direction':  1, 'axis': 'x'}),
        #     (self.button_xDown,     {'direction': -1, 'axis': 'x'}),
        #     (self.button_yUp,       {'direction':  1, 'axis': 'y'}),
        #     (self.button_yDown,     {'direction': -1, 'axis': 'y'}),
        #     (self.button_zUp,       {'direction':  1, 'axis': 'z'}),
        #     (self.button_zDown,     {'direction': -1, 'axis': 'z'}),
        #     (self.button_rollUp,    {'direction':  1, 'axis': 'rx'}),
        #     (self.button_rollDown,  {'direction': -1, 'axis': 'rx'}),
        #     (self.button_pitchUp,   {'direction':  1, 'axis': 'ry'}),
        #     (self.button_pitchDown, {'direction': -1, 'axis': 'ry'}),
        #     (self.button_yawUp,     {'direction':  1, 'axis': 'rz'}),
        #     (self.button_yawDown,   {'direction': -1, 'axis': 'rz'})
        # ]

        self.move_buttons_maping = [
            (self.button_xUp,       self.xUp),
            (self.button_xDown,     self.xDown),
            (self.button_yUp,       self.yUp),
            (self.button_yDown,     self.yDown),
            (self.button_zUp,       self.zUp),
            (self.button_zDown,     self.zDown),
            (self.button_rollUp,    self.rxUp),
            (self.button_rollDown,  self.rxDown),
            (self.button_pitchUp,   self.ryUp),
            (self.button_pitchDown, self.ryDown),
            (self.button_yawUp,     self.rzUp),
            (self.button_yawDown,   self.rzDown)
        ]

        self.lineEdit_position_mapping = [
            self.lineEdit_x,
            self.lineEdit_y,
            self.lineEdit_z,
            self.lineEdit_roll,
            self.lineEdit_pitch,
            self.lineEdit_yaw
        ]

        self.lineEdit_joints_mapping = [
            self.lineEdit_J_1,
            self.lineEdit_J_2,
            self.lineEdit_J_3,
            self.lineEdit_J_4,
            self.lineEdit_J_5,
            self.lineEdit_J_6
        ]

        self.lineEdit_tool_maping = [
            self.lineEdit_tollX,
            self.lineEdit_tool_Y,
            self.lineEdit_tool_Z,
            self.lineEdit_tool_RX,
            self.lineEdit_tool_RY,
            self.lineEdit_tool_RZ
        ]

        # self.positionalChenger_instance = PositionChenger(mainwindow=self)
        # self.launchPositionChanger()
        self.move_buttons_handler()
        self.setToolComboBox()


    def closeGraphWindow(self):
        self.stackedWidget_3.setCurrentIndex(0)

    def openFullScreen(self):
        self.stackedWidget_3.setCurrentIndex(1)

    def infoFromLineEdit(self, mapping: list) -> list:
        return [float(line_edit.text()) for line_edit in mapping]

#-------------------TOOL-------------------
    def besidesDefaultTool(func):
        def wrapper(self):
            if self.tollsComboBox.currentIndex() != 0:
                func(self)
            pass
        return wrapper

    @besidesDefaultTool
    def openToolSetPoints(self):
        self.stackedWidget_2.setCurrentIndex(1)
        self.tollsComboBox.setEnabled(False)

    def closeTeachTCPWindow(self):
        self.stackedWidget_2.setCurrentIndex(0)
        self.tollsComboBox.setEnabled(True)

    def addToolHandler(self):
        count = self.tollsComboBox.count()
        coordinates = self.infoFromLineEdit(self.lineEdit_tool_maping)
        # tool is a standard name like TCP_0
        tool = tcpmodel.addTool(toolNum=count, tcpCoordinates=coordinates)
        self.tollsComboBox.addItem(tool)
        self.tollsComboBox.setCurrentText(tool)

    @besidesDefaultTool
    def delToolHandler(self):
        tool_name = self.tollsComboBox.currentText()
        item_num = self.tollsComboBox.currentIndex()
        # if not tool_name == 'default':
        self.tollsComboBox.removeItem(item_num)
        tcpmodel.delTool(toolName=tool_name)
        # else: pass

    @besidesDefaultTool
    def resetTool(self):
        tool_name = self.tollsComboBox.currentText()
        tcpmodel.resetTool(tool_name)

        for line_edit in self.lineEdit_tool_maping:
            line_edit.setText('0.0')

    def setToolComboBox(self):
        names = tcpmodel.getToolsNames()
        for name in names:
            self.tollsComboBox.addItem(name)

    def setToolHandler(self):
        coordinates = self.infoFromLineEdit(self.lineEdit_tool_maping)
        tool_name = self.tollsComboBox.currentText()
        tcpmodel.updateTCPCoordinates(tool_name, tcpCoordinates=coordinates)
        # tcpCoordinates = tcpmodel.getTCPCoordinates(tool_name)
        # robotModel.setTool(tcpCoordinates=tcpCoordinates)

    def setToolFromItem(self, itemText: str):
        coords = tcpmodel.getTCPCoordinates(itemText)
        for line, coord in zip(self.lineEdit_tool_maping, coords):
            line.setText(str(coord))

    def setToolName(self):
        if self.lineEdit.isVisible() and self.lineEdit.text() != '':
            self.lineEdit.setCursorPosition(0)
            new_name = self.lineEdit.text()
            current_name = self.tollsComboBox.currentText()
            if not tcpmodel.checkSimilarity(new_name):
                tcpmodel.updateToolName(new_name, current_name)
                item_index = self.tollsComboBox.currentIndex()
                self.tollsComboBox.setItemText(item_index, new_name)
                self.lineEdit.setVisible(False)
            else:
                self.lineEdit.setVisible(False)
        elif self.lineEdit.isVisible() and self.lineEdit.text() == '':
            self.lineEdit.setVisible(False)
        elif self.tollsComboBox.currentIndex() == 0:
            self.lineEdit.setVisible(False)
        else:
            self.lineEdit.clear()
            self.lineEdit.setVisible(True)

    def openMoveTabWithSetPointsMode(self, button: str):
        """param: buttonNum: int number from -2 and etc."""
        self.tabWidget.setCurrentIndex(0)
        self.enableOkCancelButtonOnMovingPanel(True)
        self.CURRENT_TOOL_CALIBRATION_NAME = button.text()

    def setCalibratedPoint(self):
        self.enableOkCancelButtonOnMovingPanel(False)
        buttonText = self.CURRENT_TOOL_CALIBRATION_NAME
        toolName = self.tollsComboBox.currentText()
        xyzrpw = robotModel.getPosition()
        tcpmodel.updateCalibratedPoints(
            toolName,
            buttonText,
            [*xyzrpw['point'].values(), *xyzrpw['rotation'].values()]
            )
        self.CURRENT_TOOL_CALIBRATION_NAME = ''
        self.closeMoveTab()

    def setCalibratedTool(self):
        tool_name = self.tollsComboBox.currentText()
        tcpmodel.calculateTCP(tool_name)
        self.setToolFromItem(tool_name)
        self.tollsComboBox.setEnabled(True)

    def teachToolPointsChecker(self, buttonID: int) -> None:
        self.NUMBER_OF_TOOL_CALIBRATION_POINTS.add(buttonID)
        if len(self.NUMBER_OF_TOOL_CALIBRATION_POINTS) == 4:
            self.SetToolPointsButton.setEnabled(True)
#--------------------------------------

    def closeMoveTab(self):
        self.tabWidget.setCurrentIndex(1)

    def enableOkCancelButtonOnMovingPanel(self, state: bool):
        if state:
            self.pushButton_2.setVisible(state)
            self.pushButton_3.setVisible(state)
            self.pushButton.setVisible(state-1)
        else:
            self.pushButton_2.setVisible(state)
            self.pushButton_3.setVisible(state)
            self.pushButton.setVisible(state+1)


    def enableStepEnter(self):
        state = False
        if self.radioButton_Step.isChecked():
            state = True
        self.doubleSpinBox_step.setEnabled(state)
        self.doubleSpinBox_rotation.setEnabled(state)

    def launchPositionChanger(self):
        self.positionalChenger_instance.start()

    def getSpeed(self):
        return self.horizontalSlider_speed.value()/100

    def getLinearStep(self):
        return self.doubleSpinBox_step.value()/1000

    def getRotationStep(self):
        return self.doubleSpinBox_rotation.value()

    def move_buttons_handler(self):
        try:
            for button, move_func in self.move_buttons_maping:
                button.pressed.connect(move_func)
                button.released.connect(self.stopJog)
        except PulseApiException:
            print('loh')

    # def check_state(self):
    #     return self.radioButton_Jogging.isChecked()

    # def move_button_handler(self):
    #     try:
    #         for button, params in self.move_buttons_maping:
    #             if axis in ['x', 'y', 'z']:
    #                 button.pressed.connect(
    #                     lambda: robotModel.move(
    #                         state=self.check_state(), axis=axis, speed=self.getSpeed(),
    #                         moveStep=self.getLinearStep()*direction)
    #                                     )
    #             elif axis in ['rx', 'ry', 'rz']:
    #                 button.pressed.connect(
    #                     lambda: robotModel.move(
    #                         state=self.check_state(), axis=axis, speed=self.getSpeed(),
    #                         moveStep=self.getRotationStep()*direction)
    #                                     )
    #             button.released.connect(self.stopJog)
    #     except PulseApiException:
    #         print('loh')
    def xUp(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='x', speed=self.getSpeed(), moveStep=self.getLinearStep())

    def xDown(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='x', speed=self.getSpeed(), moveStep=self.getLinearStep(), direction=-1)

    def yUp(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='y', speed=self.getSpeed(), moveStep=self.getLinearStep())

    def yDown(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='y', speed=self.getSpeed(), moveStep=self.getLinearStep(), direction=-1)

    def zUp(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='z', speed=self.getSpeed(), moveStep=self.getLinearStep())

    def zDown(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='z', speed=self.getSpeed(), moveStep=self.getLinearStep(), direction=-1)

    def rxUp(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='rx', speed=self.getSpeed(), moveStep=self.getRotationStep())

    def rxDown(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='rx', speed=self.getSpeed(), moveStep=self.getRotationStep(), direction=-1)

    def ryUp(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='ry', speed=self.getSpeed(), moveStep=self.getRotationStep())

    def ryDown(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='ry', speed=self.getSpeed(), moveStep=-self.getRotationStep(), direction=-1)

    def rzUp(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='rz', speed=self.getSpeed(), moveStep=self.getRotationStep())

    def rzDown(self):
        state = self.radioButton_Jogging.isChecked()
        robotModel.move(
            state=state, axis='rz', speed=self.getSpeed(), moveStep=-self.getRotationStep(), direction=-1)

    def stopJog(self):
        if self.radioButton_Jogging.isChecked():
            robotModel.stopJog()
        else: pass

    def getButton_handler(self):
        robotModel.appendPositionToCSV(self.robot, config.PATH_2_CSV)

    def getPose_handler(self):
        print(robotModel.get_pose())

    def relaxRobotHandler(self):
        robotModel.relax()

    def freezeRobotHandler(self):
        robotModel.freeze()

    def enableRelaxButton(self):
        if self.enableRelaxRadioButton.isChecked():
            self.relaxButton.setEnabled(True)
        else:
            self.relaxButton.setEnabled(False)

    def showFileDialog(self):
        self.PROG_PATH = QFileDialog.getOpenFileName(self, 'Open file', '/home')[0]
        self.PROG = model.read(self.PROG_PATH)
        self.textEdit.setText(self.PROG)

    def saveProgramHandler(self):
        model.saveProgramFromTextEditor(self.PROG, self.PROG_PATH)

    def runCode(self):
        model.runCodeFromTextEditor(self.PROG, self.PROG_PATH)

    def showProgramEditor(self, item):
        state, itemNum = selectTreeItem(item.text(0))
        if state:
            self.stackedWidget.setCurrentIndex(itemNum)
        else: pass

    def goHome(self):
        tcp_velocity = self.getSpeed()
        # print(tcp_velocity)
        robotModel.goHome(speed=tcp_velocity)