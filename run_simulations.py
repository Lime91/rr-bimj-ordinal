
from subprocess import Popen, PIPE
from os import makedirs
from os.path import join, exists, dirname
from utils import prepare_power_table_segment, write_power_table
from utils import prepare_alpha_error_table, write_alpha_error_table
from typing import Iterable, List, Dict

# simulation program
R_PROGRAM = ["Rscript", "./ebstatmax/diacerein.R"]

# output directory structure
DIR_RAW_OUTPUT = "raw-output"
DIR_RESULT_TABLES = "tables"
SUBDIR_PAIN = "pain"
SUBDIR_PRURITUS = "pruritus"
SUBDIR_SCENARIO_1 = "scenario_1"
SUBDIR_SCENARIO_2 = "scenario_2"
SUBDIR_NO_EFFECT = "no_effect"
OUTFILE_NORM = "norm.json"
OUTFILE_LNORM = "lnorm.json"
OUTFILE_ALPHA_ERROR = "alpha_error.json"

# raw output files
PRURITUS_S1_NORM = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_1, OUTFILE_NORM)
PRURITUS_S1_LNORM = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_1, OUTFILE_LNORM)
PRURITUS_S2_NORM = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_2, OUTFILE_NORM)
PRURITUS_S2_LNORM = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_2, OUTFILE_LNORM)
PRURITUS_ALPHA_ERROR = \
    join(SUBDIR_PRURITUS, SUBDIR_NO_EFFECT, OUTFILE_ALPHA_ERROR)
PAIN_S1_NORM = join(SUBDIR_PAIN, SUBDIR_SCENARIO_1, OUTFILE_NORM)
PAIN_S1_LNORM = join(SUBDIR_PAIN, SUBDIR_SCENARIO_1, OUTFILE_LNORM)
PAIN_S2_NORM = join(SUBDIR_PAIN, SUBDIR_SCENARIO_2, OUTFILE_NORM)
PAIN_S2_LNORM = join(SUBDIR_PAIN, SUBDIR_SCENARIO_2, OUTFILE_LNORM)
PAIN_ALPHA_ERROR = \
    join(SUBDIR_PAIN, SUBDIR_NO_EFFECT, OUTFILE_ALPHA_ERROR)

# raw files for power table
POWER_TABLE_FILE_COLUMNS = []
POWER_TABLE_FILE_COLUMNS.append((PRURITUS_S1_NORM, PRURITUS_S1_LNORM))
POWER_TABLE_FILE_COLUMNS.append((PRURITUS_S2_NORM, PRURITUS_S2_LNORM))
POWER_TABLE_FILE_COLUMNS.append((PAIN_S1_NORM, PAIN_S1_LNORM))
POWER_TABLE_FILE_COLUMNS.append((PAIN_S2_NORM, PAIN_S2_LNORM))

# raw files for alpha error table
POWER_TABLE_FILE_ROW = (PRURITUS_ALPHA_ERROR, PAIN_ALPHA_ERROR)

# simulation settings
BASIC_SETTINGS = "-r"  # subtract and discard baseline
POWER_SIMULATIONS = {
    BASIC_SETTINGS + "-t Pruritus -s 1 -e lnorm": PRURITUS_S1_LNORM,
    BASIC_SETTINGS + "-t Pruritus -s 2 -e lnorm": PRURITUS_S2_LNORM,
    BASIC_SETTINGS + "-t Pruritus -s 1 -e norm": PRURITUS_S1_NORM,
    BASIC_SETTINGS + "-t Pruritus -s 2 -e norm": PRURITUS_S2_NORM,
    BASIC_SETTINGS + "-t Pain -s 1 -e lnorm": PAIN_S1_LNORM,
    BASIC_SETTINGS + "-t Pain -s 2 -e lnorm": PAIN_S2_LNORM,
    BASIC_SETTINGS + "-t Pain -s 1 -e norm": PAIN_S1_NORM,
    BASIC_SETTINGS + "-t Pain -s 2 -e norm": PAIN_S2_NORM
}
ALPHA_ERROR_SIMULATIONS = {
    BASIC_SETTINGS + "-t Pruritus": PRURITUS_ALPHA_ERROR,
    BASIC_SETTINGS + "-t Pain": PAIN_ALPHA_ERROR
}


def run_simulation_framework(
    method: str,
    simulation_settings: Dict[str, str],
    output_dir: str,
    extra_args="") -> List[str]:

    outfiles = []
    for options in simulation_settings:
        file = simulation_settings[options]
        outfile = join(output_dir, file)
        outfiles.append(outfile)
        command = R_PROGRAM + ["-m"] + [method] + options.split()
        if len(extra_args) > 0:
            command += extra_args.split()
        outdir = dirname(outfile)
        if not exists(outdir) and outdir != "":
            makedirs(outdir)
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
    return outfiles


