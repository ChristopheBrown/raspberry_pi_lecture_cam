from __future__ import division
from board import SCL, SDA
from guizero import *
from picamera import PiCamera
from time import gmtime, strftime
from uploader import Uploader
import Adafruit_PCA9685
import busio
import time

# Import the PCA9685 module
from adafruit_pca9685 import PCA9685
from adafruit_motor import servo

i2c = busio.I2C(SCL, SDA)

# PCA9685 class instance
pca = PCA9685(i2c)
pca.frequency = 50
servo_pan = servo.Servo(pca.channels[0])
servo_tilt = servo.Servo(pca.channels[1])

def move_up():
    if auto_select == 0:
        t_axis.value = t_axis.value - 10


def move_down():
    if auto_select == 0:
        t_axis.value = t_axis.value + 10


def move_left():
    if auto_select == 0:
        p_axis.value = p_axis.value + 3


def move_right():
    if auto_select == 0:
        p_axis.value = p_axis.value - 3


def p_axis_pos(slider_value):
    servo_pan.angle = int(slider_value)


def t_axis_pos(slider_value):
    servo_tilt.angle = int(slider_value)


def take_picture():
    global output, file_path
    if file_path == "":
        camera.stop_preview()
        app.warn("Error", "Select File Path")
        camera.start_preview(fullscreen=False, window=(10,-40,400,400))
    else:
        output = strftime(file_path + "/image%d%m%H%M.png", gmtime())
        camera.capture(output)
    if file_path != "" and save_cloud == 1:  
        gmail_recipients = ['REDACTED']
        u = Uploader(output, print_emails=True)
        u.upload()
        u.email(gmail_recipients)
        camera.stop_preview()
        app.info("Cloud Status", "Successfully uploaded to cloud!")
        camera.start_preview(fullscreen=False, window=(10,-40,400,400))


def start_rec():
    global output, file_path, rec
    if file_path == "":
        camera.stop_preview()
        app.warn("Error", "Select File Path")
        camera.start_preview(fullscreen=False, window=(10,-40,400,400))
    if file_path != "" and save_local == 1:   
        rec = 1
        rec_dot.value = "*REC"
        output = strftime(file_path + "/lecture%d%m%H%M.h264", gmtime())
        camera.start_recording(output)


def stop_rec():
    global rec
    rec = 0
    rec_dot.value = ""
    timer.value = 0
    camera.stop_recording()
    if file_path != "" and save_cloud == 1:  
        gmail_recipients = ['REDACTED']
        u = Uploader(output, print_emails=True)
        u.upload()
        u.email(gmail_recipients)
        camera.stop_preview()
        app.info("Cloud Status", "Successfully uploaded to cloud!")
        camera.start_preview(fullscreen=False, window=(10,-40,400,400))


def set_servo_pulse(channel, pulse):
    pulse_length = 1000000 
    pulse_length //= 60 
    print('{0}us per period'.format(pulse_length))
    pulse_length //= 4096
    print('{0}us per bit'.format(pulse_length))
    pulse *= 1000
    pulse //= pulse_length
    pwm.set_pwm(channel, 0, pulse)


def get_folder():
    global file_path
    camera.stop_preview()
    path.value = app.select_folder()
    file_path = str(path.value)
    camera.start_preview(fullscreen=False, window=(10,-40,400,400))


def counter():
    global rec
    if rec == 1: 
        timer.value = int(timer.value) + 1
    if int(timer.value) >= duration.value:
        stop_rec()


def toggle_local(selected_value): 
    global save_local

    if selected_value == " ON":
        save_local = 1
    else:
        save_local = 0


def toggle_cloud(selected_value): 
    global save_cloud

    if selected_value == " ON":
        save_cloud = 1
    else:
        save_cloud = 0


def close_window():
    camera.stop_preview()
    i2c.deinit()
    app.destroy()


# Set up camera
camera = PiCamera()
camera.resolution = (512, 384)
camera.hflip = True

# Start camera preview
camera.start_preview(fullscreen=False, window=(10,-40,400,400))

# Set up filename
output = ""
file_path = ""
B = False
rec = 0
save_local = 0
save_cloud = 0
auto_select = 0

# -------------------------- Window Setup ------------------------------
app = App(title="Lecture Cam GUI", height=800, width=480)
app.tk.attributes("-fullscreen", True)

