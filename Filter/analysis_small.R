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