def generate_power_table(
    methods: Iterable[str],
    period: str,
    number: int,
    caption: str,
    run_simulations=True,
    one_sided=False) -> None:

    table_segments = []
    for method in methods:
        # run simulations
        if one_sided:
            extra_args = "-u 1"
            subdir = "one-sided-" + method
        else:
            extra_args = ""
            subdir = method
        raw_output_dir = join(DIR_RAW_OUTPUT, subdir)
        if run_simulations:
            run_simulation_framework(
                method, POWER_SIMULATIONS, raw_output_dir, extra_args)
        # build and write table
        df = prepare_power_table_segment(
            raw_output_dir, POWER_TABLE_FILE_COLUMNS, period)
        table_segments.append(df)
    # write table to disc
    write_power_table(table_segments, DIR_RESULT_TABLES, number, caption)


def generate_alpha_error_table(
    number: int,
    caption: str) -> None:

    methods = [
        "nparld",
        "univariate-matched-gpc",
        "univariate-unmatched-gpc",
        "prioritized-matched-gpc",
        "prioritized-unmatched-gpc",
        "non-prioritized-unmatched-gpc"
    ]
    raw_file_rows = []
    periods = []
    rownames = []
    for method in methods:
        if method == "nparld":
            output_dir = join(DIR_RAW_OUTPUT, method)
            outfiles = run_simulation_framework(
                method, ALPHA_ERROR_SIMULATIONS, output_dir)
            raw_file_rows.extend([outfiles] * 2)
            basename = "nparLD two-sided Period "
            rownames.extend([basename + "1", basename + "2"])
            periods.extend(["period_1", "period_2"])
        else:
            one_sided_output_dir = join(DIR_RAW_OUTPUT, "one-sided-" + method)
            two_sided_output_dir = join(DIR_RAW_OUTPUT, method)
            one_sided_outfiles = run_simulation_framework(
                method, ALPHA_ERROR_SIMULATIONS, one_sided_output_dir, "-u 1")
            two_sided_outfiles = run_simulation_framework(
                method, ALPHA_ERROR_SIMULATIONS, two_sided_output_dir)
            raw_file_rows.append(one_sided_outfiles)
            raw_file_rows.append(two_sided_outfiles)
            basename = method.replace("-", " ").replace("gpc", "GPC")
            rownames.extend([basename + " one-sided", basename + " two-sided"])
            periods.extend(["combined"] * 2)

    df = prepare_alpha_error_table(raw_file_rows, periods, rownames)
    write_alpha_error_table(df, DIR_RESULT_TABLES, number, caption)


if __name__ == "__main__":

    caption_prefix = r"\texttt{[Baseline subtracted and discarded]} "

    ########################
    ####  Type I Error  ####
    ########################

    caption_7 = \
        r"Type I error simulation result for the ordinal outcome ``pruritus''" \
        r" and ``pain'' based on 5000 permutation runs using matched and " \
        r"unmatched univariate/prioritized/non-prioritized GPC (one-sided " \
        r"and two-sided) and nparLD split into time period 1 and 2 (two-sided)."
    generate_alpha_error_table(7, caption_prefix + caption_7)


    ########################
    ####  nparLD Power  ####
    ########################

    methods_1 = ["nparld"]
    caption_1 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the method nparLD."
    generate_power_table(methods_1, "period_1", 1, caption_prefix + caption_1)

    methods_8 = ["nparld"]
    caption_8 = \
        r"Power simulation results for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"nparLD for period 2 data."
    generate_power_table(methods_8, "period_2", 8, caption_prefix + caption_8,
                         run_simulations=False)


    ########################
    #####  GPC Power  ######
    ########################

    methods_2 = ["univariate-matched-gpc", "univariate-unmatched-gpc"]
    caption_2 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided univariate matched and unmatched GPC method."
    generate_power_table(methods_2, "combined", 2, caption_prefix + caption_2)

    methods_3 = ["prioritized-matched-gpc", "prioritized-unmatched-gpc"]
    caption_3 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided prioritized matched and unmatched GPC method."
    generate_power_table(methods_3, "combined", 3, caption_prefix + caption_3)

    methods_4 = ["non-prioritized-unmatched-gpc"]
    caption_4 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided non-prioritized unmatched GPC method."
    generate_power_table(methods_4, "combined", 4, caption_prefix + caption_4)

    methods_9 = [
        "univariate-matched-gpc",
        "univariate-unmatched-gpc",
        "prioritized-matched-gpc",
        "prioritized-unmatched-gpc"]
    caption_9 = \
        r"Power simulation results for the ordinal outcomes ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the one-sided univariate/prioritized matched and unmatched GPC " \
        r"method."
    generate_power_table(methods_9, "combined", 9, caption_prefix + caption_9,
                         one_sided=True)

    methods_10 = ["non-prioritized-unmatched-gpc"]
    caption_10 = \
        r"Power simulation results for the ordinal outcomes ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the one-sided non-prioritized unmatched GPC method."
    generate_power_table(methods_10, "combined", 10,
                         caption_prefix + caption_10, one_sided=True)
