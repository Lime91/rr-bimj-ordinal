#!/usr/bin/python3

# Reproduce all tables in the submitted manuscript
# Copyright (C) 2022  Konstantin Emil Thiel

from subprocess import Popen, PIPE, run
from os import makedirs
from os.path import join, exists, dirname
from pandas import read_csv
from utils import prepare_power_table_segment, write_power_table
from utils import prepare_alpha_error_table, write_alpha_error_table
from utils import write_wins_table, write_pvalue_table
from typing import Iterable, List, Dict

# simulation program
R_PROGRAM = ["Rscript", "./ebstatmax/diacerein.R"]
R_WINS_TABLE_SCRIPT = ["Rscript", "./r-script/wins_table.R"]
R_PVALUE_TABLE_SCRIPT = ["Rscript", "./r-script/p_values_table.R"]

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
BASIC_SETTINGS = ""
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


def perform_simulations(
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
    one_sided=False,
    baseline_adjustion=False) -> None:

    table_segments = []
    for method in methods:
        # run simulations
        if one_sided:
            extra_args = "-u 1"
            subdir = "one-sided-" + method
        else:
            extra_args = ""
            subdir = method
        if baseline_adjustion:
            extra_args = "-r " + extra_args
            subdir = "baseline_adjusted__" + subdir
        raw_output_dir = join(DIR_RAW_OUTPUT, subdir)
        if run_simulations:
            perform_simulations(
                method, POWER_SIMULATIONS, raw_output_dir, extra_args)
        # build and write table
        df = prepare_power_table_segment(
            raw_output_dir, POWER_TABLE_FILE_COLUMNS, period)
        table_segments.append(df)
    # write table to disc
    write_power_table(table_segments, DIR_RESULT_TABLES, number, caption)


def generate_alpha_error_table(
    number: int,
    caption: str,
    baseline_adjustion=False) -> None:

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
        if baseline_adjustion:
            extra_args = "-r "
        else:
            extra_args = ""
        if method == "nparld":
            if baseline_adjustion:
                subdir = "baseline_adjusted__" + method
            else:
                subdir = method
            output_dir = join(DIR_RAW_OUTPUT, subdir)
            outfiles = perform_simulations(
                method, ALPHA_ERROR_SIMULATIONS, output_dir, extra_args)
            raw_file_rows.extend([outfiles] * 2)
            basename = "nparLD two-sided Period "
            rownames.extend([basename + "1", basename + "2"])
            periods.extend(["period_1", "period_2"])
        else:
            if baseline_adjustion:
                subdir = "baseline_adjusted__" + method
                os_subdir = "baseline_adjusted__one-sided-" + method
            else:
                subdir = method
                os_subdir = "one-sided-" + method
            one_sided_output_dir = join(DIR_RAW_OUTPUT, os_subdir)
            two_sided_output_dir = join(DIR_RAW_OUTPUT, subdir)
            one_sided_outfiles = perform_simulations(
                method, ALPHA_ERROR_SIMULATIONS, one_sided_output_dir,
                extra_args + " -u 1")
            two_sided_outfiles = perform_simulations(
                method, ALPHA_ERROR_SIMULATIONS, two_sided_output_dir,
                extra_args)
            raw_file_rows.append(one_sided_outfiles)
            raw_file_rows.append(two_sided_outfiles)
            basename = method.replace("-", " ").replace("gpc", "GPC")
            rownames.extend([basename + " one-sided", basename + " two-sided"])
            periods.extend(["combined"] * 2)

    df = prepare_alpha_error_table(raw_file_rows, periods, rownames)
    write_alpha_error_table(df, DIR_RESULT_TABLES, number, caption)


