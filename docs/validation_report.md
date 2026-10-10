# Do the PLACES estimates outperform the alternatives?

**Validation of land-value proxies against observed conservation prices.**
Status as of 25 August 2026.

Reproduces the analysis behind Figure 2 of Nolte (2020) from the two validation
tables in the Dryad deposit. All numbers here come from `src/validate.py`; run
`python src/validate.py --no-figure` to regenerate them.

Companion to [`project_report.md`](project_report.md).

---

## 1. Summary

Yes, and by roughly a factor of two in squared log error over the best
competitor. On a like-for-like sample, PLACES-all has an MSE in logs of **0.77**
against **1.80** for the best non-PLACES proxy, and it is **unbiased** where four
of the six competitors underestimate by factors of 2 to 4.

Three qualifications matter and are developed below:

1. Aggregated to county means, the same PLACES estimates fall to MSE 2.39 —
   worse than two competitors. The advantage is *spatial resolution*, not the
   modelling approach.
2. For predicting a portfolio's **total** cost rather than individual parcels,
   USDA NASS is as accurate as PLACES and free.
3. The concern that the validation might be partly in-sample is **addressed by
   the paper and unsupported by anything testable in the data** (§7).

---

## 2. Data

| | Public acquisitions | GOCO easements |
| --- | --- | --- |
| File | `validation_public_acquisitions.csv` | `validation_goco.csv` |
| Records | 4,128 | 389 |
| Area | 110,380 ha | 249,517 ha |
| Period | not dated in the file | 1996–2017 |
| Observed price | `spending_per_ha` | `actual` |
| Proxies | 10 | 1 (`places_fmv_vacant`) |

All values are USD per hectare deflated to January 2017.

**Record counts.** The files contain 4,128 and 389 records. The paper's Figure 2
caption states 4,128 publicly funded acquisitions, so the acquisitions file is
complete as published. The GOCO file holds 389 rows, of which 335 carry a PLACES
estimate — and 335 is the count the paper reports for that dataset.

**Source of the acquisitions sample.** Per the paper, these are drawn from the
Conservation Almanac, a dataset of 67,187 publicly funded acquisitions, filtered
to those with spatial information, spending data, and satisfactory spatial
matches between Conservation Almanac polygons and assessor parcels (66% minimum
overlap in both directions). The 4,128 records are therefore already a
quality-screened subset, not a random sample of public land purchases.

---

## 3. Summary statistics and missing values

Public acquisitions, USD/ha except `ha`:

| Column | n | missing | mean | median | SD | min | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ha` | 4128 | 0 | 26.74 | 7.20 | 90.50 | 0.40 | 2,812 |
| **`spending_per_ha`** | 4128 | 0 | 99,659 | 18,869 | 351,381 | 0.06 | 9,207,005 |
| `usda_nass` | 4064 | 64 (1.6%) | 25,749 | 17,643 | 25,081 | 993 | 386,576 |
| `withey` | 4058 | 70 (1.7%) | 8,837 | 6,382 | 8,435 | 290 | 48,507 |
| `johnson` | 4128 | 0 | 12,034 | 9,056 | 9,463 | 1,013 | 103,567 |
| `stralberg_adj` | 4128 | 0 | 53,113 | 21,319 | 102,121 | 6,753 | 1,113,119 |
| `tax_assessed` | 3189 | 939 (22.7%) | 61,798 | 7,702 | 346,760 | 0.07 | 11,676,934 |
| `tax_fmv` | 2902 | 1226 (29.7%) | 83,426 | 9,864 | 380,901 | 0.38 | 11,676,934 |
| `places_fmv_vacant` | 4119 | 9 (0.2%) | 49,121 | 18,096 | 109,631 | 207 | 1,719,393 |
| `places_fmv_all` | 4119 | 9 (0.2%) | 65,438 | 20,246 | 150,048 | 179 | 2,752,286 |
| `places_fmv_vacant_county` | 4128 | 0 | 33,750 | 14,556 | 71,454 | 614 | 1,384,331 |
| `places_fmv_all_county` | 4128 | 0 | 51,274 | 18,114 | 105,930 | 757 | 1,860,292 |

GOCO easements:

| Column | n | missing | mean | median | SD | min | max |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ha_easement` | 389 | 0 | 641 | 190 | 1,569 | 1.82 | 13,484 |
| `actual` | 389 | 0 | 12,012 | 4,621 | 43,396 | 119 | 832,250 |
| `places_fmv_vacant` | 335 | 54 (13.9%) | 29,735 | 15,431 | 85,193 | 463 | 1,395,627 |

