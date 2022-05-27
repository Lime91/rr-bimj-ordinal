from utils import prepare_power_table, write_power_table

df1 = prepare_power_table("outfiles", "nparLD", "period_1")
df2 = prepare_power_table("outfiles", "nparLD", "period_2")

write_power_table([df1, df2], "nparld")
