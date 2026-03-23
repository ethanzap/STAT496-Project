import json
import glob
import math

files = glob.glob("output*.json")

def disp(f):
    disps = []
    with open(f) as fi:
        a = json.load(fi)

    for v in a.values():
        t = v['political_alignment_trajectory']
        disps.append(math.sqrt((t['0'][0] - t['7'][0]) ** 2 + (t['0'][1] - t['7'][1]) ** 2))

    return sum(disps) / len(disps)

disps = {f: disp(f) for f in files}
print(disps)
control_disps = [disp(f) for f in files if "c" in f]
bias_disps = [disp(f) for f in files if "c" not in f]
print(sum(control_disps) / len(control_disps))
print(sum(bias_disps) / len(bias_disps))