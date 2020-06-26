from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QDialog
from PyQt5.QtGui import QPixmap
from Ui_CameraLiveViewer import Ui_MainWindow
from Ui_settings import Ui_Dialog
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
import logging

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=logging.INFO)

class SettingWindow(QDialog, Ui_Dialog):
    def __init__(self, parent=None):
        super(SettingWindow, self).__init__(parent)
        self.setupUi(self)
        # self.open.connect(self.on_dialog_open)

    def on_dialog_open(self):
        logging.info("setting dialog opening.")

    def set_data(self, data):
        self.data = data


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.topButton.clicked.connect(lambda x: self.radioButton_clicked(self.topButton))
        self.ssdieButton.clicked.connect(lambda x: self.radioButton_clicked(self.ssdieButton))
        self.lsideButton.clicked.connect(lambda x: self.radioButton_clicked(self.lsideButton))
        self.settingButton.clicked.connect(self.show_settingsDlg)
        # show default image
        self.labelImage.setText('')
        self.settingData={'line_width':15}
        # self.labelImage.setPixmap(QtGui.QPixmap(r"D:\\projects\\images\\0623\\3.jpg").scaledToHeight(600))
    
    def topButton_clicked(self):
        logging.info("topButton_clicked: ++")
        if self.topButton.isChecked:
            logging.info("topButton_clicked: topButton is checked.")
            img = Image.open(r"D:\\projects\\images\\0623\\1.jpg")
            self.labelImage.setPixmap(self.handle_image(img))
        logging.info("topButton_clicked: --")

    def radioButton_clicked(self, button):
        if button is self.topButton:
            self.topButton_clicked()
        elif button is self.ssdieButton:
            if button.isChecked:
                img = Image.open(r"D:\\projects\\images\\0623\\3.jpg")
                self.labelImage.setPixmap(self.handle_image(img))
        elif button is self.lsideButton:
            if button.isChecked:
                img = Image.open(r"D:\\projects\\images\\0623\\6.jpg")
                self.labelImage.setPixmap(self.handle_image(img))

    def handle_image(self, img):
        w, h = img.size
        draw = ImageDraw.Draw(img) 
        draw.line((0,int(h/2), w,int(h/2)), fill=128, width=15)
        draw.line((int(w/2),0, int(w/2),h), fill=128, width=15)
        imageQ = ImageQt(img)
        pixmap = QPixmap.fromImage(imageQ)
        return pixmap.scaledToHeight(600)

    def show_settingsDlg(self):
        logging.info("show_settingsDlg: ++")
        settingDlg = SettingWindow()
        settingDlg.setModal(True)
        # settingDlg.setWindowModality(Qt.ApplicationModal)
        # settingDlg.set_data(self.settingData)
        # settingDlg.show()
        res = settingDlg.exec_()
        logging.info("show_settingsDlg: --")
  

if __name__ == "__main__":
    logging.info("main: ++")
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
