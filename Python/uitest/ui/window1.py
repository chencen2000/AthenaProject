# -*- coding: utf-8 -*-

"""
Module implementing MainWindow.
"""

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.QtGui import QPixmap
from Ui_window1 import Ui_MainWindow
from PIL import Image
from PIL.ImageQt import ImageQt
import gphoto2 as gp
import logging
import threading
import time
import redis
import io

class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=logging.INFO)
        self.logger = logging.getLogger("MainWindow")        
        """
        Constructor
        
        @param parent reference to the parent widget
        @type QWidget
        """
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.preview_thread = None
    
    @pyqtSlot()
    def on_pushButton_clicked(self):
        """
        Slot documentation goes here.
        """
        # pixmap = QPixmap('test.jpg')
        # self.label.setPixmap(pixmap)
        if self.preview_thread is not None:
            # stop preview
            self.stop_preview()
            pass
        else:
            # start preview
            self.start_preview()
            pass
    
    @pyqtSlot()
    def on_pushButton_2_clicked(self):
        """
        Slot documentation goes here.
        """
        QMessageBox.aboutQt(self)

    def start_preview(self):
        self.logger.info("start_preview: ++")
        self.preview_quit_event = threading.Event()
        self.preview_thread = threading.Thread(target=self.preview_thread_proc, daemon=True) 
        self.preview_thread.start()
        self.logger.info("start_preview: --")
        

    def stop_preview(self):
        self.logger.info("stop_preview: ++")
        if self.preview_quit_event is not None:
            self.preview_quit_event.set()
        if self.preview_thread is not None:
            self.preview_thread.join()
        self.preview_thread = None
        self.preview_quit_event = None
        self.logger.info("stop_preview: --")

    def preview_thread_proc(self):
        self.logger.info("preview_thread_proc: ++")
        if self.preview_quit_event is not None:  
            r = redis.Redis()          
            camera = self.init_camera(r)
            frame=0
            while not self.preview_quit_event.is_set():
                # time.sleep(1)
                camera_file = camera.capture_preview() 
                err, buf = gp.gp_file_get_data_and_size(camera_file)
                if err >= gp.GP_OK:
                    frame += 1
                    self.logger.info("get frame. No.{}".format(frame))
                    image = Image.open(io.BytesIO(buf))
                    imageQ = ImageQt(image)
                    pixmap = QPixmap.fromImage(imageQ)
                    self.label.setPixmap(pixmap)
                # read setting
                iso, expc = r.mget(["Camera_TP.iso", "Camera_TP.exposurecompensation"])
                if iso is not None or expc is not None:
                    config = camera.get_config()
                    save_config = False
                    if iso is not None:
                        c = config.get_child_by_name("iso")
                        v = c.get_value()
                        if v != iso.decode('utf-8'):
                            c.set_value(iso.decode('utf-8'))
                            save_config = True
                    if expc is not None:
                        c = config.get_child_by_name("exposurecompensation")
                        v = c.get_value()
                        if v != expc.decode('utf-8'):
                            c.set_value(expc.decode('utf-8'))
                            save_config = True
                    if save_config:
                        camera.set_config(config)
            camera.exit()
        self.logger.info("preview_thread_proc: --")
    
    def init_camera(self, r):        
        self.logger.info("init_camera: ++")
        data = r.get("Camera_TP.address")
        if data is not None:
            addr = data.decode("utf-8")
            port_info_list = gp.PortInfoList()
            port_info_list.load()
            idx = port_info_list.lookup_path(addr)
            camera_tp = gp.Camera()
            camera_tp.set_port_info(port_info_list[idx])
            camera_tp.init()
        self.logger.info("init_camera: --")
        return camera_tp

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
