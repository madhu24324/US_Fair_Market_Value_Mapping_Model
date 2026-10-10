"""Print the key metadata of a raster.

Usage:
    python src/inspect_raster.py [path/to/raster.tif ...]

Defaults to the two FMV rasters in data/raw/ if no path is given.
"""

import sys
from pathlib import Path

import rasterio

ROOT = Path(__file__).resolve().parent.parent
DEFAULTS = [
    ROOT / "data" / "raw" / "places_fmv_all.tif",
    ROOT / "data" / "raw" / "places_fmv_vacant.tif",
]


def describe(path):
    with rasterio.open(path) as src:
        left, bottom, right, top = src.bounds
        px_w, px_h = src.res

        print(f"\n{'=' * 70}")
        print(path.name)
        print("=" * 70)
        print(f"  CRS         : {src.crs}")
        if src.crs:
            print(f"                {src.crs.to_string()}  ({src.crs.linear_units})")
        print(f"  size        : {src.width} x {src.height} px  "
              f"({src.width * src.height / 1e6:,.1f} Mpx)")
        print(f"  bands       : {src.count}")
        print(f"  dtype       : {', '.join(src.dtypes)}")
        print(f"  nodata      : {src.nodata}")
        print(f"  pixel size  : {px_w:g} x {px_h:g} {src.crs.linear_units if src.crs else ''}")
        print(f"  bounds      : left   {left:>16,.2f}")
        print(f"                bottom {bottom:>16,.2f}")
        print(f"                right  {right:>16,.2f}")
        print(f"                top    {top:>16,.2f}")
        print(f"  extent      : {(right - left) / 1000:,.1f} x "
              f"{(top - bottom) / 1000:,.1f} km")
        print(f"  driver      : {src.driver}")
        print(f"  tiled       : {src.profile.get('tiled', False)}"
              f"   blocks: {src.block_shapes[0]}")
        print(f"  compression : {src.profile.get('compress', 'none')}")
        print(f"  overviews   : {src.overviews(1) or 'none'}")


def main(argv):
    paths = [Path(a) for a in argv[1:]] or DEFAULTS
    missing = [p for p in paths if not p.exists()]
    if missing:
        for p in missing:
            print(f"ERROR: not found: {p}", file=sys.stderr)
        return 1
    for p in paths:
        describe(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
