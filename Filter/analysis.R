### load libraries
if (!require("pacman")) install.packages("pacman")
pacman::p_load("ggplot2", "reshape2", "lme4", "lmerTest", "psych", "piecewiseSEM", "stringr", "brms", "DescTools", "mlr", "plyr")

### load data
setwd("C:\\Users\\bouke\\Documents\\GitHub\\DataAnalysis")
df <- read.csv("data_merged.csv", sep=";", dec=".", header=TRUE, stringsAsFactors = FALSE)

## recode some variables and missing values
#df$condition <- factor(df$condition)
#df$hand[which(df$hand==0)] <- "left"
#df$hand[which(df$hand==1)] <- "right"
#df$hand[which(df$hand==2)] <- "both"
#df$hand <- factor(df$hand)
df$gender[which(df$gender==0)] <- "male" #WHICH? https://www.rdocumentation.org/packages/base/versions/3.6.2/topics/which
df$gender[which(df$gender==1)] <- "female"
df$gender <- factor(df$gender) #FACTOR? https://www.rdocumentation.org/packages/base/versions/3.6.2/topics/factor
df$diet[which(df$diet==0)] <- "no"
df$diet[which(df$diet==1)] <- "yes"
df$diet <- factor(df$diet)
df$allergies[which(df$allergies==0)] <- "no"
df$allergies[which(df$allergies==1)] <- "yes"
df$allergies <- factor(df$allergies)
df$vegan[which(df$vegan==0)] <- "yes"
df$vegan[which(df$vegan==1)] <- "no"
df$vegan <- factor(df$vegan)
for (i in c(2, 3, 4, 5, 6, 7, 8, 10, 11)) { #???
  df[[paste0("tsc", as.character(i))]] <- 8 - df[[paste0("tsc", as.character(i))]]
}
df$tsc <- apply(data.frame(df$tsc1, df$tsc2, df$tsc3, df$tsc4, df$tsc5, df$tsc6, df$tsc7, df$tsc8, df$tsc9, df$tsc10, df$tsc11, df$tsc12, df$tsc13), 1, mean)
df$trial_block <- factor(df$trial_block, exclude = "")
df$trial_type <- factor(df$trial_type, exclude= "") #???
df$nudging_direction <- factor(df$nudging_direction, exclude= "")

var_string <- c("stim", "stim_L", "stim_R", "events", "distance_x", "distance_y", "angle", "IMA", "coor_x", "coor_y", "coor_x_ab", "coor_y_ab", "coor_x_ab_direction", "coor_y_ab_direction", "distance_x2", "distance_y2", "coor_x2", "coor_y2", "coor_x_ab2", "coor_y_ab2", "coor_x_ab_direction2", "coor_y_ab_direction2", "angle2", "IMA2")
var_minus <- c("health_L", "health_R", "taste_L", "taste_R", "RT", "AUC", "MD", "y_MD", "commitment", "min_distance", "max_velocity", "max_acceleration", "x_flip", "y_flip",
               "drag_time", "hold_time", "AUC2", "MD2", "y_MD2", "commitment", "min_distance", "max_velocity2", "max_acceleration2", "x_flip2", "y_flip2", "drag_time2", "hold_time2")
for (var in var_string) {
  df[[var]][which(df[[var]]=="[]")] <- NA #NA? https://www.rdocumentation.org/packages/base/versions/3.6.2/topics/NA
}
for (var in var_minus) {
  df[[var]][which(df[[var]]==-1)] <- NA
}

## process the string data
breakString <- function(s) { # like python function https://www.tutorialspoint.com/r/r_functions.htm
  if (is.na(s)==FALSE) {
    s2 <- str_sub(s, 2, (str_length(s)-1))
    #print(s2)
    s3 <- strsplit(s2, ",")
    #print(s3)
    if (is.na(as.numeric(s3[[1]])[1])==FALSE) {
      return (list(as.numeric(s3[[1]])))
    } else {
      return (list(s3[[1]]))
    }
  } else {
    return (NA)
  }
}

var_list <- c("coor_x", "coor_y", "coor_x_ab", "coor_y_ab", "coor_x_ab_direction", "coor_y_ab_direction", "distance_x", "distance_y", "angle", "IMA", "events",
              "coor_x2", "coor_y2", "coor_x_ab2", "coor_y_ab2", "coor_x_ab_direction2", "coor_y_ab_direction2", "distance_x2", "distance_y2", "angle2", "IMA2")