def generate_wins_table(
    number: int,
    caption: str) -> None:

    pruritus_cmd = R_WINS_TABLE_SCRIPT + ["Pruritus"]
    pruritus_proc = Popen(pruritus_cmd, stderr=PIPE, stdout=PIPE, text=True)
    pruritus_df = read_csv(
        pruritus_proc.stdout, header=0, index_col=0, dtype=str)
    pain_cmd = R_WINS_TABLE_SCRIPT + ["Pain"]
    pain_proc = Popen(pain_cmd, stderr=PIPE, stdout=PIPE, text=True)
    pain_df = read_csv(pain_proc.stdout, header=0, index_col=0, dtype=str)
    write_wins_table(pruritus_df, pain_df, DIR_RESULT_TABLES, number, caption)


def generate_pvalue_table(
    method: str,  # either "gpc" or "nparld"
    number: int,
    caption: str) -> None:

    pruritus_cmd = R_PVALUE_TABLE_SCRIPT + [method, "Pruritus"]
    pruritus_proc = Popen(pruritus_cmd, stderr=PIPE, stdout=PIPE, text=True)
    pruritus_df = read_csv(
        pruritus_proc.stdout, header=0, index_col=0, dtype=str)
    pain_cmd = R_PVALUE_TABLE_SCRIPT + [method, "Pain"]
    pain_proc = Popen(pain_cmd, stderr=PIPE, stdout=PIPE, text=True)
    pain_df = read_csv(pain_proc.stdout, header=0, index_col=0, dtype=str)
    write_pvalue_table(pruritus_df, pain_df, DIR_RESULT_TABLES, number, caption)


