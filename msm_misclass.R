library(msm)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
panel <- read.csv(file.path(OUT, "analytic_panel.csv"))
panel <- panel[order(panel$ID, panel$time), ]
nper <- ave(panel$state, panel$ID, FUN=length); panel <- panel[nper>=2, ]
fs <- ave(panel$state, panel$ID, FUN=function(x)x[1]); panel <- panel[fs!=4, ]
m0 <- readRDS(file.path(OUT,"m0_null_full.rds"))
Qi <- qmatrix.msm(m0)$estimates; diag(Qi)<-0; diag(Qi)<--rowSums(Qi)
# misclassification: observed state may err to adjacent states (1<->2, 2<->3); death exact
Ei <- rbind(c(0, .05, 0, 0),
            c(.05, 0, .05, 0),
            c(0, .05, 0, 0),
            c(0, 0, 0, 0))
t0 <- Sys.time()
mm <- try(msm(state ~ time, subject=ID, data=panel, qmatrix=Qi, ematrix=Ei,
              est.initprobs=TRUE, control=list(maxit=3000)), silent=TRUE)
cat("elapsed min:", round(difftime(Sys.time(),t0,units="mins"),1), "\n")
if (inherits(mm,"try-error")) { cat("MISCLASS FAILED:", attr(mm,"condition")$message, "\n") }
else {
  saveRDS(mm, file.path(OUT,"m0_misclass.rds"))
  sink(file.path(OUT,"misclass_results.txt"), split=TRUE)
  cat("misclassification model -2LL:", mm$minus2loglik, " (null:", m0$minus2loglik, ")\n")
  cat("\nQ:\n"); print(qmatrix.msm(mm))
  cat("\nE (misclassification odds):\n"); print(ematrix.msm(mm))
  cat("\n5y P:\n"); print(pmatrix.msm(mm, t=5))
  sink()
}
cat("DONE\n")
