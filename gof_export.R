# Data-only export (no graphics device): observed vs expected prevalence for GOF figure.
library(msm)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
m0 <- readRDS(file.path(OUT, "m0_null_full.rds"))
pv <- prevalence.msm(m0, mintime = 0, maxtime = 6)
obs <- pv$Observed; exp <- pv$Expected
df <- data.frame(t = as.numeric(rownames(obs)),
                 obs1 = obs[, "State 1"], obs2 = obs[, "State 2"], obs3 = obs[, "State 3"],
                 obsT = obs[, "Total"],
                 exp1 = exp[, "State 1"], exp2 = exp[, "State 2"], exp3 = exp[, "State 3"],
                 expT = exp[, "Total"])
write.csv(df, file.path(OUT, "gof_data.csv"), row.names = FALSE)
cat("DONE\n")
