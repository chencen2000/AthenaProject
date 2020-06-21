import gphoto2 as gp
import logging
import threading
import time
import io
from PIL import Image

class SonyCamera:
    logger = logging.getLogger("SonyCamera")
    def __init__(self):
        pass

    def init(self, args):
        ret = gp.GP_ERROR
        addr = args['addr']
        self.sn = args['serialnumber']
        if addr is not None:
            self.camera = gp.Camera()
            port_info_list = gp.PortInfoList()
            port_info_list.load()            
            idx = port_info_list.lookup_path(addr)
            self.camera.set_port_info(port_info_list[idx])
            self.camera.init()
            ret = gp.GP_OK
        return ret

    def exit(self):
        if self.camera is not None:
            self.camera.exit()

    def start_preview(self):
        SonyCamera.logger.info("start_preview: ++")
        self.preview_event = threading.Event()
        self.preview_lock = threading.Lock()
        self.preview_image = None
        self.preview_event.clear()
        self.preview_thread = threading.Thread(target=self.preview_thread_proc, daemon=True) 
        self.preview_thread.start()
        SonyCamera.logger.info("start_preview: --")
        pass

    def stop_preview(self):
        SonyCamera.logger.info("stop_preview: ++")
        if self.preview_event is not None:
            self.preview_event.set()
        if self.preview_thread is not None:
            self.preview_thread.join()
        SonyCamera.logger.info("stop_preview: --")

    def get_preview(self):
        SonyCamera.logger.info("get_preview: ++")
        ret = None
        if self.preview_lock is not None:
            self.preview_lock.acquire()
            ret = Image.open(self.preview_image)
            self.preview_lock.release()
        SonyCamera.logger.info("get_preview: --")
        return ret

    def preview_thread_proc(self):
        SonyCamera.logger.info("preview_thread_proc: ++")
        if self.preview_event is not None:
            frame=0
            while not self.preview_event.is_set():
                camera_file = self.camera.capture_preview() 
                err, buf = gp.gp_file_get_data_and_size(camera_file)
                # image = Image.open(io.BytesIO(buf))
                frame +=1
                SonyCamera.logger.info("get frame. No.{}".format(frame))
                self.preview_lock.acquire()
                self.preview_image = io.BytesIO(buf)
                self.preview_lock.release()
        SonyCamera.logger.info("preview_thread_proc: --")
     

    @staticmethod
    def autodetect():
        ret=[]
        SonyCamera.logger.info("autodetect: ++")
        camera_list = list(gp.Camera.autodetect())
        for index, (name, addr) in enumerate(camera_list):
            SonyCamera.logger.info("{}: name={}, addr={}".format(index, name, addr))
            port_info_list = gp.PortInfoList()
            port_info_list.load()            
            idx = port_info_list.lookup_path(addr)
            camera = gp.Camera()
            camera.set_port_info(port_info_list[idx])
            camera.init()
            camera_config = camera.get_config()
            model=''
            OK, conf = gp.gp_widget_get_child_by_name(camera_config, 'cameramodel')
            if OK >= gp.GP_OK:
                model = conf.get_value()
            maker = ''
            OK, conf = gp.gp_widget_get_child_by_name(camera_config, 'manufacturer')
            if OK >= gp.GP_OK:
                maker = conf.get_value()
            sn = ''
            OK, conf = gp.gp_widget_get_child_by_name(camera_config, 'serialnumber')
            if OK >= gp.GP_OK:
                sn = conf.get_value()
            d = {'name':name, 'addr':addr, 'manufacturer':maker, 'model':model, 'serialnumber':sn}
            ret.append(d)
            camera.exit()
        SonyCamera.logger.info("autodetect: --")
        return ret

# test code
if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=logging.INFO)
    cs = SonyCamera.autodetect()
    camera = SonyCamera()
    ok = camera.init(cs[0])
    camera.start_preview()
    input("press enter to terminate...")
    camera.stop_preview()
    camera.exit()
