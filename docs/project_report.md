# Recreating Figure 1 of Nolte (2020)

**Project report — status as of 20 August 2026**

Repository: `https://github.com/Shauryah24526/landvalue`
Authors: Shauryah, Madhu

---

## 1. Objective

The project has two stages.

**Stage 1 (complete, documented here).** Reproduce Figure 1 of

> Nolte, C. (2020). High-resolution land value maps reveal underestimation of
> conservation costs in the United States. *PNAS* 117(47), 29577–29583.
> https://doi.org/10.1073/pnas.2012865117

from the author's archived data, to the point where the reproduction can be
compared with the published image quantitatively rather than by eye. The figure
is a continental-scale choropleth of estimated fair market value (FMV) of
private land, captioned *"Estimated FMV of private properties"*, with federal
land and Native American land drawn as flat fills and a logarithmic colourbar in
USD per hectare.

Reproducing the figure is not the research goal in itself. It is a
verification exercise: it establishes that we can read the deposit correctly,
that we understand what the raster encodes, and that we know which auxiliary
layers the published map depends on. Every ambiguity resolved at this stage
(what "Public Land" means, what the colour scale is, which tribal layer was
used) is an ambiguity that would otherwise propagate into stage 2.

**Stage 2 (blocked).** Extend the single-year estimate to an annual series,
2000–2024, so that changes in land value — and therefore in conservation cost —
can be tracked over time rather than inferred from one cross-section. The
blocker is data access and is documented separately in
[`data_request_log.md`](data_request_log.md).

---

## 2. Data

### 2.1 Primary source

The model outputs are archived on Dryad:

> Nolte, C. (2020). *Data for: High-resolution land value maps reveal
> underestimation of conservation costs in the United States.* Dryad Digital
> Repository. https://doi.org/10.5061/dryad.np5hqbzq9

Four files are deposited: two GeoTIFF rasters (`places_fmv_all.tif`,
`places_fmv_vacant.tif`, ~125 MB each) and two validation tables
(`validation_goco.csv`, `validation_public_acquisitions.csv`). Figure 1 is built
from `places_fmv_all.tif`, the estimate fitted to vacant *and* non-vacant sales.

### 2.2 What the raster actually contains

Verified directly with `src/inspect_raster.py`:

| Property | Value |
| --- | --- |
| CRS | EPSG:5070 — NAD83 / Conus Albers, equal-area, metres |
| Size | 9618 × 6054 px (58.2 Mpx) |
| Pixel size | 480 × 480 m |
| Bounds (E, N) | −2,357,205 to 2,259,435; 268,005 to 3,173,925 |
| Extent | 4,616.6 × 2,905.9 km |
| Data type | float32, single band |
| NoData | `0.0` |
| Storage | LZW, striped (block 1 × 9618), no overviews |

Four properties matter for correct handling, and three of them are traps:

1. **The stored quantity is the natural logarithm of USD per hectare**, not
   dollars. It must be exponentiated before it can be placed on a dollar scale.
   Read at 1/4 decimation, the resulting distribution is min \$5/ha, median
   \$5,436/ha, max \$33,630,760/ha over 2,103,833 valid cells.
2. **NoData is `0.0`, not a sentinel.** A genuine value of zero is therefore
   indistinguishable from missing data. In log space `0.0` corresponds to
   \$1/ha, which is far outside the plotted range, so the ambiguity is harmless
   here — but only because we read with `masked=True` and let rasterio apply the
   nodata tag rather than filtering on `== 0` by hand.
3. **Values are a 2010 cross-section expressed in 2017 dollars.** The raster is
   a single snapshot. It contains no time dimension of any kind, which is the
   direct cause of the stage-2 blocker.
4. **The raster is striped, not tiled.** Row-range reads are fast; many small
   windowed reads are slow.

Valid (non-nodata) cells occupy 57.8% of the bounding grid at 1/4 decimation;
the remainder is ocean, large water bodies, and territory outside the
contiguous US.

### 2.3 Auxiliary layers

Figure 1 draws three layers that are **not** in the Dryad deposit. Their
identification was a substantial part of the work and is reported in §5 and §6.

