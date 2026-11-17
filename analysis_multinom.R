# Discrete-time transition analysis: multinomial logit of W6 state on covariates, stratified by 2018 state
library(nnet)
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

mvars <- c("agez","female","edu4","married","drink","htn","dm","heart","stroke18","stroke_inc","cesd10")
d <- d[complete.cases(d[, mvars]), ]

sink(file.path(OUT,"multinom_results.txt"), split=TRUE)
cat("Analysis N (2018 state + W6 outcome + complete covariates):", nrow(d), "\n")
cat("\nTransition counts (2018 state x W6 state):\n")
print(table(d$state18f, d$outcome))
cat("\nTransition proportions (row %):\n")
print(round(prop.table(table(d$state18f, d$outcome), 1) * 100, 1))

all_rows <- list()
fits <- list()
for (s in c("Normal","CIND","Dementia")) {
  ds <- d[d$state18f == s, ]
  ds$outcome <- relevel(droplevels(ds$outcome), ref = s)
  m <- multinom(outcome ~ agez + female + edu4 + married + drink + htn + dm + heart +
                stroke18 + stroke_inc + cesd10, data = ds, trace = FALSE)
  fits[[s]] <- m
  sm <- summary(m)
  cat("\n===== baseline state:", s, " n =", nrow(ds), " =====\n")
  for (lev in rownames(sm$coefficients)) {
    est <- sm$coefficients[lev, ]; se <- sm$standard.errors[lev, ]
    tab <- data.frame(
      baseline = s, outcome = lev, covariate = colnames(sm$coefficients),
      RRR = round(exp(est), 3),
      L = round(exp(est - 1.96 * se), 3),
      U = round(exp(est + 1.96 * se), 3),
      p = round(2 * pnorm(-abs(est / se)), 4))
    rownames(tab) <- NULL
    all_rows[[paste(s, lev)]] <- tab
  }
  print(all_rows[[paste(s, rownames(sm$coefficients)[1])]])
}
sink()

restab <- do.call(rbind, all_rows)
write.csv(restab, file.path(OUT, "multinom_rrr.csv"), row.names = FALSE)
saveRDS(fits, file.path(OUT, "multinom_fits.rds"))

# key result printout: stroke effects
key <- restab[restab$covariate %in% c("stroke181","stroke_inc1"), ]
cat("\n===== STROKE EFFECTS (RRR) =====\n")
print(key)
cat("DONE\n")
