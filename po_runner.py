#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      bluek
#
# Created:     23.08.2019
#-------------------------------------------------------------------------------
from .pomodules.poqgsstations import PoQgsStations
from .pomodules.poqgscurrentw import PoQgsCurrentW

from .pomodules.urlreader import UrlReader

from urllib.parse import quote
from qgis.PyQt.QtWidgets import (QToolButton, QFrame)

from PyQt5 import QtGui

import os
from qgis.core import  (QgsVectorLayer,
                        QgsProject,
                        QgsLayerTreeLayer)


class PoRunner(object):
    """Class to orchestrate the different ui elements
    of the Pegel Online Displayer
    """

    def __init__(self, ui, iface):
        self.ui = ui
        self.iface = iface
        self.initUi()

#-------------------------------------------------------------------------------
#
# INITIALIZATION
#
#-------------------------------------------------------------------------------

    def initUi(self):
        """Initialize ui and layer dictionary

        Args:
            None
        Returns:
            None
        """
        self.layers = dict.fromkeys(
                ["water_lines", "water_areas",
                 "currentW", "stations"]
            )

        self.local_dir = os.path.dirname(os.path.realpath(__file__))
        self.styleDir = os.path.join(self.local_dir, "styles")


        ur = UrlReader("stations.json")
        self.data = ur.getJsonResponse()
        self.setStations(self.data)

        self.initToolbox()
        self.initConnects()
        self.toggleStyleButtons(False)



    def initConnects(self):
        """Connects the ui signals to functions

        Args:
            None
        Returns:
            None
        """
        self.ui.cbBasemap.toggled.connect(self.showBasemap)
        self.ui.pbLoad.clicked.connect(self.loadGraph)
        self.ui.pbLoadStations.clicked.connect(self.loadStations)
        self.ui.pbLoadCurrentW.clicked.connect(self.loadCurrentW)
        self.ui.bgStyleCurrentW.buttonClicked.connect(self.changeCurrentWStlye)


    def initToolbox(self):
        """Creates the toolbox in the windget and assigns the functions
        """

        # Zoom to Full Extent
        button = QToolButton()
        button.setDefaultAction(self.iface.actionZoomFullExtent())
        self.ui.hlayout_tools.insertWidget(0, button)

        # Zoom to Selection
        button = QToolButton()
        button.setDefaultAction(self.iface.actionZoomToSelected())
        self.ui.hlayout_tools.insertWidget(0, button)

        # Spacer for zoom and selection
        vLine = QFrame()
        vLine.setFrameShape(QFrame.VLine)
        vLine.setFrameShadow(QFrame.Sunken)
        self.ui.hlayout_tools.insertWidget(0, vLine)

        # Select the rectangle selection tool
        button = QToolButton()
        button.setDefaultAction(self.iface.actionSelectRectangle())
        self.ui.hlayout_tools.insertWidget(0, button)

        # Remove selection
        button = QToolButton()
        for a in self.iface.attributesToolBar().actions():
          if a.objectName() == 'mActionDeselectAll':
            button.setDefaultAction(a)
            break
        self.ui.hlayout_tools.insertWidget(0, button)



