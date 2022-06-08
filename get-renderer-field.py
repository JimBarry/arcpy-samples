import arcpy
aprx = arcpy.mp.ArcGISProject("CURRENT")
m = aprx.listMaps("name_of_map")[0]
lyr = m.listLayers("name_of_layer")[0]
symb = lyr.symbology
rend = symb.renderer
fld = rend.classificationField
print(fld)