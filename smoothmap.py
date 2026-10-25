#!/usr/bin/env python3
"""
smoothmap.py — bản đồ tham số của SmoothLife: quét lưới 24×24 trên (b1, b2),
các tham số khác cố định theo bộ kinh điển (d1=0.261, d2=0.445, ri=3, ro=10, dt=0.115).

Phân loại mỗi ô bằng động lực học sau settle:
  dead     — thế giới chết (mass < 2)
  frozen   — cấu trúc đứng im (activity trung bình mỗi cell mỗi bước ≤ 2e-4)
  active   — "khí glider": mass ổn định + activity cao (đàn sinh vật bơi)
  shifting — mass đang trôi/đổi (chưa ổn định trong cửa sổ quan sát)

Chạy: python smoothmap.py → out/maps/map_SmoothLife.png + map_SmoothLife.json
"""

import itertools
import json
import os
import time

import numpy as np
from PIL import Image, ImageDraw

from smoothlife import SmoothLife

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "maps")

GRID = 24
B1_RANGE = (0.25, 0.32)
B2_RANGE = (0.35, 0.42)
SETTLE = 250
OBSERVE = 100

COLOR = {"dead": (10, 10, 16), "frozen": (44, 62, 110),
         "active": (240, 190, 40), "shifting": (30, 130, 150)}


def classify(b1, b2, seed=777):
    sim = SmoothLife(size=64, seed=seed, b1=b1, b2=b2)
    sim.step(SETTLE)
    m0 = sim.A.sum()
    if m0 < 2.0:
        return "dead", 0.0
    act = 0.0
    for i in range(OBSERVE):
        prev = sim.A
        sim.step(1)
        act += float(np.abs(sim.A - prev).sum())
    m1 = sim.A.sum()
    activity = act / (OBSERVE * 64 * 64)
    if abs(m1 - m0) / max(m0, 1e-9) > 0.35:
        return "shifting", activity
    if activity > 2e-4:
        return "active", activity
    return "frozen", activity


def main():
    t0 = time.time()
    gcls = [[None] * GRID for _ in range(GRID)]
    gact = [[0.0] * GRID for _ in range(GRID)]
    counts = {}
    for iy, ix in itertools.product(range(GRID), range(GRID)):
        b1 = B1_RANGE[0] + (B1_RANGE[1] - B1_RANGE[0]) * iy / (GRID - 1)
        b2 = B2_RANGE[0] + (B2_RANGE[1] - B2_RANGE[0]) * ix / (GRID - 1)
        cls, act = classify(round(b1, 4), round(b2, 4))
        gcls[iy][ix], gact[iy][ix] = cls, act
        counts[cls] = counts.get(cls, 0) + 1
        if ix == GRID - 1:
            print(f"hàng {iy + 1}/{GRID}: {counts} [{time.time() - t0:.0f}s]", flush=True)

    scale, pad = 8, 46
    img = Image.new("RGB", (GRID * scale + pad, GRID * scale + pad + 30))
    dr = ImageDraw.Draw(img)
    for iy in range(GRID):
        for ix in range(GRID):
            r, g, b = COLOR[gcls[iy][ix]]
            boost = 1.0 + min(gact[iy][ix] * 4000, 1.0) * 0.7
            dr.rectangle([pad + ix * scale, iy * scale,
                          pad + (ix + 1) * scale - 1, (iy + 1) * scale - 1],
                         fill=(min(int(r * boost), 255), min(int(g * boost), 255),
                               min(int(b * boost), 255)))
    dr.text((pad + 4, GRID * scale + 4),
            f"b1 ({B1_RANGE[0]}-{B1_RANGE[1]}) v ->   b2 ({B2_RANGE[0]}-{B2_RANGE[1]}) >   "
            f"vang=active, ngoc=shifting, xanh dam=frozen, den=dead", fill=(200, 205, 220))
    dr.text((pad + 4, GRID * scale + 18),
            f"SmoothLife (d1=0.261 d2=0.445 ri=3 ro=10 dt=0.115)  {time.time() - t0:.0f}s",
            fill=(140, 148, 170))
    img.save(os.path.join(OUT, "map_SmoothLife.png"))
    summary = dict(counts=counts, seconds=round(time.time() - t0, 1))
    with open(os.path.join(OUT, "map_SmoothLife.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print("DONE", json.dumps(counts), flush=True)


if __name__ == "__main__":
    main()
