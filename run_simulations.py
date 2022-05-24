
from subprocess import Popen, PIPE

R_PROGRAM = ["Rscript", "diacerein.R"]

simulations = {
    "nparld_pruritus_lnorm_s1": "-m nparld -t Pruritus -e lnorm -s 1",
    "nparld_pruritus_lnorm_s2": "-m nparld -t Pruritus -e lnorm -s 2",
    "nparld_pruritus_norm_s1": "-m nparld -t Pruritus -e norm -s 1",
    "nparld_pruritus_norm_s2": "-m nparld -t Pruritus -e norm -s 2",
    "nparld_pain_lnorm_s1": "-m nparld -t Pain -e lnorm -s 1",
    "nparld_pain_lnorm_s2": "-m nparld -t Pain -e lnorm -s 2",
    "nparld_pain_norm_s1": "-m nparld -t Pain -e norm -s 1",
    "nparld_pain_norm_s2": "-m nparld -t Pain -e norm -s 2"
}

for key in simulations:
    outfile = key + ".json"
    command = R_PROGRAM + simulations[key].split()
    with Popen(
        command,
        stderr=PIPE,
        stdout=open(outfile, "w"),
        bufsize=1,  # line-buffered
        text=True) as p:

        print("\n\ngenerating", outfile, "...\n")

        for line in p.stderr:
            print("## ", line, end='')