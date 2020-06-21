# AthenaProject
for Athena project.

enable gphoto2 live view optional
- install ffmpeg
sudo apt install ffmpeg
- install v4l-utils
sudo apt install v4l-utils
- install v4l2loopback-dkms
sudo apt install v4l2loopback-dkms
- create a /dev/video<n> device
sudo modprobe v4l2loopback exclusive_caps=1 card_level="GPhoto2_WebCam"
- stream gphoto2 video-capture to /dev/video<n>
sudo gphoto2 --stdout --capture-movie | sudo ffmpeg -i - -vcodec rawvideo -pix_fmt yuv420p -threads 0 -f v4l2 /dev/video0
- receive
sudo ffplay /dev/video0
  
install gphoto2 python
- install build essential
sudo apt install build-essential
- install libgphoto2
sudo apt install libgphoto2-dev
- install pkg-config
sudo apt install pkg-config
- install gphoto2 python
sudo pip3 install gphoto2

