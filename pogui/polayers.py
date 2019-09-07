#-------------------------------------------------------------------------------
# Name:        PoLayermanagent
# Purpose:     Creates the Layers and handles changes to them
#
# Author:      Benedikt Lüken-Winkels
#
# Created:     23.08.2019
#-------------------------------------------------------------------------------

import os

from ..pomodules.poqgscurrentw import PoQgsCurrentW
from ..pomodules.poqgsstations import PoQgsStations

from qgis.core import  (QgsVectorLayer,
                        QgsProject,
                        QgsLayerTreeLayer)


class PoLayermanagent(object):
    """Controls the different layers of the plugin

    Attributes:
        ui: Ui object to reference the ui elements
        iface: Reference to layers
        graphDisplay: Reference to the graph display section for search bar
    """
    def __init__(self, ui, iface, layers, graphDisplay):
        self.iface = iface
        self.ui = ui
        self.layers = layers
        self.graphDisplay = graphDisplay

        self.local_dir = os.path.dirname(os.path.realpath(__file__))
        self.styleDir = os.path.join(self.local_dir, "styles")

#-------------------------------------------------------------------------------
#
# INITIALIZATION
#

    def initUi(self):
        self.toggleStyleButtons(False)
        self.toggleLabelButtons(False)
        self.ui.cbLabels.setEnabled(False)

    def initConnects(self):
        self.ui.cbBasemap.toggled.connect(self.showBasemap)
        self.ui.pbLoadStations.clicked.connect(self.loadStations)
        self.ui.pbLoadCurrentW.clicked.connect(self.loadCurrentW)
        self.ui.cbLabels.clicked.connect(self.toggleLabels)
        self.ui.bgStyleCurrentW.buttonClicked.connect(self.changeCurrentWStyle)
        self.ui.bgLabelCurrentW.buttonClicked.connect(self.changeCurrentWLabels)

#-------------------------------------------------------------------------------
#
#   LAYER INTERACTION
#

    def selectStations(self, selection):
        """Gets the features for the selected stations
        and passes them to the graph section of the widget

        Args:
            selection: List of selected Objects in the layer
        """
        stations = []

        for id in selection:
            stations.append(self.layers["currentW"].getFeature(id))

        self.graphDisplay.setStations(stations)


#-------------------------------------------------------------------------------
#
#   BASE MAP
#

    def showBasemap(self):
        """Toggles the basemap layer

        When off, the map is not deleted but set invisible
        """

        # Create the layers only if clicked to improve loading time of the plugin
        if self.ui.cbBasemap.isChecked() == True:
            if self.layers["water_lines"] is None:
                water_lines = os.path.join(
                    self.local_dir, "basemap",
                    "waters.gpkg|layername=water_l"
                    )

                vlayer = QgsVectorLayer(water_lines, "Flüsse", "ogr")
                if not vlayer.isValid():
                    print("Layer '%s' not valid"%water_lines)
                    return
                self.layers["water_lines"] = vlayer
                (self.layers["water_lines"]
                    .willBeDeleted
                    .connect(self.disconnectWaterLines))

                QgsProject.instance().addMapLayer(vlayer, False)
                layerTree = self.iface.layerTreeCanvasBridge().rootGroup()
                layerTree.insertChildNode(-1, QgsLayerTreeLayer(vlayer))

            if self.layers["water_areas"] is None:
                water_areas = os.path.join(
                    self.local_dir, "basemap",
                    "waters.gpkg|layername=water_f"
                    )

                vlayer = QgsVectorLayer(water_areas, "Gewässer", "ogr")
                if not vlayer.isValid():
                    print("Layer '%s' not valid"%water_areas)
                    return
                self.layers["water_areas"] = vlayer
                (self.layers["water_areas"]
                    .willBeDeleted
                    .connect(self.disconnectWaterAreas))

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

