'''
Created on Jul 1, 2014

@author: kahere
'''


import requests
from requests.exceptions import (ConnectionError, TooManyRedirects, 
                                Timeout, HTTPError)
from bs4 import BeautifulSoup
import numpy as np
import sys


class ZipData():
    '''
    Get Zillow data at zip code level
    '''


    def __init__(self, zipcode):
        '''
        Point to demographics data in Zillow API, get data by zip code
        '''
        key = 'X1-ZWz1b5jgur5pu3_aypsc'
        url = 'http://www.zillow.com/webservice/GetDemographics.htm?zws-id=%s&zip=%s' % (key, zipcode)
        geturl = requests.get(url)
        pageText = geturl.text
        self.soup = BeautifulSoup(pageText,'xml')        
        
    def returnPrettify(self):
        '''
        Return XML as text to see structure
        '''
        self.soup.prettify()
        return self.soup.prettify()

    def returnState(self):
        '''
        Return the state of the given zip code
        '''
        return self.soup.state.contents[0]
    
    def returnHomeValues(self):
        '''
        Get home values at the zip code level, compile into list
        '''
        zhvi = np.int(self.soup.find(text='Zillow Home Value Index').next_element.find('value', type='USD').contents[0])
        median_sfh = np.int(self.soup.find(text='Median Single Family Home Value').next_element.find('value', type='USD').contents[0])
        median_condo = np.int(self.soup.find_all(text='Median Condo Value')[1].next_element.find('value', type='USD').contents[0])
        median_2bd = np.int(self.soup.find(text='Median 2-Bedroom Home Value').next_element.find('value', type='USD').contents[0])
        median_3bd = np.int(self.soup.find(text='Median 3-Bedroom Home Value').next_element.find('value', type='USD').contents[0])
        median_4bd = np.int(self.soup.find(text='Median 4-Bedroom Home Value').next_element.find('value', type='USD').contents[0])
        median_valuesqft = np.int(self.soup.find(text='Median Value Per Sq Ft').next_element.find('value', type='USD').contents[0])

#         get_values = {'Zillow_Home_Value_Index':zhvi, 'Median_Single_Family':median_sfh, 'Median_Condo':median_condo, 'Median_2bd':median_2bd, 'Median_3bd':median_3bd, 'Median_4bd':median_4bd, 'Median_PerSqFt':median_valuesqft}
        get_values = [zhvi, median_sfh, median_condo, median_2bd, median_3bd, median_4bd, median_valuesqft]
        
        return get_values
    
    
class AddressData():
    '''
    Get Zillow data at the address level
    '''
    
    
    def __init__(self, address, zipcode):
        self.key = 'X1-ZWz1b5jgur5pu3_aypsc'
        self.address = address
        self.zipcode = zipcode
    
    
    def get_deep_search_results(self):
        """
        GetDeepSearchResults API
        """

        url = 'http://www.zillow.com/webservice/GetDeepSearchResults.htm'
        params = {
            'address': self.address,
            'citystatezip': self.zipcode,
            'zws-id': self.key 
            }
        return self.get_data(url, params)
    
    def get_data(self, url, params):
        """
        """

        try:
            request = requests.get(
                url = url,
                params = params)
        except (ConnectionError, TooManyRedirects, Timeout):
            print('Connection Error')
            sys.exit()

        try:
            request.raise_for_status()
        except HTTPError:
            print ('HTTP Error')
            sys.exit()

        try:            
            pageText = request.text
            response = BeautifulSoup(pageText,'xml')
        except:
            print ("Zillow response is not a valid XML")
            sys.exit()

        if not response.find_all('response'):
            print ("Zillow returned no results: ", params['address'])
            return

        if len(response.find_all('message/code')) is not 0:
            print ('Error message: ', response.find_all('message/code')[0].text) 
        else:
            return response
    