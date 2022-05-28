from pylatex import Document, LongTable, MultiColumn, Tabular
from pylatex.utils import NoEscape, bold
from typing import Iterable
from pandas import DataFrame


def fill_power_table_segment(
    table: Tabular,
    df: DataFrame) -> None:

    # write header (method name)
    header = df.columns.levels[0][0]
    table.add_row(
        [MultiColumn(1), MultiColumn(4, align="|c|", data=bold(header))])
    table.add_hline()

    # write rows
    for outer_level in df.index.levels[0]:
        table.add_hline()
        partial_df = df.loc[outer_level]
        for inner_level in partial_df.index:
            row = []
            for value in partial_df.loc[inner_level]:
                row.append(MultiColumn(1, align="|c|", data=value))
            rowname = NoEscape("$" + outer_level + "=" + inner_level + "$")
            row = [MultiColumn(1, align="|c|", data=rowname)] + row
            table.add_row(row)
            table.add_hline()


def write_power_table(
    segments: Iterable[DataFrame],
    result_filename: str) -> None:

    # sanity check on column indices
    index = segments[0].columns.droplevel()
    assert all([index.equals(df.columns.droplevel()) for df in segments[1:]])

    # create table header
    table = Tabular("ccccc")
    table.add_row([MultiColumn(1), MultiColumn(4, data=bold("Power"))])
    table.append(NoEscape(r"\cline{2-5}"))
    table.add_row(
        [MultiColumn(1),
        MultiColumn(2, align="|c|", data=bold(index.levels[0][0])),
        MultiColumn(2, align="|c|", data=bold(index.levels[0][1]))])
    table.append(NoEscape(r"\cline{2-5}"))
    table.add_row(
        [MultiColumn(1),
        MultiColumn(1, align="|c|", data=index.levels[0][0]),
        MultiColumn(1, align="|c|", data=index.levels[0][1]),
        MultiColumn(1, align="|c|", data=index.levels[0][0]),
        MultiColumn(1, align="|c|", data=index.levels[0][1])])
    table.append(NoEscape(r"\cline{2-5}"))

    # create table body
    for df in segments:
        fill_power_table_segment(table, df)
    
    # write to disk
    doc = Document()
    doc.append(table)
    doc.generate_pdf(result_filename, clean_tex=False)