for (i in 1:nrow(df)) {
  print(i)
  for (var in var_list) {
    #print(var)
    df[[var]][i] <- breakString(df[[var]][i])
  }
}

df$release <- rep(NA, nrow(df)) #REP? https://www.rdocumentation.org/packages/base/versions/3.6.2/topics/rep
df$few <- rep(NA, nrow(df)) #NROW? https://www.rdocumentation.org/packages/base/versions/3.6.2/topics/nrow
for (i in 1:nrow(df)) {
  if (is.na(df$events[i])==FALSE) {
    df$release[i] <- 0
    for (j in df$events[i][[1]]) {
      if (j == " u'up'") {
        df$release[i] <- df$release[i] + 1
      }
    }
    if (length(df$events[i][[1]]) < 10) {
      df$few[i] <- 1
    } else {
      df$few[i] <- 0
    }
  }
}
df_raw <- df

## compute additional variabbles
new_var <- c("choice2", "SC_outcome", "health_dif", "taste_dif", "opt_health", "opt_taste", "consistency")
df <- df[which(df$trial_type != "filler"),]
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
    if (df$health_dif[i] > 0) {
      df$opt_health[i] <- "Lelf"
    } else if (df$health_dif[i] < 0) {
      df$opt_health[i] <- "Right"
    }
    if (df$taste_dif[i] > 0) {
      df$opt_taste[i] <- "Left"
    } else if (df$taste_dif[i] < 0) {
      df$opt_taste[i] <- "Right"
    }
    if (df$health_dif[i] * df$taste_dif[i] < 0) {
      #print("1")
      if (df$direction[i] == df$opt_health[i]) {
        #print("2")
        df$SC_outcome[i] <- "Success"
      } else {
        df$SC_outcome[i] <- "Failure"
      }
    }
    pair_current <- df$stim[i]
    pair_reverse <- StrRev(pair_current)
    data_ppn <- df[which(df$ppn==df$ppn[i]),]
    data_current <- data_ppn[union(which(data_ppn$stim==as.numeric(pair_current)), which(data_ppn$stim==as.numeric(pair_reverse))),]
    if (nrow(data_current)>=2) {
      count <- 0
      for (j in 1:(nrow(data_current))) {
        if (data_current$choice[j] == data_current$choice[1]) {
          count <- count + 1
        }
      }
      df$consistency[i] <- round(count/nrow(data_current), 3)
      if (df$consistency[i] < 0.5) {
        df$consistency[i] <- 1 - df$consistency[i]
      }
    }
  }
}

## compute self-control success rate for each individual
df$SC_rate <- rep(NA, nrow(df))
for (ppn in unique(df$ppn)) {
  data <- df$SC_outcome[which(df$ppn==ppn)]
  success <- 0
  total <- 0
  for (j in 1:length(data)) {
    if (is.na(data[j])==FALSE) {
      total <- total + 1
      if (data[j] == "Success") {
        success <- success + 1
      }
    }
  }
  print (total)
  print(success)
  if (total != 0) {
    df$SC_rate[which(df$ppn==ppn)] <- success / total
  }
}

## remove problematic trials
# trajectories with less than 10 points and with finger (or mouse) release
length(which(df$few==1)) # only 1 trial
length(which(df$release>1)) # 396 trials, 280 in touch condition (3.3% of total) and 116 in mouse condition (1.3%)
df <- df[which(df$few==0),]
df <- df[which(df$release==1),] 

# AUC and MD smaller than 0
length(which(df$AUC<=0))
df <- df[which(df$AUC>0),] # only 0.06%, 5 trials

length(which(df$AUC<0.5)) # 11.6% much smaller than the 22.8% of the last study

length(which(df$MD<=0)) # only 1.6%, 127 trials
df <- df[which(df$MD>0),]

# x_coor_ab or y_coor_ab too large
df$exclude <- rep(0, nrow(df))
for (i in 1:nrow(df)) {
  for (j in 1:length(df$coor_x_ab[i][[1]])) {
    if (abs(df$coor_x_ab[i][[1]][j])>2) {
      df$exclude[i] <- 1
      break
    }
  }
  for (j in 1:length(df$coor_y_ab[i][[1]])) {
    if (abs(df$coor_y_ab[i][[1]][j])>2) {
      df$exclude[i] <- 1
      break
    }
  }
}
df <- df[which(df$exclude==0),]

