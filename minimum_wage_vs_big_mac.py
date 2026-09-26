"""Compare the rate of increase of the U.S. federal minimum wage against the
rate of increase of the price of a McDonald's Big Mac, 2000-2020.

The two measures use different units ($ per hour vs. $ per sandwich), so the
headline chart indexes both to 100 at their first observation in the window.
That puts them on one shared axis, where the steeper line is unambiguously the
faster-growing series.

Run:  python minimum_wage_vs_big_mac.py
Writes: minimum_wage_vs_big_mac.png  and  minimum_wage_vs_big_mac.csv
"""

from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # render to a file; no interactive display needed

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import FuncFormatter

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

DATA_DIR = Path(__file__).parent / "data"
MINIMUM_WAGE_CSV = DATA_DIR / "FEDMINNFRWG.csv"
BIG_MAC_CSV = DATA_DIR / "bigmac.csv"

CHART_PATH = Path(__file__).parent / "minimum_wage_vs_big_mac.png"
TABLE_PATH = Path(__file__).parent / "minimum_wage_vs_big_mac.csv"

START_DATE = pd.Timestamp("2000-01-01")
END_DATE = pd.Timestamp("2020-12-31")

BASELINE_INDEX = 100.0  # both series are rebased to this at their first observation

# Colors are roles, not decoration: one hue per series, plus recessive chrome.
WAGE_COLOR = "#2a78d6"     # blue
BIG_MAC_COLOR = "#eb6834"  # orange
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
GRID = "#e1e0d9"


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def load_minimum_wage(csv_path: Path = MINIMUM_WAGE_CSV) -> pd.Series:
    """Return the monthly federal minimum wage in $/hour, indexed by date.

    Reads FRED's own CSV export for series FEDMINNFRWG, downloaded from
    https://fred.stlouisfed.org/series/FEDMINNFRWG. The export is two columns,
    ``observation_date`` and the series id, and it runs from 1938 to the
    present, so we slice out the window we care about.
    """
    frame = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    wage = frame.iloc[:, 0].astype(float)
    wage.name = "minimum_wage_usd_per_hour"
    return wage.loc[START_DATE:END_DATE].sort_index()


def load_big_mac_price(csv_path: Path = BIG_MAC_CSV) -> pd.Series:
    """Return the U.S. Big Mac price in $, indexed by survey date.

    Reads the Big Mac Index table (``bigmac.csv``) from the Kaggle dataset
    https://www.kaggle.com/datasets/mrmorj/big-mac-index-data. The file covers
    every surveyed country, so we keep the United States rows and read
    ``local_price``, which for the U.S. is already in dollars.
    """
    frame = pd.read_csv(csv_path, parse_dates=["date"])
    united_states = frame.loc[frame["iso_a3"] == "USA"]
    price = united_states.set_index("date")["local_price"].astype(float)
    price.name = "big_mac_price_usd"
    return price.loc[START_DATE:END_DATE].sort_index()


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

def rebase_to_first_observation(series: pd.Series) -> pd.Series:
    """Rescale a series so its first observation equals ``BASELINE_INDEX``."""
    return series / series.iloc[0] * BASELINE_INDEX


def total_growth_percent(series: pd.Series) -> float:
    """Percent increase from the first observation to the last."""
    return (series.iloc[-1] / series.iloc[0] - 1) * 100


def annualized_growth_percent(series: pd.Series) -> float:
    """Compound annual growth rate, in percent per year."""
    years = (series.index[-1] - series.index[0]).days / 365.25
    return ((series.iloc[-1] / series.iloc[0]) ** (1 / years) - 1) * 100


def big_macs_per_hour_worked(wage: pd.Series, price: pd.Series) -> pd.Series:
    """How many Big Macs one hour at the minimum wage buys, per survey date.

    The two sources are sampled on different calendars, so each Big Mac survey
    is matched to the minimum wage in effect on or before that date.
    """
    price_rows = price.rename_axis("date").reset_index()
    wage_rows = wage.rename_axis("date").reset_index()
    aligned = pd.merge_asof(
        price_rows, wage_rows, on="date", direction="backward"
    ).set_index("date")
    ratio = aligned["minimum_wage_usd_per_hour"] / aligned["big_mac_price_usd"]
    ratio.name = "big_macs_per_hour_worked"
    return ratio


# --------------------------------------------------------------------------
# Chart
# --------------------------------------------------------------------------

def _style_axes(axes: plt.Axes) -> None:
    """Apply the shared, deliberately recessive chart chrome."""
    axes.set_facecolor(SURFACE)
    axes.grid(axis="y", color=GRID, linewidth=0.8)
    axes.set_axisbelow(True)
    for side in ("top", "right", "left"):
        axes.spines[side].set_visible(False)
    axes.spines["bottom"].set_color(GRID)
    axes.tick_params(colors=INK_MUTED, labelsize=9, length=0)


def _label_line_end(axes: plt.Axes, series: pd.Series, text: str, color: str) -> None:
    """Direct-label a series at its right-hand endpoint."""
    axes.annotate(
        text,
        xy=(series.index[-1], series.iloc[-1]),
        xytext=(8, 0),
        textcoords="offset points",
        color=color,
        fontsize=10,
        fontweight="bold",
        va="center",
    )


