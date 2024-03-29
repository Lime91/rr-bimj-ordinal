% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/functions.R
\name{perform_test}
\alias{perform_test}
\title{Perform Hypothesis Test}
\usage{
perform_test(data, options, config)
}
\arguments{
\item{data}{\code{data.table} with the simulation data}

\item{options}{\code{list} with user-defined command line arguments}

\item{config}{\code{list} with further arguments

\code{options$method} is the selected statistical testing procedure.
\code{options$target} contains the name of the target variable in data.
\code{config$first_period_end} is the last point of time that belongs to the first
study period.
\code{config$time_variable} is the name of the variable containing timepoints in
data.
\code{config$subject_variable} is the name of the variable that identifies
subjects in data.
\code{config$group_variable} is the name of the group variable in data.
\code{config$alpha} is the type-I error rate.
Moreover, options and config must contain all entries required by
\code{discard_baseline}.}
}
\value{
a list with keys \code{period_1}, \code{period_2}, and \code{combined}. The
associated values are \code{TRUE} if the null hypothesis has been rejected and
\code{FALSE} otherwise. Moreover, \code{NA} is assigned if the test could not be
performed.
}
\description{
Execute statistical testing procedure selected by user.
}
