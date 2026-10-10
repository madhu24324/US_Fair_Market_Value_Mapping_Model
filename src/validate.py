"""Validate land-value proxies against observed conservation prices.

Reproduces the analysis behind Figure 2 of Nolte (2020) from the two validation
tables in the Dryad deposit:

  validation_public_acquisitions.csv   4,128 publicly funded acquisitions,
                                       observed price vs ten competing proxies
  validation_goco.csv                    389 Colorado (GOCO) easement purchases,
                                       observed price vs places_fmv_vacant

All values are USD per hectare, deflated to January 2017.

Accuracy is measured in LOGS. The prices span eight orders of magnitude
($0.06/ha to $9.2M/ha), so an error of $10,000/ha is negligible in Manhattan
and total in rural Nevada; only a ratio scale treats those alike. Squared error
in logs is therefore squared error in RATIO -- an RMSE of 1.0 means the typical
estimate is out by a factor of e = 2.7 in one direction or the other.

Usage:
    python src/validate.py                    # tables and figure
    python src/validate.py --no-figure        # tables only
    python src/validate.py --min-ha 10        # drop parcels under 10 ha
"""

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # render to file, never try to open a GUI window

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
ACQ_FILE = RAW / "validation_public_acquisitions.csv"
GOCO_FILE = RAW / "validation_goco.csv"
OUTPUT = ROOT / "figures" / "fig2_recreation.png"

ACTUAL = "spending_per_ha"

# Proxies in the order the deposit lists them: external estimates first, then
# tax records, then the paper's own PLACES estimates and their county means.
PROXIES = [
    "usda_nass", "withey", "johnson", "stralberg_adj",
    "tax_assessed", "tax_fmv",
    "places_fmv_vacant", "places_fmv_all",
    "places_fmv_vacant_county", "places_fmv_all_county",
]

LABELS = {
    "usda_nass": "USDA NASS",
    "withey": "Withey et al.",
    "johnson": "Johnson et al.",
    "stralberg_adj": "Stralberg (adj.)",
    "tax_assessed": "Tax assessed",
    "tax_fmv": "Tax FMV",
    "places_fmv_vacant": "PLACES vacant",
    "places_fmv_all": "PLACES all",
    "places_fmv_vacant_county": "PLACES vacant, county mean",
    "places_fmv_all_county": "PLACES all, county mean",
}

PLACES = {"places_fmv_vacant", "places_fmv_all",
          "places_fmv_vacant_county", "places_fmv_all_county"}

HL_COLOR = "#c0392b"      # PLACES estimates
OT_COLOR = "#34495e"      # competing proxies


# --------------------------------------------------------------------------
# loading
# --------------------------------------------------------------------------

def _positive(df, cols):
    """Blank out non-positive values, which cannot be logged.

    Zeros in the tax columns are not measurements: an assessed value of exactly
    $0.00 means the record carries no valuation, not that the land is worthless.
    Treating them as missing is the only defensible reading, and the count is
    reported so the decision stays visible.
    """
    out = df.copy()
    dropped = {}
    for c in cols:
        bad = out[c].notna() & (out[c] <= 0)
        if bad.any():
            dropped[c] = int(bad.sum())
            out.loc[bad, c] = np.nan
    return out, dropped


def load_acquisitions(min_ha=None):
    df = pd.read_csv(ACQ_FILE)
    if min_ha:
        df = df[df["ha"] >= min_ha]
    return _positive(df, [ACTUAL] + PROXIES)


def load_goco(min_ha=None):
    df = pd.read_csv(GOCO_FILE, dtype={"fips": str})
    if min_ha:
        df = df[df["ha_easement"] >= min_ha]
    return _positive(df, ["actual", "places_fmv_vacant"])


# --------------------------------------------------------------------------
# 1. summary statistics
# --------------------------------------------------------------------------

def _num(x, width):
    """Whole numbers for large values, 2 decimals for small ones."""
    return f"{x:>{width},.2f}" if abs(x) < 100 else f"{x:>{width},.0f}"


