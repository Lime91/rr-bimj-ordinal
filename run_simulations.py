
from subprocess import Popen, PIPE
from pandas import MultiIndex
from os.path import join
from utils import prepare_power_table, write_power_table
from typing import Iterable

# simulation program
R_PROGRAM = ["Rscript", "diacerein.R"]

# output directory structure
DIR_RAW_OUTPUT = "raw_output"
DIR_RESULT_TABLES = "tables"
SUBDIR_PAIN = "Pain"
SUBDIR_PRURITUS = "Pruritus"
SUBDIR_SCENARIO_1 = "Scenario 1"
SUBDIR_SCENARIO_2 = "Scenario 2"
OUTFILE_NORM = "norm.json"
OUTFILE_LNORM = "lnorm.json"

# raw output files
PRURITUS_S1_NORM = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_1, OUTFILE_NORM)
PRURITUS_S1_LNORM = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_1, OUTFILE_LNORM)
PRURITUS_S2_NORM = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_2, OUTFILE_NORM)
PRURITUS_S2_LNORM = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_2, OUTFILE_LNORM)
PAIN_S1_NORM = join(SUBDIR_PAIN, SUBDIR_SCENARIO_1, OUTFILE_NORM)
PAIN_S1_LNORM = join(SUBDIR_PAIN, SUBDIR_SCENARIO_1, OUTFILE_LNORM)
PAIN_S2_NORM = join(SUBDIR_PAIN, SUBDIR_SCENARIO_2, OUTFILE_NORM)
PAIN_S2_LNORM = join(SUBDIR_PAIN, SUBDIR_SCENARIO_2, OUTFILE_LNORM)

# raw files for power table
POWER_TABLE_FILE_COLUMNS = []
POWER_TABLE_FILE_COLUMNS.append((PRURITUS_S1_NORM, PRURITUS_S1_LNORM))
POWER_TABLE_FILE_COLUMNS.append((PRURITUS_S2_NORM, PRURITUS_S2_LNORM))
POWER_TABLE_FILE_COLUMNS.append((PAIN_S1_NORM, PAIN_S1_LNORM))
POWER_TABLE_FILE_COLUMNS.append((PAIN_S2_NORM, PAIN_S2_LNORM))

# simulation settings
POWER_SIMULATIONS = {
    "-t Pruritus -s 1 -e lnorm": PRURITUS_S1_LNORM,
    "-t Pruritus -s 2 -e lnorm": PRURITUS_S2_LNORM,
    "-t Pruritus -s 1 -e norm": PRURITUS_S1_NORM,
    "-t Pruritus -s 2 -e norm": PRURITUS_S2_NORM,
    "-t Pain -s 1 -e lnorm": PAIN_S1_LNORM,
    "-t Pain -s 2 -e lnorm": PAIN_S2_LNORM,
    "-t Pain -s 1 -e norm": PAIN_S1_NORM,
    "-t Pain -s 2 -e norm": PAIN_S2_NORM
}

# statistical testing methods:
METHOD_MAP = {  # maps method names (=table headers) to command line arguments
    "nparLD": "nparld"
}

def run_power_simulations(
    method: str,
    output_dir: str) -> None:

    for settings in POWER_SIMULATIONS:
        outfile = join(output_dir, POWER_SIMULATIONS[settings])
        command = "-m" + method + settings.split()
        with Popen(
            command,
            stderr=PIPE,
            stdout=open(outfile, "w"),
            bufsize=1,  # line-buffered
            text=True) as p:

            print("\n\nrunning simulations for", outfile, "...\n")
            for line in p.stderr:
                print("### ", line, end='')


def generate_power_table(
    method_names: Iterable[str],
    period: str,
    table_name: str,
    run_simulations=True) -> None:

    table_segments = []
    for method_name in method_names:
        # run simulations
        method = METHOD_MAP[method_name]
        raw_output_dir = join(DIR_RAW_OUTPUT, method)
        if run_simulations:
            run_power_simulations(method, raw_output_dir)

        # build and write table
        column_index_levels = (
            (method_name, ),
            (SUBDIR_PRURITUS, SUBDIR_PAIN),
            (SUBDIR_SCENARIO_1, SUBDIR_SCENARIO_2))
        column_index = MultiIndex.from_product(column_index_levels)
        df = prepare_power_table(
            raw_output_dir, POWER_TABLE_FILE_COLUMNS, period, column_index)
        table_segments.append(df)
    # write table to disc
    write_power_table(table_segments, table_name)


# table 1
generate_power_table(["nparLD"], "period_1", "table_1")
# table 8
generate_power_table(["nparLD"], "period_2", "table_1", False)




