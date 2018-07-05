import numpy as np
import argparse, os, sys, math
import pandas as pd
import SimpleITK as sitk

# Get params from cmd line
parser = argparse.ArgumentParser(description = "Preprocess nii files")
parser.add_argument("--file", "-f", help = "CSV with filepaths", 
      required = True) 
parser.add_argument("-n4", action = "store_true", 
      help = "Apply n4 bias correction")
parser.add_argument("-norm", action = "store_true",
      help = "Z-score normalize data")
parser.add_argument("-skipNoSurvival", action = "store_true", 
      help = "Skip subjects with no survival time")
args = parser.parse_args()

survival = "Survival"
ids = "BraTS18ID"
imageNames = ["T1", "T2", "T1C", "FLAIR"]
ext = ".nii.gz"

# Read csv into pandas dataframe
paths = pd.read_csv(args.file)

# file ending
ending = ""
if not args.n4 and not args.norm:
  sys.exit("Must specify at least one of -n4 and -norm")
if args.n4:
  ending = ending + "_n4"
if args.norm:
  ending = ending + "_norm"

# Create columns for new filepaths
for name in imageNames:
  paths[name + ending] = ""
paths["preprocess_roi"] = ""

# Path to folder containg csv
directory = os.path.dirname(args.file)

# Num subjects in csv
count = len(paths.index)

# Loop for each subject in csv
for i in range(count):
  
  # If --skipNoSurvival is specified in cmd args, skip subject if they do
  # not have a valid survival time
  if args.skipNoSurvival and not math.isnan(paths["Age"].iloc[i]): 

    print("Processing {0}, {1}/{2}...".format(paths[ids].iloc[i], i + 1, count))

    # Loop for each image type
    for name in imageNames:        

      # Load image from file
      filePath = directory + "/" + paths[name].iloc[i]
      img = sitk.ReadImage(filePath)
      img = sitk.Cast(img, sitk.sitkFloat32)
      imgMask = sitk.BinaryNot(sitk.BinaryThreshold(img, 0, 0))
      
      if args.n4:
        img = sitk.N4BiasFieldCorrection(img, imgMask)
      
      if args.norm:
        img = sitk.Normalize(img)

      csvPath = os.path.dirname(paths[name].iloc[i])       

      # Write filepath back to csv
      paths.at[i, name + ending] = csvPath + "/" + name + ending + ext
 
      if name is "T1":
        paths.at[i, "preprocess_roi"] = csvPath + "/roi" + ext
        sitk.WriteImage(imgMask, directory + "/" + csvPath + "/"  + "roi" + ext)
        print("Created binary mask") 

      # Write corrected image to new file
      newFilePath = directory + "/" + csvPath + "/" + name + ending + ext
      sitk.WriteImage(img, newFilePath)
      print("  Created file at {0}".format(newFilePath))

  else:

    print("Skipping {0}, {1}/{2}".format(paths[ids].iloc[i], i + 1, count))

# Write back to csv
paths.to_csv(args.file, index = False)
