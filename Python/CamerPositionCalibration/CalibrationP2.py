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
from Ui_CalibrationP2 import Ui_Frame
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
            if found:
                break
        logging.info('camera_find_by_serialnumber: -- ret={}'.format(ret))
        return ret

    def run(self):
        logging.info('run: ++')
        rc = redis.Redis()
        x = rc.get('camera.TP')
        if bool(x):
            x = x.decode('utf-8')
            camera = self.camera_find_by_serialnumber(x)
            if camera is not None:
                frame=0
                while not self.quitEvent.is_set():
                    try:
                        camera_file = camera.capture_preview() 
                        frame += 1
                        logging.info('frame: {}'.format(frame))
                        err, buf = gp.gp_file_get_data_and_size(camera_file)
                        if err >= gp.GP_OK:
                            image = Image.open(io.BytesIO(buf))
                            if self.cb is not None:
                                self.cb(image)
                    except:
                        pass
                camera.exit()
        rc.close()
        logging.info('run: --')
        pass


class CalibrationP2Widget(QtWidgets.QWidget, Ui_Frame):
    def __init__(self, parent=None):
        super(CalibrationP2Widget, self).__init__(parent)
        self.setupUi(self)
        self.get_position()
        self.pushButtonExit.clicked.connect(self.exit_cliecked)
        self.pushButtonGotoP2.clicked.connect(self.handle_gotop2)
        self.thread = CameraWorker(self.on_frame_arrival)
        self.thread.start()

    def handle_gotop2(self):
        try:
            r = requests.get('http://localhost:8010/lift/go', params={'p': 2})
            if r.status_code==200:
                pass            
        except:
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

    def on_frame_arrival(self, frame):
        image = self.draw_image(frame)
        imageQ = ImageQt(image)
        pixmap = QPixmap.fromImage(imageQ)
        self.labelImage.setPixmap(pixmap) 
        pass

    def draw_image(self, image):
        w, h = image.size
        draw = ImageDraw.Draw(image) 
        draw.line((0,int(h/2), w,int(h/2)), fill=128, width=4)
        draw.line((int(w/2),0, int(w/2),h), fill=128, width=4)
        return image

    def get_position(self):
        try:
            # r = requests.get('http://localhost:8010/lift/position?p=2')
            r = requests.get('http://localhost:8010/lift/position', params={'p':2})
            if r.status_code==200:
                if r.json()['status'] == 'OK':
                    v = r.json()['parse']['P2']
                    self.labelValue.setText('P2={}'.format(v))
        except:
            pass

    def start(self):
        pass

if __name__ == "__main__":
    import sys
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=logging.INFO)
    app = QtWidgets.QApplication(sys.argv)
    w = CalibrationP2Widget()
    w.show()
    sys.exit(app.exec_())