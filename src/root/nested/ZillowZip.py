'''
Created on Jul 1, 2014

@author: kahere
'''


import requests
from bs4 import BeautifulSoup
import numpy as np


class ZipData():
    '''
    Get Zillow data at zip code level
    '''


    def __init__(self, zip):
        '''
        Point to demographics data in Zillow API, get data by zip code
        '''
        key = 'X1-ZWz1b5jgur5pu3_aypsc'
        url = 'http://www.zillow.com/webservice/GetDemographics.htm?zws-id=%s&zip=%s' % (key, zip)
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
    
    
    