from json import load
from os.path import join
from pandas import MultiIndex, DataFrame


# global constants
SUBDIR_PAIN = "Pain"
SUBDIR_PRURITUS = "Pruritus"
SUBDIR_SCENARIO_1 = "Scenario 1"
SUBDIR_SCENARIO_2 = "Scenario 2"
OUTFILE_NORM = "norm"
OUTFILE_LNORM = "lnorm"

KEY_POWER = "power"
KEY_REJECTION_RATE = "rejection_rate"

ROWNAME_MAP = {
    "meanlog=0.2, sdlog=1": (r"\mu_{\mbox{\scriptsize log}}", r"0.2"),
    "meanlog=0.6, sdlog=1": (r"\mu_{\mbox{\scriptsize log}}", r"0.6"),
    "meanlog=0.9, sdlog=1": (r"\mu_{\mbox{\scriptsize log}}", r"0.9"),
    "mean=2, sd=1": (r"\mu_{\mbox{\scriptsize norm}}", r"2"),
    "mean=3, sd=1": (r"\mu_{\mbox{\scriptsize norm}}", r"3"),
    "mean=4, sd=1": (r"\mu_{\mbox{\scriptsize norm}}", r"4")
}


def prepare_power_table(
    output_dir: str,
    method: str,
    period: str) -> DataFrame:

    pruritus_s1_norm = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_1, OUTFILE_NORM)
    pruritus_s1_lnorm = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_1, OUTFILE_LNORM)
    pruritus_s2_norm = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_2, OUTFILE_NORM)
    pruritus_s2_lnorm = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_2, OUTFILE_LNORM)
    pain_s1_norm = join(SUBDIR_PAIN, SUBDIR_SCENARIO_1, OUTFILE_NORM)
    pain_s1_lnorm = join(SUBDIR_PAIN, SUBDIR_SCENARIO_1, OUTFILE_LNORM)
    pain_s2_norm = join(SUBDIR_PAIN, SUBDIR_SCENARIO_2, OUTFILE_NORM)
    pain_s2_lnorm = join(SUBDIR_PAIN, SUBDIR_SCENARIO_2, OUTFILE_LNORM)

    file_columns = []
    file_columns.append((pruritus_s1_norm, pruritus_s1_lnorm))
    file_columns.append((pruritus_s2_norm, pruritus_s2_lnorm))
    file_columns.append((pain_s1_norm, pain_s1_lnorm))
    file_columns.append((pain_s2_norm, pain_s2_lnorm))

    column_index_levels = ((method, ),
                           (SUBDIR_PRURITUS, SUBDIR_PAIN),
                           (SUBDIR_SCENARIO_1, SUBDIR_SCENARIO_2))
    col_index = MultiIndex.from_product(column_index_levels)

    table = []
    previous_rownames = []
    for file_column in file_columns:
        rownames = []
        data = []
        for file in file_column:
            filename = join(output_dir, method, file + ".json")
            raw_data = load(open(filename, "r"))
            power = raw_data[KEY_POWER]
            for parameters in power:
                rownames.append(parameters)
                rejection_rate = power[parameters][KEY_REJECTION_RATE]
                data.append(rejection_rate[period])
        if len(previous_rownames) > 0:  # sanity check
            assert previous_rownames == rownames
        previous_rownames = rownames
        table.append(data)

    table = [list(row) for row in zip(*table)]  # transpose
    row_index = MultiIndex.from_tuples([ROWNAME_MAP[name] for name in rownames])
    return DataFrame(table, index=row_index, columns=col_index)
