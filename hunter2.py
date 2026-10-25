#!/usr/bin/env python3
"""
hunter2 — máy săn sinh vật Lenia thế hệ 2.

Khác hunter1 ở chỗ:
- Tracking NHIỀU blob cùng lúc bằng matching tâm-khối (thay vì chỉ blob to nhất)
  → một đàn nhiều con vẫn đo được tốc độ từng con.
- Lọc transient: khối lượng thế giới cuối quan sát phải ≥ 70% lúc đầu
  → loại các "sinh vật" đang tan dần.
- Chấm điểm theo TRACK (chuỗi quan sát liên tục của một blob): track dài ≥ 10 điểm,
  kích thước ổn định, tốc độ = median từng cặp điểm liên tiếp.

Output: out/discoveries2/ — log.jsonl (mọi hit) + GIF preview cho hit tốt.
"""

import json
import os
import random
import sys
import time

import numpy as np
from scipy import ndimage

from lenia import Lenia, render_gif

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "discoveries2")

SIZE = 96
SETTLE = 250
OBSERVE = 220
GAP = 5
TOPK = 4            # theo dõi tối đa K blob lớn nhất mỗi lần quan sát
MIN_TRACK = 10      # số điểm tối thiểu của một track "thật"
MIN_SIZE = 6        # cell tối thiểu của một blob (lọc bụi)
MIN_SPEED = 0.15    # cell/time-unit
MATCH_DIST = 9.0    # px — ngưỡng ghép tâm khối giữa 2 lần quan sát
SIZE_RATIO = (0.5, 2.0)


def wrap_delta(d, n):
    return (d + n / 2) % n - n / 2


def wd(x1, x2, y1, y2):
    return float(np.hypot(wrap_delta(x2 - x1, SIZE), wrap_delta(y2 - y1, SIZE)))


def top_blobs(A, k):
    mask = A > 0.15
    lab, n = ndimage.label(mask)
    if n == 0:
        return []
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    order = np.argsort(sizes)[::-1][:k]
    out = []
    for idx in order:
        ys, xs = np.where(lab == idx + 1)
        out.append((len(ys), float(xs.mean()), float(ys.mean())))
    return out


def sample_params(rng):
    R = rng.choice([10, 13, 16, 20])
    B = rng.choice([1, 1, 1, 2, 2, 3])
    if B == 1:
        b = [1.0]
    else:
        b = [round(rng.uniform(0.3, 1.0), 2) for _ in range(B - 1)] + [1.0]
    m = round(rng.uniform(0.10, 0.40), 4)
    s = round(m * rng.uniform(0.06, 0.35), 4)
    return dict(R=int(R), T=10, b=b, m=m, s=s, kn=1, gn=1)


def evaluate(params, seed):
    """Trả về (best_track_metric, world_mass, tag) hoặc None."""
    sim = Lenia(params, size=SIZE, seed=seed)
    sim.step(SETTLE)
    m0 = sim.stats()[0]
    if m0 < 6.0:
        return None

    tracks = []  # mỗi track: list (t, x, y, size)
    for i in range(OBSERVE):
        sim.step(1)
        if (i + 1) % GAP:
            continue
        blobs = top_blobs(sim.A, TOPK)
        now = i + 1
        used = set()
        # ghép blob mới vào track cũ theo khoảng cách tâm + tương đồng kích thước
        for sz, x, y in sorted(blobs, reverse=True):
            best, best_d = None, None
            for ti, tr in enumerate(tracks):
                if ti in used:
                    continue
                lt, lx, ly, ls = tr[-1]
                if lt == now:
                    continue
                d = wd(lx, x, ly, y)
                if d < MATCH_DIST and SIZE_RATIO[0] < sz / max(ls, 1) < SIZE_RATIO[1]:
                    if best_d is None or d < best_d:
                        best, best_d = ti, d
            if best is not None:
                tracks[best].append((now, x, y, sz))
                used.add(best)
            else:
                tracks.append([(now, x, y, sz)])
        # track không được cập nhật tick này coi như chết (không ghép nữa)
        tracks = [tr for tr in tracks if tr[-1][0] == now] or tracks

    m1 = sim.stats()[0]
    if m1 < 0.70 * m0:
        return None  # thế giới đang tan — transient

    # chấm từng track
    best = None
    n_long = 0
    for tr in tracks:
        if len(tr) < MIN_TRACK:
            continue
        n_long += 1
        med_size = float(np.median([p[3] for p in tr]))
        if med_size < MIN_SIZE:
            continue
        dists = [wd(tr[j][1], tr[j + 1][1], tr[j][2], tr[j + 1][2])
                 for j in range(len(tr) - 1)]
        speed = float(np.median(dists)) / (GAP / params["T"])
        if best is None or speed > best[0]:
            best = (speed, med_size, len(tr))
    if best is None:
        return None
    speed = best[0]
    if speed < MIN_SPEED:
        return None
    tag = "single" if n_long == 1 else "colony"
    return speed, m1, tag, tracks


