# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'table_test.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import csv


class Ui_MainWindow(object):
	def setupUi(self, MainWindow):
		MainWindow.setObjectName("MainWindow")
		MainWindow.resize(1344, 923)
		self.centralwidget = QtWidgets.QWidget(MainWindow)
		self.centralwidget.setObjectName("centralwidget")
		self.pushButton = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton.setGeometry(QtCore.QRect(30, 60, 170, 48))
		self.pushButton.setObjectName("pushButton")
		self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
		self.pushButton_2.setGeometry(QtCore.QRect(40, 130, 170, 48))
		self.pushButton_2.setObjectName("pushButton_2")
		self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
		self.tableWidget.setGeometry(QtCore.QRect(240, 10, 1101, 821))
		self.tableWidget.setRowCount(10)
		self.tableWidget.setColumnCount(7)
		self.tableWidget.setObjectName("tableWidget")
		self.tableWidget.horizontalHeader().setDefaultSectionSize(150)
		MainWindow.setCentralWidget(self.centralwidget)
		self.menubar = QtWidgets.QMenuBar(MainWindow)
		self.menubar.setGeometry(QtCore.QRect(0, 0, 1344, 39))
		self.menubar.setObjectName("menubar")
		MainWindow.setMenuBar(self.menubar)
		self.statusbar = QtWidgets.QStatusBar(MainWindow)
		self.statusbar.setObjectName("statusbar")
		MainWindow.setStatusBar(self.statusbar)
		self.clip = QtWidgets.QApplication.clipboard()
		self.clip.setText("hoge")
		self.text = self.clip.text()


		self.retranslateUi(MainWindow)
		QtCore.QMetaObject.connectSlotsByName(MainWindow)


		self.pushButton.clicked.connect(copy_cells)
		self.pushButton_2.clicked.connect(paste_cells)


	def retranslateUi(self, MainWindow):
		_translate = QtCore.QCoreApplication.translate
		MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
		self.pushButton.setText(_translate("MainWindow", "copy"))
		self.pushButton_2.setText(_translate("MainWindow", "paste"))


	def keyPressEvent(self, e):
		if (e.modifiers() & QtCore.Qt.ControlModifier):
			selected = self.tableWidget.selectedRanges()
		
			if e.key() == QtCore.Qt.Key_V:#past
				first_row = selected[0].topRow()
				first_col = selected[0].leftColumn()
		
				#copied text is split by '\n' and '\t' to paste to the cells
				for r, row in enumerate(self.clip.text().split('\n')):
					for c, text in enumerate(row.split('\t')):
						self.tableWidget.setItem(first_row+r, first_col+c, QtWidgets.QTableWidgetItem(text))

		elif e.key() == QtCore.Qt.Key_C: #copy
			s = ""
			for r in xrange(selected[0].topRow(),selected[0].bottomRow()+1):
				for c in xrange(selected[0].leftColumn(),selected[0].rightColumn()+1):
					try:
						s += str(self.tableWidget.item(r,c).text()) + "\t"
					except AttributeError:
						s += "\t"
				s = s[:-1] + "\n" #eliminate last '\t'
			self.clip.setText(s)


def copy_cells():
	CopySelectedCellsAction(ui.tableWidget).copy_cells_to_clipboard()

def paste_cells():
	path = QtWidgets.QFiledialog.getOpenFileName()

class CopySelectedCellsAction(QtWidgets.QAction):
	def __init__(self, table_widget):
		if not isinstance(table_widget, QtWidgets.QTableWidget):
			raise ValueError(str('CopySelectedCellsAction must be initialised with a QTableWidget. A %s was given.' % type(table_widget)))
		super(CopySelectedCellsAction, self).__init__("Copy", table_widget)
		self.setShortcut('Ctrl+C')
		self.triggered.connect(self.copy_cells_to_clipboard)
		self.table_widget = table_widget

	def copy_cells_to_clipboard(self):
		if len(self.table_widget.selectionModel().selectedIndexes()) > 0:
			# sort select indexes into rows and columns
			previous = self.table_widget.selectionModel().selectedIndexes()[0]
			columns = []
			rows = []
			for index in self.table_widget.selectionModel().selectedIndexes():
				if previous.column() != index.column():
					columns.append(rows)
					rows = []
				rows.append(index.data())
				previous = index
			columns.append(rows)    

			# add rows and columns to clipboard            
			clipboard = ""
			nrows = len(columns[0])
			print(nrows)
			ncols = len(columns)
			for r in xrange(nrows):
				for c in xrange(ncols):
					clipboard += columns[c][r]
					if c != (ncols-1):
						clipboard += '\t'
				clipboard += '\n'

			# copy to the system clipboard
			sys_clip = QtWidgets.QApplication.clipboard()
			sys_clip.setText(clipboard)

	def copy_cells_from_clipboard(self):
		if len(self.table_widget.selectionModel().selectedIndexes()) > 0:
			# sort select indexes into rows and columns
			previous = self.table_widget.selectionModel().selectedIndexes()[0]
			columns = []
			rows = []
			for index in self.table_widget.selectionModel().selectedIndexes():
				if previous.column() != index.column():
					columns.append(rows)
					rows = []
				rows.append(index.data())
				previous = index
			columns.append(rows)     

			# add rows and columns to clipboard            
			clipboard = ""
			nrows = len(columns[0])
			ncols = len(columns)
			for r in range(nrows):
				for c in range(ncols):
					clipboard += columns[c][r]
					if c != (ncols-1):
						clipboard += '\t'
				clipboard += '\n'

			# copy to the system clipboard
			sys_clip = QtWidgets.QApplication.clipboard()
			sys_clip.setText(clipboard)

if __name__ == "__main__":
	import sys
	app = QtWidgets.QApplication(sys.argv)
	MainWindow = QtWidgets.QMainWindow()
	ui = Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())

