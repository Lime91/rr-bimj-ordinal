# get ubuntu 20.04 (focal) with R=4.1.2 installed
FROM rocker/r-ver:4.1.2

# install system dependencies for R's data.table package and for python
RUN apt-get update && \
    apt-get install -y \
        zlib1g-dev \
        python3-pip

# install R devtools in order to install specific package versions later
RUN Rscript -e 'install.packages("devtools")'

# install R packages
RUN Rscript -e 'library(devtools); \
    install_version("optparse", "1.7.1"); \
    install_version("data.table", "1.12.8"); \
    install_version("dplyr", "1.0.7"); \
    install_version("nparLD", "2.1"); \
    install_version("jsonlite", "1.7.2");'

# copy sources and change directory
COPY ./* /home/$USERNAME/rr-bimj-working-directory
WORKDIR /home/$USERNAME/rr-bimj-working-directory

# install the provided ./ebstatmax/simUtils R package (dependencies already installed above)
RUN Rscript -e 'devtools::install("./ebstatmax/simUtils", dependencies=FALSE)'

# install python packages (python 3.8.10 is pre-installed)
RUN pip install -r requirements.txt

# switch to non-root user (non-daemon users usually start at 1000)
ARG USERNAME=rr-bimj-user
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# create non-root user
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME  
USER $USERNAME

# run reproducibility script on container start
CMD ["python3", "reproduce_all_tables.py"]
