
# coding: utf-8

# In[1]:


import geojson
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# In[2]:
with open("data/milano-grid.geojson") as json_file:
    grid_json = geojson.load(json_file)
# In[3]:
with open("data/Italian_provinces.geojson") as json_file:
    provinces_json = geojson.load(json_file)
# In[3]:
# from https://github.com/johan/world.geo.json/blob/master/countries.geo.json
with open("data/countries.geojson") as json_file:
    countries_json = geojson.load(json_file)
# In[4]:


start_day = 1
end_day   = 1 + 1


# In[ ]:


# Milan to provinces
m2p_df = []
for day in range(start_day, end_day):
    m2p_df.append(pd.read_csv("data/mi-to-provinces-2013-11-{:02}.csv".format(day), engine ="python", index_col=0))
    
m2p_df = pd.concat(m2p_df)


# In[ ]:


time_indices = pd.concat([pd.DataFrame(np.repeat(m2p_df.index.drop_duplicates().values, 10000), columns=['datetime'])]).reset_index(drop=True)
cell_indices = pd.concat([pd.DataFrame(np.arange(10000), columns=['CellID'])] * 24).reset_index(drop=True)


# In[ ]:


#new_m2p_df = pd.concat([time_indices, cell_indices], axis=1)
#new_m2p_df = new_m2p_df.set_index('datetime')
#
## for index, row in m2p_df.iterrows():
##     new_m2p_df.loc[index].loc['CellID']
#
#new_m2p_df.loc[index].loc['CellID']


# In[ ]:


# Milan to countries
m2c_df = []
for day in range(start_day, end_day):
    m2c_df.append(pd.read_csv("data/sms-call-internet-mi-2013-11-{:02}.csv".format(day), engine ="python", index_col=0))
        
m2c_df = pd.concat(m2c_df)

# In[ ]:
import pycountry
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE
from collections import Counter

country_codes = dict(Counter(m2c_df['countrycode']))

calls_per_country = {}
for country_code, n_calls in country_codes.items():
    
    if country_code == 0:
        if 'Italy' not in calls_per_country:
            calls_per_country['Italy'] = n_calls
        else:
            calls_per_country['Italy'] += n_calls
    else:
        try:
            region_codes = COUNTRY_CODE_TO_REGION_CODE[country_code]
            countries = ''
            for region_code in region_codes:
                country_name = pycountry.countries.get(alpha_2=region_code).name
                countries += country_name + ', '
                
                if country_name == 'Italy':
                    if 'Italy' not in calls_per_country:
                        calls_per_country['Italy'] = n_calls
                    else:
                        calls_per_country['Italy'] += n_calls
                else:        
                    calls_per_country[country_name] = n_calls
                    
            countries = countries[:-2] # Remove the last comma
        except:
            pass

# In[ ]:


#len(set(m2c_df['countrycode']))
#
#
## In[ ]:
#
#
#df = pd.merge(m2p_df, m2c_df, on=['CellID'])
#
#
## In[ ]:
#
#
#df


# In[ ]:

from bokeh.io import show
from bokeh.models import (
    ColumnDataSource,
    HoverTool,
    LogColorMapper
)
from bokeh.palettes import Viridis256 as palette
from bokeh.plotting import figure
from bokeh.layouts import column


color_mapper = LogColorMapper(palette=palette)
TOOLS = "pan,wheel_zoom,reset,hover,save"

# In[ ]:
plots = []
for day in range(3,4):
    
    # Load data
    all_data = pd.read_csv("data/mi-to-provinces-2013-11-{:02}.csv".format(day), engine ="python", index_col=0)
    
    for hour in range(0, 8):
        data = all_data.loc['2013-11-{:02} {:02}:00:00'.format(day, hour)]

        calls_per_cell = data['CellID'].values
        calls_per_cell = Counter(calls_per_cell)
        print(day, hour, calls_per_cell.most_common(5))
        calls_per_cell = dict(calls_per_cell)
        
        for key, value in calls_per_cell.items():
            calls_per_cell[key] = value/100
            
        lon = [[coors[0] for coors in cell["geometry"]["coordinates"][0]] for cell in grid_json['features']]
        lat = [[coors[1] for coors in cell["geometry"]["coordinates"][0]] for cell in grid_json['features']]
        names = [cell["id"] for cell in grid_json['features']]
        calls = [calls_per_cell[cell["id"]+1] if cell["id"]+1 in calls_per_cell else 0 for cell in grid_json['features']]
        calls[0] = 0.0
        calls[-1] = 1.0

    #     def print_stats(x, y):
    #         x = np.asarray(x)
    #         y = np.asarray(y)
    #         print(y.max(), x.max())
    #         print(y.min(), x.min())
    #         print((y.min() + y.max()) / 2,  (x.min() + x.max()) / 2)
    #     print_stats(lon, lat)

        source = ColumnDataSource(data=dict(
            lon=lon,
            lat=lat,
            names=names,
            calls=calls,
            center_lon=[np.mean(x) for x in lon],
            center_lat=[np.mean(x) for x in lat],
        ))

        p = figure(
            title="Italian Provinces by Number of Calls with Milan", tools=TOOLS,
            x_axis_location=None, y_axis_location=None
        )
        p.grid.grid_line_color = None

        p.patches('lon', 'lat', source=source,
                  fill_color={'field': 'calls', 'transform': color_mapper},
                  fill_alpha=0.7, line_color="white", line_width=0.5)

        hover = p.select_one(HoverTool)
        hover.point_policy = "follow_mouse"
        hover.tooltips = [
            ("Name", "@names"),
            ("Calls)", "@calls"),
            ("(Lat, Lon)", "(@center_lat, @center_lon)"),
        ]
        plots.append(p)


