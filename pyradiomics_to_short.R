
#TODO make this work for combining different pyradiomics outputs

require(reshape2)

##load data, get features

# hard coded testing data:
csvName <- "BraTS18_pyradiomicsout_testing.csv"
d1 <- read.csv(csvName)

feats <- grep("(general_info_VoxelNum|_firstorder_|_shape_|_glcm_|_glrlm_|_ngtdm_|_glszm_|_gldm_)",names(d1),value=T)

# for NLM
d1$imagetype <- sub(".*_","",sub("(_RF_POS.nii.gz|_NLM.nii.gz)","",d1$Image))

#rename labels 1=, 2=
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

d1$fulltype <- paste(d1$imagetype,d1$masktype,sep="_")

# BraTS18 validation/testing

IDs <- c("BraTS18ID","Mask","masktype","Image","imagetype","fulltype","Label", "ResectionStatus","Age","type")

#TODO: melt matrix then dcast
cropMatrix <- d1[,c(IDs,feats)]

longMatrix <- melt(cropMatrix,id.vars=IDs)
longMatrix$variable <- paste(longMatrix$fulltype,longMatrix$variable,sep="_")

#validation/testing data
dcastIDs <- c("BraTS18ID","Age","type")

longMatrixCrop <- longMatrix[,c(dcastIDs,"variable","value")]
shortMatrix <- dcast(data=longMatrixCrop,formula=as.formula(paste(paste(dcastIDs,collapse="+"),"~ variable")), value.var = "value")

#Rename t1 shape features and remove redundant shape features

t1shapes <- grep("t1_.*_shape_",names(shortMatrix),value=F)
renamedShapes <- sub("t1_","mask_",names(shortMatrix)[t1shapes])

#rename t1 shapes
names(shortMatrix)[t1shapes] <- renamedShapes

#remove others
extraShapes <- setdiff( grep("_shape_",names(shortMatrix),value=T), renamedShapes)
shortMatrix[,extraShapes] <- NULL

#scale volume by 1/10000 to make it similar to means
volumefeats <- grep('_Volume$', names(shortMatrix),value=T)
shortMatrix[,volumefeats] <- (shortMatrix[,volumefeats]*1/10000)
diamfeats <- grep('DDiameter', names(shortMatrix),value=T)

shortMatrix[,diamfeats] <- (shortMatrix[,diamfeats]*1/100)

write.csv(shortMatrix,sub(".csv","_SHORT.csv",csvName),row.names=F)







