
# coding: utf-8

# In[1]:


import config
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
end_day   = 8


# In[ ]:
# Milan to Provinces
m2p_df = []
for day in range(start_day, end_day):
    m2p_df.append(pd.read_csv("data/mi-to-provinces-2013-11-{:02}.csv".format(day), engine ="python", index_col=0))
    
m2p_df = pd.concat(m2p_df)

# In[ ]:
# Milan to Countries
m2c_df = []
for day in range(start_day, end_day):
    m2c_df.append(pd.read_csv("data/sms-call-internet-mi-2013-11-{:02}.csv".format(day), engine ="python", index_col=0))
        
m2c_df = pd.concat(m2c_df)


# In[ ]:
import pycountry
from phonenumbers import COUNTRY_CODE_TO_REGION_CODE

provinces = sorted(list(set(m2p_df['provinceName'])))

countries = []
country_codes = set(m2c_df['countrycode'])
for country_code in country_codes:
    
    summed_up_data = m2c_df.loc[m2c_df['countrycode'] == country_code].sum()
    
    if country_code == 0:
        countries.append('Italy')
    else:
        try:
            region_codes = COUNTRY_CODE_TO_REGION_CODE[country_code]
            for region_code in region_codes:
                country_name = pycountry.countries.get(alpha_2=region_code).name
#                if n_calls > 1000:
                countries.append(country_name)
                print(country_name, summed_up_data.T)
        except KeyError:
            pass
countries = sorted(countries)
                
# In[]:
province_columns = list(m2p_df.columns[2:])
country_columns  = list(m2c_df.columns[2:])

column_names = []
for column in province_columns:
    for province in provinces:
        column_names.append('{}_{}'.format(column, province))
        
for column in country_columns:
    for country in countries:
        column_names.append('{}_{}'.format(column, country))
        
        # In[]:
n_cells     = 1000
n_hours     = 24

# In[ ]:
time_indices = pd.concat([pd.DataFrame(np.repeat(m2p_df.index.drop_duplicates().values, n_cells), columns=['datetime'])]).reset_index(drop=True)
cell_indices = pd.concat([pd.DataFrame(np.arange(n_cells), columns=['CellID'])] * n_hours).reset_index(drop=True)
columns = pd.DataFrame(np.zeros((n_hours*n_cells, len(column_names))), columns=column_names)

# In[ ]:

df = pd.concat([time_indices, cell_indices, columns], axis=1)
df = df.set_index('datetime')

# In[ ]:
for row in m2c_df.iterrows():
    print(row)

# In[ ]:
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