### 3.1 Missing-value handling

**Two decisions were required, and both are visible in the output.**

**Exact zeros in the tax columns are treated as missing, not as valuations.**
`tax_assessed` contains 393 values of exactly \$0.00 and `tax_fmv` contains 193.
An assessed value of exactly zero means the record carries no valuation, not
that the land is worthless; and zero cannot be logged in any case. Combined with
genuine NaNs this makes **tax FMV unusable on 29.7% of records and tax assessed
on 22.7%**. `src/validate.py` prints the count of blanked values on every run.

This missingness is very unlikely to be random — assessor coverage varies
systematically by state and by property type — so any accuracy figure for the
tax proxies is conditional on the subset where an assessment exists.

**Accuracy is reported on two samples, not one.** Pairwise-complete scoring uses
every record a proxy covers, which maximises sample size but scores different
proxies on different parcels. The common subset restricts to the **2,561 records
(62.0%)** where all ten proxies have a usable value, making the comparison
like-for-like. Both are reported; the common subset is the one to trust.

### 3.2 A note on the observed prices

`spending_per_ha` spans **\$0.06 to \$9,207,005 per hectare** — eight orders of
magnitude. The bottom end is nominal transfers and bargain sales rather than
market transactions. These were *not* filtered for the headline numbers, and
§6.2 shows they are not driving the result.

The spread is why everything here is measured in logs. An error of \$10,000/ha
is negligible in Manhattan and total in rural Nevada; only a ratio scale treats
those alike. Squared error in logs is squared error in *ratio*: an RMSE of 1.0
means the typical estimate is out by a factor of e ≈ 2.7.

---

## 4. Accuracy ranking

Common subset, n = 2,561, ranked by MSE in natural logs (lower is better).
`x-err` = exp(mean log error): the typical multiplicative miss, where values
below 1 underestimate. `sys%` is the share of MSE attributable to systematic
bias rather than scatter.

| # | Proxy | r (log) | ρ | MSE | RMSE | x-err | sys% | within 2× |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | **PLACES all** | 0.842 | 0.838 | **0.77** | 0.88 | 1.00× | 0% | 64% |
| 2 | **PLACES vacant** | 0.811 | 0.814 | 0.93 | 0.97 | 0.84× | 3% | 61% |
| 3 | Stralberg (adj.) | 0.571 | 0.578 | 1.80 | 1.34 | 1.01× | 0% | 39% |
| 4 | Tax FMV | 0.747 | 0.758 | 2.29 | 1.51 | 0.47× | 25% | 50% |
| 5 | PLACES all, county mean | 0.422 | 0.412 | 2.39 | 1.55 | 0.89× | 1% | 37% |
| 6 | PLACES vacant, county mean | 0.426 | 0.413 | 2.43 | 1.56 | 0.67× | 7% | 38% |
| 7 | USDA NASS | 0.407 | 0.419 | 2.45 | 1.56 | 0.63× | 9% | 40% |
| 8 | Johnson et al. | 0.433 | 0.446 | 3.40 | 1.85 | 0.33× | 37% | 31% |
| 9 | Tax assessed | 0.677 | 0.706 | 3.50 | 1.87 | 0.33× | 35% | 41% |
| 10 | Withey et al. | 0.283 | 0.277 | 4.84 | 2.20 | 0.23× | 44% | 24% |

Pairwise-complete scoring gives the same top three and the same bottom three;
the middle reshuffles, chiefly because USDA NASS improves and the PLACES county
means deteriorate when every proxy is held to the same parcels.

**The margin.** PLACES-all carries 43% of the squared log error of the best
competitor. In interpretable terms: typical error factor **2.4× versus 3.8×**,
and **64% of parcels priced within a factor of two versus 39%**.

### 4.1 The error is scatter, not bias — for PLACES only

Decomposing MSE into systematic bias plus scatter is where the paper's title
earns itself:

- **PLACES all is unbiased**: mean log error +0.00, i.e. 1.00×. None of its
  error is systematic.
- **Withey underestimates by 4.3×** (0.23×), and 44% of its MSE is that bias
  alone. Johnson and tax assessed both sit at 0.33× — a factor of three low —
  with 35–37% of their error systematic.

