#-------------------------------------------------------------------------------
# Name:        PegelOnline Graph Display
# Purpose:
#
# Author:      s4beluek
#
# Created:     22.08.2019
#-------------------------------------------------------------------------------

import sys
from PyQt5.QtWidgets import (QWidget,
                            QApplication)
from PyQt5 import QtCore, QtGui, QtWidgets
from .pomodules.urlreader import UrlReader
from urllib.parse import urljoin

class PoGraphDisplay(QWidget):

    def __init__(self):
        super().__init__()

        # Aufbau der Elemente im Widget
        self.initUI()
        self.setupUI()

    def initUI(self):
        """

        Args:
            None
        Returns:
            None
        """
        self.lbStation = QtWidgets.QLabel()
        self.comboBox = QtWidgets.QComboBox()
        self.lbTage = QtWidgets.QLabel()
        self.sbDays = QtWidgets.QSpinBox()
        self.pbLoad = QtWidgets.QPushButton()
        self.lbGraph = QtWidgets.QLabel()

    def setupUI(self):
        """

        Args:
            None
        Returns:
            None
        """
        # übergeordnetes Layout
        self.verticalLayout = QtWidgets.QVBoxLayout(self)

        # Input section
        self.horizontalLayout = QtWidgets.QHBoxLayout()

        self.lbStation.setText("Station")
        self.horizontalLayout.addWidget(self.lbStation)

        self.horizontalLayout.addWidget(self.comboBox)

        self.lbTage.setText("Tage")
        self.horizontalLayout.addWidget(self.lbTage)

        self.sbDays.setMinimum(0)
        self.sbDays.setMaximum(30)
        self.sbDays.setValue(30)
        self.horizontalLayout.addWidget(self.sbDays)

        self.pbLoad.setText("Laden")
        self.pbLoad.clicked.connect(self.doLoadGraph)
        self.horizontalLayout.addWidget(self.pbLoad)

        self.verticalLayout.addLayout(self.horizontalLayout)

        # Graph Section
        # nur ein Label widget
        self.verticalLayout.addWidget(self.lbGraph)

        # dritte Zeile: Spacer!
        # dritte Zeile
        spacerItem = QtWidgets.QSpacerItem(20, 40,
                                    QtWidgets.QSizePolicy.Minimum,
                                    QtWidgets.QSizePolicy.Expanding)

        self.verticalLayout.addItem(spacerItem)

    def doLoadGraph(self):
        """

        Args:
            None
        Returns:
            None
        """
        # Anzahl der Tage in der SpinBox
        days = days = self.sbDays.value()
        # Name der Station aus der ComboBox
        station = self.comboBox.currentText() # benutze quote() für die url
        print("Lade den Graphen")
        # url zusammenbauen

        requestUrl = "stations/" + station + "/W/measurements.png?start=P" + str(days) + "D"

        # Urlreader mit getDataResponse
        ur1 = UrlReader(requestUrl)

        img_data = ur1.getDataResponse()
        # Fehler-Code abfragen (es gibt Stationen ohne Wasserstandsdaten)

        if img_data is None:
            return
        # wenn ok, dann Graphik einsetzen
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(img_data) # img_data als Ergebnis von getDataResponse
        self.lbGraph.setPixmap(pixmap)
        self.lbGraph.resize(pixmap.width(), pixmap.height())

    def setStations(self, stations):
        """

        Args:
            None
        Returns:
            None
        """
        self.comboBox.clear()
        for e in stations:
            name = e['shortname']
            self.comboBox.addItem(name)

        self.comboBox.setCurrentIndex(0)


# Test
if __name__ == '__main__':
    ur = UrlReader("stations")
    data = ur.getJsonResponse()

    app = QApplication(sys.argv)
    w = PoGraphDisplay()
    w.setStations(data)
    w.show()
    sys.exit(app.exec_())