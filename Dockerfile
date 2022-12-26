# setup Docker image for reproducibility
# Copyright (C) 2022  Konstantin Emil Thiel

# get ubuntu 20.04 (focal) with R=4.1.2 installed
FROM rocker/r-ver:4.2.1

# install pdflatex(+packages), pip, and a system dependency for R's data.table package
RUN apt-get update && \
    apt-get install -y \
        texlive-latex-extra \
        python3-pip \
        zlib1g-dev

# install R devtools in order to install specific package versions later
RUN Rscript -e 'options(warn = 2); \
    install.packages("devtools")'

# install R packages
RUN Rscript -e 'options(warn = 2); \
    library(devtools); \
    install_version("ggplot2", "3.3"); \
    install_version("optparse", "1.7.3"); \
    install_version("data.table", "1.14"); \
    install_version("dplyr", "1.0.10"); \
    install_version("nparLD", "2.2"); \
    install_version("jsonlite", "1.8.3");'

# create non-root user but don't switch yet (non-daemon users usually start at 1000)
ARG USERNAME=reproducer
ARG UID=1000
ARG GID=$UID
RUN groupadd --gid $GID $USERNAME \
    && useradd --uid $UID --gid $GID -m $USERNAME  

# copy sources and change directory
COPY --chown=$UID:$GID . /home/$USERNAME/rr-bimj
WORKDIR /home/$USERNAME/rr-bimj

# install the provided ./ebstatmax/simUtils R package (dependencies already installed above)
RUN Rscript -e 'devtools::install("./ebstatmax/simUtils", dependencies=FALSE)'

# install python packages (python 3.8.10 is pre-installed)
RUN pip install -r requirements.txt

# switch to non-root user and run reproducibility script on container start
USER $USERNAME
CMD ["python3", "reproduce.py"]
