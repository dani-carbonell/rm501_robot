#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'rm501_positioner.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import time
import inputs
import os
import csv
from Queue import Queue
from threading import Thread, Lock, Event
from roboclaw27 import Roboclaw

DEFAULT_PORT="/dev/ttyUSB0"

DEFAULT_ADDRESS1=0x80
DEFAULT_ADDRESS2=0x81
DEFAULT_ADDRESS3=0x82

DEFAULT_TOLERANCE=15
DEFAULT_VEL_FAST=7000
DEFAULT_VEL_MED=3000
DEFAULT_VEL_SLOW=2000
DEFAULT_ACCEL=8000
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


class RequestPending(Exception):
	pass


class Axis(object):
	def __init__(self, rc, name, addr, m_nr, default_spd=9000, default_acc=15000):
		if not isinstance(rc, Roboclaw):
			raise TypeError("rc argument must be an instance of Roboclaw. Got {}".format(type(rc).__name__))

# str, int... is to reformat the parameters in case thay are not the correct type?
		self._rc=rc
		self.name=str(name)
		self.addr=int(addr)
		self.m_nr=int(m_nr)
		self.default_spd=default_spd
		self.default_acc=default_acc

		if (self.addr < 128) or (self.addr > 136):
			raise ValueError("Board-Address must be between 128 and 136")

		if (self.m_nr < 1) or (self.m_nr > 2):
			raise ValueError("Motor-Number must be 1 or 2")

# _port_lock is an arbitrary name you assing to an new variable in the _rc object witch is shared by all the axis instances.
		if not hasattr(self._rc, "_port_lock"):
			self._rc._port_lock = Lock()

		self._position=None
		self._position_status=Event()
		self._velocity=None
		self._velocity_status=Event()
		self._target_position=0
		self._target_position_status=Event()
		self._target_velocity=0
		self._target_velocity_status=Event()


# We are not calling this in our code yet. Right?
	def __str__(self):
		if self._position is None:
			return "{:8s} ???".format(self.name)
	
		if self._velocity is None:
			return "{:8s} {:8d} (???)".format(self.name, self._position)

		return "{:8s} {:8d} ({:8d})".format(self.name, self._position, self._velocity)

	@property
	def position(self):
		if self._position_status.wait(0.1):
			return self._position
		
		raise RequestPending("{:8s} has no position yet".format(self.name))

#	@position.setter
#	def position(self, pos):
#		self._position=pos
#		self._position_status=True

	@property
	def velocity(self):
		if self._velocity_status.wait(0.1):
			return self._velocity
		
		raise RequestPending("{:8s} has no velocity yet".format(self.name))

#	@velocity.setter
#	def velocity(self, vel):
#		self._velocity=vel
#		self._velocity_status=True

	def read_position(self):
		self._position_status.clear()

		with self._rc._port_lock:
			if (self.m_nr == 1):
				ret=self._rc.ReadEncM1(self.addr)
			else:
				ret=self._rc.ReadEncM2(self.addr)

		if ret[0]:
			self._position=ret[1]
			self._position_status.set()
			if (self._position > (self._target_position - DEFAULT_TOLERANCE)) and (self._position < (self._target_position + DEFAULT_TOLERANCE)):
				self._target_position_status.set()

	def read_velocity(self):
		self._velocity_status.clear()

		with self._rc._port_lock:
			if (self.m_nr == 1):
				ret=self._rc.ReadSpeedM1(self.addr)
			else:
				ret=self._rc.ReadSpeedM2(self.addr)

		if ret[0]:
			self._velocity=ret[1]
			self._velocity_status.set()
			if (self._velocity > (self._target_velocity - DEFAULT_TOLERANCE)) and (self._velocity < (self._target_velocity + DEFAULT_TOLERANCE)):
				self._target_velocity_status.set()

	@property
	def target_position(self):
		return self._target_position
	
	@target_position.setter
	def target_position(self, pos):
		self._target_position = pos
		with self._rc._port_lock:
			if (self.m_nr == 1):
				ret = self._rc.SpeedAccelDeccelPositionM1(self.addr, self.default_acc, self.default_spd, self.default_acc, self._target_position, 1)
			else:
				ret = self._rc.SpeedAccelDeccelPositionM2(self.addr, self.default_acc, self.default_spd, self.default_acc, self._target_position, 1)

		if ret:
			self._target_position_status.clear()

	@property
	def target_velocity(self):
		return self._target_velocity
	
	@target_velocity.setter
	def target_velocity(self, vel):
		self._target_velocity = vel
		with self._rc._port_lock:
			if (self.m_nr == 1):
				ret = self._rc.SpeedAccelM1(self.addr, self.default_acc, self._target_velocity)
			else:
				ret = self._rc.SpeedAccelM2(self.addr, self.default_acc, self._target_velocity)

		if ret:
			self._target_velocity_status.clear()

	def is_done(self):
