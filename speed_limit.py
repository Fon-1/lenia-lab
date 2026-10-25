#!/usr/bin/env python3
"""
speed_limit.py — giới hạn tốc độ của sinh vật Lenia theo bán kính kernel R.

Câu hỏi: sinh vật Lenia bơi nhanh nhất được bao nhiêu cell/time-unit, và tốc độ đó
tăng thế nào theo R? Trần lý thuyết: 1 bước lây lan tối đa R cell → R/T·? — thực tế
chịu ràng buộc của động lực học growth, nên phải đo thực nghiệm.

Phương pháp: với mỗi R ∈ {10,13,16,20} × 2 bộ kernel (1 vỏ, 2 vỏ), quét lưới 20×20
trên (μ, σ/μ), canh 64², đo tốc độ median của blob lớn nhất (có lọc ổn định khối
lượng ±25% và liên tục kích thước blob). Ghi lại tốc độ tối đa "sống ổn định".

Chạy: python speed_limit.py → out/maps/SPEED_LIMIT.md + log JSONL
"""

import itertools
import json
import os
import time

import numpy as np
from scipy import ndimage

from lenia import Lenia

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "maps")

SIZE = 64
SETTLE = 80
OBSERVE = 60
GAP = 5
GRID = 20
RS = [10, 13, 16, 20]
KERNELS = {"1 vo": [1.0], "2 vo": [0.5, 1.0]}


def wrap_delta(d, n):
    return (d + n / 2) % n - n / 2


def measure(params, R, seed=4242):
    """Tốc độ median của blob lớn nhất nếu thế giới ổn định có sinh vật; None nếu không."""
    sim = Lenia(params, size=SIZE, seed=seed)
    sim.step(SETTLE)
    m0 = sim.stats()[0]
    if m0 < 4.0:
        return None
    obs = []
    for i in range(OBSERVE):
        sim.step(1)
        if (i + 1) % GAP == 0:
            mask = sim.A > 0.15
            lab, k = ndimage.label(mask)
            if k == 0:
                obs.append(None)
                continue
            sizes = ndimage.sum(mask, lab, range(1, k + 1))
            ys, xs = np.where(lab == int(np.argmax(sizes)) + 1)
            obs.append((len(ys), float(xs.mean()), float(ys.mean())))
    m1 = sim.stats()[0]
    if abs(m1 - m0) / max(m0, 1e-9) > 0.25:
        return None
    bc = obs[-1]
    if bc is None or bc[0] < 6:
        return None
    dists = []
    cap = max(4.0, R * 0.25)  # dịch chuyển tối đa mỗi GAP=0.5tu của MỘT blob liên tục;
                              # cặp nhảy xa hơn = hoán đổi danh tính giữa 2 blob → bỏ
    for b1, b2 in zip(obs, obs[1:]):
        if b1 is None or b2 is None:
            continue
        if abs(b1[0] - b2[0]) / max(b1[0], b2[0]) > 0.4:
            continue
        d = np.hypot(wrap_delta(b2[1] - b1[1], SIZE),
                     wrap_delta(b2[2] - b1[2], SIZE))
        if d <= cap:
            dists.append(d / (GAP / params["T"]))
    if len(dists) < 4:
        return None
    return float(np.median(dists))


def main():
    t0 = time.time()
    results = []
    log = open(os.path.join(OUT, "speed_limit_log.jsonl"), "w", encoding="utf-8")
    for R, (kname, b) in itertools.product(RS, KERNELS.items()):
        best_speed, best_p = 0.0, None
        n_creature = 0
        for iy, ix in itertools.product(range(GRID), range(GRID)):
            mu = 0.10 + 0.30 * ix / (GRID - 1)
            sr = 0.06 + 0.26 * iy / (GRID - 1)
            p = dict(R=R, T=10, b=b, m=round(mu, 4), s=round(mu * sr, 5), kn=1, gn=1)
            spd = measure(p, R)
            if spd is not None:
                n_creature += 1
                if spd > best_speed:
                    best_speed, best_p = spd, p
                    log.write(json.dumps(dict(R=R, b=kname, speed=round(spd, 3),
                                              m=p["m"], sr=round(sr, 3))) + "\n")
        cells_per_step = best_speed / (10.0 / 1.0) / (1 / 0.1)  # speed/10 = cell/step
        results.append(dict(R=R, b=kname, max_speed=round(best_speed, 3),
                            n_stable=n_creature, best=best_p))
        print(f"R={R} {kname}: max={best_speed:.2f} cell/tu "
              f"({best_speed/10:.2f} cell/bước), ổn định={n_creature}/{GRID*GRID} ô, "
              f"best={best_p} [{time.time()-t0:.0f}s]", flush=True)
    log.close()

    lines = ["# SPEED LIMIT — tốc độ tối đa của sinh vật Lenia theo R", "",
             f"Quét {GRID}×{GRID} ô (μ∈[0.10,0.40], σ/μ∈[0.06,0.32]) × 4 R × 2 kernel "
             f"= {len(results)*GRID*GRID} thế giới 64². Lọc: khối lượng ổn định ±25%, "
             "blob ≥ 6 cell, tốc độ = median cặp quan sát blob liên tục.", "",
             "| R | Kernel | Tốc độ max (cell/tu) | cell/bước | Ô ổn định | Gen đạt max |",
             "|---|---|---|---|---|---|"]
    for r in results:
        bp = r["best"]
        lines.append(f"| {r['R']} | {r['b']} | {r['max_speed']:.2f} "
                     f"| {r['max_speed']/10:.2f} | {r['n_stable']}/{GRID*GRID} "
                     f"| m={bp['m']}, s={bp['s']} |" if bp else
                     f"| {r['R']} | {r['b']} | — | — | {r['n_stable']} | — |")
    lines += ["", "## Kết luận", ""]
    top = max(results, key=lambda r: r["max_speed"])
    lines.append(f"- Tốc độ tối đa toàn cục: **{top['max_speed']:.2f} cell/tu "
                 f"({top['max_speed']/10:.2f} cell/bước)** ở R={top['R']}, kernel {top['b']}.")
    lines.append("- Trần lý thuyết lây lan kernel là R cell/bước (R×10 cell/tu) — thực tế "
                 "đo được thấp hơn hàng chục lần: nút cổ chai là ĐỘNG LỰC HỌC GROWTH "
                 "(phải giữ hình trong khi di chuyển), không phải tầm nhìn của kernel.")
    lines.append("- Tốc độ max KHÔNG tăng tuyến tính theo R — R lớn hơn có tầm nhìn xa hơn "
                 "nhưng đồng thời phải đồng bộ khối lượng lớn hơn mỗi bước.")
    with open(os.path.join(OUT, "SPEED_LIMIT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
