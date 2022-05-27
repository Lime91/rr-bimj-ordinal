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
        outer_df = df.loc[outer_level]
        for inner_level in outer_df.index:
            row = []
            for value in outer_df.loc[inner_level]:
                row.append(MultiColumn(1, align="|c|", data=value))
            rowname = NoEscape("$" + outer_level + "=" + inner_level + "$")
            row = [MultiColumn(1, align="|c|", data=rowname)] + row
            table.add_row(row)
            table.add_hline()



    


table = Tabular("ccccc")
table.add_row(
    (MultiColumn(1),
    MultiColumn(4, data=bold("Power")))
)
table.append(NoEscape(r"\cline{2-5}"))
table.add_row(
    (MultiColumn(1),
    MultiColumn(2, align="|c|", data=bold("Pruritus")),
    MultiColumn(2, align="|c|", data=bold("Pain")))
)
table.append(NoEscape(r"\cline{2-5}"))
table.add_row(
    (MultiColumn(1),
    MultiColumn(1, align="|c|", data="Scenario 1"),
    MultiColumn(1, align="|c|", data="Scenario 2"),
    MultiColumn(1, align="|c|", data="Scenario 1"),
    MultiColumn(1, align="|c|", data="Scenario 2"))
)
table.append(NoEscape(r"\cline{2-5}"))

fill_power_table_segment(table, df)


doc = Document()
doc.append(table)
doc.generate_pdf("testtable", clean_tex=False)




