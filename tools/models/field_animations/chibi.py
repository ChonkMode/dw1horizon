"""Chibi proportions: reshape a reviewed imported partner to Digimon World's anatomy.

Every part of an imported model is one rigid mesh per bone, so the shape can be baked: the vertices of a bone and the
offsets of its children move through one local scale, in every animation, and nothing detaches. Head, hands and feet
grow, legs get shorter and thicker, arms and torso thicker. A uniform rescale brings the idle back to the height of
the species record. The manifest, content/models/imports/chibi.json, holds per species: the pins, the group of every
bone and the factors. An empty manifest changes nothing.

The floor is the one thing a bake cannot keep: a shorter leg leaves a walk floating and a sitting clip sinking, by
different amounts on different ticks. So each clip is replayed with the engine's interpreter and the carrier's height
is rewritten, with as few keys as a tolerance allows, against the lowest vertex of each tick: on the ground when the source is on
or near it, at the source's clearance less CLEARANCE when it really leaves the ground. No key instruction is added.

Stride and travel shrink together with the legs, down to the floor of the native speeds (pace.py's). Nothing else of
the root's motion changes. A species failing a check raises Refused, naming the check.
"""
import copy
import hashlib
import importlib
import json
import math
from pathlib import Path

import animsheet
import mmd
import motioncyclelayer
import motionstorage

ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / 'content/models/imports/chibi.json'
WALK, CONDITION, RUN = 2, 3, 4
SPEED_FLOOR = {WALK: 15, CONDITION: 9.5, RUN: 35}
SPEED_MARGIN = 1.03
CLEARANCE = 12            # a source this close over the floor counts as standing on it
KEY_TOLERANCE = 1.5       # a height key is dropped when the line through its neighbours stays this close
MAX_SINK = 4              # units a tick may stay under its target: 0.2 px at field size
MAX_FLOAT = 4             # units a tick may stay over it
MIN_FINAL_SCALE = 0.70    # the uniform rescale must not undo the reshaping
GROUND_PASSES = 3


class Refused(ValueError):
    """The species stays as it is: this check failed."""


# ------------------------------------------------------------------ small vectors
def _scale_matrix(axis, axial, radial):
    """Scale along the unit axis and across it."""
    return [[radial * (i == j) + (axial - radial) * axis[i] * axis[j] for j in range(3)] for i in range(3)]


def _diagonal(k):
    return [[k * (i == j) for j in range(3)] for i in range(3)]


def _apply(M, v):
    return [sum(M[i][j] * v[j] for j in range(3)) for i in range(3)]


def _unit(v):
    n = math.sqrt(sum(c * c for c in v))
    return [c / n for c in v] if n else None


def _principal(points):
    """The principal direction of a cloud of points, by power iteration."""
    n = len(points)
    mean = [sum(p[i] for p in points) / n for i in range(3)]
    q = [[p[i] - mean[i] for i in range(3)] for p in points]
    C = [[sum(p[i] * p[j] for p in q) for j in range(3)] for i in range(3)]
    best = max(range(3), key=lambda i: C[i][i])
    v = [float(i == best) for i in range(3)]
    for _ in range(40):
        v = _unit(_apply(C, v)) or v
    return v


def _translation(animation):
    return (6, 7, 8) if animation.has_scale else (3, 4, 5)


def _clamp16(value):
    return max(-32768, min(32767, int(round(value))))


