#-------------------------------------------------------------------------------
# Name:        PegelOnline Stations
# Purpose:
#
# Author:      s4beluek
#
# Created:     21.08.2019
#-------------------------------------------------------------------------------

from .urlreader import UrlReader


class PoStations(object):
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
                            longname
                          )
            }

        Args:

        Returns:
            stations: List with Dictionary for each station
        """


        reader = UrlReader("stations.json")
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
                                d['longname'] if "longname" in d else "",
                                d['km'] if "km" in d else 0.0,
                                d['agency'] if "agency" in d else "",
                                d['water']['longname'] if "water" in d else ""
                              )
            }

            stations.append(station)

        return stations

