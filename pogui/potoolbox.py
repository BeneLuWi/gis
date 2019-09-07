#-------------------------------------------------------------------------------
# Name:        PoToolbox
# Purpose:     Initialize the toolbox for the widget
#
# Author:      Benedikt Lüken-Winkels
#
# Created:     23.08.2019
#-------------------------------------------------------------------------------

from qgis.PyQt.QtWidgets import QToolButton, QFrame, QCompleter
from PyQt5.QtCore import QStringListModel

class PoToolbox(object):
    """Class providing functionality to the toolbox of the widget

    Attributes:
        ui: Ui object to reference the ui elements
        iface: Reference to layers
        stations: List of stations for the autocompletion of the search bar
    """

    def __init__(self, ui, iface, stations, layers, graphDisplay):
        self.iface = iface
        self.ui = ui
        self.stations = stations
        self.layers = layers
        self.graphDisplay = graphDisplay
#-------------------------------------------------------------------------------
#
# INITIALIZATION
#

    def initUi(self):
        """Creates the toolbox in the widget and assigns the functions
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

        # Remove selection
        button = QToolButton()
        for a in self.iface.attributesToolBar().actions():
          if a.objectName() == 'mActionDeselectAll':
            button.setDefaultAction(a)
            break
        self.ui.hlayout_tools.insertWidget(0, button)

        # Select the rectangle selection tool
        button = QToolButton()
        button.setDefaultAction(self.iface.actionSelectRectangle())
        self.ui.hlayout_tools.insertWidget(0, button)

        # Create completer for search bar
        list = []
        for station in self.stations:
            list.append(station["shortname"])
        model = QStringListModel()
        model.setStringList(list)
        completer = QCompleter()
        completer.setModel(model)
        completer.setCaseSensitivity(0) # Case insensitive

        self.ui.leStationSearch.setCompleter(completer)

    def initConnections(self):
        self.ui.leStationSearch.returnPressed.connect(self.searchStation)

#-------------------------------------------------------------------------------
#
#   SEARCH
#

    def searchStation(self):
        """Search for station in the currently selected layer, if it's either
        the stations or the current-waterlevel layer. If found, select the
        corresponding feature and make it available in the graph section
        """

        search = self.ui.leStationSearch.text()

        if len(search) == 0:
            return

        if (not (self.layers["stations"] is None)
                and self.iface.activeLayer().name() == "Stationen"):
            # Search through all the features
            for feat in self.layers["stations"].getFeatures():
                if search.lower() == feat["shortname"].lower():
                    # Remove previous selections
                    for a in self.iface.attributesToolBar().actions():
                      if a.objectName() == 'mActionDeselectAll':
                        a.trigger()
                        break
                    # Select and zoom
                    self.layers["stations"].select([feat.id()])
                    self.iface.actionZoomToSelected().trigger()
                    self.graphDisplay.setStations([feat])
                    return

        if (not (self.layers["currentW"] is None)
                and self.iface.activeLayer().name() == "Wasserstände"):
            # Search through all the features
            for feat in self.layers["currentW"].getFeatures():
                if search.lower() == feat["shortname"].lower():
                    # Remove previous selections
                    for a in self.iface.attributesToolBar().actions():
                      if a.objectName() == 'mActionDeselectAll':
                        a.trigger()
                        break
                    # Select and zoom
                    self.layers["currentW"].select([feat.id()])
                    self.iface.actionZoomToSelected().trigger()
                    self.graphDisplay.setStations([feat])