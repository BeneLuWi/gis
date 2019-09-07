#-------------------------------------------------------------------------------
# Name:        PoRunner
# Purpose:     Initialize and orchestrate the different ui elements
#
# Author:      Benedikt Lüken-Winkels
#
# Created:     23.08.2019
#-------------------------------------------------------------------------------
from .pomodules.urlreader import UrlReader

from .pogui.potoolbox import PoToolbox
from .pogui.pographdisplay import PoGraphdisplay
from .pogui.polayers import PoLayermanagent

class PoRunner(object):
    """Orchestrates the different ui elements
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


    def initUi(self):
        """Initialize ui
        """

        self.layers = dict.fromkeys([
                            "water_lines", "water_areas",
                            "currentW", "stations"
                            ])

        # Load station data for graph and search bar
        ur = UrlReader("stations.json")
        data = ur.getJsonResponse()

        # Init and Connect Graphdisplay Graphdisplay
        self.graphDisplay = PoGraphdisplay(self.ui, self.iface)
        self.graphDisplay.setStations(data)
        self.graphDisplay.initConnections()

        # Init and Connect Layermanagement
        self.layermanagement = PoLayermanagent(self.ui,
                                               self.iface,
                                               self.layers,
                                               self.graphDisplay)
        self.layermanagement.initUi()
        self.layermanagement.initConnects()

        # Init and Connect Toolbox
        self.toolBox = PoToolbox(self.ui,
                                 self.iface,
                                 data,
                                 self.layers,
                                 self.graphDisplay)
        self.toolBox.initUi()
        self.toolBox.initConnections()