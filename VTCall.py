import sys
import asyncio
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QImage, QPixmap, QPalette
from PyQt5.QtMultimediaWidgets import QVideoWidget
from videohandler import videoImage
import numpy as np
import cv2 as cv
import mss


class Overlay(QWidget):
    def __init__(self, videoHandle) -> None:
        super(Overlay, self).__init__(parent=None)
        self.setWindowTitle("Overlay")
        self.detection_rect = mss.mss().monitors[1]
        self.video = videoHandle()
        self.image = QVideoWidget()
        flags = 0
        flags |= Qt.WindowType.WindowTransparentForInput
        flags |= Qt.WindowStaysOnTopHint
        flags |= Qt.FramelessWindowHint
        flags |= Qt.Tool
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_elements()
        self.update_geometry()
        self.show()
        self.get_video()

    def setup_elements(self):
        # Line Corners of Overlay with a 1 pixel Solid Magenta line
        self.corners = QLabel("", self)
        self.corners.setStyleSheet("border: 1px solid magenta;")

        self.image = QVideoWidget()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def update_geometry(self):
        self.setGeometry(
            self.detection_rect["left"],
            self.detection_rect["top"],
            self.detection_rect["width"],
            self.detection_rect["height"]
        )
        # Set Corners, aka, Covers Entire Width/Height of screen
        self.corners.setGeometry(
            0,
            0,
            self.detection_rect["width"],  # Detects ASpect Ratio from Monitor
            self.detection_rect["height"]
        )

    def get_video(self):
        self.video.getVideo()
        self.video.setVideoOutput(self.image)
        self.layout.addWidget(self.image)
        self.image.show()
        self.image.setFullScreen(True)
        self.video.play()


class GUI(QMainWindow):
    update_signal = pyqtSignal()

    def __init__(self) -> None:
        super(GUI, self).__init__()
        # load_from_file()
        # save_to_file()

        # Main Window Metadata
        self.setWindowTitle("Practice")  # Title
        self.resize(1200, 1000)  # Window Size
        qApp.setStyleSheet("QWidget{font-size:18px;}")

        # Main Window Layout
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        self.layout = QGridLayout()
        centralWidget.setLayout(self.layout)

        self.overlay = Overlay(videoImage)
        self.mainTab = MainTab(self, self.overlay)  # NiL Method
        self.setup_tabs();
        self.show()

        self.update_signal.connect(self.update_graphics)  # Signals Update

        self.backgroud_thread = Worker(self.background_thread_loop)
        self.backgroud_thread.start()

    def setup_tabs(self):
        self.tabs = QTabWidget(self)
        self.layout.addWidget(self.tabs, 0, 0)

        self.underwatch_tab = self.mainTab
        self.tabs.addTab(self.underwatch_tab, "Main Window")

    def closeEvent(self, event):
        self.backgroud_thread.terminate()
        event.accept()

    async def background_thread_loop(self):
        while True:
            await asyncio.sleep(1 / 1000)

    def update_graphics(self):
        if self.computer_vision.resolution_changed or self.computer_vision.regions_changed:  # Handles Res Change
            self.overlay.close()  # restart
            self.overlay = Overlay()  # Reinit

        self.mainTab.update_current_frame()  # Update Main Tab
        self.overlay.update()  # Update the Overlay


class MainTab(QWidget):
    def __init__(self, parent, overlay):
        super(MainTab, self).__init__(parent)
        self.inner_layout = QGridLayout(self)
        self.inner_layout.setAlignment(Qt.AlignTop)
        self.label = QLabel();

        scroll_widget = QWidget(self)
        scroll_widget.setLayout(self.inner_layout)

        scroll_area = QScrollArea(self)
        scroll_area.setBackgroundRole(QPalette.Base)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        outer_layout = QGridLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(scroll_area)
        self.setLayout(outer_layout)


class Worker(QThread):
    def __init__(self, funtion):
        super(QThread, self).__init__()
        self.function = funtion

    def run(self):
        asyncio.run(self.function())


app = QApplication(sys.argv)
app_window = GUI()
app.exec()
