from PySide6.QtWidgets import QDialog, QPushButton, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView

import os


class outputWidget(QDialog):
    def __init__(self, filename, dataframe, detrended: bool):
        super().__init__()

        self.setWindowTitle("HRV indices")

        self.filename = filename
        self.dataframe = dataframe
        self.detrended = detrended

        self.tableWidget = QTableWidget()
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(len(dataframe) + 1)
        self.tableWidget.setRowCount(len(dataframe.columns))
        for i in range(len(dataframe.columns)):
            self.tableWidget.setItem(i, 0, QTableWidgetItem(dataframe.columns[i]))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(str(dataframe.iloc[0, i])))

        # Auto resize qtable with window
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        saveButton = QPushButton("Save as .csv")
        saveButton.clicked.connect(self.saveFile)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.tableWidget)
        vlayout.addWidget(saveButton)

        self.setLayout(vlayout)

    def saveFile(self):
        print("save")

        dirpath = 'output/' + self.filename + '/'
        os.makedirs(dirpath, exist_ok=True)
        print(dirpath)

        marker_start = self.dataframe["Marker Start index"][0]
        marker_stop = self.dataframe["Marker Stop index"][0]

        if self.detrended is False:
            path = dirpath + 'hrv_indices' + '_' + str(marker_start) + '-' + str(marker_stop) + '.csv'
        elif self.detrended is True:
            path = dirpath + 'hrv_indices' + '_' + 'detrended' + '_' + str(marker_start) + '-' + str(marker_stop) + '.csv'
        print(path)

        self.dataframe.to_csv(path, index=False)
