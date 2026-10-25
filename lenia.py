#!/usr/bin/env python3
"""
Lenia - continuous cellular automata ("natural artificial life")
Bert Wang-Chak Chan, arXiv:1812.05433 / Complex Systems 28(3) 2019.

Update rule:
    U = K (x) A                      potential = normalized kernel convolved with world
    A' = clip(A + (1/T) * G(U), 0, 1)  growth mapping applied once per time step dt=1/T

Kernel K: radial, built from B concentric shells. With r = d/R in [0,1]:
    shell j = floor(B*r),  weight b[j],  core applied to fractional part f = B*r - j
    kn=1 quad4 : (4f(1-f))^4          kn=2 bump4: exp(4 - 1/(f(1-f)))
Growth G (gn): 1 quad4: max(0,1-(u-m)^2/(9s^2))^4*2-1   2 gauss: exp(-(u-m)^2/(2s^2))*2-1
                3 step  : |u-m| <= s  -> +1 else -1

Usage:
    python lenia.py --species O2u --steps 200 --out out/orbium.gif
    python lenia.py --soup --params m=0.15,s=0.015,R=13,T=10,b=1 --steps 800 --out out/soup.gif
    python lenia.py --zoo            # render the curated set into out/
"""

import argparse
import json
import os
import re
import sys
from fractions import Fraction

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ANIMALS_PATH = os.path.join(HERE, "ref", "animals.json")

# ---------------------------------------------------------------- RLE codec
# Alphabet from the reference implementation: '.'/'b'=0, 'o'=255,
# single 'A'..'X' = 1..24, two chars 'pA'..'yX' = 25..255. Digits = run count,
# '$' separates rows, '!' terminates.

_DIM_DELIMS = {"$"}  # 2D only here


def ch2val(c):
    if c in ".b":
        return 0
    if c == "o":
        return 255
    if len(c) == 1:
        return ord(c) - ord("A") + 1
    return (ord(c[0]) - ord("p")) * 24 + (ord(c[1]) - ord("A") + 25)


def rle2arr(st):
    rows, row = [], []
    last, count = "", ""
    for ch in st.rstrip("!") + "$":
        if ch.isdigit():
            count += ch
        elif ch in "pqrstuvwxy":
            last = ch
        elif ch == "$":
            if count:
                row.extend([ch2val(last or ".") / 255] * int(count))
            rows.append(row)
            row, last, count = [], "", ""
        else:
            val = ch2val(last + ch) / 255
            row.extend([val] * (int(count) if count else 1))
            last, count = "", ""
    w = max(len(r) for r in rows)
    return np.asarray([r + [0.0] * (w - len(r)) for r in rows], dtype=np.float64)


# ---------------------------------------------------------------- parameters

def parse_b(st):
    """b='1/2,1' -> [0.5, 1.0]"""
    if isinstance(st, (list, tuple)):
        return [float(Fraction(str(v))) for v in st]
    return [float(Fraction(s.strip())) for s in str(st).split(",")]


def parse_overrides(items):
    out = {}
    for item in items or []:
        k, v = item.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def load_species(animal, key):
    data = json.load(open(ANIMALS_PATH, encoding="utf-8"))
    matches = [d for d in data if d.get(key) == animal and "params" in d]
    if not matches:
        sys.exit(f"no species with {key}={animal!r} in animals.json")
    return matches[0]


def make_params(base=None, **over):
    p = dict(R=13, T=10, b=[1.0], m=0.15, s=0.015, kn=1, gn=1)
    if base:
        p.update(R=int(base["R"]), T=int(base["T"]), b=parse_b(base["b"]),
                 m=float(base["m"]), s=float(base["s"]),
                 kn=int(base.get("kn", 1)), gn=int(base.get("gn", 1)))
    for k, v in over.items():
        if k == "b":
            p["b"] = parse_b(v)
        elif k in ("R", "T", "kn", "gn"):
            p[k] = int(v)
        elif k in ("m", "s"):
            p[k] = float(v)
        else:
            raise SystemExit(f"unknown param {k!r} (use R,T,b,m,s,kn,gn)")
    if max(p["b"]) > 1 or min(p["b"]) < 0:
        raise SystemExit("b shell weights must be in [0,1]")
    return p


# ---------------------------------------------------------------- simulation

def kernel_shell(R, size, b, kn):
    """Radial kernel on a size x size torus, wrapped for FFT convolution."""
    mid = size // 2
    ax = np.arange(size) - mid
    XX, YY = np.meshgrid(ax, ax)
    r = np.sqrt(XX * XX + YY * YY) / R

    B = len(b)
    Br = B * r
    j = np.minimum(np.floor(Br).astype(int), B - 1)
    f = np.clip(Br - np.floor(Br), 1e-9, 1 - 1e-9)
    if kn == 1:
        core = (4 * f * (1 - f)) ** 4
    elif kn == 2:
        core = np.exp(4 - 1 / (f * (1 - f)))
    elif kn == 3:
        core = (np.clip(f, 0, 1) >= 0.25) & (np.clip(f, 0, 1) <= 0.75)
        core = core.astype(float)
    else:
        raise SystemExit(f"unsupported kn={kn}")
    k = (r < 1) * core * np.asarray(b)[j]
    k = np.roll(np.roll(k, -mid, axis=0), -mid, axis=1)
    return k


