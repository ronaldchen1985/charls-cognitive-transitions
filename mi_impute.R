# Step 1: build panel frame and run mice imputation; save mids object.
library(mice)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
cov <- read.csv(file.path(OUT, "covariates.csv"), stringsAsFactors=FALSE)
d <- cov[!is.na(cov$state18), ]
d$died <- d$died %in% c("True", "TRUE", TRUE, 1)
d$agez <- as.numeric(scale(d$age18))
d$outcome <- d$state6
d$outcome[is.na(d$outcome) & d$died == TRUE] <- 4
d <- d[!is.na(d$outcome), ]
d$outcome <- factor(d$outcome, levels = 1:4, labels = c("Normal","CIND","Dementia","Death"))
d$state18f <- factor(d$state18, levels = 1:3, labels = c("Normal","CIND","Dementia"))
for (v in c("female","married","drink","htn","dm","heart","stroke18","stroke_inc","cesd10")) d[[v]] <- factor(d[[v]])
d$edu4 <- factor(d$edu4)
cat("Panel N for MI:", nrow(d), "\n")
impvars <- c("state18f","outcome","agez","female","edu4","married","drink","htn","dm","heart","stroke18","stroke_inc","cesd10")
di0 <- d[, impvars]
meth <- make.method(di0); meth[c("drink","stroke18","cesd10")] <- "logreg"
meth[setdiff(names(meth), c("drink","stroke18","cesd10"))] <- ""
set.seed(20261117)
imp <- mice(di0, m = 20, maxit = 10, method = meth, printFlag = FALSE)
saveRDS(imp, file.path(OUT, "mi_imp.rds"))
cat("IMPUTE DONE\n")