if __name__ == "__main__":

    # print simUtils version
    command = "suppressPackageStartupMessages(require(simUtils)); " \
              "cat(sessionInfo()$otherPkgs$simUtils$Packaged)"
    p = run(["Rscript", "-e", command], capture_output=True, text=True)
    print("\nsimUtils package installation time:", p.stdout, "\n")


    ############################
    ####  Test Statistics   ####
    ############################

    caption_5 = \
        r"Resulting interaction effect of time and group for the ordinal " \
        r"outcome ``pruritus'' and ``pain'' in the original dataset using " \
        r"nparLD with the ANOVA-type statistics."
    generate_pvalue_table("nparld", 5, caption_5)

    caption_6 = \
        r"Resulting two-sided $p$-value and test statistic for the GPC " \
        r"variants applied to the original dataset for the ordinal outcome " \
        r"``pruritus'' and ``pain''."
    generate_pvalue_table("gpc", 6, caption_6)


    ############################
    ####  Wins/Ties/Losses  ####
    ############################

    caption_11 = \
        r"Net benefit (95\% CI) and $p$-value (one-sided) for the GPC " \
        r"variants applied to the original dataset for the ordinal outcome " \
        r"``pruritus'' and ``pain'', with the following prioritization (in " \
        r"descending order): time point W4=post treatment, FU=follow up, " \
        r"W2=2 weeks, W0=baseline."
    generate_wins_table(11, caption_11)


    ########################
    ####  Type I Error  ####
    ########################

    caption_7 = \
        r"Type I error simulation result for the ordinal outcome ``pruritus''" \
        r" and ``pain'' based on 5000 permutation runs using matched and " \
        r"unmatched univariate/prioritized/non-prioritized GPC (one-sided " \
        r"and two-sided) and nparLD split into time period 1 and 2 (two-sided)."
    generate_alpha_error_table(7, caption_7)

    caption_12 = \
        r"\textit{Change from baseline approach:} Type I error simulation " \
        r"result for the ordinal outcome ``pruritus'' and ``pain'' based " \
        r"on 5000 permutation runs using matched and unmatched " \
        r"univariate/prioritized/non-prioritized GPC (one-sided and " \
        r"two-sided) and nparLD split into time period 1 and 2 (two-sided)."
    generate_alpha_error_table(12, caption_12, baseline_adjustion=True)


    ########################
    ####  nparLD Power  ####
    ########################

    methods_1 = ["nparld"]
    caption_1 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the method nparLD."
    generate_power_table(methods_1, "period_1", 1, caption_1)

    methods_8 = ["nparld"]
    caption_8 = \
        r"Power simulation results for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"nparLD for period 2 data."
    generate_power_table(methods_8, "period_2", 8, caption_8,
                         run_simulations=False)

    methods_13 = ["nparld"]
    caption_13 = \
        r"\textit{Change from baseline approach:} Power simulation results " \
        r"for the ordinal outcome ``pruritus'' and ``pain'' with varying " \
        r"log-normal effects and normal effects (with $\sigma_{log}$ and " \
        r"$\sigma_{norm} =1$) and scenarios 1 and 2 using nparLD for " \
        r"period 1 data."
    generate_power_table(methods_13, "period_1", 13, caption_13,
                         baseline_adjustion=True)


    ########################
    #####  GPC Power  ######
    ########################

    methods_2 = ["univariate-matched-gpc", "univariate-unmatched-gpc"]
    caption_2 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided univariate matched and unmatched GPC method."
    generate_power_table(methods_2, "combined", 2, caption_2)

    methods_4 = ["prioritized-matched-gpc", "prioritized-unmatched-gpc"]
    caption_4 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided prioritized matched and unmatched GPC method."
    generate_power_table(methods_4, "combined", 4, caption_4)

    methods_3 = ["non-prioritized-unmatched-gpc"]
    caption_3 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided non-prioritized unmatched GPC method."
    generate_power_table(methods_3, "combined", 3, caption_3)

    methods_10 = [
        "univariate-matched-gpc",
        "univariate-unmatched-gpc",
        "prioritized-matched-gpc",
        "prioritized-unmatched-gpc"]
    caption_10 = \
        r"Power simulation results for the ordinal outcomes ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the one-sided univariate/prioritized matched and unmatched GPC " \
        r"method."
    generate_power_table(methods_10, "combined", 10, caption_10, one_sided=True)

    methods_9 = ["non-prioritized-unmatched-gpc"]
    caption_9 = \
        r"Power simulation results for the ordinal outcomes ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the one-sided non-prioritized unmatched GPC method."
    generate_power_table(methods_9, "combined", 9, caption_9, one_sided=True)

    methods_14 = ["non-prioritized-unmatched-gpc"]
    caption_14 = \
        r"\textit{Change from baseline approach:} Power simulation result " \
        r"for the ordinal outcome ``pruritus'' and ``pain'' with varying " \
        r"log-normal effects and normal effects (with $\sigma_{log}$ and " \
        r"$\sigma_{norm} =1$) and scenarios 1 and 2 using the two-sided " \
        r"non-prioritized unmatched GPC method."
    generate_power_table(methods_14, "combined", 14, caption_10,
                         baseline_adjustion=True)

    methods_15 = [
        "univariate-matched-gpc",
        "univariate-unmatched-gpc"]
    caption_15 = \
        r"\textit{Change from baseline approach:} Power simulation result " \
        r"for the ordinal outcome ``pruritus'' and ``pain'' with varying " \
        r"log-normal effects and normal effects (with $\sigma_{log}$ and " \
        r"$\sigma_{norm} =1$) and scenarios 1 and 2 using the two-sided " \
        r"univariate matched and unmatched GPC method."
    generate_power_table(methods_15, "combined", 15, caption_15,
                         baseline_adjustion=True)

    methods_16 = [
        "prioritized-matched-gpc",
        "prioritized-unmatched-gpc"]
    caption_16 = \
        r"\textit{Change from baseline approach:} Power simulation result " \
        r"for the ordinal outcome ``pruritus'' and ``pain'' with varying " \
        r"log-normal effects and normal effects (with $\sigma_{log}$ and " \
        r"$\sigma_{norm} =1$) and scenarios 1 and 2 using the two-sided " \
        r"prioritized matched and unmatched GPC method."
    generate_power_table(methods_16, "combined", 16, caption_16,
                         baseline_adjustion=True)
