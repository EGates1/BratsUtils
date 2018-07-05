# Partitions BraTS data into training, validation, and testing sets
#
# Notes:
#   No command line interface yet, all variables must be set in the script
#   Partitioning is done by generating a random number [0,1] for each
#     patient and checking which sets' proportional range it falls in.
#     As a result, set proportions may not be exact.
#
# Input:
#   directory = path to directory containing HGG and LGG directories
#   output    = directory to create output text files in
#   filepaths = csv containing paths to each nii file per patient
#               Assumes csv file contains the following columns: 
#                   BraTS18ID = patient ID
#                   ResectionStatus = is there a ground truth file
#                                     all patients w/o ground truth are ignored
#                   channels = see channels below 
#   channels  = list of column names in filepaths corresponding to each
#               imaging feature to create a text file for
#   [train, val, test]_split = proportion of patients to partition into
#                              each category. E.g. val_split = 0.2 means
#                              20% of the patients will be used in the
#                              validation set
#
# Output:
#   For each set in [train, val, test] creates a text file corresponding to
#     each channel containing paths to the relevant files.
#   For val and test, a _pred.txt file is created with a list of prediction
#     filenames corresponding to each patient in the val and test sets 

import pandas as pd
import random

directory = "/rsrch1/ip/jgpauloski/BraTS_Data/MICCAI_BraTS_2018_Data_Training/"
output = ""
filepaths = "../BraTS_Data/MICCAI_BraTS_2018_Data_Training/BraTS18_filepaths.csv"
channels = ["T1", "T2", "T1C", "FLAIR", "seg"]
ch_range = range(len(channels))
train_split = 0.9
val_split = 0.05
test_split = 0.05

# Open all files
train_files = [open(output + "train_" + channels[i] + 
        ".txt", "w") for i in ch_range]
val_files = [open(output + "val_" + channels[i] + 
        ".txt", "w") for i in ch_range]
test_files = [open(output + "test_" + channels[i] + 
        ".txt", "w") for i in ch_range]
val_pred = open(output + "val_pred.txt", "w")
test_pred = open(output + "test_pred.txt", "w")

# Read in filenames csv as pandas data frame
fp = pd.read_csv(filepaths, sep=",")

# For each patient in the data frame
for i in range(len(fp.index)):
    # Check if patient has a ground truth file. Else skip patient
    if ((fp["ResectionStatus"].iloc[i] == "GTR") or 
            (fp["ResectionStatus"].iloc[i] == "STR")):
        # Generate random number and see which range it is in
        # Then write path of each channel to corresponding text file
        # If val or test set, also create a new filename for a prediction
        # output from the neural network
        split = random.random()
        if split < train_split:
            for j in ch_range:
                train_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
        elif split < val_split + train_split:
            for j in ch_range:
                val_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
            val_pred.write(fp["BraTS18ID"].iloc[i] + "/" + 
                    fp["BraTS18ID"].iloc[i] + "_pred.nii.gz" + "\n")
        elif split < test_split + val_split + train_split:
            for j in ch_range:
                test_files[j].write(directory + fp[channels[j]].iloc[i] + "\n")
            test_pred.write(fp["BraTS18ID"].iloc[i] + "/" +
                    fp["BraTS18ID"].iloc[i] + "_pred.nii.gz" + "\n")
