# pypistats-plots

Plots using [pypistats API](https://github.com/hugovk/pypistats).
As it is currently, the PyPiStats API seems to be more "printing tables" oriented rather than "comparing plots" oriented.
Thus we created this script to plot data instead.
Our first interest in creating this addendum project was to gauge relative use of minor Python versions to decide when to cutoff EOL Python versions e.g. Python 3.5.

![Meson weekly](./data/Meson_weekly_pypi.png)

## Usage

There is no install--just run the script like:

```sh
python plot_pypistats.py meson
```

to plot statistics on PyPi package "Meson"
