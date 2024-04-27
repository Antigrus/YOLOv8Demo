import cv2
from ultralytics import YOLO
import time

starttime = None
model = YOLO("yolov8n.pt")
cap = cv2.VideoCapture(0)

StartTime = time.time()
while cap.isOpened():
    starttime = time.time()
    flag, frame = cap.read()
    #results = model.predict(source=frame, verbose=False)
    #result = results[0].plot()
    cv2.imshow("results", frame)
    print(time.time()-starttime)
    if cv2.waitKey(1) == 27:
        break