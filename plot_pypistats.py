#!/usr/bin/env python
"""
Plots Python package stats by Python version.
"""

from __future__ import annotations
import pypistats as ps

import pandas
from matplotlib.pyplot import figure, show

import argparse
import json


def download_stats(projname: str, versions: list[str]) -> pandas.DataFrame:
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
    df = df.sort_index().fillna(0)

    return df


def normalize(dat: pandas.DataFrame, versions: list[str]) -> pandas.DataFrame:
    weekly_all = dat.resample(f"{dat.attrs['window']}W", axis=0).sum()
    weekly = weekly_all[versions]
    total = weekly.sum(axis=1)
    normed = (weekly.T / total).T
    normed.attrs = dat.attrs
    return normed


def plot_trends(normed: pandas.DataFrame, versions: list[str]):

    fg = figure()
    axs = fg.subplots(2, 1, sharex=True)
    normed.plot(ax=axs[0])
    axs[0].set_title(
        f"{normed.attrs['project_name']}: PyPI downloads by Python version (pypistats.org): {normed.attrs['window']} week average"
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
    p.add_argument("projname", help="PyPI project name")
    p.add_argument(
        "-w", "--window", help="time window to average over (weeks)", type=int, default=1
    )
    p.add_argument(
        "-v",
        "--versions",
        help="Python minor versions to consider",
        nargs="+",
        default=["3.7", "3.8", "3.9", "3.10", "3.11"],
    )
    P = p.parse_args()

    dat = download_stats(P.projname, P.versions)
    dat.attrs["window"] = P.window
    normed = normalize(dat, P.versions)

    plot_trends(normed, P.versions)

    show()
