# BratsUtils

This repo contains various helper scripts for managing BraTS Challenge Data.

### Create File Paths

`$ python createFilePaths.py -f csvfilewithids.csv [optional args]`

**Optional Arguments**
**`--id`, `-i` [ID]**
  - Name of column in csv file with IDs
  - Default = "BraTS18ID"
**`--type`, `-t` [TYPE]**
  - Name of column is csv file with types (i.e HGG, LGG, etc.)
  - Default = "type"
**`--directory`, `-d` [DIRECTORY]**
  - Directory to place output csv in
  - Default = directory of input csv file
**`--name`, `-n` [NAME]**
  - Name of output csv file
  - Default = name of input csv file
**`--overwrite`, `-o`**
  - Flag if specified will overwrite the input csv file. Only used if `--directory` and `--name` are not specified
  - Default = False, i.e will not overwrite input csv file and will append "_with_paths" to name
**`--excel`, `-e`**
  - Flag if specified will also create a .xlsx file with a column for viewer scripts
  - Default = False, i.e. if not specified, only the csv file will be created

**Example**
`$ python createFilePaths.py -f /home/user/csvfilewithids.csv -d /home/user -n newfile.csv -e`
This will create teh following files: `/home/user/newfile.csv` and `/home/user/newfile.xlsx`

**Additional Notes**
To change the path columns that the script generates, modify the `columnPathPairs` variable.
`columnPathPairs` is a list of sublists of length 2.
Each of these sublists is of the format ["COLUMN_NAME", "PATH_APPEND"] where COLUMN_NAME is used as the title of the new column in the file and PATH_APPEND is the corresponding string appended to all the paths in that column.

### DeepMedic Helper Scripts
