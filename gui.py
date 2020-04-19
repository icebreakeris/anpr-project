#pylint: disable=no-member

from PyQt5 import QtCore, QtGui, QtWidgets
from scanner import PlateScanner
import cv2
import config
import numpy as np
import sys


class Ui_MainWindow(QtWidgets.QMainWindow):

    def setupUi(self, MainWindow):
        self.img_url = ""

        MainWindow.setWindowTitle("Automatic Number Plate Recognition System")
        MainWindow.setFixedSize(1159, 565)

        self.centralwidget = QtWidgets.QWidget(MainWindow)

        self.labelTitle = QtWidgets.QLabel(self.centralwidget)
        self.labelTitle.setGeometry(QtCore.QRect(30, 30, 1101, 41))
        self.labelTitle.setText("Automatic Number Plate Recognition System")
        
        font = QtGui.QFont()
        font.setPointSize(20)
        self.labelTitle.setFont(font)

        self.lineImgUrl = QtWidgets.QLineEdit(self.centralwidget)
        self.lineImgUrl.setGeometry(QtCore.QRect(30, 460, 621, 23))
        self.lineImgUrl.setReadOnly(True)
        self.lineImgUrl.setPlaceholderText("Select an image to be scanned")

        self.btnGetImage = QtWidgets.QPushButton(self.centralwidget)
        self.btnGetImage.setGeometry(QtCore.QRect(660, 460, 75, 23))
        self.btnGetImage.setText("Select...")

        self.imgStart = QtWidgets.QLabel(self.centralwidget)
        self.imgStart.setGeometry(QtCore.QRect(30, 90, 511, 351))
        self.imgStart.setFrameShape(QtWidgets.QFrame.Box)
        self.imgStart.setText("No Plate")
        self.imgStart.setAlignment(QtCore.Qt.AlignCenter)

        self.btnStartScan = QtWidgets.QPushButton(self.centralwidget)
        self.btnStartScan.setGeometry(QtCore.QRect(777, 460, 75, 23))
        self.btnStartScan.setText("Scan")

        self.imgPlate = QtWidgets.QLabel(self.centralwidget)
        self.imgPlate.setGeometry(QtCore.QRect(550, 350, 301, 91))
        self.imgPlate.setFrameShape(QtWidgets.QFrame.Box)
        self.imgPlate.setText("No Plate")
        self.imgPlate.setAlignment(QtCore.Qt.AlignCenter)

        self.imgResult = QtWidgets.QLabel(self.centralwidget)
        self.imgResult.setGeometry(QtCore.QRect(550, 90, 301, 251))
        self.imgResult.setFrameShape(QtWidgets.QFrame.Box)
        self.imgResult.setText("No Plate")
        self.imgResult.setAlignment(QtCore.Qt.AlignCenter)

        self.settingsGroup = QtWidgets.QGroupBox(self.centralwidget)
        self.settingsGroup.setGeometry(QtCore.QRect(870, 80, 261, 361))
        self.settingsGroup.setTitle("Settings")
  
        self.chkSaveImages = QtWidgets.QCheckBox(self.settingsGroup)
        self.chkSaveImages.setGeometry(QtCore.QRect(20, 100, 221, 16))
        self.chkSaveImages.setText("Save images?")

        self.lineTesseract = QtWidgets.QLineEdit(self.settingsGroup)
        self.lineTesseract.setGeometry(QtCore.QRect(20, 50, 141, 20))
        self.lineTesseract.setReadOnly(True)

        self.btnGetConfig = QtWidgets.QPushButton(self.settingsGroup)
        self.btnGetConfig.setGeometry(QtCore.QRect(170, 50, 75, 23))
        self.btnGetConfig.setText("Select...")

        self.labelTesseract = QtWidgets.QLabel(self.settingsGroup)
        self.labelTesseract.setGeometry(QtCore.QRect(20, 30, 221, 16))
        self.labelTesseract.setText("Tesseract.exe location")

        self.chkSteps = QtWidgets.QCheckBox(self.settingsGroup)
        self.chkSteps.setGeometry(QtCore.QRect(20, 130, 221, 16))
        self.chkSteps.setText("Show processing steps? ")

        self.btnHelp = QtWidgets.QPushButton(self.settingsGroup)
        self.btnHelp.setGeometry(QtCore.QRect(170, 320, 75, 23))
        self.btnHelp.setText("Help")

        self.labelHelp = QtWidgets.QLabel(self.settingsGroup)
        self.labelHelp.setGeometry(QtCore.QRect(50, 320, 100, 16))
        self.labelHelp.setStyleSheet("color: rgb(0, 103, 0);")
        self.labelHelp.setText("Need help?")

        self.labelMadeBy = QtWidgets.QLabel(self.centralwidget)
        self.labelMadeBy.setGeometry(QtCore.QRect(950, 520, 171, 20))
        self.labelMadeBy.setWordWrap(False)
        self.labelMadeBy.setText("<html><head/><body><p align=\"center\">Made by: TSE Group 32</p></body></html>")

        MainWindow.setCentralWidget(self.centralwidget)

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

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.btnGetImage.clicked.connect(self.set_start_img)
        self.btnStartScan.clicked.connect(self.start_scan)
        self.btnGetConfig.clicked.connect(self.set_tesseract_url)
        self.btnHelp.clicked.connect(self.show_help_window)
        self.chkSteps.stateChanged.connect(lambda: config.set_steps(self.chkSteps.isChecked()))
        self.chkSaveImages.stateChanged.connect(lambda: config.set_save_images(self.chkSaveImages.isChecked()))

    def show_help_window(self):
        self.help_window = QtWidgets.QMainWindow()
        self.help_window.ui = Ui_HelpWindow()
        
        #sets up the ui
        self.help_window.ui.setupUi(self.help_window)

        #destroys the window widget once it is closed
        self.help_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.help_window.show() 

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

            _, plate, end_img, plate_img, step_images = PlateScanner(self.img_url,cfg).scan_plate()

            print("scanned!")
            if plate is not None and end_img is not None and plate_img is not None:
                end_img = convert_image(end_img)
                plate_img = convert_image(plate_img)
         
                set_image(self.imgResult, end_img)
                set_image(self.imgPlate, plate_img)
                
                if len(step_images) != 0:
                    self.process_window = QtWidgets.QMainWindow()
                    self.process_window.ui = Ui_ProcessWindow(step_images)
                    self.process_window.ui.setupUi(self.process_window)
                    self.process_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
                    self.process_window.show()
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
            #using opencv for image reading to avoid issues with png images
            pixmap = QtGui.QPixmap(convert_image(cv2.imread(self.img_url)))
            pixmap = pixmap.scaled(self.imgStart.width(), self.imgStart.height(), QtCore.Qt.KeepAspectRatio)
            self.imgStart.setPixmap(pixmap)
            
