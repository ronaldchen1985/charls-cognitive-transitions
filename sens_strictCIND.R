library(nnet); library(msm)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
cov <- read.csv(file.path(OUT, "covariates_strictCIND.csv"), stringsAsFactors=FALSE)
d <- cov[!is.na(cov$state18), ]
d$died <- d$died %in% c("True","TRUE",TRUE,1)
d$agez <- as.numeric(scale(d$age18))
d$outcome <- d$state6; d$outcome[is.na(d$outcome) & d$died] <- 4
d <- d[!is.na(d$outcome), ]
d$outcome <- factor(d$outcome, levels=1:4, labels=c("Normal","CIND","Dementia","Death"))
d$state18f <- factor(d$state18, levels=1:3, labels=c("Normal","CIND","Dementia"))
for (v in c("female","married","drink","htn","dm","heart","stroke18","stroke_inc","cesd10")) d[[v]] <- factor(d[[v]])
d$edu4 <- factor(d$edu4)
mvars <- c("agez","female","edu4","married","drink","htn","dm","heart","stroke18","stroke_inc","cesd10")
d <- d[complete.cases(d[, mvars]), ]
sink(file.path(OUT, "strictCIND_results.txt"), split=TRUE)
cat("STRICT CIND: N =", nrow(d), "\n")
print(table(d$state18f, d$outcome))
print(round(prop.table(table(d$state18f, d$outcome),1)*100,1))
for (s in c("Normal","CIND")) {
  ds <- d[d$state18f==s, ]
  ds$outcome <- relevel(droplevels(ds$outcome), ref=s)
  m <- multinom(outcome ~ agez + female + edu4 + married + drink + htn + dm + heart +
                stroke18 + stroke_inc + cesd10, data=ds, trace=FALSE)
  sm <- summary(m)
  for (lev in rownames(sm$coefficients)) {
    est <- sm$coefficients[lev,]; se <- sm$standard.errors[lev,]
    for (cv in c("stroke181","stroke_inc1")) {
      cat(sprintf("base=%s out=%s %s RRR=%.2f (%.2f-%.2f) p=%.4f\n", s, lev, cv,
                  exp(est[cv]), exp(est[cv]-1.96*se[cv]), exp(est[cv]+1.96*se[cv]),
                  2*pnorm(-abs(est[cv]/se[cv]))))
    }
  }
}
# null msm on strict states
rows <- list()
for (i in 1:nrow(d)) {
  r <- d[i, ]
  if (!is.na(r$t18)) rows[[length(rows)+1]] <- c(r$ID, max(r$t18,0), as.numeric(r$state18f))
  if (r$died) {
    td <- ifelse(!is.na(r$t6), max((r$t6+6)/2, r$t6+0.1), (r$t18+5.5)/2)
    rows[[length(rows)+1]] <- c(r$ID, td, 4)
  } else if (!is.na(r$state6) && !is.na(r$t6)) {
    rows[[length(rows)+1]] <- c(r$ID, r$t6, as.numeric(droplevels(factor(r$state6))))
  }
}
pan <- as.data.frame(do.call(rbind, rows)); names(pan) <- c("ID","time","state")
pan$time <- as.numeric(pan$time); pan$state <- as.numeric(pan$state)
pan <- pan[order(pan$ID, pan$time), ]
pan <- pan[!duplicated(pan[,c("ID","time")], fromLast=TRUE), ]
nper <- ave(pan$state, pan$ID, FUN=length); pan <- pan[nper>=2, ]
fs <- ave(pan$state, pan$ID, FUN=function(x)x[1]); pan <- pan[fs!=4, ]
cat("strict panel persons:", length(unique(pan$ID)), "\n")
Qtpl <- rbind(c(0,.1,.01,.05), c(.1,0,.05,.1), c(0,.05,0,.2), c(0,0,0,0))
ids <- unique(pan$ID)
mc <- msm(state~time, subject=ID, data=pan[pan$ID %in% ids[1:1000],],
          qmatrix=crudeinits.msm(state~time, ID, data=pan, qmatrix=Qtpl))
Qi <- qmatrix.msm(mc)$estimates; diag(Qi)<-0; diag(Qi)<--rowSums(Qi)
m0s <- msm(state~time, subject=ID, data=pan, qmatrix=Qi, control=list(maxit=5000))
cat("\nSTRICT CIND null msm Q:\n"); print(qmatrix.msm(m0s))
cat("\n5y P:\n"); print(pmatrix.msm(m0s, t=5))
sink()
cat("DONE\n")
