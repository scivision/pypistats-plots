#!/usr/bin/env python
"""
Plots Python package stats by Python version.
"""
import pypistats as ps

import pandas
import numpy as np
from matplotlib.pyplot import figure, show

import argparse
import json
import typing as T


def download_stats(projname: str, versions: T.Sequence[str]) -> pandas.DataFrame:
    endpoint = f"packages/{projname}/python_minor"
    params = ps._paramify("mirrors", False)
    dat_json = ps.pypi_stats_api(endpoint, params=params, total=None, format="json")
    dat = json.loads(dat_json)

    df = pandas.DataFrame(columns=versions)
    for d in dat["data"]:
        if d["category"] not in df.columns:
            continue
        df.loc[d["date"], d["category"]] = d["downloads"]

    df.index = pandas.to_datetime(df.index)

    df.attrs.update({"project_name": projname})

    return df


def normalize(dat: pandas.DataFrame) -> pandas.DataFrame:

    weekly_all = dat.resample(f"{dat.attrs['window']}W").sum()
    weekly = weekly_all[versions]
    total = weekly.sum(axis=1)
    normed = (weekly.T / total).T
    normed.attrs = dat.attrs
    return normed


def plot_trends(normed: pandas.DataFrame, versions: T.Sequence[str]):

    fg = figure()
    axs = fg.subplots(2, 1, sharex=True)
    normed.plot(ax=axs[0])
    axs[0].set_title(
        f"{normed.attrs['project_name']}: PyPi downloads by Python version (pypistats.org): {normed.attrs['window']} week average"
    )
    axs[0].set_ylabel("normalized downloads")
    axs[0].legend(loc="center left")

    lost = normed[versions[0]]
    current = normed[versions[1:]].sum(axis=1)

    ax = axs[1]
    current.plot(ax=ax, label=f"{versions[1]}..{versions[-1]}")
    lost.plot(ax=ax, label=f"{versions[0]}")
    ax.set_ylabel("normalized downloads")
    ax.legend(loc="center left")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("projname", help="PyPi project name")
    p.add_argument(
        "-w", "--window", help="time window to average over (weeks)", type=int, default=1
    )
    p.add_argument("-old", help="old Python version to consider dropping", type=float, default=3.5)
    p.add_argument("-new", help="newest Python version to consider", type=float, default=3.9)
    P = p.parse_args()

    if P.old < 3.4:
        v = np.around(np.arange(P.old, 2.7 + 0.1, 0.1), 1)
        if P.new > 3.4:
            v = np.append(v, np.around(np.arange(3.5, P.new + 0.1, 0.1), 1))
    else:
        v = np.around(np.arange(P.old, P.new + 0.1, 0.1), 1)

    versions = v.astype(str)

    dat = download_stats(P.projname, versions)
    dat.attrs["window"] = P.window
    normed = normalize(dat)

    plot_trends(normed, versions)

    show()