Four of the six competitors are not merely noisy but *wrong in a consistent
direction*. Rescaling them by a constant would remove a third to a half of their
total error. That is exactly the underestimation the paper's title asserts, and
it reproduces cleanly.

---

## 5. Two findings that qualify the headline

### 5.1 The county-mean collapse

Aggregating the same PLACES estimates to county means destroys most of their
advantage:

| Estimate | r (log) | MSE |
| --- | ---: | ---: |
| PLACES all, parcel level | 0.842 | 0.77 |
| PLACES all, county mean | 0.422 | 2.39 |
| PLACES vacant, parcel level | 0.811 | 0.93 |
| PLACES vacant, county mean | 0.426 | 2.43 |

MSE roughly triples, and the county-mean variants fall **below Stralberg and Tax
FMV** in the ranking. The variance explained drops from 67–72% to 26–27%.

This is a supporting result for the paper — its whole argument is that
resolution matters — but it carries a practical warning that the headline
obscures: **PLACES aggregated to county scale is a mediocre proxy**, no better
than the alternatives it is presented as beating. The advantage lives entirely
in resolving value *within* counties. Anyone citing "PLACES is more accurate"
while working at county resolution is citing a result that does not hold for
what they are doing.

### 5.2 Aggregate accuracy is a different question, and the ranking flips

Area-weighted totals over the same portfolio — what the whole set of
acquisitions would have been predicted to cost:

| Proxy | Parcels | Actual \$M | Predicted \$M | Ratio |
| --- | ---: | ---: | ---: | ---: |
| **PLACES all** | 4119 | 2,182 | 2,182 | **1.00×** |
| **USDA NASS** | 4064 | 2,168 | 2,145 | **0.99×** |
| PLACES vacant, county mean | 4128 | 2,187 | 2,107 | 0.96× |
| PLACES vacant | 4119 | 2,182 | 1,919 | 0.88× |
| Tax FMV | 2902 | 1,674 | 1,189 | 0.71× |
| Tax assessed | 3189 | 1,799 | 1,010 | 0.56× |
| Johnson et al. | 4128 | 2,187 | 1,017 | 0.46× |
| Withey et al. | 4058 | 2,141 | 650 | 0.30× |
| Stralberg (adj.) | 4128 | 2,187 | 2,982 | 1.36× |
| PLACES all, county mean | 4128 | 2,187 | 3,070 | 1.40× |

**USDA NASS predicts the total bill to within 1%** (\$2,145M against \$2,168M)
while ranking seventh of ten on parcel-level accuracy, with r = 0.41 and MSE
2.45. Its errors are large but they cancel.

The distinction is practical, not pedantic:

- **"What will this portfolio cost in aggregate?"** — USDA NASS is as accurate
  as PLACES here, and free. So is the PLACES vacant county mean at 0.96×.
- **"Which of these parcels are the expensive ones?"** — only the parcel-level
  PLACES estimates answer this, and that is where the whole advantage sits.

It also qualifies the paper's title. "Underestimation of conservation costs" is
robustly true of Withey (0.30×), Johnson (0.46×), tax assessed (0.56×) and tax
FMV (0.71×). It is **not** true of USDA NASS (0.99×) or Stralberg (1.36×), the
latter of which overestimates. The underestimation claim is a statement about
particular proxies, not about proxies in general.

---

## 6. GOCO easements and robustness

### 6.1 GOCO

n = 335 of 389 records carry an estimate.

| | |
| --- | ---: |
| r (log) | **0.852** |
| ρ | 0.815 |
| MSE | 1.301 |
| bias | +0.91 (2.49×) |
| within 10× | 98% |

**This is the highest correlation anywhere in the analysis**, above the 0.842
for PLACES-all on acquisitions. The 2.49× level offset is expected rather than
an error: an easement buys partial rights, so the fee-simple estimate should
exceed the price paid. The correlation is the meaningful quantity, and each of
these transactions was independently appraised by two certified appraisers,
making it the cleanest benchmark in the deposit.

### 6.2 Robustness

MSE in logs under four samples:

| Scenario | n | PLACES all | PLACES vacant | Best non-PLACES |
| --- | ---: | ---: | ---: | --- |
| Common subset | 2,561 | 0.77 | 0.93 | 1.80 (Stralberg) |
| Trim outer 1% of price | 2,522 | 0.71 | 0.85 | 1.66 (Stralberg) |
| Parcels ≥ 10 ha | 869 | 0.72 | **0.69** | 1.38 (USDA NASS) |
| Parcels ≥ 50 ha | 229 | 0.65 | **0.58** | 0.94 (Johnson) |

