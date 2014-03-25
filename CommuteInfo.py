'''
Module provides access to weather.gov data directly via functions & class 
methods
Date: 140319
Author: Paul Garaud
'''



from suds.client import Client  # main class for interacting w/API
import logging
from suds.cache import DocumentCache
from suds.sax.element import Element
from suds import WebFault  # to distinguish b/w server & client errors
import lxml

# log errors
logging.basicConfig(level=logging.INFO)
# debug specific modules
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
logging.getLogger('suds.xsd.schema').setLevel(logging.DEBUG)

# description of Weather.gov api
#print api

# get geo coords for a particular zip code (extends to list of zip codes)
#geoCoords = api.service.LatLonListZipCode('11776')
## parse xml
#root = lxml.etree.fromstring(geoCoords)
#coordStr = root.find('latLonList').text
#coord = coordStr.split(',')

# get weather data
#weatherData = api.service.NDFDgen(latitude=coord[0],
#                                 longitude=coord[1],
#                                 product='glance')

# write to file to examine in NPP
#tmp = open('weatherData.txt', 'w')
#tmp.write(weatherData)
#tmp.close()

# to do: write functions to extract data (check out time series as well)

class LocationForecast(object):
    '''
    Defines a location object that has methods for returning forecast
    data
    Takes a zip code (str), api (suds.Client), & forecastType as an input
    '''
    def __init__(self, zipcode, api, forecastType='glance'):
        self.zip = zipcode
        self.client = api
        self.geoLoc = self.get_coords(self.zip)
        self.forecast = forecastType  # 'glance' or 'time-series'
        self.document = self.client.service.NDFDgen(latitude=self.geoLoc[0],
                                            longitude=self.geoLoc[1],
                                            product=self.forecast)
        self.root = lxml.etree.fromstring(self.document)
        self.xPathDict = self.gen_xPathDict(self.root, '//layout-key')
        self.periodDict = self.get_periods(self.xPathDict)
        
    def get_zip(self):
        return self.zip
        
    def get_client(self):
        return self.client

    def get_coords(self, zipcode):
        coordStr = self.client.service.LatLonListZipCode(self.zip)
        root = lxml.etree.fromstring(coordStr)
        coord = root.find('latLonList').text.split(',')
        return [float(i) for i in coord]
    
    def get_tree(self):
        return self.root
    
    def get_location(self):
        return self.geoLoc
    
    def get_xml_data(self):
        return self.document    
    
    def gen_xPathDict(self, tree, query):
        xmlPdNames = [i.text for i in tree.xpath(query)]
        return {i: j for i, j in zip(['days','nights','3hr','1hr'],xmlPdNames)}
    
    def get_periods(self, xPathDict):
        '''
        builds dict of lists of periods
        '''
        periodDict = {}
        for period in xPathDict.keys():
            periodDict[period] = extractPeriods(period, self.root,
                                                self.xPathDict)
        return periodDict
    
    def get_daily_temps(self, weathXML):
        pass
    
    def get_cloud_cover(self):
        pass

# [i.text for i in a.xpath('//name')]
# use xpath functionality to select relevant nodes
# for above functions

def periodQuery(period, xPathDict):
    return ("//time-layout[layout-key = '" + xPathDict[period] +
            "']/start-valid-time")

def extractPeriods(period, tree, xPathDict, childName='start-valid-time'):
    '''
    inputs: time increment, xml tree, dict obj with map of period names 
    to elements, childName for querying relevant element children
    '''
    periods, elmnts = [], []
    elmnts = tree.xpath(periodQuery(period, xPathDict))
#    periods = elmnts[0].xpath('//' + childName)
    return [i.text for i in elmnts]

if __name__ == '__main__':
    
    api = Client('http://graphical.weather.gov/xml/DWMLgen/wsdl/ndfdXML.wsdl')
    zipCode = '11776'    
    portJeff = LocationForecast(zipCode, api)
    
    
    
    