class Ui_ProcessWindow(QtWidgets.QMainWindow):
    def __init__(self, steps): 
        super().__init__()
        self.step_images = steps
    
    def setupUi(self, ProcessWindow):
        ProcessWindow.setWindowTitle("Process Window")
        ProcessWindow.setFixedSize(1164, 650)
      
        self.imgPlate1 = QtWidgets.QLabel(ProcessWindow)
        self.imgPlate1.setGeometry(QtCore.QRect(30, 50, 510, 127))
        self.imgPlate1.setFrameShape(QtWidgets.QFrame.Box)
        self.imgPlate1.setAlignment(QtCore.Qt.AlignCenter)

        self.imgPlate2 = QtWidgets.QLabel(ProcessWindow)
        self.imgPlate2.setGeometry(QtCore.QRect(30, 230, 510, 127))
        self.imgPlate2.setFrameShape(QtWidgets.QFrame.Box)
        self.imgPlate2.setAlignment(QtCore.Qt.AlignCenter)

        self.imgPlate3 = QtWidgets.QLabel(ProcessWindow)
        self.imgPlate3.setGeometry(QtCore.QRect(580, 50, 510, 127))
        self.imgPlate3.setFrameShape(QtWidgets.QFrame.Box)
        self.imgPlate3.setAlignment(QtCore.Qt.AlignCenter)

        self.imgPlate4 = QtWidgets.QLabel(ProcessWindow)
        self.imgPlate4.setGeometry(QtCore.QRect(580, 230, 510, 127))
        self.imgPlate4.setFrameShape(QtWidgets.QFrame.Box)
        self.imgPlate4.setAlignment(QtCore.Qt.AlignCenter)

        self.labelPlate1 = QtWidgets.QLabel(ProcessWindow)
        self.labelPlate1.setGeometry(QtCore.QRect(30, 15, 510, 31))
        self.labelPlate1.setText("Contours of number plate")

        self.labelPlate2 = QtWidgets.QLabel(ProcessWindow)
        self.labelPlate2.setGeometry(QtCore.QRect(30, 200, 510, 31))
        self.labelPlate2.setText("Segmented characters of number plate")

        self.labelPlate3 = QtWidgets.QLabel(ProcessWindow)
        self.labelPlate3.setGeometry(QtCore.QRect(580, 15, 510, 31))
        self.labelPlate3.setText("Thresholded number plate")

        self.labelPlate4 = QtWidgets.QLabel(ProcessWindow)
        self.labelPlate4.setGeometry(QtCore.QRect(580, 200, 510, 31))
        self.labelPlate4.setText("Denoised number plate. This image is used for recognition.")

        self.imgCar1 = QtWidgets.QLabel(ProcessWindow)
        self.imgCar1.setGeometry(QtCore.QRect(30, 400, 340, 220))
        self.imgCar1.setFrameShape(QtWidgets.QFrame.Box)
        self.imgCar1.setAlignment(QtCore.Qt.AlignCenter)

        self.imgCar2 = QtWidgets.QLabel(ProcessWindow)
        self.imgCar2.setGeometry(QtCore.QRect(400, 400, 340, 220))
        self.imgCar2.setFrameShape(QtWidgets.QFrame.Box)
        self.imgCar2.setAlignment(QtCore.Qt.AlignCenter)

        self.imgCar3 = QtWidgets.QLabel(ProcessWindow)
        self.imgCar3.setGeometry(QtCore.QRect(770, 400, 340, 220))
        self.imgCar3.setFrameShape(QtWidgets.QFrame.Box)
        self.imgCar3.setAlignment(QtCore.Qt.AlignCenter)
         
        self.labelCar1 = QtWidgets.QLabel(ProcessWindow)
        self.labelCar1.setGeometry(QtCore.QRect(30, 370, 341, 31))
        self.labelCar1.setText("Sobel edge detection")
        
        self.labelCar2 = QtWidgets.QLabel(ProcessWindow)
        self.labelCar2.setGeometry(QtCore.QRect(400, 370, 341, 31))
        self.labelCar2.setText("Binarized sobel image")

        self.labelCar3 = QtWidgets.QLabel(ProcessWindow)
        self.labelCar3.setGeometry(QtCore.QRect(770, 370, 341, 31))
        self.labelCar3.setText("Morphed binary image")

        set_image(self.imgCar1, convert_image(self.step_images[2]))
        set_image(self.imgCar2, convert_image(self.step_images[3]))
        set_image(self.imgCar3, convert_image(self.step_images[4]))
        set_image(self.imgPlate1, convert_image(self.step_images[9]))
        set_image(self.imgPlate2, convert_image(self.step_images[7]))
        set_image(self.imgPlate3, convert_image(self.step_images[6]))
        set_image(self.imgPlate4, convert_image(self.step_images[8]))

        QtCore.QMetaObject.connectSlotsByName(ProcessWindow)