#		return (self._target_velocity_status.is_set() and self._target_position_status.is_set())
		return self._target_position_status.is_set()


class DiffTransmission(object):
	def __init__(self, this_axis, other_axis):
		if not (isinstance(this_axis, Axis) and isinstance(other_axis, Axis)):
			raise TypeError("Expected two Axis instances. Got {}, {}".format(type(this_axis).__name__, type(other_axis).__name__))

		self.this = this_axis
		self.other = other_axis

	@property
	def position(self):
		if self.this.m_nr == 1:
			pos = (self.this.position + self.other.position) / 2
		else:
			pos = (self.this.position - self.other.position) / 2

		return pos

	@property
	def velocity(self):
		if self.this.m_nr == 1:
			vel = self.this.velocity + self.other.velocity
		else:
			vel = self.this.velocity - self.other.velocity

		return vel

	@property
	def target_position(self):
		if self.this.m_nr == 1:
			pos = (self.this.target_position + self.other.target_position) / 2
		else:
			pos = (self.this.target_position - self.other.target_position) /2

		return pos

	@target_position.setter
	def target_position(self, pos):
		diff = pos - self.this.target_position

		if self.this.m_nr == 1:
			self.this.target_position += diff
			self.other.target_position += diff
		else:
			self.this.target_position += diff
			self.other.target_position -= diff


	@property
	def target_velocity(self):
		if self.this.m_nr == 1:
			vel = self.this.target_velocity + self.other.target_velocity
		else:
			vel = self.this.target_velocity - self.other.target_velocity

		return vel

	@target_velocity.setter
	def target_velocity(self, vel):
		diff = vel - self.this.target_velocity

		if self.this.m_nr == 1:
			self.this.target_velocity += diff
			self.other.target_velocity += diff
		else:
			self.this.target_velocity += diff
			self.other.target_velocity -= diff

	def is_done(self):
		return (self.this.is_done() and self.other.is_done())


# class DiffAxis(Axis):
# 	def __init__(self, rc, name, addr, this_m_nr, other_m_nr, default_spd=5000, default_acc=10000):
# 		super(DiffAxis, self).__init__(rc, name, addr, this_m_nr, default_spd, default_acc)

# 		self.om_nr=other_m_nr

# 		if (self.om_nr < 1) or (self.om_nr > 2):
# 			raise ValueError("Motor-Number must be 1 or 2")

# 	def read_position(self):
# 		self._position_status.clear()

# 		with self._rc._port_lock:
# 			if (self.m_nr == 1):
# 				this_ret=self._rc.ReadEncM1(self.addr)
# 			else:
# 				this_ret=self._rc.ReadEncM2(self.addr)

# 		if not this_ret[0]:
# 			return

# 		with self._rc._port_lock:
# 			if (self.om_nr == 1):
# 				other_ret=self._rc.ReadEncM1(self.addr)
# 			else:
# 				other_ret=self._rc.ReadEncM2(self.addr)

# 		if not other_ret[0]:
# 			return

# 		if (self.om_nr == 1):
# 			self._position=this_ret[1] - other_ret[1]
# 		else:
# 			self._position=this_ret[1] + other_ret[1]

# 		self._position_status.set()

# 	def read_velocity(self):
# 		self._velocity_status.clear()

# 		with self._rc._port_lock:
# 			if (self.m_nr == 1):
# 				this_ret=self._rc.ReadSpeedM1(self.addr)
# 			else:
# 				this_ret=self._rc.ReadSpeedM2(self.addr)

# 		if not this_ret[0]:
# 			return

# 		with self._rc._port_lock:
# 			if (self.om_nr == 1):
# 				other_ret=self._rc.ReadSpeedM1(self.addr)
# 			else:
# 				other_ret=self._rc.ReadSpeedM2(self.addr)

# 		if not other_ret[0]:
# 			return

# 		if (self.om_nr == 1):
# 			self._velocity=this_ret[1] - other_ret[1]
# 		else:
# 			self._velocity=this_ret[1] + other_ret[1]

# 		self._velocity_status.set()


