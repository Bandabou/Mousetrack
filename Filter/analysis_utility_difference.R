# Sampled from "analysis.R" by Chao
# Written by Bouke
# Has some redundant lines, which are left in for compatibility


### load libraries
if (!require("pacman")) install.packages("pacman")
pacman::p_load("ggplot2", "reshape2", "lme4", "lmerTest", "psych", "piecewiseSEM", "stringr", "brms", "DescTools", "mlr", "plyr")

### load data
setwd("C:\\Users\\bouke\\Documents\\GitHub\\DataAnalysis")
df <- read.csv("data merged FINAL.csv", sep=",", dec=".", header=TRUE, stringsAsFactors = FALSE)

## compute additional variabbles
new_var <- c("choice2", "health_dif", "taste_dif")
#df <- df[which(df$trial_type != "filler"),]

for (var in new_var) {
  df[[var]] <- rep(NA, nrow(df))
}
for (i in 1:nrow(df)) {
  if (df$direction[i] == "Left") {
    df$choice2[i] <- 1
  } else if (df$direction[i] == "Right") {
    df$choice2[i] <- 0
  }
  if (df$ppn[i] != "p44" && is.na(df$health_L[i])==FALSE) {
    df$health_dif[i] <- df$health_L[i] - df$health_R[i]
    df$taste_dif[i] <- df$taste_L[i] - df$taste_R[i]
  }
}

### effects of trial types on the parameters
df2 <- df
#df <- df[which(df$ppn!="p44"),]

## build the multilevel logistic regression model of actual choice
# fit the model
df2$choice2 <- factor(df2$choice2)
#df2$ppn <- factor(df2$ppn)

for (i in 1:nrow(df)) {
  if (is.na(df$ppn[i])) {
    print('Missing')
  }
}

x <- choice2~1+taste_dif+health_dif+(0+taste_dif+health_dif|ppn)
mod_choice <- glmer(x, df2, family=binomial)
#mod_choice_control <- glmer(x, df2[which(df2$trial_type=="control"),], family=binomial)
#mod_choice_health <- glmer(x, df2[which(df2$trial_type=="health"),], family=binomial)
#mod_choice_taste <- glmer(x, df2[which(df2$trial_type=="taste"),], family=binomial)
# same pattern, and no effects of nudging it seems
#summary mod_choice


# fit models for each participant to get individual model fit
df3 <- df2
df3$fit <- rep(NA, nrow(df3))
for (i in unique(df3$ppn)) {
  data_current <- df3[which(df3$ppn==i),]
  fit <- glm(choice2~1+taste_dif+health_dif, data_current, family=binomial)
  df3$fit[which(df3$ppn==i)] <- rsquared(fit)[5][[1]]
}
df4 <- df3[which(df3$fit >= 0.1),] # no one with fit less than 10%, so people seemed to be a bit more careful

# fit the final model
mod_choice2 <- glmer(choice2~1+taste_dif+health_dif+(0+taste_dif+health_dif|ppn), df4, family=binomial)

weight_taste_ave <- fixef(mod_choice2)[2][[1]]
weight_health_ave <- fixef(mod_choice2)[3][[1]]

weight_taste <- fixef(mod_choice2)[2][[1]] + ranef(mod_choice2)$ppn[[1]]
weight_health <- fixef(mod_choice2)[3][[1]] + ranef(mod_choice2)$ppn[[2]]
df_coef <- data.frame(ppn=unique(df4$ppn), weight_health=weight_health, weight_taste=weight_taste)
df4$weight_health <- rep(NA, nrow(df4))
df4$weight_taste <- rep(NA, nrow(df4))
for (i in 1:nrow(df4)) {
  ppn_current <- df4$ppn[i]
  df4$weight_health[i] <- df_coef$weight_health[which(df_coef$ppn==ppn_current)]
  df4$weight_taste[i] <- df_coef$weight_taste[which(df_coef$ppn==ppn_current)]
}

for (i in 1:nrow(df4)) {
  df4$utility_L1[i] <- df4$health_L[i] + df4$taste_L[i]
  df4$utility_R1[i] <- df4$health_R[i] + df4$taste_R[i]
  df4$utility_dif1[i] <- abs(df4$utility_L1[i] - df4$utility_R1[i])
  df4$trade_off_health1[i] <- abs(df4$health_L[i] - df4$health_R[i])
  df4$trade_off_taste1[i] <- abs(df4$taste_L[i] - df4$taste_R[i])
  if (df4$utility_L1[i] - df4$utility_R1[i] > 0) {
    df4$opt_stronger1[i] <- "Left"
  } else if (df4$utility_L1[i] - df4$utility_R1[i] < 0) {
    df4$opt_stronger1[i] <- "Right"
  }  
}


## categorize trials
df4$trade_off <- df4$health_dif * df4$taste_dif
df4$trial_type1 <- rep(NA, nrow(df4))
# categorization using attributes without weights from the model
for (i in 1:nrow(df4)) {
  if (df4$trade_off[i] >= 0) {
    if (df4$utility_dif1[i] >= 5) {
      if (is.na(df4$opt_stronger1[i])==FALSE) {
        if (df4$direction[i] == df4$opt_stronger1[i]) {
          df4$trial_type1[i] <- "dominate"
        }
      } else {
        df4$trial_type1[i] <- "dominate"
      }
    } else if (df4$utility_dif1[i] <= 1) {
      df4$trial_type1[i] <- "similar"
    }
  } else {
    if (df4$utility_dif1[i] <= 1) {
      if (df4$trade_off_health1[i] >= 2 && df4$trade_off_taste1[i] >= 2) {
        df4$trial_type1[i] <- "trade-off"
      } else {
        df4$trial_type1[i] <- "similar"
      }
    }
  }
}
  
theme_set(theme_bw())
df4_1 <- df4[which(is.na(df4$trial_type1)==FALSE),]
ggplot(df4_1, aes(x=health_dif, y=taste_dif, group=trial_type1, color=trial_type1)) + geom_point(size=3, alpha=0.3) + geom_jitter() +
  theme(axis.title=element_text(size=15)) +
  theme(legend.text=element_text(size=14)) +
  theme(legend.title=element_text(size=14)) + xlab("health difference") + ylab("taste difference")

# same but with absolute difference
theme_set(theme_bw())
df4_1 <- df4[which(is.na(df4$trial_type1)==FALSE),]
ggplot(df4_1, aes(x=abs(health_dif), y=abs(taste_dif), group=trial_type1, color=trial_type1)) + geom_point(size=3, alpha=0.3) + geom_jitter() +
  theme(axis.title=element_text(size=15)) +
  theme(legend.text=element_text(size=14)) +
  theme(legend.title=element_text(size=14)) + xlab("health difference") + ylab("taste difference")

write.csv(df4$utility_dif1,"C:\\Users\\bouke\\Documents\\GitHub\\DataAnalysis\\utility_dif1.csv", row.names = FALSE)
write.csv(df4,"C:\\Users\\bouke\\Documents\\GitHub\\DataAnalysis\\utility.csv", row.names = FALSE)