class Ui_HelpWindow(QtWidgets.QMainWindow):
    def __init__(self): 
        super().__init__()

    def setupUi(self, HelpWindow):
        
        HelpWindow.setWindowTitle("Help window")
        HelpWindow.setFixedSize(921, 758)

        self.centralwidget = QtWidgets.QWidget(HelpWindow)

        self.textTessLocation = QtWidgets.QTextEdit(self.centralwidget)
        self.textTessLocation.setReadOnly(True)
        self.textTessLocation.setGeometry(QtCore.QRect(50, 50, 381, 121))
        self.textTessLocation.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">To start using this application, first you will need to locate <span style=\" font-weight:600;\">Tesseract.exe. </span>It can be found in the location where the software has been installed. </p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Most commonly it can be found here:</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">C:/Program Files/Tesseract-OCR/</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Once you\'ve found it, the application can now take in vehicle images!</p></body></html>")

        self.textSelection = QtWidgets.QTextEdit(self.centralwidget)
        self.textSelection.setReadOnly(True)
        self.textSelection.setGeometry(QtCore.QRect(50, 350, 381, 41))
        self.textSelection.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">To start scanning your image, press <span style=\" font-weight:600;\">Select... </span>that is located right below the image placeholders.</p></body></html>")

        self.textCheckmarks = QtWidgets.QTextEdit(self.centralwidget)
        self.textCheckmarks.setReadOnly(True)
        self.textCheckmarks.setGeometry(QtCore.QRect(50, 201, 381, 80))
        self.textCheckmarks.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Now that the application is ready for use, you can choose to save the images or show the steps the application has taken to get the number plate.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Pressing on the checkbox will enable/disable these features.</p></body></html>")

        self.textFormats = QtWidgets.QTextEdit(self.centralwidget)
        self.textFormats.setReadOnly(True)
        self.textFormats.setGeometry(QtCore.QRect(50, 480, 381, 41))
        self.textFormats.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The application can only process images of formats such as these: png; jpg; jpeg, so ensure your image is of those formats.</p></body></html>")

        self.textStartScan = QtWidgets.QTextEdit(self.centralwidget)
        self.textStartScan.setReadOnly(True)
        self.textStartScan.setGeometry(QtCore.QRect(50, 590, 381, 71))
        self.textStartScan.setHtml("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">After selecting your image, you can start the scan!</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The application will provide you with the results if the detection has been successful, and if not, it will let you know.</p></body></html>")

        self.imgTessLocation = QtWidgets.QLabel(self.centralwidget)
        self.imgTessLocation.setGeometry(QtCore.QRect(450, 50, 441, 121))
        self.imgTessLocation.setFrameShape(QtWidgets.QFrame.Box)
        self.imgTessLocation.setAlignment(QtCore.Qt.AlignCenter)
        set_image(self.imgTessLocation, convert_image(cv2.imread("assets/images/help_1.png")))

        self.imgCheckmarks = QtWidgets.QLabel(self.centralwidget)
        self.imgCheckmarks.setGeometry(QtCore.QRect(450, 180, 441, 121))
        self.imgCheckmarks.setFrameShape(QtWidgets.QFrame.Box)
        self.imgCheckmarks.setAlignment(QtCore.Qt.AlignCenter)
        set_image(self.imgCheckmarks, convert_image(cv2.imread("assets/images/help_2.png")))

        self.imgSelection = QtWidgets.QLabel(self.centralwidget)
        self.imgSelection.setGeometry(QtCore.QRect(450, 310, 441, 121))
        self.imgSelection.setFrameShape(QtWidgets.QFrame.Box)
        self.imgSelection.setAlignment(QtCore.Qt.AlignCenter)
        set_image(self.imgSelection, convert_image(cv2.imread("assets/images/help_3.png")))

        self.imgFormats = QtWidgets.QLabel(self.centralwidget)
        self.imgFormats.setGeometry(QtCore.QRect(450, 570, 441, 121))
        self.imgFormats.setFrameShape(QtWidgets.QFrame.Box)
        self.imgFormats.setAlignment(QtCore.Qt.AlignCenter)
        set_image(self.imgFormats, convert_image(cv2.imread("assets/images/help_4.png")))

        self.imgStartScan = QtWidgets.QLabel(self.centralwidget)
        self.imgStartScan.setGeometry(QtCore.QRect(450, 440, 441, 121))
        self.imgStartScan.setStyleSheet("border-color: rgba(255, 255, 255, 0);")
        self.imgStartScan.setFrameShape(QtWidgets.QFrame.Box)
        self.imgStartScan.setAlignment(QtCore.Qt.AlignCenter)
        set_image(self.imgStartScan, convert_image(cv2.imread("assets/images/help_5.png")))

        HelpWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(HelpWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 921, 21))

        HelpWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(HelpWindow)

        HelpWindow.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(HelpWindow)

