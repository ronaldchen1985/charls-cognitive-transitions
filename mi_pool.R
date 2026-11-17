# Step 2: fit stratified multinom on each imputed dataset; pool with Rubin's rules.
library(mice); library(nnet)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
imp <- readRDS(file.path(OUT, "mi_imp.rds"))
fml <- outcome ~ agez + female + edu4 + married + drink + htn + dm + heart + stroke18 + stroke_inc + cesd10
est <- list(); ses <- list()
for (i in 1:20) {
  di <- complete(imp, i)
  di$stroke_inc[di$stroke18 == "1"] <- factor("0", levels = c("0","1"))  # structural constraint
  for (s in c("Normal","CIND","Dementia")) {
    ds <- di[di$state18f == s, ]
    ds$outcome <- relevel(droplevels(ds$outcome), ref = s)
    mfit <- multinom(fml, data = ds, trace = FALSE)
    co <- coef(mfit); se <- summary(mfit)$standard.errors
    for (r in rownames(co)) for (cn in colnames(co)) {
      nm <- paste(s, r, cn, sep = "|")
      est[[nm]] <- c(est[[nm]], co[r, cn])
      ses[[nm]] <- c(ses[[nm]], se[r, cn])
    }
  }
  cat("imp", i, "done\n")
}
m <- 20
rows <- list()
for (nm in names(est)) {
  q <- est[[nm]]; u <- ses[[nm]]^2
  qbar <- mean(q); ubar <- mean(u); b <- var(q)
  se <- sqrt(ubar + (1 + 1/m) * b)
  parts <- strsplit(nm, "\\|")[[1]]
  rows[[nm]] <- data.frame(baseline = parts[1], outcome = parts[2], covariate = parts[3],
    RRR = round(exp(qbar), 3), L = round(exp(qbar - 1.96*se), 3),
    U = round(exp(qbar + 1.96*se), 3), p = round(2*pnorm(-abs(qbar/se)), 4))
}
mi <- do.call(rbind, rows); rownames(mi) <- NULL
write.csv(mi, file.path(OUT, "mi_rrr.csv"), row.names = FALSE)
sink(file.path(OUT, "mi_results.txt"), split = TRUE)
cat("MI sensitivity (m=20): pooled RRRs\n")
cc <- read.csv(file.path(OUT, "multinom_rrr.csv"))
keycov <- c("stroke181","stroke_inc1")
cat("\n== MI pooled (stroke) ==\n"); print(mi[mi$covariate %in% keycov, ])
cat("\n== Complete-case (stroke) ==\n"); print(cc[cc$covariate %in% keycov, ])
cat("\n== MI pooled: reversion predictors (baseline CIND -> Normal) ==\n")
print(mi[mi$baseline=="CIND" & mi$outcome=="Normal" & mi$covariate %in% c("agez","married1"), ])
sink()
cat("DONE\n")
