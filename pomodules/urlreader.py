#-------------------------------------------------------------------------------
# Name:        URL Reader
# Purpose:     Class to get and Parse data for PegelOnline Plugin
#
# Author:      s4beluek
#
# Created:     21.08.2019
#-------------------------------------------------------------------------------

import json
import os
import urllib.request
import gzip
from urllib.parse import urljoin

class UrlReader(object):
    """Fetches and returns data from the PegelOnline Server in different formats
    """

    def __init__(self):
        pass


    def openUrl(self):
        """Creates and executes HTTP-request

        Args:
            None
        Returns:
            response of the HTTP-request as gzip
        Raises:
            URLError: An error occured when the URL cant be reached
            HTTPError: An error occured during the communication
        """

        url = urljoin("https://www.pegelonline.wsv.de/webservices/rest-api/v2/", "stations.json")
        req = urllib.request.Request(url)
        req.add_header('Accept-Encoding', 'gzip')

        try:
            return urllib.request.urlopen(req)

        except urllib.error.URLError as e:
            print(e.reason)
        except urllib.error.HTTPError as e:
            print(e.code)


    def getDataResponse(self):
        """Unzips and returns data received from openUrl if present

        Args:
            None
        Returns:
            data: Raw unzipped data
        """
        response = self.openUrl()

        if not (response is None and response.headers['Content-Encoding'] == 'gzip') :
            data = gzip.GzipFile(fileobj=response).read()
            return data
        else:
            return None


    def getJsonResponse(self):
        """Creates and returns data from PegelOnline as JSON

        Args:
            None
        Returns:
            data: Data received from getDataResponse() as JSON
        """
        data = self.getDataResponse()

        if not (data is None):
            data = json.loads(data)
            return data
        else:
            return None


    def getFileResponse(self):
        """Saves the fetched data from PegelOnline as json file 'stations.json'

        Args:
            None
        Returns:
            None
        """
        data = self.getDataResponse()

        if not (data is None):
            with open ("stations.json", "wb") as f:
                f.write(data)

    def getDataTable(jsdata, columns):
        """Creates a list of values with specific columns

        Args:
            jsdata: Data to be parsed as a table
            columns: Dictionary keys
        Returns:
            table: List of Dictionaries
        """

        pass

