#!/usr/bin/env python3
"""How far each species has been checked, so a count of species never reads as a claim that all of them were played.

  tools/species_status.py report                     how many species stand at each level, and which were checked
  tools/species_status.py record OUTDIR COMMIT       adds the species a species_proof.py run passed, on that commit
  tools/species_status.py review ID [ID ...]         a person watched them in the game

The levels, lowest first:
  native / imported   in the game (id < 180: from the original; 180 and up: taken from another game), nothing checked
  smoke-tested        species_proof.py passed: it evolved, fought, played its techniques and finisher, ate, showed its status
  reviewed            a person also watched its models and animations in the game

A proof belongs to the commit it ran on: a later change to a species does not clear it by itself.
"""
import argparse, glob, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLE = os.path.join(ROOT, 'docs/data/species-proof.json')


def species_ids():
    return sorted(int(os.path.basename(p).split('-')[0]) for p in glob.glob(os.path.join(ROOT, 'content/species/[0-9]*.json')))


def load(path=TABLE):
    with open(path) as stream:
        return json.load(stream)


def save(table, path=TABLE):
    with open(path, 'w') as stream:
        json.dump(table, stream, indent=1, sort_keys=True)
        stream.write('\n')


def level(table, species):
    entry = table['species'].get(str(species), {})
    if entry.get('reviewed'): return 'reviewed'
    if entry.get('proof'): return 'smoke-tested'
    return 'imported' if species >= 180 else 'native'


def record(table, results, commit):
    """Passing species gain the commit; a failing one loses its old proof, because that proof is no longer true."""
    for key, result in results.items():
        entry = table['species'].setdefault(str(key), {})
        if result.get('ok'):
            entry['proof'] = commit
        else:
            entry.pop('proof', None)
            if not entry: del table['species'][str(key)]


def counts(table, ids):
    out = {name: 0 for name in ('native', 'imported', 'smoke-tested', 'reviewed')}
    for species in ids: out[level(table, species)] += 1
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    sub.add_parser('report')
    r = sub.add_parser('record'); r.add_argument('out'); r.add_argument('commit')
    v = sub.add_parser('review'); v.add_argument('ids', nargs='+', type=int)
    a = ap.parse_args()
    table = load()
    if a.cmd == 'record':
        with open(os.path.join(a.out, 'result.json')) as stream:
            record(table, json.load(stream), a.commit)
        save(table)
    elif a.cmd == 'review':
        for species in a.ids:
            if level(table, species) not in ('smoke-tested', 'reviewed'):
                sys.exit(f'{species}: pass species_proof.py first')
            table['species'][str(species)]['reviewed'] = True
        save(table)
    ids = species_ids()
    for name, count in counts(table, ids).items():
        print(f'{name:13} {count}')


if __name__ == '__main__':
    main()
