from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QMenu, QPushButton, QTabWidget, QVBoxLayout, QWidget

from PySide6.QtGui import QAction

import pyqtgraph as pg

import platform
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.filePath = getUserPath()
        print(self.filePath)
        self.setWindowTitle("HRVpyGUI")

        # create plots
        self.rriPlot = createPlot()
        self.rspPlot = createPlot()
        self.ecgPlot = createPlot()

        # create RRi buttons
        self.evalButton = QPushButton("Evaluate HRV")
        self.periodogramButton = QPushButton("Periodogram")
        self.markersButton = QPushButton("Set markers")

        self.markerLabel = QLabel("Markers:")
        self.markerComboBox = QComboBox()

        # position buttons
        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.evalButton)
        buttonLayout.addWidget(self.periodogramButton)
        buttonLayout.addWidget(self.markerComboBox)
        buttonLayout.addWidget(self.markersButton)

        # create RRi widget
        rriLayout = QHBoxLayout()
        rriLayout.addWidget(self.rriPlot)
        rriLayout.addLayout(buttonLayout)

        self.rriWidget = QWidget()
        self.rriWidget.setLayout(rriLayout)

        # create RSP widget
        self.rspWidget = QWidget()
        self.rspLayout = QVBoxLayout()
        self.rspLayout.addWidget(self.rspPlot)
        self.rspWidget.setLayout(self.rspLayout)

        # create ECG widget
        self.ecgWidget = QWidget()
        self.ecgLayout = QVBoxLayout()
        self.ecgLayout.addWidget(self.ecgPlot)
        self.ecgWidget.setLayout(self.ecgLayout)

        # position widgets in application
        self.tabsWidget = QTabWidget()

        self.tabsWidget.addTab(self.rriWidget, 'RRi')
        self.tabsWidget.addTab(self.rspWidget, 'RSP')
        self.tabsWidget.addTab(self.ecgWidget, 'ECG')

        self.setCentralWidget(self.tabsWidget)

        # Menubar
        self.loadMenu = QMenu("&File")

        self.ecgLoadAction = QAction("Load Polar-like formatted ECG")
        self.markerLoadAction = QAction("Load Polar-like formatted Markers")

        self.loadMenu.addAction(self.ecgLoadAction)
        self.loadMenu.addAction(self.markerLoadAction)

        self.menuBar().addMenu(self.loadMenu)

        def loadMarkers(self):
            fileName, _ = QFileDialog.getOpenFileName(self, "Load Polar-like formatted .txt", self.filesPath, 'Text files (*.txt)')


def createPlot():
    plot = pg.PlotWidget()

    plot.hideButtons()
    plot.setMenuEnabled(False)
    plot.getPlotItem().setContentsMargins(10, 10, 10, 10)

    return plot


def getUserPath():
    if platform.system() == 'Windows':
        path = os.path.expanduser('~user')

    elif platform.system() in ('Linux', 'Darwin'):
        path = os.path.expanduser('~')

    else:
        path = os.getcwd()

    return path
