import arcpy
import requests
import json

### User inputs a US street address and in return is shown
### information about the Congressional District that address
### resides within.

# GEOCODE THE INPUT ADDRESS

input_address = input('Enter a street address:')

# this is Esri's "World Geocoding Service"
geocode_url = "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"

# this builds the parameters needed by the geocoding REST service call
input_address_parameter = "?SingleLine=" + input_address
token = "&token=your_token_or_api_key_here"
extra_params = "&f=json"
api_url = geocode_url + input_address_parameter + token + extra_params

# make the REST API call request
# and receive response
response = requests.get(api_url)

# format the response into JSON
response_json = response.json()

# parse the JSON response to pull out the data that we need
best_candidate = response_json["candidates"][0]
standardized_address = best_candidate["address"]
location = best_candidate["location"]
x = location["x"]
y = location["y"]
ptGeocoded = arcpy.Point(x,y)
ptGeocoded_geom = arcpy.PointGeometry(ptGeocoded, '4326')

# just a gut check to ensure that the geocoding returned a point
print('x: ' + str(x) + ', ' + 'y: ' + str(y))

# FIND THE CONGRESSIONAL DISTRICT FOR A POINT LOCATION

# the feature class where we will store the geocoded point
fcGeocodedPoint = "C:/mapdata/congress_districts/data/congress_data.gdb/geocoded_points"

# the feature class that contains the congressional district polygons
fcCongress = "C:/mapdata/congress_districts/data/congress_data.gdb/USA_118_Congress"

# the fields in that feature class that contain the data we're want to know
fldsCongress = ["STATE_NAME", "CDFIPS", "NAME", "PARTY"]

# edit the geocoded point into the "geocoded_points" feature class
ucGeocodedPoint = arcpy.da.UpdateCursor(fcGeocodedPoint, ["SHAPE@"])
for row in ucGeocodedPoint:
    row[0] = ptGeocoded_geom
    ucGeocodedPoint.updateRow(row)
    
# select the congressional district that contains the geocoded point
selDistrict = arcpy.management.SelectLayerByLocation(fcCongress, "CONTAINS", fcGeocodedPoint, 0, "NEW SELECTION")
	
# open the selected attribute table so that we can read data we need from the selected fields
scDistrict = arcpy.da.SearchCursor(selDistrict, fldsCongress)
	
# format and display the results to the user
for row in scDistrict:
    result = "\nStandardized address: " + standardized_address + \
	     "\n" + \
	     "\nState: " + row[0] + \
	     "\nDistrict: " + row[1] + \
	     "\nRepresentative: " + row[2] + \
	     "\nParty: " + row[3]
    print(result)
    
    
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
