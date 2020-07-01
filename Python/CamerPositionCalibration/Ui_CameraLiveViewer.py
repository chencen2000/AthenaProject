# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\projects\github\AthenaProject\Python\CamerPositionCalibration\CameraLiveViewer.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(560, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.topButton = QtWidgets.QRadioButton(self.centralwidget)
        self.topButton.setObjectName("topButton")
        self.verticalLayout.addWidget(self.topButton)
        self.lsideButton = QtWidgets.QRadioButton(self.centralwidget)
        self.lsideButton.setObjectName("lsideButton")
        self.verticalLayout.addWidget(self.lsideButton)
        self.ssdieButton = QtWidgets.QRadioButton(self.centralwidget)
        self.ssdieButton.setObjectName("ssdieButton")
        self.verticalLayout.addWidget(self.ssdieButton)
        self.settingButton = QtWidgets.QPushButton(self.centralwidget)
        self.settingButton.setObjectName("settingButton")
        self.verticalLayout.addWidget(self.settingButton)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.zoomInButton = QtWidgets.QPushButton(self.centralwidget)
        self.zoomInButton.setObjectName("zoomInButton")
        self.horizontalLayout_4.addWidget(self.zoomInButton)
        self.zoomOutButton = QtWidgets.QPushButton(self.centralwidget)
        self.zoomOutButton.setObjectName("zoomOutButton")
        self.horizontalLayout_4.addWidget(self.zoomOutButton)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.calibrateButton = QtWidgets.QPushButton(self.centralwidget)
        self.calibrateButton.setObjectName("calibrateButton")
        self.verticalLayout.addWidget(self.calibrateButton)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.exitButton = QtWidgets.QPushButton(self.centralwidget)
        self.exitButton.setObjectName("exitButton")
        self.verticalLayout.addWidget(self.exitButton)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.scrollArea = QtWidgets.QScrollArea(self.centralwidget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 372, 558))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.scrollAreaWidgetContents)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelImage = QtWidgets.QLabel(self.scrollAreaWidgetContents)
        self.labelImage.setObjectName("labelImage")
        self.horizontalLayout_3.addWidget(self.labelImage)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.horizontalLayout.addWidget(self.scrollArea)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 20)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.exitButton.clicked.connect(MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.topButton.setText(_translate("MainWindow", "Top"))
        self.lsideButton.setText(_translate("MainWindow", "Long Side"))
        self.ssdieButton.setText(_translate("MainWindow", "Short Side"))
        self.settingButton.setText(_translate("MainWindow", "Setting"))
        self.zoomInButton.setText(_translate("MainWindow", "+"))
        self.zoomOutButton.setText(_translate("MainWindow", "-"))
        self.calibrateButton.setText(_translate("MainWindow", "Calibrate"))
        self.exitButton.setText(_translate("MainWindow", "Exit"))
        self.labelImage.setText(_translate("MainWindow", "TextLabel"))