PLACES wins all four, so the extreme observed prices are not driving the result.
Two secondary observations:

- Above 10 ha the **vacant** variant overtakes the **all** variant, which is
  coherent: large conservation parcels are undeveloped, and a vacant-land model
  fits them better.
- On parcels above 50 ha the margin narrows sharply, with Johnson closing to
  0.94 against 0.58. Most of the competitors' error is concentrated in small
  parcels near development. For large-parcel conservation planning specifically,
  the case for PLACES is real but far less dramatic than the headline suggests.

---

## 7. The circularity question

PLACES is a model of property transaction prices, and the validation targets are
property transaction prices. If any of the 4,128 acquisitions were in the
model's training sample, the comparison would be partly in-sample and the margin
inflated. This was raised as an open concern before the paper's Methods were
consulted; it is now resolved, and the resolution is the paper's, not ours.

### 7.1 What the paper says

From the Materials and Methods of Nolte (2020), obtained from the Europe PMC
full-text API (PNAS and PMC both refuse automated retrieval). Training sales
come from ZTRAX, version 9 October 2019 — 6.01 million nonduplicate land sales.
The paper excludes, verbatim:

> "Sales likely involving public buyers or sellers, as estimated from seller,
> buyer, and owner names"

> "Sales of properties encumbered by easements"

and, on the prediction side:

> "To counter overfitting, OOB predictions are used for properties that were
> part of the training sample."

> "OOB predictions are model predictions that use only the subset of base
> learners (decision trees) that were not trained on the observation whose value
> they predict."

**The concern is addressed, and twice over.** Publicly funded acquisitions have,
by definition, a public buyer, so the first filter should remove them from
training outright. GOCO easements are encumbered, so the second filter removes
those. And even where a validation property did enter training, the prediction
used is out-of-bag — computed only from trees that never saw it.

One residual weakness is worth stating: the public-buyer filter is **heuristic
and name-based** ("as estimated from seller, buyer, and owner names"). An
acquisition routed through a land trust or NGO intermediary, with a private
seller and a nonprofit buyer, would not necessarily be flagged as public. The
paper does not quantify the filter's error rate. The out-of-bag mechanism is
what makes this second-order rather than fatal.

### 7.2 What we can test from our own columns

**Nothing in either file can link a row to a training observation.** The
acquisitions table carries `ct_id` (a Conservation Almanac transaction id —
8 digits, all unique, ranging 10028528 to 10490643), `fips`, `state`, `ha` and
the value columns. There is no sale date, no parcel number, no ZTRAX identifier,
and no buyer or seller name. The GOCO table adds only `year`. A direct
membership test is therefore impossible with the deposited data.

Three indirect tests were run instead. All three are negative for leakage.

**Test 1 — excess mass at zero residual.** A model fitted to an observation's own
price tends to reproduce it unusually closely, leaving a spike at zero in the
residual distribution. Comparing the share of residuals within ±0.01 in logs
against what local smoothness predicts from the ±0.05 and ±0.10 shares:

| Proxy | \|d\|<0.01 | \|d\|<0.05 | ratio | \|d\|<0.10 | ratio |
| --- | ---: | ---: | ---: | ---: | ---: |
| PLACES all | 1.12% | 6.55% | 0.85 | 12.65% | 0.88 |
| PLACES vacant | 1.29% | 5.85% | 1.10 | 12.04% | 1.07 |
| Stralberg (adj.) | 0.65% | 2.88% | 1.13 | 6.32% | 1.03 |
| Tax FMV | 0.62% | 3.62% | 0.86 | 7.06% | 0.88 |
| USDA NASS | 0.44% | 2.53% | 0.87 | 5.73% | 0.77 |

A ratio near 1 means the residual density is locally smooth through zero. The
PLACES columns (0.85–1.10) sit inside the range spanned by proxies that
**cannot** have been fitted to these prices (0.77–1.13). There is no spike.

**Test 2 — a provably clean control.** GOCO easements are excluded from training
by an explicit, mechanical filter, so they cannot be in-sample. If leakage were
inflating the acquisitions result, acquisitions should fit *better* than GOCO.

