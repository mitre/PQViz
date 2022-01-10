#!/usr/bin/env Rscript

library(argparser)
library(data.table)

library(growthcleanr)

# CONFIGURATION
MY_INPUT_FILENAME <- "my_observation_data.csv"
MY_OUTPUT_FILENAME <- "my_cleaned_data.csv"

# See growthcleanr documentation for details
adult_cutpoint = 20 # use default
weight_cap = Inf  # use default


# START HERE
argv <- list()

log.path <-
  sprintf("output-log_%s_%s", Sys.Date(), MY_INPUT_FILENAME)

# HERE: using default
argv$sdrecenter <- ""
if (argv$sdrecenter != "") {
  if (argv$sdrecenter == "nhanes") {
    sdrecenter = "nhanes"
  } else {
    sdrecenter <- fread(argv$sdrecenter)
  }
} else {
  sdrecenter <- ""
}

# HERE: TRUE
parallel <- TRUE
num.batches <- 11

# HERE: read in csv file with data
df_in <- fread(MY_INPUT_FILENAME)
df_in$id_order <- 1:nrow(df_in)

# handle adult split arguments
# HERE: how many splits for your data do you want
adult_split <- 100

# we'll process the adult data using a split, then do the work
if (adult_split < Inf &
    length(unique(df_in$subjid)) < adult_split) {
  adult_split <- length(unique(df_in$subjid))
}

if (adult_split < Inf & adult_split > 1) {
  # will warn if they're not exact multiples
  # split by subject
  subj_split <-
    suppressWarnings(split(unique(df_in$subjid), 1:adult_split))
  # map indices to subjects
  # subj_split <- data.frame(
  #   entry = rep(seq_along(subj_split), length(subj_split)),
  #   subjid = as.character(unlist(subj_split))
  # )
  subj_split_df <- data.frame()
  for (spl in 1:length(subj_split)) {
    subj_split_df <- rbind(subj_split_df,
                           data.frame("entry" = spl,
                                      "subjid" = as.character(subj_split[[spl]])))
  }
  df_in$subjid <- as.character(df_in$subjid)
  
  # add batch to df_in
  df_in <- merge(df_in, subj_split_df, by = "subjid")
  
  # split based on subject id
  split.list <- suppressWarnings(split(df_in, df_in$entry))
  
} else {
  # no need for copy, they can refer to the same thing
  split.df <- df_in
  adult_split <- 1 # for Inf, just converting for later
}

quietly <- argv$quietly <- F # use FALSE

# do split based on number of adult splits
df_out <- lapply(1:adult_split, function(x) {
  if (!argv$quietly) {
    cat(
      sprintf(
        "[%s] Processing adult data split %g, using %d batch(es)...\n",
        Sys.time(),
        x,
        num.batches
      )
    )
  }
  
  if (adult_split > 1) {
    split.df <- split.list[[x]]
  } # otherwise, split adult has already been created
  
  # Separate the logs or they'll overwrite each other
  split.log.path <- sprintf("%s_split-%03d", log.path, x)
  
  split.df$gcr_result <- cleangrowth(
    split.df$subjid,
    split.df$param,
    split.df$agedays,
    split.df$sex,
    split.df$measurement,
    sd.recenter = sdrecenter,
    adult_cutpoint = adult_cutpoint,
    weight_cap = weight_cap,
    log.path = split.log.path,
    num.batches = num.batches,
    parallel = parallel,
    quietly = quietly
  )
  
  return(split.df)
})

# put all the splits together
df_out <- rbindlist(df_out)
# get it in the original order
df_out <- df_out[order(df_out$id_order),]
# remove indexing variables
idx_var <- if (adult_split == 1) {
  c("id_order")
} else {
  c("id_order", "entry")
}
df_out <- df_out[, !idx_var, with = FALSE]

# HERE: replace argv$outfile with filename
fwrite(df_out, MY_OUTPUT_FILENAME, row.names = FALSE)