# ------------------------------------------------------------------ the rig at rest
class Rig:
    def __init__(self, model, skeleton):
        self.m, self.skeleton, self.nb = model, skeleton, len(skeleton)
        self.children = {b: [c for c in range(self.nb) if skeleton[c][1] == b] for b in range(self.nb)}
        self.verts = {b: [list(v[:3]) for v in model.tmd.obj_verts(o)] for b, (o, _) in enumerate(skeleton) if o >= 0}
        self.verts = {b: v for b, v in self.verts.items() if v}
        roots = self.children[0]
        if len(roots) != 1:
            raise Refused(f'one carrier under the root expected, found {roots}')
        self.carrier = roots[0]

    def rest(self):
        """(pose, matrices) of the first idle tick, the root at the origin."""
        frames = animsheet.slot_frames(self.m, self.nb, 0)[0]
        pose = [list(v) for v in frames[0]]
        pose[0] = [4096, 4096, 4096, 0, 0, 0, 0, 0, 0]
        return pose, mmd.bone_matrices(self.m, pose)

    def bounds(self):
        """(top, ground): the highest and the lowest y of the rest pose; y grows downwards."""
        _, mats = self.rest()
        ys = [mats[b][1][0] * x + mats[b][1][1] * y + mats[b][1][2] * z + mats[b][1][3]
              for b, vs in self.verts.items() for x, y, z in vs]
        return -min(ys), max(ys)


# ------------------------------------------------------------------ the bake
def _axis(rig, rest, b, groups):
    """The direction along which a limb piece is long, in its own frame: to its child in the chain, else its vertices."""
    g = groups[b]
    follows = {'thigh': ('thigh', 'shin', 'foot'), 'shin': ('shin', 'foot'), 'arm': ('arm', 'hand'),
               'shoulder': ('shoulder', 'arm', 'hand'), 'cloth': ('cloth',)}.get(g, (g,))
    kids = [c for c in rig.children[b] if groups[c] in follows]
    if kids:
        offset = rest[kids[0]][6:9]
        if math.sqrt(sum(c * c for c in offset)) > 3:
            return _unit(offset)
    if b in rig.verts and len(rig.verts[b]) >= 3:
        return _principal(rig.verts[b])
    return [0.0, 1.0, 0.0]


def _sole(rig, mats, b):
    """The height (own frame) of the point of a foot that is lowest at rest: a foot grows about it and stays planted."""
    if b not in rig.verts:
        return [0.0, 0.0, 0.0]
    M = mats[b]
    lowest = max(rig.verts[b], key=lambda v: M[1][0] * v[0] + M[1][1] * v[1] + M[1][2] * v[2])
    return [0.0, float(lowest[1]), 0.0]


def bone_scales(rig, groups, factors):
    """bone -> (local scale matrix, anchor in the bone's frame)."""
    rest, mats = rig.rest()
    F = lambda name: factors.get(name, 1.0)
    out = {}
    for b in range(1, rig.nb):
        g = groups[b]
        anchor = [0.0, 0.0, 0.0]
        M = None
        if g in ('head', 'headpart') and F('head') != 1:
            M = _diagonal(F('head'))
        elif g == 'hand' and F('hand') != 1:
            M = _diagonal(F('hand'))
        elif g in ('foot', 'footpart') and F('foot') != 1:
            M = _diagonal(F('foot'))
            if g == 'foot':
                anchor = _sole(rig, mats, b)
        elif g in ('thigh', 'shin', 'hipjoint') and (F('leg_axial') != 1 or F('leg_radial') != 1):
            M = _scale_matrix(_axis(rig, rest, b, groups), F('leg_axial'), F('leg_radial'))
        elif g in ('arm', 'shoulder') and F('arm_radial') != 1:
            M = _scale_matrix(_axis(rig, rest, b, groups), 1.0, F('arm_radial'))
        elif g in ('chest', 'carrier', 'pelvis', 'neck') and F('torso') != 1:
            M = _diagonal(F('torso'))
        elif g == 'cloth' and F('leg_axial') != 1:
            M = _scale_matrix(_axis(rig, rest, b, groups), F('leg_axial'), 1.0)
        if M is not None:
            out[b] = (M, anchor)
    return out