def summary_table(df, cols, title):
    print(f"\n{f' {title} ':=^100}")
    print(f"{'column':<28}{'n':>7}{'missing':>16}{'mean':>13}{'median':>12}"
          f"{'SD':>14}{'min':>11}{'max':>13}")
    for c in cols:
        v = df[c]
        ok = v.dropna()
        miss = int(v.isna().sum())
        pct = f"({miss / len(v) * 100:.1f}%)" if miss else ""
        print(f"{c:<28}{len(ok):>7}{miss:>6}{pct:<10}"
              f"{_num(ok.mean(), 13)}{_num(ok.median(), 12)}{_num(ok.std(), 14)}"
              f"{_num(ok.min(), 11)}{_num(ok.max(), 13)}")


def log_summary(df, cols, title):
    """The same columns in log space, where the analysis actually happens."""
    print(f"\n{f' {title} ':=^100}")
    print(f"{'column':<28}{'n':>7}{'mean ln':>10}{'SD ln':>9}"
          f"{'geometric mean':>17}{'geo. SD factor':>17}")
    for c in cols:
        v = np.log(df[c].dropna())
        print(f"{c:<28}{len(v):>7}{v.mean():>10.2f}{v.std():>9.2f}"
              f"{np.exp(v.mean()):>16,.0f}{np.exp(v.std()):>16.2f}x")


# --------------------------------------------------------------------------
# 2. accuracy
# --------------------------------------------------------------------------

def accuracy(actual, proxy, subset=None):
    """Accuracy of one proxy against observed price, in logs.

    Returns correlation, mean squared error, and the bias/variance split of
    that error. The split matters: a proxy can be uniformly wrong (large bias,
    correctable by rescaling) or erratic (large variance, not correctable).
    """
    m = actual.notna() & proxy.notna()
    if subset is not None:
        m &= subset
    a, p = np.log(actual[m]), np.log(proxy[m])
    if len(a) < 3:
        return None

    d = p - a                                   # log ratio: + means overestimate
    mse = float((d ** 2).mean())
    bias = float(d.mean())
    # Spearman is Pearson on ranks; computed directly to avoid a scipy dependency.
    rho = float(np.corrcoef(a.rank(), p.rank())[0, 1])
    return {
        "n": int(m.sum()),
        "r": float(np.corrcoef(a, p)[0, 1]),
        "rho": rho,
        "mse": mse,
        "rmse": float(np.sqrt(mse)),
        "bias": bias,
        "bias_ratio": float(np.exp(bias)),        # typical multiplicative error
        "med_ratio": float(np.exp(np.median(d))),
        "var": float(d.var()),
        "bias_share": bias ** 2 / mse * 100,      # % of MSE that is systematic
        "within2x": float((np.abs(d) < np.log(2)).mean() * 100),
        "within10x": float((np.abs(d) < np.log(10)).mean() * 100),
    }


def rank_table(df, actual_col, proxies, title, subset=None):
    """Score every proxy and print them ranked by MSE in logs (lower better)."""
    rows = {}
    for c in proxies:
        r = accuracy(df[actual_col], df[c], subset)
        if r:
            rows[c] = r
    order = sorted(rows, key=lambda c: rows[c]["mse"])

    print(f"\n{f' {title} ':=^100}")
    print(f"{'#':<3}{'proxy':<28}{'n':>6}{'r(log)':>8}{'rho':>7}{'MSE':>8}"
          f"{'RMSE':>7}{'bias':>7}{'x-err':>8}{'sys%':>7}{'<2x':>7}{'<10x':>7}")
    for i, c in enumerate(order, 1):
        r = rows[c]
        star = "*" if c in PLACES else " "
        print(f"{i:<3}{star}{LABELS[c]:<27}{r['n']:>6}{r['r']:>8.3f}"
              f"{r['rho']:>7.3f}{r['mse']:>8.3f}{r['rmse']:>7.2f}"
              f"{r['bias']:>+7.2f}{r['bias_ratio']:>7.2f}x{r['bias_share']:>6.0f}%"
              f"{r['within2x']:>6.0f}%{r['within10x']:>6.0f}%")
    print("  * = estimate from this paper (PLACES)")
    print("  MSE/RMSE/bias in natural logs; x-err = exp(bias), the typical")
    print("  multiplicative error (>1 overestimates, <1 underestimates);")
    print("  sys% = share of MSE that is systematic bias rather than scatter.")
    return rows, order


