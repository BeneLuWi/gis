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

import os

class PoRunner(object):

    def __init__(self, ui, iface):
        self.ui = ui
        self.iface = iface


    def show_basemap():
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
        self.ui.lbGraph.setPixmap(pixmap)
        self.ui.lbGraph.resize(pixmap.width(), pixmap.height())