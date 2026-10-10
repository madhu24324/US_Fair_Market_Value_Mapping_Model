# Predictor inventory

An itemised list of every predictor variable used to estimate parcel-level fair
market value in Nolte (2020) and in the extension by Gold, Binder and Nolte
(2023), together with the source dataset, vintage and resolution of each — and
an assessment of which of them could be re-measured year by year to support the
planned 2000–2024 annual series.

## 1. Scope and provenance

Three documents were used, and it matters which contributed what.

| Document | What it contributed |
| --- | --- |
| Nolte (2020), *SI Appendix* (`data/refs/pnas.2012865117.sapp.pdf`) | **Table S3** — the authoritative list of predictor variables and the domain groupings. Nothing else: Table S3 has three columns, *Domain / Variables / Justification*, and names **no source dataset, no vintage and no resolution for any variable**. |
| Nolte (2020), *main text*, Materials and Methods → Training Data | Every source dataset, product name and citation in Table 1 below. |
| Gold et al. (2023), PLOS ONE 18(9):e0291182 (`data/refs/journal.pone.0291182.pdf`) | The added predictors in Table 2, with their sources, and the one-sentence characterisation of Nolte's base set. |

The main text was not among the files supplied. Because the SI alone cannot
answer four of the seven requested columns, it was retrieved from the Europe PMC
REST API (`PMC7703645`) and the raw XML was parsed and read directly, rather
than through a summarising layer — a citation year is the publication year of a
dataset reference, not the vintage of the phenomenon the data describes, and the
two are easy to conflate.

**How "not stated" is used below.** The *Source*, *Vintage* and *Native
resolution* columns are strictly what the papers say. Where a paper gives a
product but no vintage, the cell reads `not stated`, and any year that appears
only in the reference list is labelled as a product or release year rather than
being promoted to a vintage. *Update frequency* is different: **neither paper
addresses update frequency for any variable**, so that column is an assessment,
marked as such, and §5 lists the external facts it rests on.

## 2. Table 1 — Nolte (2020), main model

Variable names are quoted from SI Appendix Table S3; sources from the main-text
Methods. Twenty-nine variables in ten domains.

