#!/usr/bin/env python3
"""
arena.py — đấu vòng tròn giữa các loài Lenia.

Mỗi cặp đấu 2 LƯỢT để công bằng: lượt "sân nhà A" (dùng kernel/growth của A) và
lượt "sân nhà B". Hai sinh vật đặt ở hai bên thế giới 128², chạy 300 bước.

Chấm điểm mỗi lượt theo khối lượng cuối của từng phe so với khối lượng đầu
(khối lượng phe = tổng A trong nửa thế giới của phe đó):
  giữ ≥60%      → "giữ vững"
  <30%          → "tan"
  tổng ×1.3     → "bùng nổ"
  tổng <0.5×    → "sụp đổ"
Xếp hạng: số lượt "giữ vững" / tổng lượt của loài (5 đối thủ × 2 sân).

Chạy: python arena.py   → out/arena/*.gif + out/arena/RANKING.md
"""

import itertools
import json
import os

import numpy as np

from lenia import Lenia, load_species, make_params, rle2arr, build_lut, frame_rgb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "arena")
SPECIES = ["O2u", "OG2g", "O4s", "2PG1v", "2S1f", "S3s"]
SIZE = 128
STEPS = 300
GAP_PX = 30


def place(world, cells, cy, cx):
    h, w = cells.shape
    y0 = int(cy - h / 2) % SIZE
    x0 = int(cx - w / 2) % SIZE
    for dy in range(h):
        for dx in range(w):
            world[(y0 + dy) % SIZE, (x0 + dx) % SIZE] = cells[dy, dx]


def battle(pa, cells_a, pb, cells_b, host):
    """Trả về (kết quả dict, khung GIF chụp dọc đường) — host = 'A' hoặc 'B'."""
    p = dict(pa) if host == "A" else dict(pb)
    sim = Lenia(p, size=SIZE, cells=np.zeros((1, 1)))
    w = sim.A
    wa = cells_a.shape[1]
    wb = cells_b.shape[1]
    cy = SIZE // 2
    xa = GAP_PX // 2 + wa // 2 + 4
    xb = SIZE - 1 - (GAP_PX // 2 + wb // 2 + 4)
    place(w, cells_a, cy, xa)
    place(w, cells_b, cy, xb)
    m_a0 = w[:, : SIZE // 2].sum()
    m_b0 = w[:, SIZE // 2:].sum()

    lut = build_lut("fire" if host == "A" else "ice")
    frames = [frame_rgb(w, 3, lut)]
    for i in range(STEPS):
        sim.step(1)
        if (i + 1) % 2 == 0 and len(frames) < 160:
            frames.append(frame_rgb(w, 3, lut))
    m_a1 = sim.A[:, : SIZE // 2].sum()
    m_b1 = sim.A[:, SIZE // 2:].sum()
    total = (m_a1 + m_b1) / max(m_a0 + m_b0, 1e-9)
    keep_a = m_a1 / max(m_a0, 1e-9)
    keep_b = m_b1 / max(m_b0, 1e-9)
    if total > 1.3:
        verdict = "bùng nổ (hợp nhất/tăng khối)"
    elif total < 0.5:
        verdict = "sụp đổ (cả hai tan)"
    elif keep_a >= 0.6 and keep_b >= 0.6:
        verdict = "cùng sống"
    elif keep_a >= 0.6 and keep_b < 0.3:
        verdict = "A thắng — B tan"
    elif keep_b >= 0.6 and keep_a < 0.3:
        verdict = "B thắng — A tan"
    else:
        verdict = "hỗn chiến, cả hai suy yếu"
    return dict(keep_a=round(keep_a, 2), keep_b=round(keep_b, 2),
                total=round(total, 2), verdict=verdict), frames


def main():
    os.makedirs(OUT, exist_ok=True)
    zoo = {}
    for code in SPECIES:
        d = load_species(code, "code")
        zoo[code] = dict(name=d["name"], p=make_params(d["params"]),
                         cells=rle2arr(d["cells"]))

    results = []
    gifs = []
    for a, b in itertools.combinations(SPECIES, 2):
        for host in ("A", "B"):
            pa, ca = zoo[a]["p"], zoo[a]["cells"]
            pb, cb = zoo[b]["p"], zoo[b]["cells"]
            if host == "B":
                pa, pb = pb, pa
                ca, cb = cb, ca
            res, frames = battle(pa, ca, pb, cb, host)
            res.update(a=a, b=b, host=host)
            results.append(res)
            gifs.append((f"{a}_vs_{b}_{host}", frames,
                         f"{a} vs {b} (san nha {host}) {res['verdict']}"))
        print(f"{a} vs {b}: 2 luot xong", flush=True)

    def drama(r):
        return {"bùng nổ (hợp nhất/tăng khối)": 4, "sụp đổ (cả hai tan)": 4,
                "A thắng — B tan": 3, "B thắng — A tan": 3}.get(r["verdict"], 1)
    gifs.sort(key=lambda g: -drama(next(r for r in results
                                        if f"{r['a']}_vs_{r['b']}_{r['host']}" == g[0])))
    for name, frames, cap in gifs[:6]:
        frames[0].save(os.path.join(OUT, name + ".gif"), save_all=True,
                       append_images=frames[1:], duration=100, loop=0, optimize=True)

    wins = {c: 0 for c in SPECIES}
    games = {c: 0 for c in SPECIES}
    for r in results:
        for side, code in (("a", r["a"]), ("b", r["b"])):
            games[code] += 1
            if r[f"keep_{side}"] >= 0.6:
                wins[code] += 1
    lines = ["# RANKING — Arena Lenia (15 cặp × 2 sân nhà)", "",
             "| Hạng | Loài | Giữ vững / Tổng lượt | Tỉ lệ |",
             "|---|---|---|---|"]
    rank = sorted(SPECIES, key=lambda c: -wins[c] / games[c])
    for i, c in enumerate(rank, 1):
        lines.append(f"| {i} | {c} {zoo[c]['name']} | {wins[c]}/{games[c]} "
                     f"| {wins[c]/games[c]*100:.0f}% |")
    lines += ["", "## Chi tiết từng lượt", "",
              "| A | B | Sân | giữ A | giữ B | tổng | Kết quả |",
              "|---|---|---|---|---|---|---|"]
    for r in results:
        lines.append(f"| {r['a']} | {r['b']} | {r['host']} | {r['keep_a']} "
                     f"| {r['keep_b']} | {r['total']} | {r['verdict']} |")
    with open(os.path.join(OUT, "RANKING.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print("DONE arena:", len(results), "luot; ranking:",
          {c: f"{wins[c]}/{games[c]}" for c in rank}, flush=True)


if __name__ == "__main__":
    main()
