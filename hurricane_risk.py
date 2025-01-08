import tropycal.tracks as tracks
import datetime as dt
import pandas as pd
import math
import sys


basin = tracks.TrackDataset(basin='north_atlantic',source='hurdat',include_btk=False)
cities = pd.read_csv('Major_Gulf_cities.csv')

def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert latitude and longitude from degrees to radians 
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1) 
    lat2_rad = math.radians(lat2) 
    lon2_rad = math.radians(lon2) 
    # Compute the differences 
    dlat = lat2_rad - lat1_rad 
    dlon = lon2_rad - lon1_rad 
    # Apply the haversine formula 
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2 
    c = 2 * math.asin(math.sqrt(a)) 
    # Radius of the Earth in kilometers (mean radius) 
    R = 6371.009 
    distance = R * c
    
    return distance

years = {1998,1999,2000,2001,2002,2003,2004,2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,2020,2021,2022,2023}
distance = 0
mindistance = 0 

cityname = sys.argv[1]

result = cities[cities['City Name'] == cityname]

latitude = float(result['Latitude'].iloc[0])
longitude = float(result['Longitude'].iloc[0])



StormDistances = pd.DataFrame()

print('Calculating distance of all hurricanes in the last 25 years, this may take several minutes...')
for year in years:
    season = basin.get_season(year)
    df = season.to_dataframe()
    for index, row in df.iterrows():
        storm = basin.get_storm(row['id'])
        storm = storm.to_dataframe()
        
        if row['category'] > 0:
            for index1, row1 in storm.iterrows():
                stormlat = float(row1['lat'])
                stormlon = float(row1['lon'])
                #calculate euclidean distance: ((latitude-stormlat)**2+(longitude-stormlon)**2)**0.5
                distance = haversine_distance(latitude, longitude, stormlat, stormlon)
                if index1 == 0:
                    mindistance = distance
                elif distance <= mindistance:
                    mindistance = distance
            gauss = (2.71828)**(-(mindistance ** 2) / (2*(160**2)))
            
            
            new_row = {'Storm': row['name'], 'Distance': mindistance, 'Category' : row['category'], 'Density' : gauss}
            rows = []
            rows.append(new_row)
            StormDistances = pd.concat([StormDistances, pd.DataFrame(rows)], ignore_index=True)

print('Getting final average.....')

sumcat = 0
weightedsum = 0

for index, row in StormDistances.iterrows():
    if row['Distance'] <= 80:
        weightedsum += (row['Category'] * row['Density'])
        sumcat += row['Category']

print('Final Risk Percentage of',cityname,':',weightedsum / sumcat)