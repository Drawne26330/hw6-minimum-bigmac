# Federal minimum wage vs. the price of a Big Mac, 2000-2020

`minimum_wage_vs_big_mac.py` charts how fast each of the two figures grew over
the same 21 years.

```
python -m pip install pandas matplotlib
python minimum_wage_vs_big_mac.py
```

It writes `minimum_wage_vs_big_mac.png` (the chart) and
`minimum_wage_vs_big_mac.csv` (every plotted value, so the numbers are readable
without the picture).

## What it shows

| | 2000 | 2020 | Total | Annualized |
|---|---|---|---|---|
| Federal minimum wage | $5.15/hr | $7.25/hr | +40.8% | +1.65%/yr |
| Big Mac | $2.24 | $4.82 | +115.2% | +3.86%/yr |

The Big Mac rose about 2.8x as fast. An hour of minimum-wage work bought 2.30
Big Macs in 2000 and 1.50 in 2020.

The two measures are in different units ($/hour vs. $/sandwich), so the top
panel indexes both to 100 at their first 2000 observation. That is what puts
them on a single shared axis — plotting dollars-per-hour and dollars-per-burger
against two different y-scales would invent a relationship the data doesn't
contain. The minimum wage is drawn as a step function because it is one: it
holds flat until Congress changes it (2007, 2008, 2009 here).

## Data files

Both files are the real downloads, unmodified.

### `data/FEDMINNFRWG.csv` — federal minimum wage

FRED's CSV export of series
[FEDMINNFRWG](https://fred.stlouisfed.org/series/FEDMINNFRWG) — "Federal
Minimum Hourly Wage for Nonfarm Workers for the United States", monthly,
dollars per hour. Two columns, `observation_date,FEDMINNFRWG`, covering
1938-10 to the present; the script slices out 2000-2020.

Within that window the wage moves three times — $5.15 → $5.85 (2007-07) →
$6.55 (2008-07) → $7.25 (2009-07) — and has not moved since.

### `data/bigmac.csv` — Big Mac price

The Big Mac Index table from
<https://www.kaggle.com/datasets/mrmorj/big-mac-index-data>, one row per
country per survey (`date, iso_a3, name, local_price, dollar_price, ...`).

The script keeps the `iso_a3 == "USA"` rows and reads `local_price`, which for
the United States is the price in dollars. The Economist surveys roughly twice
a year, so 2000-2020 gives 33 observations.

## Notes on the comparison

- Both series are nominal dollars — neither is inflation-adjusted. That is the
  point of the comparison: it asks how minimum-wage pay tracked one everyday
  price, and general inflation is what sits between them.
- Federal minimum wage only. Many states set a higher floor, so this understates
  what a lot of minimum-wage workers actually earned.
- The Big Mac price is a national average from The Economist's survey, not a
  menu price at any particular restaurant.
