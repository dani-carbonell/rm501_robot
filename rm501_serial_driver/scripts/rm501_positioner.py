# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rm501_positioner.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import time
import inputs
from roboclaw import Roboclaw

rc = Roboclaw("/dev/ttyUSB0",115200)
address1 = 0x80
address2 = 0x81
address3 = 0x82

DEFAULT_VEL_FAST=5000
DEFAULT_VEL_MED=2000
DEFAULT_VEL_SLOW=1000
DEFAULT_ACCEL=10000
AXIS1_MIN_LIM=-135
AXIS1_MAX_LIM=135
AXIS2_MIN_LIM=-10
AXIS2_MAX_LIM=90
AXIS3_MIN_LIM=-90
AXIS3_MAX_LIM=0
AXIS4_MIN_LIM=-90
AXIS4_MAX_LIM=90
AXIS5_MIN_LIM=-180
AXIS5_MAX_LIM=180




def connect():
	rc.Open()
	version1 = rc.ReadVersion(address1)
	version2 = rc.ReadVersion(address2)
	version3 = rc.ReadVersion(address3)

	if version1[0]==False:
		print "GETVERSION Failed"
	else:
		print repr(version1[1])
		print repr(version2[1])
		print repr(version3[1])

def gripper_moveb():
	rc.SpeedAccelM1(address1,DEFAULT_ACCEL,DEFAULT_VEL_SLOW)

def gripper_movef():
	rc.SpeedAccelM1(address1,DEFAULT_ACCEL,-DEFAULT_VEL_SLOW)

def gripper_stop():
	rc.SpeedAccelM1(address1,DEFAULT_ACCEL,0)

def axis1_moveb():
	rc.SpeedAccelM2(address1,DEFAULT_ACCEL,DEFAULT_VEL_FAST)

def axis1_movef():
	rc.SpeedAccelM2(address1,DEFAULT_ACCEL,-DEFAULT_VEL_FAST)

def axis1_stop():
	rc.SpeedAccelM2(address1,DEFAULT_ACCEL,0)

def axis2_moveb():
	rc.SpeedAccelM1(address2,DEFAULT_ACCEL,DEFAULT_VEL_MED)

def axis2_movef():
	rc.SpeedAccelM1(address2,DEFAULT_ACCEL,-DEFAULT_VEL_MED)

def axis2_stop():
	rc.SpeedAccelM1(address2,DEFAULT_ACCEL,0)

def axis3_moveb():
	rc.SpeedAccelM2(address2,DEFAULT_ACCEL,DEFAULT_VEL_FAST)

def axis3_movef():
	rc.SpeedAccelM2(address2,DEFAULT_ACCEL,-DEFAULT_VEL_FAST)

def axis3_stop():
	rc.SpeedAccelM2(address2,DEFAULT_ACCEL,0)

def axis4_moveb():
	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,DEFAULT_VEL_MED)
	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,DEFAULT_VEL_MED)

def axis4_movef():
	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,-DEFAULT_VEL_MED)
	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,-DEFAULT_VEL_MED)

def axis4_stop():
	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,0)
	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,0)

def axis5_moveb():
	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,-DEFAULT_VEL_MED)
	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,DEFAULT_VEL_MED)

def axis5_movef():
	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,DEFAULT_VEL_MED)
	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,-DEFAULT_VEL_MED)

def axis5_stop():
	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,0)
	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,0)