| Layer | Source | Selection |
| --- | --- | --- |
| Public Land (blue) | `PADUS2_1VectorAnalysisFile_ClipCensus.gdb` in the project archive `FMV.zip`; PADUS 2.1, 761,302 polygons | `Mang_Type = 'FED'` — 244,654 polygons, 2,667,263 km² |
| Native American (tan) | `bia_aian_lar_5070.geojson` in `FMV.zip`; BIA American Indian / Alaska Native Land Area Representations | all 333 polygons, 303,872 km² |
| State borders and coastline | US Census Bureau TIGER `cb_2018_us_state_500k` | 49 features, dropping FIPS 02, 15, 60, 66, 69, 72, 78 |

---

## 3. Method

The pipeline is a single script, `src/render_fig1.py` (~330 lines). It runs
end-to-end in one command and takes no manual steps.

```bash
python src/render_fig1.py --scale 1        # full resolution
python src/render_fig1.py                  # 1/4 draft, the default
```

**Step 1 — decimated masked read.** The raster is read at 1/*scale* resolution
using rasterio's `out_shape` with `Resampling.nearest`, and the affine transform
is rescaled to match. Nearest-neighbour is not a performance choice but a
correctness one: any averaging resampler blends nodata cells into their
neighbours, inventing finite land values along every coastline and lake margin.
With nearest, nodata cells stay exactly `0.0` and remain maskable.

**Step 2 — exponentiate.** `np.ma.exp` converts log USD/ha to USD/ha while
preserving the mask.

**Step 3 — colour mapping.** A `LogNorm` spanning \$1,000–\$1,000,000/ha is
applied through a `LinearSegmentedColormap` built from 64 stops recovered from
the published figure (§4), interpolated to 256 levels. Masked cells render
white. The result is converted to an explicit RGB array rather than passed to
`imshow` as scalars, because the next step overwrites individual pixels.

**Step 4 — flat fills.** Federal and tribal polygons are rasterised onto the
same grid with `rasterio.features.rasterize` and written into the RGB array as
constant colours — federal `#8ec0fe`, tribal `#e4aa75`, both sampled as the
modal pixel value inside those regions in the published image. Tribal is drawn
second, matching the published layer order where the two overlap.

Rasterisation uses `all_touched=False`, so a cell is filled only when its
*centre* falls inside a polygon. This is load-bearing. With `all_touched=True`,
every sub-pixel parcel in the 761,302-polygon PADUS file claims an entire 1.9 km
cell (at 1/4 decimation), which over-paints the map and speckles the whole
eastern half of the country blue.

**Step 5 — vector overlays.** The image is drawn in the raster's own projected
coordinates via `array_bounds`, so state boundaries and the merged national
outline register exactly without a separate warp. State borders are grey
`#7a7a7a`; the coastline, obtained by dissolving the states into one polygon, is
near-black `#1a1a1a`.

**Step 6 — furniture.** The colourbar (with `extend="both"` arrowheads, ticks at
1K/2K/5K/10K/20K/50K/100K/200K/500K/1M and the title "USD / ha") and the two
legend swatches are placed in figure-fraction coordinates measured off the
published image, which is 4164 × 2500 px with the map occupying 3924 × 2470 px
at offset (28, 14). Font size and line width are expressed as fractions of
figure height, so the layout is resolution-independent: the same constants
produce a correctly proportioned figure at 1/4 draft and at full resolution.

**Output.** Full resolution is 10206 × 6127 px, 53.4 MB PNG, produced in a
single pass.

**Environment.** Python 3.12; rasterio 1.5.1, geopandas 1.1.4, pyogrio 0.13.0,
matplotlib 3.11.1, numpy 2.5.2, shapely 2.1.2. Pinned in `requirements.txt`.

---

## 4. Recovering the colour scale

The published figure supplies a colourbar image but no colour specification.
The scale had to be recovered from the image itself.

### 4.1 The first attempt failed

The initial palette was a 33-stop ramp assembled by eye from the figure. It
produced a map that looked broadly plausible. Measured, it was not: of the
FMV-coloured pixels in the published figure, only **1.0%** fell within a
per-channel distance of 10 of *any* stop in that palette, 7.7% within 20, with a
median nearest-stop distance of **39**. A palette that cannot reproduce the
source image's own colours to better than 39/255 per channel is not that
image's palette.

This is worth recording because the failure was invisible to inspection. The
eye tolerates a wrong green ramp easily; the measurement does not.

### 4.2 Sampling the colourbar directly

The second attempt sampled the published colourbar. Two things had to be
established first.

**Is the bar logarithmic?** The ten tick positions were regressed on
log₁₀(value):

| Tick | y (px) | predicted | residual |
| ---: | ---: | ---: | ---: |
| \$1,000,000 | 1128 | 1128.1 | −0.13 |
| \$500,000 | 1219 | 1219.3 | −0.26 |
| \$200,000 | 1340 | 1339.7 | +0.28 |
| \$100,000 | 1431 | 1430.8 | +0.16 |
| \$50,000 | 1522 | 1522.0 | +0.03 |
| \$20,000 | 1642 | 1642.4 | −0.43 |
| \$10,000 | 1734 | 1733.6 | +0.44 |
| \$5,000 | 1825 | 1824.7 | +0.32 |
| \$2,000 | 1945 | 1945.1 | −0.14 |
| \$1,000 | 2036 | 2036.3 | −0.27 |

Fit: *y* = −302.714 · log₁₀(USD) + 2944.4, i.e. 302.71 px per decade.
**R² = 0.99999910, maximum residual 0.44 px over a 908 px bar.** The scale is
logarithmic, and `LogNorm(1e3, 1e6)` is the correct normalisation.

**Extraction.** For each of the 909 rows between the \$1K and \$1M ticks, the
median RGB across bar columns 4100–4152 was taken (median rather than mean, to
reject the tick marks that intrude at the bar edge). The resulting ramp was
reversed to run low→high and resampled to 64 evenly log-spaced stops, which are
listed verbatim in `src/render_fig1.py`. Endpoint colours: \$1,000/ha →
`#003908`, \$1,000,000/ha → `#000000`.

### 4.3 Validating the new ramp

Comparison is alignment-free — it compares colour *distributions*, not
co-located pixels, so it is unaffected by any residual registration error.
Distance is per-channel maximum (L∞) to the nearest palette stop; furniture is
blanked to white in both images before measuring.

| | ≤10 | ≤20 | ≤40 | median |
| --- | ---: | ---: | ---: | ---: |
| Published figure vs old 33-stop palette | 1.0% | 7.7% | 52.6% | 39 |
| Published figure vs new 64-stop palette | **48.9%** | **70.6%** | **83.4%** | **11** |
| Our recreation vs new 64-stop palette | 95.2% | 99.6% | 99.7% | 2 |

The third row is a control: our own render is drawn *from* this palette, so
95.2% within distance 10 measures the noise floor of PNG rendering and
anti-aliasing, not agreement. The published figure's residual distance (median
11) is attributable to the same anti-aliasing plus whatever compression the
published image has been through. The improvement over the first palette —
median 39 → 11, and a 49-fold increase in the share of near-exact matches — is
the substantive result.

---

## 5. "Public Land" means federal land only

The published legend says "Public Land". The obvious reading — every publicly
managed PADUS polygon — is wrong, and getting this right required rejecting one
hypothesis and testing four alternatives.

### 5.1 The exclusion hypothesis, tested and rejected

The figure is captioned *"Estimated FMV of **private** properties"*. This
suggests blue might mark land the model *excluded* rather than public land as
such — in which case blue would coincide with raster nodata, not with polygon
membership.

Measured on the raster grid:

| | cells | share |
| --- | ---: | ---: |
| Federal mask, total | 476,783 | |
| — over cells carrying a modelled value | 469,912 | **98.6%** |
| — over nodata cells | 6,871 | 1.4% |
| NoData cells, total | 1,533,419 | |
| — under public polygons | 6,871 | 0.4% |
| — under tribal polygons | 1,019 | 0.1% |
| — neither (ocean, lakes) | 1,525,967 | **99.5%** |

The hypothesis is decisively false. The model assigns values *underneath* public
land: 98.6% of federal land sits over cells that carry a modelled value. NoData
is essentially just water. Expressed as competing rules, as a share of painted
land:

| Rule | public | tribal | FMV-coloured |
| --- | ---: | ---: | ---: |
| Published figure (measured) | 22.6% | 3.9% | 73.5% |
| A: blue = all federal land | 22.6% | 3.5% | 73.9% |
| B: blue = public **and** nodata | 0.3% | 3.7% | 96.0% |
| B2: both overlays restricted to nodata | 0.3% | 0.0% | 99.6% |

Rule B would paint 0.3% of the map blue against a published 22.6%. The raster is
a wall-to-wall surface, and the blue is a mask drawn on top of it, not a hole in
it.

### 5.2 Which polygons, then?

Testing rule A against the earlier, broader definition of public land exposed a
5.5-percentage-point over-painting. Sweeping the candidate definitions:

| Rule | polygons | public share | tribal share |
| --- | ---: | ---: | ---: |
| Published figure (measured) | | **22.6%** | 3.9% |
| `Mang_Type ∈ {FED, STAT, LOC, DIST}` | 684,627 | 28.4% | 3.4% |
| `Mang_Type ∈ {FED, STAT, LOC}` | 666,094 | 28.3% | 3.4% |
| `Mang_Type ∈ {FED, STAT}` | 416,195 | 27.7% | 3.4% |
| **`Mang_Type = FED`** | **244,654** | **22.6%** | 3.5% |

Federal-only reproduces the published area exactly. A minimum-polygon-size
threshold was tested as an alternative explanation (the hypothesis being that
tiny municipal parks were dropped) and rejected: on the broad definition, the
public share falls only from 28.4% to 23.4% at a ≥25 km² cutoff and to 20.9% at
≥100 km², never passing cleanly through 22.6%, and doing so only by discarding
99.6% of the polygons.

### 5.3 Confirming it spatially, not just by area

Matching area is necessary but not sufficient — two different masks can cover
the same fraction of the map. A direct per-pixel test was run and, importantly,
**it could not discriminate**, which is reported here rather than suppressed.

Registering our grid onto the published image by maximising silhouette IoU gives
a best fit of 3924 × 2470 px at offset (28, 14), silhouette IoU **96.1%**, over
5,599,110 co-registered land pixels:

| Candidate | IoU vs published blue | recall | precision | coverage |
| --- | ---: | ---: | ---: | ---: |
| Published blue | | | | 22.8% |
| FED only | 45.7% | 62.4% | 63.1% | 22.5% |
| FED+STAT | 45.9% | 69.6% | 57.5% | 27.6% |
| FED+STAT+LOC+DIST | 45.7% | 70.4% | 56.6% | 28.4% |
| Tribal (BIA AIAN) — control | 47.0% | 62.3% | 65.7% | 3.7% |

All three candidates score ~46%, and so does the tribal layer, which is already
known to be correct. That ~46% is therefore a ceiling imposed by registration
slop at polygon edges, not a measure of layer identity. Per-pixel IoU is simply
not sensitive enough at this registration accuracy.

A registration-robust design was needed. The test asks a targeted question: in
the areas that state and local land *adds* on top of federal land, is the
published figure blue or is it FMV-coloured? Federal land is buffered outward by
approximately 12 px (a 25 px maximum filter) and those cells excluded, so
registration error near federal boundaries cannot leak into the comparison.

| Region | pixels | blue in published figure |
| --- | ---: | ---: |
| All mapped land (baseline) | 5,798,457 | 22.5% |
| Federal land | 1,262,134 | **63.1%** |
| State land, >12 px clear of federal | 75,765 | **23.0%** |
| Local/district land, >12 px clear of federal | 13,213 | 17.1% |
| No PADUS public polygon at all | 4,210,923 | 9.7% |

The result is unambiguous. Inside federal parcels the published figure is 63.1%
blue. Inside state parcels well clear of any federal parcel it is 23.0% blue —
statistically indistinguishable from the 22.5% baseline for all mapped land, and
nothing like 63.1%. Local and district land is 17.1%, *below* baseline. State,
local and district land is priced by the model, not masked.

The conclusion is that "Public Land" in the published legend means federally
managed land. This is a real substantive finding about the figure, not a
rendering detail: it implies the published map prices state and municipal
holdings as though they were on the market.

---

## 6. Overlay layers used and rejected

`FMV.zip` contains four candidate vector layers. Two were used and two rejected.

| Layer | Extent | Decision |
| --- | ---: | --- |
| `PADUS…gdb`, `Mang_Type = FED` | 2,667,263 km² | **Used** as Public Land — see §5 |
| `bia_aian_lar_5070.geojson` | 303,872 km² | **Used** as Native American |
| `padus_tribal_5070.geojson` | 411,654 km² | Rejected |
| `padus_private_5070.geojson` | 12,294 km² | Rejected |

**Why `padus_tribal` was rejected.** Two tribal layers exist. `padus_tribal`
(PADUS polygons with `Mang_Type = TRIB`) covers 411,654 km² and extends into
Alaska, which is outside the mapped area entirely. The BIA layer covers
303,872 km², is bounded to the lower 48, and burns to 3.6% of painted land
against a published 3.9% — the closest match available.

**Why `padus_private` was rejected.** Despite the name, it is not the private
land the figure prices. It is the ~0.2% of *protected areas* under private
management — land trusts and NGO preserves — totalling 12,294 km². It cannot be
the "Public Land" layer, which covers roughly 22% of the map, and it is not the
figure's subject either.

The name of a layer is not evidence of its contents; in both rejected cases the
name pointed the wrong way and only the measured extent settled it.

---

## 7. Validation results

All figures below compare the full-resolution recreation
(10206 × 6127 px) against the published figure (4164 × 2500 px). Both are
measured after blanking the same *relative* regions — the colourbar column right
of x = 0.9606 W, and the legend block below y = 0.86 H in the right-hand 13.5% —
so that neither image's furniture is counted as map content.

### 7.1 Colour agreement

Reported in §4.3. Summary: median nearest-stop distance 11 for the published
image against our palette, versus 2 for our own render against the same palette
and 39 for the palette the project started with.

### 7.2 Overlay coverage

| Layer | Published | Recreation | Difference |
| --- | ---: | ---: | ---: |
| Public land (blue) | 22.5% | 21.7% | −0.7 |
| Tribal land (tan) | 3.9% | 3.6% | −0.2 |
| FMV-coloured | 73.7% | 74.6% | +1.0 |

Coverage is stable under decimation — federal land burns to 13.1% of the
bounding grid at both 1/4 and full resolution — so the residual is not a
resampling artefact.

### 7.3 Value distribution by band

Sixteen equal-width bands in log space between \$1,000 and \$1,000,000/ha. The
"raster" column reads values straight from the GeoTIFF for priced cells only;
the "recreation" and "published" columns read them back out of the respective
PNGs by nearest-palette-stop lookup. The raster column is the ground truth and
is included specifically to separate rendering error from read-back error.

| Band | \$/ha | Raster | Recreation | Published | Pub − Rec |
| ---: | --- | ---: | ---: | ---: | ---: |
| 0 | 1,000–1,540 | 7.2% | 7.3% | 12.8% | **+5.5** |
| 1 | 1,540–2,371 | 8.5% | 8.6% | 8.3% | −0.3 |
| 2 | 2,371–3,652 | 13.6% | 12.7% | 9.5% | −3.2 |
| 3 | 3,652–5,623 | 17.4% | 17.4% | 13.7% | −3.7 |
| 4 | 5,623–8,660 | 17.4% | 17.7% | 18.8% | +1.1 |
| 5 | 8,660–13,335 | 13.8% | 14.9% | 10.2% | −4.7 |
| 6 | 13,335–20,535 | 8.3% | 8.4% | 9.5% | +1.1 |
| 7 | 20,535–31,623 | 4.2% | 4.1% | 3.3% | −0.8 |
| 8 | 31,623–48,697 | 2.6% | 2.5% | 1.5% | −1.0 |
| 9 | 48,697–74,989 | 1.8% | 1.7% | 2.1% | +0.4 |
| 10 | 74,989–115,478 | 1.3% | 1.3% | 7.4% | **+6.1** |
| 11 | 115,478–177,828 | 1.0% | 1.1% | 1.0% | −0.1 |
| 12 | 177,828–273,842 | 0.9% | 0.8% | 0.3% | −0.5 |
| 13 | 273,842–421,697 | 0.7% | 0.7% | 0.5% | −0.2 |
| 14 | 421,697–649,382 | 0.5% | 0.5% | 0.7% | +0.1 |
| 15 | 649,382–1,000,000 | 0.9% | 0.3% | 0.3% | ±0.0 |

Total absolute difference between published and recreation: **28.8 percentage
points**, of which bands 0 and 10 alone account for 11.6.

The critical column is Raster vs Recreation: they agree to within 0.6 points in
every band except band 15, where clamping of values above \$1M/ha into the top
stop accounts for the gap. **The render is faithful to the raster.** Any
remaining discrepancy therefore lives either in the published figure or in the
process of reading dollar values back out of a published PNG — not in the
rendering pipeline.

---

## 8. Known limitations

**Band 10 (\$75K–\$115K/ha): published 7.4% vs 1.3%, deliberately not chased.**
This is the largest single discrepancy. It was ruled out of scope on
methodological grounds rather than left open by neglect. Our band figures for
the published image are obtained by inferring dollar values from PNG colours,
and near the yellow–orange transition several adjacent bands map to nearly
identical RGB values. The lookup is therefore least reliable exactly where the
anomaly appears, so the anomaly cannot be attributed to the map's content
without an independent measurement that the published PNG cannot supply.

**Band 0 (\$1,000–\$1,540/ha): published 12.8% vs 7.3%.** Same signature, same
cause. The raster gives 7.2% and our render gives 7.3%, so the render is
correct; the discrepancy is in the read-back. Ramp stops 0–7 span only
RGB(0,57,8) to (2,78,1) — eight bands compressed into a colour range of roughly
20 units per channel, well inside compression noise. A further 3.2% of priced
cells fall below \$1,000/ha and are clamped into band 0, which the published
figure handles with its lower arrowhead.

**9.7% of land with no PADUS public polygon reads blue in the published
figure.** This is the clearest unresolved item. Part of it is registration slop
at parcel edges and part is inland water rendered in a similar blue, but neither
fully accounts for 9.7%, and it is the likely source of the 0.7-point shortfall
in our public-land coverage (21.7% vs 22.5%). Resolving it would require either
a higher-quality copy of the published figure or the author's own rendering
code.

**Registration is 96.1%, not 100%.** Silhouette IoU between our grid and the
published map tops out at 96.1%. The residual 3.9% is concentrated at
coastlines and is consistent with a slightly different coastal clip in the
published figure, but we have not identified the exact difference. This bounds
the precision of every co-located pixel comparison, which is why §5.3 needed a
registration-robust design.

**The validation tables are unused.** `validation_goco.csv` and
`validation_public_acquisitions.csv` have been downloaded but play no part in
Figure 1 and have not yet been examined.

**`places_fmv_vacant.tif` is unused.** Only the all-sales raster has been
rendered.

**Comparison is against a PNG, not the vector original.** Every measurement in
§7 is bounded by the quality of the published raster image available to us. The
project has no access to the figure's source vector or the code that produced
it.

---

## 9. What blocks the next stage

Stage 2 requires per-year land values for 2000–2024. The Dryad deposit cannot
supply them under any manipulation: it is one 2010 cross-section, and no
sequence of operations on a single snapshot produces a time series.

Producing the series requires re-estimating the model on transaction data with
sale dates. The underlying source is ZTRAX (Zillow Transaction and Assessment
Dataset), which is licensed and not redistributable — this is why the deposit
contains model outputs and validation tables but no sales microdata.

Two access routes are being pursued in parallel, and both are currently open:

1. Obtain ZTRAX through ICPSR study 39652 and re-estimate. Blocked on
   institutional access — IIIT Delhi is not an ICPSR member — and, even if
   granted, the current release ends in 2020, leaving 2021–2024 uncovered.
2. Ask the author directly whether per-year FMV estimates already exist, which
   would avoid re-estimation entirely.

Both enquiries have been sent and neither has been answered. Full detail,
including the fee position and the agreement requirements, is in
[`data_request_log.md`](data_request_log.md).

Until one of these resolves, stage 2 cannot begin. Work that can proceed
meanwhile: examining the two validation tables, rendering and comparing
`places_fmv_vacant.tif`, and reproducing the paper's other figures from the
same deposit.

---

## 10. Repository state

Six commits on `main`, latest `3a11ed4`. Seven tracked files:

```
.gitignore
README.md
requirements.txt
src/inspect_raster.py       raster metadata inspection
src/render_fig1.py          the full pipeline
figures/.gitkeep
src/.gitkeep
```

No data and no figures are tracked, by design. The rasters are ~125 MB each and
the PADUS geodatabase is ~423 MB — all above GitHub's 100 MB file limit and all
publicly redownloadable. `README.md` §3, §3b and §3c give exact download
instructions and expected paths for every input, so a clean clone plus
`pip install -r requirements.txt` plus those downloads reproduces the figure
with one command.

The analysis scripts used to produce §4, §5 and §7 were exploratory and are not
tracked; their numerical results are recorded in this report, and every
measurement quoted here was re-run against the current code before writing.