# now, 7966 trials left for analyses (93.7% when excluding the procedurally missing data)
# plot the parameters
df_mouse <- df[which(df$trial_block=="mouse"),]
df_touch <- df[which(df$trial_block=="touch"),]

df_plot_mouse <- data.frame(AUC=df_mouse$AUC, MD=df_mouse$MD, commitment=df_mouse$commitment, min_distance=df_mouse$min_distance, x_flip=df_mouse$x_flip, DT=df_mouse$drag_time, MV=df_mouse$max_velocity, MA=df_mouse$max_acceleration)
df_plot_touch <- data.frame(AUC=df_touch$AUC, MD=df_touch$MD, commitment=df_touch$commitment, min_distance=df_touch$min_distance, x_flip=df_touch$x_flip, DT=df_touch$drag_time, MV=df_touch$max_velocity, MA=df_touch$max_acceleration)

df_plot_mouse <- makePairs(df_plot_mouse)
df_plot_touch <- makePairs(df_plot_touch)

mega_feature_mouse <- data.frame(df_plot_mouse$all)
mega_feature_touch <- data.frame(df_plot_touch$all)

theme_set(theme_bw())

ggplot(mega_feature_mouse, aes_string(x = "x", y = "y")) + 
  facet_grid(xvar ~ yvar, scales = "free") + 
  geom_point(size=1.5, na.rm = TRUE, alpha=0.3) + 
  stat_density(aes(x = x, y = ..scaled.. * diff(range(x)) + min(x)), 
               data = df_plot_mouse$densities, position = "identity", 
               colour = "grey0", geom = "line") +
  theme(strip.text.x = element_text(size = 13)) +
  theme(strip.text.y = element_text(size = 13)) + 
  theme(axis.text.x = element_text(size = 13)) + 
  theme(axis.text.y = element_text(size = 13))

ggplot(mega_feature_touch, aes_string(x = "x", y = "y")) + 
  facet_grid(xvar ~ yvar, scales = "free") + 
  geom_point(size=1.5, na.rm = TRUE, alpha=0.3) + 
  stat_density(aes(x = x, y = ..scaled.. * diff(range(x)) + min(x)), 
               data = df_plot_touch$densities, position = "identity", 
               colour = "grey0", geom = "line") +
  theme(strip.text.x = element_text(size = 13)) +
  theme(strip.text.y = element_text(size = 13)) + 
  theme(axis.text.x = element_text(size = 13)) + 
  theme(axis.text.y = element_text(size = 13))


## log transform the parameters (except for AUC)
df2 <- df
var_log <- c("MD", "drag_time", "max_velocity", "max_acceleration")
for (var in var_log) {
  df2[[var]] <- log(df2[[var]])
}

# Z-score and remvong extreme values
features <- c("AUC", "MD", "drag_time", "max_velocity", "max_acceleration", "x_flip")
features_std <- c("AUC", "MD", "x_flip", "drag_time", "max_velocity", "max_acceleration")
for (feature in features_std) {
  df2[[feature]] <- scale(df2[[feature]])
  for (i in 1:nrow(df2)) {
    if (is.na(df2[[feature]][i]) == FALSE) {
      if (abs(df2[[feature]][i]) >= 3) {
        df[[feature]][i] <- NA
      }
    }
  } 
}
for (feature in features) {
  df <- df[which(is.na(df[[feature]])==FALSE),]# this would further remove 5.6% of the remaining trials
}
# now 7585 trials left (88.2%)




### compare the touch and mouse conditions
## AUC and MD
# compared with previous data, the mean of AUC and MD are slightly higher (0.75 and 0.4, compared with 0.61 and 0.23), or after std,
# -0.02 and 0.05 compared with -0.05, 0.01. And interestingly kurtosis is much smaller for AUC (0.26 and 0.47). Might due to the removal of releasing trials (to be checked)
plot_input <- list()
fit_input <- list()
for (feature in features) {
  plot_input[[feature]] <- ggplot(df, aes_string(x=feature, group="trial_block", fill="trial_block")) + geom_density(alpha=0.25)
  fit_input[[feature]] <- lmer(as.formula(paste0(feature, "~1+trial_block+(1|ppn)")), df, REML=FALSE)
}
# very small difference between the two input methods. Mouse produces just slight more spread in AUC and MD, slightly smaller max_acceleration, and
# due to the sensitivity difference of the touch method, much less x_flip detected in mouse condition.

