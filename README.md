# rr-bimj-ordinal
Reproducible Research Supplement for a Publication in Biometrical Journal

## Content

Main element is the `reproduce_all_tables.py` script, which generates all tables from the submitted paper.
Some of the script's functionalities are outsourced to the `utils` module.
`reproduce_all_tables.py` calls the `ebstatmax` simulation framework repeatedly to compute type-I errors and power of the investigated statistical testing procedures.
`ebstatmax` is provided as a `git subtree`.
See `ebstatmax/README.md` for further documentation of the simulation framework itself.
`r-script/` provides additional scripts that compute data for p-value tables.
These scripts are also executed by `reproduce_all_tables.py`.

Note that all tables are generated as `tex` files and additionally compiled to `pdf`.
This is done with the `pythontex` package.

## Requirements

### Run as a Docker Container

The easiest way to reproduce all tables is to use Docker.
A `Dockerfile` is provided for that purpose.
Execute the following commands:
  - `sudo docker build . -t rr-bimj:latest`. This builds a new image.
  - `sudo docker run -it --name rr-bimj rr-bimj:latest`. This sets up a new container from the image and executes `reproduce_all_tables.py` in this container.

When `reproduce_all_tables.py` is finished (presumably after several hours of computation), the container stops and tables can be obtained from it.
Use the following commands:
  - `sudo docker cp rr-bimj:/home/reproducer/rr-bimj/tables ./tables` to copy all tables into a local directory `./tables`.
  - `sudo docker cp rr-bimj:/home/reproducer/rr-bimj/raw-output ./raw-output` to copy intermediate simulation results into a local directory `./raw-output`.

See the provided `Dockerfile` for details.


### Run Locally

In order to run `reproduce_all_tables.py` without Docker, the folowing requrements must be met:

rr-bimj-ordinal was mainly developed using the `ubuntu20.04` operating system and `python3.8.10`.
All python packages listed in `requirements.txt` are needed.
Moreover, `R>=3.6.3` and all packages listed in `ebstatmax/README.md` are required. 
Another requirement is the `pdflatex` compiler and several latex packages used by `pythontex`, which can be installed on ubuntu with `apt-get install texlive-latex-extra`.

Once these requirements are met, execute the following commands:
  - `sudo Rscript -e "devtools::install('ebstatmax/simUtils', dependencies=F)"`. This installs the `simUtils` package required by the `ebstatmax` simulation framework.
  - `python3 reproduce_all_tables.py`.

Wait for the python interpreter to terminate again (this is likely to take several hours).
Once the computation is finished, tables can be found in a newly created `tables/` directory and intermediate simulation results are in `raw-output/`.

## Copyright

Copyright (C) 2022  Konstantin Emil Thiel

rr-bimj-ordinal is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

rr-bimj-ordinal is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
