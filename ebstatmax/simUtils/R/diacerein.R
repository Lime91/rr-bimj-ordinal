#' Original Diacerein Study Data
#'
#' Collected by Wally et al. (2018) "Diacerein orphan drug development for 
#' epidermolysis bullosa simplex: A phase 2/3 randomized, placebo-controlled, 
#' double-blind clinical trial"
#' https://www.sciencedirect.com/science/article/pii/S0190962218301300
#'
#' @format A `data.table` with 112 rows and 8 variables:
#' \describe{
#'   \item{Id}{patient identifier}
#'   \item{Time}{timepoints (study nurse visits), encoded as integers}
#'   \item{Group}{either 'P' (placebo) or 'V' (verum)}
#'   \item{Blister_count}{number of blisters counted on a given part of the 
#' patient's skin surface}
#'   \item{Pruritus}{sensed by the patient, measured on a VAS}
#'   \item{Pain}{sensed by the patient, measured on a VAS}
#'   \item{Completed.years}{some comments}
#'   \item{Comments}{additional comments}
#' }
"diacerein"
