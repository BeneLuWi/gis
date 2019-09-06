#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      bluek
#
# Created:     23.08.2019
#-------------------------------------------------------------------------------

from qgis.PyQt.QtWidgets import QToolButton, QFrame, QCompleter
from PyQt5.QtCore import QStringListModel

class PoToolbox(object):

    def __init__(self, ui, iface, stations):
        self.iface = iface
        self.ui = ui
        self.stations = stations

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