#-------------------------------------------------------------------------------
#
#   CURRENT WATERLEVEL LAYER
#

    def loadCurrentW(self):
        """Load and create the current-waterlevel layer
        """

        if not (self.layers["currentW"] is None):
            return

        self.ui.leStationSearch.setEnabled(True)

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
        self.ui.cbLabels.setEnabled(True)


    def changeCurrentWStyle(self, button):
        """Changes the displayed information of the current water level

        Args:
            button: selcted radio button from the style button group
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

        if not (styleToLoad is None):
            self.loadStyle(styleToLoad)
            self.ui.bgLabelCurrentW.buttonClicked.emit(
                self.ui.bgLabelCurrentW.checkedButton()
            )


    def toggleLabels(self):
        """Enable or disable and remove labels from the current-waterlevel layer
        """
        if self.layers["currentW"] is None:
            return

        if self.ui.cbLabels.isChecked() == True:
            self.toggleLabelButtons(True)
        else:
            self.layers["currentW"].setLabelsEnabled(False)
            self.iface.actionMapTips().setChecked(False)
            self.layerRefresh(self.layers["currentW"])
            self.toggleLabelButtons(False)

    def changeCurrentWLabels(self, button):
        """Changes the displayed information of the current water level

        Args:
            button: selcted radio button from the style button group
        """
        if self.layers["currentW"] is None or button is None:
            return

        # Load the chosen label
        selected = button.objectName()
        styleToLoad = None

        if selected == "rbLabelNames":
            styleToLoad = "currentWLabelNames.qml"
        if selected == "rbLabelValues":
            styleToLoad = "currentWLabelValues.qml"
        if selected == "rbLabelMapTips":
            self.iface.actionMapTips().setChecked(True)
            styleToLoad = "currentWMapTip.qml"

        if not (styleToLoad is None):
            self.layers["currentW"].setLabelsEnabled(True)
            self.loadStyle(styleToLoad)



    def loadStyle(self, styleToLoad):
        """Changes the style of the current water levellayer and
        refreshes it afterwards

        Args:
            styleToLoad: filename of the style to be applied
        """
        self.layers["currentW"].loadNamedStyle(
                                    os.path.join(self.styleDir, styleToLoad)
                                    )
        self.layerRefresh(self.layers["currentW"])



#-------------------------------------------------------------------------------
#
#   STATIONS LAYER
#

    def loadStations(self):
        """Create and display the stations layer
        """

        if not (self.layers["stations"] is None):
            return

        self.ui.leStationSearch.setEnabled(True)

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

#-------------------------------------------------------------------------------
#
# HELPERS (do what their names say)
#


    def layerRefresh(self, lyr):
        if self.iface.mapCanvas().isCachingEnabled():
            lyr.triggerRepaint()
        else:
            self.iface.mapCanvas().refresh()

    def toggleLabelButtons(self, newState):
        self.ui.rbLabelValues.setEnabled(newState)
        self.ui.rbLabelNames.setEnabled(newState)
        self.ui.rbLabelMapTips.setEnabled(newState)

        if (newState == False and
                not (self.ui.bgLabelCurrentW.checkedButton() is None)):
            self.ui.bgLabelCurrentW.setExclusive(False)
            self.ui.bgLabelCurrentW.checkedButton().setChecked(False)
            self.ui.bgLabelCurrentW.setExclusive(True)

    def toggleStyleButtons(self, newState):
        self.ui.rbStyleT.setEnabled(newState)
        self.ui.rbStyleN.setEnabled(newState)
        self.ui.rbStyleM.setEnabled(newState)

    def disconnectStations(self):
        self.layers["stations"] = None
        self.graphDisplay.setStations([])
        if (self.layers["currentW"] is None):
            self.ui.leStationSearch.setEnabled(False)

    def disconnectCurrentW(self):
        self.layers["currentW"] = None
        self.ui.cbLabels.setChecked(False)
        self.ui.cbLabels.setEnabled(False)
        self.iface.actionMapTips().setChecked(False)
        self.toggleLabelButtons(False)

        if (self.layers["stations"] is None):
            self.ui.leStationSearch.setEnabled(False)

        self.toggleStyleButtons(False)

    def disconnectWaterLines(self):
        self.layers["water_lines"] = None

    def disconnectWaterAreas(self):
        self.layers["water_areas"] = None