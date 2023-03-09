# this script loops thru a feature class, and for each
# unique value in a field, it selects features in a 
# layer and displays that selection on a map, one per second

import arcpy
import time

# fill out these values to match your data
file_gdb = r'C:\name\of\the\file.gdb'
feature_class_name = 'fc_in_that_fgdb_above'
field_name = 'A_FIELD'    # field name that contains the unique values
map_name = 'Map'          # this is the name of the map in your Pro project
layer_name = 'layer_name' # this is the name of the layer in that map

arcpy.env.workspace = file_gdb
cursorSearch = arcpy.da.SearchCursor(feature_class_name, [field_name])

aprx = arcpy.mp.ArcGISProject("CURRENT") 
m = aprx.listMaps(map_name)[0]
lyr = m.listLayers(layer_name)[0] 
arcpy.management.SelectLayerByAttribute(lyr, "CLEAR_SELECTION")

for row in cursorSearch:
    county_name = row[0]
    sql_where = field_name + " = '" + county_name + "'"
    print(sql_where)
    arcpy.management.SelectLayerByAttribute(lyr, "NEW_SELECTION", sql_where)
    time.sleep(1)
    arcpy.management.SelectLayerByAttribute(lyr, "CLEAR_SELECTION")
    