plot_type <- list()
for (feature in features) {
  plot_type[[feature]] <- ggplot(df, aes_string(x=feature, group="trial_type", fill="trial_type")) + geom_density(alpha=0.25)
}
# filler trial: tiny difference for AUC and MD, but much faster, and higher max_velocity, less x_flip (but filler always to left because of a bug)

plot_direction <- list()
for (feature in features) {
  plot_direction[[feature]] <- ggplot(df, aes_string(x=feature, group="direction", fill="direction")) + geom_density(alpha=0.25)
}
# contrary to the previous data, not much difference between direction, even right is a bit more complex

### effects of trial types on the parameters
df <- df[which(df$ppn!="p44"),]
df2 <- df
## build the multilevel logistic regression model of actual choice
# fit the model
df2$choice2 <- factor(df2$choice2)
mod_choice <- glmer(choice2~1+taste_dif+health_dif+(0+taste_dif+health_dif|ppn), df2, family=binomial)
mod_choice_control <- glmer(choice2~1+taste_dif+health_dif+(0+taste_dif+health_dif|ppn), df2[which(df2$trial_type=="control"),], family=binomial)
mod_choice_health <- glmer(choice2~1+taste_dif+health_dif+(0+taste_dif+health_dif|ppn), df2[which(df2$trial_type=="health"),], family=binomial)
mod_choice_taste <- glmer(choice2~1+taste_dif+health_dif+(0+taste_dif+health_dif|ppn), df2[which(df2$trial_type=="taste"),], family=binomial)
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
# does self-report health goal correlate with health weights
df4$trait <- rep(0, nrow(df4))
ppn_current <- "p00"
for (i in 1:nrow(df4)) {
  if (df4$ppn[i] != ppn_current) {
    df4$trait[i] <- 1
    ppn_current <- df4$ppn[i]
  } 
}
fit_health_goal <- lm(weight_health~goal_health, df4[which(df4$trait==1),]) # unlike the previous study, seems to be a small correlation

