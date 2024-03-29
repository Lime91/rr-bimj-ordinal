% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/nparld.R
\name{nparld}
\alias{nparld}
\title{Perform Hypothesis Test with nparLD}
\usage{
nparld(data, options, config)
}
\arguments{
\item{data}{\code{data.table} with the simulation data}

\item{options}{\code{list} with user-defined command line arguments}

\item{config}{\code{list} with further arguments}
}
\value{
\code{list} of p-values for the respective tests
}
\description{
Split the dataset according to the specified period and perform a hypothesis
test.
}
\details{
\code{options$target} contains the name of the target variable in data.
\code{config$first_period_end} is the last point of time that belongs to the
first study period.
\code{config$time_variable} is the name of the variable containing timepoints in
data.
\code{config$subject_variable} is the name of the variable that identifies
subjects in data.
\code{config$group_variable} is the name of the group variable in data.
\code{config$alpha} is the type-I error rate.
}