| Predictor group | Variable name as used in the paper | What it measures | Source dataset | Vintage | Native resolution | Update frequency (assessed) |
| --- | --- | --- | --- | --- | --- | --- |
| Buildings | Building density (n/ha) | How many buildings stand on the parcel, per hectare — whether it is built on at all | Microsoft U.S. Building Footprints (125.2 M buildings) | not stated (product released 2018; accessed 2 Feb 2020) | not stated | One-off snapshot |
| Buildings | % building area | Share of the parcel's surface under a building footprint — how heavily built it is | Microsoft U.S. Building Footprints | not stated (as above) | not stated | One-off snapshot |
| Nearby development | % building footprints within 500 m radius | How built-up the immediate surroundings are — local development pressure | Microsoft U.S. Building Footprints | not stated (as above) | not stated | One-off snapshot |
| Nearby development | % building footprints within 5 km radius | The same at neighbourhood-to-town scale — regional development pressure | Microsoft U.S. Building Footprints | not stated (as above) | not stated | One-off snapshot |
| Accessibility | Distance to paved roads | How far the parcel is from the nearest paved road — whether it can be reached and serviced | TIGER/Line Shapefiles, US Census Bureau | 2019 (stated in the product name) | not stated | **Annual** |
| Accessibility | Travel time to major cities | How long it takes to reach a major urban market from the parcel | Nelson (2008), *Travel Time to Major Cities: A Global Map of Accessibility*, JRC, European Commission | not stated (product published 2008) | not stated | One-off |
| Demographics | Median household income (block group) | Typical income of households in the surrounding neighbourhood — local spending capacity | IPUMS National Historical Geographic Information System (NHGIS), v13.0 | **not stated** — no census or ACS table, and no survey year, is named | Census block group (Table S3); "census block" (main text) — see §4 | **Annual** (ACS), from the mid-2000s |
| Nearby protection | % protection (area) within 5 km radius in 2010 | How much of the surrounding land is already permanently protected — open-space amenity | PAD-US 2.0 (fee ownership) + National Conservation Easement Database (easements); New England Protected Open Space in New England; COMaP in Colorado | **2010** (the measurement year, stated in Table S3) | not stated | Periodic (source releases); the *variable* is year-specific — see §6 |
| Terrain | Average slope (deg) | Mean steepness of the parcel — buildability and farmability | USGS National Elevation Dataset | not stated (product year 2017; accessed 6 Dec 2018) | **1/3 arc-second** (stated) | Static in effect |
| Terrain | Average elevation (m) | Mean height above sea level | USGS National Elevation Dataset | not stated (as above) | **1/3 arc-second** (stated) | Static in effect |
| Water | % wetland area | Share of the parcel that is wetland — restricts most other uses | USFWS National Wetlands Inventory (Seamless Wetlands Data) | **not stated** — the reference carries no year at all | not stated | Rolling revision, no annual vintages |
| Water | Water frontage (rivers and lakes) | Whether, and how much, the parcel fronts onto a river or lake — an amenity | USGS National Hydrography Dataset | not stated (product year 2017) | not stated | Rolling revision, no annual vintages |
| Water | % coastal waters within 2.5 km | Immediate coastal exposure — beach and boating access | Esri, North America Water polygons | not stated (product year 2009) | not stated | One-off |
| Water | % coastal waters within 50 km | Broader coastal setting — being on an island, peninsula or spit | Esri, North America Water polygons | not stated (as above) | not stated | One-off |
| Flood risk | Average metres of inundation, 100-year **pluvial** flood | Expected depth of standing water in a 1%-annual-chance rainfall flood | Wing et al. (2018), US-wide flood hazard layers | not stated | not stated | One-off research product |
| Flood risk | Average metres of inundation, 100-year **fluvial** flood | The same for river flooding | Wing et al. (2018) | not stated | not stated | One-off research product |
| Land cover | % forest | Share of the parcel under tree cover | National Land Cover Database | **2011** (stated) | not stated | Periodic (~2–3 yr) |
| Land cover | % cropland | Share under cultivated crops | NLCD | **2011** (stated) | not stated | Periodic (~2–3 yr) |
| Land cover | % pasture | Share under managed pasture or hay | NLCD | **2011** (stated) | not stated | Periodic (~2–3 yr) |
| Land cover | % grassland | Share under unmanaged herbaceous cover | NLCD | **2011** (stated) | not stated | Periodic (~2–3 yr) |
| Land cover | % shrubland | Share under scrub and shrub | NLCD | **2011** (stated) | not stated | Periodic (~2–3 yr) |
| Land cover | % barren | Share of bare rock, sand or clay | NLCD | **2011** (stated) | not stated | Periodic (~2–3 yr) |
| Land cover | % open space | Share of developed-but-open land — parks, verges, large lots | NLCD | **2011** (stated) | not stated | Periodic (~2–3 yr) |
| Land cover | Development intensity | How densely developed the parcel is, on NLCD's low/medium/high gradient | NLCD | **2011** (stated) | not stated | Periodic (~2–3 yr) |
| Space | x | Easting of the parcel — absorbs unobserved east–west variation | Derived from parcel geometry; no external dataset | n/a | Parcel | Static by construction |
| Space | y | Northing of the parcel | Derived from parcel geometry | n/a | Parcel | Static by construction |
| Space | 45° diagonal | Position along a NE–SW axis, so the trees can cut space on a diagonal rather than only N–S/E–W | Derived from parcel geometry | n/a | Parcel | Static by construction |
| Space | 135° diagonal | Position along a NW–SE axis | Derived from parcel geometry | n/a | Parcel | Static by construction |
| Time | Date of sale (continuous variable) | When the sale happened — absorbs inflation and market cycles | ZTRAX (Zillow Transaction and Assessment Database), version 9 October 2019 | **2000–2019** (the training window, stated) | Transaction-level date | **Discontinued** — see §6 |

Two structural facts that belong with this table:

- **Parcel size is not in the main model.** It appears only as a robustness
  check ("Area as predictor: addition of log parcel size"), so the 29 variables
  above are the full main specification.
- **Every variable is computed on one parcel fabric.** The main text states that
  parcel boundaries "reflect conditions observed recently, mostly between 2016
  and 2019", with 25 ha hexagonal dummy parcels where no digital boundaries
  exist. This has consequences for the annual series that §6 returns to.