# 	@target_position.setter
# 	def target_position(self, pos):
# 		self._target_position = pos
# 		with self._rc._port_lock:
# 			if (self.m_nr == 1):
# 				ret = self._rc.SpeedAccelDeccelPositionM1(self.addr, self.default_acc, self.default_spd, self.default_acc, self._target_position, 1)
# 			else:
# 				ret = self._rc.SpeedAccelDeccelPositionM2(self.addr, self.default_acc, self.default_spd, self.default_acc, self._target_position, 1)

# 		if ret:
# 			self._target_position_status.clear()

# 	@target_velocity.setter
# 	def target_velocity(self, vel):
# 		self._target_velocity = vel
# 		with self._rc._port_lock:
# 			if (self.m_nr == 1):
# 				ret = self._rc.SpeedAccelM1(self.addr, self.default_acc, self._target_velocity)
# 			else:
# 				ret = self._rc.SpeedAccelM2(self.addr, self.default_acc, self._target_velocity)

# 		if ret:
# 			self._target_velocity_status.clear()




class RM501_Control:
	axis_map = (
		("gripper", 128, 1, 5000, 10000),
		("axis 1", 128, 2, 5000, 10000),
		("axis 2", 129, 1, 5000, 10000),
		("axis 3", 129, 2, 5000, 10000),
		("axis 4", 130, 1, 5000, 10000),
		("axis 5", 130, 2, 5000, 10000),
	)

	def __init__(self, serport=DEFAULT_PORT):
		self._rc = Roboclaw(serport, 115200)
		self._rc_polling_thread = Thread(target=self._polling_loop,name="Encoders Polling Thread")

		self.axes = []
		self.addrs = []

		for (name, addr, m_nr, def_spd, def_acc) in self.axis_map:
			self.axes.append(Axis(self._rc, name, addr, m_nr, def_spd, def_acc))

			if addr not in self.addrs:
				self.addrs.append(addr)

		self.diff_axes = [DiffTransmission(self.axes[4], self.axes[5]), DiffTransmission(self.axes[5], self.axes[4])]
	
	def connect(self):
		if hasattr(self._rc, "_port") and self._rc._port.isOpen():
			return 

		self._rc.Open()
#		if not self._rc.Open():
#			raise RuntimeError("Could not open port {}".format(self._rc.comport))

		self.versions = {}
		
		for addr in self.addrs:
			(success, version) = self._rc.ReadVersion(addr)
			if success:
				self.versions[addr] = version
			else:
				raise RuntimeError("GETVERSION on board {} Failed".format(addr))
		

		for (addr, version) in self.versions.items():
			print("Board {} Version: {}".format(addr, version))


		self._run_polling=True
		self._rc_polling_thread.start()
		threadpool.start(worker)


	def _polling_loop(self):
		while self._run_polling:
			for a in self.axes:
				a.read_position()
				a.read_velocity()

			time.sleep(0.05)

	def stop(self):
		print("STOPPING {}".format(self._rc_polling_thread.name))
		self._run_polling=False
		self._rc_polling_thread.join()
		worker.running=False
		waypoint_executor.running=False
		self._rc._port.close()
		print("{} STOPPED".format(self._rc_polling_thread.name))
		







def gripper_moveb():
	rm501.axes[0].target_velocity = DEFAULT_VEL_SLOW
# 	rc.SpeedAccelM1(address1,DEFAULT_ACCEL,DEFAULT_VEL_SLOW)

def gripper_movef():
	rm501.axes[0].target_velocity = -DEFAULT_VEL_SLOW
# 	rc.SpeedAccelM1(address1,DEFAULT_ACCEL,-DEFAULT_VEL_SLOW)

def gripper_stop():
	rm501.axes[0].target_velocity = 0
# 	rc.SpeedAccelM1(address1,DEFAULT_ACCEL,0)

def axis1_moveb():
	rm501.axes[1].target_velocity = DEFAULT_VEL_FAST
# 	rc.SpeedAccelM2(address1,DEFAULT_ACCEL,DEFAULT_VEL_FAST)

def axis1_movef():
	rm501.axes[1].target_velocity = -DEFAULT_VEL_FAST
# 	rc.SpeedAccelM2(address1,DEFAULT_ACCEL,-DEFAULT_VEL_FAST)

def axis1_stop():
	rm501.axes[1].target_velocity = 0
# 	rc.SpeedAccelM2(address1,DEFAULT_ACCEL,0)

def axis2_moveb():
	rm501.axes[2].target_velocity = DEFAULT_VEL_MED
# 	rc.SpeedAccelM1(address2,DEFAULT_ACCEL,DEFAULT_VEL_MED)

