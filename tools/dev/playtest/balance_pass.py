#!/usr/bin/env python3
"""Prove the care and reward pass on an original-2-MB disc (docs/mods/balance.md, 6.2).

Boots the release corpus card, sets each case's state and runs the real script section through the frame-boundary
call of qol.py, answering its menus with the pad; every result is read back from RAM.

  tools/dev/playtest/balance_pass.py DISC.cue --exe BUILD/exe/SLUS_010.32 --out DIR [--case hunt]
"""
import argparse
import json
import os
import re
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'tools'), str(ROOT / 'tools/dev/playtest')]
from qol import ProofEmu, test_card, select_option, state
from tools.langpatch import elf_symbols

OMNIPOTENT, RESTORE, BRAIN_CHIP = 9, 11, 25
SUKAMON_T, ANDROMON_T, MYOTISMON_T, GABUMON_T, VADEMON_T = 239, 240, 266, 217, 228
AGUMON, NUMEMON, MAMEMON, MONZAEMON, FLAMINGWING = 3, 11, 13, 14, 73
VACCINE = AGUMON
PARTNER = 'PARTNER_ENTITY'


def section(e, script, number, entity=0):
    gl = e.A('gameLoop')
    if entity:
        e.poke('TALKED_TO_ENTITY', bytes([entity]))
    e.run('lua', f'''
      BP_CALL={{phase=0}}
      BP_CALL.bp=PCSX.addBreakpoint({gl}, 'Exec', 4, 'balance-pass', function()
        local r=PCSX.getRegisters()
        if BP_CALL.phase==0 then
          BP_CALL.ra=r.GPR.n.ra
          r.GPR.n.a0={script}; r.GPR.n.a1={number}; r.GPR.n.a2=1
          r.GPR.n.ra={gl}; r.pc={e.A('callScriptSection')}; BP_CALL.phase=1
        else
          r.GPR.n.ra=BP_CALL.ra; BP_CALL.phase=2; BP_CALL.bp:remove()
        end
      end)
    ''')
    for _ in range(100):
        if e.run('lua', 'return BP_CALL.phase').strip() == '2':
            return
        e.wait(.1)
    raise AssertionError('section call did not return')


def drive(e, picks=(), tries=240):
    """Answer the conversation until the script ends; picks: the option of each menu, in order."""
    picks = list(picks)
    for _ in range(tries):
        s = state(e)
        if s['paused'] == 1:
            return
        if s['opcode'] == 0x10:
            e.wait(.6)
            select_option(e, picks.pop(0) if picks else 0, s['options'])
        e.press('CONFIRM', 8); e.wait(.2)
    raise AssertionError('the script did not end')


def setup(e, out, screen, triggers=(), partner=None, bits=10000, hour=12):
    e.run('load', str(out / 'boot.state'))
    e.run('lua', 'PCSX.resumeEmulator()'); e.wait(1)
    e.gs('set', f'hour={hour}', 'minute=0', 'gametime_running=0')
    for t, v in triggers:
        e.gs('trigger', str(t), str(v))
    assert e.warp(screen), f'screen {screen} did not load'
    e.wait(2)
    e.poke('INVENTORY', struct.pack('<30h', *[-1] * 30) + bytes(60) + bytes([30]))
    e.poke('MONEY', struct.pack('<i', bits))
    if partner is not None:
        e.poke(PARTNER, struct.pack('<i', partner))


def items(e):
    s = state(e)
    return [t for t, n in zip(s['types'], s['amounts']) if t != -1 and n]


def hunt(e, out, plan, roll, days, gabumon, want):
    flag, var = (178, 22) if plan == 'cheap' else (179, 23)
    setup(e, out, 209, [(90, 1), (178, 0), (179, 0), (flag, 1), (GABUMON_T, int(gabumon))])
    e.gs('pstat', '30', str(days)); e.gs('pstat', str(var), str(roll))
    section(e, 169, 81, 2)
    drive(e)
    got = items(e)
    if want is None:
        assert not got, got
    else:
        assert got[:1] == [want] and len(got) <= 3, got
    return dict(plan=plan, roll=roll, days=days, gabumon=gabumon, items=got)


def order(e, out):
    setup(e, out, 209, [(90, 1), (178, 0), (179, 0)], bits=1999)
    section(e, 169, 81, 2); drive(e, [1, 0])
    short = state(e)['bits']
    assert short == 1999, short
    setup(e, out, 209, [(90, 1), (178, 0), (179, 0)], bits=2000)
    section(e, 169, 81, 2); drive(e, [1, 0])
    assert state(e)['bits'] == 0
    return dict(short_keeps_bits=short, ordered_left=0)