def convert_image(img):
    gray_color_table = [QtGui.qRgb(i, i, i) for i in range(256)]
    
    if img is None:
        return QtGui.QImage()
    
    if img.dtype == np.float64:
        img=np.uint8(img)
    
    if img.dtype == np.uint8:

        #if image doesnt have colour channel
        if len(img.shape) == 2:
            #set image data from image to qimage
            end_img = QtGui.QImage(bytes(img.data), img.shape[1], img.shape[0], img.strides[0], QtGui.QImage.Format_Indexed8)
            #grayscale image
            end_img.setColorTable(gray_color_table)
            return end_img
        
        elif len(img.shape) == 3:
            if img.shape[2] == 3:
                #if the image does have a colour channel, return that image with the correct data
                #first the image returned is in the BGR (blue, green, red) format which means it needs to be swapped to RGB (red, green, blue).
                end_img = QtGui.QImage(bytes(img.data), img.shape[1], img.shape[0], img.shape[1] * 3, QtGui.QImage.Format_RGB888).rgbSwapped() 
                return end_img

def set_image(img_widget, img):
    #sets given image to given widget
    pixmap = QtGui.QPixmap(img)
    pixmap = pixmap.scaled(img_widget.width(), img_widget.height(), QtCore.Qt.KeepAspectRatio)
    img_widget.setPixmap(pixmap)

def set_theme(app):
    #sets dark theme
    app.setStyle('Fusion')
    
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15,15,15))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53,53,53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142,45,197).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    
    app.setPalette(palette)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    set_theme(app)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
