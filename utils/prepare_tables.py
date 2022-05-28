from json import load
from pandas import MultiIndex, DataFrame
from typing import Iterable
from os.path import join


# global constants
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
    outfile_directory: str,
    outfile_columns: Iterable[Iterable[str]],
    period: str,
    column_index: MultiIndex) -> DataFrame:

    table = []
    previous_rownames = []
    for outfile_column in outfile_columns:
        rownames = []
        data = []
        for name in outfile_column:
            filename = join(outfile_directory, name)
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
    return DataFrame(table, index=row_index, columns=column_index)
