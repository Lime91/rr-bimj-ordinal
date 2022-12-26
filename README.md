# rr-bimj-ordinal
Reproducible research supplement for the submission by Geroldinger et al. in Biometrical Journal: *A neutral comparison of statistical methods for analyzing longitudinally measured ordinal outcomes in rare diseases*.


## Content

This project's main item is `reproduce.py`, which generates all simulation results from the submitted paper, mainly by invoking `ebstatmax/diacerein.R` repeatedly to compute type-I errors and power of the investigated statistical testing procedures (GPC variants as well as nparLD).
Moreover, `reproduce.py` executes the scripts in `r-script/` to generate additional tables and figures.
The `utils/` python module provides functions for these tasks.

`ebstatmax/` is a git subtree that provides a standalone simulation framework, including the original study data used in our simulations.
Documentation is available in `ebstatmax/README.md`.

`Diacerein_80-matched.txt` contains a subset of the original study data and is used as an extra input for some simulations.

Note that all tables are generated as `tex` files and additionally compiled to `pdf`.
This is done with the `pythontex` package.

Reproducing all results using this supplement takes several hours of time.
All code is executed sequentially (not in parallel).
On a machine with an *AMD Ryzen 7 PRO 4750U* CPU, the runtime of `reproduce.py` is approximately 20 hours.

## Requirements

### Run as a Docker Container

The easiest way to reproduce all results is to use Docker.
A `Dockerfile` is provided for that purpose.
Execute the following commands:
  - `sudo docker build . -t rr-bimj:latest`. This builds a new image.
  - `sudo docker run -it --name rr-bimj rr-bimj:latest`. This sets up a new container from the image and executes `reproduce.py` in this container.

When `reproduce.py` is finished (presumably after several hours of computation), the container stops and results can be obtained from it.
Use the following commands:
  - `sudo docker cp rr-bimj:/home/reproducer/rr-bimj/results ./results` to copy all tables into a local directory `./results`.
  - `sudo docker cp rr-bimj:/home/reproducer/rr-bimj/raw-output ./raw-output` to copy intermediate simulation outputs into a local directory `./raw-output`.

See the provided `Dockerfile` for details.


### Run Locally

In order to run `reproduce.py` without Docker, the folowing requrements must be met:

This project was mainly developed on `ubuntu20.04` operating system using `python3.8.10`.
All python packages listed in `requirements.txt` are needed.
Moreover, `R==4.2.1` and all packages listed in `ebstatmax/README.md` are required. 
Another requirement is the `pdflatex` compiler and several latex packages used by `pythontex`, which can be installed on ubuntu with `apt-get install texlive-latex-extra`.

Once these requirements are met, execute the following commands:
  - `sudo Rscript -e "devtools::install('ebstatmax/simUtils', dependencies=F)"`. This installs the `simUtils` package required by the `ebstatmax` simulation framework.
  - `python3 reproduce.py`.

Wait for the python interpreter to terminate again (which is expected after several hours of runtime).
Results can be found in a newly created `results/` directory and intermediate simulation outputs are in `raw-output/`.

## Copyright

Copyright (C) 2022  Konstantin Emil Thiel

rr-bimj-ordinal is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

rr-bimj-ordinal is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
