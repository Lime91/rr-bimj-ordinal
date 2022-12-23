#!/usr/bin/python3

# Reproduce tables and figures in the submitted manuscript
# Copyright (C) 2022  Konstantin Emil Thiel

from subprocess import Popen, PIPE, run
from os import makedirs, mkdir
from os.path import join, exists, dirname, basename, splitext
from shutil import rmtree
from pandas import read_csv
from utils import prepare_power_table_segment, write_power_table
from utils import prepare_alpha_error_table, write_alpha_error_table
from utils import write_wins_table, write_pvalue_table
from typing import Iterable, List, Dict

# simulation program
R_PROGRAM = ["Rscript", "./ebstatmax/diacerein.R"]
R_WINS_TABLE_SCRIPT = ["Rscript", "./r-script/wins_table.R"]
R_PVALUE_TABLE_SCRIPT = ["Rscript", "./r-script/p_values_table.R"]
R_BOXPLOT_SCRIPT = ["Rscript", "./r-script/boxplot.R"]

# output directory structure
DIR_RAW_OUTPUT = "raw-output"
DIR_RESULTS = "results"
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

# dataset for additional simulations
DIACEREIN_80_MATCHED = "./Diacerein_80-matched.txt"


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
    baseline_adjustion=False,
    extra_dataset=None) -> None:

    table_segments = []
    for method in methods:
        # run simulations
        extra_args = ""
        subdir = method
        if extra_dataset:
            extra_args += " -d {}".format(extra_dataset)
            subdir += "__" + splitext(basename(extra_dataset))[0]
        if one_sided:
            extra_args += " -u 1"
            subdir += "__one-sided"
        if baseline_adjustion:
            extra_args += " -r"
            subdir += "__baseline_adjusted"
        raw_output_dir = join(DIR_RAW_OUTPUT, subdir)
        if run_simulations:
            perform_simulations(
                method, POWER_SIMULATIONS, raw_output_dir, extra_args)
        # build and write table
        df = prepare_power_table_segment(
            raw_output_dir, POWER_TABLE_FILE_COLUMNS, period)
        table_segments.append(df)
    # write table to disc
    write_power_table(table_segments, DIR_RESULTS, number, caption)


def generate_alpha_error_table(
    number: int,
    caption: str,
    baseline_adjustion=False,
    extra_dataset=None,
    methods=None,
    add_one_sided_gpc=True) -> None:

    if methods is None:
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
        extra_args = ""
        subdir = method
        os_subdir = method
        if extra_dataset:
            extra_args += " -d {}".format(extra_dataset)
            subdir += "__" + splitext(basename(extra_dataset))[0]
            os_subdir += "__one-sided__" + splitext(basename(extra_dataset))[0]
        if baseline_adjustion:
            extra_args += " -r "
            subdir += "__baseline_adjusted"
            os_subdir += "__baseline_adjusted"
        if method == "nparld":
            output_dir = join(DIR_RAW_OUTPUT, subdir)
            outfiles = perform_simulations(
                method, ALPHA_ERROR_SIMULATIONS, output_dir, extra_args)
            raw_file_rows.extend([outfiles] * 2)
            rname = "nparLD two-sided Period "
            rownames.extend([rname + "1", rname + "2"])
            periods.extend(["period_1", "period_2"])
        else:
            rname = method.replace("-", " ").replace("gpc", "GPC")
            if add_one_sided_gpc:
                one_sided_output_dir = join(DIR_RAW_OUTPUT, os_subdir)
                one_sided_outfiles = perform_simulations(
                    method,
                    ALPHA_ERROR_SIMULATIONS, one_sided_output_dir,
                    extra_args + " -u 1")
                raw_file_rows.append(one_sided_outfiles)
                rownames.append(rname + " one-sided")
                periods.append("combined")
            two_sided_output_dir = join(DIR_RAW_OUTPUT, subdir)
            two_sided_outfiles = perform_simulations(
                method, ALPHA_ERROR_SIMULATIONS, two_sided_output_dir,
                extra_args)
            raw_file_rows.append(two_sided_outfiles)
            rownames.append(rname + " two-sided")
            periods.append("combined")

    df = prepare_alpha_error_table(raw_file_rows, periods, rownames)
    write_alpha_error_table(df, DIR_RESULTS, number, caption)


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
    write_wins_table(pruritus_df, pain_df, DIR_RESULTS, number, caption)


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
    write_pvalue_table(pruritus_df, pain_df, DIR_RESULTS, number, caption)


