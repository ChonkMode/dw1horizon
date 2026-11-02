#!/usr/bin/env python3
"""One whole life of a partner, played the way a player does: the proof that the game's main loop still holds together.

  EMU_PORT=38335 DW_SYMS=EXE tools/dev/playtest/journey.py DISC.cue OUTDIR

A new game from the title on an empty card; food from the menu; a wild fight, played by the game's own AI to the end; the
natural evolution when its hour comes; the save machine in Jijimon's house; the emulator stopped, and a fresh boot with
that card, which must bring back the evolved partner with its stats.

Three things are not played, because they would take days of game time, and they are written to RAM: the warps between
screens, the food put in the bag, and the partner's stats and hours at its level, which win the fight and bring its
evolution forward. No check is written to RAM. Prints JSON, writes OUTDIR/journey.json and screenshots; exit 1 when a step failed.
"""
import json, os, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'tools')]
from tools.dev.playtest import species_proof as P

JIJIMONS_HOUSE, NATIVE_FOREST = 218, 0
SAVE_MACHINE = (-650, -550)              # the first tile of use trigger 5 (`dws slots 218`)
HP = 'PARTNER_ENTITY.digimonEntity.stats.base.hp'
SAVE_DONE = 0x41                         # the last card menu of the save machine


def partner():
    return P.partner_type()


def new_game(cue, out):
    """NEW GAME on empty cards, Jijimon's questions, the names, the movie, until the Tamer has control."""
    emu = P.EMU = P.emulator(cue)
    emu.run('stop', check=False)
    os.makedirs(emu.home, exist_ok=True)
    for card in ('memcard1.mcd', 'memcard2.mcd'):
        if os.path.exists(os.path.join(emu.home, card)): os.remove(os.path.join(emu.home, card))
    emu.run('start', cue)
    emu.wait(30)
    chosen = False
    for _ in range(90):
        ram = emu.ram()
        menu = emu.peek('CURRENT_MENU', 'i', ram)
        if menu == 0 and emu.peek('MAIN_MENU_TICKS', 'i', ram) > 3:
            if emu.peek('MENU_HIGHLIGHTS', 'b', ram): emu.press('UP', 6)
            else: emu.press('CROSS', 6); chosen = True
        elif not chosen: emu.press('START', 6)
        elif menu == -1: break
        else: emu.press('CROSS', 6)
        emu.wait(2)
    stable, last, t0 = 0, None, time.time()
    while time.time() - t0 < 900:       # the opening: every question, name and line takes the first answer
        ram = emu.ram()
        now = (emu.peek('CURRENT_SCREEN', 'h', ram), emu.peek('IS_SCRIPT_PAUSED', 'i', ram), emu.peek('TAMER_STATE', 'b', ram),
               emu.peek('CURRENT_MENU', 'i', ram), emu.peek('MAIN_STATE', 'i', ram))
        if now != last: print('opening', round(time.time() - t0), now, flush=True); last = now
        stable = stable + 1 if now[1] == 1 and now[2] == 0 else 0
        if stable >= 4: break
        if stable == 0: emu.press('CROSS', 4)
        emu.wait(1.5)
        if int(time.time() - t0) % 60 < 3: P.run(P.E + ['shot', f'{out}/opening-{int(time.time() - t0) // 60}.png'])
    P.run(P.E + ['shot', f'{out}/new-game.png'])
    return stable >= 4


def fight(out, r):
    """A wild fight in Native Forest, the game's AI playing, until the results are closed."""
    P.run(P.G + ['trigger', '1', '1'])
    P.mset(*[f'PARTNER_ENTITY.digimonEntity.stats.base.{k}=300' for k in ('off', 'def', 'speed', 'brain')])   # the fight must be won
    arrived = P.EMU.warp(NATIVE_FOREST) or P.EMU.in_control()
    P.run(P.G + ['approach', '0'])
    before = P.mem('PARTNER_PARA.battles').get('PARTNER_PARA.battles')
    for _ in range(6):
        P.press('CONFIRM'); P.EMU.wait(2)
        if P.game_state() == 1: break
    r['fight_started'] = arrived and P.game_state() == 1
    for _ in range(120):
        P.EMU.wait(3)
        state = P.game_state()
        if state == 0: break
        if state != 1: P.press('CONFIRM')
    P.EMU.in_control()
    P.run(P.E + ['shot', f'{out}/after-fight.png'])
    after = P.mem('PARTNER_PARA.battles').get('PARTNER_PARA.battles')
    r['fight_finished'] = P.game_state() == 0
    r['battles'] = [before, after]
    r['fight_counted'] = isinstance(before, int) and isinstance(after, int) and after > before


