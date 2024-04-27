from ultralytics import YOLO
import socket
import cv2
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

class CameraViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.client = None
        self.ip = ("192.168.36.56", 8080)
        self.url = None
        self.model = None
        self.CtrlData = {"AG":0, "LG":0, "RO":0}
        self.xywh = [0, 0, 0, 0]
        self.xywhn = [0, 0, 0, 0]
        self.capture = None
        self.setup_ui()

    def setup_ui(self):
        #yolo模型初始化
        self.model = YOLO('yolov8n.pt')
        #套接字初始化
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.url = "http:/192.168.36.56:81/stream"
        #UI初始化
        self.setWindowTitle("Camera Viewer")
        self.resize(640, 480)

        self.iplabel = QLabel("监听地址：")
        self.iplabel.setMinimumSize(80, 20)
        self.portlabel = QLabel("监听端口：")
        self.portlabel.setMinimumSize(80, 20)

        self.ipedit = QLineEdit()
        self.ipedit.setMinimumSize(160, 20)
        self.portedit = QLineEdit()
        self.portedit.setMinimumSize(160, 20)

        self.image_label = QLabel(self)
        self.image_label.setMinimumSize(640, 480)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.start_button = QPushButton("Start", self)
        self.start_button.setMinimumSize(160, 40)
        self.start_button.setShortcut("1")
        self.start_button.clicked.connect(self.start_capture)

        self.show_button = QPushButton("show", self)
        self.show_button.setMinimumSize(160, 40)
        self.show_button.setShortcut("2")
        self.show_button.clicked.connect(self.show_info)

        self.forward_button = QPushButton("forward", self)
        self.forward_button.setMinimumSize(160, 40)
        self.forward_button.setShortcut("W")
        self.forward_button.clicked.connect(self.forwardCtrl)

        self.back_button = QPushButton("back", self)
        self.back_button.setMinimumSize(160, 40)
        self.back_button.setShortcut("S")
        self.back_button.clicked.connect(self.backCtrl)

        self.left_button = QPushButton("left", self)
        self.left_button.setMinimumSize(160, 40)
        self.left_button.setShortcut("A")
        self.left_button.clicked.connect(self.leftCtrl)

        self.right_button = QPushButton("right", self)
        self.right_button.setMinimumSize(160, 40)
        self.right_button.setShortcut("D")
        self.right_button.clicked.connect(self.rightCtrl)

        main_layout = QGridLayout()

        main_layout.addWidget(self.iplabel, 0, 0)
        main_layout.addWidget(self.ipedit, 0, 1)
        main_layout.addWidget(self.portlabel, 0, 2)
        main_layout.addWidget(self.portedit, 0,3)
        main_layout.addWidget(self.image_label, 2,0, 2,4)
        main_layout.addWidget(self.start_button, 4, 0)
        main_layout.addWidget(self.forward_button, 4, 1)
        main_layout.addWidget(self.show_button, 4, 2)
        main_layout.addWidget(self.left_button, 5, 0)
        main_layout.addWidget(self.back_button, 5, 1)
        main_layout.addWidget(self.right_button, 5, 2)

        main_layout.setAlignment(self.iplabel, Qt.AlignHCenter)
        main_layout.setAlignment(self.portlabel, Qt.AlignHCenter)
        main_layout.setAlignment(self.ipedit, Qt.AlignJustify)
        main_layout.setAlignment(self.portedit, Qt.AlignJustify)

        self.setLayout(main_layout)

    @Slot()
    def start_capture(self):
        self.capture = cv2.VideoCapture(0)
        self.timer1 = QTimer(self)
        self.timer1.timeout.connect(self.detect_frame)
        self.timer1.start(1)

    def detect_frame(self):
        ret, frame = self.capture.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.model.predict(source=frame, verbose=False, max_det=1)

            for r in results:
                boxsz = r.boxes.xywhn.size()
                if int(boxsz[0]) == 0:
                    continue
                else:
                    for i in range(0, 4):
                        self.xywh[i] = int(r.boxes.xywh[0, i])
                        self.xywhn[i] = float(r.boxes.xywhn[0, i])

            frame = results[0].plot()

            h, w, ch = frame.shape
            img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)

            self.image_label.setPixmap(QPixmap.fromImage(img))

    def show_info(self):
        print("xywh:", self.xywh, "xywhn:", self.xywhn, self.CtrlData)
        print(self.CtrlData)

    def sent_ctrl(self):
        msg = "AG"+str(self.CtrlData['AG']) + 'LG'+str(self.CtrlData['LG']) + "RO"+str(self.CtrlData['RO'])
        print(msg)
        self.client.sendto(msg.encode('utf-8'), self.ip)

    def forwardCtrl(self):
        self.CtrlData = {"AG":90, "LG":40, "RO":0}
        self.sent_ctrl()

    def backCtrl(self):
        self.CtrlData = {"AG":270, "LG":40, "RO":0}
        self.sent_ctrl()

    def leftCtrl(self):
        self.CtrlData = {"AG":0, "LG":40, "RO":0}
        self.sent_ctrl()

    def rightCtrl(self):
        self.CtrlData = {"AG":180, "LG":40, "RO":0}
        self.sent_ctrl()


if __name__ == "__main__":
    app = QApplication()
    viewer = CameraViewer()
    viewer.show()
    app.exec_()