def meal(e, out):
    setup(e, out, 214, [(VADEMON_T, 1)])
    e.gs('pstat', '27', '4')
    e.gs('set', 'partner.para.foodLevel=0')
    section(e, 218, 51, 2); drive(e, [2])
    bits = state(e)['bits']
    assert bits == 8500, bits
    return dict(bits=bits)


def gate(e, out, screen, script, partner, trigger, opened, inside):
    setup(e, out, screen, [(trigger, int(opened))], partner=partner)
    section(e, script, 51)
    drive(e)
    e.wait(3)
    where = e.peek('CURRENT_SCREEN', 'h')
    assert (where == inside) == opened, where
    return dict(screen=where, opened=opened)


def costume(e, out):
    setup(e, out, 145, [(350, 1)], partner=NUMEMON)
    section(e, 139, 81)
    for _ in range(120):
        if e.peek(PARTNER, 'i') == MONZAEMON and state(e)['paused'] == 1:
            return dict(partner=MONZAEMON)
        s = state(e)
        if s['paused'] != 1:
            e.press('CONFIRM', 8)
        e.wait(.5)
    raise AssertionError(('no evolution', e.peek(PARTNER, 'i')))


def sukamon(e, out):
    setup(e, out, 168, [(SUKAMON_T, 1)], hour=22, bits=1500)
    pile = struct.pack('<hBBbB', 5, 50, 50, 8, 0)
    e.poke('WORLD_POOP', pile * 3)
    section(e, 162, 6, 3)
    drive(e, [0])
    bits = state(e)['bits']; left = e.peek('WORLD_POOP', '18B')
    assert bits == 500, bits
    assert not any(left[4::6]), left
    return dict(bits=bits)


def andromon(e, out):
    setup(e, out, 168, [(ANDROMON_T, 1)], partner=MAMEMON, bits=2500)
    for _ in range(24):                  # he stands there on about one daytime visit in four
        if e.peek('ENTITY_TABLE+16', 'I'):
            break
        assert e.warp(204, 0) and e.warp(168), 'File City did not load'
        e.wait(1)
    else:
        raise AssertionError('Andromon never came')
    section(e, 162, 7, 4)
    picks = [0]
    for _ in range(240):                 # an evolution holds the pad for many seconds: wait, do not press
        s = state(e)
        if s['paused'] == 1:
            break
        if s['opcode'] == 0x10:
            e.wait(.6); select_option(e, picks.pop(0) if picks else 0, s['options'])
        if s['opcode'] in (0x10, 0x1A):
            e.press('CONFIRM', 8)
        e.wait(.5)
    else:
        e.run('shot', str(out / 'andromon-stuck.png'))
        raise AssertionError(('the script did not end', state(e)['opcode'], state(e)['bits'], e.peek(PARTNER, 'i'), e.peek('TAMER_STATE', 'b')))
    bits, species = state(e)['bits'], e.peek(PARTNER, 'i')
    assert bits == 500 and species in (MAMEMON, 27, 41), (bits, species)
    return dict(bits=bits, species=species)


def call(e, name, *args, before='', after=''):
    gl = e.A('gameLoop')
    regs = ''.join(f'r.GPR.n.a{i}={v};' for i, v in enumerate(args))
    e.run('lua', f'''
      BP_FN={{phase=0}}
      BP_FN.bp=PCSX.addBreakpoint({gl}, 'Exec', 4, 'balance-call', function()
        local r=PCSX.getRegisters()
        if BP_FN.phase==0 then
          BP_FN.ra=r.GPR.n.ra; {regs} {before}
          r.GPR.n.ra={gl}; r.pc={e.A(name)}; BP_FN.phase=1
        else
          {after} r.GPR.n.ra=BP_FN.ra; BP_FN.phase=2; BP_FN.bp:remove()
        end
      end)
    ''')
    for _ in range(100):
        if e.run('lua', 'return BP_FN.phase').strip() == '2':
            return
        e.wait(.1)
    raise AssertionError(f'{name} did not return')