def largest_blob(A, r_pad):
    mask = A > 0.15
    lab, n = ndimage.label(mask)
    if n == 0:
        return None
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    ys, xs = np.where(lab == int(np.argmax(sizes)) + 1)
    y0 = max(int(ys.min()) - r_pad, 0)
    y1 = min(int(ys.max()) + r_pad + 1, A.shape[0])
    x0 = max(int(xs.min()) - r_pad, 0)
    x1 = min(int(xs.max()) + r_pad + 1, A.shape[1])
    return A[y0:y1, x0:x1]


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 1200
    rng = random.Random(777)
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(OUT, "log.jsonl"), "a", encoding="utf-8")
    seen, hits = set(), 0
    t0 = time.time()

    for i in range(trials):
        p = sample_params(rng)
        key = (p["R"], tuple(p["b"]), round(p["m"], 3), round(p["s"], 3))
        if key in seen:
            continue
        seen.add(key)
        seed = rng.randrange(1 << 31)
        try:
            res = evaluate(p, seed)
        except Exception:
            continue
        if not res:
            continue
        speed, mass, tag, _ = res
        hits += 1
        rec = dict(id=hits, params=p, seed=seed,
                   speed=round(speed, 3), mass=round(mass, 1), tag=tag)
        if hits <= 16:
            # render preview: tái lập thế giới từ seed rồi cắt khối lớn nhất
            sim = Lenia(p, size=SIZE, seed=seed)
            sim.step(SETTLE)
            snap = largest_blob(sim.A, p["R"] + 2)
            if snap is not None and min(snap.shape) >= 4:
                side = max(64, 2 * max(snap.shape))
                w = Lenia(p, size=side, cells=np.zeros((1, 1)))
                top = (side - snap.shape[0]) // 2
                left = (side - snap.shape[1]) // 2
                w.A[top:top + snap.shape[0], left:left + snap.shape[1]] = snap
                cap = (f"m={p['m']:.3f} s={p['s']:.3f} R={p['R']} "
                       f"b={'+'.join(f'{x:g}' for x in p['b'])} v={speed:.2f} {tag}")
                fname = f"h2_{hits:03d}_v{speed:.2f}.gif"
                render_gif(w, os.path.join(OUT, fname), 160,
                           scale=max(2, 320 // side), caption=cap)
                rec["gif"] = fname
        log.write(json.dumps(rec, ensure_ascii=False) + "\n")
        log.flush()
        print(f"HIT #{hits} [{tag}]: v={speed:.2f} mass={mass:.0f} {p}", flush=True)
        if (i + 1) % 50 == 0:
            print(f"[{i + 1}/{trials}] hits={hits} elapsed={time.time() - t0:.0f}s", flush=True)

    print(f"DONE trials={trials} hits={hits} trong {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
