CaptureImage.exe -dir=<output folder full path> -imei=<imei>

-dir, optional, default use current folder as output folder
-imei, optional, default use "output" as imei
the final output folder will be "dir"\"imei"\,
under this folder there are 8 images saved in jpg format,
1-1.jpg, top, 1-1 is the image took with low light source
1-2.jpg, top, 1-2 is the image took with high light source, +0 steps
1-3.jpg, top, 1-3 is the image took with high light source, -3 steps
2.jpg
3.jpg
4.jpg
5.jpg
6.jpg


commands:

(base) qa@ubuntu:~$ gphoto2 --auto-detect
Model                          Port
----------------------------------------------------------
Sony Alpha-A6000 (Control)     usb:001,010
(base) qa@ubuntu:~$


// get config
(base) qa@ubuntu:~$ gphoto2 --get-config /main/capturesettings/exposurecompensation

// set config
gphoto2 --set-config /main/capturesettings/exposurecompensation=11

// specify camera
gphoto2 --summary --port=usb:001,010