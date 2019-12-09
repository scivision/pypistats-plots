#!/usr/bin/env python
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
    P = p.parse_args()

    dat = download_stats(P.projname)
    weekly = dat.resample("1W").sum()

    fg = figure(1)
    fg.clf()
    ax = fg.gca()
    weekly.plot(ax=ax)
    ax.set_title("Meson: PyPi downloads by Python version (pypistats.org)")
    ax.set_ylabel("weekly downloads")

    lost = weekly["3.5"]
    current = weekly[["3.6", "3.7", "3.8", "3.9"]].sum(axis=1)

    fg2 = figure(2)
    fg2.clf()
    ax = fg2.gca()
    ax.plot(current, label="3.6..3.9")
    ax.plot(lost, label="3.5")
    ax.set_title("Meson: PyPi downloads by Python version (pypistats.org)")
    ax.set_ylabel("weekly downloads")
    ax.grid(True)
    ax.legend()

    show()
