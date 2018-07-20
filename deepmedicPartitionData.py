# Partitions BraTS data into training, validation, and testing sets
#
# Notes:
#   Partitioning is done by generating a random number [0,1] for each
#     patient and checking which sets' proportional range it falls in.
#     As a result, set proportions may not be exact.
#
# Input/Args:
#   Usage:
#     $ python deepmedicPartitionData.py -f paths.csv [optional args
#
#   Args:
#     --file, -f [FILE]  path to csv file of filepaths to read from
#     --type, -t [TYPE]  types to consider [HGG, LGG, VAL, TEST, all]
#                        Default: None
#                        If None, HGG/LGG cases are used in training set
#                                 VAL cases used in val set
#                                 TEST cases used in test set
#                                 train/val/test args ignored
#                        If all, only LGG/HGG cases are considered and will
#                                be partitioned with train/val/test args
#                        If HGG, LGG, VAL, or TEST
#                                only those cases will be considered and
#                                partitioned with train/val/test args
#     --directory -f [DIRECTORY]
#                        Optional directory to place outpus files in
#                        Default: places in current directory
#     --train [0,1]      Args to specify ratio of data in each set
#     --val [0,1]          Sum of train, val, test args cannot be greater than
#     --test [0,1]         1.
#
# Output:
#   For each set in [train, val, test] creates a text file corresponding to
#     each channel containing paths to the relevant files.
#   For val and test, a _pred.txt file is created with a list of prediction
#     filenames corresponding to each patient in the val and test sets 

import pandas as pd
import random, argparse, os

# Get params from cmd line
parser = argparse.ArgumentParser(description = "Partition filepaths into " + 
    "text files for deepmedic")
parser.add_argument("--file", "-f", help = "CSV with filepaths",
      required = True)
parser.add_argument("--type", "-t", default = None,
      help = "Type [HGG, LGG, VAL, TEST, all] in csv file to use\n" +
             "Note: 'all' just includes HGG/LGGi." +
             "If --type not specified, HGG/LGG used in train and " +
             "VAL and TEST are used for val and test respectively")
parser.add_argument("--directory", "-d", default = "",
      help = "Directory to place output files in")
parser.add_argument("--train", default = 0, type = float,
      help = "Ratio [0,1] of cases to put in train set")
parser.add_argument("--val", default = 0, type = float,
      help = "Ratio [0,1] of cases to put in validation set")
parser.add_argument("--test", default = 0, type = float,
      help = "Ratio [0,1] of cases to put in test set")
args = parser.parse_args()

# Check if sum of ratios is greater than 1
if args.train + args.test + args.val > 1.0:
  sys.exit("Error: Sum of ratios train, val, and test cannot be greater that 1")

# Directory of image files, not to be confused with directory to place output
# files in
directory = os.path.dirname(args.file)

# Channels of files to make
channels = ["dm_T1_znorm", "dm_T2_znorm", "dm_T1C_znorm", "dm_FLAIR_znorm", 
"seg", "dm_roi_mask"]
ch_range = range(len(channels))

# Format directory and make sure it exists
if args.directory[-1] is not "/":
  args.directory = args.directory + "/"
if not os.path.isdir(args.directory):
  os.makedirs(args.directory)

# Open all files
train_files = [open(args.directory + "train_" + channels[i] + 
        ".txt", "w") for i in ch_range]
val_files = [open(args.directory + "val_" + channels[i] + 
        ".txt", "w") for i in ch_range]
test_files = [open(args.directory + "test_" + channels[i] + 
        ".txt", "w") for i in ch_range]
val_pred = open(args.directory + "val_pred.txt", "w")
test_pred = open(args.directory + "test_pred.txt", "w")

# Read in filenames csv as pandas data frame
fp = pd.read_csv(args.file, sep=",")

if args.type is None:
  # For each patient in the data frame
  for i in range(len(fp.index)):
    split = fp["type"].iloc[i]
    if split == "HGG" or split == "LGG":
      for j in ch_range:
        train_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
    elif split == "VAL":
      for j in ch_range:
        val_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
      val_pred.write(fp["BraTS18ID"].iloc[i] + "_pred.nii.gz" + "\n")
    elif split == "TEST":
      for j in ch_range:
        test_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
      test_pred.write(fp["BraTS18ID"].iloc[i] + "_pred.nii.gz" + "\n")

elif args.type == "all":
  # For each patient in the data frame
  for i in range(len(fp.index)):
    if fp["type"].iloc[i] == "HGG" or fp["type"].iloc[i] == "LGG":
      # Generate random number and see which range it is in
      # Then write path of each channel to corresponding text file
      # If val or test set, also create a new filename for a prediction
      # output from the neural network
      split = random.random()
      if split < args.train:
        for j in ch_range:
          train_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
      elif split < args.train + args.val:
        for j in ch_range:
          val_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
        val_pred.write(fp["BraTS18ID"].iloc[i] + "_pred.nii.gz" + "\n")
      elif split < args.train + args.val + args.test:
        for j in ch_range:
          test_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
        test_pred.write(fp["BraTS18ID"].iloc[i] + "_pred.nii.gz" + "\n")

else:
  # For each patient in the data frame
  for i in range(len(fp.index)):
    if fp["type"].iloc[i] == args.type:
      # Generate random number and see which range it is in
      # Then write path of each channel to corresponding text file
      # If val or test set, also create a new filename for a prediction
      # output from the neural network
      split = random.random()
      if split < args.train:
        for j in ch_range:
          train_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
      elif split < args.train + args.val:
        for j in ch_range:
          val_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
        val_pred.write(fp["BraTS18ID"].iloc[i] + "_pred.nii.gz" + "\n")
      elif split < args.train + args.val + args.test:
        for j in ch_range:
          test_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
        test_pred.write(fp["BraTS18ID"].iloc[i] + "_pred.nii.gz" + "\n")
     else:
       sys.exit("Error: Type: '" + args.type + "' not found in file")
