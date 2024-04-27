import socket
import cv2
import io
from PIL import Image
import numpy as np
from ultralytics import YOLO
from cv2 import getTickCount, getTickFrequency

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
s.bind(("0.0.0.0", 9090))
model = YOLO("result/yolov8n4/weights/best.pt")

#储存目标位置信息，像素信息
xywh = [0, 0, 0, 0]
#归一化信息
xywhn = [0, 0, 0, 0]

len_sock = 100000

while True:
    loop_start = getTickCount()

    data, IP = s.recvfrom(len_sock)
    bytes_stream = io.BytesIO(data)
    image = Image.open(bytes_stream)
    img = np.asarray(image)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)  # ESP32采集的是RGB格式，要转换为BGR（opencv的格式）
    result = model.predict(source=img)

    for r in result:
        boxsz = r.boxes.xywhn.size()
        if int(boxsz[0]) == 0:
            continue
        else:
            for i in range(0, 4):
                xywh[i] = int(r.boxes.xywh[0, i])
                xywhn[i] = float(r.boxes.xywhn[0, i])

    img = result[0].plot()

    cv2.circle(img, (xywh[0], xywh[1]), int(xywh[3] / 10), (0, 0, 255))

    loop_time = getTickCount() - loop_start
    total_time = loop_time / (getTickFrequency())
    FPS = int(1 / total_time)
    # 在图像左上角添加FPS文本
    fps_text = f"FPS: {FPS:.2f}"
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_thickness = 2
    text_color = (0, 0, 255)  # 红色
    text_position = (10, 30)  # 左上角位置

    cv2.putText(img, fps_text, text_position, font, font_scale, text_color, font_thickness)
    cv2.imshow("ESP32 Capture Image", img)
    if cv2.waitKey(1) == ord("q"):
        break

