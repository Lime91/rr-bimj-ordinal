#!/usr/bin/Rscript

################################################################################
# this script is designed to reproduce a segment of the p-value tables in the
# ordinal outcome paper.
# The script takes two command line arguments:
#   1) method (either nparld or gpc)
#   2) target variable (either Pain or Pruritus)
################################################################################


# get command line arguments
args <- commandArgs(trailingOnly=TRUE)
METHOD <- ifelse(length(args) > 0, args[[1]], "nparld")
TARGET <- ifelse(length(args) > 1, args[[2]], "Pain")
cat("method:", METHOD, "\n", file=stderr())
cat("target variable:", TARGET, "\n", file=stderr())


# load simUtils package and nparld
if (!suppressPackageStartupMessages(require(simUtils)))
  suppressMessages(devtools::load_all("../ebstatmax/simUtils"))
if (!suppressPackageStartupMessages(require(nparLD)))
  stop("could not load nparLD package")


# global parameters for GPC
SIDE <- 2  # two-sided test
BEST <- "lower"  # lower VAS values are prefered
REPEATED <- simUtils::CONFIG$repeated_priority  # timepoint prioritization order


# load and prepare study data
prepare_data <- function(target) {
  data("diacerein")  # provided in simUtils package
  data <- diacerein
  BLOCKLENGTH <- 4
  data <- simUtils::exclude_na_blocks(data, target, BLOCKLENGTH)
}


# execute nparld and add get test statistics + p_values
run_all_nparld <- function(target) {
  data <- prepare_data(target)
  query <- data[[simUtils::CONFIG$time_variable]] <= simUtils::CONFIG$first_period_end
  period1_data <- data[query]
  period2_data <- data[!query]
  form <- as.formula(paste(
    target,
    paste(simUtils::CONFIG$group_variable, simUtils::CONFIG$time_variable, sep="*"),
    sep="~"))
  capture.output(
    period1_result <- nparLD::nparLD(
      form,
      period1_data,
      subject=simUtils::CONFIG$subject_variable)$ANOVA.test,
    period2_result <- nparLD::nparLD(
      form,
      period2_data,
      subject=simUtils::CONFIG$subject_variable)$ANOVA.test
  )
  df <- data.frame(
    "test_statistic"=c(period1_result[3, 1], period2_result[3, 1]),
    "p_value"=c(period1_result[3, 3], period2_result[3, 3]),
    row.names=c("nparLD Period 1", "nparLD Period 2")
  )
  names(df) <- c("Test Statistic", "$p$-value")
  df
}



# execute GCP and add get test statistic + p_value
run_gpc <- function(data, target, type, matching) {
  options <- list(
    target=target,
    side=SIDE
  )
  l <- simUtils::gpc(
    data, type, REPEATED, matching, BEST, options, simUtils::CONFIG)
  p_value <- l$combined
  test_statistic <- qnorm(1-(p_value/2))
  data.frame("test_statistic"=test_statistic, "p_value"=p_value)
}


# execute all GPC variants and collect list of data.frames
run_all_gpc <- function(target) {
  data <- prepare_data(target)
  data <- simUtils::harmonize_period_times(data, simUtils::CONFIG)
  l <- list(
    "matched univariate GPC"=run_gpc(data, target, "univariate", "matched"),
    "unmatched univariate GPC" = run_gpc(data, target, "univariate", "unmatched"),
    "matched prioritized GPC" = run_gpc(data, target, "prioritized", "matched"),
    "unmatched prioritized GPC" = run_gpc(data, target, "prioritized", "unmatched"),
    "unmatched non-prioritized GPC" = run_gpc(data, target, "non-prioritized", "unmatched")
  )
  df <- do.call("rbind", l)
  names(df) <- c("Test Statistic", "$p$-value")
  df
}


if (METHOD == "nparld") {
  df <- run_all_nparld(TARGET)
} else if (METHOD == "gpc") {
  df <- run_all_gpc(TARGET)
} else {
  stop("unknown method")
}


# print result to stdout
write.table(
  round(df, 4),
  quote=TRUE,
  sep=",",
  dec= ".",
  row.names=TRUE
)
