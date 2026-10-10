"""Recreate Figure 1 of Nolte (2020): US fair market value of private land.

The raster stores the NATURAL LOG of USD per hectare, so values are
exponentiated back into dollars before plotting on a log colour scale.
Federal land and tribal land are painted as flat fills on top, state
boundaries and the national coastline are drawn over that, and the
colourbar and legend are laid out to match the published figure.

Usage:
    python src/render_fig1.py                  # 1/4 resolution draft
    python src/render_fig1.py --scale 1        # full resolution
    python src/render_fig1.py --no-overlays    # raster only
    python src/render_fig1.py --no-furniture   # no colourbar, legend, borders
"""

import argparse
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # render to file, never try to open a GUI window

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from affine import Affine
from matplotlib.cm import ScalarMappable
from matplotlib.colors import LinearSegmentedColormap, LogNorm, to_rgb
from matplotlib.patches import Rectangle
from rasterio.enums import Resampling
from rasterio.features import rasterize
from rasterio.transform import array_bounds

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RASTER = RAW / "places_fmv_all.tif"
OUTPUT = ROOT / "figures" / "fig1_recreation.png"

PADUS_GDB = RAW / "PADUS2_1VectorAnalysisFile_ClipCensus.gdb"
PADUS_LAYER = "PADUS2_1Fee_Designation_Easement_DOD_Trbl_FlatVectorSingPart_ClipCensus"
# "Public Land" in the published legend means FEDERALLY managed land only.
# Measured against the published figure: federal land alone covers 22.6% of the
# mapped area, exactly matching the published blue. Adding STAT/LOC/DIST pushes
# it to 28.4%. State land drawn well clear of any federal parcel is only 23.0%
# blue in the published figure -- indistinguishable from the 22.5% baseline for
# all mapped land, and nothing like the 63.1% seen inside federal parcels.
# So state, local and district land is priced, not masked.
PUBLIC_TYPES = ("FED",)
TRIBAL_FILE = RAW / "bia_aian_lar_5070.geojson"
STATES_FILE = RAW / "cb_2018_us_state_500k" / "cb_2018_us_state_500k.shp"
# FIPS codes outside the contiguous US: AK, HI, AS, GU, MP, PR, VI
NON_CONUS_FIPS = ("02", "15", "60", "66", "69", "72", "78")

# Colour scale bounds, in USD per hectare, read off the published colourbar.
VMIN, VMAX = 1_000, 1_000_000
CBAR_TICKS = [1e3, 2e3, 5e3, 1e4, 2e4, 5e4, 1e5, 2e5, 5e5, 1e6]

# Fill colours sampled from the published figure (modal pixel value).
PUBLIC_FILL = "#8ec0fe"
TRIBAL_FILL = "#e4aa75"
BORDER_COLOR = "#7a7a7a"
COAST_COLOR = "#1a1a1a"
TEXT_COLOR = "#1a1a1a"

# Ramp sampled directly from the published figure's colourbar, between the
# $1K and $1M ticks (confirmed log-spaced: R^2 = 0.9999991, max residual
# 0.44 px over 908 px). Low -> high.
COLORS = [
    "#003908", "#013d09", "#004005", "#044306", "#064607", "#004704",
    "#004b01", "#024e01", "#065001", "#005b00", "#006400", "#006e00",
    "#007700", "#008000", "#0e8c01", "#009400", "#089f00", "#28a803",
    "#49b004", "#67b804", "#86c004", "#9ac700", "#a5cc01", "#aed002",
    "#b8d406", "#c0db00", "#c9df04", "#d4e500", "#ddea00", "#e7ee02",
    "#f1f300", "#fbf908", "#fff300", "#ffe601", "#ffd906", "#fece04",
    "#ffc008", "#feb209", "#ffa60b", "#ff990a", "#ff8910", "#fc7608",
    "#fb6309", "#f75009", "#f73d06", "#f32803", "#f11600", "#f00400",
    "#ea0000", "#e40000", "#de0000", "#da0000", "#d50001", "#ce0001",
    "#c90002", "#c40001", "#aa0001", "#910001", "#7b0001", "#610001",
    "#450000", "#2f0000", "#150000", "#000000",
]

# --- layout, as fractions of the figure, measured off the published figure ---
# The published image is 4164 x 2500 px with the map occupying 3924 x 2470 px
# at offset (28, 14), leaving a narrow legend column on the right.
FIG_W_MULT = 4164 / 3924          # figure width  / map width
FIG_H_MULT = 2500 / 2470          # figure height / map height
MAP_RECT = (28 / 4164, 1 - 2484 / 2500, 3924 / 4164, 2470 / 2500)
# Colourbar rect spans the arrowheads too; matplotlib's extend triangles take
# ~5% of the axes at each end, which is what the published bar uses (47/908).
CBAR_RECT = (4095 / 4164, 1 - 2083 / 2500, 62 / 4164, (2083 - 1081) / 2500)
CBAR_TITLE_XY = (3990 / 4164, 1 - 971 / 2500)
SWATCH_X, SWATCH_W, SWATCH_H = 4066 / 4164, 63 / 4164, 52 / 2500
SWATCH_YS = {"Public Land": 1 - 2267 / 2500, "Native American": 1 - 2372 / 2500}
FONT_FRAC = 0.026                 # em height as a fraction of figure height
LINE_FRAC = 2 / 2500              # hairline width as a fraction of figure height


