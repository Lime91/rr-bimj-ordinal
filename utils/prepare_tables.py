from json import load
from pandas import MultiIndex, DataFrame, Index
from typing import Iterable
from os.path import join


# global constants
KEY_POWER = "power"
KEY_ALPHA_ERROR = "alpha_error"
KEY_REJECTION_RATE = "rejection_rate"
KEY_METHOD = "method"
KEY_SIDE = "side"
KEY_TARGET = "target"
KEY_SCENARIO = "scenario"

ROWNAME_MAP = {
    "meanlog=0.2, sdlog=1": (r"\mu_{\mbox{\scriptsize log}}", r"0.2"),
    "meanlog=0.6, sdlog=1": (r"\mu_{\mbox{\scriptsize log}}", r"0.6"),
    "meanlog=0.9, sdlog=1": (r"\mu_{\mbox{\scriptsize log}}", r"0.9"),
    "mean=2, sd=1": (r"\mu_{\mbox{\scriptsize norm}}", r"2"),
    "mean=3, sd=1": (r"\mu_{\mbox{\scriptsize norm}}", r"3"),
    "mean=4, sd=1": (r"\mu_{\mbox{\scriptsize norm}}", r"4")
}
METHOD_MAP = {
    "nparld": "nparLD",
    "univariate-matched-gpc": "univariate matched GPC",
    "univariate-unmatched-gpc": "univariate unmatched GPC",
    "prioritized-matched-gpc": "prioritized matched GPC",
    "prioritized-unmatched-gpc": "prioritized unmatched GPC",
    "non-prioritized-unmatched-gpc": "non-prioritized unmatched GPC"
}
TARGET_MAP = {
    "Pain": "Pain",
    "Pruritus": "Pruritus"
}
SCENARIO_MAP = {
    1: "Secenario 1",
    2: "Secenario 2",
}


def prepare_power_table_segment(
    outfile_directory: str,
    outfile_columns: Iterable[Iterable[str]],
    period: str) -> DataFrame:

    table = []
    previous_rownames = []  # for sanity checking
    methods = []            # for sanity checking
    sides = []              # for sanity checking
    colnames = []
    for outfile_column in outfile_columns:
        rownames = []
        data = []
        scenarios = []  # for sanity checking
        targets = []    # for sanity checking
        for name in outfile_column:
            filename = join(outfile_directory, name)
            raw_data = load(open(filename, "r"))
            power_dict = raw_data[KEY_POWER]
            for parameters in power_dict:
                rownames.append(parameters)
                power = power_dict[parameters][KEY_REJECTION_RATE][period]
                if isinstance(power, float):
                    power = round(power, 4)
                data.append(power)
            methods.append(raw_data[KEY_METHOD])
            sides.append(raw_data[KEY_SIDE])
            scenarios.append(raw_data[KEY_SCENARIO])
            targets.append(raw_data[KEY_TARGET])

        # perform sanity checks
        assert len(set(scenarios)) == 1
        assert len(set(targets)) == 1
        assert len(set(methods)) == 1
        assert len(set(sides)) == 1
        if len(previous_rownames) > 0:
            assert previous_rownames == rownames
        previous_rownames = rownames
        colnames.append(
            (METHOD_MAP[set(methods).pop()],
             TARGET_MAP[set(targets).pop()],
             SCENARIO_MAP[set(scenarios).pop()]))
        table.append(data)

    table = [list(row) for row in zip(*table)]  # transpose
    row_index = MultiIndex.from_tuples([ROWNAME_MAP[name] for name in rownames])
    col_index = MultiIndex.from_tuples(colnames)
    return DataFrame(table, index=row_index, columns=col_index)


def prepare_alpha_error_table(
    outfile_rows: Iterable[Iterable[str]],
    periods: Iterable[str],
    rownames: Iterable[str]) -> DataFrame:

    # perform sanity check
    assert len(outfile_rows) == len(periods) == len(rownames)

    table = []
    previous_colnames = []  # for sanity checking
    for outfile_row, period in zip(outfile_rows, periods):
        colnames = []
        data = []
        methods = []  # for sanity checking
        sides = []    # for sanity checking
        for filename in outfile_row:
            with open(filename, "r") as out:
                raw_data = load(out)
            alpha_error = raw_data[KEY_ALPHA_ERROR][KEY_REJECTION_RATE][period]
            if isinstance(alpha_error, float):
                alpha_error = round(alpha_error, 4)
            data.append(alpha_error)
            colnames.append(raw_data[KEY_TARGET])
            methods.append(raw_data[KEY_METHOD])
            sides.append(raw_data[KEY_SIDE])

        # perform sanity checks
        assert len(set(methods)) == 1
        assert len(set(sides)) == 1
        if len(previous_colnames) > 0:
            assert previous_colnames == colnames
        previous_colnames = colnames
        table.append(data)

    return DataFrame(table, index=rownames, columns=colnames)
