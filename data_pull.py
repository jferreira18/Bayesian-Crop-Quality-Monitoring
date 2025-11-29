import requests
import pandas as pd

########### Crop Data

def crop_pull():
        
    key = '3C7B7C44-4D80-3975-AF68-2423CD934AA5'

    url = "https://quickstats.nass.usda.gov/api/api_GET/"

    params = {
        "key": key,
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "commodity_desc": "HAY",
        "statisticcat_desc": "CONDITION",
        "agg_level_desc": "STATE",
        "state_alpha": "RI",
        "freq_desc": "WEEKLY",
        "year__GE": "2015"
    }

    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()["data"]   

    df = pd.DataFrame(data)

    data = df.drop(columns = ['county_code', 'country_code', 'watershed_code', 'statisticcat_desc',
        'domaincat_desc', 'load_time', 'commodity_desc', 'source_desc',
        'short_desc', 'region_desc', 'prodn_practice_desc', 'year', 'CV (%)',
        'location_desc', 'county_ansi', 'asd_code', 'sector_desc',
        'state_fips_code', 'end_code', 'zip_5', 'reference_period_desc',
        'begin_code', 'state_ansi', 'domain_desc',
        'agg_level_desc', 'group_desc', 'congr_district_code', 'watershed_desc',
        'util_practice_desc', 'asd_desc', 'state_alpha', 'class_desc',
        'state_name', 'freq_desc', 'country_name', 'county_name'])

    data['week_ending'] = pd.to_datetime(data['week_ending'])

    data['date'] = data['week_ending']
    data['quality'] = data['unit_desc']
    data['Value'] = pd.to_numeric(data['Value'])
    data.drop(columns = ['week_ending', 'unit_desc'], inplace=True)

    crop_data = data.pivot_table(index='date', columns='quality', values='Value', aggfunc='mean').reset_index()
    
    return crop_data

def crop_yield():
    key = '3C7B7C44-4D80-3975-AF68-2423CD934AA5'

    url = "https://quickstats.nass.usda.gov/api/api_GET/"

    params = {
        "key": key,
        "source_desc": "SURVEY",
        "sector_desc": "CROPS",
        "commodity_desc": "HAY",
        "statisticcat_desc": "YIELD",
        "agg_level_desc": "STATE",
        "state_alpha": "RI",
        "freq_desc": "WEEKLY",
        "year__GE": "2015"
    }
    
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json()["data"]   

    df = pd.DataFrame(data)
    
    print(df)
    print(df.columns)

    data = df.drop(columns = ['county_code', 'country_code', 'watershed_code', 'statisticcat_desc',
        'domaincat_desc', 'load_time', 'commodity_desc', 'source_desc',
        'short_desc', 'region_desc', 'prodn_practice_desc', 'year', 'CV (%)',
        'location_desc', 'county_ansi', 'asd_code', 'sector_desc',
        'state_fips_code', 'end_code', 'zip_5', 'reference_period_desc',
        'begin_code', 'state_ansi', 'domain_desc',
        'agg_level_desc', 'group_desc', 'congr_district_code', 'watershed_desc',
        'util_practice_desc', 'asd_desc', 'state_alpha', 'class_desc',
        'state_name', 'freq_desc', 'country_name', 'county_name'])

    data['week_ending'] = pd.to_datetime(data['week_ending'])

    data['date'] = data['week_ending']
    data['quality'] = data['unit_desc']
    data['Value'] = pd.to_numeric(data['Value'])
    data.drop(columns = ['week_ending', 'unit_desc'], inplace=True)

    crop_data = data.pivot_table(index='date', columns='quality', values='Value', aggfunc='mean').reset_index()
    


########## Weather Data

def weather_pull():
        
    key = 'KmmwiCbiXtqCkSHgXDaoiZPvLIQUwrwT'

    url = 'https://www.ncei.noaa.gov/cdo-web/api/v2/data'

    headers = {'token': key}

    params = {
        "datasetid": "GSOM",
        "stationid": "GHCND:USW00014765", ###this is PVD, RI
        "datatypeid": ['TAVG', 'PRCP', 'SNOW', 'AWND', 'EMXT', 'EMNT', 'CLDD', 'HTDD'],
        "startdate": "2015-01-01",
        "enddate": "2024-12-31",
        "limit": 1000, ###will return max of 1000 rows regardless of date range
        "units": "standard",
    }

    r = requests.get(url=url, params=params, headers=headers).json()

    data = pd.DataFrame(r['results'])

    weather_data = data.drop(['station','attributes'], axis =1)
    weather_data['date'] = pd.to_datetime(weather_data['date'])
    weather_data = weather_data.pivot(index='date', columns='datatype', values='value')
    
    return weather_data

########### Align Both

def align_data(crop_data, weather_data):

    crop_data['date'] = pd.to_datetime(crop_data['date'])
    crop_data['date'] = crop_data['date'].dt.to_period('M').dt.to_timestamp()

    crop_data = crop_data.groupby('date').mean()

    crop_data.index = pd.to_datetime(crop_data.index)
    
    weather_data.index = pd.to_datetime(weather_data.index)

    idx = crop_data.index.intersection(weather_data.index)

    cd = crop_data.loc[idx]
    wd = weather_data.loc[idx]

    #print('cd', cd)
    #print(cd.shape[0])
    #print('wd',wd)

    cd.to_csv('crop_data.csv')
    wd.to_csv('weather_data.csv')
    
if __name__ == '__main__':
    weather = weather_pull()
    crop = crop_pull()
    align_data(crop_data=crop, weather_data=weather)
    #crop_yield()
    