#-------------------------------------------------------------------------------
# Name:        Pegel Online Loader Processing Alogrithm
# Purpose:
#
# Author:      s4beluek
#
# Created:     21.08.2019
#-------------------------------------------------------------------------------

# -*- coding: utf-8 -*-

from PyQt5.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterEnum,
                       QgsApplication,
                       QgsWkbTypes)
import processing

import sys
sys.path.append(QgsApplication.qgisSettingsDirPath() + '\\processing\\scripts')

from pomodules.poqgsstations import PoQgsStations

class PegelOnlineLoader(QgsProcessingAlgorithm):
    """
    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs.
    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    QUERY_OPTIONS = ['Stations', 'Waterlevels']

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return PegelOnlineLoader()

    def name(self):
        return 'pegelonlineloader'

    def displayName(self):
        return self.tr('PegelOnline Loader')

    def shortHelpString(self):
        return self.tr("Example algorithm short description")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        self.addParameter(
            QgsProcessingParameterEnum(self.INPUT,
                                         self.tr(self.INPUT),
                                         self.QUERY_OPTIONS))
        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT,
                                              self.tr('Output layer'),
                                              QgsProcessing.TypeVectorAnyGeometry))

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """
        # Input parameter
        qx = self.parameterAsInt(parameters, self.INPUT, context)
        query = self.QUERY_OPTIONS[qx]
        feedback.pushInfo(query)

        # we're loading from PegelOnline
        if query == 'Stations':
            poQuery = PoQgsStations()
        # not implemented yet
        # elif query == 'Waterlevels':
            # poQuery = PoQgsCurrentW()
        else:
            feedback.pushInfo("This query is not implemented yet")
            # stop and return with empty dict
            return {}

        feedback.pushInfo("Downloading %s ..."%query)
        features = poQuery.getFeatures()
        # field and crs definitions from query
        fields = poQuery.fields
        crs = poQuery.crs
        feedback.pushInfo("Download done!")

        sink, dest_id = self.parameterAsSink(parameters,
                                             self.OUTPUT,
                                             context,
                                             fields,
                                             QgsWkbTypes.Point,
                                             crs)

        for f in features:
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        return {self.OUTPUT: dest_id}
