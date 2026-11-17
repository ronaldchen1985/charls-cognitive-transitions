# Sensitivity: multiple imputation of covariates (drink, stroke18, cesd10),
# then repeat baseline-state-stratified multinomial models and pool via Rubin's rules.
library(mice); library(nnet)
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
imp <- mice(di0, m = 20, maxit = 20, method = meth, printFlag = FALSE)

mvars <- c("agez","female","edu4","married","drink","htn","dm","heart","stroke18","stroke_inc","cesd10")
fml <- outcome ~ agez + female + edu4 + married + drink + htn + dm + heart + stroke18 + stroke_inc + cesd10

est <- list(); ses <- list()
for (i in 1:20) {
  di <- complete(imp, i)
  di$stroke_inc[di$stroke18 == "1"] <- factor("0", levels = c("0","1"))
  for (s in c("Normal","CIND","Dementia")) {
    ds <- di[di$state18f == s, ]
    ds$outcome <- relevel(droplevels(ds$outcome), ref = s)
    m <- multinom(fml, data = ds, trace = FALSE)
    co <- coef(m); se <- summary(m)$standard.errors
    for (r in rownames(co)) for (cn in colnames(co)) {
      nm <- paste(s, r, cn, sep = "|")
      est[[nm]] <- c(est[[nm]], co[r, cn])
      ses[[nm]] <- c(ses[[nm]], se[r, cn])
    }
  }
}
m <- 20
rows <- list()
for (nm in names(est)) {
  q <- est[[nm]]; u <- ses[[nm]]^2
  qbar <- mean(q); ubar <- mean(u); b <- var(q)
  tv <- ubar + (1 + 1/m) * b
  se <- sqrt(tv)
  parts <- strsplit(nm, "\\|")[[1]]
  rows[[nm]] <- data.frame(baseline = parts[1], outcome = parts[2], covariate = parts[3],
    RRR = round(exp(qbar), 3), L = round(exp(qbar - 1.96*se), 3),
    U = round(exp(qbar + 1.96*se), 3), p = round(2*pnorm(-abs(qbar/se)), 4))
}
mi <- do.call(rbind, rows); rownames(mi) <- NULL
write.csv(mi, file.path(OUT, "mi_rrr.csv"), row.names = FALSE)

sink(file.path(OUT, "mi_results.txt"), split = TRUE)
cat("MI sensitivity (m=20): pooled RRRs, key parameters\n")
cc <- read.csv(file.path(OUT, "multinom_rrr.csv"))
keycov <- c("stroke181","stroke_inc1")
k <- mi[mi$covariate %in% keycov, ]
cat("\n== MI pooled (stroke) ==\n"); print(k)
cat("\n== Complete-case (stroke) ==\n"); print(cc[cc$covariate %in% keycov, ])
cat("\n== MI pooled: reversion predictors (baseline CIND -> Normal) ==\n")
print(mi[mi$baseline=="CIND" & mi$outcome=="Normal" & mi$covariate %in% c("agez","married1"), ])
sink()
cat("DONE\n")
