from pylatex import Document, MultiColumn, Tabular, Table
from pylatex.utils import NoEscape, bold
from typing import Iterable
from pandas import DataFrame
from os import makedirs
from os.path import exists, join


def fill_power_table_segment(
    tabular: Tabular,
    df: DataFrame) -> None:

    # write header (method name)
    header = df.columns.levels[0][0]
    tabular.add_row(
        [MultiColumn(1), MultiColumn(4, align="|c|", data=bold(header))])
    tabular.add_hline()

    # write rows
    for outer_level in df.index.levels[0]:
        tabular.add_hline()
        partial_df = df.loc[outer_level]
        for inner_level in partial_df.index:
            row = []
            for value in partial_df.loc[inner_level]:
                row.append(MultiColumn(1, align="|c|", data=value))
            rowname = NoEscape("$" + outer_level + "=" + inner_level + "$")
            row = [MultiColumn(1, align="|c|", data=rowname)] + row
            tabular.add_row(row)
            tabular.add_hline()


def write_power_table(
    segments: Iterable[DataFrame],
    result_directory: str,
    number: int,
    caption: str) -> None:

    # sanity check on column indices
    index = segments[0].columns.droplevel()
    assert all([index.equals(df.columns.droplevel()) for df in segments[1:]])

    # create table header
    tabular = Tabular("ccccc")
    tabular.add_row([MultiColumn(1), MultiColumn(4, data=bold("Power"))])
    tabular.append(NoEscape(r"\cline{2-5}"))
    tabular.add_row(
        [MultiColumn(1),
        MultiColumn(2, align="|c|", data=bold(index.levels[0][0])),
        MultiColumn(2, align="|c|", data=bold(index.levels[0][1]))])
    tabular.append(NoEscape(r"\cline{2-5}"))
    tabular.add_row(
        [MultiColumn(1),
        MultiColumn(1, align="|c|", data=index.levels[0][0]),
        MultiColumn(1, align="|c|", data=index.levels[0][1]),
        MultiColumn(1, align="|c|", data=index.levels[0][0]),
        MultiColumn(1, align="|c|", data=index.levels[0][1])])
    tabular.append(NoEscape(r"\cline{2-5}"))

    # create table body
    for df in segments:
        fill_power_table_segment(tabular, df)

    # add caption + number and write to disc
    table = Table()
    table.add_caption(NoEscape(caption))
    table.append(tabular)
    doc = Document()
    doc.append(NoEscape(r"\setcounter{table}{" + str(number - 1) + r"}"))
    doc.append(table)
    if not exists(result_directory) and result_directory != "":
        makedirs(result_directory)
    result_filename = join(result_directory, "table_" + str(number))
    doc.generate_pdf(result_filename, clean_tex=False)


