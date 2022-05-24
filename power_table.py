from sqlite3 import paramstyle
from pylatex import Document, LongTable, MultiColumn
from typing import Iterable, List
from json import load
from os.path import join


# global constants
SUBDIR_PAIN = "Pain"
SUBDIR_PRURITUS = "Pruritus"
SUBDIR_SCENARIO_1 = "Scenario 1"
SUBDIR_SCENARIO_2 = "Scenario 2"
OUTFILE_NORM = "norm"
OUTFILE_LNORM = "lnorm"
KEY_POWER = "power"
KEY_REJECTION_RATE = "rejection_rate"


def collect_single_power_table(
    output_dir: str,
    key_period: str) -> List[List[str]]:

    pruritus_s1_norm = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_1, OUTFILE_NORM)
    pruritus_s1_lnorm = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_1, OUTFILE_LNORM)
    pruritus_s2_norm = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_2, OUTFILE_NORM)
    pruritus_s2_lnorm = join(SUBDIR_PRURITUS, SUBDIR_SCENARIO_2, OUTFILE_LNORM)
    pain_s1_norm = join(SUBDIR_PAIN, SUBDIR_SCENARIO_1, OUTFILE_NORM)
    pain_s1_lnorm = join(SUBDIR_PAIN, SUBDIR_SCENARIO_1, OUTFILE_LNORM)
    pain_s2_norm = join(SUBDIR_PAIN, SUBDIR_SCENARIO_2, OUTFILE_NORM)
    pain_s2_lnorm = join(SUBDIR_PAIN, SUBDIR_SCENARIO_2, OUTFILE_LNORM)

    columns = []
    columns.append((pruritus_s1_norm, pruritus_s1_lnorm))
    columns.append((pruritus_s2_norm, pruritus_s2_lnorm))
    columns.append((pain_s1_norm, pain_s1_lnorm))
    columns.append((pain_s2_norm, pain_s2_lnorm))

    table = []
    for column in columns:
        rownames = []
        data = []
        for outfile in column:
            filename = join(output_dir, outfile + ".json")
            output = load(open(filename, "r"))
            power = output[KEY_POWER]
            for parameters in power:
                rownames.append(parameters)
                rejection_rate = power[parameters][KEY_REJECTION_RATE]
                data.append(rejection_rate[key_period])
        table.append(data)
    
    table = [rownames] + table
    return(table)







def genenerate_combined_power_table(
    outfiles: Iterable[str],
    period: str) -> None:

    geometry_options = {
        "margin": "2.54cm",
        "includeheadfoot": True
    }
    doc = Document(page_numbers=True, geometry_options=geometry_options)

    # Generate data table
    with doc.create(LongTable("l l l")) as data_table:
            data_table.add_hline()
            data_table.add_row(["header 1", "header 2", "header 3"])
            data_table.add_hline()
            data_table.end_table_header()
            data_table.add_hline()
            data_table.add_row((MultiColumn(3, align='r',
                                data='Continued on Next Page'),))
            data_table.add_hline()
            data_table.end_table_footer()
            data_table.add_hline()
            data_table.add_row((MultiColumn(3, align='r',
                                data='Not Continued on Next Page'),))
            data_table.add_hline()
            data_table.end_table_last_footer()
            row = ["Content1", "9", "Longer String"]
            for i in range(150):
                data_table.add_row(row)

    doc.generate_pdf("longtable", clean_tex=False)


table = collect_single_power_table("nparLD", "period_1")
n_row = len(table[0])
for i in range(n_row):
    row = [col[i] for col in table]
    print(row)
print()