def _bake(rig, scales):
    """The vertices of each scaled bone, and in every animation the offsets of its children."""
    tmd = rig.m.tmd
    for b, (M, anchor) in scales.items():
        o = rig.skeleton[b][0]
        if o < 0:
            continue
        ob = tmd.objects[o]
        for i in range(ob.vert_start, ob.vert_start + ob.nvert):
            x, y, z, p = tmd.verts[i]
            v = _apply(M, [x - anchor[0], y - anchor[1], z - anchor[2]])
            v = [v[j] + anchor[j] for j in range(3)]
            if any(abs(c) > 32767 for c in v):
                raise Refused('a vertex leaves the 16-bit range')
            tmd.verts[i] = (round(v[0]), round(v[1]), round(v[2]), p)
    rig.verts = {b: [list(v[:3]) for v in tmd.obj_verts(rig.skeleton[b][0])] for b in rig.verts}
    for a in rig.m.anims.anims:
        ti = _translation(a)
        for b, (M, anchor) in scales.items():
            for c in rig.children[b]:
                v = a.pose[c - 1]
                moved = _apply(M, [v[ti[j]] - anchor[j] for j in range(3)])
                for j in range(3):
                    v[ti[j]] = _clamp16(moved[j] + anchor[j])
        for instruction in a.instrs:
            if instruction['op'] != 'key':
                continue
            for block in instruction['bones']:
                parent = rig.skeleton[block['bone']][1] if block['bone'] < rig.nb else -1
                if parent in scales and any(ch in block['vals'] for ch in ('tx', 'ty', 'tz')):
                    moved = _apply(scales[parent][0], [block['vals'].get(ch, 0) for ch in ('tx', 'ty', 'tz')])
                    for ch, value in zip(('tx', 'ty', 'tz'), moved):
                        if ch in block['vals']:
                            block['vals'][ch] = _clamp16(value)


def _scale_keys(animations, bone, k):
    """Multiply a bone's translation keys by k; their sum per loop segment stays what k times the old sum is."""
    for a in animations:
        segment, groups = 0, {}
        for instruction in a.instrs:
            if instruction['op'] == 'loop_start':
                segment += 1
            elif instruction['op'] == 'key':
                for block in instruction['bones']:
                    if block['bone'] == bone:
                        for ch in ('tx', 'ty', 'tz'):
                            if ch in block['vals']:
                                groups.setdefault((segment, ch), []).append((block, block['vals'][ch]))
        for (_, ch), items in groups.items():
            new = [_clamp16(v * k) for _, v in items]
            rest = round(sum(v for _, v in items) * k) - sum(new)
            if rest:
                i = max(range(len(items)), key=lambda n: abs(items[n][1]))
                new[i] = _clamp16(new[i] + rest)
            for (block, _), value in zip(items, new):
                block['vals'][ch] = value


def _rescale(model, k):
    """The whole model grows by k (sizes.py's rule: vertices and every translation)."""
    t = model.tmd
    t.verts = [tuple(_clamp16(c * k) for c in v[:3]) + (v[3],) for v in t.verts]
    for a in model.anims.anims:
        ti = _translation(a)
        for v in a.pose:
            for i in ti:
                v[i] = _clamp16(v[i] * k)
        for instruction in a.instrs:
            if instruction['op'] == 'key':
                for block in instruction['bones']:
                    for ch in ('tx', 'ty', 'tz'):
                        if ch in block['vals']:
                            block['vals'][ch] = _clamp16(block['vals'][ch] * k)


# ------------------------------------------------------------------ clips
def clips(model):
    """{animation index: the first slot that plays it}."""
    out = {}
    for slot, index in enumerate(model.anims.table):
        if index is not None:
            out.setdefault(index, slot)
    return out


def replay(model, nb, index, slot, carrier):
    """A clip through the engine's interpreter, one pass of any loop: its frames (the frame counter of each tick), the
    poses with the root travel taken out but for its height, the carrier's height per tick, and its events."""
    player = mmd.AnimPlayer(model.anims.anims[index], nb, slot)
    frames, poses, heights = [], [], []
    while len(poses) < 600 and player.tick(stop_at_infinite_loop=True):
        frames.append(player.frames[-1])
        pose = [list(v) for v in player.pose]
        pose[0][6:9] = [0, player.root[1], 0]
        poses.append(pose)
        heights.append(pose[carrier][7])
    return frames, poses, heights, player.events


