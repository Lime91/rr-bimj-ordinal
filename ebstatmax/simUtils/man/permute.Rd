% Generated by roxygen2: do not edit by hand
% Please edit documentation in R/functions.R
\name{permute}
\alias{permute}
\title{Permute Target Variable Values}
\usage{
permute(data, target, blocklength)
}
\arguments{
\item{data}{\code{data.table} with the simulation data}

\item{target}{name of the target variable column in data}

\item{blocklength}{number of measurements in a block}
}
\description{
Permutation distributes the target variable randomly across study subjects.
More precisely, the target variable is distributed across study entities.
Each study entity consists of a uniformly sized block of target variable
measurements for one subject. The measurements are permuted across these
entities, but not within a block.
}
\details{
\code{data} will be modified in place.
}
