import redis
import logging
import gphoto2 as gp
import json

logging.basicConfig(format='%(asctime)s: %(levelname)s: %(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger("camera_detection")
logger.info("start")

def set_data():
    r = redis.Redis()
    r.set("Camera_TP.serialnumber", "123456")

def autodetect():
    ret=[]
    logger.info("autodetect: ++")
    camera_list = list(gp.Camera.autodetect())
    for index, (name, addr) in enumerate(camera_list):
        logger.info("{}: name={}, addr={}".format(index, name, addr))
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
        d = {'name':name, 'address':addr, 'manufacturer':maker, 'model':model, 'serialnumber':sn}
        logger.info("{}: {}".format(index, json.dumps(d)))
        ret.append(d)
        camera.exit()
    logger.info("autodetect: --")
    return ret

def save_camera(r, camera, prefix):
    for key in camera:
        r.set("{}.{}".format(prefix, key), camera[key])

r = redis.Redis()
sn_tp = r.get("Camera_TP.serialnumber").decode("utf-8") 
# sn_ss = r.get("Camera_SS.serialnumber").decode("utf-8") 
sn_ss = None
# sn_ls = r.get("Camera_LS.serialnumber").decode("utf-8") 
sn_ls = None
logger.info("Camera_TP: {}".format(sn_tp))
cameras = autodetect()
camera_tp = None
camera_ss = None
camera_ls = None
for c in cameras:
    if c['serialnumber'] == sn_tp:
        camera_tp = c
    if c['serialnumber'] == sn_ss:
        camera_ss = c
    if c['serialnumber'] == sn_ls:
        camera_ls = c
if camera_tp is not None:
    save_camera(r, camera_tp, "Camera_TP")
if camera_ss is not None:
    save_camera(r, camera_ss, "Camera_SS")
if camera_ls is not None:
    save_camera(r, camera_ls, "Camera_LS")
logger.info("done.")