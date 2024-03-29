# This script builds and sends a request to the World Route ArcGIS REST API
# For each row, it gets origin and destination point locations
# It then parses the results and writes them into columns into the same row

# modules we'll need
import arcpy
import requests
import json

# file geodatabase that we want to work with
arcpy.env.workspace = r'C:\mapdata\NSroutes\data\routes_data.gdb'

# feature class within that fgdb that we want to work with
feature_class_name = "ods"

# adjust these field names to fit yours
# the first 4 are for reading, the last 2 are for writing
fields_for_cursor = ["Origin_Lat", "Origin_Long", "Destin_Lat", "Destin_Long", "Esri_Time", "Esri_Distance"]

# create an UpdateCursor for reading and writing
cursorODs = arcpy.da.UpdateCursor(feature_class_name, fields_for_cursor)

# start to prepare the REST API URL
route_url = "https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"
token = "&token=your_token_or_api_key_goes_here"
return_format = "&f=pjson"

# for each row, route between two points and write the results into the same row
for row in cursorODs:
    # read the origin and destination lats and longs
    # the index values below are the same order as the "fields_for_cursor" list above
    # with the new "arcpy.da" module, you refer to fields by index, not by name
    origin_lat = row[0]
    origin_lon = row[1]
    destin_lat = row[2]
    destin_lon = row[3]

    # build the "stops" parameter values
    stops = "?stops=" + str(origin_lon) + "," + str(origin_lat) + ";" + str(destin_lon) + "," + str(destin_lat)

    # build the full REST API URL call
    api_url = route_url + stops + token + return_format
    #print(api_url)

    # get the response from the REST request
    response = requests.get(api_url)

    # load the response into a Python dictionary
    response_json = response.json()

    # get the time and distance for the shortest route found
    attribs = response_json["routes"]["features"][0]["attributes"]
    travel_time_minutes = attribs["Total_TravelTime"]
    travel_dist_miles = attribs["Total_Miles"]

    # write the travel time and distance
    row[4] = travel_time_minutes
    row[5] = travel_dist_miles

    # commit the edits to the row
    cursorODs.updateRow(row)

    # display the results to the notebook if you want
    print(str(ctr) + "- min: " + str(travel_time_minutes) + "; miles:" + str(travel_dist_miles))
    ctr+=1
    
# finish up
print("DONE")
del cursorODs

