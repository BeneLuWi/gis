#-------------------------------------------------------------------------------
# Name:        PoRunner
# Purpose:
#
# Author:      bluek
#
# Created:     23.08.2019
#-------------------------------------------------------------------------------
from .pomodules.urlreader import UrlReader

from .pogui.potoolbox import PoToolbox
from .pogui.pographdisplay import PoGraphdisplay
from .pogui.polayers import PoLayermanagent

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
        """
        self.layers = dict.fromkeys(
                ["water_lines", "water_areas",
                 "currentW", "stations"]
            )

        # Load station data
        ur = UrlReader("stations.json")
        data = ur.getJsonResponse()

        # Init and Connect Toolbox
        self.toolBox = PoToolbox(self.ui, self.iface, data)
        self.toolBox.initUi()

        # Init and Connect Graphdisplay Graphdisplay
        self.graphDisplay = PoGraphdisplay(self.ui, self.iface)
        self.graphDisplay.setStations(data)
        self.graphDisplay.initConnections()

        # Init and Connect Layermanagement
        self.layermanagement = PoLayermanagent(self.ui, self.iface,
                                            self.layers, self.graphDisplay)
        self.layermanagement.initUi()
        self.layermanagement.initConnects()

