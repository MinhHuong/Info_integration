"""plotting.py: plots the evaluation result"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys

__authors__ = "Billel Guerfa, Armita Khajehnassiri, Minh-Huong Le-Nguyen, Nafaa Si Said"


def gen_filename(setting, param, is_random):
    # syntax: "../experiments/recent/[random]_result_[thres]_[ratio]_[depth].csv"

    if setting == "error":
        folder = "error_ratio/"
    elif setting == "func_thres":
        folder = "func_thres/"
    else:
        folder = "depth/"

    filename = "../experiments/recent/" + folder

    if is_random:
        filename += "random_"

    filename += "result_1_80_"

    if setting == "error":
        filename += "0.8_" + str(param) + "_" + "0.csv"
    elif setting == "func_thres":
        filename += str(param) + "_0.5_0.csv"
    else:
        filename += "0.8_0.5_" + str(param) + ".csv"

    return filename


if len(sys.argv) < 2:
    print("Select one of the three parameters: ratio, func_thres, depth")
    sys.exit(0)

setting = sys.argv[1]

# plot by error some measure range
ratios = np.arange(0.1, 1.1, 0.1)
threshold_range = np.array([0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0])
depths = np.arange(0, 21, 2)

# the place we should change to apply to the template
# just stupid if-else here
if setting == "error":
    x_range = ratios
    measure_folder = "error_ratio"
    x_label = "Ratio of erroneous links"
elif setting == "func_thres":
    x_range = threshold_range
    measure_folder = "func_thres"
    x_label = "Functionality threshold"
else:
    x_range = depths
    measure_folder = "depth"
    x_label = "Depth of URIs sub-validation"


measure_range = len(x_range)
ps_by_measure = np.zeros(measure_range)
rs_by_measure = np.zeros(measure_range)
f1_by_measure = np.zeros(measure_range)
time_by_measure = np.zeros(measure_range)
zeros_ratio = np.zeros(measure_range)  # ratio of zero-valued precision and recall for each result file
zeros_data = []

ps_by_measure_random = np.zeros(measure_range)
rs_by_measure_random = np.zeros(measure_range)
f1_by_measure_random = np.zeros(measure_range)
time_by_measure_random = np.zeros(measure_range)

i = 0
for t in x_range:
    # empirical result
    if setting == "error":
        param = (i+1)/10
    else:
        param = t

    result = pd.read_csv(gen_filename(setting, param, False), sep=",", skiprows=5)
    ps = result["Precision"].values
    rs = result["Recall"].values
    times = result["Time(s)"].values
    folders = result["Folder"].values
    p_i = np.mean(ps[np.nonzero(ps)])
    r_i = np.mean(rs[np.nonzero(rs)])
    # p_i = np.mean(ps)
    # r_i = np.mean(rs)
    ps_by_measure[i] = p_i
    rs_by_measure[i] = r_i
    f1_by_measure[i] = 2 * p_i * r_i / (p_i + r_i)
    time_by_measure[i] = np.mean(times)

    zeros_ratio[i] = np.sum([1 for p, r in zip(ps, rs) if p == 0 and r == 0]) / 80
    zeros_data.append([f for p, r, f in zip(ps, rs, folders) if p == 0 and r == 0])

    # random result
    result_random = pd.read_csv(gen_filename(setting, param, True), sep=",", skiprows=5)
    ps_random = result_random["Precision"].values
    rs_random = result_random["Recall"].values
    times_random = result_random["Time(s)"].values
    folders_random = result_random["Folder"].values
    p_i_random = np.mean(ps_random[np.nonzero(ps_random)])
    r_i_random = np.mean(rs_random[np.nonzero(rs_random)])
    # p_i_random = np.mean(ps_random)
    # r_i_random = np.mean(rs_random)
    ps_by_measure_random[i] = p_i_random
    rs_by_measure_random[i] = r_i_random
    f1_by_measure_random[i] = 2 * p_i_random * r_i_random / (p_i_random + r_i_random)
    time_by_measure_random[i] = np.mean(times_random[np.nonzero(ps_random)])

    i += 1

# plot by precision/recall/time by x_range
fig, ax1 = plt.subplots(figsize=(7, 6))

ax1.plot(x_range, ps_by_measure, label="Precision", color="#1f77b4", marker="^")
ax1.plot(x_range, rs_by_measure, label="Recall", color="#ff7f0e", marker="^")
ax1.plot(x_range, ps_by_measure_random, label="Precision_Random", linestyle="--", color="#1f77b4")
ax1.plot(x_range, rs_by_measure_random, label="Recall_Random", linestyle="--", color="#ff7f0e")
ax1.set_xticks(x_range)
ax1.set_xlabel(x_label)
ax1.set_ylabel("Precision/Recall")
ax1.set_ylim((0.0, 1.0))
ax1.set_yticks(np.arange(0.0, 1.0, 0.1))

ax2 = ax1.twinx()
ax2.plot(x_range, time_by_measure, label="Time", linestyle=":", marker="o", color="#7f7f7f", linewidth=3.)
ax2.set_ylabel("Time (s)")

fig.legend()
plt.show()
