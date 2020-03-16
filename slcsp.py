import numpy as np
import pandas as pd

def main():
    #import the data
    zips    = pd.read_csv('zips.csv')
    plans   = pd.read_csv('plans.csv')
    request = pd.read_csv('slcsp.csv')
    
    #select only Silver plans
    silver_filter = (plans['metal_level'] == 'Silver')
    silver_plans  = plans.loc[silver_filter, ['state','rate_area','rate']].drop_duplicates()
    
    silver_plans.sort_values(by=['state','rate_area','rate'],ascending=[True,True,False],inplace=True)
    silver_plans.set_index('state', inplace=True)
    
    #create a dictionary with the slcsp for each available area if it exists
    area_groups = silver_plans.groupby(['state','rate_area'])
    area_slcsp  = dict()
    for (state,area_idx),area_group in area_groups:
        area_group = area_group.groupby('rate_area')
        for number,area_rates in area_group:
            area_name = state+str(area_idx)
            if area_rates.shape[0] == 1:
                #print(f'{area_name} has no SLCSP')
                continue
            else:
                slcsp = round(area_rates.iloc[1],2)
                area_slcsp[area_name] = slcsp['rate']
      
    #assign slcsp's to the requested group of zipcodes, if applicable
    code_areas = zips[['zipcode','state','rate_area']].drop_duplicates().set_index('zipcode')
    for idx,code in enumerate(request['zipcode']):
        if len(code_areas.loc[code].shape) != 1:
            #print(f'{code} belongs to more than one rate_area')
            continue
        else:
            area_str = str(code_areas.loc[code]['state'])+str(code_areas.loc[code]['rate_area'])
            try:
                request.loc[idx,'rate'] = area_slcsp[area_str]
            except:
                #print(f'Zip code {code}: there is no rate info available its area {area_str}')
                continue
    
    #save dataframe           
    request.to_csv('slcsp_assigned.csv', index=False)

if __name__ == "__main__":   
    main()