# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from scanner import PlateScanner
import cv2
import config
import numpy as np
import sys


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.img_url = ""
        self.config = None

        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1159, 565)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.labelTitle = QtWidgets.QLabel(self.centralwidget)
        self.labelTitle.setGeometry(QtCore.QRect(30, 30, 441, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.labelTitle.setFont(font)
        self.labelTitle.setObjectName("labelTitle")
        
        self.lineImgUrl = QtWidgets.QLineEdit(self.centralwidget)
        self.lineImgUrl.setGeometry(QtCore.QRect(30, 460, 621, 23))
        self.lineImgUrl.setReadOnly(True)
        self.lineImgUrl.setObjectName("lineImgUrl")
        
        self.btnGetImage = QtWidgets.QPushButton(self.centralwidget)
        self.btnGetImage.setGeometry(QtCore.QRect(660, 460, 75, 23))
        self.btnGetImage.setObjectName("btnGetImage")
        
        self.imgStart = QtWidgets.QLabel(self.centralwidget)
        self.imgStart.setGeometry(QtCore.QRect(30, 90, 511, 351))
        self.imgStart.setFrameShape(QtWidgets.QFrame.Box)
        self.imgStart.setText("No Plate")
        self.imgStart.setAlignment(QtCore.Qt.AlignCenter)
        self.imgStart.setObjectName("imgStart")
        
        self.btnStartScan = QtWidgets.QPushButton(self.centralwidget)
        self.btnStartScan.setGeometry(QtCore.QRect(777, 460, 75, 23))
        self.btnStartScan.setObjectName("btnStartScan")
        
        self.imgPlate = QtWidgets.QLabel(self.centralwidget)
        self.imgPlate.setGeometry(QtCore.QRect(550, 350, 301, 91))
        self.imgPlate.setFrameShape(QtWidgets.QFrame.Box)
        self.imgPlate.setText("No Plate")
        self.imgPlate.setAlignment(QtCore.Qt.AlignCenter)
        self.imgPlate.setObjectName("imgPlate")
        
        self.imgResult = QtWidgets.QLabel(self.centralwidget)
        self.imgResult.setGeometry(QtCore.QRect(550, 90, 301, 251))
        self.imgResult.setFrameShape(QtWidgets.QFrame.Box)
        self.imgResult.setText("No Plate")
        self.imgResult.setAlignment(QtCore.Qt.AlignCenter)
        self.imgResult.setObjectName("imgResult")
        
        self.settingsGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.settingsGroup.setGeometry(QtCore.QRect(870, 80, 261, 361))
        self.settingsGroup.setObjectName("settingsGroup")
        
        self.chkSaveImages = QtWidgets.QCheckBox(self.settingsGroup)
        self.chkSaveImages.setGeometry(QtCore.QRect(20, 100, 91, 16))
        self.chkSaveImages.setObjectName("chkSaveImages")
        
        self.lineTesseract = QtWidgets.QLineEdit(self.settingsGroup)
        self.lineTesseract.setGeometry(QtCore.QRect(20, 50, 141, 20))
        self.lineTesseract.setText("")
        self.lineTesseract.setReadOnly(True)
        self.lineTesseract.setObjectName("lineTesseract")
        
        self.btnGetConfig = QtWidgets.QPushButton(self.settingsGroup)
        self.btnGetConfig.setGeometry(QtCore.QRect(170, 50, 75, 23))
        self.btnGetConfig.setObjectName("btnGetConfig")
        
        self.labelTesseract = QtWidgets.QLabel(self.settingsGroup)
        self.labelTesseract.setGeometry(QtCore.QRect(20, 30, 121, 16))
        self.labelTesseract.setObjectName("labelTesseract")
        
        self.chkSteps = QtWidgets.QCheckBox(self.settingsGroup)
        self.chkSteps.setGeometry(QtCore.QRect(20, 130, 181, 16))
        self.chkSteps.setObjectName("chkSteps")
        
        self.labelMadeBy = QtWidgets.QLabel(self.centralwidget)
        self.labelMadeBy.setGeometry(QtCore.QRect(1000, 520, 121, 16))
        self.labelMadeBy.setWordWrap(False)
        self.labelMadeBy.setObjectName("labelMadeBy")
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1078, 21))
        self.menubar.setObjectName("menubar")
        
        MainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
        
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.btnGetImage.clicked.connect(self.set_start_img)
        self.btnStartScan.clicked.connect(self.start_scan)
        self.btnGetConfig.clicked.connect(self.set_tesseract_url)
        self.chkSteps.stateChanged.connect(lambda: config.set_steps(self.chkSteps.isChecked()))
        self.chkSaveImages.stateChanged.connect(lambda: config.set_save_images(self.chkSaveImages.isChecked()))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("Automatic Number Plate Recognition", "Automatic Number Plate Recognition System"))
        self.labelTitle.setText(_translate("MainWindow", "Automatic Number Plate Recognition System"))
        
        self.lineImgUrl.setPlaceholderText("Select an image to be scanned")
        self.labelMadeBy.setText("<html><head/><body><p align=\"center\">Made by: TSE Group 32</p></body></html>")

        self.btnGetImage.setText("Select...")
        self.btnStartScan.setText("Scan")
        self.settingsGroup.setTitle("Settings")
        self.chkSaveImages.setText("Save images?")
        self.btnGetConfig.setText("Select...")
        self.labelTesseract.setText(_translate("MainWindow", "Tesseract.exe location"))
        self.chkSteps.setText(_translate("MainWindow", "Show processing steps? "))

        cfg = config.check_config()
        if cfg: 
            if cfg["tesseract_url"]: 
                self.lineTesseract.setPlaceholderText(cfg["tesseract_url"])
            if cfg["show_steps"]:
                self.chkSteps.setChecked(True)
            if cfg["save_images"]:
                self.chkSaveImages.setChecked(True)

        else:
            self.lineTesseract.setPlaceholderText("...")

    def show_message(self, message_type, title, message):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)

        if message_type == "Error":
            msg.setIcon(QtWidgets.QMessageBox.Critical)

        msg.setWindowTitle(title)
        msg.setText(f"{message_type}\n\n{message}")

        msg.exec_()

    def start_scan(self):
        if self.img_url == "" or self.img_url == None:
            self.show_message("Error", "Image Error", "No image selected!")
            return

        cfg = config.check_config()
        if cfg:
            if not cfg["tesseract_url"]:
                self.show_message("Error", "error", "Tesseract.exe not found.")
                return

            _, plate, end_img, plate_img = PlateScanner(self.img_url,cfg).scan_plate()
            print("scanned!")
            if plate is not None and end_img is not None and plate_img is not None:
                end_img = self.convert_image(end_img)
                plate_img = self.convert_image(plate_img)
         
                self.set_image(self.imgResult, end_img)
                self.set_image(self.imgPlate, plate_img)
            else:
                self.imgResult.setText("Plate not detected")
                self.imgPlate.setText("Plate not detected")
        else:
            self.show_message("Error", "Config error", "Invalid configuration. Please try again.")

    def set_tesseract_url(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select File", "", "tesseract.exe")
        if config.set_tesseract_url(fileName):
           self.lineTesseract.setText(fileName)

    def set_start_img(self):
        self.img_url, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Image", "", "Image Files (*.png *.jpg *.jpeg)")
        self.lineImgUrl.setText(self.img_url)

        if self.img_url:
            pixmap = QtGui.QPixmap(self.img_url)
            pixmap = pixmap.scaled(self.imgStart.width(), self.imgStart.height(), QtCore.Qt.KeepAspectRatio)
            self.imgStart.setPixmap(pixmap)
            

    def convert_image(self, img):
        gray_color_table = [QtGui.qRgb(i, i, i) for i in range(256)]
        if img is None:
            return QtGui.QImage()

        if img.dtype == np.float64:
            img=np.uint8(img)
        
        if img.dtype == np.uint8:

            #if image doesnt have colour channel
            if len(img.shape) == 2:
                end_img = QtGui.QImage(bytes(img.data), img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_Indexed8)
                end_img.setColorTable(gray_color_table)
                return end_img
            
            elif len(img.shape) == 3:
                if img.shape[2] == 3:
                    end_img = QtGui.QImage(bytes(img.data), img.shape[1], img.shape[0], img.shape[1] * 3, QtGui.QImage.Format_RGB888).rgbSwapped() 
                    return end_img

    def set_image(self, img_widget, img):
        pixmap = QtGui.QPixmap(img)
        pixmap = pixmap.scaled(img_widget.width(), img_widget.height(), QtCore.Qt.KeepAspectRatio)
        img_widget.setPixmap(pixmap)
      
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
