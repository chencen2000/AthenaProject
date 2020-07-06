import io
import os
import logging
import gphoto2 as gp
import time
import json
from PIL import Image, ImageDraw

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
    sn_config = camera.get_single_config("serialnumber")
    frame = 0
    image = None
    capture_image = False
    while frame <= 100 :
        logging.warn("get frame. No.{}".format(frame))
        try:
            camera_file = camera.capture_preview()        
            err, buf = gp.gp_file_get_data_and_size(camera_file)
            image = Image.open(io.BytesIO(buf))
            frame += 1
            if frame==20 or frame==50 or frame ==90:
                if capture_image:
                    file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
                    camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
                    camera_file.save("test_{}.jpg".format(frame))    
                    camera.exit()
                    camera = gp.Camera()
                    camera.init()
                else:
                    image.save("test_{}.jpg".format(frame))

        except:
            pass
        # camera_file.save("test.jpg")        
    camera.exit()
    if image is not None:
        image.save("test.jpg")

def test_select_camera_by_serialnumber(sn):
    ret = None
    cnt, cameras = gp.gp_camera_autodetect()
    for i in range(cnt):
        c = cameras[i]
        if len(c) == 2:
            addr = c[1]
            port_info_list = gp.PortInfoList()
            port_info_list.load()
            idx = port_info_list.lookup_path(addr)
            camera = gp.Camera()
            camera.set_port_info(port_info_list[idx])
            camera.init()
            config = camera.get_config()
            OK, sn = gp.gp_widget_get_child_by_name(config, 'serialnumber')
            if OK >= gp.GP_OK:
                sn_text = sn.get_value()
                if sn == sn_text:
                    pass
            camera.exit()            
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

def test_camera_config():
    callback_obj = gp.check_result(gp.use_python_logging())
    camera = gp.Camera()
    camera.init()
    config = camera.get_config()
    iso_config = config.get_child_by_name("iso")
    v = iso_config.get_value()
    iso_config.set_value('Auto ISO')
    ec = config.get_child_by_name("exposurecompensation")
    v = ec.get_value()
    ec.set_value('3')
    camera.set_config(config)
    camera.exit()


def read_matedata(file):
    with open(file, 'rb') as image_file:
        my_image = Image(image_file)


def test_draw_top_lines():    
    with open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CamerPositionCalibration'),'config.json')) as f:
        config = json.load(f)
    image = Image.open('test_20.jpg')
    w, h = image.size
    draw = ImageDraw.Draw(image) 
    ys = config['lines']['top']['y']
    for y,dy in ys:
        y = int(y*h/100)
        dy = int(dy*h/100)
        draw.line((0, y, w, y), fill=(255,0,0), width=1)
        draw.line((0, y+dy, w, y+dy), fill=(255,0,0), width=1)
    xs = config['lines']['top']['x']
    for x,dx in xs:
        x = int(x*w/100)
        dx = int(dx*w/100)
        draw.line((x ,0, x, h), fill=(255,0,0), width=1)
        draw.line((x+dx, 0, x+dx,h), fill=(255,0,0), width=1)
    image.save('test_draw.jpg')

def handle_longside_image():
    with open(os.path.join(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CamerPositionCalibration'),'config.json')) as f:
        config = json.load(f)
    image = Image.open('test_20.jpg')
    # ret = None
    w, h = image.size
    draw = ImageDraw.Draw(image) 
    ys = config['lines']['longside']['y']
    for y,dy in ys:
        y = int(y*h/100)
        dy = int(dy*h/100)
        draw.line([(0, y), (w, y)], fill=(255,0,0), width=1)
        draw.line([(0, y+dy), (w, y+dy)], fill=(255,0,0), width=1)
    xs = config['lines']['longside']['x']
    for x,dx in xs:
        x = int(x*w/100)
        dx = int(dx*w/100)
        draw.line([(x ,0), (x, h)], fill=(255,0,0), width=1)
        draw.line([(x+dx, 0), (x+dx,h)], fill=(255,0,0), width=1)
    # imageQ = ImageQt(image)
    # pixmap = QPixmap.fromImage(imageQ)
    # ret = pixmap.scaledToHeight(int(h*self.image_ratio))
    # return ret
    image.save('test_draw.jpg')

# test_select_camera_by_serialnumber("")
# test2()
# err, devs = gp.gp_camera_autodetect()
# all_devs = list(devs)
# test4()
# test_preview()
# test_camera_config()
# test_draw_lines()
handle_longside_image()