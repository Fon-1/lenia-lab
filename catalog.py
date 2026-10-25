#!/usr/bin/env python3
"""
catalog.py — chọn 20 gen đẹp nhất từ kho 3 đợt săn (discoveries, discoveries2, discoveries3),
tái lập từng sinh vật từ seed, cắt khối, render GIF chuẩn (scale 3, 160 bước, palette ice).

Tiêu chí chọn: speed ≤ 2 cell/tu (đủ bơi để thấy, đủ chậm để soi), ưu tiên "single"
(cá thể đơn), đa dạng gen (không lấy 20 con gần trùng tham số).

Chạy: python catalog.py → out/catalog/*.gif + CATALOG.md
"""

import json
import os

import numpy as np

from lenia import Lenia, render_gif
from hunter2 import largest_blob

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "catalog")
SOURCES = [
    ("h1", os.path.join(HERE, "out", "discoveries", "log.jsonl")),
    ("h2", os.path.join(HERE, "out", "discoveries2", "log.jsonl")),
    ("h3", os.path.join(HERE, "out", "discoveries3", "log.jsonl")),
]
N_PICK = 20


def main():
    os.makedirs(OUT, exist_ok=True)
    pool, seen = [], set()
    for src, path in SOURCES:
        if not os.path.exists(path):
            continue
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            p = r["params"]
            key = (p["R"], tuple(p["b"]), round(p["m"], 3), round(p["s"], 3))
            if key in seen or r.get("speed", 0) > 2.0:
                continue
            seen.add(key)
            pool.append(dict(src=src, p=p, seed=r["seed"], speed=r["speed"],
                             tag=r.get("tag", "?"), mass=r.get("mass", 0)))
    # ưu tiên single, rồi speed cao; ép đa dạng: không lấy 2 gen gần trùng (R, số vỏ, m, s)
    pool.sort(key=lambda c: (c["tag"] != "single", -c["speed"]))
    picked = []
    for c in pool:
        if len(picked) >= N_PICK:
            break
        p = c["p"]
        if any(x["p"]["R"] == p["R"] and len(x["p"]["b"]) == len(p["b"])
               and abs(x["p"]["m"] - p["m"]) < 0.03
               and abs(x["p"]["s"] - p["s"]) < 0.01 for x in picked):
            continue
        picked.append(c)

    lines = ["# CATALOG — 20 gen đẹp nhất từ kho 1222 gen của 3 đợt săn", "",
             "| # | Nguồn | Gen (R · b · m · s) | Speed (cell/tu) | Loại | GIF |",
             "|---|---|---|---|---|---|"]
    for i, c in enumerate(picked, 1):
        p, seed = c["p"], c["seed"]
        sim = Lenia(p, size=96, seed=seed)
        sim.step(250)
        snap = largest_blob(sim.A, p["R"] + 2)
        if snap is None or min(snap.shape) < 4:
            continue
        side = max(64, 2 * max(snap.shape))
        w = Lenia(p, size=side, cells=np.zeros((1, 1)))
        top = (side - snap.shape[0]) // 2
        left = (side - snap.shape[1]) // 2
        w.A[top:top + snap.shape[0], left:left + snap.shape[1]] = snap
        bstr = "+".join(f"{x:g}" for x in p["b"])
        fname = f"cat_{i:02d}_R{p['R']}_m{p['m']:.3f}.gif"
        render_gif(w, os.path.join(OUT, fname), 160, scale=3, palette="ice",
                   caption=f"R={p['R']} b={bstr} m={p['m']:.3f} s={p['s']:.3f} v={c['speed']:.2f}")
        lines.append(f"| {i} | {c['src']}/{c['tag']} | R={p['R']} · b={bstr} · "
                     f"m={p['m']} · s={p['s']} | {c['speed']:.2f} | {c['tag']} | {fname} |")
        print(f"[{i:02d}/{N_PICK}] {fname} v={c['speed']:.2f}", flush=True)
    with open(os.path.join(OUT, "CATALOG.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
