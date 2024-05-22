from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox, QPushButton, QTabWidget, QVBoxLayout, QWidget

from PySide6.QtGui import QAction

from PySide6 import QtCore # TODO usunac

import pyqtgraph as pg
import pandas as pd
import neurokit2 as nk

import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # set working dir
        # self.filePath = getUserPath()
        self.filePath = QtCore.QDir.homePath() # TODO do porownania plus windows
        print(self.filePath)

        # variable initialization
        self.dfECG = None

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

        self.ecgLoadAction.triggered.connect(self.loadECG)
        self.markerLoadAction.triggered.connect(self.loadMarkers)

        self.loadMenu.addAction(self.ecgLoadAction)
        self.loadMenu.addAction(self.markerLoadAction)

        self.menuBar().addMenu(self.loadMenu)

    def loadECG(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "HRVpyGUI:\tLoad Polar-like formatted .txt", self.filePath, 'Text files (*.txt)')

        if fileName:
            self.filePath = os.path.dirname(fileName)
            self.setWindowTitle("HRVpyGUI: " + os.path.basename(fileName))

            self.dfECG = pd.read_csv(fileName, sep=';')
            self.dfECG["timestamp [s]"] = self.dfECG["timestamp [ms]"]/1000

            self.setSampling()

            self.dfECG["ecg cleaned [uV]"] = nk.ecg_clean(self.dfECG["ecg [uV]"], sampling_rate=self.fs)

            self.setPlots()

        else:
            print("ECG wasn't loaded.")
        # TODO if else filename nieistnieje

    def loadMarkers(self):
        # TODO ECG must be load first
        # if ecg exists then
        if self.dfECG is None:
            # TODO zmien according na inne slowo
            text = "ECG must be loaded before markers"
            detailedText = "Program calculates time from first timestamp in ECG and according markers"
            showInfoBox(text, QMessageBox.Warning, detailedText=detailedText)
        else:
             fileName, _ = QFileDialog.getOpenFileName(self, "HRVpyGUI:\tLoad Polar-like formatted .txt", self.filePath, 'Text files (*.txt)')
             dfMarkers = pd.read_csv(fileName, sep=';')
             print(dfMarkers)
        # else daj komunikat o wczytaniu ecg
        # TODO napisz klase, do ktorej bedziesz dawal w konstruktorze parametr z textem i to bedzie wyswietlalo odpowiednie komunikaty, bledy itp

    def setSampling(self):
        self.fs = 1000 * len(self.dfECG["timestamp [ms]"]) / self.dfECG["timestamp [ms]"].iloc[-1]
        print(f"Sampling Frequency: {self.fs:.2f} Hz")

    def setPlots(self):
        self.ecgPlot.clear()
        self.rriPlot.clear()
        self.rspPlot.clear()

        self.setECGPlot()

    def setECGPlot(self):
        self.ecgPlot.setLabel(axis='left', text='ECG [μV]') # TODO opisac, ze wczytanie ecg automatycznie wykonuje jego cleaning
        self.ecgPlot.setLabel(axis='bottom', text='Time [s]')
        self.ecgPlot.plot(self.dfECG["timestamp [s]"], self.dfECG["ecg cleaned [uV]"])

    # def setRSPPlot(self):
    # def setRRiPlot(self):


def createPlot():
    plot = pg.PlotWidget()

    plot.hideButtons()
    plot.setMenuEnabled(False)
    plot.getPlotItem().setContentsMargins(10, 10, 10, 10)

    return plot


def showInfoBox(text: str, icon, **kwargs):
    """
    **kwargs:
        detailedText: str

    Qt built in icons:
        QMessageBox.NoIcon
        QMessageBox.Question
        QMessageBox.Information
        QMessageBox.Warning
        QMessageBox.Critical
    """

    infobox = QMessageBox()
    infobox.setWindowTitle("HRVpyGUI: Warning")
    infobox.setIcon(icon)
    infobox.setText(text)
    if "detailedText" in kwargs.keys():
        infobox.setDetailedText(kwargs["detailedText"])

    infobox.exec()
