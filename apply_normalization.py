# Call normalization parts of neuroimage pipeline to normalize images and create masks for brain/tumor/nontumor
#
# Requires segmentations ('seg') to be present
#
# Usage:
#   $ python apply_normalization.py -f BraTS18_filepaths.csv -i BraTS18ID
#
# Uses the same file structure as createFilePaths.py
#
#   Optional command line args
#      --file, -f             Name of csv file with filepaths, needs
#                               at least 'T1', 'seg', 'tumor', and 'mask'
#                               columns
#      --id, -i [ID]          Name of column in csv file with IDs 
#                               (default = BraTS18ID)
#      --atropos, -a          Logical (True/False) whether or not to run
#                                automatic gray/white/csf segmentation
#                                for tissue labels, requires T2, FLAIR
#                                images and 'atropos' column
#                                  (default = False)

import os
import argparse
import csv
import sys

sys.path.append('/rsrch1/ip/egates1/github/RadPath/Code/Neuroimage_Pipeline')

from Segmodule import *

# Get params from cmd line
# Default don't include overwrite option
parser = argparse.ArgumentParser(description = "Normalizes images based on filepath csv")
parser.add_argument("--file", "-f", help = "CSV with IDs", 
      required = True) 
parser.add_argument("--id", "-i", default = "BraTS18ID", 
      help = "Name of column with IDs")
#parser.add_argument("--overwrite", "-o", action = "store_true",
#      help = "Overwrite given csv of IDs")
parser.add_argument("--atropos", "-a", default = False,
      help = "Option to run Atropos auto tissue segmentation")
args = parser.parse_args()

print(os.getcwd())
IDvar = args.id
csvPath = args.file
with open(csvPath,'r') as csvData:
  csvR = csv.DictReader(csvData)

  for row in csvR:
    outdir = '/'.join([row['type'],row[IDvar]])
    
#create mask if it doesn't exist already
    t1path = row['T1']
    maskpath = row['mask']
    segpath = row['seg']
    tumorpath = row['tumor']
    c3dcmd = 'c3d %s -background 0 -binarize -type uchar -o %s' % (t1path, maskpath)
    if not os.path.isfile(maskpath):
      print(c3dcmd)
      os.system(c3dcmd)

    c3dcmd2 = 'c3d %s -background -0 -binarize -type uchar -o %s' % (segpath, tumorpath)
    if not os.path.isfile(tumorpath):    
      print(c3dcmd2)
      os.system(c3dcmd2)

#Apply ATROPOS to non-tumor tissues
    nontumorpath = row['nontumor']
    atroposname = row['atropos']
    c3dcmd3 = 'c3d %s %s -scale -1 -add -threshold 1 1 1 0 -type uchar -o %s' % (maskpath, tumorpath, nontumorpath)
      if not os.path.isfile(nontumorpath):
        print(c3dcmd3)
        os.system(c3dcmd3)

    if args.atropos:
      FLpath = row['FLAIR']
      t2path = row['T2']
      atroposname = row['atropos']
      atroposcmd = '/opt/apps/ANTsR/dev//ANTsR_src/ANTsR/src/ANTS/ANTS-build//bin/Atropos -d 3 -c [5,0.001] -m [0.2,1x1x1] -i kmeans[3] -x %s -a %s %s %s -o %s' % (nontumorpath, t1path, t2path, FLpath, atroposname)
      if not os.path.isfile(atroposname):
        print(atroposcmd)
        os.system(atroposcmd)

# Apply landmark normalization, will also check for tumor masks
    segment_and_normalize(csv_path = csvPath, output_directory = outdir, ptMRN = row[IDvar], baseline_image= 'T1')


