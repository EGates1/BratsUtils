import argparse, os
import pandas as pd
import SimpleITK as sitk

# Get params from cmd line
parser = argparse.ArgumentParser(description = "Preprocess nii files")
parser.add_argument("--file", "-f", help = "CSV with filepaths", 
      required = True) 
parser.add_argument("-n4", action = "store_true", 
      help = "Apply n4 bias correction. NOTE: Takes a long time")
args = parser.parse_args()

imageNames = ["dm_T1_znorm", "dm_T2_znorm", "dm_T1C_znorm", 
              "dm_FLAIR_znorm", "dm_roi_mask"]

# Get directory of csv file
directory = os.path.dirname(args.file)

# Read csv into pandas dataframe
paths = pd.read_csv(args.file)

# Num subjects in csv
count = len(paths.index)

# Loop for each subject in csv
for i in range(count):
  
  print("Processing subject {1}/{2}...".format(i + 1, count))

  # Loop for each image type
  for name in imageNames:        

    # Load image from file
    filePath = directory + "/" + paths[name].iloc[i]
    img = sitk.ReadImage(filePath)
    img = sitk.Cast(img, sitk.sitkFloat32)
    imgMask = sitk.BinaryNot(sitk.BinaryThreshold(img, 0, 0))
      
    # If specified on cmd line, do n4 bias correction
    if args.n4:
      img = sitk.N4BiasFieldCorrection(img, imgMask)
      
    # Z-score normalize image
    img = sitk.Normalize(img)

    # Create binary path from T1 image
    if name is "T1":
      sitk.WriteImage(imgMask, filePath)
      print("Created binary mask") 

    # Write corrected image to new file
    sitk.WriteImage(img, filepath)
    print("  Created file at {0}".format(newFilePath))

print("Preprocessing and normalization complete")