def axis2_movef():
	rm501.axes[2].target_velocity = -DEFAULT_VEL_MED
# 	rc.SpeedAccelM1(address2,DEFAULT_ACCEL,-DEFAULT_VEL_MED)

def axis2_stop():
	rm501.axes[2].target_velocity = 0
# 	rc.SpeedAccelM1(address2,DEFAULT_ACCEL,0)

def axis3_moveb():
	rm501.axes[3].target_velocity = DEFAULT_VEL_FAST
# 	rc.SpeedAccelM2(address2,DEFAULT_ACCEL,DEFAULT_VEL_FAST)

def axis3_movef():
	rm501.axes[3].target_velocity = -DEFAULT_VEL_FAST
# 	rc.SpeedAccelM2(address2,DEFAULT_ACCEL,-DEFAULT_VEL_FAST)

def axis3_stop():
	rm501.axes[3].target_velocity = 0
# 	rc.SpeedAccelM2(address2,DEFAULT_ACCEL,0)

def axis4_moveb():
	rm501.diff_axes[0].target_velocity = DEFAULT_VEL_MED
# 	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,DEFAULT_VEL_MED)
# 	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,DEFAULT_VEL_MED)

def axis4_movef():
	rm501.diff_axes[0].target_velocity = -DEFAULT_VEL_MED
# 	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,-DEFAULT_VEL_MED)
# 	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,-DEFAULT_VEL_MED)

def axis4_stop():
	rm501.diff_axes[0].target_velocity = 0
# 	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,0)
# 	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,0)

def axis5_moveb():
	rm501.diff_axes[1].target_velocity = DEFAULT_VEL_MED
# 	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,-DEFAULT_VEL_MED)
# 	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,DEFAULT_VEL_MED)

def axis5_movef():
	rm501.diff_axes[1].target_velocity = -DEFAULT_VEL_MED
# 	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,DEFAULT_VEL_MED)
# 	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,-DEFAULT_VEL_MED)

def axis5_stop():
	rm501.diff_axes[1].target_velocity = 0
# 	rc.SpeedAccelM1(address3,DEFAULT_ACCEL,0)
# 	rc.SpeedAccelM2(address3,DEFAULT_ACCEL,0)


class WaypointTableWidget(QtWidgets.QTableWidget):

	def import_csv(self):
		path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')
		if path[0] != '':
			with open(path[0], 'rU') as csv_file:
				self.setRowCount(0)
				self.setColumnCount(7)
				my_file = csv.reader(csv_file, dialect='excel')
				for row_data in my_file:
					row = self.rowCount()
					self.insertRow(row)
#					if len(row_data) > 10:
#						self.setColumnCount(len(row_data))
					for column, stuff in enumerate(row_data):
						item = QtWidgets.QTableWidgetItem(stuff)
						self.setItem(row, column, item)

	def export_csv(self):
		path = QtWidgets.QFileDialog.getSaveFileName(self, 'Save CSV', os.getenv('HOME'), 'CSV(*.csv)')
		if path[0] != '':
			with open(path[0], 'w') as csv_file:
				writer = csv.writer(csv_file, dialect='excel')
				for row in range(self.rowCount()):
					row_data = []
					for column in range(self.columnCount()):
						item = self.item(row, column)
						if item is not None:
							row_data.append(item.text())
						else:
							row_data.append('')

					print(row_data)
					writer.writerow(row_data)


