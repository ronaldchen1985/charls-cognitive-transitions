library(msm)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
m0 <- readRDS(file.path(OUT,"m0_null_full.rds"))
pv <- prevalence.msm(m0, mintime=0, maxtime=6)
obs <- pv$Observed; exp <- pv$Expected
sink(file.path(OUT,"gof_prevalence.txt"), split=TRUE)
cat("Observed vs expected state prevalence (counts):\n")
print(round(cbind(obs, exp), 2))
sink()

# Keep only measurement windows with enough observed individuals and
# drop late rows where midpoint-imputed death times artefactually
# deplete transient states (t > 4.5).
t <- as.numeric(rownames(obs))
tot <- obs[, "Total"]
keep <- which(tot >= 1500 & t <= 4.5)
obsp <- obs[keep,1:3] / tot[keep] * 100
expp <- exp[keep,1:3] / exp[keep, "Total"] * 100
tt <- t[keep]

cols <- c("#4C9F70","#E8A33D","#C0392B")
labs <- c("Normal cognition","CIND","Dementia")
png(file.path(OUT,"figS_gof.png"), width=1100, height=750, res=140)
par(mar=c(4.5,4.5,3,1))
plot(range(tt), c(0, max(c(obsp,expp))*1.12), type="n",
     xlab="Years since July 2018", ylab="Prevalence (%)",
     main="Observed (points) vs model-expected (lines)\ntransient-state prevalence")
for (j in 1:3) {
  points(tt, obsp[,j], pch=16, col=cols[j], cex=1.1)
  lines(tt, expp[,j], lty=1, lwd=2, col=cols[j])
}
legend("topright", labs, col=cols, lty=1, lwd=2, pch=16, bty="n", cex=0.9)
dev.off()
cat("DONE\n")
