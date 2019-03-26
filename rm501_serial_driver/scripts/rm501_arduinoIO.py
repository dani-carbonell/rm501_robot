# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'trigger_test.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import serial
import serial
import time, threading

DEFAULT_PORT_ARDUINO="/dev/arduino_nano"


class rm501_ArduinoIO:
	def __init__(self, comport, rate, timeout=0.01, retries=3):
		self.comport = comport
		self.rate = rate
		self.timeout = timeout;
		self._trystimeout = retries
		self._crc = 0;

	def Open(self):
		self._port = serial.Serial(port=self.comport, baudrate=self.rate, timeout=1, interCharTimeout=self.timeout)



	class Arduino_Listener(QtCore.QRunnable):

		def __init__(self,dialog):
			if not isinstance(dialog,Ui_Dialog):
				raise TypeError("Given dialog argument must be an instance of Ui_Dialog.")
			
			super(QtCore.QRunnable,self).__init__()

			self.dialog=dialog
			self.running=True
			print(str("Arduino Listener running."))


	#@QtCore.pyqtSlot()
	#def run(self):