## 3. Table 2 — Gold et al. (2023), predictors added to the base set

Gold et al. take Nolte's set as their "Restricted" set, **drop the two flood-risk
variables**, and add the following to form the "Full" set.

| Predictor group | Variable name as used in the paper | What it measures | Source dataset | Vintage | Native resolution | Update frequency (assessed) |
| --- | --- | --- | --- | --- | --- | --- |
| Climate | Minimum temperature, seasonal normal (× 4 seasons) | How cold it typically gets — a limit on which crops will grow | PRISM Climate Group, Oregon State University — *PRISM 30-year climate normals* | 30-year normals; **the normals period is not stated** (reference dated 2021) | not stated | Re-issued once per decade |
| Climate | Mean temperature, seasonal normal (× 4) | Typical growing-season warmth | PRISM 30-year normals | as above | not stated | Once per decade |
| Climate | Maximum temperature, seasonal normal (× 4) | How hot it typically gets — heat and drought stress | PRISM 30-year normals | as above | not stated | Once per decade |
| Climate | Dew point temperature, seasonal normal (× 4) | Atmospheric humidity — evaporative demand on crops | PRISM 30-year normals | as above | not stated | Once per decade |
| Climate | Precipitation, seasonal normal (× 4) | How much rain falls, and in which season | PRISM 30-year normals | as above | not stated | Once per decade |
| Irrigation | Ever irrigated prior to sale (binary) | Whether the parcel has ever been irrigated — a marker of sunk investment in machinery and infrastructure | LANID-US (Landsat-based Irrigation Dataset); Xie & Lark (2021) | **1997–2017 annual** (stated) | **30 m** (printed in the paper as "30 sq. meters") | Annual within 1997–2017; **series ends 2017** |
| Irrigation | Irrigated in the 3 years preceding sale (binary) | Whether irrigation is currently active rather than historical | LANID-US | **1997–2017** (stated) | **30 m** (as printed) | as above |
| Soil | % Prime farmland | Share of the parcel on soil of optimal agricultural quality | USDA NRCS Soil Survey Geographic Database (SSURGO) | **not stated** — the reference prints its year as "N/A" | not stated ("map unit polygons") | Rolling revision, no annual vintages |
| Soil | % Unique farmland | Share on soil supporting high-value speciality crops (e.g. Californian vineyards) | SSURGO | not stated | not stated | Rolling |
| Soil | % Farmland of statewide importance | Share on state-designated farmland one tier below prime | SSURGO | not stated | not stated | Rolling |
| Soil | % Farmland of local importance | Share on locally designated farmland below the statewide tier | SSURGO | not stated | not stated | Rolling |
| Soil | % Conditional classes (e.g. "Prime if drained", "Prime if protected from flooding") | Share on soil that would be prime or important *given* a stated improvement | SSURGO | not stated | not stated | Rolling |
| Real estate | House price index (county, annual, all-transactions) — county models | How local house prices have moved over time, indexed — carries the time trend in the residential market | US Federal Housing Finance Agency, All-Transactions House Price Index | Yearly values across the **2000–2020** sample (stated) | County | **Annual** (published quarterly) |
| Real estate | Median home value (county-year) — farm-resource-region models | The dollar level of the local housing market, comparable across counties | Realtor.com, *Real Estate Data, Inventory — Monthly*, county median listing price, rebased to 2017 and extended with the HPI | Listing data **July 2016 – present** (stated); extended across 2000–2020 by multiplying by HPI | County | **Monthly**, but begins July 2016 |
| Parcel | Parcel size | How large the parcel is | Parcel boundaries (Regrid "Data with Purpose", plus the commercial and open sources used by PLACES) | not stated | Parcel | Rolling |

The exact number of individual conditional-soil variables is **not stated**; the
paper describes the aggregation rule (`"Prime if drained or protected from
flooding"` is assigned to both `Prime if drained` and `Prime if protected from
flooding`) but never enumerates the resulting columns. The five soil rows above
are therefore groups, not a variable count. The climate rows expand to
**20 variables** — five measures across four meteorological seasons.

## 4. Discrepancies between the two documents

These are worth recording because they affect anyone trying to rebuild the
predictor set from the published description alone.

