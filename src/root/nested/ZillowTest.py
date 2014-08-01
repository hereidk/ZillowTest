'''
Created on Jul 1, 2014

@author: kahere
'''

from ZillowZip import ZipData, AddressList  # @UnresolvedImport
import pandas

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
    

if __name__ == '__main__':    
    
#     zips()

    address_list = AddressList()
    address_list.runAddress()
        
