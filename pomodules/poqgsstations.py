#-------------------------------------------------------------------------------
# Name:        PoQgsStations
# Purpose:     Get stations from Pegel Online and create QGIS-Features
#
# Author:      Benedikt Lüken-Winkels
#
# Created:     21.08.2019
#-------------------------------------------------------------------------------

from .postations import PoStations
from qgis.PyQt.QtCore import QVariant
from qgis.core import  (QgsField,
                        QgsFields,
                        QgsFeature,
                        QgsGeometry,
                        QgsPointXY,
                        QgsCoordinateReferenceSystem)

class PoQgsStations(PoStations):
    """Gets stations from Pegel Online and creates QGIS-Features
    """
    def __init__(self):
        super(PoQgsStations, self).__init__()

        self.fields = None
        self.crs = None

    def getFeatures(self):
        """Parses the Pegel Online station data to QgsFeature
        Returns:
            features: QgsFeature of the PO station data
        """

        data = self.getData()

        self.crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        # Fields for the features
        self.fnames = ('uuid', 'number', 'shortname', 'longname', 'km', 'agency', 'water')

        self.fields = QgsFields()
        self.fields.append(QgsField("uuid" , QVariant.String ))
        self.fields.append(QgsField("number" , QVariant.Int ))
        self.fields.append(QgsField("shortname" , QVariant.String ))
        self.fields.append(QgsField("longname" , QVariant.String ))
        self.fields.append(QgsField("km" , QVariant.Double ))
        self.fields.append(QgsField("agency" , QVariant.String ))
        self.fields.append(QgsField("water" , QVariant.String ))

        # Processing
        features = []
        for d in data:
            f = QgsFeature(self.fields)

            geo = d["geometry"]
            attrs = d["attributes"]

            f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(geo[0] or 0, geo[1] or 0)))

            # Set attributes for Feature
            for i in range(len(self.fnames)):
                attrName = self.fnames[i]
                f[i] = attrs[i]

            features.append(f)

        return features