'''
Created on Jul 1, 2014

@author: kahere
'''

from root.nested.ZillowZip import ZipData, AddressData
import pandas
import numpy as np
import tkinter
import tkinter.filedialog as tkFileDialog
import os
import sys

def zips():
    # Get list of zip codes from csv file
    zip_list = pandas.DataFrame().from_csv(r'C:\Python code\ZillowTest\src\root\nested\zip_code_database.csv')
    
    # Select state to test
    zips = zip_list[zip_list.state=='FL'].index
    print (zips)
    zips = zips[:5]
    
    home_values = pandas.DataFrame(index=zips,columns=['Zillow_Home_Value_Index','Median_Single_Family','Median_Condo','Median_2bd','Median_3bd','Median_4bd','Median_PerSqFt','State'])
    for i in zips:
        # Loop through zip code list, extracting home value data at each zip code
        getzip = ZipData(i)
        
        try:
            get_values = getzip.returnHomeValues()
            home_values.ix[i,:-1] = get_values
            home_values.ix[i,-1] = getzip.returnState()
        except AttributeError:
            print (i)
            continue
                
    print (home_values)
    
def address(address, test_zipcode):
    # Call AddressData class methods
    address_data = AddressData(address, test_zipcode)
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

def selectFile():
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
            validfile = True
        elif len(tempdir) == 0:
            validfile = True
            sys.exit()
        else:
            print("Error: File type must be .csv.")      
    return portfolio_file             

if __name__ == '__main__':    
    
#     zips()

    validfile = False
    while validfile == False:
        file_name = selectFile()
        # Load text file
        address_list = np.loadtxt(file_name,delimiter=',',skiprows=1,dtype=str)
        if not address_list.shape[1] == 4:
            print ('Text file should have 4 columns: Street address, city, state, postal code. Please try again.')
        elif len(file_name) == 0:
            validfile = True
            sys.exit()
        else:
            validfile = True 
    
    # Attributes to collect from Zillow
    column_list = columns=['street_address','city','state','zipcode','latitude','longitude','property_type','tax_assessment','year_built','lot_size','sq_ft','bedrooms','bathrooms','estimated_mkt_value']
    
    
    
    # Check each record to see if Zillow can find it, add results to address_info dataframe
    address_info = pandas.DataFrame(columns=column_list)
    for row in address_list:
        single_address = row[0][2:-1]+' '+row[1][2:-1]+' '+row[2][2:-1]
        zipcode = row[-1][2:-1]
        
        # Excel removes leading 0, this adds them back
        if len(str(zipcode)) < 5:
            zipcode = str(zipcode).zfill(5)    
        
        get_address = pandas.DataFrame(address(single_address,zipcode),columns=column_list)
        address_info = address_info.append(get_address)

    # Output address dataframe to .csv file
    address_info.to_csv('address_test.csv',sep=',',index=False)
        