def evolution_item(e, out):
    setup(e, out, 168, partner=AGUMON)
    e.gs('set', 'partner.stats.hp=100', 'partner.para.age=1')
    life = e.peek('PARTNER_PARA+0x48', 'h')
    call(e, 'handleEvoItems', FLAMINGWING)
    for _ in range(120):
        if e.peek(PARTNER, 'i') != AGUMON and e.peek('TAMER_STATE', 'b') == 0:
            break
        e.wait(.5)
    e.wait(2)
    species = e.peek(PARTNER, 'i')
    hp = int(re.search(r"'hp': (\d+)", e.gs('show', 'partner.stats')).group(1))
    assert species == 21 and hp == 800 and e.peek('HAS_USED_EVOITEM', 'B') == 0, (species, hp)
    return dict(species=species, hp=hp, lifetime=[life, e.peek('PARTNER_PARA+0x48', 'h')])


def battle_gain(e, out):
    """A real wild fight, won at once: the strongest enemy's stats are 2000, the partner's 3000."""
    setup(e, out, 168, [(1, 1)])
    assert e.warp(0, 0), 'Native Forest did not load'
    e.wait(2)
    e.gs('set', 'partner.stats.off=999', 'partner.stats.speed=999', 'partner.stats.hp=9000', 'partner.stats.currentHP=9000')
    e.gs('approach', '0', '150')
    for _ in range(80):
        if e.peek('GAME_STATE', 'H') == 1:
            break
        e.press('CONFIRM', 8); e.wait(.3)
    else:
        raise AssertionError('the fight did not start')
    e.wait(3)
    e.poke('INITIAL_COMBAT_STATS', struct.pack('<6h', *[3000] * 6) + struct.pack('<6h', *[2000] * 6))
    e.poke('STATS_GAINS', bytes(12))
    for _ in range(120):
        e.poke('INITIAL_COMBAT_STATS', struct.pack('<6h', *[3000] * 6) + struct.pack('<6h', *[2000] * 6))
        gains = e.peek('STATS_GAINS', '6h')
        if any(gains):
            assert gains == [20] * 6, gains
            return dict(gains=gains)
        e.press('CONFIRM', 8); e.wait(.4)
    raise AssertionError('no battle end')


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('disc'); p.add_argument('--exe', required=True); p.add_argument('--out', required=True)
    p.add_argument('--case', default='all')
    p.add_argument('--port', type=int, default=int(os.environ.get('EMU_PORT', 39147)))
    a = p.parse_args(); out = Path(a.out).resolve(); out.mkdir(parents=True, exist_ok=True)
    e = ProofEmu(a.disc, a.exe, a.port, str(out / 'emu'))
    for name, (address, _, _) in elf_symbols(a.exe + '.elf').items():
        e.table.setdefault(name, address)
    e.env['EMU_ARGS'] = '-interpreter -debugger'
    cases = {
        'hunt-wait': lambda: hunt(e, out, 'cheap', 0, 0, False, None),
        'hunt-cheap': lambda: hunt(e, out, 'cheap', 0, 1, False, OMNIPOTENT),
        'hunt-pricey': lambda: hunt(e, out, 'pricey', 99, 3, False, BRAIN_CHIP),
        'hunt-gabumon': lambda: hunt(e, out, 'pricey', 0, 3, True, RESTORE),
        'order': lambda: order(e, out),
        'meal': lambda: meal(e, out),
        'mansion-closed': lambda: gate(e, out, 35, 35, VACCINE, MYOTISMON_T, False, 52),
        'mansion-open': lambda: gate(e, out, 35, 35, VACCINE, MYOTISMON_T, True, 52),
        'costume': lambda: costume(e, out),
        'sukamon': lambda: sukamon(e, out),
        'andromon': lambda: andromon(e, out),
        'evolution-item': lambda: evolution_item(e, out),
        'battle-gain': lambda: battle_gain(e, out),
    }
    results = {}
    try:
        e.start(test_card(out))
        error = e.continue_game(); assert error == 0, f'Continue failed: {error}'
        e.wait(5); assert e.in_control()
        e.gs('set', 'partner.para.condition=0', 'partner.para.foodLevel=240', 'partner.para.tiredness=0')
        e.run('save', str(out / 'boot.state'))
        for name, case in cases.items():
            if a.case not in ('all', name):
                continue
            try:
                results[name] = case()
            except BaseException as err:
                results[name] = dict(error=repr(err)[:300])
                e.run('shot', str(out / f'{name}-fail.png'), check=False)
            print(name, results[name], flush=True)
            (out / 'result.json').write_text(json.dumps(results, indent=2) + '\n')
    finally:
        e.stop()
    return 1 if any('error' in r for r in results.values()) else 0


if __name__ == '__main__':
    sys.exit(main())
