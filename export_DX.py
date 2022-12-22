#BEFORE YOU RUN THIS SCRIPT:
#
#1-Start with a feature dataset that contains: a polyline feature class 
#  of tracks, a point feature class of switches, and a trace network.
#
#2-Select all features, then built a Basic Diagram.
#
#3-Run the Apply Relative Mainline network diagram layout tool.
#
#4-On that diagram, run the Export Diagram Content tool to export the
#  diagram to a JSON file.
#
#5-Go back to the original tracks and switches layers, and export them
#  both to be two new feature classes. Basically carbon copies of these
#  two original feature classes.
#
#6-In the code below:
#  a. update the path to the gdb folder in which you stored the fc copies
#     you created in Step 5
#  b. update the feature class names in the two .UpdateCursor lines below
#     to be the feature class names of the copies you created in Step 5.
#  c. update the path and file name of the json file that you exported
#     in Step 4.
#
#7-Run the script below. Each record of the two copied feature classes
#  will be edited so that the features in the Shape field are updated
#  from the original geographic feature to the new schematic feature

import arcpy
import json


#location of FGDB folder the contains the edges and junctions feature classes
arcpy.env.workspace = r'C:\mapdata\Diagram_JSON_to_FC\data\ns_leach_schematic.gdb'

#edges/junctions feature classes, and the oid and shape fields
cursorPolylines = arcpy.da.UpdateCursor("tracks_schematic_23", ["OBJECTID", "SHAPE@"])
cursorPoints = arcpy.da.UpdateCursor("switches_schematic_23", ["OBJECTID", "SHAPE@"])
    

#open the json file that contains the exported diagram
jsonDX = open(r'C:\mapdata\Diagram_JSON_to_FC\data\exported_1.json')

#load the json object contents into a python object tree structure
dataDX = json.load(jsonDX)

#get the spatial reference wkid
wkid = dataDX['spatialRef']['wkid']


# EXPORT JUNCTIONS FROM DIAGRAM TO FGDB POINT FEATURE CLASS

#for every "junction" feature in the exported diagram json file, 
#create a point feature geometry, and write it into the shape field  
#of the associated record in the "switches" point feature class.
#
#...important ... 
#the order of the features in the exported diagram json is NOT the 
#same order as the records in the feature class you're editing, 
#so, for each record in the feature class, get its oid, then loop 
#thru the json until you find the object with the same oid.
#
#once you found the correct object in the json, construct a point
#geometry object and write it into the "switches" point feature class' 
#shape field.

for row in cursorPoints:
    oidFC = row[0]
    for junction in dataDX['junctions']:
        oidDX = junction['attributes']['OBJECTID']
        if oidDX == oidFC:
            x = junction['geometry']['x']
            y = junction['geometry']['y']
            z = junction['geometry']['z']
            m = junction['geometry']['m']
            pt = arcpy.Point(x,y,z,m)
            ptGeometry = arcpy.PointGeometry(pt, wkid)
            row[1] = ptGeometry
            cursorPoints.updateRow(row)
    

# EXPORT EDGES FROM DIAGRAM TO FGDB POLYLINE FEATURE CLASS

#for every "edge" feature in the exported diagram json file, create 
#a polyline feature geometry, and write it into the shape field of the 
#associated record in the "tracks" polyline feature class.
#
#...important ... 
#the order of the features in the exported diagram is NOT the same
#order as the records in the feature class you're editing, so,
#for each record in the feature class, get its oid, then loop thru
#the json until you find the object with the same oid.
#
#once you found the correct object in the json, construct a polyline
#object and write it into the "tracks" polyline feature class' shape field.
#
#also, for some reason, the x,y,z,m values for each vertex in the
#json file are named 0,1,2,3

for row in cursorPolylines:
    oidFC = row[0]
    for edge in dataDX['edges']:
        oidDX = edge['attributes']['OBJECTID']
        if oidDX == oidFC:            
            pathNew = arcpy.Array()
            pathJson = edge['geometry']['paths'][0]
            z = 0
            hasZ = edge['geometry']['hasZ']
            m = 0
            hasM = edge['geometry']['hasM']
            for vertex in pathJson:
                x = vertex[0]
                y = vertex[1]
                if hasZ: z = vertex[2]
                if hasM: m = vertex[3]
                pt = arcpy.Point(x,y,z,m)
                pathNew.add(pt)
            paths = arcpy.Array()
            paths.add(pathNew)
            pline = arcpy.Polyline(paths, wkid)
            row[1] = pline
            cursorPolylines.updateRow(row)


#clean up cursors and report complete
del cursorPolylines
del cursorPoints
print("DONE!!")







