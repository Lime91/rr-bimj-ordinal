from pylatex import Document, LongTable, MultiColumn, Tabular
from pylatex.utils import NoEscape, bold
from typing import Iterable
from pandas import DataFrame


def fill_power_table_segment(
    table: Tabular,
    df: DataFrame) -> None:
    


table = Tabular("|cclcl|")
table.add_row(
    (MultiColumn(1),
    MultiColumn(4, data=bold("Power")))
)
table.append(NoEscape(r"\cline{2-5}"))
table.add_row(
    (MultiColumn(1),
    MultiColumn(2, align="|c|", data=bold("Pruritus")),
    MultiColumn(2, align="c|", data=bold("Pain")))
)
table.append(NoEscape(r"\cline{2-5}"))
table.add_row(
    (MultiColumn(1),
    MultiColumn(1, align="|c|", data="Scenario 1"),
    MultiColumn(1, align="c|", data="Scenario 2"),
    MultiColumn(1, align="c|", data="Scenario 1"),
    MultiColumn(1, align="c|", data="Scenario 2"))
)
table.append(NoEscape(r"\cline{2-5}"))
table.add_row(
    (MultiColumn(1),
    MultiColumn(4, align="|c|", data=bold("nparLD")))
)
table.add_hline()
table.add_hline()
table.add_row(
    (MultiColumn(1, align="|c|", data=NoEscape(r"$\mu_{\mbox{\scriptsize log}}=0.2$")),
    MultiColumn(1, align="|c|", data=0.1948),
    MultiColumn(1, align="|c|", data=0.1896),
    MultiColumn(1, align="|c|", data=0.2340),
    MultiColumn(1, align="|c|", data=0.2226))
)
table.add_hline()
table.add_row(
    (MultiColumn(1, align="|c|", data=NoEscape(r"$\mu_{\mbox{\scriptsize log}}=0.6$")),
    MultiColumn(1, align="|c|", data=0.3160),
    MultiColumn(1, align="|c|", data=0.2906),
    MultiColumn(1, align="|c|", data=0.3242),
    MultiColumn(1, align="|c|", data=0.3018))
)
table.add_hline()
table.add_row(
    (MultiColumn(1, align="|c|", data=NoEscape(r"$\mu_{\mbox{\scriptsize log}}=0.9$")),
    MultiColumn(1, align="|c|", data=0.4372),
    MultiColumn(1, align="|c|", data=0.3980),
    MultiColumn(1, align="|c|", data=0.4230),
    MultiColumn(1, align="|c|", data=0.3802))
)
table.add_hline()
table.add_hline()

doc = Document()
doc.append(table)
doc.generate_pdf("testtable", clean_tex=False)




