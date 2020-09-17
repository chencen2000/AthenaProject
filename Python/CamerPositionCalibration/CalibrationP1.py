import io
import redis
import logging
import requests
import threading
import gphoto2 as gp
from PyQt5.QtGui import QPixmap
from PIL.ImageQt import ImageQt
from PIL import Image, ImageDraw
from PyQt5 import QtWidgets, QtGui
from Ui_CalibrationP1 import Ui_Frame
from PyQt5.QtCore import QThread, pyqtSignal

class CameraWorker(QThread):
    def __init__(self, cb=None):
        super(CameraWorker, self).__init__()
        self.quitEvent = threading.Event()
        self.cb = cb

    def camera_find_by_serialnumber(self, serialnumber):
        logging.info('camera_find_by_serialnumber: ++ sn = {}'.format(serialnumber))
        found = False
        ret = None
        cnt, cameras = gp.gp_camera_autodetect()
        for i in range(cnt):
            if len(cameras[i]) == 2 :
                try:
                    addr = cameras[i][1]
                    port_info_list = gp.PortInfoList()
                    port_info_list.load()
                    idx = port_info_list.lookup_path(addr)
                    c = gp.Camera()
                    c.set_port_info(port_info_list[idx])
                    c.init()
                    config = c.get_config()
                    OK, sn = gp.gp_widget_get_child_by_name(config, 'serialnumber')
                    if OK >= gp.GP_OK:
                        sn_text = sn.get_value()
                        if serialnumber == sn_text[-len(serialnumber):] :
                            found =True
                            ret = c
                    if not found:
                        c.exit()
                except:
                    pass
            if found:
                break
        logging.info('camera_find_by_serialnumber: -- ret={}'.format(ret))
        return ret

    def load_camera(self):
        rc = redis.Redis()
        camera_LS = None
        camera_SS = None
        x = rc.get('camera.LS')
        if bool(x):
            x = x.decode('utf-8')
            camera_LS = self.camera_find_by_serialnumber(x)
        x = rc.get('camera.SS')
        if bool(x):
            x = x.decode('utf-8')
            camera_SS = self.camera_find_by_serialnumber(x)
        rc.close()
        return camera_LS, camera_SS

    def run(self):
        logging.info('run: ++')
        camera_LS, camera_SS = self.load_camera()
        if bool(camera_LS) and bool(camera_SS):
            frame_LS = 0
            frame_SS = 0
            image_LS = None
            image_SS = None
            while not self.quitEvent.is_set():
                try:
                    camera_file = camera_LS.capture_preview() 
                    frame_LS += 1
                    logging.info('[LS] frame: {}'.format(frame_LS))
                    err, buf = gp.gp_file_get_data_and_size(camera_file)
                    if err >= gp.GP_OK:
                        image_LS = Image.open(io.BytesIO(buf))
                except:
                    pass
                try:
                    camera_file = camera_SS.capture_preview() 
                    frame_SS += 1
                    logging.info('[SS] frame: {}'.format(frame_SS))
                    err, buf = gp.gp_file_get_data_and_size(camera_file)
                    if err >= gp.GP_OK:
                        image_SS = Image.open(io.BytesIO(buf))
                except:
                    pass
                if self.cb is not None:
                    self.cb(image_LS, image_SS)
            camera_LS.exit()
            camera_SS.exit()
        logging.info('run: --')
        pass


class CalibrationP1Widget(QtWidgets.QWidget, Ui_Frame):
    def __init__(self, parent=None):
        super(CalibrationP1Widget, self).__init__(parent)
        self.setupUi(self)
        self.image_ratio = 0.5
        self.get_position()
        self.pushButtonExit.clicked.connect(self.exit_cliecked)
        self.pushButtonGotoP1.clicked.connect(self.handle_gotop1)
        self.thread = CameraWorker(self.on_frame_arrival)
        self.thread.start()

    def handle_gotop1(self):
        try:
            r = requests.get('http://localhost:8010/lift/go', params={'p': 1})
            if r.status_code==200:
                pass
        except:
            pass

        pass

    def exit_cliecked(self):
        self.close()
        pass

    def closeEvent(self, event):
        logging.info('closeEvent: ++')
        self.thread.quitEvent.set()
        self.thread.wait()
        logging.info('closeEvent: --')
        pass

    def on_frame_arrival(self, frame_LS, frame_SS):
        image_LS, image_SS = self.draw_image(frame_LS, frame_SS)
        w, h = image_LS.size
        imageQ_LS = ImageQt(image_LS)
        pixmap_LS = QPixmap.fromImage(imageQ_LS)
        pixmap_LS = pixmap_LS.scaledToHeight(int(h*self.image_ratio))
        self.label_image_1.setPixmap(pixmap_LS) 
        w, h = image_SS.size
        imageQ_SS = ImageQt(image_SS)
        pixmap_SS = QPixmap.fromImage(imageQ_SS)
        pixmap_SS = pixmap_SS.scaledToHeight(int(h*self.image_ratio))
        self.label_image_2.setPixmap(pixmap_SS) 
        pass

    def draw_image(self, image_LS, image_SS):
        w, h = image_LS.size
        draw_LS = ImageDraw.Draw(image_LS) 
        draw_LS.line((0,int(h/2), w,int(h/2)), fill=128, width=4)
        draw_LS.line((int(w/2),0, int(w/2),h), fill=128, width=4)
        w, h = image_SS.size
        draw_SS = ImageDraw.Draw(image_SS) 
        draw_SS.line((0,int(h/2), w,int(h/2)), fill=128, width=4)
        draw_SS.line((int(w/2),0, int(w/2),h), fill=128, width=4)
        return image_LS, image_SS

    def get_position(self):
        try:
            # r = requests.get('http://localhost:8010/lift/position?p=2')
            r = requests.get('http://localhost:8010/lift/position', params={'p': 1})
            if r.status_code==200:
                if r.json()['status'] == 'OK':
                    v = r.json()['parse']['P1']
                    self.labelValue.setText('P1={}'.format(v))
        except:
            pass

    def start(self):
        pass

if __name__ == "__main__":
    import sys
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=logging.INFO)
    app = QtWidgets.QApplication(sys.argv)
    w = CalibrationP1Widget()
    w.show()
    sys.exit(app.exec_())