class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1152, 840)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(90, 760, 461, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(190, 630, 170, 48))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(450, 630, 170, 48))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setGeometry(QtCore.QRect(190, 560, 170, 48))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        self.pushButton_4.setGeometry(QtCore.QRect(450, 560, 170, 48))
        self.pushButton_4.setObjectName("pushButton_4")
        self.pushButton_5 = QtWidgets.QPushButton(Dialog)
        self.pushButton_5.setGeometry(QtCore.QRect(190, 490, 170, 48))
        self.pushButton_5.setObjectName("pushButton_5")
        self.pushButton_6 = QtWidgets.QPushButton(Dialog)
        self.pushButton_6.setGeometry(QtCore.QRect(450, 490, 170, 48))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_7 = QtWidgets.QPushButton(Dialog)
        self.pushButton_7.setGeometry(QtCore.QRect(190, 420, 170, 48))
        self.pushButton_7.setObjectName("pushButton_7")
        self.pushButton_8 = QtWidgets.QPushButton(Dialog)
        self.pushButton_8.setGeometry(QtCore.QRect(450, 420, 170, 48))
        self.pushButton_8.setObjectName("pushButton_8")
        self.pushButton_9 = QtWidgets.QPushButton(Dialog)
        self.pushButton_9.setGeometry(QtCore.QRect(190, 350, 170, 48))
        self.pushButton_9.setObjectName("pushButton_9")
        self.pushButton_10 = QtWidgets.QPushButton(Dialog)
        self.pushButton_10.setGeometry(QtCore.QRect(450, 350, 170, 48))
        self.pushButton_10.setObjectName("pushButton_10")
        self.pushButton_11 = QtWidgets.QPushButton(Dialog)
        self.pushButton_11.setGeometry(QtCore.QRect(460, 30, 170, 48))
        self.pushButton_11.setObjectName("pushButton_11")
        self.pushButton_12 = QtWidgets.QPushButton(Dialog)
        self.pushButton_12.setGeometry(QtCore.QRect(190, 280, 170, 48))
        self.pushButton_12.setObjectName("pushButton_12")
        self.pushButton_13 = QtWidgets.QPushButton(Dialog)
        self.pushButton_13.setGeometry(QtCore.QRect(450, 280, 170, 48))
        self.pushButton_13.setObjectName("pushButton_13")
        self.pushButton_14 = QtWidgets.QPushButton(Dialog)
        self.pushButton_14.setGeometry(QtCore.QRect(250, 30, 170, 48))
        self.pushButton_14.setObjectName("pushButton_14")
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setGeometry(QtCore.QRect(650, 30, 491, 791))
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton_15 = QtWidgets.QPushButton(Dialog)
        self.pushButton_15.setGeometry(QtCore.QRect(300, 100, 211, 121))
        self.pushButton_15.setObjectName("pushButton_15")
        self.pushButton_16 = QtWidgets.QPushButton(Dialog)
        self.pushButton_16.setGeometry(QtCore.QRect(40, 30, 170, 48))
        self.pushButton_16.setObjectName("pushButton_16")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(370, 640, 71, 31))
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(370, 570, 71, 34))
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(370, 500, 71, 34))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(370, 430, 71, 34))
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(370, 360, 71, 34))
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(370, 290, 71, 34))
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.spinBox = QtWidgets.QSpinBox(Dialog)
        self.spinBox.setGeometry(QtCore.QRect(142, 90, 121, 49))
        self.spinBox.setObjectName("spinBox")
        self.spinBox_2 = QtWidgets.QSpinBox(Dialog)
        self.spinBox_2.setGeometry(QtCore.QRect(142, 140, 121, 49))
        self.spinBox_2.setObjectName("spinBox_2")
        self.spinBox_3 = QtWidgets.QSpinBox(Dialog)
        self.spinBox_3.setGeometry(QtCore.QRect(142, 190, 121, 49))
        self.spinBox_3.setObjectName("spinBox_3")

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "Axis1-"))
        self.pushButton_2.setText(_translate("Dialog", "Axis1+"))
        self.pushButton_3.setText(_translate("Dialog", "Axis2-"))
        self.pushButton_4.setText(_translate("Dialog", "Axis2+"))
        self.pushButton_5.setText(_translate("Dialog", "Axis3-"))
        self.pushButton_6.setText(_translate("Dialog", "Axis3+"))
        self.pushButton_7.setText(_translate("Dialog", "Axis4-"))
        self.pushButton_8.setText(_translate("Dialog", "Axis4+"))
        self.pushButton_9.setText(_translate("Dialog", "Axis5-"))
        self.pushButton_10.setText(_translate("Dialog", "Axis5+"))
        self.pushButton_11.setText(_translate("Dialog", "Connect"))
        self.pushButton_12.setText(_translate("Dialog", "Close"))
        self.pushButton_13.setText(_translate("Dialog", "Open"))
        self.pushButton_14.setText(_translate("Dialog", "HOME"))
        self.pushButton_15.setText(_translate("Dialog", "RecordPosition"))
        self.pushButton_16.setText(_translate("Dialog", "Nest"))
        self.label.setText(_translate("Dialog", "0"))
        self.label_2.setText(_translate("Dialog", "0"))
        self.label_3.setText(_translate("Dialog", "0"))
        self.label_4.setText(_translate("Dialog", "0"))
        self.label_5.setText(_translate("Dialog", "0"))
        self.label_6.setText(_translate("Dialog", "0"))


	##USER CODE##
	self.pushButton.pressed.connect(axis1_moveb)
	self.pushButton.released.connect(axis1_stop)
	self.pushButton_2.pressed.connect(axis1_movef)
	self.pushButton_2.released.connect(axis1_stop)
	self.pushButton_3.pressed.connect(axis2_moveb)
	self.pushButton_3.released.connect(axis2_stop)
	self.pushButton_4.pressed.connect(axis2_movef)
	self.pushButton_4.released.connect(axis2_stop)
	self.pushButton_5.pressed.connect(axis3_moveb)
	self.pushButton_5.released.connect(axis3_stop)
	self.pushButton_6.pressed.connect(axis3_movef)
	self.pushButton_6.released.connect(axis3_stop)
	self.pushButton_7.pressed.connect(axis4_moveb)
	self.pushButton_7.released.connect(axis4_stop)
	self.pushButton_8.pressed.connect(axis4_movef)
	self.pushButton_8.released.connect(axis4_stop)
	self.pushButton_9.pressed.connect(axis5_moveb)
	self.pushButton_9.released.connect(axis5_stop)
	self.pushButton_10.pressed.connect(axis5_movef)
	self.pushButton_10.released.connect(axis5_stop)
	self.pushButton_12.pressed.connect(gripper_moveb)
	self.pushButton_12.released.connect(gripper_stop)
	self.pushButton_13.pressed.connect(gripper_movef)
	self.pushButton_13.released.connect(gripper_stop)

	self.pushButton_11.clicked.connect(connect)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Dialog = QtWidgets.QDialog()
    ui = Ui_Dialog()
    ui.setupUi(Dialog)
    Dialog.show()
    sys.exit(app.exec_())