# top box
title_box = Box(app, width="fill", align="top")
close_bt = PushButton(title_box, close_window, text="Exit", align="right")
title = Text(title_box, text="Lecture Cam  ", size=30, font="Times New Roman", color="blue", align="right")

# ------------------------ Recording Controls ---------------------------
rec_box = Box(app, height="fill", align="right", border=B)
rec_pad_box1 = Box(rec_box, height="fill", align="right", border=B)
rec_control_box = Box(rec_box, height="fill", align="right", border=B, layout="grid")
rec_pad_box2 = Box(rec_box, height="fill", align="right", border=B)

# pad text
# rec_pad1_text = Text(rec_pad_box1, text="  1               ")
rec_pad2_text = Text(rec_pad_box2, text="         ")

# recording controls
pad_rec1 = Text(rec_control_box, "                                              ", grid=[1, 0])
save_text = Text(rec_control_box, "Save Locally:", grid=[0, 1])
save_local_tog = Combo(rec_control_box, options=["OFF", " ON"], command=toggle_local, grid=[1, 1])
pad_rec2 = Text(rec_control_box, " ", grid=[0, 2])

save_text = Text(rec_control_box, "Screenshot:", grid=[0, 3])
screenshot = PushButton(rec_control_box, take_picture, text="Capture", grid=[1, 3])

folder_bt = PushButton(rec_control_box, command=get_folder, text="Select path", padx=10, pady=2, grid=[0, 4])
path = Text(rec_control_box, grid=[1, 4])
pad_rec3 = Text(rec_control_box, " ", grid=[0, 5])

rec_text = Text(rec_control_box, "Save to Cloud:", grid=[0, 6])
save_cloud_tog = Combo(rec_control_box, options=["OFF", " ON"], command=toggle_cloud, grid=[1, 6])
pad_rec4 = Text(rec_control_box, " ", grid=[0, 7])

dur_text = Text(rec_control_box, "Duration (sec):", grid=[0, 8])
duration = Slider(rec_control_box, start=0, end=150, grid=[1, 8])
pad_rec5 = Text(rec_control_box, " ", grid=[0, 9])

start_rec_bt = PushButton(rec_control_box, start_rec, text="Start Recording", grid=[0, 10])
timer = Text(rec_control_box, text="0", grid=[1, 10])
pad_rec6 = Text(rec_control_box, " ", grid=[0, 11])

stop_rec_bt = PushButton(rec_control_box, stop_rec, text="Stop Recording", grid=[0, 12])
rec_dot = Text(rec_control_box,  "", color="red", grid=[1, 12])

timer.repeat(1000, counter)

# ------------------------- Camera Controls -----------------------------
control_box = Box(app, width="fill", align="bottom", border=True)
control_title = Text(control_box, text="   Manual Control                        Camera Position  ", align="top")

pad_box1 = Box(control_box, height="fill", align="left", border=B)
manual_control_box = Box(control_box, height="fill", align="left", border=B, layout="grid")
pad_box2 = Box(control_box, height="fill", align="left", border=B)
position_control_box = Box(control_box, height="fill", align="left", border=B)
pad_box3 = Box(control_box, height="fill", align="left", border=B)
auto_control_box = Box(control_box, height="fill", align="left", border=B)

# pad text
pad1_text = Text(pad_box1, text="  ")
pad2_text = Text(pad_box2, text="              ")
pad3_text = Text(pad_box3, text="   ")

# manual control
up_button = PushButton(manual_control_box, command=move_up, text="UP", grid=[1, 0], padx=22, pady=10)
down_button = PushButton(manual_control_box, command=move_down, text="DOWN", grid=[1, 2], padx=10, pady=10)
left_button = PushButton(manual_control_box, command=move_left, text="LEFT", grid=[0, 1], padx=16, pady=10)
right_button = PushButton(manual_control_box, command=move_right, text="RIGHT", grid=[2, 1], padx=10, pady=10)

# position control
p_text = Text(position_control_box, text="Pan")
p_axis = Slider(position_control_box, command=p_axis_pos, start=0, end=180)
p_text = Text(position_control_box, text="Tilt")
t_axis = Slider(position_control_box, command=t_axis_pos, start=40, end=170, horizontal=True)


app.display()