def lowest(model, points, pose):
    """The lowest y of the mesh in a pose."""
    mats = mmd.bone_matrices(model, pose)
    worst = -1e9
    for b, vs in points.items():
        M = mats[b][1]
        a, b_, c, d = M[0], M[1], M[2], M[3]
        for x, y, z in vs:
            value = a * x + b_ * y + c * z + d
            if value > worst:
                worst = value
    return worst


def lows(model, rig):
    """{animation index: the lowest y of each tick}."""
    out = {}
    for index, slot in clips(model).items():
        poses = replay(model, rig.nb, index, slot, rig.carrier)[1]
        out[index] = [lowest(model, rig.verts, p) for p in poses]
    return out


def target(low):
    """Where a tick's lowest vertex belongs, given the source's: y grows downwards, the floor is 0."""
    if low >= -CLEARANCE:
        return 0.0
    return max(low, 2.0 * (low + CLEARANCE))        # a ramp, so a hover at twice the margin stays where it was


def _chains(animation):
    """The clip's key instructions cut at its loop marks: [(instructions, frame the last one runs up to, loop start
    frame or None)], or None when a stretch of the clip has no key where the height could change."""
    chains, keys = [], []
    def flush(until, jump=None):
        if keys:
            chains.append((list(keys), until, jump))
            keys.clear()
    for instruction in animation.instrs:
        op = instruction['op']
        if op == 'key':
            keys.append(instruction)
            continue
        if op == 'loop_start':
            if keys:
                chains.append((list(keys), None, None))
                keys.clear()
        elif op == 'loop_end':
            flush(instruction['frame'], instruction['jump'])
        elif op == 'end':
            flush(animation.frame_count)
    flush(animation.frame_count)
    for i, (keyset, until, jump) in enumerate(chains):
        if until is None:
            if i + 1 == len(chains):
                return None
            chains[i] = (keyset, chains[i + 1][0][0]['frame'], None)
        if jump is not None and keyset[0]['frame'] != jump:
            return None
        if i and chains[i][0][0]['frame'] > chains[i - 1][1]:
            return None
    return chains


def _simplify(points, tolerance):
    """Indices kept of [(x, y)]: the ends and whatever a line between kept points misses by more than the tolerance."""
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        (xa, ya), (xb, yb) = points[a], points[b]
        worst, at = tolerance, None
        for i in range(a + 1, b):
            x, y = points[i]
            miss = abs(y - (ya + (yb - ya) * (x - xa) / (xb - xa)))
            if miss > worst:
                worst, at = miss, i
        if at is not None:
            keep.add(at)
            stack += [(a, at), (at, b)]
    return sorted(keep)


def _rewrite_heights(animation, carrier, height, tolerance):
    """The carrier's height follows height[frame] (rounded) with as few keys as the tolerance allows; the old height
    keys go. A key lands on an existing key instruction when one sits on that frame, else on a new one."""
    animation.instrs = [i for i in animation.instrs if not i.get('added')]
    for instruction in animation.instrs:
        if instruction['op'] == 'key':
            for block in instruction['bones']:
                if block['bone'] == carrier:
                    block['vals'].pop('ty', None)
            instruction['bones'] = [g for g in instruction['bones'] if g['vals']]
    chains = _chains(animation)
    ti = _translation(animation)
    animation.pose[carrier - 1][ti[1]] = _clamp16(height[chains[0][0][0]['frame']])
    for keys, until, jump in chains:
        first = keys[0]['frame']
        if first >= until:
            continue
        end = height[jump if jump is not None else until]
        line = [(f, height[f]) for f in range(first, until)] + [(until, end)]
        kept = _simplify(line, tolerance)
        for a, b in zip(kept, kept[1:]):
            frame, ticks = line[a][0], line[b][0] - line[a][0]
            delta = round(line[b][1]) - round(line[a][1])
            instruction = next((k for k in keys if k['frame'] == frame and frame != until), None)
            if instruction is None:
                instruction = dict(op='key', frame=frame, bones=[], added=True)
                after = animation.instrs.index(keys[0])
                at = next(i for i in range(after, len(animation.instrs))
                          if animation.instrs[i]['op'] in ('end', 'loop_start', 'loop_end') or animation.instrs[i]['frame'] > frame)
                animation.instrs.insert(at, instruction)
            block = next((g for g in instruction['bones'] if g['bone'] == carrier and g['div'] == ticks), None)
            if block is None:
                block = dict(bone=carrier, div=ticks, vals={})
                instruction['bones'].append(block)
            block['vals']['ty'] = delta


