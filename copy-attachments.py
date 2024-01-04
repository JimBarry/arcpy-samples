import arcpy

#Script assumes that both feature classes and related attachment tables
# are all in the same file geodatabase.
#If they're not, then you can do some tweaking to ensure that the
# subsequent objects below are pointing to the right places.
fgdb_name = 'C:/mapdata/photo/photo_attach_1.gdb'
fgdb_path = fgdb_name + '/'
arcpy.env.workspace = fgdb_name

# **** IMPORTANT ****
#If you're going to run this script more than once, be sure to first delete
# all of the records out of the output attachments table
#
#Also, when you run this script, you may see some strange behavior, like the
# features in the map might disappear. The script creates all kinds of new view
# layers and tables, etc.  I recommend you remove all the new view layers and tables
# leaving the original ones, also close the output attachments table, then save the 
# project, close ArcGIS Pro, then reopen ArcGIS Pro, then reopen this project.  
# Everything should be clean then. At that point, open the output attachments table
# to find that all the new records are there. Also, in the map, you'll see the green
# points layer, which is the input fc, and also the red points layer which is the 
# output fc. If you choose the Explore tool, you can click on any of the points to 
# find that both of the layers have all the correct attachment images in the popup.

#If you have any questions or comments about this, contact Jim Barry at Esri
# jbarry@esri.com

#fcIN is the feature class that contains the photo attachments you want copied over
fcIN = fgdb_path + 'boros_1'
fcFldsIN = ['OBJECTID', 'boroname']
#The second field above contains values that have a one-to-one relationship
# with a field in the output feature class. The values in these two fields
# will be used to find the correct attachment file.

#tblAttIN is the attachments table for fcIN
tblAttIN = fgdb_path + 'boros_1__ATTACH'
tblAttFldsIN = ['REL_OBJECTID', 'CONTENT_TYPE', 'ATT_NAME', 'DATA_SIZE', 'DATA']
#The [DATA] field is a BLOB that contains a raw binary representation of the
# attached image.

#fcOUT is the feature class that you want to copy the attachments info from fcIN
fcOUT = fgdb_path + 'boros_2'
fcFldsOUT = ['OBJECTID', 'boroname']
#The second field above contains values that have a one-to-one relationship
# with a field in the input feature class. The values in these two fields
# will be used to find the correct attachment file.

#tblAttOUT is the attachments table for fcOUT, and it starts out empty
tblAttOUT = fgdb_path + 'boros_2__ATTACH'
tblAttFldsOUT = ['REL_OBJECTID', 'CONTENT_TYPE', 'ATT_NAME', 'DATA_SIZE', 'DATA']
#The [DATA] field is a BLOB that contains a raw binary representation of the
# attached image.

#SearchCursor for the input feature class
searchcursorFcIN = arcpy.da.SearchCursor(fcIN, fcFldsIN)

#SearchCursor for the input feature class' attachment table
searchcursorTblAttIN = arcpy.da.SearchCursor(tblAttIN, tblAttFldsIN)

#SearchCursor for the output feature class
searchcursorFcOUT = arcpy.da.SearchCursor(fcOUT, fcFldsOUT)

#This outermost loop is looping through the OUTPUT feature class.
#For every feature, we're going to find the attachment associated with it
# and copy it over
for row in searchcursorFcOUT:
    
    #get the objectid of the output feature class record
    # this value we will be writing into the output attachments table, so that each of the 
    # features in the output fc will know which row in its attachments table stores its image
    intOutOBJECTID = row[0]
    #get the value from the output feature class that we will search for
    strOutLinkName = row[1]
    
    #use the value from the output fc to find the associated record in the input fc
    selFcIN = arcpy.management.SelectLayerByAttribute(fcIN, 'NEW_SELECTION', "boroname = '" + strOutLinkName + "'")
    #the only field we need in this search result is the OBJECTID
    scFcIN = arcpy.da.SearchCursor(selFcIN, ["OBJECTID"])
    
    #Optimally 'scFcIN' should only have one record in it
    for rowScFcIN in scFcIN:
        
        #get the OBJECTID of the associate feature in the input fc 
        selOIDFcIN = rowScFcIN[0]
        
        #using that OBJECTID, find the associated record in the input attachments table
        selTblAttIN = arcpy.management.SelectLayerByAttribute(tblAttIN, "NEW_SELECTION", "REL_OBJECTID = " + str(selOIDFcIN))
        #from this search result, we need all the attachment table fields from the input attachments table
        # that we'll need for copying values over into the output attachments table 
        scTblAttIN = arcpy.da.SearchCursor(selTblAttIN, ["CONTENT_TYPE", "ATT_NAME", "DATA_SIZE", "DATA"])

        #Optimally 'scTblAttIN' should only have one record in it
        for rowScTblAttIN in scTblAttIN:
            
            #get all the values from the input attachments table that we'll write into the output attachments table
            strCONTENT_TYPE = rowScTblAttIN[0]
            strATT_NAME = rowScTblAttIN[1]
            intDATA_SIZE = rowScTblAttIN[2]
            blobDATA = rowScTblAttIN[3]
            
            #create an insert cursor for the output attachments table
            insertcursorTblAttOUT = arcpy.da.InsertCursor(tblAttOUT, tblAttFldsOUT)
            
            #write a new row into the output attachments table and write field values into it,
            # including the 'blobData' which is a binary representation of the attached image
            insertcursorTblAttOUT.insertRow([intOutOBJECTID, strCONTENT_TYPE, strATT_NAME, intDATA_SIZE, blobDATA]) 
            
            #delete the InsertCursor
            del insertcursorTblAttOUT    

# delete all the SearchCursors
del searchcursorFcIN
del searchcursorTblAttIN
del searchcursorFcOUT
