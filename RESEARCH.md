# RESEARCH.md — khảo sát repo game/mô phỏng (đợt 1, 10:45)

Phương pháp: GitHub Search API (sort stars) → chọn lọc → đọc source lõi → đánh giá
"rút được gì vào hệ Lenia Petri". Kết quả build: **`particle-life.html`** (GPU, 6 loài).

## Kho repo đã khảo sát

| Repo | ★ | Là gì | Rút được gì |
|---|---|---|---|
| [mxgmn/WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse) | 25.4k | Sinh bitmap/tilemap từ 1 mẫu bằng ràng buộc | **Hàng đợi build**: WFC overlapping-model bằng JS (~200 dòng) → sinh "bản đồ thế giới" cho Petri v0.3 |
| [chrxh/alien](https://github.com/chrxh/alien) | 5.6k | ALIFE mô phỏng trên CUDA, plant/herbivore/carnivore | Ý tưởng: chuỗi dinh dưỡng 3 tầng — Lenia Petri có thể thêm "thức ăn" là gen yếu bị ăn |
| [The-Powder-Toy](https://github.com/The-Powder-Toy/The-Powder-Toy) | 5.4k | Falling-sand desktop kinh điển, C++/SDL | **Hàng đợi build**: falling-sand CPU typed-array (sand/water/stone/fire) — hợp kiến trúc ping-pong sẵn |
| [hunar4321/particle-life](https://github.com/hunar4321/particle-life) | 3.4k | ALife bằng lực hút/đẩy hạt — **đã đọc source lõi** | ✅ ĐÃ BUILD: `particle-life.html` |
| [Chakazul/Lenia](https://github.com/Chakazul/Lenia) | 3.9k | Gốc — đã dùng từ đầu | — |
| [R74nCom/sandboxels](https://github.com/R74nCom/sandboxels) | 472 | Falling-sand in-browser, 500+ phần tử | Tham khảo bảng reaction khi làm sand mode |
| [Slackermanz/VulkanAutomata](https://github.com/Slackermanz/VulkanAutomata) | 391 | CA "multiple-neighbor" Vulkan — visual organic điên rồ | **Cần đọc tiếp**: họ luật tham số hóa kernel lớn — họ hàng trực hệ Lenia, có thể ra preset mới |
| [lenia-org/Lenia-Tutorial](https://github.com/lenia-org/Lenia-Tutorial) | 51 | "From Conway to Lenia" tutorial | Tài liệu dạy tốt cho README giáo dục |

## Particle Life — thuật toán gốc (đã đọc `particle_life.py` của hunar4321)

Toàn bộ "sự sống" nằm trong ~15 dòng:

```
cho mỗi cặp hạt (a, b) với 0 < d < 80px:
    dx = a.pos - b.pos
    F = g / d                       # g = hệ số loài a → loài b (±)
    a.vel += F * dx                 # = g * đơn vị(dx) — độ lớn chỉ phụ thuộc g!
a.vel = (a.vel + force) * 0.5       # ma sát 0.5/frame — chuyển động "dẻo"
pos += vel;  đập tường thì bật lại
```

Ba điều bất ngờ khi đọc:
1. **Lực ~ 1/d** (không phải 1/d²) — chỉ có hướng là theo khoảng cách, độ lớn gần như chỉ
   là `g`: hạt "cảm nhận" đều mọi hạt trong bán kính, xa gần như nhau.
2. **Ma sát lớn** (×0.5) là điều kiện cần — không có nó thì hệ nổ tung, không có cấu trúc.
3. **Không đối xứng là bắt buộc**: g[A][B] ≠ g[B][A] — tính đối xứng cho ra cụm nhàm chán.

Bản GPU của chúng ta (`particle-life.html`): hạt lưu texture RGBA32F ping-pong (xy = vị trí,
zw = vận tốc), loài ở texture R32F riêng (mirror JS để vẽ/paint), ma trận 6×6 uniform,
mỗi fragment quét tất cả hạt (1536 hạt → ~2.4M cặp/frame — GPU nuốt chưa no). UI: ma trận
lực click-đảo-dấu 6×6, 4 preset (Ngẫu nhiên/Tế bào/Chuỗi săn/Đối xứng), vẽ hạt bằng chuột.

## Hàng đợi nghiên cứu/build tiếp

1. Falling-sand CPU (sandboxels/Powder-Toy style) — 300 dòng, chơi được ngay
2. WFC overlapping JS — sinh map từ sample
3. Đọc sâu Slackermanz shaders — họ luật tham số (nhiều "vỏ" kernel lớn, họ hàng Lenia)
4. alien: mô hình 3 tầng dinh dưỡng → Lenia Petri v0.3 "chuỗi thức ăn"