def ground(model, rig, source_lows, tolerance=KEY_TOLERANCE):
    """Rewrite the carrier's height of every clip so each tick's lowest vertex lands on its target. -> report per
    slot: source, before and after, as (min, max) of the lowest vertex, and the worst miss."""
    carrier, nb = rig.carrier, rig.nb
    report = {}
    for index, slot in clips(model).items():
        animation = model.anims.anims[index]
        frames, poses, _, events = replay(model, nb, index, slot, carrier)
        reference = [[v for j, v in enumerate(bone) if (b, j) != (carrier, 7)] for p in poses for b, bone in enumerate(p)]
        goal = [target(low) for low in source_lows[index]]
        before = [lowest(model, rig.verts, p) for p in poses]
        constant = _chains(animation) is None or any(i['op'] == 'tex' for i in animation.instrs)
        for _ in range(GROUND_PASSES):
            frames, poses, heights, _ = replay(model, nb, index, slot, carrier)
            miss = [lowest(model, rig.verts, p) - g for p, g in zip(poses, goal)]
            if constant:
                ti = _translation(animation)
                animation.pose[carrier - 1][ti[1]] = _clamp16(animation.pose[carrier - 1][ti[1]] - max(miss))
                continue
            height = {}
            for f, h, m in zip(frames, heights, miss):
                height[f] = min(height.get(f, 1e9), h - m)
            _rewrite_heights(animation, carrier, height, tolerance)
        frames, poses, _, after_events = replay(model, nb, index, slot, carrier)
        after = [lowest(model, rig.verts, p) for p in poses]
        same = [[v for j, v in enumerate(bone) if (b, j) != (carrier, 7)] for p in poses for b, bone in enumerate(p)]
        if same != reference or after_events != events:
            raise Refused(f'slot {slot:#x}: the height rewrite changed something else')
        miss = [a - g for a, g in zip(after, goal)]
        report[slot] = dict(ticks=len(after), source=_span(source_lows[index]), before=_span(before), after=_span(after),
                            sink=round(max(miss), 1), float=round(-min(miss), 1), constant=constant)
    return report


def _span(values):
    return [round(min(values), 1), round(max(values), 1)]


def _close_loops(model, nb, carrier):
    """Rounding can leave a looping clip a few units open sideways: take that off its last key inside the loop."""
    left = {}
    for index, slot in clips(model).items():
        animation = model.anims.anims[index]
        for _ in range(8):
            frames, start, _ = animsheet.slot_frames(model, nb, slot)
            if start is None or len(frames) - 1 <= start:
                break
            first, last = frames[start][carrier], frames[-1][carrier]
            drift = {ch: last[j] - first[j] for j, ch in zip((6, 7, 8), ('tx', 'ty', 'tz')) if last[j] != first[j]}
            if not drift:
                left.pop(slot, None)
                break
            left[slot] = drift
            body, inside = [], False
            for instruction in animation.instrs:
                if instruction['op'] == 'loop_start':
                    inside = True
                elif instruction['op'] == 'loop_end':
                    inside = False
                elif instruction['op'] == 'key' and inside:
                    body.append(instruction)
            for ch, d in drift.items():
                for instruction in reversed(body):
                    block = next((g for g in instruction['bones'] if g['bone'] == carrier and ch in g['vals']), None)
                    if block is not None:
                        block['vals'][ch] = _clamp16(block['vals'][ch] - d)
                        break
    return left