# In[ ]:


show(column(*plots))



# In[ ]:


data = pd.read_csv("data/mi-to-provinces-2013-11-{:02}.csv".format(day), engine ="python", index_col=0)

calls_per_province = data['provinceName'].values
calls_per_province = Counter(calls_per_province)

print(calls_per_province.most_common(5))

calls_per_province = dict(calls_per_province)

for province in provinces_json['features']:
    province = province["properties"]["PROVINCIA"].upper()
    if province not in calls_per_province:
        
        def replace_key(new_key, old_key):
            calls_per_province[new_key] = calls_per_province[old_key]
            del calls_per_province[old_key]
            
        replace_key("AOSTA", "VALLE D'AOSTA")
        replace_key("BOLZANO", "BOLZANO/BOZEN")
        replace_key("MASSA CARRARA", "MASSA-CARRARA")
        
        if province not in calls_per_province:
            raise ValueError('{} is not in province list!'.format(province))

lon = [[coors[0] for coors in province["geometry"]["coordinates"][0][0]] for province in provinces_json['features']]
lat = [[coors[1] for coors in province["geometry"]["coordinates"][0][0]] for province in provinces_json['features']]
names = [province["properties"]["PROVINCIA"] for province in provinces_json['features']]
calls = [calls_per_province[province["properties"]["PROVINCIA"].upper()] for province in provinces_json['features']]

source = ColumnDataSource(data=dict(
    lon=lon,
    lat=lat,
    names=names,
    calls=calls,
    center_lon=[np.mean(x) for x in lon],
    center_lat=[np.mean(x) for x in lat],
))

p = figure(
    title="Italian Provinces by Number of Calls with Milan", tools=TOOLS,
    x_axis_location=None, y_axis_location=None
)
p.grid.grid_line_color = None

p.patches('lon', 'lat', source=source,
          fill_color={'field': 'calls', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.5)

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("Name", "@names"),
    ("Calls)", "@calls"),
    ("(Lat, Lon)", "(@center_lat, @center_lon)"),
]

show(p)

# In[ ]:

lon = []
lat = []
names = []
calls = []
for country in countries_json['features']:  
    
    
    if country["id"] == '-99': # Norther Cyprus
        country["id"] = "CYP"
    elif country["id"] == 'CS-KM': # Kosovo
        country["id"] = "SRB"
    name = pycountry.countries.get(alpha_3=country["id"]).name
    
    if name not in calls_per_country:
        continue
    
    geometry = country["geometry"]
    if geometry['type'] == 'Polygon':
        country_borders = [geometry["coordinates"][0]]
        
    elif geometry['type'] == 'MultiPolygon':
        country_borders = []
        for polygon in geometry["coordinates"]:
            country_borders += polygon
    else:
        raise ValueError('Unknown type of geojson')
        
    for polygon in country_borders:
        lon.append([])
        lat.append([])
        print(country["id"], country['properties']['name'])
        names.append(name)
        calls.append(calls_per_country[name])
        for coors in polygon:
            lon[-1].append(coors[0])
            lat[-1].append(coors[1])

#names = [country["properties"]["name"] for country in countries_json['features']]
#calls = [0 for country in countries_json['features']]

source = ColumnDataSource(data=dict(
    lon=lon,
    lat=lat,
    names=names,
    calls=calls,
    center_lon=[np.mean(x) for x in lon],
    center_lat=[np.mean(x) for x in lat],
))

p = figure(
    title="Countries by Number of Calls with Milan", tools=TOOLS,
    x_axis_location=None, y_axis_location=None,
    plot_width=1500, plot_height=600
)
p.grid.grid_line_color = None

p.patches('lon', 'lat', source=source,
          fill_color={'field': 'calls', 'transform': color_mapper},
          fill_alpha=0.7, line_color="white", line_width=0.5)

hover = p.select_one(HoverTool)
hover.point_policy = "follow_mouse"
hover.tooltips = [
    ("Name", "@names"),
    ("Calls)", "@calls"),
    ("(Lat, Lon)", "(@center_lat, @center_lon)"),
]

show(p)

