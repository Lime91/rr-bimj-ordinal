# rr-bimj-ordinal
Reproducible Research Supplement for a Publication in Biometrical Journal
Copyright (C) 2022  Konstantin Emil Thiel

rr-bimj-ordinal is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

rr-bimj-ordinal is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Content

Main element is the `reproduce_all_tables.py` script, which generates all tables from the submitted paper.
Some of the script's functionalities are outsourced to the `utils` module.
`reproduce_all_tables.py` calls the `ebstatmax` simulation framework repeatedly to compute type-I errors and power of the investigated statistical testing procedures.
`ebstatmax` is provided as a `git subtree`.
See `ebstatmax/README.md` for further documentation of the simulation framework itself.
`r-script/` provides additional scripts that compute data for p-value tables.
These scripts are also executed by `reproduce_all_tables.py`.

Note that all tables are generated as `tex` files and additionally compiled to `pdf`.
