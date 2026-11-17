library(msm)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
pan <- read.csv(file.path(OUT, "panel_strictCIND.csv"))
pan <- pan[order(pan$ID, pan$time), ]
nper <- ave(pan$state, pan$ID, FUN=length); pan <- pan[nper>=2, ]
fs <- ave(pan$state, pan$ID, FUN=function(x)x[1]); pan <- pan[fs!=4, ]
cat("persons:", length(unique(pan$ID)), "\n")
Qtpl <- rbind(c(0,.1,.01,.05), c(.1,0,.05,.1), c(0,.05,0,.2), c(0,0,0,0))
ids <- unique(pan$ID)
mc <- msm(state~time, subject=ID, data=pan[pan$ID %in% ids[1:1000],],
          qmatrix=crudeinits.msm(state~time, ID, data=pan, qmatrix=Qtpl))
Qi <- qmatrix.msm(mc)$estimates; diag(Qi)<-0; diag(Qi)<--rowSums(Qi)
m0s <- msm(state~time, subject=ID, data=pan, qmatrix=Qi, control=list(maxit=5000))
sink(file.path(OUT, "strictCIND_msm.txt"), split=TRUE)
cat("STRICT CIND null msm, persons:", length(unique(pan$ID)), "\n")
print(qmatrix.msm(m0s))
cat("\n5y P:\n"); print(pmatrix.msm(m0s, t=5))
sink()
cat("DONE\n")
