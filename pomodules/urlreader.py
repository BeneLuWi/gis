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
from . import BASE_URL

class UrlReader(object):
    """Fetches and returns data from the PegelOnline Server in different formats
    """

    def __init__(self, url):
        self.url = str(url)

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
        reqUrl = urljoin(BASE_URL, self.url)
        req = urllib.request.Request(reqUrl)
        req.add_header('Accept-Encoding', 'gzip')

        try:
            request = urllib.request.urlopen(req)
        except urllib.error.URLError as e:
            print(e.reason)
        except urllib.error.HTTPError as e:
            print(e.code)
        else:
            return request

    def getDataResponse(self):
        """Unzips and returns data received from openUrl if present

        Args:
            None
        Returns:
            data: Raw unzipped data
        """
        response = self.openUrl()

        if response is None:
            return

        if (response.headers['Content-Encoding'] == 'gzip') :
            data = gzip.GzipFile(fileobj=response).read()
            print("Loaded")
            return data

        return response.read()


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
