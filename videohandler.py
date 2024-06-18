import numpy as np
import cv2 as cv
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl


# Goal: Apply this class to an Overlay
class videoImage(QMediaPlayer):
    def __init__(self) -> None:
        super(videoImage, self).__init__(parent=None)
        self.width, self.height = 0, 0

    def getVideo(self):
        # Default, Goals: add parameters to change video capture
        self.setMedia(QMediaContent(QUrl("venv/aiko.mp4")))