def growth(n, m, s, gn):
    if gn == 1:
        return np.maximum(0, 1 - (n - m) ** 2 / (9 * s ** 2)) ** 4 * 2 - 1
    if gn == 2:
        return np.exp(-((n - m) ** 2) / (2 * s ** 2)) * 2 - 1
    if gn == 3:
        return (np.abs(n - m) <= s) * 2 - 1
    raise SystemExit(f"unsupported gn={gn}")


class Lenia:
    def __init__(self, params, size=96, cells=None, seed=None):
        self.p = params
        self.size = size
        self.gen = 0
        self.rng = np.random.default_rng(seed)
        self.A = np.zeros((size, size))
        if cells is not None and cells.size:
            h, w = cells.shape
            if h > size or w > size:
                raise SystemExit(f"species {w}x{h} does not fit in {size}x{size} world, increase --size")
            top, left = (size - h) // 2, (size - w) // 2
            self.A[top:top + h, left:left + w] = cells
        elif cells is None:
            self.A = (self.rng.random((size, size)) < 0.5).astype(float)
        self._rebuild_kernel()

    def _rebuild_kernel(self):
        k = kernel_shell(self.p["R"], self.size, self.p["b"], self.p["kn"])
        self.KF = np.fft.fft2(k / k.sum())

    def step(self, n=1):
        dt = 1.0 / self.p["T"]
        for _ in range(n):
            U = np.fft.ifft2(np.fft.fft2(self.A) * self.KF).real
            self.A = np.clip(self.A + dt * growth(U, self.p["m"], self.p["s"], self.p["gn"]), 0, 1)
            self.gen += 1

    def stats(self):
        mass = self.A.sum()
        ys, xs = np.indices(self.A.shape)
        if mass < 1e-9:
            return mass, 0.0, 0.0
        return mass, (self.A * xs).sum() / mass, (self.A * ys).sum() / mass

    def track_speed(self, steps):
        """displacement per time unit, averaged over a window"""
        m0, x0, y0 = self.stats()
        hist = []
        for i in range(steps):
            self.step(1)
            if i % max(1, self.p["T"] // 10) == 0:
                _, x, y = self.stats()
                hist.append((x, y))
        if len(hist) < 2:
            return 0.0
        (xa, ya), (xb, yb) = hist[0], hist[-1]
        t = (len(hist) - 1) * max(1, self.p["T"] // 10) / self.p["T"]
        d = np.hypot((xb - xa + self.size / 2) % self.size - self.size / 2,
                     (yb - ya + self.size / 2) % self.size - self.size / 2)
        return d / max(t, 1e-9)


# ---------------------------------------------------------------- rendering

PALETTES = {
    "ice":   [(2, 3, 12), (10, 50, 130), (0, 190, 220), (225, 250, 255)],
    "fire":  [(8, 2, 2), (140, 20, 10), (255, 140, 0), (255, 245, 200)],
    "jade":  [(2, 8, 4), (6, 90, 50), (80, 220, 120), (230, 255, 235)],
    "mono":  [(0, 0, 0), (110, 110, 110), (200, 200, 200), (255, 255, 255)],
}


def build_lut(name):
    stops = PALETTES[name]
    xs = np.linspace(0, 1, 256)
    lut = np.zeros((256, 3))
    n = len(stops) - 1
    for i, x in enumerate(xs):
        pos = x * n
        k = min(int(pos), n - 1)
        f = pos - k
        lut[i] = [(1 - f) * stops[k][c] + f * stops[k + 1][c] for c in range(3)]
    return lut


def frame_rgb(A, scale, lut, caption=None):
    idx = (np.clip(A, 0, 1) * 255).astype(np.uint8)
    img = Image.fromarray(idx).resize((A.shape[1] * scale, A.shape[0] * scale), Image.NEAREST)
    # map grayscale indices through the palette LUT
    lut8 = lut.astype(np.uint8)
    flat = np.asarray(img).reshape(-1)
    mapped = lut8[flat].reshape(img.size[1], img.size[0], 3)
    if caption:
        bar = 22
        canvas = np.zeros((img.size[1] + bar, img.size[0], 3), dtype=np.uint8)
        canvas[:img.size[1]] = mapped
        im = Image.fromarray(canvas)
        ImageDraw.Draw(im).text((8, img.size[1] + 5), caption, fill=(210, 215, 230))
        return im
    return Image.fromarray(mapped)


def render_gif(sim, path, steps, scale=4, palette="ice", caption=None, every=None):
    lut = build_lut(palette)
    T = sim.p["T"]
    stride = every if every is not None else max(1, T // 10)
    frames = [frame_rgb(sim.A, scale, lut, caption)]
    for i in range(steps):
        sim.step(1)
        if (i + 1) % stride == 0:
            frames.append(frame_rgb(sim.A, scale, lut, caption))
        if len(frames) >= 400:
            break
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=100, loop=0, optimize=True)
    return len(frames), sim.gen


# ---------------------------------------------------------------- zoo / cli

ZOO = [
    ("O2u",  "ice",  200, 96,  4, "Orbium unicaudatus - the classic glider"),
    ("OG2g", "ice",  200, 96,  4, "Gyrorbium gyrans - rotating orb"),
    ("2PG1v", "fire", 200, 96,  4, "Gyropteron serratus velox - fast spinner"),
    ("2S1f", "jade", 240, 112, 4, "Scutium serratus fluens - 4-shell kernel"),
    ("~S2p", "mono", 300, 96,  4, "Discutium pachus - different kernel+growth"),
    ("S3s",  "ice",  240, 96,  4, "Triscutium solidus - stable oscillator"),
]


def cmd_species(args):
    d = load_species(args.species, "code" if len(args.species) <= 4 else "name")
    p = make_params(d["params"])
    cells = rle2arr(d["cells"])
    sim = Lenia(p, size=args.size, cells=cells, seed=args.seed)
    if args.mass_stats:
        m, x, y = sim.stats()
        print(f"loaded {d.get('name')}: world {args.size}x{args.size}, mass={m:.1f}, "
              f"R={p['R']} T={p['T']} b={p['b']} m={p['m']} s={p['s']} kn={p['kn']} gn={p['gn']}")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    nf, gen = render_gif(sim, args.out, args.steps, args.scale, args.palette,
                         caption=f"{d.get('code','')} {d.get('name','')}" if args.caption else None,
                         every=args.every)
    speed = sim.track_speed(args.speed_window) if args.speed else None
    print(f"wrote {args.out}: {nf} frames, gen={gen}"
          + (f", speed={speed:.3f} cell/time-unit" if speed is not None else ""))


def cmd_soup(args):
    p = make_params(**parse_overrides(args.params))
    sim = Lenia(p, size=args.size, seed=args.seed)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    nf, gen = render_gif(sim, args.out, args.steps, args.scale, args.palette,
                         caption="random soup, m=%.3f s=%.3f" % (p["m"], p["s"]) if args.caption else None,
                         every=args.every)
    print(f"wrote {args.out}: {nf} frames, gen={gen}, final mass={sim.stats()[0]:.0f}")


def cmd_zoo(args):
    outdir = os.path.join(HERE, "out")
    os.makedirs(outdir, exist_ok=True)
    for code, pal, steps, size, scale, label in ZOO:
        d = load_species(code, "code")
        p = make_params(d["params"])
        sim = Lenia(p, size=size, cells=rle2arr(d["cells"]), seed=args.seed)
        path = os.path.join(outdir, f"{re.sub(r'[^A-Za-z0-9]+', '_', d.get('name', code))}.gif")
        nf, gen = render_gif(sim, path, steps, scale, pal, caption=f"{code}  {d.get('name','')}")
        print(f"{code:6s} -> {os.path.basename(path):44s} {nf:3d} frames gen={gen}")


def main():
    ap = argparse.ArgumentParser(description="Lenia continuous cellular automata")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("species", help="simulate a named species")
    sp.add_argument("species", help="species code (e.g. O2u) or name")
    sp.add_argument("-o", "--out", default="out/species.gif")
    sp.add_argument("--steps", type=int, default=200)
    sp.add_argument("--size", type=int, default=96)
    sp.add_argument("--scale", type=int, default=4)
    sp.add_argument("--palette", default="ice", choices=list(PALETTES))
    sp.add_argument("--every", type=int, default=None, help="capture a frame every N steps")
    sp.add_argument("--seed", type=int, default=None)
    sp.add_argument("--caption", action="store_true")
    sp.add_argument("--speed", action="store_true")
    sp.add_argument("--speed-window", type=int, default=100)
    sp.set_defaults(func=cmd_species, mass_stats=True)

    so = sub.add_parser("soup", help="random soup with given params")
    so.add_argument("-o", "--out", default="out/soup.gif")
    so.add_argument("--params", nargs="*", default=["m=0.15", "s=0.015", "R=13", "T=10", "b=1"])
    so.add_argument("--steps", type=int, default=800)
    so.add_argument("--size", type=int, default=128)
    so.add_argument("--scale", type=int, default=3)
    so.add_argument("--palette", default="ice", choices=list(PALETTES))
    so.add_argument("--every", type=int, default=None)
    so.add_argument("--seed", type=int, default=7)
    so.add_argument("--caption", action="store_true")
    so.set_defaults(func=cmd_soup)

    zz = sub.add_parser("zoo", help="render curated species set")
    zz.add_argument("--seed", type=int, default=None)
    zz.set_defaults(func=cmd_zoo)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
