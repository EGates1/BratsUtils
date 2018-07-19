#  
#  Creates image filepaths in a csv and excel file from IDs
#  
#  Assumes following directory structure
#    .
#    +-- csvfilewithids.csv     # CSV file with ids
#    +-- HGG                    # Directory for each type (HGG, LGG, VAL, ...)
#    |   +-- ID_1               # Directory for each ID belonging to the type
#    |   |  +-- ID_1_t1.nii.gz  # Images for each ID
#    |   |  +-- ID_1_t2.nii.gz
#    |   |  ...
#    |   +-- ID_2
#    |   ...
#    +-- LGG
#    |
#    +-- VAL
#    ...
#
#  Usage:
#    $ python createFilePaths.py -f csvfilewithids.csv
# 
#    Optional command line args
#      --id, -i [ID]          Name of column in csv file with IDs 
#                               (default = BraTS18ID)
#      --type, -t [TYPE]      Name of colume in csv with patient type
#                               i.e. HGG, LGG, VAL, etc. where these are folders
#                               containing sub folders for each ID 
#                               (default = type)
#      --directory, -d [DIR]  Path to new directory to place csv file in
#                               (default = directory of csv file with ids)
#      --overwrite, -o        Flag if specified will allow input csv to be
#                               overwritten. Only used if --directory or --name
#                               are not specified
#      --excel, -e            Flag to also make an excel file with viewer column
#      --name, -n [NAME]      Name of new csv file (default = name of input csv)

import argparse, os
import pandas as pd

# Get params from cmd line
parser = argparse.ArgumentParser(description = "Creates filepaths for image files from IDs")
parser.add_argument("--file", "-f", help = "CSV with IDs", 
      required = True) 
parser.add_argument("--id", "-i", default = "BraTS18ID", 
      help = "Name of column with IDs")
parser.add_argument("--type", "-t", default = "type", 
      help = "Name of column with type (i.e. HGG, LGG, VAL, TEST, etc.)")
parser.add_argument("--directory", "-d", default = None,
      help = "Directory to write new CSV to")
parser.add_argument("--overwrite", "-o", action = "store_true",
      help = "Overwrite given csv of IDs")
parser.add_argument("--excel", "-e", action = "store_true",
      help = "Create excel file with filepaths plus viewer column")
parser.add_argument("--name", "-n", default = None,
      help = "Name of output CSV file")
args = parser.parse_args()

# List of list of length 2 where the first index is the column title and
# the second index is string to append to the filepath + id
#   e.g.  ["COLNAME", "FILEAPPEND"]
#         a column called "COLNAME" will be created and for each row with an
#         ID, a new filepath will be added with format 
#         "path/to/ROWID_FILEAPPEND.nii.gz"
# To add more columns, just add a new ["COLNAME", "FILEAPPEND"] to this list
columnPathPairs = [
    ["T1", "t1"], ["T2", "t2"], ["T1C", "t1ce"], ["FLAIR", "flair"],
    ["seg", "seg"], ["mask", "mask"], ["tumor", "tumor"], 
    ["nontumor", "nontumor"], ["tissue", "tissue"], ["atropos", "atropos"],
    ["BE3_Grade", "BE3_Grade_RF_POS"], ["CD", "CD_RF_POS"],
    ["ERGarea", "ERGarea_RF_POS"], ["Ki67", "Ki67_RF_POS"],
    ["dm_T1_znorm", "dm_t1_znorm"], ["dm_T2_znorm", "dm_t2_znorm"], 
    ["dm_T1C_znorm", "dm_t1ce_znorm"], ["dm_FLAIR_znorm", "dm_flair_znorm"], 
    ["dm_roi_mask", "dm_roi_mask"]
  ] 

print("Reading file {0}".format(args.file))
csvFile = pd.read_csv(args.file)

print("Creating columns: {0}".format([pair[0] for pair in columnPathPairs]))

# Create empty column for each COLNAME in columnPathPairs if the column does
# not already exist
for pair in columnPathPairs:
  if pair[0] not in csvFile:
    csvFile[pair[0]] = ""

print("Writing filepaths...")

# For each ID in csvFile
for i in range(len(csvFile.index)):
  # Get row ID
  rowID = csvFile[args.id].iloc[i]

  # get row type if exists
  if args.type in csvFile:  
    rowType = csvFile[args.type].iloc[i] + "/"
  else: 
    rowType = ""

  # For each column write path for current ID
  # Filepath format:
  #   TYPE/ID/ID_FILEAPPEND.nii.gz
  #   e.g. HGG/Brats_CBICA_ABC_1/Brats_CBICA_ABC_1_t2.nii.gz
  # TODO Check if is blank else skip
  for pair in columnPathPairs:
    filepath = rowType + rowID + "/" + rowID + "_" + pair[1] + ".nii.gz"
    csvFile.at[i, pair[0]] = filepath

print("All filepaths created")

# Create new filename/path to write csv file to
newCSVFile = None
# If directory specified make new csv file in that directory
if args.directory is not None:
  # check if dir exists, if not make it
  if not os.path.isdir(args.directory):
    os.makedirs(args.directory)
  newCSVFile = args.directory
  # Use specified name or use existing name of file
  if args.name is not None:
    newCSVFile = newCSVFile + "/" + args.name
  else:
    newCSVFile = newCSVFile + "/" + os.path.basename(args.file)
# If no directoy, use current directory with given name
elif args.name is not None:
  newCSVFile = os.path.dirname(args.file) + args.name
# If no directory or name specified but overwrite flag is true
# overwrite the input csv file
elif args.overwrite:
  newCSVFile = args.file
# If overwrite flag == false, append input filename to write csv file to
else:
  split = os.path.splitext(args.file)
  newCSVFile = split[0] + "_with_paths" + split[1]

# Write csv file
csvFile.to_csv(newCSVFile, index=False)
print("CSV file written to {0}".format(newCSVFile))

if args.excel:
  print("Creating \"viewer\" column...")

  # Create excel file
  xlsxFileName = os.path.splitext(newCSVFile)[0] + ".xlsx"
  xlsxFile = pd.ExcelWriter(xlsxFileName)

  viewerList = []
  for i in range(len(csvFile.index)):
    # Get row ID
    rowID = csvFile[args.id].iloc[i]

    # get row type if exists
    if args.type in csvFile:
      rowType = csvFile[args.type].iloc[i] + "/"
    else:
      rowType = ""

    viewer = ("=REVIEWTRUTH(1,\"-C " + os.path.dirname(args.file) + 
              " -f prediction.makefile " + rowType + rowID + 
              "/reviewtruth\")")
    viewerList.append(viewer)
   
  # Create viewer column with vector
  csvFile.insert(csvFile.columns.get_loc(
      columnPathPairs[0][0]), "viewer", viewerList)

  print("Viewer column created")

  # Write excel file
  csvFile.to_excel(xlsxFile, index=False)
  xlsxFile.save()
  print("Excel file written to {0}".format(xlsxFileName))