def evolve(start, out, r):
    """The partner meets its next level's needs and its hours; the game decides when, and into what."""
    P.mset('PARTNER_PARA.evoTimer=96', 'PARTNER_PARA.careMistakes=0', 'PARTNER_PARA.discipline=90',
           'PARTNER_PARA.happiness=90', 'PARTNER_PARA.weight=30', 'PARTNER_PARA.battles=20',
           *[f'PARTNER_ENTITY.digimonEntity.stats.base.{k}={v}' for k, v in
             (('hp', 2000), ('mp', 2000), ('off', 300), ('def', 300), ('speed', 300), ('brain', 300))])
    for _ in range(80):
        P.EMU.wait(3)                    # the game looks when the hour changes: a game hour is a minute
        if partner() != start and P.EMU.peek('TAMER_STATE', 'b') == 0: break
    P.EMU.in_control()
    P.run(P.E + ['shot', f'{out}/evolved.png'])
    r['evolved_into'] = partner()
    r['evolved'] = r['evolved_into'] not in (None, start)


def save(out, r):
    """The save machine: the first use explains it, the next asks, and yes opens the card screens."""
    arrived = P.EMU.warp(JIJIMONS_HOUSE) or P.EMU.in_control()
    seen = []
    for _ in range(4):
        P.EMU.in_control()
        P.run(P.G + ['move', str(SAVE_MACHINE[0]), str(SAVE_MACHINE[1])])
        P.EMU.wait(1)
        for _ in range(30):
            P.press("CONFIRM"); P.EMU.wait(1.5)
            menu = P.EMU.peek('CURRENT_MENU', 'i')
            if menu not in seen[-1:]: seen.append(menu)
            if menu == -1 and (SAVE_DONE in seen or len(seen) > 1 and P.EMU.peek('TAMER_STATE', 'b') == 0): break
        if SAVE_DONE in seen: break
    r['save_menus'] = seen
    r['saved'] = bool(arrived and SAVE_DONE in seen and seen[-1] == -1)
    P.EMU.wait(3)
    P.run(P.E + ['shot', f'{out}/saved.png'])
    r['hp_saved'] = P.mem(HP).get(HP)
    P.EMU.stop()                         # the emulator writes the card file when it stops
    card = os.path.join(out, 'journey.mcd')
    P.shutil.copy(P.EMU.card_out(), card)
    return card


def main():
    cue, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(out, exist_ok=True)
    r = {}
    try:
        r['new_game'] = new_game(cue, out)
        start = r['partner'] = partner()
        if r['new_game']:
            P.feed(start, out, r)
            fight(out, r)
            evolve(start, out, r)
            card = save(out, r)
            r['reload_booted'] = P.boot(cue, card)
            P.run(P.E + ['shot', f'{out}/reloaded.png'])
            r['partner_after_reload'] = partner()
            r['hp_after_reload'] = P.mem(HP).get(HP)
            r['reloaded'] = bool(r['reload_booted']) and r['evolved'] and r['partner_after_reload'] == r['evolved_into'] \
                and r['hp_after_reload'] == r['hp_saved']
    finally:
        P.run(P.E + ['stop'])
        r['ok'] = all(r.get(k) for k in ('new_game', 'fed', 'fight_started', 'fight_finished', 'fight_counted', 'evolved',
                                         'saved', 'reloaded'))
        with open(os.path.join(out, 'journey.json'), 'w') as stream:
            json.dump(r, stream, indent=1)
        print(json.dumps(r), flush=True)
    sys.exit(0 if r['ok'] else 1)


if __name__ == '__main__':
    main()
