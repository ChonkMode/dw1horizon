#!/usr/bin/env python3
"""Spaces in Japanese dialogue: the ones that break a word ("あ るよ") are errors.

  python3 tools/dws/text/jaspace.py [ja] [--write] [--show N]

Japanese does not space its words, so a space between two of its letters shows as a gap in the middle of a word. They
came in with machine rewrites that joined the rows of a page with a space and wrapped the text again letter by letter
(textbank.fit did the same at build time until it learnt join_rows). The rule, for every row of text/ja/dialogue/*.json
and the other Japanese dialogue banks:

  stray (removed):
    - a space between two kana or kanji (ー included): "あ るよ", "青リン ゴ", "問題 ありません";
    - a space after a Latin letter or digit before a kana or kanji: "HPとMP が", "2 倍";
    - a space before 、。！？ and a space after 、;
  kept:
    - a space after 。！？ (the text's sentence spacing, as the original's full-width space after ！？) and around "...";
    - a space between Latin words, numbers and references ({partner}), before a Latin word or number ("グレード D",
      "トレーニング x5") and after a speaker's name row;
    - a space in front of a sign's direction (東: 西: 南: 北:), which separates the sign's destinations;
    - every space of a laid-out box, whose spaces separate fields: the boxes of MAPHEAD tables and the cup notices
      (profiles.UNPACKED_KEYS: "8名 参加自由", "はい いいえ") and the boxes the story sizes itself (set_textbox_size:
      the fishing and digging instructions, Shell News), and of a few names kept spaced on purpose (KEPT).
names.json (the executable's menus) is laid out with spaces and is not touched.
Without --write it prints how many rows change and --show N of them. The text audit (tools/localize/check.py) and the
text bank (textbank.load_source) report a stray space as an error."""
import argparse, functools, glob, json, os, pathlib, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
from dws.text.profiles import packed_key      # noqa: E402

J = '぀-ヿ㐀-鿿'                           # kana (ー and ・ included) and kanji
SP = '[ 　]+'
STRAY = re.compile(rf'(?<=[{J}]){SP}(?=[{J}])|(?<=[A-Za-z0-9]){SP}(?=[{J}])|{SP}(?=[、。！？])|(?<=、){SP}')
SIGN = re.compile('[東西南北]:')                             # a space before a sign's next direction
KEPT = ('かみなりと かぜカップ',)                             # the cup's name in kana, spaced as two words


@functools.lru_cache(None)
def sized_keys(root=ROOT):
    """The keys the story shows in a box it sizes itself (set_textbox_size, then show_textbox(text("key")))."""
    pattern = re.compile(r'set_textbox_size\([^,]+,\s*\d+,\s*\d+\);\s*show_textbox\(text\("([^"]+)"\)\)')
    return frozenset(k for p in pathlib.Path(root, 'story/base').rglob('*.dws') for k in pattern.findall(p.read_text()))


def laid_out(key):
    """A key whose spaces separate fields: none of them is stray."""
    key = re.sub(r'^s000\.sec(\d+)\.', r'm\1.', key)          # s000.sec1238.u15: MAPHEAD's m1238.u15 in script 0
    return not packed_key(key) or key in sized_keys()


def stray_spaces(key, row):
    """The stray spaces of a Japanese row -> [match]: none for a row without Japanese or a laid-out key."""
    if laid_out(key) or not re.search(f'[{J}]', row):
        return []
    kept = [(m.start(), m.end()) for k in KEPT for m in re.finditer(re.escape(k), row)]
    return [m for m in STRAY.finditer(re.sub(r'\{[^}]*\}', lambda e: '\x00' * len(e.group()), row))
            if not SIGN.match(row, m.end()) and not any(a <= m.start() < b for a, b in kept)]


def clean(key, row):
    for m in reversed(stray_spaces(key, row)):
        row = row[:m.start()] + row[m.end():]
    return row


def problems(key, value):
    """['stray space in "...": ...'] for a value (a string, rows or pages)."""
    rows = [value] if isinstance(value, str) else [r for x in value for r in ([x] if isinstance(x, str) else x)]
    return [f'stray space in the middle of Japanese text: "{r[max(0, m.start() - 6):m.end() + 6]}"'
            for r in rows for m in stray_spaces(key, r)]


def banks(root=ROOT):
    """The Japanese dialogue banks: text/ja/dialogue/*.json, text/ja.json and the mods' text/ja.json."""
    return sorted(glob.glob(os.path.join(root, 'text', 'ja', 'dialogue', '*.json'))) + \
        [p for p in [os.path.join(root, 'text', 'ja.json')] if os.path.exists(p)] + \
        sorted(glob.glob(os.path.join(root, 'story', 'mods', '*', 'text', 'ja.json')))


def main(argv):
    from dws.text.repage import dump
    ap = argparse.ArgumentParser()
    ap.add_argument('--write', action='store_true')
    ap.add_argument('--show', type=int, default=0)
    a = ap.parse_args(argv)
    rows = keys = shown = 0
    for f in banks():
        raw = open(f, encoding='utf-8').read()
        d = json.loads(raw)
        style = next((st for st in ('compact', 'indent') if dump(d, st).rstrip('\n') == raw.rstrip('\n')), None)
        dirty = False
        for k, v in d.items():
            if k.startswith('_') or not isinstance(v, (str, list)): continue
            fix = (lambda r: clean(k, r))
            new = fix(v) if isinstance(v, str) else [fix(x) if isinstance(x, str) else [fix(r) for r in x] for x in v]
            if new == v: continue
            keys += 1
            flat = lambda x: [x] if isinstance(x, str) else [r for y in x for r in flat(y)]
            for x, y in zip(flat(v), flat(new)):
                if x != y:
                    rows += 1
                    if shown < a.show:
                        shown += 1; print(f'{os.path.relpath(f, ROOT)} {k}:\n  was {x}\n  now {y}')
            d[k] = new; dirty = True
        if dirty and a.write:
            if style is None:
                print(f'{os.path.relpath(f, ROOT)}: an unknown layout, left as it is'); continue
            open(f, 'w', encoding='utf-8').write(dump(d, style).rstrip('\n') + raw[len(raw.rstrip('\n')):])
    print(f'{rows} rows of {keys} entries have stray spaces' + (', removed' if a.write else ' (dry run)'))


if __name__ == '__main__':
    main(sys.argv[1:])
