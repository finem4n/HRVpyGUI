import qdarktheme

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QBrush, QColor, QFontMetrics, QPainter
from PySide6.QtWidgets import QApplication, QGridLayout, QMenu, QLabel, \
        QMainWindow, QVBoxLayout, QPushButton, QSpinBox, QWidget

import numpy as np


class AnimationWidget(QWidget):
    def __init__(self, n, freq):
        super().__init__()

        self.outerColor = QColor(29, 41, 39)
        self.innerColor = QColor(32, 68, 64)
        self.movingColor = QColor(38, 57, 53)

        self.RMIN = 50
        self.RMAX = 150

        self.n = n
        self.freq = freq

        # create timers
        self.frame_timer = QTimer(timeout=self.update)
        self.getReadyTimer = QTimer(singleShot=True, timeout=self.animate)
        self.totalTimer = QTimer(singleShot=True, timeout=self.stopExercise)
        self.timer = QTimer()

    def startExercise(self):
        self.t = 60 / self.freq * 1000  # signle breath period in ms
        self.T = self.t * self.n  # total time in ms

        self.frame_timer.start(16)  # animation refresh rate - approx. 60 Hz
        self.getReadyTimer.start(3500)

    def animate(self):
        self.timer.start(self.t)
        self.totalTimer.start(self.T)

    def paintEvent(self, event):
        self.drawStaticCircle()

        if self.getReadyTimer.isActive():
            self.drawStaticCircle2()
            self.drawGettingReady()

        elif self.totalTimer.isActive():
            self.drawMovingCircle()
            self.drawStaticCircle2()
            self.drawRemainingTime()
            self.drawTime()

        else:
            self.drawStaticCircle2()

    # draw outer circle
    def drawStaticCircle(self):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.outerColor))
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(self.rect().center(), self.RMAX, self.RMAX)

    # draw inner circle
    def drawStaticCircle2(self):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(self.innerColor))
        painter.setPen(Qt.NoPen)

        painter.drawEllipse(self.rect().center(), self.RMIN, self.RMIN)

    def drawMovingCircle(self):
        radius = - (self.RMAX - self.RMIN)/2 * np.cos(self.timer.remainingTime() / self.t * 2 * np.pi) + (self.RMAX - self.RMIN)/2 + self.RMIN

        if np.sin(self.timer.remainingTime()/self.t * 2 * np.pi) > 0:
            self.drawText("Breath Out")
        else:
            self.drawText("Breath In")

        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.movingColor))

        painter.drawEllipse(self.rect().center(), radius, radius)

    def drawText(self, text):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        font = painter.font()
        font.setPointSize(16)
        painter.setFont(font)

        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)

        x = (self.width() - text_width) / 2
        y = 450

        painter.drawText(x, y, text)

    def drawTime(self):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        font = painter.font()
        font.setPointSize(16)
        painter.setFont(font)

        if self.timer.remainingTime() > self.t:
            text = f"{self.t / 1000:.1f}"
        else:
            text = f"{self.timer.remainingTime() / 1000:.1f}"

        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()

        x = (self.width() - text_width) / 2
        y = (self.height() + text_height) / 2

        painter.drawText(x, y, text)

    def drawRemainingTime(self):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        font = painter.font()
        font.setPointSize(16)
        painter.setFont(font)

        time = int(self.totalTimer.remainingTime()/1000)
        mm = time // 60
        ss = time % 60
        text = f'{mm:02d}:{ss:02d}'

        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)

        x = (self.width() - text_width) / 2
        y = 50

        painter.drawText(x, y, text)

    def drawGettingReady(self):
        painter = QPainter(self)

        painter.setRenderHint(QPainter.Antialiasing)
        font = painter.font()
        font.setPointSize(16)
        painter.setFont(font)

        time = int(self.getReadyTimer.remainingTime()/1000)
        text = f'{time}'

        fm = QFontMetrics(font)
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()

        x = (self.width() - text_width) / 2
        y = (self.height() + text_height) / 2

        painter.drawText(x, y, text)

    def setParams(self, n, freq):
        self.n = n
        self.freq = freq

    def stopExercise(self):
        # stop every timer
        self.frame_timer.stop()
        self.timer.stop()
        self.getReadyTimer.stop()
        self.totalTimer.stop()

        # clear texts, animations, etc.
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # set window properties
        height = 700
        width = 500

        self.setMinimumSize(width, height)
        self.setMaximumSize(width, height)

        self.setWindowTitle("pyBreathe")

        # create spinboxes labels
        self.nLabel = QLabel("Number of repetitions")
        self.freqLabel = QLabel("Frequency in breaths per minute")

        self.nLabel.setFixedHeight(20)
        self.freqLabel.setFixedHeight(20)

        # create spinboxes
        self.nSpinBox = self.createSpinBox(11)
        self.freqSpinBox = self.createSpinBox(12)

        # create total time label
        self.totalTimeLabel = QLabel()
        self.totalTimeLabel.setFixedHeight(20)
        self.setTimeLabelText()

        # create buttons
        self.startButton = QPushButton("Start")
        self.stopButton = QPushButton("Stop")

        # create Animation Widget
        self.animWidget = AnimationWidget(self.nSpinBox.value(),
                                          self.freqSpinBox.value())

        # connect elements to functions
        self.nSpinBox.textChanged.connect(self.applySpinBox)
        self.freqSpinBox.textChanged.connect(self.applySpinBox)

        self.startButton.clicked.connect(self.animWidget.startExercise)
        self.stopButton.clicked.connect(self.animWidget.stopExercise)

        # create menubar
        self.presetsMenu = QMenu('&Presets')

        self.preset1Act = QAction('n = 36, f = 12 bpm')  # 0.2 Hz
        self.preset2Act = QAction('n = 54, f = 18 bpm')  # 0.(3) Hz

        self.preset1Act.triggered.connect(lambda: self.applyPreset(36, 12))
        self.preset2Act.triggered.connect(lambda: self.applyPreset(54, 18))

        self.presetsMenu.addAction(self.preset1Act)
        self.presetsMenu.addAction(self.preset2Act)

        self.menuBar().addMenu(self.presetsMenu)

        # position spinboxes with grid layout
        spinboxes_grid = QGridLayout()

        spinboxes_grid.addWidget(self.nLabel, 0, 0)
        spinboxes_grid.addWidget(self.freqLabel, 0, 1)

        spinboxes_grid.addWidget(self.nSpinBox, 1, 0)
        spinboxes_grid.addWidget(self.freqSpinBox, 1, 1)

        # position elements in vertical layout
        vmain_layout = QVBoxLayout()

        vmain_layout.addWidget(self.animWidget)
        vmain_layout.addLayout(spinboxes_grid)
        vmain_layout.addWidget(self.totalTimeLabel)
        vmain_layout.addWidget(self.startButton)
        vmain_layout.addWidget(self.stopButton)

        central_window = QWidget()
        central_window.setLayout(vmain_layout)

        self.setCentralWidget(central_window)

    def applyPreset(self, n, f):
        self.nSpinBox.setValue(n)
        self.freqSpinBox.setValue(f)

        self.setTimeLabelText()

    def createSpinBox(self, default_value):
        nSpinBox = QSpinBox()
        nSpinBox.setMinimum(1)
        nSpinBox.setMaximum(500)
        nSpinBox.setSingleStep(1)
        nSpinBox.setValue(default_value)

        return nSpinBox

    def applySpinBox(self):
        self.animWidget.setParams(self.nSpinBox.value(),
                                  self.freqSpinBox.value())

        self.setTimeLabelText()

    def setTimeLabelText(self):
        time = 1 / self.freqSpinBox.value() * 60 * self.nSpinBox.value()
        mm = time // 60
        ss = round(time % 60)

        if ss == 60:
            ss = 0
            mm += 1

        self.totalTimeLabel.setText(f"Total time:\t{mm:.0f}min {ss:.0f}s")


if __name__ == "__main__":
    app = QApplication()

    qdarktheme.setup_theme()

    window = MainWindow()
    window.show()

    app.exec()