## compute utility and tradeoff scores based on the estimated decision weights
# calculate utility without weights from the model
new_var <- c("utility_L1", "utility_R1", "utility_dif1", "trade_off_health1", "trade_off_taste1", "opt_stronger1")
for (var in new_var) {
  df4[[var]] <- rep(NA, nrow(df4))
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

# calculate utility with averaged weights
new_var <- c("utility_L2", "utility_R2", "utility_dif2", "trade_off_health2", "trade_off_taste2", "opt_stronger2")
for (var in new_var) {
  df4[[var]] <- rep(NA, nrow(df4))
}

for (i in 1:nrow(df4)) {
  df4$utility_L2[i] <- df4$health_L[i] * weight_health_ave + df4$taste_L[i] * weight_taste_ave
  df4$utility_R2[i] <- df4$health_R[i] * weight_health_ave + df4$taste_R[i] * weight_taste_ave
  df4$utility_dif2[i] <- abs(df4$utility_L2[i] - df4$utility_R2[i])
  df4$trade_off_health2[i] <- abs(weight_health_ave * (df4$health_L[i] - df4$health_R[i]))
  df4$trade_off_taste2[i] <- abs(weight_taste_ave * (df4$taste_L[i] - df4$taste_R[i]))
  if (df4$utility_L2[i] - df4$utility_R2[i] > 0) {
    df4$opt_stronger2[i] <- "Left"
  } else if (df4$utility_L2[i] - df4$utility_R2[i] < 0) {
    df4$opt_stronger2[i] <- "Right"
  }  
}


# calculate utility with personal weights
new_var <- c("utility_L3", "utility_R3", "utility_dif3", "trade_off_health3", "trade_off_taste3", "opt_stronger3")
for (var in new_var) {
  df4[[var]] <- rep(NA, nrow(df4))
}

##MARKK
for (i in 1:nrow(df4)) {
  df4$utility_L3[i] <- df4$health_L[i] * df4$weight_health[i] + df4$taste_L[i] * df4$weight_taste[i]
  df4$utility_R3[i] <- df4$health_R[i] * df4$weight_health[i] + df4$taste_R[i] * df4$weight_taste[i]
  df4$utility_dif3[i] <- abs(df4$utility_L3[i] - df4$utility_R3[i])
  df4$trade_off_health3[i] <- abs(df4$weight_health[i] * (df4$health_L[i] - df4$health_R[i]))
  df4$trade_off_taste3[i] <- abs(df4$weight_taste[i] * (df4$taste_L[i]  - df4$taste_R[i]))
  if (df4$utility_L3[i] - df4$utility_R3[i] > 0) {
    df4$opt_stronger3[i] <- "Left"
  } else if (df4$utility_L3[i] - df4$utility_R3[i] < 0) {
    df4$opt_stronger3[i] <- "Right"
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

# plot the categorization
theme_set(theme_bw())
df4_1 <- df4[which(is.na(df4$trial_type1)==FALSE),]
ggplot(df4_1, aes(x=health_dif, y=taste_dif, group=trial_type1, color=trial_type1)) + geom_point(size=3, alpha=0.3) + geom_jitter() +
  theme(axis.title=element_text(size=15)) +
  theme(legend.text=element_text(size=14)) +
  theme(legend.title=element_text(size=14)) + xlab("health difference") + ylab("taste difference")

# categorization using attributes without averaged weithts
df4$trial_type2 <- rep(NA, nrow(df4))
for (i in 1:nrow(df4)) {
  if (df4$trade_off[i] >= 0) {
    if (df4$utility_dif2[i] >= 4) {
      if (is.na(df4$opt_stronger2[i])==FALSE) {
        if (df4$direction[i] == df4$opt_stronger2[i]) {
          df4$trial_type2[i] <- "dominate"
        }
      } else {
        df4$trial_type2[i] <- "dominate"
      }
    } else if (df4$utility_dif2[i] <= 1) {
      df4$trial_type2[i] <- "similar"
    }
  } else {
    if (df4$utility_dif2[i] <= 1) {
      if (df4$trade_off_health2[i] >= 0 && df4$trade_off_taste2[i] >= 0) {
        df4$trial_type2[i] <- "trade-off"
      } else {
        df4$trial_type2[i] <- "similar"
      }
    }
  }
}

# plot the categorization
theme_set(theme_bw())
df4_2 <- df4[which(is.na(df4$trial_type2)==FALSE),]
ggplot(df4_2, aes(x=health_dif, y=taste_dif, group=trial_type2, color=trial_type2)) + geom_point(size=3, alpha=0.3) + geom_jitter() + 
  theme(axis.title=element_text(size=15)) +
  theme(legend.text=element_text(size=14)) +
  theme(legend.title=element_text(size=14)) + xlab("health difference") + ylab("taste difference")

df4$trial_type3 <- rep(NA, nrow(df4))
for (i in 1:nrow(df4)) {
  if (df4$trade_off[i] >= 0) {
    if (df4$utility_dif3[i] >= 2) {
      if (is.na(df4$opt_stronger3[i])==FALSE) {
        if (df4$direction[i] == df4$opt_stronger3[i]) {
          df4$trial_type3[i] <- "dominate"
        }
      } else {
        df4$trial_type3[i] <- "dominate"
      }
    } else if (df4$utility_dif3[i] <= 2) {
      df4$trial_type3[i] <- "similar"
    }
  } else {
    if (df4$utility_dif3[i] <= 2) {
      if (df4$trade_off_health3[i] >= 0 && df4$trade_off_taste3[i] >= 0) {
        df4$trial_type3[i] <- "trade-off"
      } else {
        df4$trial_type3[i] <- "similar"
      }
    }
  }
}

# plot the categorization
theme_set(theme_bw())
df4_3 <- df4[which(is.na(df4$trial_type3)==FALSE),]
ggplot(df4_3, aes(x=health_dif, y=taste_dif, group=trial_type3, color=trial_type3)) + geom_point(size=3, alpha=0.3) + geom_jitter() +
  theme(axis.title=element_text(size=15)) +
  theme(legend.text=element_text(size=14)) +
  theme(legend.title=element_text(size=14)) + xlab("health difference") + ylab("taste difference")


# fit the models
#fit_type1 <- list()
#fit_type2 <- list()
fit_type3 <- list()
for (feature in features) {
  #fit_type1[[feature]] <- lmer(as.formula(paste0(feature, "~1+trial_type1*trial_block+(1|ppn)")), df4, REML=FALSE)
  #fit_type2[[feature]] <- lmer(as.formula(paste0(feature, "~1+trial_type2*trial_block+(1|ppn)")), df4, REML=FALSE)
  fit_type3[[feature]] <- lmer(as.formula(paste0(feature, "~1+trial_type3+(1|ppn)")), df4, REML=FALSE)
}

#plot_type1 <- list()
#plot_type2 <- list()
plot_type3 <- list()
for (feature in features) {
  #plot_type1[[feature]] <- ggplot(df4[which(is.na(df4$trial_type1)==FALSE),], aes_string(x=feature, group="trial_type1", fill="trial_type1")) + geom_density(alpha=0.25) + facet_grid(~trial_block)
  #plot_type2[[feature]] <- ggplot(df4[which(is.na(df4$trial_type2)==FALSE),], aes_string(x=feature, group="trial_type2", fill="trial_type2")) + geom_density(alpha=0.25)+ facet_grid(~trial_block)
  plot_type3[[feature]] <- ggplot(df4[which(is.na(df4$trial_type3)==FALSE),], aes_string(x=feature, group="trial_type3", fill="trial_type3")) + geom_density(alpha=0.25)
}

# separate by input condition
fit_type1_input <- list()
fit_type2_input <- list()
fit_type3_input <- list()
for (feature in features) {
  fit_type1_input[[feature]] <- lmer(as.formula(paste0(feature, "~1+trial_type1*trial_block+(1|ppn)")), df4, REML=FALSE)
  fit_type2_input[[feature]] <- lmer(as.formula(paste0(feature, "~1+trial_type2*trial_block+(1|ppn)")), df4, REML=FALSE)
  fit_type3_input[[feature]] <- lmer(as.formula(paste0(feature, "~1+trial_type3*trial_block+(1|ppn)")), df4, REML=FALSE)
}

plot_type1_input <- list()
plot_type2_input <- list()
plot_type3_input <- list()
for (feature in features) {
  plot_type1_input[[feature]] <- ggplot(df4[which(is.na(df4$trial_type1)==FALSE),], aes_string(x=feature, group="trial_type1", fill="trial_type1")) + geom_density(alpha=0.25) + facet_grid(~trial_block)
  plot_type2_input[[feature]] <- ggplot(df4[which(is.na(df4$trial_type2)==FALSE),], aes_string(x=feature, group="trial_type2", fill="trial_type2")) + geom_density(alpha=0.25) + facet_grid(~trial_block)
  plot_type3_input[[feature]] <- ggplot(df4[which(is.na(df4$trial_type3)==FALSE),], aes_string(x=feature, group="trial_type3", fill="trial_type3")) + geom_density(alpha=0.25) + facet_grid(~trial_block)
}

## mostly the same results as last time. No big difference between mouse and touch in terms of the effects


### Effects of nudges
## do people comply with nudges?
df4$direction <- factor(df4$direction, exclude = NA)
fit_comply <- glmer(direction~nudging_direction+(1|ppn), df4, family="binomial") # people did not choose more in line with nudges
fit_comply_health <- glmer(direction~nudging_direction+(1|ppn), df4[which(df4$trial_type=="health"),], family="binomial") # no
fit_comply_taste <- glmer(direction~nudging_direction+(1|ppn), df4[which(df4$trial_type=="taste"),], family="binomial") # no

## do people choose more healthier food in health nudging condition?
df4$SC_outcome <- factor(df4$SC_outcome, exclude = NA)
fit_SC_nudge <- glmer(SC_outcome~trial_type+(1|ppn), df4, family = "binomial") # no effect, even a trend in the negative direction for health nudge

# some other influences
fit_SC_goal <- glmer(SC_outcome~goal_health+(1|ppn), df4, family = "binomial")
fit_SC_hunger <- glmer(SC_outcome~hunger+(1|ppn), df4, family = "binomial")
fit_SC_diet <- glmer(SC_outcome~diet+(1|ppn), df4, family = "binomial")
df4$tsc <- apply(data.frame(df4$tsc1, df4$tsc2, df4$tsc3, df4$tsc4, df4$tsc5, df4$tsc6, df4$tsc7, df4$tsc8, df4$tsc9, df4$tsc10, df4$tsc11, df4$tsc12, df4$tsc13), 1, mean)
fit_SC_tsc <- glmer(SC_outcome~tsc+(1|ppn), df4, family = "binomial")
# no effects for anything

## general nudging effects on parameters
plot_nudge <- list()
for (feature in features) {
  plot_nudge[[feature]] <- ggplot(df4, aes_string(x=feature, group="trial_type", fill="trial_type")) + geom_density(alpha=0.25)
}
# no effects whatsoever


## effects on parameters depending on trial types
df4$nudge <- rep(NA, nrow(df4))
for (i in 1:nrow(df4)) {
  if (df4$trial_type[i] != "control") {
    if (df4$nudging_direction[i] == df4$direction[i]) {
      df4$nudge[i] <- "For"
    } else {
      df4$nudge[i] <- "Against"
    }
  } else {
    df4$nudge[i] <- "No"
  }
}

# only look at health nudge and trial_type3
df5 <- df4[which(df4$trial_type!="taste"),]
fit_nudge_health <- list()
for (feature in features) {
  fit_nudge_health[[feature]] <- lmer(as.formula(paste0(feature, "~1+nudge*trial_type3+(1|ppn)")), df5, REML=FALSE)
}

plot_nudge_health <- list()
for (feature in features) {
  plot_nudge_health[[feature]] <- ggplot(df5[which(is.na(df5$trial_type3)==FALSE),], aes_string(x=feature, group="nudge", fill="nudge")) + geom_density(alpha=0.25) + facet_grid(~trial_type3)
}

# only look at health and consistency
df4$consistent <- rep(NA, nrow(df4))
df4$consistent[which(df4$consistency==1)] <- "Consistent"
df4$consistent[which(df4$consistency<1)] <- "Not Consistent"
df4$consistent <- factor(df4$consistent, exclude = NA)
plot_nudge_health2 <- list()
for (feature in features) {
  plot_nudge_health2[[feature]] <- ggplot(df4[which(is.na(df4$consistent)==FALSE),], aes_string(x=feature, group="nudge", fill="nudge")) + geom_density(alpha=0.25) + facet_grid(~consistent)
}

fit_nudge_health2 <- list()
for (feature in features) {
  fit_nudge_health2[[feature]] <- lmer(as.formula(paste0(feature, "~1+nudge*consistent+(1|ppn)")), df4, REML=FALSE)
}

## make plots for nudging effects in different conditions
plot_nudge <- list()
fit_nudge <- list()
for (feature in features) {
  fit_nudge[[feature]] <- lmer(as.formula(paste0(feature, "~1+nudge*consistent*trial_block+(1|ppn)")), df4[which(is.na(df4$consistent)==FALSE),], REML=FALSE)
  data <- summarySE(df4[which(is.na(df4$consistent)==FALSE),], measurevar = feature, groupvars = c("trial_block", "nudge", "consistent"))
  plot_nudge[[feature]] <- ggplot(data, aes_string(x="nudge", y=feature, group="consistent", color="consistent")) + geom_point() + geom_line() + 
    facet_grid(~trial_block) + geom_errorbar(aes_string(ymin=paste0(feature, "-ci"), ymax=paste0(feature, "+ci")), width=0.3)
}


plot_nudge2 <- list()
fit_nudge2 <- list()
for (feature in features) {
  fit_nudge2[[feature]] <- lmer(as.formula(paste0(feature, "~1+nudge*trial_type3*trial_block+(1|ppn)")), df4[which(is.na(df4$trial_type3)==FALSE),], REML=FALSE)
  data <- summarySE(df4[which(is.na(df4$trial_type3)==FALSE),], measurevar = feature, groupvars = c("trial_block", "nudge", "trial_type3"))
  plot_nudge2[[feature]] <- ggplot(data, aes_string(x="nudge", y=feature, group="trial_type3", color="trial_type3")) + geom_point() + geom_line() + 
    facet_grid(~trial_block) + geom_errorbar(aes_string(ymin=paste0(feature, "-ci"), ymax=paste0(feature, "+ci")), width=0.3)
}


### what if trials with more than 1 commitment are removed (so only subtle continuous differences can have effects, a strong use of mouse-tracking)
df5 <- df4[which(df4$commitment <= 1),] # remove 1177 trials, 16.7%
fit_type_before <- list()
fit_type_after <- list()
for (feature in features) {
  fit_type_before[[feature]] <- lmer(as.formula(paste0(feature, "~1+trial_type3+(1|ppn)")), df4, REML=FALSE)
  fit_type_after[[feature]] <- lmer(as.formula(paste0(feature, "~1+trial_type3+(1|ppn)")), df5, REML=FALSE)
}

# AUC: 0.7% to 0.04%
# MD: 1.5% to 0.1%
# min_distance: 1.6% to 0.2%
# x_flip: 0.9% to 0.4%
# drag_time: 3.5% to 2.5%
# MV: 0.4% to 1.1%
# MA: 1.8% to 1.7%



fit_choice_type_before <- list()
fit_choice_type_after <- list()
for (feature in features) {
  fit_choice_type_before[[feature]] <- lmer(as.formula(paste0(feature, "~1+utility_dif3+utility_ave3+trade_off+(1|ppn)")), df4, REML=FALSE)
  fit_choice_type_after[[feature]] <- lmer(as.formula(paste0(feature, "~1+utility_dif3+utility_ave3+trade_off+(1|ppn)")), df5, REML=FALSE)
}


# AUC: 4.5% to 0.6%
# MD: 9.5% to 1.8%
# min_distance: 9.1% to 2.0%
# x_flip: 2.5% to 0.9%
# drag_time: 9.9% to 7.5%
# MV: 0.5% to 3.3%
# MA: 5.3% to 5.7%

## so it seems spatial parameters depend a lot on extreme trials where at least one choice commitment is made before the final choices, whereas temporal parameters were affected much less. 
## But this would also mean that trajectories are not continuous measure of choice conflicts...and when no change of mind happens, decision time is still the best parameter, which can be measured without mouse-tracking


## follow the script analysis.R
df4$sep <- df4$trade_off
df4$trade_off <- rep(NA, nrow(df4))
for (i in 1:nrow(df4)) {
 if (df4$sep[i] >= 0) {
   df4$trade_off[i] <- "No"
 } else {
   if (df4$trade_off_health1[i] >= 0 && df4$trade_off_taste1[i] >= 0) {
     df4$trade_off[i] <- "Yes"
   } else {
     df4$trade_off[i] <- NA
   }
 }
}
df4$trade_off <- factor(df4$trade_off, exclude=NA)

df4$utility_dif3_c <- df4$utility_dif3 - mean(df4$utility_dif3, na.rm=TRUE)

df4$utility_ave1 <- apply(data.frame(df4$utility_L1, df4$utility_R1), 1, mean)
df4$utility_ave2 <- apply(data.frame(df4$utility_L2, df4$utility_R2), 1, mean)
df4$utility_ave3 <- apply(data.frame(df4$utility_L3, df4$utility_R3), 1, mean)

df4$utility_high1 <- apply(data.frame(df4$utility_L1, df4$utility_R1), 1, max)
df4$utility_high2 <- apply(data.frame(df4$utility_L2, df4$utility_R2), 1, max)
df4$utility_high3 <- apply(data.frame(df4$utility_L3, df4$utility_R3), 1, max)

df4$trade_off_score <- df4$trade_off_health3 * df4$trade_off_taste3

theme_set(theme_bw())
fit_choice_type <- list()
plot_choice_type <- list()
for (feature in features) {
  fit_choice_type[[feature]] <- lmer(as.formula(paste0(feature, "~1+utility_dif3+utility_high3+trade_off+(1|ppn)")), df4, REML=FALSE)
  plot_choice_type[[feature]] <- ggplot(df4[which(is.na(df4$trade_off)==FALSE),], aes_string(x="utility_dif3", y=feature, group="trade_off", color="trade_off")) + geom_point(alpha=0.3)
}

df_hard <- df4[which(df4$utility_dif3<=2),]
fit_hard_type <- list()
plot_hard_type <- list()
for (feature in features) {
  fit_hard_type[[feature]] <- lmer(as.formula(paste0(feature, "~1+trade_off*utility_dif3_c+(1|ppn)")), df_hard, REML=FALSE)
  plot_hard_type[[feature]] <- ggplot(df_hard[which(is.na(df_hard$trade_off)==FALSE),], aes_string(x=feature, group="trade_off", color="trade_off")) + geom_density(alpha=0.3)
}


df5 <- df4[which(df4$commitment <= 1),]
theme_set(theme_bw())
fit_choice_type2 <- list()
plot_choice_type2 <- list()
for (feature in features) {
  fit_choice_type2[[feature]] <- lmer(as.formula(paste0(feature, "~1+utility_dif3+utility_high3+trade_off+(1|ppn)")), df5, REML=FALSE)
  plot_choice_type2[[feature]] <- ggplot(df5[which(is.na(df4$trade_off)==FALSE),], aes_string(x="utility_dif3", y=feature, group="trade_off", color="trade_off")) + geom_point(alpha=0.3)
}



fit_choice_type_re <- list()
for (feature in features) {
  fit_choice_type_re[[feature]] <- lmer(as.formula(paste0(feature, "~1+utility_dif3+utility_high3+trade_off+(1+utility_dif3+utility_high3+trade_off|ppn)")), df4, REML=FALSE)
}
