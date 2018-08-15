# Call normalization parts of neuroimage pipeline to normalize images and create masks for brain/tumor/nontumor
#
# Requires segmentations ('seg') to be present
#
# Usage:
#   $ Rscript pyradiomics_to_short.R pyradiomicsout.csv pyradiomicsout_SHORT.csv suffix ID1 ID2 ID3 ...
#
#
#  Command line args
#     pyradiomicsout.csv       Name of csv file pyradiomics output (Image,
#                                Mask, label) and other feature columns
#     pyradiomicsout_SHORT.csv Name of output shortened matrix
#     suffix                   Image type is assumed to be everything between
#                                 the last _ and suffix
#                                   (default: .nii.gz)
#     ID[X]                    Strings with column names that identify
#                                unique cases (ex: MRN, age)
#                                  (default: use each image as one case)
#
# Sample ID vectors:
# BraTS18 validation
#IDs <- c("BraTS18ID","Mask","masktype","Image","imagetype","fulltype","Label", "ResectionStatus","Age","type")
# Command line:
# Rscript pyradiomics_to_short.R BraTS18_validation_pyradiomicsout.csv testSHORT.csv _NLM.nii.gz BraTS18ID Age ResectionStatus type


options(error = quote({dump.frames(to.file=TRUE);q()}))
require(reshape2)

args <- commandArgs( trailingOnly = TRUE )
print("args:")
print(args)
print("=========================================")
if( length( args ) < 2 )
  {
  cat("Supply at least two arguments with in/out csv filepaths")
  stopQuietly()
  }

csvName <- args[1]
outcsvName <- args[2]


if( length(args) > 2){
  suffix = args[3]
  } else {
  suffix = '.nii.gz'
  }

if( length(args) > 3){
  IDs <- args[4:length(args)]
  } else {
  IDs <- "Image"
  } 

# validation/testing data:
# csvName <- "BraTS18_pyradiomicsout_validation_combined_firstorder.csv"
# csvName <- "BraTS18_pyradiomicsout_testing_GTRonly_nopath_flairnonenhonly.csv"
d1 <- read.csv(csvName)

if( any(! (IDs %in% names(d1))) ){
    print("One or more ID variables is not a column name")
  print(IDs[!(IDs %in% names(d1))])

  stop("Remove that column name from your command")
  }



# Pyradiomics features
feats <- grep("(general_info_VoxelNum|_firstorder_|_shape_|_glcm_|_glrlm_|_ngtdm_|_glszm_|_gldm_)",names(d1),value=T)

#extracts t1ce,flair,etc
#d1$imagetype <- sub('.nii.gz','',sub(".*_","",d1$Image))

# get repeat image types by removing suffix (like _NLM.nii.gz) and beginning stuff.
d1$imagetype <- sub(".*_","",sub(suffix,"",d1$Image))

# rename labels 1=, 2=
# This is mosty specific for BraTS data
# replace 'nonenh', 'edema' etc with project specific names or just "Label1"
d1$masktype <- "mask"

d1[grepl("tumor",d1$Mask), "masktype"] <- "tumor"


d1[which( grepl("atropos",d1$Mask) & (d1$Label ==1) ),"masktype"] <- "atropos_csf"
d1[which( grepl("atropos",d1$Mask) & (d1$Label ==2) ),"masktype"] <- "atropos_gm"
d1[which( grepl("atropos",d1$Mask) & (d1$Label ==3) ),"masktype"] <- "atropos_wm"

d1[which( grepl("tissue",d1$Mask) & (d1$Label ==1) ),"masktype"] <- "tissue_csf"
d1[which( grepl("tissue",d1$Mask) & (d1$Label ==2) ),"masktype"] <- "tissue_gm"
d1[which( grepl("tissue",d1$Mask) & (d1$Label ==3) ),"masktype"] <- "tissue_wm"

d1[which( grepl("seg",d1$Mask) & (d1$Label ==1) ),"masktype"] <- "nonenh"
d1[which( grepl("seg",d1$Mask) & (d1$Label ==2) ),"masktype"] <- "edema"
d1[which( grepl("seg",d1$Mask) & (d1$Label ==4) ),"masktype"] <- "enhanc"

d1[which( grepl("Grade",d1$Mask) & (d1$Label ==1) ),"masktype"] <- "normal"
d1[which( grepl("Grade",d1$Mask) & (d1$Label ==2) ),"masktype"] <- "lower"
d1[which( grepl("Grade",d1$Mask) & (d1$Label ==3) ),"masktype"] <- "higher"

#get unique regions by combining image and mask type
d1$fulltype <- paste(d1$imagetype,d1$masktype,sep="_")



# Add image types to ID vector
#print(names(d1))

longIDs <- union(IDs, c("Mask","masktype","Image","imagetype","fulltype","Label"))

#print("")
#print(longIDs)
#print(longIDs %in% names(d1))
#IDs <- c("BraTS18ID","Mask","masktype","Image","imagetype","fulltype","Label", "ResectionStatus","Age","type")

#TODO melt matrix then dcast
#TODO don't remove extra columns?
cropMatrix <- d1[,c(longIDs,feats)]

longMatrix <- melt(cropMatrix,id.vars=longIDs)
longMatrix$variable <- paste(longMatrix$fulltype,longMatrix$variable,sep="_")

# top: BraTS17. bottom atropos_tissue
#dcastIDs <- c("ID","survival","age","type")
#dcastIDs <- c("ID")

#validation data example
# dcastIDs <- c("BraTS18ID","Age","type")
dcastIDs <- IDs

longMatrixCrop <- longMatrix[,c(dcastIDs,"variable","value")]
shortMatrix <- dcast(data=longMatrixCrop,formula=as.formula(paste(paste(dcastIDs,collapse="+"),"~ variable")), value.var = "value")


#Disabled: remove redundant shapes
# Rename t1 shape features and remove redundant shape features

##t1shapes <- grep("flair_.*_shape_",names(shortMatrix),value=F)
##renamedShapes <- sub("flair_","mask_",names(shortMatrix)[t1shapes])
##
###rename t1 shapes
##names(shortMatrix)[t1shapes] <- renamedShapes
##
###remove others
##extraShapes <- setdiff( grep("_shape_",names(shortMatrix),value=T), renamedShapes)
##shortMatrix[,extraShapes] <- NULL

#scale volume by 1/10000 to make it similar to means for BraTS data
##volumefeats <- grep('_Volume$', names(shortMatrix),value=T)
##shortMatrix[,volumefeats] <- (shortMatrix[,volumefeats]*1/10000)
##diamfeats <- grep('DDiameter', names(shortMatrix),value=T)

##shortMatrix[,diamfeats] <- (shortMatrix[,diamfeats]*1/100)



write.csv(shortMatrix,outcsvName,row.names=F)







