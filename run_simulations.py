
from subprocess import Popen, PIPE
from pandas import MultiIndex
from os import makedirs
from os.path import join, exists, dirname
from utils import prepare_power_table, write_power_table
from typing import Iterable

# simulation program
R_PROGRAM = ["Rscript", "./ebstatmax-subtree/diacerein.R"]

# output directory structure
DIR_RAW_OUTPUT = "raw-output"
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
    "nparLD": "nparld",
    "univariate matched GPC": "univariate-matched-gpc",
    "univariate unmatched GPC": "univariate-unmatched-gpc",
    "prioritized matched GPC": "prioritized-matched-gpc",
    "prioritized unmatched GPC": "prioritized-unmatched-gpc",
    "non-prioritized unmatched GPC": "non-prioritized-unmatched-gpc"
}

def run_power_simulations(
    method: str,
    output_dir: str,
    extra_args="") -> None:

    for settings in POWER_SIMULATIONS:
        outfile = join(output_dir, POWER_SIMULATIONS[settings])
        outdir = dirname(outfile)
        if not exists(outdir) and outdir != "":
            makedirs(outdir)
        command = R_PROGRAM + ["-m"] + [method] + settings.split()
        if len(extra_args) > 0:
            command += extra_args.split()
        with open(outfile, "w") as out:
            with Popen(
                command,
                stderr=PIPE,
                stdout=out,
                bufsize=1,  # line-buffered
                text=True) as p:

                print("\n\nrunning simulations for", outfile, "...\n")
                for line in p.stderr:
                    print("### ", line, end='')


def generate_power_table(
    method_names: Iterable[str],
    period: str,
    number: int,
    caption: str,
    run_simulations=True,
    extra_args="") -> None:

    table_segments = []
    for method_name in method_names:
        # run simulations
        method = METHOD_MAP[method_name]
        raw_output_dir = join(DIR_RAW_OUTPUT, method)
        if run_simulations:
            run_power_simulations(method, raw_output_dir, extra_args)

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
    write_power_table(table_segments, DIR_RESULT_TABLES, number, caption)


if __name__ == "__main__":
    # nparLD power
    methods_1 = ["nparLD"]
    caption_1 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the method nparLD."
    generate_power_table(methods_1, "period_1", 1, caption_1)

    methods_8 = ["nparLD"]
    caption_8 = \
        r"Power simulation results for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"nparLD for period 2 data."
    generate_power_table(methods_8, "period_2", 8, caption_8,
                         run_simulations=False)

    # GPC power
    methods_2 = ["univariate matched GPC", "univariate unmatched GPC"]
    caption_2 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided univariate matched and unmatched GPC method."
    generate_power_table(methods_2, "combined", 2, caption_2)

    methods_3 = ["prioritized matched GPC", "prioritized unmatched GPC"]
    caption_3 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided prioritized matched and unmatched GPC method."
    generate_power_table(methods_3, "combined", 3, caption_3)

    methods_4 = ["non-prioritized unmatched GPC"]
    caption_4 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided non-prioritized unmatched GPC method."
    generate_power_table(methods_4, "combined", 4, caption_4)

    methods_9 = [
        "univariate matched GPC",
        "univariate unmatched GPC",
        "prioritized matched GPC",
        "prioritized unmatched GPC"]
    extra_args_9 = "-u 1"  # one-sided gpc test
    caption_9 = \
        r"Power simulation results for the ordinal outcomes ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the one-sided univariate/prioritized matched and unmatched GPC " \
        r"method."
    generate_power_table(methods_9, "combined", 9, caption_9,
                         extra_args=extra_args_9)

    methods_10 = ["non-prioritized unmatched GPC"]
    extra_args_10 = "-u 1"  # one-sided gpc test
    caption_10 = \
        r"Power simulation results for the ordinal outcomes ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the one-sided non-prioritized unmatched GPC method."
    generate_power_table(methods_10, "combined", 10, caption_10,
                         extra_args=extra_args_10)
