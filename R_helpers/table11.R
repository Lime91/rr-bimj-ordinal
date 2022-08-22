#!/usr/bin/Rscript

############################################################################
# this script is designed to reproduce Table 11 of the ordinal outcome paper
############################################################################

# get target variable from command line
args <- commandArgs(trailingOnly=TRUE)
TARGET <- ifelse(length(args) > 0, args[[1]], "Pain")


# load simUtils package
if (!suppressPackageStartupMessages(require(simUtils)))
  suppressMessages(devtools::load_all("../../ebstatmax/simUtils"))
devtools::load_all("../../ebstatmax/simUtils")


# global parameters for GPC
SIDE <- 1  # one-sided test
BEST <- "lower"  # lower VAS values are prefered
REPEATED <- simUtils::CONFIG$repeated_priority  # timepoint prioritization order
VERBOSE <- TRUE  # add wins & losses to the GPC result


# execute GCP and add obtain result partial data.frame
run_gpc <- function(data, target, type, matching) {
  options <- list(
    target=target,
    side=SIDE
  )
  l <- simUtils::gpc(
    data, type, REPEATED, matching, BEST, options, simUtils::CONFIG, VERBOSE)
  df <- l$win
  df["p_value"] <- rep("", nrow(df))
  df[nrow(df), "p_value"] <- round(l$combined, 4)
  if (nrow(df) == 5)
    row_names <- c("W4", "FU", "W2", "W0", "Total")
  else if (nrow(df) == 1)
    row_names <- ""
  else
    stop("wrong number of rows")
  rownames(df) <- NULL
  df <- cbind(row_names, df)
  df
}


# execute all GPC variants and collect list of data.frames
run_all_gpc <- function(target) {
  # load and prepare study data
  data("diacerein")  # provided in simUtils package
  data <- diacerein
  BLOCKLENGTH <- 4
  data <- simUtils::exclude_na_blocks(data, target, BLOCKLENGTH)
  data <- simUtils::harmonize_period_times(data, simUtils::CONFIG)
  list(
    "matched_univariate" = run_gpc(data, target, "univariate", "matched"),
    "unmatched_univariate" = run_gpc(data, target, "univariate", "unmatched"),
    "matched_prioritized" = run_gpc(data, target, "prioritized", "matched"),
    "unmatched_prioritized" = run_gpc(data, target, "prioritized", "unmatched"),
    "unmatched_non_prioritized" = run_gpc(data, target, "non-prioritized", "unmatched")
  )
}


# build single dataframe with all results
get_combined_df <- function(target) {
  dfs <- run_all_gpc(target)
  df <- rbind(dfs$matched_univariate, dfs$unmatched_univariate)
  df$row_names <- c("matched univariate GPC", "unmatched univariate GPC")
  df <- rbind(df, rep("", ncol(df)))
  df[nrow(df), 1] <- "matched prioritized GPC"
  df <- rbind(df, dfs$matched_prioritized)
  df <- rbind(df, rep("", ncol(df)))
  df[nrow(df), 1] <- "unmatched prioritized GPC"
  df <- rbind(df, dfs$unmatched_prioritized)
  df <- rbind(df, rep("", ncol(df)))
  df[nrow(df), 1] <- "unmatched non-prioritized GPC"
  df <- rbind(df, dfs$unmatched_non_prioritized)
  names(df) <- c("name", "#wins", "#losses", "#ties", "net benefit (95%CI)", "$p$-value one-sided")
  df
}


# print result to stdout
write.table(
  get_combined_df(TARGET),
  quote=TRUE,
  sep=",",
  dec= "../../ebstatmax/misc",
  row.names=FALSE
)