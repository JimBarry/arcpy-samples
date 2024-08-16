#------START OF SCRIPT--------------------------

# This script measures railroad track curvature.
# 2024-06-01
# 
# Questions, comments: contact Jim Barry at Esri: jbarry@esri.com
# 
#
# This script runs on an M-enabled Polyline feature class built for routes.
# Each route should be calibrated so that the M values are mileposts.
# For each route feature, this script walks from start to end, placing a 
# measure point every 50' so that each three sets of points is 100' long,
# creating a measureable angle. You can adjust this value on LINE 26. 
# 
# Then during this walk, the angle created by each set of three points 
# can be measured, and then stored in the center point's attribute record.
#
# When the angle created by each set of three measured points is 
# less than 0.5 degrees, that angle is considered "STRAIGHT". This 
# curve tolerance value is also adjustable on LINE 26.

import arcpy

# spatial reference conversion objects
sr4326 = arcpy.SpatialReference(4326)
sr102005 = arcpy.SpatialReference(102005)
gt = "NAD_1983_To_WGS_1984_4"

# curve tolerance, a curve percent less than this is considered "STRAIGHT"
CURVE_TOLERANCE_PERCENT = 0.5

# measurement constants: feet, meters, miles
CURVE_LENGTH_INTERVAL_FEET = 100  # 100' per USDOT FRA PTC
CURVE_POINT_INTERVAL_FEET = CURVE_LENGTH_INTERVAL_FEET / 2
CURVE_POINT_INTERVAL_METERS = CURVE_POINT_INTERVAL_FEET * 0.3048
CURVE_POINT_INTERVAL_MILES = CURVE_POINT_INTERVAL_FEET * 0.0001893932


#-----------------------------------------------

# normalize bearing to 0-360 degrees
def normalize_bearing(angle):
    az = angle
    if az < 0:
        az = 180 + (180 - abs(az))
    if az >= 360:
        az = 0
    return az 

#-----------------------------------------------

# FGDB for reading in the track lines, and where the curve points will go
fgdb = "C:/mapdata/Curvature/data/RR_Track.gdb"
arcpy.env.workspace = fgdb

# FC of the track centerlines
# ...this FC must contain PolylineM route features
# ...this routes FC must be calibrated so that every vertex's M is a milepost value
fcIN = fgdb + "/TRK_CTL_routes_calib_milepost"
fieldsIN = ['SHAPE@']
cursorREAD = arcpy.da.SearchCursor(fcIN, fieldsIN)

# at the moment, we're just working with one route centerline
# (when you have many, this will need to be a loop)
row = cursorREAD.next()
pline_D = row[0]
pline_D_len = pline_D.length
pline_P = pline_D.projectAs(sr102005, gt)
pline_P_len = round(pline_P.length, 5)
print('lenD: ' + str(pline_D_len) + ', lenM: ' + str(pline_P_len))
    
#-----------------------------------------------

# FC for writing out the curve points, stored in the same FGDB
# ensure the FGDB also contains the feature class template!
arcpy.management.CreateFeatureclass(fgdb, "curve_points", "POINT", \
                                    "curve_points_template", "ENABLED", "ENABLED", sr4326)
fcOUT = fgdb + "/curve_points"
fieldsOUT = ['SHAPE@', 'X', 'Y', 'lambda', 'phi', 'milepost', \
             'curve_percent_actual', 'curve_percent_absolute', 'curve_direction']
cursorWRITE = arcpy.da.InsertCursor(fcOUT, fieldsOUT)

#-----------------------------------------------

# initialize the output curve point FC with its first record
# ( measuring curvature begins with the 2nd curve point)
ptFirst_P = pline_P.firstPoint
ptFirst_D = pline_D.firstPoint
ptgFirst_D = arcpy.PointGeometry(ptFirst_D, sr4326)
thisMeasure = ptFirst_D.M
print(thisMeasure) # the milepost of the first
to_insert = [ptgFirst_D, ptFirst_P.X, ptFirst_P.Y, ptFirst_D.X, ptFirst_D.Y, thisMeasure, \
             0, 0, 'STRAIGHT']
cursorWRITE.insertRow(to_insert)

#-----------------------------------------------

startpt_len = 0
basept_len = startpt_len + CURVE_POINT_INTERVAL_METERS
endpt_len = startpt_len + (CURVE_POINT_INTERVAL_METERS * 2)
idx = 0

while endpt_len < pline_P_len:
    
    idx += 1
    #if idx == 5:
    #    break
    
    # find the start, base, and end point in projected space
    ptgStart_P = pline_P.positionAlongLine(startpt_len)
    ptStart_P = ptgStart_P.firstPoint
    ptgBase_P = pline_P.positionAlongLine(basept_len)
    ptBase_P = ptgBase_P.firstPoint
    ptgEnd_P = pline_P.positionAlongLine(endpt_len)
    ptEnd_P = ptgEnd_P.firstPoint
    
    # find the start, base, and end point in unprojected space
    ptgStart_D = ptgStart_P.projectAs(sr4326, gt)
    ptStart_D = ptgStart_D.firstPoint
    ptgBase_D = ptgBase_P.projectAs(sr4326, gt)
    ptBase_D = ptgBase_D.firstPoint
    ptgEnd_D = ptgEnd_P.projectAs(sr4326, gt)
    ptEnd_D = ptgEnd_D.firstPoint
    
    #### calculate the first and second bearings, and the delta
    aad1 = ptgStart_D.angleAndDistanceTo(ptgBase_D)
    angle1 = round(aad1[0], 5)
    bearing1 = normalize_bearing(angle1)
    aad2 = ptgBase_D.angleAndDistanceTo(ptgEnd_D)
    angle2 = round(aad2[0], 5)
    bearing2 = normalize_bearing(angle2)
    bearing_delta = bearing2 - bearing1
    curve_percent_actual = round(bearing_delta, 5)
    curve_percent_absolute = abs(bearing_delta)
    
    # determine if this measured angle is right, left, or straight
    if curve_percent_actual > 0:
        curve_direction = "RIGHT"
    if curve_percent_actual < 0:
        curve_direction = "LEFT"
    if curve_percent_absolute < CURVE_TOLERANCE_PERCENT:
        curve_direction = "STRAIGHT"
    
    # calculate the milepost value of the base point
    thisMeasure = round(thisMeasure + CURVE_POINT_INTERVAL_MILES, 5)
    
    # populate the base point shape and its attributes
    to_insert = [ptgBase_D, ptBase_P.X, ptBase_P.Y, ptBase_D.X, ptBase_D.Y, thisMeasure, \
                 curve_percent_actual, curve_percent_absolute, curve_direction]
    cursorWRITE.insertRow(to_insert)
    
    # increment each of the three lengths by 50'
    startpt_len = round(basept_len, 5)
    basept_len = round(endpt_len, 5)
    endpt_len = round(endpt_len + CURVE_POINT_INTERVAL_METERS, 5)
    
    print(str(idx)+ ': mile, ' + str(thisMeasure) + ', len, ' + str(endpt_len) + "/" + str(pline_P_len))
       
del cursorWRITE    
    
print('done')    

#------END OF SCRIPT----------------------------






























