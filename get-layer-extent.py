# Use this script to get the rectangular extent bounding box of a layer in your map.
# This can be a feature layer or an image layer.  Any layer as far as I can tell.
# The x/y values returned are in the layer's native spatial reference, not the spatial reference of the map.
# Of course if you need to convert those values, the WKID returned below is what you can use.

# not needed if running in a Pro notebook
import arcpy 

# assuming you're running this on your current Pro project's notebook
aprx = arcpy.mp.ArcGISProject("CURRENT") 

# obviously you need to edit these parameters
m = aprx.listMaps("name_of_your_map")[0]
lyr = m.listLayers("name_of_the_layer")[0]

src = lyr.dataSource
desc = arcpy.Describe(src)
ext = desc.extent #bounding box
srfc = desc.spatialReference.factoryCode #the WKID

# tell 'em what they won, Johnny
print('minX: ' + str(ext.XMin))
print('minY: ' + str(ext.YMin))
print('maxX: ' + str(ext.XMax))
print('maxY: ' + str(ext.YMax))
print('WKID: ' + str(srfc))


