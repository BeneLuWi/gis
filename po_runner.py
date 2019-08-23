#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      bluek
#
# Created:     23.08.2019
# Copyright:   (c) bluek 2019
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from .pomodules.poqgsstations import PoQgsStations
#from .pomodules.poqgscurrentw import PoQgsCurrentW
from .pomodules.urlreader import UrlReader

from urllib.parse import quote
from PyQt5 import QtGui
import os

class PoRunner(object):

    def __init__(self, ui, iface):
        self.ui = ui
        self.iface = iface
        self.initUi()


    def initUi(self):

        self.init_connects()

        ur = UrlReader("stations")
        data = ur.getJsonResponse()
        self.setStations(data)




    def init_connects(self):
        #self.ui.cbBasemap.toggled.connect(self.doBasemapOptionChanged)
        self.ui.pbLoad.clicked.connect(self.doLoadGraph)

    def show_basemap(self):
        local_dir = os.path.join(__file__, "basemap")
        water_lines = os.path.join(local_dir, "waters.gpkg|layername=water_l")
        water_areas = os.path.join(local_dir, "waters.gpkg|layername=water_f")

        vlayer = QgsVectorLayer(water_lines, "Flüsse", "ogr")
        if not vlayer.isValid():
            print("Layer '%s' not valid"%water_lines)
            return
        QgsProject.instance().addMapLayer(vlayer, False)
        layerTree = iface.layerTreeCanvasBridge().rootGroup()
        layerTree.insertChildNode(-1, QgsLayerTreeLayer(vlayer))

        vlayer = QgsVectorLayer(water_areas, "Gewässer", "ogr")
        if not vlayer.isValid():
            print("Layer '%s' not valid"%water_areas)
            return
        QgsProject.instance().addMapLayer(vlayer, False)
        layerTree = iface.layerTreeCanvasBridge().rootGroup()
        layerTree.insertChildNode(-1, QgsLayerTreeLayer(vlayer))

    def setStations(self, stations):
        """

        Args:
            None
        Returns:
            None
        """
        self.ui.cbStations.clear()
        for e in stations:
            name = e['shortname']
            self.ui.cbStations.addItem(name)

        self.ui.cbStations.setCurrentIndex(0)

    def doLoadGraph(self):
        """

        Args:
            None
        Returns:
            None
        """
        # Anzahl der Tage in der SpinBox
        days = days = self.ui.sbDays.value()
        # Name der Station aus der ComboBox
        station = self.ui.cbStations.currentText() # benutze quote() für die url
        print("Lade den Graphen")
        # url zusammenbauen

        requestUrl = "stations/" + quote(station) + "/W/measurements.png?start=P" + str(days) + "D"

        # Urlreader mit getDataResponse
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