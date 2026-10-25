# LENIA PETRI 🐙 — evolution pet game chạy thật trên GPU

> Một game nuôi-đấu-lai sinh vật số, trong đó **mỗi con vật là một công thức toán học**
> (automata tế bào liên tục "Lenia", Bert Chan 2018) mô phỏng thật bằng WebGL2 fragment shader.
> Toàn bộ project — game, engine, công cụ nghiên cứu, automation — được xây trong ~1 ngày
> bởi một agent AI (ZCode) chạy qua đêm.

## 🎮 Chơi ngay

Mở **`lenia-petri.html`** bằng Chrome/Edge/Firefox (double-click, không cần server, không asset, không server-side).

- 🍜 **Săn** — rót bể hoang với gen ngẫu nhiên; nếu sự sống tự tổ chức nổi lên, bắt về codex
- ⚔ **Đấu** — creature của bạn đánh trận GPU thật với đối thủ hoang dã, chấm theo % khối lượng
- 🧬 **Lai** — trộn 2 gen thành con mới; con có thể ra huyền thoại hoặc chết non trong bể ươm
- 📤 **Share gen** — xuất creature thành 1 dòng code `LNP1....` gửi bạn bè nhập vào codex
- Mục tiêu: thu thập 30 gen để lên danh hiệu **"Thần Lenia"** · save tự động (localStorage)

**`playground.html`** là bản sandbox cho người muốn vọc gốc: mọi slider gen (μ, σ, R, T,
số vỏ kernel, growth mapping), comet trails, chroma theo trường tiềm năng, tô sinh mầm bằng chuột.

## 🔬 Lab đêm — nghiên cứu tự động

`night_lab/` là hệ thống 15 nhịp cron tự chạy qua đêm: hàng đợi thí nghiệm → ghi journal → sổ token → tổng kết sáng.

Kết quả đêm đầu tiên (chi tiết trong [`night_lab/SUMMARY.md`](night_lab/SUMMARY.md)):

- **2.145 gen sống** săn được từ ~10.500 thế giới mô phỏng (4 đợt hunter, hit-rate 11.8% → 33.5% sau khi tinh chỉnh)
- **4 bản đồ "vũ trụ gen"** (`out/maps/`): kernel 2 vỏ nở vùng sự sống ×2.6; SmoothLife xếp pha dải dọc khác biên chéo của Lenia
- **Arena 30 trận**: Gyrorbium gyrans vô địch 90% — Orbium huyền thoại bét bảng 20%
- **Giới hạn tốc độ**: max 2.35–6.18 cell/tu, không tăng theo R — nút cổ chai là động lực học growth
- Phát hiện phương pháp: đo tốc độ trong đàn phải chống "blob hoán đổi danh tính" (artifact 47–68 cell/tu)

## 🗂 Cấu trúc

```
lenia-petri.html      # GAME v0.2 — chơi được ngay (1 file)
playground.html       # sandbox vọc Lenia gốc (comet trails + chroma)
lenia.py / hunter*.py # mô phỏng + 4 thế hệ máy săn gen (numpy FFT)
arena.py / catalog.py # 30 trận đối đầu / 20 gen đẹp nhất
mapgen.py / smoothmap.py  # bản đồ tham số Lenia & SmoothLife
smoothlife.py         # họ hàng SmoothLife (Rafler 2011)
night_lab/            # nhịp tim cron + QUEUE + journal + sổ token + SUMMARY
ref/                  # animals.json 548 loài gốc + LeniaND.py (thuộc repo chakazul/lenia)
KINHDOANH.md          # kế hoạch itch.io / Steam / content — kỳ vọng minh bạch
```

## 🛠 Kỹ thuật

- Lenia: `A' = clip(A + 1/T·G(K⊗A))`, kernel vỏ đồng tâm `(4f(1-f))⁴`, FFT torus
- GPU: ping-pong **RG32F** (kênh R = trạng thái, G = trường tiềm năng), kernel nén texture 1D,
  vòng lặp tích chập trong fragment shader — 110–120 fps ở N=128–192
- Game loop + economy + codex + share-gen base64 trong 1 file HTML (~1.400 dòng)
- Bẫy đo đạc: trần dịch chuyển theo R + filter blob liên tục + median (chống artifact hoán đổi danh tính)

## 📄 License & nguồn

- Code này: MIT
- Lenia: Bert Wang-Chak Chan, *Complex Systems* 28(3) 2019 — arXiv:1812.05433 · repo gốc [chakazul/lenia](https://github.com/chakazul/lenia) (`ref/` giữ nguyên tín dụng)
- SmoothLife: Stephan Rafler 2011
