#!/usr/bin/env python3
"""
SmoothLife — "Game of Life" liên tục của Stephan Rafler (2011), họ hàng của Lenia.

Khác Lenia: SmoothLife có HAI miền tích chập —
  m = trung bình khối lượng trong ĐĨA trong (bán kính ri)
  n = trung bình khối lượng trong VÀNH NGOÀI (ri < d <= ro)
và luật chuyển tiếp bằng sigmoid mượt, dạng TỔNG theo ngữ nghĩa Life:
  s(n, m) = w(m)·sigma2(n, d1, d2) + (1 − w(m))·sigma2(n, b1, b2)
  (ô sống m>0.5 → dải survival [d1,d2]; ô chết m<0.5 → dải birth [b1,b2];
   w(m) = sigmoid(m, 0.5, alpha_m) là cầu trộn mượt)
  x' = clip(x + dt * (2*s - 1), 0, 1)

Bộ tham số kinh điển cho glider:
  b1=0.278 b2=0.365 d1=0.261 d2=0.445 alpha_n=0.028 alpha_m=0.147 dt=0.115 ri=3 ro=10

Chạy:
  python smoothlife.py soup    # canh ngẫu nhiên -> out/smoothlife_soup.gif
  python smoothlife.py glider  # canh -> đợi -> cắt con bơi -> out/smoothlife_glider.gif
"""

import os
import sys

import numpy as np

from lenia import build_lut, frame_rgb

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

P = dict(b1=0.278, b2=0.365, d1=0.261, d2=0.445,
         alpha_n=0.028, alpha_m=0.147, dt=0.115, ri=3, ro=10)


def sigmoid1(x, a, alpha):
    return 1.0 / (1.0 + np.exp(-4.0 * (x - a) / alpha))


def sigmoid2(x, a, b, alpha):
    return sigmoid1(x, a, alpha) * (1.0 - sigmoid1(x, b, alpha))


def kernel_masks(size, ri, ro):
    mid = size // 2
    ax = np.arange(size) - mid
    XX, YY = np.meshgrid(ax, ax)
    d = np.sqrt(XX * XX + YY * YY)
    disk = (d <= ri).astype(np.complex128)
    ring = ((d > ri) & (d <= ro)).astype(np.complex128)
    disk = np.roll(np.roll(disk, -mid, axis=0), -mid, axis=1)
    ring = np.roll(np.roll(ring, -mid, axis=0), -mid, axis=1)
    return disk / disk.sum(), ring / ring.sum()


class SmoothLife:
    def __init__(self, size=96, seed=7, density=0.5, **over):
        self.p = dict(P)
        self.p.update(over)
        self.size = size
        self.rng = np.random.default_rng(seed)
        self.A = (self.rng.random((size, size)) < density).astype(np.float64)
        kd, kr = kernel_masks(size, self.p["ri"], self.p["ro"])
        self.KD = np.fft.fft2(kd)
        self.KR = np.fft.fft2(kr)
        self.gen = 0

    def step(self, n=1):
        p = self.p
        an, am = p["alpha_n"], p["alpha_m"]
        for _ in range(n):
            FA = np.fft.fft2(self.A)
            m = np.fft.ifft2(FA * self.KD).real
            nn = np.fft.ifft2(FA * self.KR).real
            w = sigmoid1(m, 0.5, am)  # trọng số "đang sống" mượt theo m
            s = (w * sigmoid2(nn, p["d1"], p["d2"], an)
                 + (1.0 - w) * sigmoid2(nn, p["b1"], p["b2"], an))
            self.A = np.clip(self.A + p["dt"] * (2.0 * s - 1.0), 0.0, 1.0)
            self.gen += 1

    def largest_blob(self, pad=10):
        from scipy import ndimage
        mask = self.A > 0.3
        lab, k = ndimage.label(mask)
        if k == 0:
            return None
        sizes = ndimage.sum(mask, lab, range(1, k + 1))
        ys, xs = np.where(lab == int(np.argmax(sizes)) + 1)
        y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, self.size)
        x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, self.size)
        return self.A[y0:y1, x0:x1]


def render(sim, path, steps, scale=4, stride=1):
    lut = build_lut("ice")
    frames = [frame_rgb(sim.A, scale, lut)]
    for _ in range(steps):
        sim.step(1)
        frames.append(frame_rgb(sim.A, scale, lut))
        if len(frames) >= 400:
            break
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=100, loop=0, optimize=True)
    return len(frames)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "soup"
    os.makedirs(OUT, exist_ok=True)
    if mode == "soup":
        sim = SmoothLife(size=96, seed=7)
        sim.step(300)
        n = render(sim, os.path.join(OUT, "smoothlife_soup.gif"), 200)
        print(f"soup: mass sau settle = {sim.A.sum():.0f}, GIF {n} khung", flush=True)
    else:
        sim = SmoothLife(size=128, seed=11)
        sim.step(700)  # đợi canh tự tổ chức thành glider
        crop = sim.largest_blob(pad=12)
        if crop is None or min(crop.shape) < 24:
            print("không tìm thấy blob đủ lớn", flush=True)
            return
        side = max(64, 2 * max(crop.shape))
        sim2 = SmoothLife(size=side, seed=3)
        sim2.A[:] = 0.0
        top = (side - crop.shape[0]) // 2
        left = (side - crop.shape[1]) // 2
        sim2.A[top:top + crop.shape[0], left:left + crop.shape[1]] = crop
        n = render(sim2, os.path.join(OUT, "smoothlife_glider.gif"), 250)
        print(f"glider: crop {crop.shape}, GIF {n} khung, mass={sim2.A.sum():.1f}", flush=True)


if __name__ == "__main__":
    main()