# --------------------------------------------------------------------------
# aggregate cost, the paper's actual claim
# --------------------------------------------------------------------------

def aggregate_cost(df, area_col, actual_col, proxies, title):
    """Would each proxy have predicted the total bill for this portfolio?

    The paper's headline is about UNDERESTIMATED CONSERVATION COSTS, which is a
    statement about totals, not about per-parcel error. This weights each
    parcel by its area and compares predicted total spending with observed.
    """
    print(f"\n{f' {title} ':=^100}")
    print(f"{'proxy':<28}{'parcels':>9}{'ha':>12}{'actual $M':>12}"
          f"{'predicted $M':>14}{'ratio':>9}")
    for c in proxies:
        m = df[actual_col].notna() & df[c].notna()
        ha = df.loc[m, area_col]
        act = (df.loc[m, actual_col] * ha).sum()
        pred = (df.loc[m, c] * ha).sum()
        print(f"{LABELS.get(c, c):<28}{int(m.sum()):>9}{ha.sum():>12,.0f}"
              f"{act / 1e6:>12,.0f}{pred / 1e6:>14,.0f}{pred / act:>8.2f}x")
    print("  Area-weighted. ratio < 1 means the proxy underestimates the total.")


# --------------------------------------------------------------------------
# 3. figure
# --------------------------------------------------------------------------

def _panel(ax, a, p, label, res, color):
    lo, hi = 30, 3e7
    ax.plot([lo, hi], [lo, hi], color="#888", lw=1.0, ls="--", zorder=1)
    ax.scatter(a, p, s=3.5, alpha=0.22, color=color, linewidths=0, zorder=2)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.tick_params(labelsize=7)
    ax.set_title(label, fontsize=9, pad=4)
    ax.text(0.04, 0.955,
            f"n = {res['n']:,}\nr = {res['r']:.2f}\nMSE = {res['mse']:.2f}",
            transform=ax.transAxes, fontsize=7, va="top", ha="left",
            linespacing=1.4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)


def render(acq, goco, order, res, goco_res, output, dpi=200):
    """Log-log scatter of estimate vs observed price, one panel per proxy.

    Panels run best-to-worst by MSE, so the ranking is visible in the layout.
    All panels share identical axes, and the dashed line is 1:1 -- points below
    it are underestimates.
    """
    n = len(order) + 1
    ncol = 4
    nrow = int(np.ceil(n / ncol))
    fig, axes = plt.subplots(nrow, ncol, figsize=(3.1 * ncol, 3.35 * nrow),
                             dpi=dpi)
    fig.patch.set_facecolor("white")
    axes = np.atleast_1d(axes).ravel()

    for ax, c in zip(axes, order):
        m = acq[ACTUAL].notna() & acq[c].notna()
        _panel(ax, acq.loc[m, ACTUAL], acq.loc[m, c],
               LABELS[c], res[c], HL_COLOR if c in PLACES else OT_COLOR)

    # GOCO easements, a separate portfolio with a single proxy
    ax = axes[len(order)]
    m = goco["actual"].notna() & goco["places_fmv_vacant"].notna()
    _panel(ax, goco.loc[m, "actual"], goco.loc[m, "places_fmv_vacant"],
           "GOCO easements (PLACES vacant)", goco_res, "#1f7a4d")

    for ax in axes[n:]:
        ax.set_visible(False)

    fig.suptitle("Land-value proxies vs observed conservation prices "
                 "(USD/ha, 2017 dollars)", fontsize=12, y=0.997)
    fig.supxlabel("Observed price paid, USD / ha", fontsize=10)
    fig.supylabel("Estimated land value, USD / ha", fontsize=10)
    fig.tight_layout(rect=(0.015, 0.015, 1, 0.985))

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=dpi, facecolor="white")
    plt.close(fig)


