#!/usr/bin/env python3
"""
mapgen — vẽ "bản đồ vũ trụ gen" của Lenia: quét lưới (μ, σ/μ) cho một bộ gen kernel,
nấu canh ở mỗi ô, phân loại ô đó, rồi tô màu ra ảnh PNG.

Phân loại mỗi ô:
  dead    — thế giới chết (khối lượng tan hết / không đủ bụi)
  dust    — chỉ còn bụi li ti (blob < MIN_SIZE)
  static  — cấu trúc ổn định nhưng đứng yên (khiên, ô vuông…)
  drift   — trôi lờ đờ (0.05–0.15 cell/tu)
  creature— có sinh vật di chuyển bền bỉ (≥ 0.15 cell/tu)

Chạy:  python mapgen.py <ten_config>
Config nằm ở đáy file (MAP_CONFIGS).
"""

import json
import os
import sys
import time

import numpy as np
from scipy import ndimage
from PIL import Image, ImageDraw

from lenia import Lenia

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "maps")

SIZE = 64
SETTLE = 90
OBSERVE = 70
GAP = 5
GRID = 52          # số ô mỗi trục
MU_RANGE = (0.10, 0.40)
SR_RANGE = (0.06, 0.32)   # σ/μ

CLASS_COLOR = {
    "dead":     (10, 10, 16),
    "dust":     (38, 34, 52),
    "static":   (44, 62, 110),
    "drift":    (30, 130, 150),
    "creature": (240, 190, 40),
}


def wrap_delta(d, n):
    return (d + n / 2) % n - n / 2


def classify_cell(params, seed=12345):
    sim = Lenia(params, size=SIZE, seed=seed)
    sim.step(SETTLE)
    m0 = sim.stats()[0]
    obs = []  # (world_mass, blob_com) ghi DURING mô phỏng, không phải đo lại khung cuối
    for i in range(OBSERVE):
        sim.step(1)
        if (i + 1) % GAP == 0:
            st = sim.stats()
            obs.append((st[0], quick_blob(sim.A)))
    m_end = obs[-1][0]
    if m_end < 1.0:
        return "dead", 0.0
    last_bc = obs[-1][1]
    if last_bc is None or last_bc[0] < 6:
        return "dust", 0.0
    if abs(m_end - m0) / max(m0, 1) > 0.6:
        return "dust", 0.0
    speeds = []
    for (m1, bc1), (m2, bc2) in zip(obs, obs[1:]):
        if bc1 is None or bc2 is None:
            continue
        s1, x1, y1 = bc1
        s2, x2, y2 = bc2
        if abs(s1 - s2) / max(s1, s2) <= 0.4:
            speeds.append(np.hypot(wrap_delta(x2 - x1, SIZE),
                                   wrap_delta(y2 - y1, SIZE)) / (GAP / params["T"]))
    speed = float(np.median(speeds)) if speeds else 0.0
    if speed < 0.05:
        return "static", 0.0
    if speed < 0.15:
        return "drift", speed
    return "creature", min(speed, 1.0)


def quick_blob(A):
    mask = A > 0.15
    lab, n = ndimage.label(mask)
    if n == 0:
        return None
    sizes = ndimage.sum(mask, lab, range(1, n + 1))
    ys, xs = np.where(lab == int(np.argmax(sizes)) + 1)
    return len(ys), float(xs.mean()), float(ys.mean())


def render_map(grid_cls, grid_spd, cfg_name, cfg, elapsed):
    n = GRID
    scale = 8
    pad = 46
    W = n * scale + pad
    img = Image.new("RGB", (W, W))
    dr = ImageDraw.Draw(img)
    for iy in range(n):
        for ix in range(n):
            cls = grid_cls[iy][ix]
            r, g, b = CLASS_COLOR[cls]
            boost = 1.0 + min(grid_spd[iy][ix], 1.0) * 0.8
            col = (min(int(r * boost), 255), min(int(g * boost), 255),
                   min(int(b * boost), 255))
            dr.rectangle([pad + ix * scale, iy * scale,
                          pad + (ix + 1) * scale - 1, (iy + 1) * scale - 1], fill=col)
    dr.text((pad + 4, n * scale + 6),
            f"mu ({MU_RANGE[0]}-{MU_RANGE[1]}) ->   s/m ↓ ({SR_RANGE[0]}-{SR_RANGE[1]})   "
            f"{cfg_name}  R={cfg['R']} b={cfg['b']}  {elapsed:.0f}s", fill=(200, 205, 220))
    # trục μ dưới
    for frac, lab in [(0, "0.10"), (0.5, "0.25"), (1, "0.40")]:
        x = pad + int(frac * (n * scale - 1))
        dr.text((x - 8, n * scale + 20), lab, fill=(140, 148, 170))
    path = os.path.join(OUT, f"map_{cfg_name}.png")
    img.save(path)
    return path


MAP_CONFIGS = {
    "b1_R13":  dict(R=13, b=[1.0]),
    "b2_R13":  dict(R=13, b=[0.5, 1.0]),
    "b3_R15":  dict(R=15, b=[1 / 6, 0.5, 1.0]),
}


def main():
    cfg_name = sys.argv[1] if len(sys.argv) > 1 else "b1_R13"
    cfg = MAP_CONFIGS[cfg_name]
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    gcls = [[None] * GRID for _ in range(GRID)]
    gspd = [[0.0] * GRID for _ in range(GRID)]
    counts = {}
    for iy in range(GRID):
        sr = SR_RANGE[0] + (SR_RANGE[1] - SR_RANGE[0]) * iy / (GRID - 1)
        for ix in range(GRID):
            mu = MU_RANGE[0] + (MU_RANGE[1] - MU_RANGE[0]) * ix / (GRID - 1)
            params = dict(R=cfg["R"], T=10, b=cfg["b"], m=round(mu, 4),
                          s=round(mu * sr, 5), kn=1, gn=1)
            cls, spd = classify_cell(params)
            gcls[iy][ix], gspd[iy][ix] = cls, spd
            counts[cls] = counts.get(cls, 0) + 1
        print(f"hàng {iy + 1}/{GRID} xong ({time.time() - t0:.0f}s) {counts}", flush=True)
    path = render_map(gcls, gspd, cfg_name, cfg, time.time() - t0)
    summary = dict(config=cfg_name, params=cfg, grid=GRID,
                   counts=counts, seconds=round(time.time() - t0, 1), image=os.path.basename(path))
    with open(os.path.join(OUT, f"map_{cfg_name}.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print("DONE", json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