class Ui_Dialog(object):
	def setupUi(self, Dialog):
		Dialog.setObjectName("Dialog")
		Dialog.resize(1592, 926)
		self.pushButton = QtWidgets.QPushButton(Dialog)
		self.pushButton.setGeometry(QtCore.QRect(180, 630, 150, 48))
		self.pushButton.setObjectName("pushButton")
		self.pushButton_2 = QtWidgets.QPushButton(Dialog)
		self.pushButton_2.setGeometry(QtCore.QRect(480, 630, 150, 48))
		self.pushButton_2.setObjectName("pushButton_2")
		self.pushButton_3 = QtWidgets.QPushButton(Dialog)
		self.pushButton_3.setGeometry(QtCore.QRect(180, 560, 150, 48))
		self.pushButton_3.setObjectName("pushButton_3")
		self.pushButton_4 = QtWidgets.QPushButton(Dialog)
		self.pushButton_4.setGeometry(QtCore.QRect(480, 560, 150, 48))
		self.pushButton_4.setObjectName("pushButton_4")
		self.pushButton_5 = QtWidgets.QPushButton(Dialog)
		self.pushButton_5.setGeometry(QtCore.QRect(180, 490, 150, 48))
		self.pushButton_5.setObjectName("pushButton_5")
		self.pushButton_6 = QtWidgets.QPushButton(Dialog)
		self.pushButton_6.setGeometry(QtCore.QRect(480, 490, 150, 48))
		self.pushButton_6.setObjectName("pushButton_6")
		self.pushButton_7 = QtWidgets.QPushButton(Dialog)
		self.pushButton_7.setGeometry(QtCore.QRect(180, 420, 150, 48))
		self.pushButton_7.setObjectName("pushButton_7")
		self.pushButton_8 = QtWidgets.QPushButton(Dialog)
		self.pushButton_8.setGeometry(QtCore.QRect(480, 420, 150, 48))
		self.pushButton_8.setObjectName("pushButton_8")
		self.pushButton_9 = QtWidgets.QPushButton(Dialog)
		self.pushButton_9.setGeometry(QtCore.QRect(180, 350, 150, 48))
		self.pushButton_9.setObjectName("pushButton_9")
		self.pushButton_10 = QtWidgets.QPushButton(Dialog)
		self.pushButton_10.setGeometry(QtCore.QRect(480, 350, 150, 48))
		self.pushButton_10.setObjectName("pushButton_10")
		self.pushButton_11 = QtWidgets.QPushButton(Dialog)
		self.pushButton_11.setGeometry(QtCore.QRect(460, 30, 170, 48))
		self.pushButton_11.setObjectName("pushButton_11")
		self.pushButton_12 = QtWidgets.QPushButton(Dialog)
		self.pushButton_12.setGeometry(QtCore.QRect(180, 280, 150, 48))
		self.pushButton_12.setObjectName("pushButton_12")
		self.pushButton_13 = QtWidgets.QPushButton(Dialog)
		self.pushButton_13.setGeometry(QtCore.QRect(480, 280, 150, 48))
		self.pushButton_13.setObjectName("pushButton_13")
		self.pushButton_14 = QtWidgets.QPushButton(Dialog)
		self.pushButton_14.setGeometry(QtCore.QRect(240, 30, 170, 48))
		self.pushButton_14.setObjectName("pushButton_14")
		self.pushButton_15 = QtWidgets.QPushButton(Dialog)
		self.pushButton_15.setGeometry(QtCore.QRect(20, 750, 240, 121))
		self.pushButton_15.setObjectName("pushButton_15")
		self.pushButton_16 = QtWidgets.QPushButton(Dialog)
		self.pushButton_16.setGeometry(QtCore.QRect(30, 30, 151, 48))
		self.pushButton_16.setObjectName("pushButton_16")
		self.label = QtWidgets.QLabel(Dialog)
		self.label.setGeometry(QtCore.QRect(340, 640, 130, 31))
		self.label.setAlignment(QtCore.Qt.AlignCenter)
		self.label.setObjectName("label")
		self.label_2 = QtWidgets.QLabel(Dialog)
		self.label_2.setGeometry(QtCore.QRect(340, 570, 130, 34))
		self.label_2.setAlignment(QtCore.Qt.AlignCenter)
		self.label_2.setObjectName("label_2")
		self.label_3 = QtWidgets.QLabel(Dialog)
		self.label_3.setGeometry(QtCore.QRect(340, 500, 130, 34))
		self.label_3.setAlignment(QtCore.Qt.AlignCenter)
		self.label_3.setObjectName("label_3")
		self.label_4 = QtWidgets.QLabel(Dialog)
		self.label_4.setGeometry(QtCore.QRect(340, 430, 130, 34))
		self.label_4.setAlignment(QtCore.Qt.AlignCenter)
		self.label_4.setObjectName("label_4")
		self.label_5 = QtWidgets.QLabel(Dialog)
		self.label_5.setGeometry(QtCore.QRect(340, 360, 130, 34))
		self.label_5.setAlignment(QtCore.Qt.AlignCenter)
		self.label_5.setObjectName("label_5")
		self.label_6 = QtWidgets.QLabel(Dialog)
		self.label_6.setGeometry(QtCore.QRect(340, 290, 130, 34))
		self.label_6.setAlignment(QtCore.Qt.AlignCenter)
		self.label_6.setObjectName("label_6")
		self.spinBox = QtWidgets.QSpinBox(Dialog)
		self.spinBox.setGeometry(QtCore.QRect(512, 100, 121, 49))
		self.spinBox.setObjectName("spinBox")
		self.spinBox_2 = QtWidgets.QSpinBox(Dialog)
		self.spinBox_2.setGeometry(QtCore.QRect(512, 150, 121, 49))
		self.spinBox_2.setObjectName("spinBox_2")
		self.spinBox_3 = QtWidgets.QSpinBox(Dialog)
		self.spinBox_3.setGeometry(QtCore.QRect(512, 200, 121, 49))
		self.spinBox_3.setObjectName("spinBox_3")
		self.lineEdit = QtWidgets.QLineEdit(Dialog)
		self.lineEdit.setGeometry(QtCore.QRect(10, 630, 150, 42))
		self.lineEdit.setObjectName("lineEdit")
		self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
		self.lineEdit_2.setGeometry(QtCore.QRect(10, 560, 150, 42))
		self.lineEdit_2.setObjectName("lineEdit_2")
		self.lineEdit_3 = QtWidgets.QLineEdit(Dialog)
		self.lineEdit_3.setGeometry(QtCore.QRect(10, 420, 150, 42))
		self.lineEdit_3.setObjectName("lineEdit_3")
		self.lineEdit_4 = QtWidgets.QLineEdit(Dialog)
		self.lineEdit_4.setGeometry(QtCore.QRect(10, 490, 150, 42))
		self.lineEdit_4.setObjectName("lineEdit_4")
		self.lineEdit_5 = QtWidgets.QLineEdit(Dialog)
		self.lineEdit_5.setGeometry(QtCore.QRect(10, 280, 150, 42))
		self.lineEdit_5.setObjectName("lineEdit_5")
		self.lineEdit_6 = QtWidgets.QLineEdit(Dialog)
		self.lineEdit_6.setGeometry(QtCore.QRect(10, 350, 150, 42))
		self.lineEdit_6.setObjectName("lineEdit_6")
		self.pushButton_17 = QtWidgets.QPushButton(Dialog)
		self.pushButton_17.setGeometry(QtCore.QRect(270, 750, 101, 61))
		self.pushButton_17.setObjectName("pushButton_17")
		self.pushButton_18 = QtWidgets.QPushButton(Dialog)
		self.pushButton_18.setGeometry(QtCore.QRect(270, 810, 101, 61))
		self.pushButton_18.setObjectName("pushButton_18")
		self.tableWidget = WaypointTableWidget(Dialog)
		self.tableWidget.setGeometry(QtCore.QRect(650, 30, 941, 831))
		self.tableWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
		self.tableWidget.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustToContents)
		self.tableWidget.setAlternatingRowColors(True)
		self.tableWidget.setRowCount(0)
		self.tableWidget.setColumnCount(7)
		self.tableWidget.setObjectName("tableWidget")
		item = QtWidgets.QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(0, item)
		item = QtWidgets.QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(1, item)
		item = QtWidgets.QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(2, item)
		item = QtWidgets.QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(3, item)
		item = QtWidgets.QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(4, item)
		item = QtWidgets.QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(5, item)
		item = QtWidgets.QTableWidgetItem()
		self.tableWidget.setHorizontalHeaderItem(6, item)
		self.tableWidget.horizontalHeader().setDefaultSectionSize(130)
		self.label_7 = QtWidgets.QLabel(Dialog)
		self.label_7.setGeometry(QtCore.QRect(368, 110, 141, 34))
		self.label_7.setObjectName("label_7")
		self.label_8 = QtWidgets.QLabel(Dialog)
		self.label_8.setGeometry(QtCore.QRect(368, 160, 141, 34))
		self.label_8.setObjectName("label_8")
		self.label_9 = QtWidgets.QLabel(Dialog)
		self.label_9.setGeometry(QtCore.QRect(368, 210, 141, 34))
		self.label_9.setObjectName("label_9")
		self.checkBox = QtWidgets.QCheckBox(Dialog)
		self.checkBox.setGeometry(QtCore.QRect(400, 750, 175, 40))
		self.checkBox.setObjectName("checkBox")
		self.pushButton_19 = QtWidgets.QPushButton(Dialog)
		self.pushButton_19.setGeometry(QtCore.QRect(1320, 870, 261, 48))
		self.pushButton_19.setObjectName("pushButton_19")
		self.pushButton_20 = QtWidgets.QPushButton(Dialog)
		self.pushButton_20.setGeometry(QtCore.QRect(650, 870, 261, 48))
		self.pushButton_20.setObjectName("pushButton_20")

		self.threadpool_waypoints = QtCore.QThreadPool()


		self.retranslateUi(Dialog)
		QtCore.QMetaObject.connectSlotsByName(Dialog)

	def retranslateUi(self, Dialog):
		_translate = QtCore.QCoreApplication.translate
		Dialog.setWindowTitle(_translate("Dialog", "RM501 Control"))
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
		self.pushButton_15.setText(_translate("Dialog", "Record Position"))
		self.pushButton_16.setText(_translate("Dialog", "Nest "))
		self.label.setText(_translate("Dialog", "0"))
		self.label_2.setText(_translate("Dialog", "0"))
		self.label_3.setText(_translate("Dialog", "0"))
		self.label_4.setText(_translate("Dialog", "0"))
		self.label_5.setText(_translate("Dialog", "0"))
		self.label_6.setText(_translate("Dialog", "0"))
		self.pushButton_17.setText(_translate("Dialog", "Start"))
		self.pushButton_18.setText(_translate("Dialog", "Stop"))
		self.tableWidget.setSortingEnabled(False)
		item = self.tableWidget.horizontalHeaderItem(0)
		item.setText(_translate("Dialog", "Gripper"))
		item = self.tableWidget.horizontalHeaderItem(1)
		item.setText(_translate("Dialog", "Axis 1"))
		item = self.tableWidget.horizontalHeaderItem(2)
		item.setText(_translate("Dialog", "Axis 2"))
		item = self.tableWidget.horizontalHeaderItem(3)
		item.setText(_translate("Dialog", "Axis 3"))
		item = self.tableWidget.horizontalHeaderItem(4)
		item.setText(_translate("Dialog", "Axis 4"))
		item = self.tableWidget.horizontalHeaderItem(5)
		item.setText(_translate("Dialog", "Axis 5"))
		item = self.tableWidget.horizontalHeaderItem(6)
		item.setText(_translate("Dialog", "MaxTime"))
		self.label_7.setText(_translate("Dialog", "PosToler"))
		self.label_8.setText(_translate("Dialog", "SerialTO"))
		self.label_9.setText(_translate("Dialog", "Max Time"))
		self.checkBox.setText(_translate("Dialog", "Loop"))
		self.pushButton_19.setText(_translate("Dialog", "Export CSV"))
		self.pushButton_20.setText(_translate("Dialog", "Import CSV"))



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
		self.pushButton_15.clicked.connect(self.record_position)
		self.pushButton_11.clicked.connect(rm501.connect)

		self.pushButton_17.clicked.connect(self.waypoint_start)
		self.pushButton_18.clicked.connect(self.waypoint_stop)
		self.pushButton_19.clicked.connect(self.tableWidget.export_csv)
		self.pushButton_20.clicked.connect(self.tableWidget.import_csv)




	def record_position(self,Dialog):
		

		self.tableWidget.insertRow(self.tableWidget.rowCount())
		last_row=self.tableWidget.rowCount()-1
		items=[]

		items.append(QtWidgets.QTableWidgetItem(str(rm501.axes[0].position)))
		items.append(QtWidgets.QTableWidgetItem(str(rm501.axes[1].position)))
		items.append(QtWidgets.QTableWidgetItem(str(rm501.axes[2].position)))
		items.append(QtWidgets.QTableWidgetItem(str(rm501.axes[3].position)))
		items.append(QtWidgets.QTableWidgetItem(str(rm501.axes[4].position)))
		items.append(QtWidgets.QTableWidgetItem(str(rm501.axes[5].position)))
		items.append(QtWidgets.QTableWidgetItem(str(self.spinBox_3.value())))


		self.tableWidget.setCurrentCell(last_row,0)

		for n in range(len(items)):

			self.tableWidget.setItem(last_row,n, items[n])
		

		self.tableWidget.scrollToItem(self.tableWidget.currentItem())


	def start_secuence(self,Dialog):


		self.tableWidget.setCurrentCell(0,0)

		rm501.diff_axes[0].target_position=10000
		rm501.diff_axes[0].target_position=10000
		#rm501.diff_axes[0].target_position=int(self.tableWidget.item(0,4).text())
		#rm501.diff_axes[1].target_position=int(self.tableWidget.item(0,5).text())

		time.sleep(3)
		#while not rm501.diff_axes[4].is_done():
		#	time.sleep(0.1)

		rm501.diff_axes[0].target_position=int(self.tableWidget.item(1,4).text())
		rm501.diff_axes[1].target_position=int(self.tableWidget.item(1,5).text())

	def waypoint_start(self,Dialog):
		self.waypoint_executor = Waypoint_Executor(self)
		self.threadpool_waypoints.start(self.waypoint_executor)

	def waypoint_stop(self,Dialog):
		self.waypoint_executor.stop()
		

