# Formal tests of stage-dependence: Wald contrasts between outcome-level
# coefficients within each baseline-state-stratified multinomial model.
# Refits the three stratum models exactly as analysis_multinom.R (also serves
# as an independent refit check), then tests, for each exposure, whether the
# association with progression to dementia exceeds that with CIND onset
# (Normal stratum) or reversion (CIND stratum).
library(nnet)
OUT <- "D:/CHARLS/DementiaTransition_W6/output"
cov <- read.csv(file.path(OUT, "covariates.csv"), stringsAsFactors = FALSE)
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
mvars <- c("agez","female","edu4","married","drink","htn","dm","heart","stroke18","stroke_inc","cesd10")
d <- d[complete.cases(d[, mvars]), ]
cat("analysis N:", nrow(d), "\n")

fits <- list()
for (s in c("Normal","CIND","Dementia")) {
  ds <- d[d$state18f == s, ]
  ds$outcome <- relevel(droplevels(ds$outcome), ref = s)
  fits[[s]] <- multinom(outcome ~ agez + female + edu4 + married + drink + htn +
                        dm + heart + stroke18 + stroke_inc + cesd10,
                        data = ds, trace = FALSE)
}

specs <- list(
  list("Normal", "stroke181",  "Dementia", "CIND"),   # progression vs onset
  list("Normal", "stroke_inc1","Dementia", "CIND"),
  list("CIND", "stroke181",  "Dementia", "Normal"),   # progression vs reversion
  list("CIND", "stroke_inc1","Dementia", "Normal"),
  list("Normal", "cesd101", "Dementia", "CIND"),      # parallel pattern: depression
  list("CIND",   "cesd101", "Dementia", "Normal")
)

res <- data.frame()
for (s in specs) {
  stratum <- s[[1]]; cv <- s[[2]]; levA <- s[[3]]; levB <- s[[4]]
  m <- fits[[stratum]]
  co <- coef(m); V <- vcov(m)
  nA <- paste0(levA, ":", cv); nB <- paste0(levB, ":", cv)
  if (!(nA %in% colnames(V)) || !(nB %in% colnames(V))) {
    cat("MISSING:", stratum, cv, levA, levB, "\n"); next
  }
  diff <- co[levA, cv] - co[levB, cv]
  se <- sqrt(V[nA, nA] + V[nB, nB] - 2 * V[nA, nB])
  z <- diff / se; p <- 2 * pnorm(-abs(z))
  res <- rbind(res, data.frame(
    stratum = stratum, covariate = cv,
    contrast = paste(levA, "vs", levB),
    d_logRRR = round(diff, 3), se = round(se, 3),
    z = round(z, 2), p = signif(p, 4)))
}
res$p_BH <- signif(p.adjust(res$p, method = "BH"), 4)
print(res, row.names = FALSE)
write.csv(res, file.path(OUT, "interaction_tests.csv"), row.names = FALSE)
cat("DONE\n")
