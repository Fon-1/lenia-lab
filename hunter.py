#!/usr/bin/env python3
"""
Species hunter — săn sinh vật Lenia mới bằng tìm kiếm ngẫu nhiên có định hướng.

Cách làm: nhiễu hóa gen (R, số vỏ kernel b, μ, σ) quanh vùng sống được, nấu canh
ngẫu nhiên, chờ đám đông tự tổ chức, rồi chấm điểm:
  - khối vật chất phải tồn tại ổn định (khối lượng biến thiên < 25%)
  - tâm khối phải di chuyển bền bỉ (tốc độ ≥ MIN_SPEED cell/time-unit)
Thỏa mãn = phát hiện một "creature" — cắt đúng khối vật chất đó ra, lưu gen + GIF.

Cách này chính xác là cách cộng đồng Lenia đã tìm ra hàng trăm loài trong repo gốc.
Chạy:  python hunter.py 300
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
OUT = os.path.join(HERE, "out", "discoveries")

SIZE = 96        # thế giới mỗi lần thử
SETTLE = 250     # bước chờ đám đông tự tổ chức
OBSERVE = 200    # bước quan sát tốc độ
GAP = 5          # bước giữa hai lần lấy tâm khối
MIN_SPEED = 0.15 # cell / time-unit (median) — dưới là bụi/khiên tĩnh, không phải kẻ di chuyển
MIN_MASS = 6.0
MAX_GIFS = 12    # chỉ render GIF cho 12 phát hiện đầu


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


def wrap_delta(d, n):
    return (d + n / 2) % n - n / 2


def blob_com(A):
    """Tâm khối + kích thước của khối vật chất liên thông lớn nhất."""
    mask = A > 0.15
    lab, n = ndimage.label(mask)
    if n == 0:
        return None
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    ys, xs = np.where(lab == int(np.argmax(sizes)) + 1)
    return len(ys), float(xs.mean()), float(ys.mean())


def evaluate(params, seed):
    """Trả về (tốc độ blob lớn nhất, khối lượng thế giới) nếu có sinh vật di chuyển."""
    sim = Lenia(params, size=SIZE, seed=seed)
    sim.step(SETTLE)
    m0 = sim.stats()[0]
    if m0 < MIN_MASS:
        return None
    obs = []
    for i in range(OBSERVE):
        sim.step(1)
        if (i + 1) % GAP == 0:
            bc = blob_com(sim.A)
            if bc:
                obs.append(bc)
    m1 = sim.stats()[0]
    if abs(m1 - m0) / m0 > 0.25:
        return None
    if len(obs) < 6:
        return None
    med_size = float(np.median([o[0] for o in obs]))
    if med_size < 6:
        return None
    # chỉ tính cặp quan sát cùng "danh tính" blob (kích thước tương đương),
    # lấy median để khử nhiễu do blob trộn/nhiều con cùng lúc
    dists = []
    for (s1, x1, y1), (s2, x2, y2) in zip(obs, obs[1:]):
        if abs(s1 - s2) / max(s1, s2) > 0.4:
            continue
        dists.append(np.hypot(wrap_delta(x2 - x1, SIZE), wrap_delta(y2 - y1, SIZE)))
    if len(dists) < 4:
        return None
    speed = float(np.median(dists)) / (GAP / params["T"])
    if speed < MIN_SPEED:
        return None
    return speed, m1, sim.A


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
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    rng = random.Random(2026)
    os.makedirs(OUT, exist_ok=True)
    log_path = os.path.join(OUT, "log.jsonl")
    log = open(log_path, "a", encoding="utf-8")
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

        speed, mass, A = res
        hits += 1
        rec = dict(id=hits, params=p, seed=seed,
                   speed=round(speed, 3), mass=round(mass, 1))
        if hits <= MAX_GIFS:
            snap = largest_blob(A, p["R"] + 2)
            if snap is not None and min(snap.shape) >= 4:
                side = max(64, 2 * max(snap.shape))
                w = Lenia(p, size=side, cells=np.zeros((1, 1)))
                top = (side - snap.shape[0]) // 2
                left = (side - snap.shape[1]) // 2
                w.A[top:top + snap.shape[0], left:left + snap.shape[1]] = snap
                cap = (f"m={p['m']:.3f} s={p['s']:.3f} R={p['R']} "
                       f"b={'+'.join(f'{x:g}' for x in p['b'])} v={speed:.2f}")
                fname = f"disc_{hits:03d}_v{speed:.2f}.gif"
                nf, gen = render_gif(w, os.path.join(OUT, fname), 160,
                                     scale=max(2, 320 // side), caption=cap)
                rec["gif"] = fname
        log.write(json.dumps(rec, ensure_ascii=False) + "\n")
        log.flush()
        print(f"HIT #{hits}: v={speed:.2f} mass={mass:.0f} {p}", flush=True)

        if (i + 1) % 25 == 0:
            print(f"[{i + 1}/{trials}] hits={hits} elapsed={time.time() - t0:.0f}s", flush=True)

    print(f"DONE trials={trials} hits={hits} trong {time.time() - t0:.0f}s", flush=True)
    print(f"Log: {log_path}", flush=True)


if __name__ == "__main__":
    main()
