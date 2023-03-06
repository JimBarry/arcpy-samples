import arcpy
import requests
import json

# set this value between 1-5 to control the topHierarchyLevel
hier = "1"

# FGDB and cursor built on the FC
arcpy.env.workspace = r'C:\mapdata\NSroutes\data\routes_data.gdb'
cursorODs = arcpy.da.UpdateCursor("ods_hierarchies", ["Origin_Lat", "Origin_Long", "Destin_Lat", "Destin_Long", "Miles_TopH_"+hier, "Mins_TopH_"+hier])

# start building the REST API URL; all but the "stops"
route_url = "https://route.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"
use_hier = "&useHierarchy=true"
impedance = "&impedanceAttributeName=Miles"
accum = "&accumulateAttributeNames=Minutes"
directions = "&returnDirections=false"
output_lines = "&outputLines=esriNAOutputLineNone"
overrides = "&overrides=%7BtopHierarchyLevel=" + hier + "%7D" # ie, overrides = {topHierarchyLevel=1}
token = "&token=xxxxx" #your token or API Key goes here
return_format = "&f=pjson"

# cursor thru each record in the FC
ctr = 0
for row in cursorODs:

    # read the origin and destination coordinates
    origin_lat = row[0]
    origin_lon = row[1]
    destin_lat = row[2]
    destin_lon = row[3]

    # build the "stops" part of the REST URL
    stops = "?stops=" + str(origin_lon) + "," + str(origin_lat) + ";" + str(destin_lon) + "," + str(destin_lat)

    # build the REST URL
    api_url = route_url + stops + use_hier + impedance + accum + directions + output_lines + overrides + token + return_format

    # make the REST call, get results, convert to a Python dictionary
    response = requests.get(api_url)
    response_json = response.json()

    # parse the JSON to grab the shortest path's mileage (and time, if you want it too)
    attribs = response_json["routes"]["features"][0]["attributes"]
    travel_distance_miles = int(attribs["Total_Miles"])
    travel_time_minutes = int(attribs["Total_Minutes"])

    # write the shortest path's miles and minutes into the FC
    row[4] = travel_distance_miles
    row[5] = travel_time_minutes
    cursorODs.updateRow(row)

    # just so that you see it running
    print(str(ctr) + "- min: " + str(travel_time_minutes) + "; miles:" + str(travel_distance_miles))
    ctr+=1
  
print("DONE")
del cursorODs