class Postion_Displayer(QtCore.QRunnable):
		
	def __init__(self, dialog):
		if not isinstance(dialog,Ui_Dialog):
			raise TypeError("Given dialog argument must be an instance of Ui_Dialog.")

		super(QtCore.QRunnable,self).__init__()
			
		self.dialog=dialog
		self.running=True
		
	@QtCore.pyqtSlot()
	def run(self):
		while self.running:
			try:
				_translate = QtCore.QCoreApplication.translate
				self.dialog.label.setText(_translate("Dialog", str(rm501.axes[1].position)))
				self.dialog.label_2.setText(_translate("Dialog", str(rm501.axes[2].position)))
				self.dialog.label_3.setText(_translate("Dialog", str(rm501.axes[3].position)))
				self.dialog.label_4.setText(_translate("Dialog", str(rm501.diff_axes[0].position)))
				self.dialog.label_5.setText(_translate("Dialog", str(rm501.diff_axes[1].position)))
				self.dialog.label_6.setText(_translate("Dialog", str(rm501.axes[0].position)))
			except RequestPending as e:
	#			pass
				print("timeout on {}".format(str(e)))
			

class Waypoint_Executor(QtCore.QRunnable):

	def __init__(self,dialog):
		if not isinstance(dialog,Ui_Dialog):
			raise TypeError("Given dialog argument must be an instance of Ui_Dialog.")
		

		super(QtCore.QRunnable,self).__init__()

		self.dialog=dialog
		self.running=True
		print(str("Waypoint executor running."))


	@QtCore.pyqtSlot()
	def run(self):


		self.dialog.tableWidget.scrollToItem(self.dialog.tableWidget.currentItem())
		#self.dialog.tableWidget.setCurrentCell(0,0)

		while self.running:
		
			try:	
				for waypoint_index in range(self.dialog.tableWidget.rowCount()):

					if not self.running:
						break

					waypoint_data=self.read_waypoint(waypoint_index)
					print(str("Waypoint index: {}").format(waypoint_index))
					#waypoint_timer=QtCore.QBasicTimer()

					for axis in range(6):

							if axis is (0):
								rm501.axes[axis].target_velocity=int(self.dialog.tableWidget.item(waypoint_index,axis).text())
								print(str("{}").format(rm501.axes[axis].target_velocity))
								time.sleep(1)
							else:
								rm501.axes[axis].target_position=int(self.dialog.tableWidget.item(waypoint_index,axis).text())
								print(str("{}").format(rm501.axes[axis].target_position))
								#waypoint_timer.start()

					while not rm501.axes[1].is_done() or not rm501.axes[2].is_done() or not rm501.axes[3].is_done() or not rm501.axes[4].is_done() or not rm501.axes[5].is_done():
						
						if not self.running:
							break

						print("Reaching waypoint: {}".format(waypoint_index))
						for done in range(6):
							if rm501.axes[done].is_done():
								print("Axis{}: DONE".format(done))
							else:	
								print("Axis{}: NOT DONE".format(done))


						time.sleep(0.1)

					if (not self.dialog.checkBox.isChecked()) and (waypoint_index == (self.dialog.tableWidget.rowCount() - 1)):
						self.stop()

			except RequestPending as e:
				print("timeout on {}".format(str(e)))

	def stop(self):
		self.running=False
		for axis in range(6):
			rm501.axes[axis].target_velocity=0
	
	def read_waypoint(self,waypoint_index):

		waypoint_data=[]
		
		for column in range(self.dialog.tableWidget.columnCount()):
			waypoint_data.append(int(self.dialog.tableWidget.item(waypoint_index,column).text()))
		return waypoint_data


if __name__ == "__main__":
	import sys
	
	rm501 = RM501_Control()

	app = QtWidgets.QApplication(sys.argv)
	Dialog = QtWidgets.QDialog()
	threadpool = QtCore.QThreadPool()
#	threadpool_waypoints = QtCore.QThreadPool()
	print("Multithreading with maximum {} threads".format(threadpool.maxThreadCount()))
	ui = Ui_Dialog()
	ui.setupUi(Dialog)



	worker = Postion_Displayer(ui)
#	waypoint_executor = Waypoint_Executor(ui)

	Dialog.show()
	exit_code = app.exec_()
	rm501.stop()
	sys.exit(exit_code)

