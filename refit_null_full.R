# P0: refit null model on FULL panel (no covariate complete-case restriction)
library(msm)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
panel <- read.csv(file.path(OUT, "analytic_panel.csv"), stringsAsFactors = FALSE)
panel <- panel[order(panel$ID, panel$time), ]
nper <- ave(panel$state, panel$ID, FUN = length)
panel <- panel[nper >= 2, ]
fs <- ave(panel$state, panel$ID, FUN = function(x) x[1])
panel <- panel[fs != 4, ]
cat("full panel persons:", length(unique(panel$ID)), " rows:", nrow(panel), "\n")
Qtpl <- rbind(c(0,.1,.01,.05), c(.1,0,.05,.1), c(0,.05,0,.2), c(0,0,0,0))
ids <- unique(panel$ID)
m_chunk <- msm(state ~ time, subject = ID, data = panel[panel$ID %in% ids[1:1000], ],
               qmatrix = crudeinits.msm(state ~ time, ID, data = panel, qmatrix = Qtpl))
Qi <- qmatrix.msm(m_chunk)$estimates; diag(Qi) <- 0; diag(Qi) <- -rowSums(Qi)
m0f <- msm(state ~ time, subject = ID, data = panel, qmatrix = Qi, control = list(maxit = 5000))
saveRDS(m0f, file.path(OUT, "m0_null_full.rds"))
sink(file.path(OUT, "null_model_full_results.txt"), split = TRUE)
cat("=== NULL MODEL, FULL PANEL ===\n")
cat("Q matrix:\n"); print(qmatrix.msm(m0f))
cat("\nSojourn:\n"); print(sojourn.msm(m0f))
cat("\n5-year P matrix:\n"); print(pmatrix.msm(m0f, t = 5, ci = "normal"))
cat("\n1-year P matrix:\n"); print(pmatrix.msm(m0f, t = 1))
cat("\n-2LL:", m0f$minus2loglik, "\n")
sink()
cat("DONE\n")