# --------------------------------------------------------------------------

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--min-ha", type=float, default=None,
                   help="drop parcels smaller than this many hectares")
    p.add_argument("--output", type=Path, default=OUTPUT)
    p.add_argument("--dpi", type=int, default=200)
    p.add_argument("--no-figure", action="store_true")
    args = p.parse_args(argv)

    missing = [f for f in (ACQ_FILE, GOCO_FILE) if not f.exists()]
    if missing:
        print("ERROR: validation tables missing: "
              + ", ".join(m.name for m in missing), file=sys.stderr)
        print("Extract them from the Dryad zip into data/raw/ -- see README.md",
              file=sys.stderr)
        return 1

    acq, acq_dropped = load_acquisitions(args.min_ha)
    goco, goco_dropped = load_goco(args.min_ha)

    print(f"public acquisitions : {len(acq):,} records, {acq['ha'].sum():,.0f} ha")
    print(f"GOCO easements      : {len(goco):,} records, "
          f"{goco['ha_easement'].sum():,.0f} ha, {goco.year.min()}-{goco.year.max()}")
    if args.min_ha:
        print(f"(filtered to parcels >= {args.min_ha:g} ha)")
    for name, d in (("acquisitions", acq_dropped), ("GOCO", goco_dropped)):
        if d:
            items = ", ".join(f"{k} {v}" for k, v in d.items())
            print(f"non-positive values blanked in {name}: {items}")

    # ---- 1. summary statistics ----
    summary_table(acq, ["ha", ACTUAL] + PROXIES,
                  "PUBLIC ACQUISITIONS: summary (USD/ha unless noted)")
    log_summary(acq, [ACTUAL] + PROXIES,
                "PUBLIC ACQUISITIONS: same columns in log space")
    summary_table(goco, ["ha_easement", "actual", "places_fmv_vacant"],
                  "GOCO EASEMENTS: summary")

    # ---- 2. accuracy ----
    # Pairwise-complete: every proxy scored on every record it covers. Maximises
    # sample size but scores different proxies on different parcels.
    res, order = rank_table(acq, ACTUAL, PROXIES,
                            "ACCURACY, pairwise-complete (ranked by MSE in logs)")

    # Common subset: the parcels where EVERY proxy has a usable value, so the
    # comparison is like-for-like. This is the ranking to trust.
    common = acq[PROXIES].notna().all(axis=1)
    print(f"\ncommon subset: {int(common.sum()):,} of {len(acq):,} records "
          f"({common.mean() * 100:.1f}%) have a usable value for all "
          f"{len(PROXIES)} proxies")
    res_c, order_c = rank_table(acq, ACTUAL, PROXIES,
                                "ACCURACY, common subset (like-for-like)",
                                subset=common)

    if order[:3] != order_c[:3]:
        print("\nNOTE: the top three differ between the two subsets -- the "
              "ranking is partly an artefact of which parcels each proxy covers.")

    goco_res = accuracy(goco["actual"], goco["places_fmv_vacant"])
    print(f"\n{' GOCO EASEMENTS: PLACES vacant vs observed ':=^100}")
    print(f"  n = {goco_res['n']}   r(log) = {goco_res['r']:.3f}   "
          f"rho = {goco_res['rho']:.3f}   MSE = {goco_res['mse']:.3f}   "
          f"RMSE = {goco_res['rmse']:.2f}")
    print(f"  bias = {goco_res['bias']:+.2f} ({goco_res['bias_ratio']:.2f}x)   "
          f"within 2x: {goco_res['within2x']:.0f}%   "
          f"within 10x: {goco_res['within10x']:.0f}%")
    print("  Easements buy partial rights, so the estimate is expected to")
    print("  exceed the price paid; the bias here is not an error as such.")

    # ---- aggregate ----
    aggregate_cost(acq, "ha", ACTUAL, PROXIES,
                   "AGGREGATE COST: predicted vs actual total spending")

    # ---- 3. figure ----
    if not args.no_figure:
        print(f"\nrendering to {args.output.name}")
        render(acq, goco, order_c, res_c, goco_res, args.output, args.dpi)
        print(f"done -> {args.output} "
              f"({args.output.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