def load(path, scale):
    """Read the raster at 1/scale resolution. Returns (USD/ha, transform, crs)."""
    with rasterio.open(path) as src:
        height = max(1, src.height // scale)
        width = max(1, src.width // scale)

        # masked=True builds a mask from the file's nodata value (0.0 here).
        # Nearest-neighbour resampling returns real source values, so nodata
        # cells stay exactly 0 and remain maskable -- averaging would blend
        # them into neighbours and invent data along every coastline.
        log_usd = src.read(1, out_shape=(height, width),
                           resampling=Resampling.nearest, masked=True)
        log_usd = np.ma.masked_equal(log_usd, 0)  # in case the tag is missing

        transform = src.transform * Affine.scale(src.width / width,
                                                 src.height / height)
        crs = src.crs

    print(f"  read      : {width} x {height} px  (1/{scale} resolution)")
    print(f"  valid     : {log_usd.count():,} px "
          f"({100 * log_usd.count() / log_usd.size:.1f}% of grid)")

    usd = np.ma.exp(log_usd)
    v = usd.compressed()
    if v.size:
        print(f"  USD/ha    : min ${v.min():,.0f}  median ${np.median(v):,.0f}  "
              f"max ${v.max():,.0f}")
    return usd, transform, crs


def burn(gdf, shape, transform):
    """Rasterise polygons to a boolean mask on the raster grid."""
    if gdf.empty:
        return np.zeros(shape, bool)
    # all_touched=False: a cell is filled only if its CENTRE falls inside a
    # polygon. With all_touched=True every sub-pixel parcel would claim a whole
    # cell, over-painting the map and speckling the entire eastern half.
    return rasterize(
        ((geom, 1) for geom in gdf.geometry),
        out_shape=shape, transform=transform,
        fill=0, dtype="uint8", all_touched=False,
    ).astype(bool)


def load_overlays(shape, transform, crs):
    """Rasterise federal-land and tribal-land polygons onto the raster grid."""
    import geopandas as gpd  # imported lazily; only needed with overlays

    quoted = ",".join(f"'{t}'" for t in PUBLIC_TYPES)
    print(f"  public    : reading PADUS where Mang_Type IN ({quoted})")
    pub = gpd.read_file(PADUS_GDB, layer=PADUS_LAYER, columns=["Mang_Type"],
                        where=f"Mang_Type IN ({quoted})")
    print(f"              {len(pub):,} polygons, {pub.geometry.area.sum()/1e6:,.0f} km2")
    if pub.crs is not None and crs is not None and pub.crs != crs:
        pub = pub.to_crs(crs)

    print(f"  tribal    : reading {TRIBAL_FILE.name}")
    trib = gpd.read_file(TRIBAL_FILE)
    print(f"              {len(trib):,} polygons, {trib.geometry.area.sum()/1e6:,.0f} km2")
    if trib.crs is not None and crs is not None and trib.crs != crs:
        trib = trib.to_crs(crs)

    pub_mask = burn(pub, shape, transform)
    trib_mask = burn(trib, shape, transform)
    n = shape[0] * shape[1]
    print(f"  burned    : public {pub_mask.sum()/n*100:.1f}% of grid, "
          f"tribal {trib_mask.sum()/n*100:.1f}% of grid")
    return pub_mask, trib_mask


def load_states(crs):
    """Contiguous-US state polygons, reprojected onto the raster's CRS."""
    import geopandas as gpd

    print(f"  states    : reading {STATES_FILE.name}")
    gdf = gpd.read_file(STATES_FILE, columns=["STATEFP"])
    gdf = gdf[~gdf["STATEFP"].isin(NON_CONUS_FIPS)]
    if gdf.crs is not None and crs is not None and gdf.crs != crs:
        gdf = gdf.to_crs(crs)
    print(f"              {len(gdf)} states")
    return gdf


def _national_outline(states):
    """Merge the states into one shape so only the coastline survives."""
    try:
        return states.geometry.union_all()
    except AttributeError:            # geopandas < 1.0
        return states.geometry.unary_union


def _fmt_dollars(v, _pos=None):
    return f"{v / 1e6:g} M" if v >= 1e6 else f"{v / 1e3:g} K"


def _add_furniture(fig, cmap, font, hairline):
    """Colourbar with arrowheads, USD/ha title, and the two legend swatches."""
    cax = fig.add_axes(CBAR_RECT)
    sm = ScalarMappable(norm=LogNorm(vmin=VMIN, vmax=VMAX), cmap=cmap)
    sm.set_array([])
    cbar = fig.colorbar(sm, cax=cax, extend="both")
    cbar.outline.set_visible(False)
    cbar.set_ticks(CBAR_TICKS)
    cbar.set_ticklabels([_fmt_dollars(t) for t in CBAR_TICKS])
    cax.minorticks_off()
    cax.yaxis.set_ticks_position("left")
    cax.tick_params(labelsize=font, length=font * 0.35, width=hairline,
                    colors=TEXT_COLOR, pad=font * 0.3)

    fig.text(*CBAR_TITLE_XY, "USD / ha", ha="center", va="center",
             fontsize=font, color=TEXT_COLOR)

    for label, fill in (("Public Land", PUBLIC_FILL),
                        ("Native American", TRIBAL_FILL)):
        y = SWATCH_YS[label]
        fig.add_artist(Rectangle((SWATCH_X, y), SWATCH_W, SWATCH_H,
                                 transform=fig.transFigure, facecolor=fill,
                                 edgecolor="none"))
        fig.text(SWATCH_X - 0.006, y + SWATCH_H / 2, label, ha="right",
                 va="center", fontsize=font, color=TEXT_COLOR)


def render(usd, transform, output, pub_mask=None, trib_mask=None, states=None,
           dpi=300, furniture=True):
    cmap = LinearSegmentedColormap.from_list("nolte_fmv", COLORS, N=256)
    cmap.set_bad(color="white")

    sm = ScalarMappable(norm=LogNorm(vmin=VMIN, vmax=VMAX), cmap=cmap)
    rgb = sm.to_rgba(usd)[..., :3]

    # Flat fills painted over the raster; tribal drawn last, as published.
    if pub_mask is not None:
        rgb[pub_mask] = to_rgb(PUBLIC_FILL)
    if trib_mask is not None:
        rgb[trib_mask] = to_rgb(TRIBAL_FILL)

    height, width = usd.shape
    if furniture:
        fig_w, fig_h = width * FIG_W_MULT / dpi, height * FIG_H_MULT / dpi
        rect = MAP_RECT
    else:
        fig_w, fig_h = width / dpi, height / dpi
        rect = (0, 0, 1, 1)

    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    fig.patch.set_facecolor("white")
    ax = fig.add_axes(rect)
    ax.set_facecolor("white")
    ax.set_axis_off()

    # Draw in the raster's own coordinates so the vector layers line up.
    left, bottom, right, top = array_bounds(height, width, transform)
    ax.imshow(rgb, extent=(left, right, bottom, top), interpolation="nearest",
              aspect="equal")

    font = FONT_FRAC * fig_h * 72          # points
    hairline = LINE_FRAC * fig_h * 72

    if states is not None:
        states.boundary.plot(ax=ax, color=BORDER_COLOR, linewidth=hairline)
        import geopandas as gpd
        gpd.GeoSeries([_national_outline(states)], crs=states.crs).boundary.plot(
            ax=ax, color=COAST_COLOR, linewidth=hairline)

    ax.set_xlim(left, right)
    ax.set_ylim(bottom, top)

    if furniture:
        _add_furniture(fig, cmap, font, hairline)

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=dpi, facecolor="white")
    plt.close(fig)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--scale", type=int, default=4,
                   help="read 1/SCALE of full resolution (default 4)")
    p.add_argument("--raster", type=Path, default=RASTER)
    p.add_argument("--output", type=Path, default=OUTPUT)
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--no-overlays", action="store_true",
                   help="skip the federal-land and tribal-land fills")
    p.add_argument("--no-furniture", action="store_true",
                   help="skip the colourbar, legend and boundary lines")
    args = p.parse_args(argv)

    if args.scale < 1:
        p.error("--scale must be 1 or greater")
    if not args.raster.exists():
        print(f"ERROR: raster not found: {args.raster}", file=sys.stderr)
        print("Download it from https://doi.org/10.5061/dryad.np5hqbzq9 "
              "into data/raw/ -- see README.md", file=sys.stderr)
        return 1

    print(f"reading {args.raster.name}")
    start = time.perf_counter()
    usd, transform, crs = load(args.raster, args.scale)

    pub_mask = trib_mask = states = None
    if not args.no_overlays:
        missing = [f for f in (PADUS_GDB, TRIBAL_FILE) if not f.exists()]
        if missing:
            print("ERROR: overlay layers missing: "
                  + ", ".join(m.name for m in missing), file=sys.stderr)
            print("Extract them from FMV.zip into data/raw/ -- see README.md",
                  file=sys.stderr)
            return 1
        pub_mask, trib_mask = load_overlays(usd.shape, transform, crs)

    if not args.no_furniture:
        if not STATES_FILE.exists():
            print(f"ERROR: state boundaries missing: {STATES_FILE}",
                  file=sys.stderr)
            print("Download cb_2018_us_state_500k.zip from the US Census "
                  "into data/raw/ -- see README.md", file=sys.stderr)
            return 1
        states = load_states(crs)

    print(f"rendering to {args.output.name} at {args.dpi} dpi")
    render(usd, transform, args.output, pub_mask, trib_mask, states,
           args.dpi, furniture=not args.no_furniture)

    print(f"done in {time.perf_counter() - start:.1f}s  -> {args.output}  "
          f"({args.output.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
