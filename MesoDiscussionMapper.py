

import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import ast
import requests
from PIL import Image
import numpy as np
from io import BytesIO
import datetime


source = input('Are you using a direct link? (y or n): ')

coords = []
coordinates = []

if source == 'n':
    text = input('Paste the raw coordinates: ') 
    
if source == 'y': 
    url = input('Enter Meso Discussion Link: ')
    #open the URL and extract the text
    html = urlopen(url).read()
    soup = BeautifulSoup(html,features="html.parser")
    text = soup.get_text() #get URL text


#extract 8-digit numbers from discussion (lat/lon) 
pattern = r'\b\d{8}\b'
matches = re.findall(pattern, text)
matches_tuple = tuple(matches)

for n in matches:
    coords.append("("+n[0:2]+'.'+n[2:4]+',-'+n[4:6]+'.'+n[6:]+")")
coords.append("("+matches[-1][0:2]+'.'+matches[-1][2:4]+',-'+matches[-1][4:6]+'.'+matches[-1][6:]+")")
for z in coords:
    coordinates.append(ast.literal_eval(z))
    
# Create a Polygon from the Mesoscale Discussion coordinates then Create a GeoDataFrame with the polygon
polygon = Polygon([(lat, lon) for lon, lat in coordinates])
polygon_gdf = gpd.GeoDataFrame(index=[0], geometry=[polygon], crs="EPSG:4326")
polygon_gdf2 = gpd.GeoDataFrame(index=[0], geometry=[polygon], crs="EPSG:4326")

# Define the path to shapefiles
nys_border = "/Users/ethan/Desktop/GIS - Projects/NYS Mapping Layers/NYS Shorline.shp"
border = gpd.read_file(nys_border) # Load the shapefile into a GeoDataFrame 
nys_interstates = "/Users/ethan/Desktop/GIS - Projects/NYS Mapping Layers/NYS Interstates.shp"
interstates = gpd.read_file(nys_interstates) 
interstates2 = gpd.read_file(nys_interstates) 
nys_cities = "/Users/ethan/Desktop/GIS - Projects/NYS Mapping Layers/NYS Cities.shp"
cities = gpd.read_file(nys_cities) 
nys_counties = "/Users/ethan/Desktop/GIS - Projects/NYS Mapping Layers/NYS Counties.shp"
counties = gpd.read_file(nys_counties) 
us_states = "/Users/ethan/Desktop/GIS - Projects/NYS Mapping Layers/US StatesCoastlines.shp"
states = gpd.read_file(us_states) 
world_countries = "/Users/ethan/Desktop/GIS - Projects/NYS Mapping Layers/World Countries.shp"
countries = gpd.read_file(world_countries) 

# Plot the shapefiles
fig, ax = plt.subplots(figsize=(10, 10))
interstates2.plot(ax=ax, edgecolor='white', facecolor='none', alpha=1, linewidth=1)
interstates.plot(ax=ax, edgecolor='blue', facecolor='none', alpha=1, linewidth=0.5)
countries.plot(ax=ax, edgecolor='black', facecolor='darkgray', alpha=1, linewidth=0.25)
states.plot(ax=ax, edgecolor='black', facecolor='darkgray', alpha=1, linewidth=0.25)
counties.plot(ax=ax, edgecolor='black', facecolor='white', alpha=1, linewidth=0.25)
border.plot(ax=ax, edgecolor='black', facecolor='none', alpha=1, linewidth=2)



# Using the current time, generate the radar from the previous 5-minute benchmark
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M') #used in the plot timestamp
minute05 = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 0]
minute04 = [4, 9, 14, 19, 24, 29, 34, 39, 44, 49, 54, 59]
minute03 = [3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53, 58]
minute02 = [2, 7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57]
minute01 = [1, 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, 56]
for n in minute05: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=5))
    else: 
        continue
for n in minute04: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=4))
    else: 
        continue
for n in minute03: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=3))
    else: 
        continue
for n in minute02: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=2))
    else: 
        continue
for n in minute01: 
    if datetime.datetime.now().minute == n: 
        changedtime = str(datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=1))
    else: 
        continue
year = changedtime[0:4]
month = changedtime[5:7]
day = changedtime[8:10]
hour = changedtime[11:13]
minute = changedtime[14:16]
radar_time = year+'-'+month+'-'+day+' '+hour+':'+minute
png_url = "https://mesonet.agron.iastate.edu/archive/data/" + year + "/" + month + "/" + day + "/GIS/uscomp/n0q_" + year + month + day + hour + minute + ".png"
wld_url = "https://mesonet.agron.iastate.edu/archive/data/" + year + "/" + month + "/" + day + "/GIS/uscomp/n0q_" + year + month + day + hour + minute + ".wld"

# Download the PNG image
png_response = requests.get(png_url)
png_image = Image.open(BytesIO(png_response.content)).convert('RGBA')

# Download and parse the world file
wld_response = requests.get(wld_url)
wld_content = wld_response.text.strip().split()
wld_values = list(map(float, wld_content))

# Extract georeferencing information from the world file
pixel_size_x = wld_values[0]
rotation_y = wld_values[1]
rotation_x = wld_values[2]
pixel_size_y = wld_values[3]
upper_left_x = wld_values[4]
upper_left_y = wld_values[5]

# Compute the extent of the image
width, height = png_image.size
extent = [
    upper_left_x,
    upper_left_x + width * pixel_size_x,
    upper_left_y + height * pixel_size_y,
    upper_left_y
]



#Give the radar image a transparent background
data = np.array(png_image)
alpha = np.where((data[:, :, 0] == 0) & (data[:, :, 1] == 0) & (data[:, :, 2] == 0), 0, 255) # Create a mask from RGB pixel values at a threshold (0,0,0 = black)
data[:, :, 3] = alpha
# Create a new image with the transparent background
new_image = Image.fromarray(data, 'RGBA')
# Plot the radar
ax.imshow(np.asarray(new_image), extent=extent, origin='upper', zorder=9, alpha = 0.75)


# Plot the polygon on top of the shapefiles and radar
polygon_gdf.plot(ax=ax, edgecolor='red', facecolor='yellow', alpha=0.25, linewidth=2, zorder=10)
polygon_gdf2.plot(ax=ax, edgecolor='red', facecolor='none', alpha=1, linewidth=2, zorder=10)
cities.plot(ax=ax, edgecolor='black', facecolor='white', alpha=1, linewidth=1, zorder=10)


# Get the current time
current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

# Add a text box with the timestamp
ax.text(
    x=0.03, y=0.05,  # Position (relative coordinates, adjusted for margins)
    s=f'Map generated at: {current_time}',  
    fontsize=10,  
    bbox=dict(facecolor='white', alpha=0.7, edgecolor='black'),  # Bounding box properties
    transform=ax.transAxes,  # Use axes coordinate system
    zorder=10
)

# Customize the plot
plt.title("Current Focus Area", fontsize=20)
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.xlim(-81,-71.5)
plt.ylim(40,45.5)
ax.set_facecolor('lightblue')


# Show the plot
plt.show()
