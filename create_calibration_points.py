########
#
# Script: "create_calibration_points.py"
#
# CREATE CALIBRATION POINTS FROM PolylineZM FEATURE CLASS
# 2022-01-25, Jim Barry, Esri, jbarry@esri.com
#
# Description:
#
# This script takes a PolylineMZ feature class that has Ms that you
# want to use to calibrate an LRS Network. And for every XYZM vertex
# it creates a PointZM and writes this feature and attributes into
# an output PointZM feature class.
#
# Prep:
#
# First, before you run the script, use Catalog to create a new empty
# PointZM feature class that uses the same spatial reference as the 
# input PolylineZM routes feature class, and the same fields as is in
# your LRS Network's Calibration_Points feature class.  This script 
# assumes that the input PolylineZM and the output PointZM are in 
# the same FGDB.
# 
# Before you run the script, check all the pathing and naming stuff in
# the first cell below to ensure it lines up with reality. 
# 
# Running the script:
#
# As for the script itself, when you run it, it will loop through every 
# vertex, of every part, of every polyline, and for each vertex, it will 
# write out a new PointZM feature and record, and also the minimum 
# attributes that the LRS Network is expecting as a calibration points 
# feature class.  Namely: PointMZ, RouteName, RouteID, Measure
#
# After you run the script:
# 
# You can take the new output PointZM and append it to your LRS Network's
# Calibration_Points feature class, or replace it, or however you want
# to do it. Make sure the fields are the same, or that the field
# mappings are correct before the append.  Once these new features/records
# are appended to the LRS Network's Calibration_Points feature class, 
# then you can run Generate Routes again, which will apply the new 
# Measures to all of the routes.
#
########

# following line not needed if you're running this script in ArcGIS Pro
# import arcpy 


#### STEP 1

## ENTER HERE the path to the FOLDER into which you saved the fgdb that...
## ...contains both the input polylines and output points, with closing slash
data_path = 'C:/mapdata/data/' # just a sample


#### STEP 2

## INPUT ROUTES FEATURE CLASS AND FIELDS

# fgdb and the input routes PolylineZM feature class
fcIN = data_path + 'name_of_your.gdb/tracks_routes'
# fields from input routes feature class that we need... 
#  ...to bring over to the output calibration point feature class
fieldsIN = ['SHAPE@', 'RouteName', 'RouteId']


#### STEP 3

## OUTPUT CALIBRATION POINT FEATURE CLASS AND FIELDS

# the fgdb where the calibration points will be created
# --be sure this new PointZM feature class is empty
fcOUT = data_path + 'name_of_your.gdb/calib_points'
# fields that the calibration points feature class will need
fieldsOUT = ['SHAPE@', 'RouteName', 'RouteId', 'Measure']

#

# the InsertCursor we need for writing calibration points into
# ...the output PointZM feature class
cursorWRITE = arcpy.da.InsertCursor(fcOUT, fieldsOUT)

# the SearchCursor we need for reading vertices and attributes
# ...out of the input PolylineZM routes feature class
with arcpy.da.SearchCursor(fcIN, fieldsIN) as cursorREAD:
    
    recno = 0
    
    # for each feature record in the input PolylineZM feature class
    for row in cursorREAD:
        
        # get route name and id
        strRouteName = 'route - ' + str(recno)
        strRouteId = row[2]
        
        #loop thru each vertex of each part
        pline = row[0]
        for part in pline:
            for pnt in part:
                # read out the M value, so that it can be written.. 
                # ...into the output 'Measure' column
                m = pnt.M  
                # write each point to the output calibration point feature class
                cursorWRITE.insertRow([pnt, strRouteName, strRouteId, m])
        
        recno += 1

# report back and clean up
print('ALL DONE')
del cursorREAD
del cursorWRITE


