# Use this script on a feature layer in a Pro Map, to find the name of the field currently being used by the Symbology Renderer on that layer

# don't need this if you're running in a notebook within Pro
import arcpy

# assume you're running this script in the same project your map is in
aprx = arcpy.mp.ArcGISProject("CURRENT")

# edit these parameters to fit your map name and layer name
m = aprx.listMaps("name_of_map")[0]
lyr = m.listLayers("name_of_layer")[0]

# the layer has symbology; the symbology has a renderer; the renderer has a classificationField
symb = lyr.symbology
rend = symb.renderer
fld = rend.classificationField

# robert's your father's brother
print(fld)
