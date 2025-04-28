from PySide6.QtWidgets import QComboBox, QFileDialog, QHBoxLayout, QLabel, QMainWindow, QMenu, QMessageBox, QPushButton, QTabWidget, QVBoxLayout, QWidget

from PySide6.QtGui import QAction

import pyqtgraph as pg
import pandas as pd
import neurokit2 as nk

# from files
import hrv_utils
import prsa
import data_window
import periodogram

import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # set working dir
        self.filePath = hrv_utils.getUserPath()

        print(self.filePath)

        # variable initialization
        self.filename = None
        self.detrended = False
        self.dfECG = None
        self.markers = []

        self.setWindowTitle("HRVpyGUI")

        # create plots
        self.rriPlot = createPlot()
        self.rspPlot = createPlot()
        self.ecgPlot = createPlot()

        # create RRi buttons
        self.evalButton = QPushButton("Evaluate HRV")
        self.evalButton.clicked.connect(self.evalHRV)
        self.periodogramButton = QPushButton("Periodogram")
        self.periodogramButton.clicked.connect(self.createLSplot)

        self.markerLabel = QLabel("Time markers:")
        self.markerLabel.setFixedHeight(20)
        self.markerComboBox = QComboBox()
        self.markerComboBox.activated.connect(self.setMarkers)
        self.markerComboBox.setMinimumContentsLength(20)

        # position buttons
        markersLayout = QVBoxLayout()
        markersLayout.addWidget(self.markerLabel)
        markersLayout.addWidget(self.markerComboBox)

        buttonLayout = QVBoxLayout()
        buttonLayout.addWidget(self.evalButton)
        buttonLayout.addWidget(self.periodogramButton)
        buttonLayout.addLayout(markersLayout)

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

        # File Menu
        self.loadMenu = QMenu("&File")

        self.ecgLoadAction = QAction("Load Polar-like formatted ECG")
        self.markerLoadAction = QAction("Load Polar-like formatted Time markers")

        self.ecgLoadAction.triggered.connect(self.loadECG)
        self.markerLoadAction.triggered.connect(self.loadMarkers)

        self.loadMenu.addAction(self.ecgLoadAction)
        self.loadMenu.addAction(self.markerLoadAction)

        # Preprocessing Menu
        self.preprocMenu = QMenu("&Preprocessing")

        self.detrendAction = QAction("Detrend whole data set using smoothness priors methods")
        self.detrendAction.triggered.connect(self.applyDetrend)

        self.preprocMenu.addAction(self.detrendAction)

        self.menuBar().addMenu(self.loadMenu)
        self.menuBar().addMenu(self.preprocMenu)

    def loadECG(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "HRVpyGUI:\tLoad Polar-like formatted ECG", self.filePath, 'Text files (*.txt)')

        if fileName:
            self.filePath = os.path.dirname(fileName)
            self.filename = os.path.basename(fileName)
            self.setWindowTitle("HRVpyGUI: " + self.filename)

            self.dfECG = pd.read_csv(fileName, sep=';')
            self.dfECG["timestamp [s]"] = self.dfECG["timestamp [ms]"] / 1000

            self.detrended = False
            self.setSampling()

            self.dfECG["ecg cleaned [uV]"] = nk.ecg_clean(self.dfECG["ecg [uV]"], sampling_rate=self.fs)
            self.dfRR, self.peaks = hrv_utils.getRR(self.dfECG["ecg cleaned [uV]"], self.dfECG["timestamp [ms]"], self.fs)

            self.setPlots()

        else:
            print("ECG wasn't loaded.")

    def loadMarkers(self):
        if self.dfECG is None:
            text = "ECG must be loaded before markers"
            detailedText = "Program calculates time from first timestamp in ECG and markers"
            showInfoBox(text, QMessageBox.Warning, detailedText=detailedText)
        else:
            fileName, _ = QFileDialog.getOpenFileName(self, "HRVpyGUI:\tLoad Polar-like formatted time markers", self.filePath, 'Text files (*.txt)')
            if fileName:
                self.dfMarkers = pd.read_csv(fileName, sep=';')

                print("\nLoaded markers:")
                print(self.dfMarkers)
                print("\n")

                self.addMarkers()

            else:
                print("\nMarkers weren't loaded.")

    def addMarkers(self):
        """Adds markers to QComboBox"""

        time0 = self.dfECG["Phone timestamp"][0]
        self.dfMarkers["timestamp [s]"] = hrv_utils.timestampsToTime(self.dfMarkers["Phone timestamp"], time0)

        self.markers = []
        markers_string = []

        self.markers.append([self.dfECG["timestamp [s]"].iloc[0], self.dfECG["timestamp [s]"].iloc[-1]])  # Whole data set
        markers_string.append("Whole data set")

        for i in range(0, len(self.dfMarkers), 2):
            self.markers.append([self.dfMarkers["timestamp [s]"][i], self.dfMarkers["timestamp [s]"][i + 1]])
            markers_string.append(f"{self.dfMarkers['timestamp [s]'][i]:.2f}s : {self.dfMarkers['timestamp [s]'][i + 1]:.2f}s")

        self.markerComboBox.clear()

        self.markerComboBox.addItems(markers_string)  # NOTE  can't be centered without making items editable

    def setMarkers(self):
        selected_marker = self.markerComboBox.currentIndex()
        self.regionSelector.setRegion(self.markers[selected_marker])

    def setSampling(self):
        self.fs = 1000 * len(self.dfECG["timestamp [ms]"]) / self.dfECG["timestamp [ms]"].iloc[-1]
        print(f"Sampling Frequency: {self.fs:.2f} Hz")

    def setPlots(self):
        self.ecgPlot.clear()
        self.rriPlot.clear()
        self.rspPlot.clear()

        self.setECGPlot()
        self.setRRiPlot()
        self.setRSPPlot()

    def setECGPlot(self):
        self.ecgPlot.setLabel(axis='left', text='ECG [μV]')
        self.ecgPlot.setLabel(axis='bottom', text='Time [s]')
        self.ecgPlot.plot(self.dfECG["timestamp [s]"], self.dfECG["ecg cleaned [uV]"])

    def setRRiPlot(self):
        self.rriPlot.setLabel(axis='left', text='RRI [ms]')
        self.rriPlot.setLabel(axis='bottom', text='Time [s]')
        self.rriPlot.plot(self.dfRR["Time [s]"], self.dfRR["RR Intervals [ms]"])

        self.setRegionSelector()

    def setRSPPlot(self):
        # ECG-Derived Respiration (EDR)
        ecg, _ = nk.ecg_process(self.dfECG["ecg [uV]"], method='hamilton2002', sampling_rate=self.fs)
        ecg_rsp = nk.ecg_rsp(ecg["ECG_Rate"], sampling_rate=self.fs)

        self.rspPlot.setLabel(axis='left', text='Respiration [a.u.]')
        self.rspPlot.setLabel(axis='bottom', text='Time [s]')
        self.rspPlot.plot(self.dfECG["timestamp [s]"], ecg_rsp)

    def setRegionSelector(self):
        """Creates LineearRegionItem"""

        self.regionSelector = pg.LinearRegionItem(bounds=(self.dfRR["Time [s]"].iloc[0], self.dfRR["Time [s]"].iloc[-1]))

        # Set default region to entire data set
        self.regionSelector.setRegion((self.dfRR["Time [s]"].iloc[0], self.dfRR["Time [s]"].iloc[-1]))

        self.updateRegionSelector()
        self.regionSelector.sigRegionChanged.connect(self.updateRegionSelector)

        self.rriPlot.addItem(self.regionSelector)

    def updateRegionSelector(self):
        """Gets selected region x values."""

        region_values = self.regionSelector.getRegion()

        # Set bounds to nearest data points
        x_min = min(self.dfRR["Time [s]"], key=lambda val: abs(val - region_values[0]))
        x_max = min(self.dfRR["Time [s]"], key=lambda val: abs(val - region_values[1]))
        self.regionSelector.setRegion([x_min, x_max])

        self.x_min_index = self.dfRR[self.dfRR["Time [s]"] == x_min].index[0]
        self.x_max_index = self.dfRR[self.dfRR["Time [s]"] == x_max].index[0]

    def applyDetrend(self):
        """Applies Smoothness Priors method on whole data set"""

        if self.detrended is True:
            print("\nAlready detrened\n")
        elif self.detrended is False:
            self.dfRR["RR Intervals [ms]"] = hrv_utils.signal_detrend_tarvainen2002(self.dfRR["RR Intervals [ms]"])
            self.detrended = True

            new_title = self.windowTitle() + " --> DETRENDED"
            self.setWindowTitle(new_title)

            self.rriPlot.clear()
            self.setRRiPlot()

    def evalHRV(self):
        # selectedPeaks = self.peaks.copy()
        # selectedPeaks["ECG_R_Peaks"] = selectedPeaks["ECG_R_Peaks"][self.x_min_index:self.x_max_index + 1]

        print(self.x_min_index)
        npRRI = self.dfRR["RR Intervals [ms]"][self.x_min_index:self.x_max_index + 1].to_numpy()
        npRRI_TIME = self.dfRR["Time [s]"][self.x_min_index:self.x_max_index + 1].to_numpy()
        
        selectedPeaks = {
            "RRI": npRRI,
            "RRI_TIME": npRRI_TIME
        }

        timestamps = pd.DataFrame({'Marker Start [s]': [self.dfRR["Time [s]"][self.x_min_index]],
                                   'Marker Stop [s]': [self.dfRR["Time [s]"][self.x_max_index]]})
        timestamps_indexes = pd.DataFrame({'Marker Start index': [self.x_min_index],
                                           'Marker Stop index': [self.x_max_index]})

        hrv_time = nk.hrv_time(selectedPeaks, sampling_rate=self.fs)[["HRV_SDNN", "HRV_RMSSD", "HRV_pNN50"]]
        hrv_freq = nk.hrv_frequency(selectedPeaks, sampling_rate=self.fs)[["HRV_LFn", "HRV_HFn", "HRV_LFHF"]]
        hrv_nonlin = nk.hrv_nonlinear(selectedPeaks, sampling_rate=self.fs)[["HRV_SD1", "HRV_SD2", "HRV_SampEn", "HRV_CSI", "HRV_CVI", "HRV_DFA_alpha1"]]

        prsaL = 16
        prsaDC, prsaAC = prsa.eval_ACDC(self.dfRR["RR Intervals [ms]"][self.x_min_index:self.x_max_index + 1].to_numpy(), L=prsaL, T=1)
        prsaDF = pd.DataFrame({'PRSA DC': [prsaDC],
                               'PRSA AC': [prsaAC]})

        if self.detrended is False:
            detrened = pd.DataFrame({'Detrened': ['False']})
        if self.detrended is True:
            detrened = pd.DataFrame({'Detrened': ['True']})

        hrv_all = pd.concat([detrened, timestamps, timestamps_indexes, hrv_time, hrv_freq, hrv_nonlin, prsaDF], axis=1)
        hrv_all_renamed = hrv_all.rename(columns={'HRV_SDNN': 'SDNN',
                                                  'HRV_RMSSD': 'RMSSD',
                                                  'HRV_pNN50': 'pNN50',
                                                  'HRV_LFn': 'LFn',  # normalized
                                                  'HRV_HFn': 'HFn',  # normalized
                                                  'HRV_LFHF': 'LF/HF',
                                                  'HRV_SD1': 'SD1',
                                                  'HRV_SD2': 'SD2',
                                                  'HRV_SampEn': 'Sample Entropy',
                                                  'HRV_CSI': 'CSI',
                                                  'HRV_CVI': 'CVI',
                                                  'HRV_DFA_alpha1': 'DFA alpha 1'})

        for i in range(len(hrv_all)):
            print(hrv_all_renamed.loc[i])

        # Change float precision
        for col in hrv_all_renamed:
            tmp = hrv_all_renamed[col][0]
            if isinstance(tmp, float):
                tmp = round(tmp, 2)
                hrv_all_renamed[col][0] = tmp

        outputWindow = data_window.outputWidget(self.filename, hrv_all_renamed, detrended=self.detrended)
        outputWindow.exec()

    def createLSplot(self):
        selectedRR = self.dfRR[self.x_min_index:self.x_max_index + 1].copy()
        self.lsWindow = periodogram.LombScargleWidget(selectedRR["Time [s]"], selectedRR["RR Intervals [ms]"], self.x_min_index, self.x_max_index, self.filename, self.detrended)

        self.lsWindow.show()


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
