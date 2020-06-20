import io
import logging
import gphoto2 as gp
import time
from PIL import Image

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
logging.warn("start")

def test():
    error, camera = gp.gp_camera_new()
    error = gp.gp_camera_init(camera)
    error, text = gp.gp_camera_get_summary(camera)
    print('Summary')
    print('=======')
    print(text.text)
    error = gp.gp_camera_exit(camera)

def test_capture():
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
    camera.init()
    file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
    camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
    camera_file.save("test.jpg")
    camera.exit()

def test_preview():
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
    camera.init()
    frame = 50
    image = None
    while frame > 0 :
        logging.warn("get frame. No.{}".format(frame))
        camera_file = camera.capture_preview()        
        err, buf = gp.gp_file_get_data_and_size(camera_file)
        image = Image.open(io.BytesIO(buf))
        frame -= 1
        # camera_file.save("test.jpg")        
    camera.exit()
    if image is not None:
        pass

def test_select_camera():
    camera_list = list(gp.Camera.autodetect())
    if not camera_list:
        return 1
    for index, (name, addr) in enumerate(camera_list):
        print('{:d}:  {:s}  {:s}'.format(index, addr, name))
    name, addr = camera_list[0]
    port_info_list = gp.PortInfoList()
    port_info_list.load()
    idx = port_info_list.lookup_path(addr)
    camera = gp.Camera()
    camera.set_port_info(port_info_list[idx])
    camera.init()
    error, text = gp.gp_camera_get_summary(camera)
    print(text.text)


# test2()
# err, devs = gp.gp_camera_autodetect()
# all_devs = list(devs)
# test4()
test_preview()