1. **Coastal radii disagree by a factor of 1,000.** The main text says
   "a short-distance radius (50 m …) and a long-distance radius (2,500 m …)".
   Table S3 says "% coastal waters within 2.5km and 50km (respectively)".
   2,500 m and 2.5 km agree; **50 m and 50 km do not**. One of the two is a unit
   error, and there is no way to tell which from the published material. The
   main text's reasoning — 50 m to "flag properties with beach and boating
   access" — is internally coherent for a very tight buffer.
2. **The income geography disagrees.** Table S3 says block group; the main text
   says "census block level". Median household income is not published at block
   level, so block group is the plausible reading, but the papers conflict.
3. **The land-cover class list disagrees.** The main text names six classes
   (forest, crops, pasture, grassland, shrub, barren). Table S3 names eight,
   adding `% open space` and `development intensity`. The SI's own "No land
   cover" robustness check names the same six as the main text, which suggests
   open space and development intensity are carried in the model but grouped
   elsewhere.
4. **Protection is described as multiple variables but tabulated as one.** The
   main text says "I compute the presence of nearby protection (% area) within
   different radii and *years*" (plural); Table S3 lists a single variable, at
   5 km, in 2010.
5. **Gold et al.'s HPI citation points at the wrong series.** The text describes
   "yearly all-transaction house price index values at the county level", but
   reference [14] is `USSTHPI`, the FHFA all-transactions index **for the United
   States** as a whole. The county-level product exists; the citation does not
   point to it.
6. **The NHGIS citation gives a platform version, not a dataset.** "IPUMS NHGIS,
   version 13.0" identifies the delivery system. Which census or ACS table, and
   which survey year, supplied median household income is not recoverable from
   either paper.

## 5. Resolutions and update cycles the papers do not give

The tables above say `not stated` wherever the papers are silent, which leaves
most of the resolution column empty and the whole update-frequency column
unsupported. The publishers do document these. **The following is not from
either paper** — it is background needed to answer §6, and should be verified
against each provider before it is relied on in print.

| Product | Native resolution | Release cadence |
| --- | --- | --- |
| Microsoft U.S. Building Footprints | Vector polygons (no raster resolution) | Released 2018; later national refreshes exist but not as a back-castable annual series |
| TIGER/Line | Vector | Annual editions |
| Nelson travel-time map | ~1 km (30 arc-second) | One-off, 2008 |
| NHGIS (ACS) | Block group | ACS 5-year estimates released annually |
| PAD-US | Vector | Periodic major versions (roughly every 1–2 years) |
| USGS NED / 3DEP | 1/3 arc-second ≈ 10 m | Rolling; terrain effectively static |
| USFWS NWI | Vector | Rolling revision |
| USGS NHD | Vector | Rolling revision |
| Esri North America Water | Vector | One-off, 2009 |
| Wing et al. flood layers | 30 m | One-off research product |
| NLCD | 30 m | Periodic: 2001, 2004, 2006, 2008, 2011, 2013, 2016, 2019, 2021 |
| PRISM 30-year normals | 800 m | Normals period advances once per decade |
| LANID-US | 30 m | Annual, but the published series runs 1997–2017 |
| SSURGO | Vector map units (~1:12,000–1:24,000) | Rolling revision |
| FHFA county HPI | County | Annual (published quarterly), back to the 1970s |

## 6. Which predictors could be re-measured per year for 2000–2024

The question only bites for predictors that actually change over a 25-year
window. Sorting the 29 + 15 variables that way gives four groups.

### 6.1 Time-invariant — annual re-measurement is unnecessary, not impossible

`x`, `y`, both diagonals, average slope, average elevation, water frontage,
both coastal-water variables, % wetland area, all five soil groups, and all
twenty climate normals.

Terrain, coastline, soil taxonomy and 30-year climate normals do not move on a
25-year timescale in any way a land-value model would detect. Holding these
fixed across the series is defensible and costs nothing. The two flood-risk
variables belong here in practice: flood hazard is quasi-static, and Gold et al.
drop them anyway.

**This is roughly 30 of the 44 variables.** The annual-series problem is much
narrower than the predictor count suggests.

### 6.2 Genuinely available per year across the full 2000–2024 span

