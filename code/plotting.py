import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# plot by error some measure range
ratios = np.arange(0.1, 1.1, 0.1)
threshold_range = np.array([0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0])
depths = np.arange(0, 21, 2)

# the place we should change to apply to the template
x_range = depths
measure_folder = "depth"
x_label = "Depth of URIs sub-validation"

measure_range = len(x_range)
ps_by_measure = np.zeros(measure_range)
rs_by_measure = np.zeros(measure_range)
f1_by_measure = np.zeros(measure_range)
time_by_measure = np.zeros(measure_range)

ps_by_measure_random = np.zeros(measure_range)
rs_by_measure_random = np.zeros(measure_range)
f1_by_measure_random = np.zeros(measure_range)
time_by_measure_random = np.zeros(measure_range)

i = 0
for t in x_range:
    # empirical result
    result = pd.read_csv("../experiments/recent/" + measure_folder + "/result_1_80"
                         + "_" + "0.8"
                         + "_" + "0.5"
                         + "_" + str(t)
                         + ".csv",
                         sep=",",
                         skiprows=5)
    ps = result["Precision"].values
    rs = result["Recall"].values
    times = result["Time(s)"].values
    folders = result["Folder"].values
    # p_i = np.mean(ps[np.nonzero(ps)])
    # r_i = np.mean(rs[np.nonzero(rs)])
    p_i = np.mean(ps)
    r_i = np.mean(rs)
    ps_by_measure[i] = p_i
    rs_by_measure[i] = r_i
    f1_by_measure[i] = 2 * p_i * r_i / (p_i + r_i)
    time_by_measure[i] = np.mean(times)

    # random result
    result_random = pd.read_csv("../experiments/recent/" + measure_folder + "/random_result_1_80"
                                + "_" + "0.8"
                                + "_" + "0.5"
                                + "_" + str(t)
                                + ".csv",
                                sep=",",
                                skiprows=5)
    ps_random = result_random["Precision"].values
    rs_random = result_random["Recall"].values
    times_random = result_random["Time(s)"].values
    folders_random = result_random["Folder"].values
    # p_i_random = np.mean(ps_random[np.nonzero(ps_random)])
    # r_i_random = np.mean(rs_random[np.nonzero(rs_random)])
    p_i_random = np.mean(ps_random)
    r_i_random = np.mean(rs_random)
    ps_by_measure_random[i] = p_i_random
    rs_by_measure_random[i] = r_i_random
    f1_by_measure_random[i] = 2 * p_i_random * r_i_random / (p_i_random + r_i_random)
    time_by_measure_random[i] = np.mean(times_random)

    i += 1


# plot precision by recall
# plt.figure()
# plt.plot(ps_by_measure, rs_by_measure)
# plt.show()

# plot by f-measure and time
# fig, ax1 = plt.subplots()
# t = depths
#
# ax1.plot(t, f1_by_measure, label="F1-score", color="orange")
# ax1.plot(t, f1_by_measure_random, label="F1-score_Random", color="green")
# ax1.set_ylabel("F1-score")
# ax1.set_ylim((0, 1.0))
#
# ax2 = ax1.twinx()
# ax2.plot(t, time_by_measure, label="Time", linestyle=":", color="orange")
# ax2.plot(t, time_by_measure_random, linestyle=":", label="Time_Random", color="green")
# ax2.set_ylabel("Time")
#
# fig.tight_layout()
# plt.show()


# plot by precision/recall/time by x_range
# plt.figure()
fig, ax1 = plt.subplots(figsize=(7, 6))

ax1.plot(x_range, ps_by_measure, label="Precision", color="#1f77b4")
ax1.plot(x_range, rs_by_measure, label="Recall", color="#ff7f0e")
ax1.plot(x_range, ps_by_measure_random, label="Precision_Random", linestyle=":", color="#1f77b4")
ax1.plot(x_range, rs_by_measure_random, label="Recall_Random", linestyle=":", color="#ff7f0e")
ax1.set_xticks(x_range)
ax1.set_xlabel(x_label)
ax1.set_ylabel("Precision/Recall")
ax1.set_ylim((0.0, 1.0))
ax1.set_yticks(np.arange(0.0, 1.0, 0.1))

ax2 = ax1.twinx()
ax2.plot(x_range, time_by_measure, label="Time", linestyle="--", marker="*", color="#d62728")
ax2.set_ylabel("Time (s)")

# fig.tight_layout()

# plt.plot(x_range, time_by_measure, label="Time")
# plt.plot(x_range, time_by_measure_random, label="Time_Random")

# plt.yticks(np.arange(0.1, 0.9, 0.05))

fig.legend(loc=0)
# plt.title("Precision-Recall by " + x_label)
plt.show()