def _speed(model, nb, slot):
    """Forward units per tick of a looping field clip, or None."""
    if slot >= len(model.anims.table) or model.anims.table[slot] is None:
        return None
    frames, loop, _ = animsheet.slot_frames(model, nb, slot)
    if loop is None or len(frames) - 1 <= loop:
        return None
    return abs(frames[-1][0][8] - frames[loop][0][8]) / (len(frames) - 1 - loop)


def carried_point(scales, k, bone, point):
    """Where a point fixed to a bone (an effect origin, a condition bubble) lands: the same bake as the bone's vertices."""
    p = [float(c) for c in point]
    if bone in scales:
        M, anchor = scales[bone]
        p = _apply(M, [p[j] - anchor[j] for j in range(3)])
        p = [p[j] + anchor[j] for j in range(3)]
    return [round(c * k) for c in p]


def species_patch(record, scales, k):
    """The fields of the species record tied to bones, carried through the bake."""
    patch = {}
    def moved(bone, xyz):
        if 'any' in xyz:
            return xyz[:1] + carried_point(scales, k, bone, [0, *xyz[1:]])[1:] if xyz[0] == 'any' else xyz
        return carried_point(scales, k, bone, xyz)
    if 'effect_origins' in record:
        patch['effect_origins'] = [[e[0], *moved(e[0], e[1:4]), e[4], *moved(e[4], e[5:8])] for e in record['effect_origins']]
    if 'effect_origin_fallback' in record:
        e = record['effect_origin_fallback']
        patch['effect_origin_fallback'] = [e[0], *moved(e[0], e[1:4])]
    if 'condition_bubble' in record:
        e = record['condition_bubble']
        patch['condition_bubble'] = [*moved(e[3], e[:3]), e[3]]
    return patch


