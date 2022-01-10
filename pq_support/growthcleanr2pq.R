# import libraries
library(growthcleanr)
library(data.table)
library(dplyr)

# BMI categorizing formulas
source("bmi_selection.R")

# BMI chart (used in BMI categorization)
bmi_chart = read.csv("bmiagerev.csv")

# CONFIGURATION
MY_CLEANED_DATA_FILENAME <- "my_cleaned_data.csv"
MY_DEMOGRAPHIC_DATA_FILENAME <- "my_demographic_data.csv"
MY_PQ_READY_OUTPUT_DATA_FILENAME <- "my_pq_ready_data.csv"

# load data that has gone through growthcleanr
growthclean_df <- read.csv(MY_CLEANED_DATA_FILENAME)

growthclean_df$DATE <- as.Date(growthclean_df$DATE)
growthclean_df$sex <- as.numeric(growthclean_df$sex)
# convert data to wide
wide_df <- growthcleanr::longwide(growthclean_df)
# BMI calculation
wide_df_with_bmi <- simple_bmi(wide_df, wtcol = "wt", htcol = "ht")
# create variable for merging year data back in
wide_df_with_bmi$subage <-
  paste0(wide_df_with_bmi$subjid, wide_df_with_bmi$agedays)
growthclean_df$subage <-
  paste0(growthclean_df$subjid, growthclean_df$agedays)
# merge growthcleanr data back in so to pull in year data for demo matching.
# Selected only include lines and using just the weight lines for cleanliness. Left Join
merged_df <-
  merge(
    wide_df_with_bmi,
    growthclean_df [(growthclean_df$param == "WEIGHTKG") &
                      (growthclean_df$gcr_result == "Include"), ],
    by.x = "subage",
    by.y = "subage",
    all.x = T
  )

# filter to columns that we need
merged_df_s <-
  merged_df[, c("subjid.x",
                "bmi",
                "agey",
                "agem",
                "agedays.x",
                "DATE",
                "sex.y",
                "wt",
                "ht")]
# renaming columns
merged_df_s <-
  setnames(
    merged_df_s,
    old = c("subjid.x", 'agedays.x', "sex.y", "agem"),
    new = c('subjid', 'agedays', "sex", "agemonths")
  )
names(merged_df_s) <- colnames(merged_df_s)
# creating year column
merged_df_s$year <-  format(merged_df_s$DATE, format = "%Y")



# sort into adult and ped dataframes
adult_df <- merged_df_s %>% filter(agey >= 20)

ped_df <- merged_df_s %>% filter(agey < 20)

# bmi categorization
adult_df$category <- computeAdultBMICategory(bmi = adult_df$bmi)
ped_df$category <- sapply(1:nrow(ped_df), function(x) {
  computePediatricBMICategory(as.numeric(ped_df[x, "bmi"]),
                              as.numeric(ped_df[x, "sex"]),
                              as.numeric(ped_df[x, "agemonths"]))
})

# creating one dataset
cleaned_df <- rbind(adult_df, ped_df)

# load demographic data for merging with cleaned data
demo_df <-
  read.csv(MY_DEMOGRAPHIC_DATA_FILENAME, stringsAsFactors = F) %>% select(!X)

# merge cleaned_df with demographics
full_df <- merge(cleaned_df,
                 demo_df,
                 by = c("subjid", "year"),
                 all.x = T)
# removing those who BMI category was unknown
full_df <- full_df[!full_df$category == "UNKNOWN",]
# Dropping multiple instances in one year, keeping the instance where the person age is largest
full_df <- full_df[order(full_df$agedays, decreasing = TRUE),]
full_df <- setDF(full_df)
full_df <-
  full_df[!(duplicated(full_df[c("subjid", "year")], fromLast = TRUE)), ]
# dropping rows without demographic information
final_df <- full_df[!is.na(full_df$ZIP), ]
# rounding agey to integer
final_df$agey <- round(final_df$agey, digits = 0)

final_df <-
  final_df[, c(
    "subjid",
    "sex",
    "agey",
    "race",
    "state",
    "site_location",
    "ht",
    "wt",
    "bmi",
    "category",
    "year"
  )]
final_df <-
  data.table::setnames(
    final_df,
    old = c("sex", "agey", 'race', "state", "ht", "wt", "category"),
    new = c(
      "SEX_NUM",
      'AGEYEARS',
      'ETHNICITY',
      "SITE_KEY",
      "HEIGHT_MEASUREMENT",
      "WEIGHT_MEASUREMENT",
      "WEIGHT_CATEGORY"
    )
  )
final_df$ETHNICITY <- toupper(final_df$ETHNICITY)
names(final_df) <- toupper(colnames(final_df))

write.csv(final_df, MY_PQ_READY_OUTPUT_DATA_FILENAME)
