import cv2
from ultralytics import YOLO
from cv2 import getTickCount, getTickFrequency
# 加载 YOLOv8 模型
model = YOLO("result/yolov8n4/weights/best.pt")

url = "http://192.168.120.142:81/stream"

# 获取摄像头内容，参数 0 表示使用默认的摄像头
cap = cv2.VideoCapture(0)

#储存目标位置信息，像素信息
xywh = [0, 0, 0, 0]
#归一化信息
xywhn = [0, 0, 0, 0]

while cap.isOpened():
    loop_start = getTickCount()
    success, frame = cap.read(0)  # 读取摄像头的一帧图像

    results = model.predict(source=frame, max_det=1, show_boxes=False) # 对当前帧进行目标检测并显示结果

    for r in results:
        boxsz = r.boxes.xywhn.size()
        if int(boxsz[0]) == 0:
            continue
        else:
            for i in range(0, 4):
                xywh[i] = int(r.boxes.xywh[0, i])
                xywhn[i] = float(r.boxes.xywhn[0, i])

    annotated_frame = results[0].plot()

    cv2.circle(annotated_frame, (xywh[0], xywh[1]), int(xywh[3]/10), (0, 0, 255))
    # 中间放自己的显示程序
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

    cv2.putText(annotated_frame, fps_text, text_position, font, font_scale, text_color, font_thickness)
    cv2.imshow('img', annotated_frame)
    # 通过按下 'q' 键退出循环
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()  # 释放摄像头资源
cv2.destroyAllWindows()  # 关闭OpenCV窗口
