#-------------------------------------------------------------------------------
# Name:        PegelOnline Stations
# Purpose:
#
# Author:      s4beluek
#
# Created:     21.08.2019
#-------------------------------------------------------------------------------

from .urlreader import UrlReader


class PoCurrentW(object):
    """
    """

    def __init__(self):
        pass

    def getData(self):
        """

        Station data has the form
        station = {
            'geometry': (longitude, latitude),
            'attributes': ( uuid,
                            number,
                            shortname,
                            longname,
                            km,
                            agency,
                            water.longname
                          )
            }

        Args:

        Returns:
            stations: List with Dictionary for each station
        """


        reader = UrlReader("stations.json?timeseries=W&includeTimeseries=true&includeCurrentMeasurement=true")
        jsonData = reader.getJsonResponse()

        stations = []

        # process all stations
        for d in jsonData:
            station = {
                'geometry': (
                    d['longitude']  if "longitude" in d else 0 ,
                    d['latitude']   if "latitude" in d else 0
                    ),
                'attributes': ( d['uuid'] if "uuid" in d else 0,
                                d['number'] if "number" in d else 0,
                                d['shortname'] if "shortname" in d else "",
                                d['timeseries'][0]['currentMeasurement']['timestamp'],
                                d['timeseries'][0]['currentMeasurement']['value'],
                                d['timeseries'][0]['currentMeasurement']['trend'],
                                d['timeseries'][0]['currentMeasurement']['stateMnwMhw'],
                                d['timeseries'][0]['currentMeasurement']['stateNswHsw'])
            }

            stations.append(station)

        return stations

