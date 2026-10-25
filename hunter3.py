#!/usr/bin/env python3
"""
hunter3 — đợt săn tinh chỉnh 3000 lượt, nghiêng về vùng giàu hit mà ANALYSIS.md chỉ ra:
  b = 1-2 vỏ (2 vỏ chiếm 80/177 hits của hunter2), R ∈ {10,13,16},
  m ∈ [0.19, 0.33], σ/μ ∈ [0.08, 0.20].
Không render GIF (chỉ log) — GIF đẹp để catalog lo riêng.

Chạy: python hunter3.py 3000   → out/discoveries3/log.jsonl
"""

import json
import os
import random
import sys
import time

import numpy as np

from hunter2 import evaluate

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "discoveries3")


def sample_params(rng):
    R = rng.choice([10, 13, 16])
    B = rng.choice([1, 2, 2, 2])
    if B == 1:
        b = [1.0]
    else:
        b = [round(rng.uniform(0.35, 1.0), 2), 1.0]
    m = round(rng.uniform(0.19, 0.33), 4)
    s = round(m * rng.uniform(0.08, 0.20), 4)
    return dict(R=int(R), T=10, b=b, m=m, s=s, kn=1, gn=1)


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    rng = random.Random(999)
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
        log.write(json.dumps(rec, ensure_ascii=False) + "\n")
        log.flush()
        if (i + 1) % 100 == 0:
            print(f"[{i + 1}/{trials}] hits={hits} elapsed={time.time() - t0:.0f}s", flush=True)
    print(f"DONE trials={trials} hits={hits} trong {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
