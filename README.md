# BratsUtils

This repo contains various helper scripts for managing BraTS Challenge Data.

## Create File Paths

### Usage
 
`$ python createFilePaths.py -f csvfilewithids.csv [optional args]`

**Optional Arguments**

Use `$ python createFilePaths.py --help` to see arguments.

`--id, -i [ID]`

  - Name of column in csv file with IDs
  - Default = "BraTS18ID"

`--type, -t [TYPE]`

  - Name of column is csv file with types (i.e HGG, LGG, etc.)
  - Default = "type"

`--directory, -d [DIRECTORY]`

  - Directory to place output csv in
  - Default = directory of input csv file

`--name, -n [NAME]`

  - Name of output csv file
  - Default = name of input csv file

`--overwrite, -o`

  - Flag if specified will overwrite the input csv file. Only used if `--directory` and `--name` are not specified
  - Default = False, i.e will not overwrite input csv file and will append "_with_paths" to name

`--excel, -e`

  - Flag if specified will also create a .xlsx file with a column for viewer scripts
  - Default = False, i.e. if not specified, only the csv file will be created

**Example**

`$ python createFilePaths.py -f /home/user/csvfilewithids.csv -d /home/user -n newfile.csv -e`

This will create the following files: `/home/user/newfile.csv` and `/home/user/newfile.xlsx`

### Additional Notes

To change the path columns that the script generates, modify the `columnPathPairs` variable.
`columnPathPairs` is a list of sublists of length 2.
Each of these sublists is of the format ["COLUMN_NAME", "PATH_APPEND"] where COLUMN_NAME is used as the title of the new column in the file and PATH_APPEND is the corresponding string appended to all the paths in that column.

Dependencies: pandas

## DeepMedic Helper Scripts

### deepmedicPreprocess.py

Uses output csv file from `createFilePaths.py` as input. 
Normalizes images and create roi mask. 
To edit what image files are preprocessed, edit the `imageNames` list with columns in the csv to process.

**Usage**

`$ python deepmedicPreprocess.py -f csvwithfilepaths.py`

See comment at the top of the script for additional arguments.

### deepmedicPartitionData.py

Creates text files of filepaths to images as required by DeepMedic.
Uses output csv from `createFilePaths.py` as input.
By default uses the normalized images + masks from `deepmedicPreprocess.py`.
See `channels` list in the script to edit what images are used.

**Usage**

`$ python deepmedicPartitionData.py -f csvwithfilepaths.py`

See comment at the top of the script for additional arguments.
Includes options to specify what types of cases (HGG, LGG, etc.) are used, output directories, and train/val/test splits.

### Build TensorFlow from Source

`build_tensorflow_from_source.txt` contains the steps used to build a custom version of tensorflow for CPUs that do not support AVX and therefore cannot use TensorFlow >1.5.
Note: finding versions of gcc, CUDA, Cudnn, and Nvidia drivers that work together can be difficult so you may have to try multiple times.
I found that gcc 5, CUDA 9.1, Cudnn 7.1, and the lastest Nvidia driver worked. The text file also contains multiple links to the references I used. Be sure to read those as well.
