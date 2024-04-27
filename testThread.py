import socket
import cv2
import io
from PIL import Image
import numpy as np
from ultralytics import YOLO
import time
import threading

# SockForCli = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
# SockForCli.bind(("0.0.0.0", 9090))
#
# SockForSer = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
# SockForSer.bind(("192.168.126.184", 1234))

url = "http://192.168.126.184:81/stream"

cap = cv2.VideoCapture(url)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

flag = None
frame = None
StartTime = None
model = YOLO("yolov8n.pt")

def getframe():
    global frame, cap, flag
    while cap.isOpened():
        flag, frame = cap.read()
        cv2.waitKey(1)

def getframeUDP():
    global frame, s
    while True:
        data, IP = s.recvfrom(100000)
        bytes_stream = io.BytesIO(data)
        image = Image.open(bytes_stream)
        image = np.asarray(image)
        frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)  # ESP32采集的是RGB格式，要转换为BGR（opencv的格式）

def detectframe():
    global frame, model, StartTime
    while True:
        StartTime = time.time()
        results = model.predict(source=frame, max_det=1, verbose=False)
        result = results[0].plot()
        print(int(1/(time.time()-StartTime)))
        cv2.imshow("result", result)
        c = cv2.waitKey(1)
        if c == 27:
            break

def msgsent():
    global SockForSer
    while True:
        KeyWord = cv2.waitKey(1)
        if KeyWord == ord('w'):
            pass
        elif KeyWord == ord('a'):
            pass
        elif KeyWord == ord('s'):
            pass
        elif KeyWord == ord('d'):
            pass

thread1 = threading.Thread(target=getframe)
thread2 = threading.Thread(target=detectframe)
thread3 = threading.Thread(target=msgsent)
thread1.start()
thread2.start()
thread3.start()



