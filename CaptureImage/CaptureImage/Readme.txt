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


qa@apc1:~$ gphoto2  --auto-detect
Model                          Port
----------------------------------------------------------
Sony Alpha-A6000 (Control)     usb:003,029
Sony Alpha-A6000 (Control)     usb:003,026
Sony Alpha-A6000 (Control)     usb:003,037
Sony Alpha-A6000 (Control)     usb:003,024
Sony Alpha-A6000 (Control)     usb:003,052
Sony Alpha-A7r II (Control)    usb:003,050
qa@apc1:~$ gphoto2 --port usb:003,050 --get-config /main/capturesettings/exposurecompensation
Label: Exposure Compensation
Readonly: 0
Type: RADIO
Current: 0
Choice: 0 0
Choice: 1 0.001
Choice: 2 0.002
Choice: 3 5
Choice: 4 4.7
Choice: 5 4.5
Choice: 6 4.3
Choice: 7 4
Choice: 8 3.7
Choice: 9 3.5
Choice: 10 3.3
Choice: 11 3
Choice: 12 2.7
Choice: 13 2.5
Choice: 14 2.3
Choice: 15 2
Choice: 16 1.7
Choice: 17 1.5
Choice: 18 1.3
Choice: 19 1
Choice: 20 0.7
Choice: 21 0.5
Choice: 22 0.3
Choice: 23 -0.3
Choice: 24 -0.5
Choice: 25 -0.7
Choice: 26 -1
Choice: 27 -1.3
Choice: 28 -1.5
Choice: 29 -1.7
Choice: 30 -2
Choice: 31 -2.3
Choice: 32 -2.5
Choice: 33 -2.7
Choice: 34 -3
Choice: 35 -3.3
Choice: 36 -3.5
Choice: 37 -3.7
Choice: 38 -4
Choice: 39 -4.3
Choice: 40 -4.5
Choice: 41 -4.7
Choice: 42 -5
END
qa@apc1:~$
