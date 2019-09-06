#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      bluek
#
# Created:     23.08.2019
#-------------------------------------------------------------------------------

from PyQt5 import QtGui
from urllib.parse import quote
from ..pomodules.urlreader import UrlReader

class PoGraphdisplay(object):

    def __init__(self, ui, iface):
        self.iface = iface
        self.ui = ui

    def initConnections(self):
        self.ui.pbLoad.clicked.connect(self.loadGraph)

    def setStations(self, stations):
        """Assigns a list of stations to the select box of the graph section
        of the widget

        Args:
            stations: list of dictionaries containing the staions to be displayed
        """

        self.ui.cbStations.clear()

        for e in stations:
            name = e['shortname']
            self.ui.cbStations.addItem(name)

        if len(stations) > 0:
            self.ui.cbStations.setCurrentIndex(0)

    def loadGraph(self):
        """Gets the currently selected station from the select box and creates
        the graphic to be displayed in the widget
        """
        # Anzahl der Tage in der SpinBox
        days = days = self.ui.sbDays.value()
        # Name der Station aus der ComboBox
        station = self.ui.cbStations.currentText() # benutze quote() für die url

        requestUrl = (
            "stations/" + quote(station) +
            "/W/measurements.png?start=P" +
            str(days) + "D"
            )

        ur1 = UrlReader(requestUrl)

        img_data = ur1.getDataResponse()
        # Fehler-Code abfragen (es gibt Stationen ohne Wasserstandsdaten)

        if img_data is None:
            self.ui.lbGraph.clear()
            self.ui.lbGraph.setText("Graph konnte nicht geladen werden.")
            return
        # wenn ok, dann Graphik einsetzen
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(img_data) # img_data als Ergebnis von getDataResponse
        self.ui.lbGraph.setPixmap(pixmap)
        self.ui.lbGraph.resize(pixmap.width(), pixmap.height())