def draw_boxplot() -> None:
    Popen(R_BOXPLOT_SCRIPT, stderr=PIPE, stdout=PIPE, text=True)
    

if __name__ == "__main__":

    # print simUtils version
    command = "suppressPackageStartupMessages(require(simUtils)); " \
              "cat(sessionInfo()$otherPkgs$simUtils$Packaged)"
    p = run(["Rscript", "-e", command], capture_output=True, text=True)
    print("\nsimUtils package installation time:", p.stdout, "\n")

    if exists(DIR_RESULTS):
        rmtree(DIR_RESULTS)
    if exists(DIR_RAW_OUTPUT):
        rmtree(DIR_RAW_OUTPUT)
    
    mkdir(DIR_RESULTS)
    mkdir(DIR_RAW_OUTPUT)

    ############################
    ####   Fig. 3 Boxplot   ####
    ############################

    draw_boxplot()
    

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

    caption_13 = \
        r"Net benefit (95\% CI) and $p$-value (one-sided) for the GPC " \
        r"variants applied to the original dataset for the ordinal outcome " \
        r"``pruritus'' and ``pain'', with the following prioritization (in " \
        r"descending order): time point W4=post treatment, FU=follow up, " \
        r"W2=2 weeks, W0=baseline."
    generate_wins_table(13, caption_13)


    ########################
    ####  Type I Error  ####
    ########################

    methods_8 = [
        "univariate-unmatched-gpc",
        "prioritized-unmatched-gpc",
        "non-prioritized-unmatched-gpc"]
    caption_8 = \
        r"Type I error simulation result for the ordinal outcome ``pruritus''" \
        r" and ``pain'' based on 5000 permutation runs using using " \
        r"the two-sided unmatched GPC variants when restricted to data from " \
        r"subjects who participated in both treatment periods (N=80)."
    generate_alpha_error_table(8, caption_8, methods=methods_8,
                               extra_dataset=DIACEREIN_80_MATCHED,
                               add_one_sided_gpc=False)

    caption_9 = \
        r"Type I error simulation result for the ordinal outcome ``pruritus''" \
        r" and ``pain'' based on 5000 permutation runs using matched and " \
        r"unmatched univariate/prioritized/non-prioritized GPC (one-sided " \
        r"and two-sided) and nparLD split into time period 1 and 2 (two-sided)."
    generate_alpha_error_table(9, caption_9)

    caption_14 = \
        r"\textit{Change from baseline approach:} Type I error simulation " \
        r"result for the ordinal outcome ``pruritus'' and ``pain'' based " \
        r"on 5000 permutation runs using matched and unmatched " \
        r"univariate/prioritized/non-prioritized GPC (one-sided and " \
        r"two-sided) and nparLD split into time period 1 and 2 (two-sided)."
    generate_alpha_error_table(14, caption_14, baseline_adjustion=True)


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

    methods_10 = ["nparld"]
    caption_10 = \
        r"Power simulation results for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"nparLD for period 2 data."
    generate_power_table(methods_10, "period_2", 10, caption_10,
                         run_simulations=False)

    methods_15 = ["nparld"]
    caption_15 = \
        r"\textit{Change from baseline approach:} Power simulation results " \
        r"for the ordinal outcome ``pruritus'' and ``pain'' with varying " \
        r"log-normal effects and normal effects (with $\sigma_{log}$ and " \
        r"$\sigma_{norm} =1$) and scenarios 1 and 2 using nparLD for " \
        r"period 1 data."
    generate_power_table(methods_15, "period_1", 15, caption_15,
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

    methods_3 = ["non-prioritized-unmatched-gpc"]
    caption_3 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided non-prioritized unmatched GPC method."
    generate_power_table(methods_3, "combined", 3, caption_3)

    methods_4 = ["prioritized-matched-gpc", "prioritized-unmatched-gpc"]
    caption_4 = \
        r"Power simulation result for the ordinal outcome ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided prioritized matched and unmatched GPC method."
    generate_power_table(methods_4, "combined", 4, caption_4)

    methods_7 = [
        "univariate-unmatched-gpc",
        "prioritized-unmatched-gpc",
        "non-prioritized-unmatched-gpc"]
    caption_7 = \
        r"Power simulation results for the ordinal outcomes ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the two-sided unmatched GPC variants when restricted to data from " \
        r"subjects who participated in both treatment periods (N=80)."
    generate_power_table(methods_7, "combined", 7, caption_7,
                         extra_dataset=DIACEREIN_80_MATCHED)

    methods_11 = ["non-prioritized-unmatched-gpc"]
    caption_11 = \
        r"Power simulation results for the ordinal outcomes ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the one-sided non-prioritized unmatched GPC method."
    generate_power_table(methods_11, "combined", 11, caption_11, one_sided=True)

    methods_12 = [
        "univariate-matched-gpc",
        "univariate-unmatched-gpc",
        "prioritized-matched-gpc",
        "prioritized-unmatched-gpc"]
    caption_12 = \
        r"Power simulation results for the ordinal outcomes ``pruritus'' and " \
        r"``pain'' with varying log-normal effects and normal effects (with " \
        r"$\sigma_{log}$ and $\sigma_{norm} =1$) and scenarios 1 and 2 using " \
        r"the one-sided univariate/prioritized matched and unmatched GPC " \
        r"method."
    generate_power_table(methods_12, "combined", 12, caption_12, one_sided=True)

    methods_16 = ["non-prioritized-unmatched-gpc"]
    caption_16 = \
        r"\textit{Change from baseline approach:} Power simulation result " \
        r"for the ordinal outcome ``pruritus'' and ``pain'' with varying " \
        r"log-normal effects and normal effects (with $\sigma_{log}$ and " \
        r"$\sigma_{norm} =1$) and scenarios 1 and 2 using the two-sided " \
        r"non-prioritized unmatched GPC method."
    generate_power_table(methods_16, "combined", 16, caption_16,
                         baseline_adjustion=True)

    methods_17 = [
        "univariate-matched-gpc",
        "univariate-unmatched-gpc"]
    caption_17 = \
        r"\textit{Change from baseline approach:} Power simulation result " \
        r"for the ordinal outcome ``pruritus'' and ``pain'' with varying " \
        r"log-normal effects and normal effects (with $\sigma_{log}$ and " \
        r"$\sigma_{norm} =1$) and scenarios 1 and 2 using the two-sided " \
        r"univariate matched and unmatched GPC method."
    generate_power_table(methods_17, "combined", 17, caption_17,
                         baseline_adjustion=True)

    methods_18 = [
        "prioritized-matched-gpc",
        "prioritized-unmatched-gpc"]
    caption_18 = \
        r"\textit{Change from baseline approach:} Power simulation result " \
        r"for the ordinal outcome ``pruritus'' and ``pain'' with varying " \
        r"log-normal effects and normal effects (with $\sigma_{log}$ and " \
        r"$\sigma_{norm} =1$) and scenarios 1 and 2 using the two-sided " \
        r"prioritized matched and unmatched GPC method."
    generate_power_table(methods_18, "combined", 18, caption_18,
                         baseline_adjustion=True)