def plot_comparison(wage: pd.Series, price: pd.Series) -> plt.Figure:
    """Build the two-panel figure comparing the two rates of increase."""
    wage_index = rebase_to_first_observation(wage)
    price_index = rebase_to_first_observation(price)
    purchasing_power = big_macs_per_hour_worked(wage, price)

    figure, (ax_growth, ax_power) = plt.subplots(
        nrows=2,
        figsize=(11, 8.5),
        gridspec_kw={"height_ratios": [3, 2], "hspace": 0.32},
        facecolor=SURFACE,
    )

    # -- Panel 1: both series rebased to 100, so growth rates are comparable --
    # The minimum wage is a step function: it holds flat until Congress acts.
    ax_growth.plot(
        wage_index.index,
        wage_index.values,
        drawstyle="steps-post",
        color=WAGE_COLOR,
        linewidth=2,
        label="Federal minimum wage",
    )
    ax_growth.plot(
        price_index.index,
        price_index.values,
        color=BIG_MAC_COLOR,
        linewidth=2,
        marker="o",
        markersize=4,
        markerfacecolor=BIG_MAC_COLOR,
        markeredgecolor=SURFACE,
        markeredgewidth=1,
        label="Big Mac price",
    )
    ax_growth.axhline(BASELINE_INDEX, color=GRID, linewidth=1)

    _label_line_end(
        ax_growth, price_index, f"+{total_growth_percent(price):.0f}%", BIG_MAC_COLOR
    )
    _label_line_end(
        ax_growth, wage_index, f"+{total_growth_percent(wage):.0f}%", WAGE_COLOR
    )

    ax_growth.set_title(
        "The Big Mac outran the minimum wage, 2000-2020",
        fontsize=16,
        fontweight="bold",
        color=INK,
        loc="left",
        pad=30,
    )
    ax_growth.text(
        0.0,
        1.035,
        f"Both series indexed to 100 at their first observation in 2000. "
        f"Big Mac {annualized_growth_percent(price):.1f}%/yr vs. "
        f"minimum wage {annualized_growth_percent(wage):.1f}%/yr.",
        transform=ax_growth.transAxes,
        fontsize=10,
        color=INK_SECONDARY,
    )
    ax_growth.set_ylabel("Index (2000 = 100)", fontsize=10, color=INK_SECONDARY)
    ax_growth.legend(
        loc="upper left",
        frameon=False,
        fontsize=10,
        labelcolor=INK_SECONDARY,
    )

    # -- Panel 2: what that gap actually costs an hour of work --
    ax_power.plot(
        purchasing_power.index,
        purchasing_power.values,
        color=WAGE_COLOR,
        linewidth=2,
        marker="o",
        markersize=4,
        markerfacecolor=WAGE_COLOR,
        markeredgecolor=SURFACE,
        markeredgewidth=1,
    )
    ax_power.fill_between(
        purchasing_power.index, purchasing_power.values, color=WAGE_COLOR, alpha=0.08
    )
    _label_line_end(
        ax_power,
        purchasing_power,
        f"{purchasing_power.iloc[-1]:.2f} Big Macs",
        WAGE_COLOR,
    )
    ax_power.set_title(
        "One hour at the federal minimum wage, priced in Big Macs",
        fontsize=12,
        fontweight="bold",
        color=INK,
        loc="left",
        pad=10,
    )
    ax_power.set_ylabel("Big Macs per hour worked", fontsize=10, color=INK_SECONDARY)
    ax_power.yaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{v:.1f}"))

    for axes in (ax_growth, ax_power):
        _style_axes(axes)
        axes.set_xlim(START_DATE, END_DATE)

    figure.text(
        0.01,
        0.015,
        "Sources: FRED series FEDMINNFRWG (federal minimum hourly wage, nonfarm workers); "
        "Big Mac Index, The Economist / Kaggle.",
        fontsize=8,
        color=INK_MUTED,
    )
    figure.subplots_adjust(left=0.08, right=0.90, top=0.88, bottom=0.10)
    return figure


def build_table(wage: pd.Series, price: pd.Series) -> pd.DataFrame:
    """The table-view twin of the chart: every plotted value, one row per survey."""
    table = pd.DataFrame({"big_mac_price_usd": price})
    table["minimum_wage_usd_per_hour"] = wage.reindex(
        price.index, method="ffill"
    ).values
    table["big_mac_index_2000_base"] = rebase_to_first_observation(price).round(1)
    table["minimum_wage_index_2000_base"] = (
        rebase_to_first_observation(table["minimum_wage_usd_per_hour"]).round(1)
    )
    table["big_macs_per_hour_worked"] = big_macs_per_hour_worked(wage, price).round(2)
    return table


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def main() -> None:
    wage = load_minimum_wage()
    price = load_big_mac_price()

    figure = plot_comparison(wage, price)
    figure.savefig(CHART_PATH, dpi=200, facecolor=SURFACE)
    plt.close(figure)

    build_table(wage, price).to_csv(TABLE_PATH, float_format="%.2f")

    print(f"Federal minimum wage: ${wage.iloc[0]:.2f} -> ${wage.iloc[-1]:.2f} "
          f"(+{total_growth_percent(wage):.1f}%, "
          f"{annualized_growth_percent(wage):.2f}%/yr)")
    print(f"Big Mac price:        ${price.iloc[0]:.2f} -> ${price.iloc[-1]:.2f} "
          f"(+{total_growth_percent(price):.1f}%, "
          f"{annualized_growth_percent(price):.2f}%/yr)")
    print(f"Wrote {CHART_PATH.name} and {TABLE_PATH.name}")


if __name__ == "__main__":
    main()