#-------------------------------------------------------------------------------
#
# USER INTERACTION
#
#-------------------------------------------------------------------------------

    def selectStations(self, selection):
        """Gets the features for the selected stations
        and passes them to the graph section of the widget

        Args:
            selection: List of selected Objects in the layer
        Returns:
            None
        """
        stations = []

        for id in selection:
            stations.append(self.layers["currentW"].getFeature(id))

        self.setStations(stations)




    def changeCurrentWStlye(self, button):
        """Changes the displayed information of the current water level

        Args:
            button: selcted radio button from the style button group
        Returns:
            None
        """
        if self.layers["currentW"] is None:
            return

        selected = button.objectName()
        styleToLoad = None

        if selected == "rbStyleT":
            styleToLoad = "currentWT.qml"
        if selected == "rbStyleM":
            styleToLoad = "currentWM.qml"
        if selected == "rbStyleN":
            styleToLoad =  "currentWN.qml"

        if styleToLoad is None:
            return

        self.loadStyle(styleToLoad)


    def loadStyle(self, styleToLoad):
        """Changes the style of the layer and refreshes it afterwards

        Args:
            styleToLoad: filename of the style to be applied
        Returns:
            None
        """
        self.layers["currentW"].loadNamedStyle(
                                    os.path.join(self.styleDir, styleToLoad)
                                )
        self.layerRefresh(self.layers["currentW"])


    def showBasemap(self):
        """Toggles the basemap layer

        When off, the map is not deleted but set invisible

        Args:
            None
        Returns:
            None
        """

        # Create the layers only if clicked to improve loading time of the plugin
        if self.ui.cbBasemap.isChecked() == True:
            if self.layers["water_lines"] is None:
                water_lines = os.path.join(self.local_dir, "basemap", "waters.gpkg|layername=water_l")

                vlayer = QgsVectorLayer(water_lines, "Flüsse", "ogr")
                if not vlayer.isValid():
                    print("Layer '%s' not valid"%water_lines)
                    return
                self.layers["water_lines"] = vlayer
                self.layers["water_lines"].willBeDeleted.connect(self.disconnectWaterLines)
                QgsProject.instance().addMapLayer(vlayer, False)
                layerTree = self.iface.layerTreeCanvasBridge().rootGroup()
                layerTree.insertChildNode(-1, QgsLayerTreeLayer(vlayer))

            if self.layers["water_areas"] is None:
                water_areas = os.path.join(self.local_dir, "basemap", "waters.gpkg|layername=water_f")

                vlayer = QgsVectorLayer(water_areas, "Gewässer", "ogr")
                if not vlayer.isValid():
                    print("Layer '%s' not valid"%water_areas)
                    return
                self.layers["water_areas"] = vlayer
                self.layers["water_areas"].willBeDeleted.connect(self.disconnectWaterAreas)
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
        """Assigns a list of stations to the select box of the graph section
        of the widget

        Args:
            stations: list of dictionaries containing the staions to be displayed
        Returns:
            None
        """

        self.ui.cbStations.clear()

        for e in stations:
            name = e['shortname']
            self.ui.cbStations.addItem(name)

        if len(stations) > 0:
            self.ui.cbStations.setCurrentIndex(0)

    def loadStations(self):
        """

        Args:
            None
        Returns:
            None
        """

        if not (self.layers["stations"] is None):
            return

        po = PoQgsStations()
        features = po.getFeatures()
        fields = po.fields
        crs = po.crs

        layer_uri = "Point?crs=%s"%crs.authid()
        vl = QgsVectorLayer(layer_uri, "Stationen", "memory")

        # Provider = Dateiebene
        pr = vl.dataProvider()
        pr.addAttributes(fields)
        pr.addFeatures(features)
        # layer-Informationen aktualisieren
        vl.updateFields()
        vl.updateExtents()
        e = vl.extent()

        self.layers["stations"] = vl
        self.layers["stations"].willBeDeleted.connect(self.disconnectStations)
        # Layer anzeigen
        QgsProject.instance().addMapLayer(vl)



    def loadCurrentW(self):
        """

        Args:
            None
        Returns:
            None
        """

        if not (self.layers["currentW"] is None):
            return

        po = PoQgsCurrentW()
        features = po.getFeatures()
        fields = po.fields
        crs = po.crs

        layer_uri = "Point?crs=%s"%crs.authid()
        vl = QgsVectorLayer(layer_uri, "Wasserstände", "memory")

        # Provider = Dateiebene
        pr = vl.dataProvider()
        pr.addAttributes(fields)
        pr.addFeatures(features)
        # layer-Informationen aktualisieren
        vl.updateFields()
        vl.updateExtents()
        e = vl.extent()


        vl.loadNamedStyle(os.path.join(self.styleDir, "currentWT.qml"))
        self.layers["currentW"] = vl
        self.layers["currentW"].willBeDeleted.connect(self.disconnectCurrentW)
        self.layers["currentW"].selectionChanged.connect(self.selectStations)

        # Layer anzeigen
        QgsProject.instance().addMapLayer(vl)

        self.toggleStyleButtons(True)



    def loadGraph(self):

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

#-------------------------------------------------------------------------------
#
# HELPER
#
#-------------------------------------------------------------------------------

    def layerRefresh(self, lyr):
        if self.iface.mapCanvas().isCachingEnabled():
            lyr.triggerRepaint()
        else:
            self.iface.mapCanvas().refresh()

    def toggleLabelButtons(self, newState):
        self.ui.rbLabelValue.setEnabled(newState)
        self.ui.rbLabelName.setEnabled(newState)

    def toggleStyleButtons(self, newState):
        self.ui.rbStyleT.setEnabled(newState)
        self.ui.rbStyleN.setEnabled(newState)
        self.ui.rbStyleM.setEnabled(newState)

    def disconnectStations(self):
        self.layers["stations"] = None
        self.setStations([])

    def disconnectCurrentW(self):
        self.layers["currentW"] = None
        self.toggleStyleButtons(False)
        pass

    def disconnectWaterLines(self):
        self.layers["water_lines"] = None

    def disconnectWaterAreas(self):
        self.layers["water_areas"] = None