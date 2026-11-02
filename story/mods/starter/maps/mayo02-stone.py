#!/usr/bin/env python3
"""Kunemon's Bed (MAYO02, screen 1): the round stone at the west of the clearing becomes step trigger 1.

Nothing is painted and nothing of the disc is committed: the recipe reads the player's own map at build time and
changes only the collision of a few tiles, so the background stays as it is. The map already has step trigger 0, so the
next one is 1. The story (src/kunemons_bed.py) answers it with @bed.on_step(1).

    python3 story/mods/starter/maps/mayo02-stone.py OUT_DIR        writes OUT_DIR/MAYO02.MAP (it replaces the disc's)
"""
import glob, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import dwmap  # noqa: E402
from maps import reach  # noqa: E402

STEP = 1                                                # a tile value of 51 + N is step trigger N
STONE_TILES = [(tx, tz) for tz in (42, 43) for tx in (31, 32, 33)]      # free tiles on the stone, three rows from the arrival


def tile_centre(tx, tz):
    """World x, z of a tile's centre: the map is 100 by 100 tiles of 100 units."""
    return (tx - 50) * 100 + 50, (49 - tz) * 100 + 50


def main(out):
    found = glob.glob(os.path.join(ROOT, 'extracted', 'MAP', '*', 'MAYO02.MAP'))
    if not found: sys.exit('MAYO02.MAP is not in extracted/MAP (extract the disc first: tools/extract.sh)')
    m = dwmap.MapFile(open(found[0], 'rb').read())
    col = list(m.collision)
    if 51 + STEP in col: sys.exit(f'the map already has step trigger {STEP}: pick a number it does not use')
    for tx, tz in STONE_TILES:
        if col[tz * 100 + tx] != 0: sys.exit(f'tile ({tx}, {tz}) is not free ground: only plain floor becomes a trigger')
        col[tz * 100 + tx] = 51 + STEP
    m.collision = col

    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'MAYO02.MAP'), 'wb').write(m.build())

    reach.check_recipe_arrivals(m, 'MAYO02')            # every arrival still stands on free ground
    walkable = reach.from_spawn_coordinates(m)          # the tamer's body box, from every arrival
    if not any(tile_centre(tx, tz) in walkable for tx, tz in STONE_TILES): sys.exit('the stone is not reachable')
    print(f'MAYO02: {len(STONE_TILES)} tiles of step trigger {STEP}, reachable floor {len(walkable)}')


if __name__ == '__main__':
    if len(sys.argv) != 2: sys.exit(__doc__)
    main(sys.argv[1])
