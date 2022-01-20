# pq-support

Additional R code to support the
[CODI-PQ project](https://github.com/NORC-UChicago/CODI-PQ).

This outlines the steps need that need to be taken to format the data so that it
can be processed through the PQ algorithm.

## Target data format for CODI-PQ

To process data with CODI-PQ, it should first be processed through growthcleanr,
and then transformed into the format specified in the table below, with each row
representing one encounter.

| Column             | Description                                                 | Variable type | Valid Values                                                             |
| ------------------ | ----------------------------------------------------------- | ------------- | ------------------------------------------------------------------------ |
| SUJID              | Patient Identifier                                          | Integer       | PQ will not accept Alphanumeric inputs                                   |
| SEX_NUM            | Patient's sex at birth, where 0 is male, 1 is female        | Integer       | 0 or 1                                                                   |
| AGEYEARS           | Patient’s age in years at the time of the medical encounter | Integer       | Must be a rounded number                                                 |
| ETHNICITY          | Patient’s race if known or ethnicity if race is not known   | Character     | AFRICAN AMERICAN, ASIAN, CAUCASIAN, HISPANIC, OTHER, UNKNOWN             |
| SITE_KEY           | Patient’s residential state, two-letter state abbreviations | Character     | AL, AK, AZ, ... , WY                                                     |
| SITE LOCATION      | Patient’s residential ZCTA-3 (first 3 digits of ZCTA code)  | Integer       | 3 digit number                                                           |
| HEIGHT_MEASUREMENT | Patient’s height in cm                                      | Float         | Any number greater than 0                                                |
| WEIGHT_MEASUREMENT | Patient’s weight in kg                                      | Float         | Any number greater than 0                                                |
| BMI                | Calculated BMI                                              | Float         | Any number greater than 0                                                |
| WEIGHT_CATEGORY    | Patient’s weight category                                   | Character     | Normal or Healthy Weight, Obese, Overweight, Severe Obesity, Underweight |
| YEAR               | Year of the medical encounter                               | Integer       | yyyy                                                                     |

## Preparing EHR data for CODI-PQ

The process of preparing EHR data for use with CODI-PQ requires three steps:

- Separate demographic data
- Clean data with growthcleanr
- Select and classify BMI values

### Separate demographic data

In the next step, growthcleanr does not require demographic information such as
ethnicity or clinical site. You may wish to separate these values into a
distinct file prior to data cleaning to keep your cleaning file input lean. A
later step, during selecting and classifying BMI data, provides a good spot to
re-join these values.

### Clean data with growthcleanr

The [growthcleanr](https://github.com/carriedaymont/growthcleanr) R package
provides an algorithm for cleaning anthropomorphic EHR data, specifically height
and weight observations for pediatric (2-18 years old) and adult (18-65)
subjects. The [growthcleanr
documentation](https://carriedaymont.github.io/growthcleanr/index.html) provides
a (Quickstart
guide)[https://carriedaymont.github.io/growthcleanr/articles/quickstart.html]
and full details about the specification of data required to use growthcleanr
and how to interpret its output. The growthcleanr package also provides utility
functions for reshaping data and computing values such as BMI.

If you have a large number of observations (typically, more than one million
individual height and weight records), the growthcleanr algorithm can take some
time to run. The optional script `growthcleanr_batching.R` provides an example
of processing a large data set using the batching options growthcleanr provides.
It is not required, and is provided as a template that researchers may use. Note
also that with large sets of observations, removing demographic data not
required by growthcleanr (such as ethnicity and clinical site details) may help
keep file sizes small.

If you want to use `growthcleanr_batching.R`, note that there are two
configurable file names at the top of the script (see the section labelled
`# CONFIGURATION`) which you should fill in to point to your input data and what
you want the output file to be called.

The next step uses the output of growthcleanr to prepare data for CODI-PQ.

## Select and classify BMI value

Data that has been run though growthcleanr has the same format as growthcleanr
input, with an added column containing the growthcleanr cleaning assessment.
This output data is ready to run through BMI calculation, selection, and
classification. The script `growthcleanr2pq.R` takes configuration values for
your cleaned data file name, your demographic file name (assuming you separated
these columns prior to cleaning), and the name of the CODI-PQ-ready output file
to save classified BMI values to. Set these values under the section commented
with `# CONFIGURATION`. The script handles both pediatric and adult data.

This script will create a csv that is in a format ready to be run through
CODI-PQ.