## In[ ]:
#
#from bokeh.io import show
#from bokeh.models import (
#    ColumnDataSource,
#    HoverTool,
#    LogColorMapper
#)
#from bokeh.palettes import Viridis256 as palette
#from bokeh.plotting import figure
#from bokeh.layouts import column
#
#
#color_mapper = LogColorMapper(palette=palette)
#TOOLS = "pan,wheel_zoom,reset,hover,save"
#
## In[ ]:
#plots = []
#for day in range(3,4):
#    
#    # Load data
#    all_data = pd.read_csv("data/mi-to-provinces-2013-11-{:02}.csv".format(day), engine ="python", index_col=0)
#    
#    for hour in range(0, 8):
#        data = all_data.loc['2013-11-{:02} {:02}:00:00'.format(day, hour)]
#
#        calls_per_cell = data['CellID'].values
#        calls_per_cell = Counter(calls_per_cell)
#        print(day, hour, calls_per_cell.most_common(5))
#        calls_per_cell = dict(calls_per_cell)
#        
#        for key, value in calls_per_cell.items():
#            calls_per_cell[key] = value/100
#            
#        lon = [[coors[0] for coors in cell["geometry"]["coordinates"][0]] for cell in grid_json['features']]
#        lat = [[coors[1] for coors in cell["geometry"]["coordinates"][0]] for cell in grid_json['features']]
#        names = [cell["id"] for cell in grid_json['features']]
#        calls = [calls_per_cell[cell["id"]+1] if cell["id"]+1 in calls_per_cell else 0 for cell in grid_json['features']]
#        calls[0] = 0.0
#        calls[-1] = 1.0
#
#    #     def print_stats(x, y):
#    #         x = np.asarray(x)
#    #         y = np.asarray(y)
#    #         print(y.max(), x.max())
#    #         print(y.min(), x.min())
#    #         print((y.min() + y.max()) / 2,  (x.min() + x.max()) / 2)
#    #     print_stats(lon, lat)
#
#        source = ColumnDataSource(data=dict(
#            lon=lon,
#            lat=lat,
#            names=names,
#            calls=calls,
#            center_lon=[np.mean(x) for x in lon],
#            center_lat=[np.mean(x) for x in lat],
#        ))
#
#        p = figure(
#            title="Italian Provinces by Number of Calls with Milan", tools=TOOLS,
#            x_axis_location=None, y_axis_location=None
#        )
#        p.grid.grid_line_color = None
#
#        p.patches('lon', 'lat', source=source,
#                  fill_color={'field': 'calls', 'transform': color_mapper},
#                  fill_alpha=0.7, line_color="white", line_width=0.5)
#
#        hover = p.select_one(HoverTool)
#        hover.point_policy = "follow_mouse"
#        hover.tooltips = [
#            ("Name", "@names"),
#            ("Calls)", "@calls"),
#            ("(Lat, Lon)", "(@center_lat, @center_lon)"),
#        ]
#        plots.append(p)
#
#
## In[ ]:
#
#show(column(*plots))
## In[ ]:
#
#    
#        
#from bokeh.io import output_file, show
#from bokeh.models import (
#  GMapPlot, GMapOptions, ColumnDataSource, Patches, Range1d, PanTool, WheelZoomTool, BoxSelectTool
#)
#from bokeh.palettes import Greys256
#gmap_color_mapper = LogColorMapper(palette=Greys256)
#            
#lon = [[coors[0] for coors in cell["geometry"]["coordinates"][0]] for cell in grid_json['features']]
#lat = [[coors[1] for coors in cell["geometry"]["coordinates"][0]] for cell in grid_json['features']]
#names = [cell["id"] for cell in grid_json['features']]
#
## map_types = ['satellite', 'roadmap', 'terrain', 'hybrid']
#map_options = GMapOptions(lat=np.asarray(lat).mean(), lng=np.asarray(lon).mean(), map_type="hybrid", zoom=11, scale_control=True)
#
#
#plots = []
#for day in range(1, 2):
#    
#    # Load data
#    all_data = pd.read_csv("data/mi-to-provinces-2013-11-{:02}.csv".format(day), engine ="python", index_col=0)
#    
#    for hour in range(1):
#        data = all_data
#
#        calls_per_cell = data['CellID'].values
#        calls_per_cell = Counter(calls_per_cell)
##        print(day, hour, calls_per_cell.most_common(5))
#        calls_per_cell = dict(calls_per_cell)
#        
#        for key, value in calls_per_cell.items():
#            calls_per_cell[key] = value/100
#        calls = [calls_per_cell[cell["id"]+1] if cell["id"]+1 in calls_per_cell else 0 for cell in grid_json['features']]
#        calls[0] = 0.0
#        calls[-1] = 1.0
#
#        source = ColumnDataSource(data=dict(
#            lon=lon,
#            lat=lat,
#            names=names,
#            calls=calls,
#            center_lon=[np.mean(x) for x in lon],
#            center_lat=[np.mean(x) for x in lat],
#        ))
#
#        p = GMapPlot(x_range=Range1d(), y_range=Range1d(), map_options=map_options)
#        p.grid.grid_line_color = None
#        p.title.text = "Milan"
#        p.api_key = config.gmaps_api_key
#
#        patches = Patches(xs='lon', ys='lat',
#                  fill_color={'field': 'calls', 'transform': color_mapper},
#                  fill_alpha=0.5, line_color=None, line_width=1)
#        p.add_glyph(source, patches)
#
#        plots.append(p)
#        
#show(column(*plots))
## In[ ]:
#
#
#data = pd.read_csv("data/mi-to-provinces-2013-11-{:02}.csv".format(day), engine ="python", index_col=0)
#
#calls_per_province = data['provinceName'].values
#calls_per_province = Counter(calls_per_province)
#
#print(calls_per_province.most_common(5))
#
#calls_per_province = dict(calls_per_province)
#
#for province in provinces_json['features']:
#    province = province["properties"]["PROVINCIA"].upper()
#    if province not in calls_per_province:
#        
#        def replace_key(new_key, old_key):
#            calls_per_province[new_key] = calls_per_province[old_key]
#            del calls_per_province[old_key]
#            
#        replace_key("AOSTA", "VALLE D'AOSTA")
#        replace_key("BOLZANO", "BOLZANO/BOZEN")
#        replace_key("MASSA CARRARA", "MASSA-CARRARA")
#        
#        if province not in calls_per_province:
#            raise ValueError('{} is not in province list!'.format(province))
#
#lon = [[coors[0] for coors in province["geometry"]["coordinates"][0][0]] for province in provinces_json['features']]
#lat = [[coors[1] for coors in province["geometry"]["coordinates"][0][0]] for province in provinces_json['features']]
#names = [province["properties"]["PROVINCIA"] for province in provinces_json['features']]
#calls = [calls_per_province[province["properties"]["PROVINCIA"].upper()] for province in provinces_json['features']]
#
#source = ColumnDataSource(data=dict(
#    lon=lon,
#    lat=lat,
#    names=names,
#    calls=calls,
#    center_lon=[np.mean(x) for x in lon],
#    center_lat=[np.mean(x) for x in lat],
#))
#
#p = figure(
#    title="Italian Provinces by Number of Calls with Milan", tools=TOOLS,
#    x_axis_location=None, y_axis_location=None
#)
#p.grid.grid_line_color = None
#
#p.patches('lon', 'lat', source=source,
#          fill_color={'field': 'calls', 'transform': color_mapper},
#          fill_alpha=0.7, line_color="white", line_width=0.5)
#
#hover = p.select_one(HoverTool)
#hover.point_policy = "follow_mouse"
#hover.tooltips = [
#    ("Name", "@names"),
#    ("Calls)", "@calls"),
#    ("(Lat, Lon)", "(@center_lat, @center_lon)"),
#]
#
#show(p)
#
## In[ ]:
#
#lon = []
#lat = []
#names = []
#calls = []
#for country in countries_json['features']:  
#    
#    
#    if country["id"] == '-99': # Norther Cyprus
#        country["id"] = "CYP"
#    elif country["id"] == 'CS-KM': # Kosovo
#        country["id"] = "SRB"
#    name = pycountry.countries.get(alpha_3=country["id"]).name
#    
#    if name not in calls_per_country:
#        continue
#    
#    geometry = country["geometry"]
#    if geometry['type'] == 'Polygon':
#        country_borders = [geometry["coordinates"][0]]
#        
#    elif geometry['type'] == 'MultiPolygon':
#        country_borders = []
#        for polygon in geometry["coordinates"]:
#            country_borders += polygon
#    else:
#        raise ValueError('Unknown type of geojson')
#        
#    for polygon in country_borders:
#        lon.append([])
#        lat.append([])
#        names.append(name)
#        calls.append(calls_per_country[name])
#        for coors in polygon:
#            lon[-1].append(coors[0])
#            lat[-1].append(coors[1])
#
##names = [country["properties"]["name"] for country in countries_json['features']]
##calls = [0 for country in countries_json['features']]
#
#source = ColumnDataSource(data=dict(
#    lon=lon,
#    lat=lat,
#    names=names,
#    calls=calls,
#    center_lon=[np.mean(x) for x in lon],
#    center_lat=[np.mean(x) for x in lat],
#))
#
#p = figure(
#    title="Countries by Number of Calls with Milan", tools=TOOLS,
#    x_axis_location=None, y_axis_location=None,
#    plot_width=1500, plot_height=600
#)
#p.grid.grid_line_color = None
#
#p.patches('lon', 'lat', source=source,
#          fill_color={'field': 'calls', 'transform': color_mapper},
#          fill_alpha=0.7, line_color="white", line_width=0.5)
#
#hover = p.select_one(HoverTool)
#hover.point_policy = "follow_mouse"
#hover.tooltips = [
#    ("Name", "@names"),
#    ("Calls)", "@calls"),
#    ("(Lat, Lon)", "(@center_lat, @center_lon)"),
#]
#
#show(p)

