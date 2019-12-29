#!/usr/bin/env python
"""
Plots Python package stats by Python version.
"""
import pypistats as ps
from matplotlib.pyplot import figure, show
import argparse
import json
import pandas


def download_stats(projname: str) -> pandas.DataFrame:
    endpoint = f"packages/{projname}/python_minor"
    params = ps._paramify("mirrors", False)
    dat_json = ps.pypi_stats_api(endpoint, params=params, total=None, format="json")
    dat = json.loads(dat_json)

    df = pandas.DataFrame(columns=["3.4", "3.5", "3.6", "3.7", "3.8", "3.9"])
    for d in dat["data"]:
        if d["category"] not in df.columns:
            continue
        df.loc[d["date"], d["category"]] = d["downloads"]

    df.index = pandas.to_datetime(df.index)

    return df


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("projname", help="PyPi project name")
    p.add_argument("-w", "--window", help="time window to average over (weeks)", type=int, default=1)
    P = p.parse_args()

    dat = download_stats(P.projname)
    weekly_all = dat.resample(f"{P.window}W").sum()
    weekly = weekly_all[["3.5", "3.6", "3.7", "3.8", "3.9"]]
    total = weekly.sum(axis=1)
    normed = (weekly.T / total).T

    fg = figure()
    axs = fg.subplots(2, 1, sharex=True)
    normed.plot(ax=axs[0])
    axs[0].set_title(f"{P.projname}: PyPi downloads by Python version (pypistats.org): {P.window} week average")
    axs[0].set_ylabel("normalized downloads")
    axs[0].legend(loc="center left")

    lost = normed["3.5"]
    current = normed[["3.6", "3.7", "3.8", "3.9"]].sum(axis=1)

    ax = axs[1]
    current.plot(ax=ax, label="3.6..3.9")
    lost.plot(ax=ax, label="3.5")
    ax.set_ylabel("normalized downloads")
    ax.legend(loc="center left")

    show()
