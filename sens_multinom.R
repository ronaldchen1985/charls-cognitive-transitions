library(nnet)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
for (cut in c("348","39")) {
  cov <- read.csv(file.path(OUT, paste0("covariates_cut", cut, ".csv")), stringsAsFactors=FALSE)
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
  cat("\n########## CUTOFF", cut, " N =", nrow(d), "##########\n")
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
        cat(sprintf("cut=%s base=%s out=%s %s RRR=%.2f (%.2f-%.2f) p=%.4f\n", cut, s, lev, cv,
                    exp(est[cv]), exp(est[cv]-1.96*se[cv]), exp(est[cv]+1.96*se[cv]),
                    2*pnorm(-abs(est[cv]/se[cv]))))
      }
    }
  }
}
