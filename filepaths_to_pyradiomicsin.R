
#takes filepaths and makes pyradiomics input files
require(reshape2)

#Currently hard coded for testing data "TST"
csvPath <- "BraTS18_filepaths_testing.csv"

#need headings: BraTS18ID,  type, ResectionStatus, Age, and filepaths (T1, T2, T1C, FLAIR)
dat <- read.csv("csvPath")
dat <- dat[dat$type=="VAL" & !is.na(dat$ResectionStatus) & dat$ResectionStatus =="GTR" , ]


IDvars <- c("BraTS18ID","type","Age","ResectionStatus")

labelmerge <- data.frame(image=c(rep("seg",3), "tumor"), Label = c(1,2,4,1)

datmelt <- melt(dat[,c(IDvars,"T1","T2","T1C","FLAIR","seg","tumor")], id.vars = c(IDvars,"seg","tumor"), value.name = "Image")
datmelt$variable <- NULL

datmelt2 <- melt(datmelt, id.vars = c(IDvars,"Image"),value.name = "Mask")


datmerge <- merge(datmelt2, labelmerge, by.x = "variable", by.y = "Image")
datmerge$variable <- NULL

#make NLM filepaths not regular

if(!any(grepl("NLM", datmerge$Image))){
  datmerge$Image <- sub(".nii.gz","_NLM.nii.gz",datmerge$Image)


write.csv(datmerge, "BraTS18_pyradiomicsin_testing_NLM.csv",row.names=F)

