# landvalue

Analysis of high-resolution US land value data from Nolte (2020), *High-resolution
land value maps reveal underestimation of conservation costs in the United States*,
PNAS. The underlying rasters estimate the fair market value of private land across
the contiguous United States, modelled from roughly 6 million land sales.

## Documentation

| Document | What it covers |
| --- | --- |
| [`docs/project_report.md`](docs/project_report.md) | Full written report: objective, what the raster contains, how the render pipeline works, how the colour scale was recovered, the federal-only "Public Land" finding, validation results, and known limitations |
| [`docs/validation_report.md`](docs/validation_report.md) | Whether the PLACES estimates outperform the competing proxies: ranking, the county-mean collapse, aggregate vs parcel-level accuracy, and the circularity question |
| [`docs/predictor_inventory.md`](docs/predictor_inventory.md) | Every predictor variable in both models, with source dataset, vintage, resolution and update cadence — and which of them can be re-measured annually |
| [`docs/data_request_log.md`](docs/data_request_log.md) | Record of the ZTRAX / ICPSR data access effort that blocks the 2000–2024 extension |

Current state: Figure 1 is reproduced and validated against the published
image. The planned extension to an annual series is blocked on data access —
see the request log.

## Repository contents

Only code and documentation are tracked in Git. **The data is not in this
repository and never will be** — the rasters are far too large (GitHub rejects
any file over 100 MB). Generated figures are not tracked either, since they can
be reproduced by re-running the code.

## Getting set up

### 1. Clone the repository

```bash
git clone https://github.com/Shauryah24526/landvalue.git
cd landvalue
```

This is a **private** repository — you must be signed in as an invited
collaborator for the clone to work.

### 2. Create the folder structure

Git does not track empty folders, so the data folders will not appear when you
clone. Create them yourself before downloading anything:

```bash
# macOS / Linux
mkdir -p data/raw data/processed

# Windows PowerShell
New-Item -ItemType Directory -Force data/raw, data/processed
```

The full layout you should end up with:

```
landvalue/
├── data/                 <- git-ignored, you create this locally
│   ├── raw/              <- Dryad downloads go here, unmodified
│   │   ├── places_fmv_all.tif
│   │   ├── places_fmv_vacant.tif
│   │   ├── validation_goco.csv
│   │   └── validation_public_acquisitions.csv
│   ├── refs/             <- reference papers (PDFs), read but not redistributed
│   └── processed/        <- intermediate files the code generates
├── figures/              <- .png outputs are git-ignored
├── src/                  <- analysis code (tracked in git)
├── .gitignore
└── README.md
```

Treat `data/raw/` as read-only: never edit those files in place. Anything the
code derives from them belongs in `data/processed/` so that a fresh download
always reproduces the same starting point.

### 3. Download the data

The dataset is archived on Dryad:

**DOI: [10.5061/dryad.np5hqbzq9](https://doi.org/10.5061/dryad.np5hqbzq9)**
Direct link: https://datadryad.org/dataset/doi:10.5061/dryad.np5hqbzq9

Citation:

> Nolte, Christoph (2020). *Data for: High-resolution land value maps reveal
> underestimation of conservation costs in the United States.* Dryad Digital
> Repository. https://doi.org/10.5061/dryad.np5hqbzq9

Associated paper: https://doi.org/10.1073/pnas.2012865117

Files to download into `data/raw/`:

| File | What it is |
| --- | --- |
| `places_fmv_all.tif` | Estimated 2010 land values, modelled from vacant **and** non-vacant property sales |
| `places_fmv_vacant.tif` | Estimated land values from vacant property sales only |
| `validation_goco.csv` | Conservation easement prices vs. estimated land values |
| `validation_public_acquisitions.csv` | Public acquisition prices vs. several cost proxies |

The GeoTIFFs are ~125 MB each, so allow time and disk space for the download.
Both collaborators must download them independently; they are deliberately
never shared through Git.

**The Dryad download is a zip inside a zip.** `doi_10_5061_dryad_np5hqbzq9…zip`
contains `places_fmv_pnas_dryad.zip`, and the files above live inside *that*,
under `1 estimates/` and `2 validation/`. Extract the four files flat into
`data/raw/` — `validate.py` expects `data/raw/validation_goco.csv` and
`data/raw/validation_public_acquisitions.csv`, without the folder prefix. The
inner zip also holds a `3 replication/` folder (a 160 MB `johnson_replication.csv`
and `lawler_replication.csv`) which nothing in this repository uses yet.

### 3b. Overlay layers (needed by `render_fig1.py`)

Figure 1 paints public land and tribal land as flat fills on top of the
raster. Those boundaries are **not** part of the Dryad deposit — they come
from the project archive `FMV.zip`, under `FMV/Data/`:

| File | What it is | Used as |
| --- | --- | --- |
| `PADUS2_1VectorAnalysisFile_ClipCensus.gdb/` | PADUS 2.1, 761,302 protected-area polygons, all ownership classes | **Public Land** (filtered to `Mang_Type = 'FED'`) |
| `bia_aian_lar_5070.geojson` | BIA American Indian / Alaska Native Land Area Representations, 333 reservations | **Native American** |
| `padus_tribal_5070.geojson` | PADUS polygons where `Mang_Type = TRIB` (includes Alaska) | not used — see below |
| `padus_private_5070.geojson` | PADUS polygons where `Mang_Type = PVT`, only 12,294 km² | not used — see below |

Three traps worth knowing:

- **`padus_private` is not public land.** It is the ~0.2% of protected areas
  under *private* management (land trusts, NGO preserves). It cannot be the
  "Public Land" layer, which covers roughly 22% of the map.
- **There are two candidate tribal layers.** `bia_aian_lar_5070` (303,872 km²,
  bounded to the lower 48) matches the published figure's tan coverage closely;
  `padus_tribal_5070` (411,654 km²) extends into Alaska. The BIA layer is the
  one used here.
- **"Public Land" means federal land only, not all publicly managed land.**
  Federal PADUS polygons cover 22.6% of the mapped area, matching the published
  blue exactly; adding state, local and district land pushes it to 28.4%. In the
  published figure, state land drawn well clear of any federal parcel is only
  23.0% blue — indistinguishable from the 22.5% baseline across all mapped land,
  and nothing like the 63.1% measured inside federal parcels. State and local
  land is priced by the model, not masked.

PADUS is independently available from USGS if `FMV.zip` is ever unavailable:
https://www.usgs.gov/programs/gap-analysis-project/science/pad-us-data-download

### 3c. State boundaries

The published figure draws state borders and a national coastline. That layer
is in neither the Dryad deposit nor `FMV.zip`, so download it from the US
Census Bureau into `data/raw/` and unzip it there:

https://www2.census.gov/geo/tiger/GENZ2018/shp/cb_2018_us_state_500k.zip

`render_fig1.py` expects it at
`data/raw/cb_2018_us_state_500k/cb_2018_us_state_500k.shp` and drops the seven
non-contiguous FIPS codes (AK, HI, AS, GU, MP, PR, VI) itself.

All of these are covered by the `data/` rule in `.gitignore`.

### 4. Set up a Python environment

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

The `.venv/` folder is git-ignored. With it activated, install the pinned
dependencies:

```bash
pip install -r requirements.txt
```

Built and tested against Python 3.12. If you add a new package, re-run
`pip freeze > requirements.txt` and commit the result so the other person
stays in sync.

### 5. Check that it worked

```bash
python src/inspect_raster.py
```

This opens both rasters and prints their CRS, dimensions, dtype, nodata value,
bounds and pixel size. If it prints metadata without error, your environment
and data are both correct. Pass a path to inspect any other raster.

To reproduce the figures and the proxy validation:

```bash
python src/render_fig1.py --scale 1    # Figure 1, full resolution
python src/validate.py                 # Figure 2 tables and scatter grid
python src/validate.py --no-figure     # tables only
```

`validate.py` needs only the two validation CSVs, not the rasters or PADUS.

Expected output for both files: EPSG:5070 (NAD83 / Conus Albers), 9618 x 6054
px, float32, nodata `0.0`, 480 m pixels.

Two quirks worth knowing:

- **NoData is `0.0`**, not a sentinel value, so a genuine land value of zero is
  indistinguishable from missing data. Read with `src.read(1, masked=True)` and
  let rasterio's mask handle it rather than filtering on `== 0` yourself.
- **The GeoTIFFs are striped, not tiled** (one full row per block) and carry no
  overviews. Reading row ranges is fast; many small windowed reads are slow.
  If that becomes a bottleneck, write a tiled copy into `data/processed/`.

## First-time Git setup

Git stamps an author name and email into every commit, so each person
configures their own once per machine before committing:

```bash
git config --global user.name "madhu"
git config --global user.email "your@email.address"
```

This is how the history shows who did what — commits from this project's two
authors appear as `shauryah` and `madhu`.

## Working together

- Pull before you start work (`git pull`) and commit in small, focused steps.
- If you both edit the same file at once, Git will ask you to resolve a
  conflict — coordinate on who owns which files to keep this rare.
- Never use `git add -A` blindly without checking `git status` first. The
  `.gitignore` protects you, but it is worth confirming no large file has
  slipped in before you commit.