def reshape(data, skeleton, sid, row):
    """The reshaped model of a row (groups, factors, height) -> (bytes, report, the bone scales and the final k).
    Raises Refused when a check fails."""
    mmd.exe().skeleton[sid] = skeleton
    mmd.exe().bone_count[sid] = len(skeleton)
    model = mmd.MMD.parse(data, len(skeleton))
    model.type = sid
    rig = Rig(model, skeleton)
    groups = {int(b): g for b, g in row['groups'].items()}
    groups = [groups.get(b, 'other') for b in range(rig.nb)]
    factors = row['factors']
    source_lows = lows(model, rig)
    speeds = {slot: _speed(model, rig.nb, slot) for slot in SPEED_FLOOR}
    standing = rig.bounds()[1]            # a hovering species keeps its clearance
    scales = bone_scales(rig, groups, factors)
    _bake(rig, scales)
    kl = factors.get('leg_axial', 1.0)
    carrier = rig.carrier
    if kl != 1:
        # a clip's first carrier offset differs from the idle's by the leg geometry of its first pose: it shrinks too
        idle = model.anims.anims[model.anims.table[0]]
        base = [idle.pose[carrier - 1][i] for i in _translation(idle)]
        for a in model.anims.anims:
            if a is not idle:
                v = a.pose[carrier - 1]
                for i, b0 in zip(_translation(a), base):
                    v[i] = _clamp16(b0 + kl * (v[i] - b0))
        _scale_keys(model.anims.anims, carrier, kl)
    top, floor = rig.bounds()
    for a in model.anims.anims:
        ti = _translation(a)
        a.pose[carrier - 1][ti[1]] = _clamp16(a.pose[carrier - 1][ti[1]] + standing - floor)
    k = (row['height'] + standing) / (top + floor)
    if k < MIN_FINAL_SCALE:
        raise Refused(f'final scale {k:.3f}: the height rule shrinks the body too much')
    _rescale(model, k)
    rig.verts = {b: [list(v[:3]) for v in model.tmd.obj_verts(skeleton[b][0])] for b in rig.verts}
    for slot, speed in speeds.items():
        if speed:
            wanted = min(speed, max(speed * kl, SPEED_FLOOR[slot] * SPEED_MARGIN))
            now = _speed(model, rig.nb, slot)
            _scale_keys([model.anims.anims[model.anims.table[slot]]], 0, wanted / now)
    left = _close_loops(model, rig.nb, carrier)
    if left:
        raise Refused(f'loops left open: {left}')
    floors = ground(model, rig, source_lows, row.get('key_tolerance', KEY_TOLERANCE))
    left = _close_loops(model, rig.nb, carrier)
    if left:
        raise Refused(f'loops left open after grounding: {left}')
    for slot, row_ in floors.items():
        if row_['sink'] > MAX_SINK or row_['float'] > MAX_FLOAT:
            raise Refused(f'slot {slot:#x}: {row_["sink"]} under, {row_["float"]} over its floor')
    after = {slot: _speed(model, rig.nb, slot) for slot in SPEED_FLOOR}
    for slot, speed in after.items():
        if speed is not None and speed < SPEED_FLOOR[slot] and speed < speeds[slot]:
            raise Refused(f'slot {slot}: {speed:.1f} under the speed floor')
    model.anims.anims, model.anims.table = motioncyclelayer.share_identical_streams(model.anims.anims, model.anims.table)
    result = model.build()
    try:
        storage = motionstorage.require(result, len(skeleton))
    except ValueError as error:
        raise Refused(str(error))
    rig.m = mmd.MMD.parse(result, len(skeleton))
    rig.m.type = sid
    height = rig.bounds()[0]
    if abs(height - row['height']) > 0.01 * row['height']:
        raise Refused(f'height {height:.0f} against {row["height"]}')
    report = dict(species=sid, factors=factors, final_scale=round(k, 4), height=round(height), bytes=[len(data), len(result)],
                  speeds={str(s): [speeds[s] and round(speeds[s], 1), after[s] and round(after[s], 1)] for s in speeds},
                  floors={f'{s:#x}': v for s, v in floors.items()}, storage=storage['fits'])
    return result, report, scales, k


def build(data, skeleton):
    """The reviewed overlay of a pinned species (the manifest's row) over the recipe before it."""
    rows = json.loads(MANIFEST.read_text())
    digest = hashlib.sha256(data).hexdigest()
    matches = [(int(sid), row) for sid, row in rows.items() if row['source_sha256'] == digest]
    if len(matches) != 1:
        raise ValueError('Chibi proportions require an individually pinned source')
    sid, row = matches[0]
    if hashlib.sha256(json.dumps(skeleton).encode()).hexdigest() != row['skeleton_sha256']:
        raise ValueError('Chibi proportions: the skeleton differs from its reviewed source')
    previous = None
    if row.get('base_generator'):
        data, previous = importlib.import_module(row['base_generator']).build(data, skeleton)
    if hashlib.sha256(data).hexdigest() != row['post_source_sha256']:
        raise ValueError('Chibi proportions: the preceding recipe differs from the reviewed input')
    result, report, scales, k = reshape(data, skeleton, sid, row)
    record = json.loads(next((ROOT / 'content/species').glob(f'{sid}-*.json')).read_text())
    proof = dict(report, source_sha256=digest, output_sha256=hashlib.sha256(result).hexdigest(),
                 preceding_recipe=previous, species_patch=species_patch(record, scales, k))
    if previous and 'generated_skeleton' in previous:
        proof['generated_skeleton'] = previous['generated_skeleton']
    return result, proof
