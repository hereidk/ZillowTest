'''
Created on Jul 1, 2014

@author: kahere

Portions of AddressData modified from pyzillow: https://github.com/hanneshapke/pyzillow
'''


import requests
from requests.exceptions import (ConnectionError, TooManyRedirects, 
                                Timeout, HTTPError)
from bs4 import BeautifulSoup
import numpy as np
import sys
import pandas
import tkinter
import tkinter.filedialog as tkFileDialog
import os


class ZipData():
    '''
    Get Zillow data at zip code level
    '''


    def __init__(self, zipcode):
        '''
        Point to demographics data in Zillow API, get data by zip code
        '''
        key = 'X1-ZWz1b5jgur5pu3_aypsc' # Zillow API key
        url = 'http://www.zillow.com/webservice/GetDemographics.htm?zws-id=%s&zip=%s' % (key, zipcode)
        geturl = requests.get(url)
        pageText = geturl.text
        self.soup = BeautifulSoup(pageText,'xml') # Parse text with BeautifulSoup
        
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
        self.key = 'X1-ZWz1b5jgur5pu3_aypsc' # Zillow API key
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
            # Parse text results using BeautifulSoup           
            pageText = request.text
            response = BeautifulSoup(pageText,'xml')
        except:
            print ("Zillow response is not a valid XML")
            sys.exit()

        if not response.find_all('response'):
            # Check if address has been found - print any addresses with no matches
            print ("Zillow returned no results: ", params['address'])
            return

        if len(response.find_all('message/code')) is not 0:
            print ('Error message: ', response.find_all('message/code')[0].text) 
        else:
            return response
    
class AddressList():
    def __init__(self):
        pass
    
    def runAddress(self):    
        # Attributes to collect from Zillow
        column_list = ['street_address','city','state','zipcode','latitude','longitude','property_type','tax_assessment','year_built','lot_size','sq_ft','bedrooms','bathrooms','estimated_mkt_value']
        address_list = self.selectFile()
         
        # Check each record to see if Zillow can find it, add results to address_info dataframe
        address_info = pandas.DataFrame(columns=column_list)
        for row in address_list:
            single_address = row[0][2:-1]+' '+row[1][2:-1]+' '+row[2][2:-1]
            zipcode = row[-1][2:-1]
             
            # Excel removes leading 0, this adds them back
            if len(str(zipcode)) < 5:
                zipcode = str(zipcode).zfill(5)    
             
            get_address = pandas.DataFrame(self.address(single_address,zipcode),columns=column_list)
            address_info = address_info.append(get_address)
     
        # Output address dataframe to .csv file
        address_info.to_csv('address_test.csv',sep=',',index=False)
    
    def selectFile(self):
        # Browse to directory of portfolio file
        root2 = tkinter.Tk()
        root2.withdraw()
        currdir = os.getcwd()
        validfile = False
        while validfile == False: 
            tempdir = tkFileDialog.askopenfilename(parent=root2, initialdir=currdir, title='Please select an address .csv file.')
    
            # Make sure file is correct type
            if tempdir.endswith('.csv'):
                portfolio_file = tempdir
                address_list = np.loadtxt(portfolio_file,delimiter=',',skiprows=1,dtype=str)
                
                # Make sure file is in correct format with expected number of columns
                if not address_list.shape[1] == 4:
                    print ('Text file should have 4 columns: Street address, city, state, postal code. Please try again.')
                else:
                    validfile = True 
            
            # Handle cancel
            elif len(tempdir) == 0:
                validfile = True
                sys.exit()
            
            # If file exists but doesn't end with .csv, is wrong file type
            else:
                print("Error: File type must be .csv.")      
        return address_list         

    
    def address(self, single_address, zipcode):
        # Call AddressData class methods
        address_data = AddressData(single_address, zipcode)
        results = address_data.get_deep_search_results()
        
        # Select desired property attributes from Zillow
        attributes = ['result.address.street.contents',
                      'result.address.city.contents',
                      'result.address.state.contents',
                      'result.address.zipcode.contents',
                      'result.latitude.contents',
                      'result.longitude.contents',
                      'result.useCode.contents',
                      'result.taxAssessment.contents',
                      'result.yearBuilt.contents',
                      'result.lotSizeSqFt.contents',
                      'result.finishedSqFt.contents',
                      'result.bedrooms.contents',
                      'result.bathrooms.contents',
                      'result.zestimate.amount.contents']
        
        def splitAttr(attrstring):
            # Split attribute list, iteratively navigate XML tree
            attrs = attrstring.split('.')
            for i in range(len(attrs)):
                if i == 0:
                    lvl_1 = getattr(results, attrs[i])
                else:
                    lvl_2 = getattr(lvl_1, attrs[i]) 
                    lvl_1 = lvl_2
                    if i == len(attrs) - 1:
                        lvl_1 = lvl_1[0]
            return lvl_1        
        
        if results is not None:
            dataset = [0] * len(attributes)
            count = -1
            
            # Find results for all attributes, add to dataset list
            for item in attributes:
                count += 1
                try:
                    dataset[count] = splitAttr(item)
                except (AttributeError, IndexError):
                    continue            
                
            # Convert dataset to array, reshape output
            dataset = np.array(dataset)
            dataset = dataset.reshape((1,np.shape(dataset)[0]))
            
            return dataset
        
        else:
            return
        
    


    