| Variable | Why it works |
| --- | --- |
| Date of sale | Time is a predictor by construction; varying it is what generates a different year's prediction |
| House price index (county) | FHFA publishes county-level annual values continuously and well before 2000 — full coverage of 2000–2024 |
| % protection within 5 km | PAD-US and NCED record establishment dates, so protection-as-of-year *t* is reconstructable rather than merely snapshottable. Nolte already computed this variable "in 2010", so the machinery exists |
| Distance to paved roads | TIGER/Line has annual editions, though comparability across the earlier years needs checking |

### 6.3 Time-varying but **not** available annually — the real constraints

| Variable(s) | The problem |
| --- | --- |
| Building density, % building area, % footprints within 500 m and 5 km (**4 variables**) | Microsoft's footprint layer is a **single 2018 snapshot**. There is no 2000, 2005 or 2010 national building-footprint layer to fall back on. This is the most damaging gap: new construction is precisely the mechanism by which land value changes over 25 years, and it is exactly the thing that cannot be back-cast |
| All eight land-cover variables | NLCD is periodic, not annual. Its epochs (2001, 2006, 2011, 2016, 2019, 2021) do at least straddle the target window, so land cover can be stepped between epochs — measured at intervals, interpolated between them, and the interpolation stated as such |
| Median household income | ACS 5-year estimates run annually from the 2005–2009 release onward. Before that there is only the 2000 decennial census, leaving **2001–2004 without an annual source** |
| Both irrigation variables | LANID-US ends at **2017**. Years 2018–2024 are unavailable |
| Median home value (Realtor.com) | Listing data begins **July 2016**. Gold et al. themselves reach back to 2000 only by rebasing with the HPI — that is an extrapolation of the level, not a measurement |

### 6.4 Not available as a historical series at all

| Item | Why |
| --- | --- |
| **Training sales (ZTRAX)** | The known blocker, documented in `docs/data_request_log.md`. The ICPSR release ends at 2020, so 2021–2024 has no training data under any access outcome |
| **Parcel boundaries** | The deeper and less obvious blocker. Every parcel-level variable is computed on a parcel fabric observed "mostly between 2016 and 2019". Historical parcel geometry — the subdivisions, splits and consolidations of the intervening 20 years — is not published for the United States at national scale. A parcel that was one 200-hectare farm in 2000 and is forty house lots by 2018 exists in the data only in its 2018 form |

The parcel-geometry point changes how the series should be *described*, not just
how it is built. An annual series produced this way estimates **what a fixed
2016–2019 parcel fabric would have been worth in year *t***, not the value of
the parcels that actually existed in year *t*. That distinction should be stated
in any output, because it is invisible in the resulting raster.

### 6.5 What this implies for the extension

The realistic construction is not "re-measure all 44 predictors annually". It is:

1. Hold the ~30 time-invariant predictors fixed (§6.1) — defensible, and states
   plainly what is assumed.
2. Vary the four predictors in §6.2, of which **county HPI is the load-bearing
   one**. Gold et al. give direct evidence for this: their Fig 7 shows that
   adding the annual county HPI to an otherwise unchanged predictor set
   "reduces the magnitude of the error, particularly the over-prediction in the
   early years of the sample and the under-prediction in its later years". The
   HPI is the mechanism that carries time through the model.
3. Step land cover between NLCD epochs and hold building footprints at their
   single vintage, declaring both.
4. Accept the span limits: **2000–2020** at best, set by ZTRAX; **2000–2017** if
   the irrigation variables are kept. The requested 2000–2024 is not attainable
   from any of these sources as currently published.

Point 4 is the one to raise before any modelling work starts, since it caps the
deliverable regardless of how the ICPSR request resolves.

## 7. Open items

- The normals period behind the PRISM variables (1981–2010 vs 1991–2020) is not
  stated by Gold et al. and would need to be confirmed with the authors or from
  the released code at `https://github.com/binders1/fmv`.
- The census/ACS table and survey year behind Nolte's median household income is
  not recoverable from either paper.
- The 50 m / 50 km coastal-radius contradiction (§4.1) is unresolved in the
  published material.
- Neither paper states a native resolution for most of its raster inputs; §5 is
  external and unverified.
