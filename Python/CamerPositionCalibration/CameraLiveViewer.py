from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QThread, pyqtSignal
from Ui_CameraLiveViewer import Ui_MainWindow
from Ui_settings import Ui_Dialog
from PIL import Image, ImageDraw
from PIL.ImageQt import ImageQt
import os
import io
import sys
import time
import json
import logging
import configparser
import threading
if sys.platform=='linux':
    import gphoto2 as gp
    import redis

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

class CameraWorker(QThread):
    def __init__(self, config):
        super(CameraWorker, self).__init__()
        self.camera_data = dict()
        # self.config = configparser.ConfigParser()
        # self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'camera.ini'))
        self.config = config
        self.camera_name = None
        self.camera_object = None
        self.camera_stop_event = threading.Event()
        self.cb = None
        self.take_image_event = threading.Event()
        self.image = None

    def get_camera_name(self):
        return self.camera_name

    def same_camera(self, camera_name):
        same_camera = False
        if self.camera_name is not None and camera_name==self.camera_name:
            same_camera = True
        return same_camera

    def start_camera_preview(self, camera_name='', cb=None):
        logging.info("start_camera_preview: ++")
        ret = False
        if camera_name:
            if not self.same_camera(camera_name):
                cam = self.camera_find_by_name(camera_name)
                if cam is None:
                    ret = False
                else:
                    self.camera_name = camera_name
                    self.camera_object = cam
                    self.cb = cb
                    self.start()
                    ret = True                    
            else:
                # same camera    
                ret = True                 
        logging.info("start_camera_preview: -- ret={}".format(ret))                
        return ret

    def stop_camera_preview(self):
        logging.info("stop_camera_preview: ++")
        if self.isRunning():
            self.camera_stop_event.set()
            while not self.isFinished():
                time.sleep(1)
        if self.camera_object is not None:
            self.camera_object.exit()
        logging.info("stop_camera_preview: --")

    def camera_find_by_name(self, camera_name):
        sn = self.config['camera'][camera_name]  
        camera = self.camera_find_by_serialnumber(sn)              
        return camera


    def camera_find_by_serialnumber(self, serialnumber):
        found = False
        ret = None
        logging.info("camera_find_by_serialnumber: ++ {}".format(serialnumber))
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
        logging.info("camera_find_by_serialnumber: -- found={}".format(found))
        return ret

    def take_photo(self):
        image = None
        self.take_image_event.set()
        while self.take_image_event.is_set():
            self.sleep(1)
        image = self.image            
        return image

    def run(self):
        logging.info("CameraWorker: run: ++")
        sn_config = self.camera_object.get_single_config("serialnumber")
        sn = sn_config.get_value()
        frame=0        
        while not self.camera_stop_event.is_set():
            if self.take_image_event.is_set():
                done = False
                while not done:
                    try:
                        file_path = self.camera_object.capture(gp.GP_CAPTURE_IMAGE)
                        camera_file = self.camera_object.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
                        err, buf = gp.gp_file_get_data_and_size(camera_file)
                        self.image = Image.open(io.BytesIO(buf))
                        self.take_image_event.clear()
                        # re-init camera
                        self.camera_object.exit()
                        self.camera_object = self.camera_find_by_serialnumber(sn)
                        done = True
                    except:
                        pass
            try:
                camera_file = self.camera_object.capture_preview() 
                err, buf = gp.gp_file_get_data_and_size(camera_file)
                if err >= gp.GP_OK:
                    frame += 1
                    logging.info("get frame. No.{}".format(frame))
                    image = Image.open(io.BytesIO(buf))
                    # self.on_camera_frame_arrival.emit(image)
                    if self.cb is not None:
                        self.cb(image)
                    # self.handle_image(image) 
                    # self.labelImage.setPixmap(self.handle_image(image))           
            except:
                pass
        self.camera_stop_event.clear()
        logging.info("CameraWorker: run: --")


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    Class documentation goes here.
    """
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # self.setFixedSize(1024,768)
        self.topButton.clicked.connect(lambda x: self.radioButton_clicked(self.topButton))
        self.ssdieButton.clicked.connect(lambda x: self.radioButton_clicked(self.ssdieButton))
        self.lsideButton.clicked.connect(lambda x: self.radioButton_clicked(self.lsideButton))
        self.settingButton.clicked.connect(self.show_settingsDlg)
        self.zoomInButton.clicked.connect(self.zoomInButton_clicked)
        self.zoomOutButton.clicked.connect(self.zoomOutButton_clicked)
        self.calibrateButton.clicked.connect(self.calibrate_handler)
        self.testButton.clicked.connect(self.test_button)
        # show default image
        self.labelImage.setText('')
        self.settingData={'line_width':15}
        # self.labelImage.setPixmap(QtGui.QPixmap(r"D:\\projects\\images\\0623\\3.jpg").scaledToHeight(600))
        # self.config = configparser.ConfigParser()
        # self.config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'camera.ini'))
        self.config = None
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')) as f:
            self.config = json.load(f)
        # self.rc = redis.Redis()
        # write camera calibration data in redis
        # self.rc.set("Camera_TP.serialnumber", self.config['location']['camera_tp'])
        # self.rc.set("Camera_LS.serialnumber", self.config['location']['camera_ls'])
        # self.rc.set("Camera_SS.serialnumber", self.config['location']['camera_ss'])
        self.camera_data = None
        self.camera_worker = None
        # quit = QAction("Quit", self)
        self.image_ratio = 0.0
        self.current_image= None
        self.current_image_lock=threading.Lock()

    def closeEvent(self, event):        
        logging.info("close event: ++")
        # if self.camera_data is not None:
        #     self.camera_stop_liveview()
        if self.camera_worker is not None:
            self.camera_worker.stop_camera_preview()
    
    def test_button(self):
        if self.current_image is not None:
            self.current_image_lock.acquire()
            self.current_image.save('test_liveview.jpg')
            self.current_image_lock.release()
        pass

    def calibrate_handler(self):
        logging.info("calibrate_handler: ++")
        if self.camera_worker is not None:
            img = self.camera_worker.take_photo()
            if img is not None:
                img.save("test.jpg")
                # with open('save.jpg', 'rb') as f:
                #     img.save(f)
        pass

    def zoomInButton_clicked(self):
        if self.image_ratio > 0:
            delta = self.image_ratio * 0.1
            self.image_ratio += delta
            if sys.platform == 'win32':
                if self.topButton.isChecked():
                    self.radioButton_clicked(self.topButton)
                if self.ssdieButton.isChecked():
                    self.radioButton_clicked(self.ssdieButton)
                if self.lsideButton.isChecked():
                    self.radioButton_clicked(self.lsideButton)
        pass

    def zoomOutButton_clicked(self):
        if self.image_ratio > 0:
            delta = self.image_ratio * 0.1
            self.image_ratio -= delta
            if sys.platform == 'win32':
                if self.topButton.isChecked():
                    self.radioButton_clicked(self.topButton)
                if self.ssdieButton.isChecked():
                    self.radioButton_clicked(self.ssdieButton)
                if self.lsideButton.isChecked():
                    self.radioButton_clicked(self.lsideButton)
        pass

    def topButton_clicked(self):
        logging.info("topButton_clicked: ++")
        if self.topButton.isChecked():
            logging.info("topButton_clicked: topButton is checked.")
            img = Image.open(r"D:\\projects\\images\\0623\\1.jpg")
            self.labelImage.setPixmap(self.handle_image(img))
        logging.info("topButton_clicked: --")

    def radioButton_clicked(self, button):
        camera_name = None
        if button is self.topButton:
            # self.topButton_clicked()
            camera_name = 'Camera_TP'
            try:
                img = Image.open(r"D:\\projects\\images\\0623\\1.jpg")
            except:
                pass
        elif button is self.ssdieButton:
            camera_name = 'Camera_SS'
            # if button.isChecked:
            try:
                img = Image.open(r"D:\\projects\\images\\0623\\3.jpg")
            except:
                pass
            #     self.labelImage.setPixmap(self.handle_image(img))
        elif button is self.lsideButton:
            camera_name = 'Camera_LS'
            # if button.isChecked:
            try:
                img = Image.open(r"D:\\projects\\images\\0623\\6.jpg")
            except:
                pass
            #     self.labelImage.setPixmap(self.handle_image(img))
        # if not self.handle_camera_start(camera_name):
        if not self.handle_camera_start_v2(camera_name):
            if img is not None:
                self.labelImage.setPixmap(self.handle_image(img))

    def handle_image(self, img):
        ret = None
        w, h = img.size
        if self.image_ratio == 0:            
            sz = self.labelImage.size()
            self.image_ratio = min(sz.width()/w, sz.height()/h)
        camera_name = ''
        try:
            camera_name = self.camera_worker.get_camera_name()
        except:
            pass
        if camera_name == 'Camera_TP':
            ret = self.handle_top_image(img)
        elif camera_name == 'Camera_SS':
            ret = self.handle_shortside_image(img)
        elif camera_name == 'Camera_LS':
            ret = self.handle_longside_image(img)
        else:
            draw = ImageDraw.Draw(img) 
            draw.line((0,int(h/2), w,int(h/2)), fill=128, width=4)
            draw.line((int(w/2),0, int(w/2),h), fill=128, width=4)
            ret = img
            # imageQ = ImageQt(img)
            # pixmap = QPixmap.fromImage(imageQ)
            # ret = pixmap.scaledToHeight(int(h*self.image_ratio))
        # return pixmap
        return ret

    def show_settingsDlg(self):
        logging.info("show_settingsDlg: ++")
        settingDlg = SettingWindow()
        settingDlg.setModal(True)
        # settingDlg.setWindowModality(Qt.ApplicationModal)
        # settingDlg.set_data(self.settingData)
        # settingDlg.show()
        res = settingDlg.exec_()
        logging.info("show_settingsDlg: --")

    def handle_camera_start_v2(self, camera_name):
        ret = False
        if self.camera_worker is not None:
            if self.camera_worker.same_camera(camera_name):
                ret = True
            else:
                self.camera_worker.stop_camera_preview()
                self.camera_worker = None
        if self.camera_worker is None:
            self.camera_worker = CameraWorker(self.config)
            # self.camera_worker.on_camera_frame_arrival.connect(self.on_frame_arrival)
            ret = self.camera_worker.start_camera_preview(camera_name, self.on_frame_arrival)        
        return ret 

    def on_frame_arrival(self, frame):
        img = self.handle_image(frame)
        self.current_image_lock.acquire()
        self.current_image = img
        self.current_image_lock.release()
        w, h = img.size
        imageQ = ImageQt(img)
        pixmap = QPixmap.fromImage(imageQ)
        # pixmap.scaledToHeight(int(h*self.image_ratio))
        ret = pixmap.scaledToHeight(int(h*self.image_ratio))
        self.labelImage.setPixmap(ret) 
        # self.labelImage.setPixmap(self.handle_image(frame)) 

    def handle_top_image(self, image):
        ret = None
        w, h = image.size
        draw = ImageDraw.Draw(image) 
        ys = self.config['lines']['top']['y']
        for y,dy in ys:
            y = int(y*h/100)
            dy = int(dy*h/100)
            draw.line((0, y, w, y), fill=(255,0,0), width=1)
            draw.line((0, y+dy, w, y+dy), fill=(255,0,0), width=1)
        xs = self.config['lines']['top']['x']
        for x,dx in xs:
            x = int(x*w/100)
            dx = int(dx*w/100)
            draw.line((x ,0, x, h), fill=(255,0,0), width=1)
            draw.line((x+dx, 0, x+dx,h), fill=(255,0,0), width=1)
        ret = image
        # imageQ = ImageQt(image)
        # pixmap = QPixmap.fromImage(imageQ)
        # ret = pixmap.scaledToHeight(int(h*self.image_ratio))
        return ret
    
    def handle_shortside_image(self, image):
        ret = None
        w, h = image.size
        draw = ImageDraw.Draw(image) 
        ys = self.config['lines']['shortside']['y']
        for y,dy in ys:
            y = int(y*h/100)
            dy = int(dy*h/100)
            draw.line((0, y, w, y), fill=(255,0,0), width=1)
            draw.line((0, y+dy, w, y+dy), fill=(255,0,0), width=1)
        xs = self.config['lines']['shortside']['x']
        for x,dx in xs:
            x = int(x*w/100)
            dx = int(dx*w/100)
            draw.line((x ,0, x, h), fill=(255,0,0), width=1)
            draw.line((x+dx, 0, x+dx,h), fill=(255,0,0), width=1)
        ret = image
        # imageQ = ImageQt(image)
        # pixmap = QPixmap.fromImage(imageQ)
        # ret = pixmap.scaledToHeight(int(h*self.image_ratio))
        return ret

    def handle_longside_image(self, image):
        ret = None
        w, h = image.size
        draw = ImageDraw.Draw(image) 
        ys = self.config['lines']['longside']['y']
        for y,dy in ys:
            y = int(y*h/100)
            dy = int(dy*h/100)
            # print("y={}, dy={}".format(y,dy))
            draw.line((0, y, w, y), fill=(255,0,0), width=1)
            draw.line((0, y+dy, w, y+dy), fill=(255,0,0), width=1)
            # draw.line([(0, y), (w, y),(0, y+dy), (w, y+dy)], fill=(255,0,0), width=1)
        xs = self.config['lines']['longside']['x']
        for x,dx in xs:
            x = int(x*w/100)
            dx = int(dx*w/100)
            # print("x={}, dx={}".format(x,dx))
            draw.line((x ,0, x, h), fill=(255,0,0), width=1)
            draw.line((x+dx, 0, x+dx,h), fill=(255,0,0), width=1)
            # draw.line([(x ,0), (x, h),(x+dx, 0), (x+dx,h)], fill=(255,0,0), width=1)
        ret = image
        # imageQ = ImageQt(image)
        # pixmap = QPixmap.fromImage(imageQ)
        # ret = pixmap.scaledToHeight(int(h*self.image_ratio))
        return ret

    # def handle_camera_start(self, camera_name):
    #     ret = False
    #     if sys.platform == 'linux':
    #         same_camera = False
    #         # check if same camera
    #         if self.camera_data is not None:
    #             if 'name' in self.camera_data.keys():
    #                 if self.camera_data['name'] == camera_name:
    #                     same_camera = True
    #         if not same_camera:
    #             if self.camera_data is not None:
    #                 # stop current live view
    #                 self.camera_stop_liveview()
    #                 pass
    #             # start live view
    #             ret = self.camera_start_liveview(camera_name)
    #         else:
    #             ret = True
    #     return ret

    # def camera_stop_liveview(self):
    #     logging.info("camera_stop_liveview: ++")
    #     if self.camera_data is not None:
    #         e = self.camera_data['quitevent']
    #         e.set()
    #         if 'thread' in self.camera_data.keys():
    #             t = self.camera_data['thread']
    #             t.join()
    #         c = self.camera_data['object']
    #         c.exit()
    #     self.camera_data = None
    #     logging.info("camera_stop_liveview: --")

    # def camera_start_liveview(self, camera_name):
    #     ret = False
    #     logging.info("camera_start_liveview: ++")
    #     camera = self.camera_find_by_name(camera_name)
    #     if camera is None:
    #         QMessageBox.information(self, 'Error', 'Cannot found camera {}'.format(camera_name))
    #     else:
    #         self.camera_data = {}
    #         self.camera_data['name'] = camera_name
    #         self.camera_data['object'] = camera
    #         self.camera_data['quitevent'] = threading.Event()
    #         t = threading.Thread(target=self.camera_liveview_thread, daemon=True) 
    #         self.camera_data['thread'] = t
    #         t.start()
    #         ret = True
    #     logging.info("camera_start_liveview: -- ret={}".format(ret))
    #     return ret

    # def camera_liveview_thread(self):
    #     logging.info("camera_liveview_thread: ++")
    #     evt = self.camera_data['quitevent']
    #     camera = self.camera_data['object']
    #     frame=0        
    #     while not evt.is_set():
    #         camera_file = camera.capture_preview() 
    #         err, buf = gp.gp_file_get_data_and_size(camera_file)
    #         if err >= gp.GP_OK:
    #             frame += 1
    #             logging.info("get frame. No.{}".format(frame))
    #             image = Image.open(io.BytesIO(buf))
    #             # self.handle_image(image) 
    #             self.labelImage.setPixmap(self.handle_image(image))           
    #     logging.info("camera_liveview_thread: --")
        

    # def camera_find_by_name(self, camera_name):
    #     sn = self.config['location'][camera_name]  
    #     camera = self.camera_find_by_serialnumber(sn)              
    #     return camera


    # def camera_find_by_serialnumber(self, serialnumber):
    #     found = False
    #     ret = None
    #     logging.info("camera_find_by_serialnumber: ++ {}".format(serialnumber))
    #     cnt, cameras = gp.gp_camera_autodetect()
    #     for i in range(cnt):
    #         if len(cameras[i]) == 2 :
    #             addr = cameras[i][1]
    #             port_info_list = gp.PortInfoList()
    #             port_info_list.load()
    #             idx = port_info_list.lookup_path(addr)
    #             c = gp.Camera()
    #             c.set_port_info(port_info_list[idx])
    #             c.init()
    #             config = c.get_config()
    #             OK, sn = gp.gp_widget_get_child_by_name(config, 'serialnumber')
    #             if OK >= gp.GP_OK:
    #                 sn_text = sn.get_value()
    #                 if serialnumber == sn_text[-len(serialnumber):] :
    #                     found =True
    #                     ret = c
    #             if not found:
    #                 c.exit()
    #         if found:
    #             break
    #     logging.info("camera_find_by_serialnumber: -- found={}".format(found))
    #     return ret
  

if __name__ == "__main__":
    logging.info("main: ++ {}".format(__file__))
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    # w.show()
    w.showMaximized()
    sys.exit(app.exec_())
