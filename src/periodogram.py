from PySide6.QtWidgets import QDialog, QVBoxLayout, QPushButton
import pyqtgraph as pg
from astropy.timeseries import LombScargle
import pandas as pd
import os


class LombScargleWidget(QDialog):
    def __init__(self, time, rri, index_min, index_max, filename, detrended):
        super().__init__()

        self.setWindowTitle("Lomb-Scargle Periodogram")

        self.index_min = index_min
        self.index_max = index_max
        self.filename = filename
        self.detrended = detrended

        self.plotWidget = pg.PlotWidget()

        # plot settings
        self.plotWidget.getPlotItem().setContentsMargins(10, 10, 10, 10)
        self.plotWidget.hideButtons()
        self.plotWidget.setMenuEnabled(False)

        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.saveFile)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.plotWidget)
        vlayout.addWidget(saveButton)

        self.setLayout(vlayout)

        freq, pgram = LombScargle(time, rri).autopower(maximum_frequency=0.5)

        self.plotWidget.setLabel(axis='left', text='Power [a.u.]')
        self.plotWidget.setLabel(axis='bottom', text='Frequency [Hz]')

        self.df_ls = pd.DataFrame(data=[freq, pgram]).T
        self.df_ls.columns = ['Frequency Hz', 'Power a.u.']

        self.plotWidget.plot(freq, pgram)

    def saveFile(self):
        print("save")

        dirpath = 'output/' + self.filename + '/'
        os.makedirs(dirpath, exist_ok=True)
        print(dirpath)

        if self.detrended is False:
            path = dirpath + 'ls' + '_' + str(self.index_min) + '-' + str(self.index_max) + '.csv'
        elif self.detrended is True:
            path = dirpath + 'ls' + '_' + 'detrended' + '_' + str(self.index_min) + '-' + str(self.index_max) + '.csv'
        print(path)

        self.df_ls.to_csv(path, index=False)
