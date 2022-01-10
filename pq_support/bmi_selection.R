library(dplyr)
library(tidyr)
library(anytime)
library(sjmisc)

# Finds and returns the height/weight pair from the same day that are closest to the target date.
heightWeightPairClosestTo <-
  function(measurements_df, target_date) {
    # Pull the unique dates from the dataframe of measurements.
    dates <- unique(measurements_df$event_date)
    current_closest_df <-
      measurements_df %>% filter(event_date == first(dates))
    # For each of the unique dates...
    for (date in dates) {
      temp_date_df  <- measurements_df %>% filter(event_date == date)
      # Take the pair that is closest to the target date.
      temp_date  <- anytime(date)
      current_closest_date <-
        anytime(first(current_closest_df$event_date))
      # If there is at least one weight and one height measurement on the current temp_date,
      #and it is closer than the previous closest date to the target date, then update the current closest measurements.
      if ((abs(target_date - temp_date) < abs(target_date - current_closest_date)) &
          (nrow(temp_date_df[temp_date_df['param'] == 'HEIGHTCM',]) != 0) &
          (nrow(temp_date_df[temp_date_df['param'] == 'WEIGHTKG',] != 0))) {
        current_closest_df <- temp_date_df
      }
    }
    return(current_closest_df)
  }

# Performs a simple BMI calulcation based on an input height in cm and weight in kg.
computeBMI <- function(heightcm, weightkg) {
  # Source: https://www.cdc.gov/nccdphp/dnpao/growthcharts/training/bmiage/page5_1.html#:~:text=Calculation:%20[weight%20(kg)%20/%20height%20(cm)%20/%20height,in%20kilograms%20divided%20by%20height%20in%20meters%20squared.
  return((weightkg / heightcm / heightcm) * 10000)
}
# Computes the BMI category for an adult based on an input BMI.
computeAdultBMICategory <- function(bmi) {
  # Source: https://www.cdc.gov/healthyweight/assessing/bmi/adult_bmi/index.html#InterpretedAdults
  # Source: https://www.cdc.gov/obesity/adult/defining.html
  category <- if_else(bmi < 18.5,
                      "Underweight",
                      if_else(
                        bmi < 25,
                        'Normal or Healthy Weight',
                        if_else(
                          bmi < 30,
                          'Overweight',
                          if_else(
                            bmi < 35,
                            'Obesity (Class 1)',
                            if_else(bmi < 40, 'Obesity (Class 2)',
                                    'Obesity (Class 3) - Severe Obesity')
                          )
                        )
                      ))
  return(category)
}



# Computes the BMI category for a child based on the CDC Pediatric BMI Category chart.
computePediatricBMICategory <- function(bmi, sex, age_months) {
  # Source: https://gitlab.mitre.org/codi/wrangle-iqvia/-/blob/master/bmiagerev.csv
  # Calculating age months to to be the middle of their age in years.
  #age_months <- (age_years *12) + 6
  # If the value of months is close enough to it's rounded value (4 decimal places), round it.
  if (near(age_months, round(age_months), tol = 1e-4)) {
    age_months = round(age_months)
  }
  # Pull the relevant sex bmi chart for this peron's sex.
  bmi_chart_sex <-  bmi_chart %>% filter(Sex == sex)
  # Pull the relevant age bmi chart for this peron's age in months
  bmi_chart_sex_age <-
    bmi_chart_sex %>% filter(Agemos == as.integer(age_months))
  if (is_empty(bmi_chart_sex_age$P5) == TRUE) {
    # Very occasionally, a person's extracted bmi calculation chart will be empty.
    #Maurie Note: I wasnt sure if empty would come up as "  " or Nulls so I used is_empty
    #print(age_months)
    #print(bmi_chart_sex_age)
    category <- 'UNKNOWN'
  } else if (bmi < first(bmi_chart_sex_age$P5)) {
    category <- 'Underweight'
    
  } else if (bmi < first(bmi_chart_sex_age$P85)) {
    category <- 'Normal or Healthy Weight'
  } else if (bmi < first(bmi_chart_sex_age$P95)) {
    category <- 'Overweight'
  } else if (bmi < 1.2 * first(bmi_chart_sex_age$P95)) {
    category <- 'Obese'
  } else {
    category <- 'Severe Obesity'
  }
  return(category)
}
