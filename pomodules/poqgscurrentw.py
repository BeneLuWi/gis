#-------------------------------------------------------------------------------
# Name:        POStations for QGIS
# Purpose:
#
# Author:      s4beluek
#
# Created:     21.08.2019
#-------------------------------------------------------------------------------

from .pocurrentw import PoCurrentW
from qgis.PyQt.QtCore import QVariant
from qgis.core import  (QgsField,
                        QgsFields,
                        QgsFeature,
                        QgsGeometry,
                        QgsPointXY,
                        QgsCoordinateReferenceSystem)

class PoQgsCurrentW(PoCurrentW):
    """
    """
    def __init__(self):
        super(PoQgsCurrentW, self).__init__()

        self.fields = None
        self.crs = None

    def getFeatures(self):
        """

        Args:

        Returns:

        """

        data = self.getData()

        self.crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)

        # Diese Fields anlegen:
        self.fnames = (
                        'uuid', 'number',
                        'shortname', 'timestamp',
                        'value', 'trend',
                        'stateMnwMhw', 'stateNswHsw'
                        )

        self.fields = QgsFields()
        self.fields.append(QgsField("uuid" , QVariant.String ))
        self.fields.append(QgsField("number" , QVariant.Int ))
        self.fields.append(QgsField("shortname" , QVariant.String ))
        self.fields.append(QgsField("timestamp" , QVariant.String ))
        self.fields.append(QgsField("value" , QVariant.Int ))
        self.fields.append(QgsField("trend" , QVariant.Int))
        self.fields.append(QgsField("stateMnwMhw" , QVariant.String ))
        self.fields.append(QgsField("stateNswHsw" , QVariant.String ))

        # Verarbeitung
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