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
from qgis.core import  (QgsVectorLayer,
                        QgsProject,
                        QgsLayerTreeLayer)


class PoRunner(object):
    """
    """
    def __init__(self, ui, iface):
        self.ui = ui
        self.iface = iface
        self.layers = dict.fromkeys(["water_lines", "water_areas"])
        self.initUi()


    def initUi(self):
        """

        Args:
            None
        Returns:
            None
        """

        self.initConnects()

        ur = UrlReader("stations")
        data = ur.getJsonResponse()
        self.setStations(data)

        self.local_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "basemap")



    def initConnects(self):
        """

        Args:
            None
        Returns:
            None
        """
        self.ui.cbBasemap.toggled.connect(self.showBasemap)
        self.ui.pbLoad.clicked.connect(self.doLoadGraph)

    def showBasemap(self):
        """

        Args:
            None
        Returns:
            None
        """

        # Create the layers only if clicked to improve loading time of the plugin
        if self.ui.cbBasemap.isChecked() == True:
            if self.layers["water_lines"] is None:
                water_lines = os.path.join(self.local_dir, "waters.gpkg|layername=water_l")

                vlayer = QgsVectorLayer(water_lines, "Flüsse", "ogr")
                if not vlayer.isValid():
                    print("Layer '%s' not valid"%water_lines)
                    return
                self.layers["water_lines"] = vlayer
                self.layers["water_lines"].willBeDeleted.connect(self.doDisconnectWaterLines)
                QgsProject.instance().addMapLayer(vlayer, False)
                layerTree = self.iface.layerTreeCanvasBridge().rootGroup()
                layerTree.insertChildNode(-1, QgsLayerTreeLayer(vlayer))

            if self.layers["water_areas"] is None:
                water_areas = os.path.join(self.local_dir, "waters.gpkg|layername=water_f")

                vlayer = QgsVectorLayer(water_areas, "Gewässer", "ogr")
                if not vlayer.isValid():
                    print("Layer '%s' not valid"%water_areas)
                    return
                self.layers["water_areas"] = vlayer
                self.layers["water_areas"].willBeDeleted.connect(self.doDisconnectWaterAreas)
                QgsProject.instance().addMapLayer(vlayer, False)
                layerTree = self.iface.layerTreeCanvasBridge().rootGroup()
                layerTree.insertChildNode(-1, QgsLayerTreeLayer(vlayer))

            # Make the layers visible
            (QgsProject.instance()
                .layerTreeRoot()
                .findLayer(self.layers["water_lines"].id())
                .setItemVisibilityChecked(True))

            (QgsProject.instance()
                .layerTreeRoot()
                .findLayer(self.layers["water_areas"].id())
                .setItemVisibilityChecked(True))


        else:
            if not (self.layers["water_lines"] is None):
                (QgsProject.instance()
                    .layerTreeRoot()
                    .findLayer(self.layers["water_lines"].id())
                    .setItemVisibilityChecked(False))
            if not (self.layers["water_areas"] is None):
                (QgsProject.instance()
                    .layerTreeRoot()
                    .findLayer(self.layers["water_areas"].id())
                    .setItemVisibilityChecked(False))

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

    def doDisconnectWaterLines(self):
        self.layers["water_lines"] = None

    def doDisconnectWaterAreas(self):
        self.layers["water_areas"] = None