| Sample | r (log) | n |
| --- | ---: | ---: |
| GOCO easements (provably excluded) | **0.852** | 335 |
| Public acquisitions (same proxy) | 0.820 | 4,119 |

The clean sample fits **better**, not worse — the opposite of the leakage
prediction. This comparison is confounded (Colorado only, easements rather than
fee, appraised rather than negotiated prices), so it is suggestive rather than
decisive, but it points away from leakage.

**Test 3 — accuracy over time.** The raster is a 2010 cross-section and training
sales run to 2019. A leakage-driven fit should be tight inside the training era
and loose outside it. GOCO transactions by era:

| Era | n | r (log) | MSE | bias |
| --- | ---: | ---: | ---: | ---: |
| 1996–2001 | 47 | 0.828 | 2.78 | +1.53 |
| 2002–2007 | 145 | 0.840 | 1.16 | +0.84 |
| 2008–2013 | 104 | 0.907 | 0.86 | +0.72 |
| 2014–2017 | 39 | 0.909 | 1.21 | +0.94 |

Correlation is stable at 0.83–0.91 throughout, including the years before ZTRAX
coverage. MSE is worst in 1996–2001, but that is almost entirely **bias**
(+1.53, i.e. 4.6×) — land appreciation between a 1990s purchase and a 2010
valuation, which is expected and has nothing to do with training membership.

**Conclusion.** The paper addresses the concern explicitly through two exclusion
filters and out-of-bag prediction; no test available to us shows any trace of
leakage. The margin in §4 should be read as genuine. The one caveat that cannot
be closed from outside the paper is the accuracy of the name-based public-buyer
filter.

---

## 8. Cross-check against the paper's published numbers

Our independently computed statistics were compared with the values Nolte (2020)
reports. Squaring our log correlations gives variance explained:

| Quantity | Paper | This analysis | |
| --- | --- | --- | --- |
| USDA NASS, variance explained | 8% | 8.4% | ✔ |
| Tax FMV, variance explained | 56% | 55.8% | ✔ |
| PLACES parcel-level, variance explained | 67–72% | 67.2% / 71.6% | ✔ |
| PLACES county means, variance explained | 26–27% | 26.8% / 26.2% | ✔ |
| Withey underestimation factor | 3.5× | 3.4× (0.29×) | ✔ |
| Johnson underestimation factor | 2.2× | 2.2× (0.46×) | ✔ |

Six independent quantities reproduce, two of them exactly. This is strong
evidence that `src/validate.py` computes what the paper computed, and it
validates the pipeline in a way the Figure 1 work could not — against published
numbers rather than against pixels.

**One figure is unreconciled.** A summary of the paper's text attributed 32%
variance explained to the "county extractive returns" proxy, which is Withey.
Our Withey correlation gives 11.2%, while our Stralberg correlation gives 32.4%.
The 32% figure appears to belong to Stralberg rather than Withey, but this was
not confirmed against the paper's verbatim sentence and is recorded here as
open rather than resolved either way.

---

## 9. Limitations

- **The tax proxies are scored only where they exist**, on 70–77% of records,
  and that missingness is not random. Their ranking is conditional.
- **The acquisitions sample is quality-screened**, not random: 4,128 of 67,187
  Conservation Almanac transactions survived the spatial-match filter. Results
  generalise to well-mapped acquisitions, not to all public land purchases.
- **Stralberg is not an independent proxy in units.** The paper converts a
  unitless human-footprint index into dollars "by multiplying it with a constant
  derived from PLACES estimates". Its near-zero bias (1.01×) is therefore partly
  constructed, not measured. Its correlation remains independent; its *level*
  does not.
- **No confidence intervals.** Every figure here is a point estimate. Differences
  of 0.05 in MSE between adjacent proxies should not be treated as meaningful.
- **The Figure 2 reconstruction is not validated.** `figures/fig2_recreation.png`
  is built from the column list, not matched against the published image, which
  we do not have. The paper's Figure 2 has eight panels (A–H); the county-mean
  variants are discussed in the text rather than plotted. Deferred by request.

---

## 10. Reproducing

```bash
python src/validate.py --no-figure     # all tables in this document
python src/validate.py                 # tables plus the scatter grid
python src/validate.py --min-ha 10     # large-parcel sensitivity
```

Requires only `data/raw/validation_public_acquisitions.csv` and
`data/raw/validation_goco.csv` — not the rasters, not PADUS. Both are extracted
from the nested Dryad zip; see README §3.
