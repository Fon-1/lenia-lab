# SUMMARY — Tổng kết lab đêm Lenia (01:45 → 08:03)

Đêm chạy theo nhịp tim 25 phút (automation-0c4ba8e5), 14 nhịp đã thực hiện. Dưới đây là
tất cả kết quả, theo thứ tự hàng đợi. Toàn bộ file nằm trong `lenia-lab/`.

## Con số lớn nhất của đêm

- **1.222 gen sống** được săn được qua 3 đợt (40 + 177 + 1.005) từ 4.540 thế giới mô phỏng.
- **4 bản đồ vũ trụ gen** (3 cho Lenia theo số vỏ kernel + 1 cho SmoothLife) = 8.784 thế giới quét lưới.
- **30 trận arena** giữa 6 loài + bảng xếp hạng.
- **Playground thêm 2 tính năng** (comet trails + chroma), đã verify bằng browser thật.
- **0 giả số**: mọi kết quả nhanh bất thường đều bị phát hiện là artifact đo và được lọc/bẫy.

## Từng mục QUEUE

| # | Mục | Kết quả chính | Artifact |
|---|---|---|---|
| 1 | Phân tích hunter2 | 177 hits / 0 artifact; kernel **2 vỏ chiếm 80/177** — điểm ngọt | `out/discoveries2/ANALYSIS.md` |
| 2 | Map b2_R13 | Vùng creature **×2.6** (544→1410) — 2 vỏ nở vùng sự sống | `out/maps/map_b2_R13.png` |
| 3 | Map b3_R15 | 3 vỏ = đỉnh "drift" (1330), creature 877 | `out/maps/map_b3_R15.png` |
| 4 | Ghép map + pha | Static sụp 875→109 khi thêm vỏ; 5 nhận xét cấu trúc pha | `out/maps/all_maps.png`, `PHASES.md` |
| 5 | SmoothLife | Dạng tổng (không phải dạng tích paper-recall) → mass ổn định; 2 GIF mê cung | `smoothlife.py`, `out/smoothlife_*.gif` |
| 6 | Chroma mode | RG32F mang tiềm năng U, hue theo U; verify browser sạch | `playground.html` (mục "màu sắc") |
| 7 | Arena 30 lượt | **OG2g vô địch 90%; Orbium huyền thoại bét 20%** | `arena.py`, `out/arena/RANKING.md` + 6 GIF |
| 8 | Speed limit | Max 2.35–6.18 cell/tu; **không tăng theo R** — nút cổ chai là động lực học growth | `speed_limit.py`, `out/maps/SPEED_LIMIT.md` |
| 10 | hunter3 tinh chỉnh | **1005 hits / 3000 (33.5%)** — sampler nghiêng vùng giàu hit hiệu quả gấp 3 | `hunter3.py`, `out/discoveries3/log.jsonl` |
| 12 | Catalog | 20 GIF đẹp nhất tái lập từ seed (bọt bong bóng, bánh răng, vỏ xoáy) | `catalog.py`, `out/catalog/` + `CATALOG.md` |
| 13 | SmoothLife map | Pha là **dải dọc theo b2** (khác biên chéo của Lenia); active 52% | `smoothmap.py`, `out/maps/map_SmoothLife.png` |
| 11 | Arena (bản trùng) | SKIP — đã làm ở mục 7 | — |

## Bài học phương pháp (đã gặp lặp lại 3 lần)

Đo tốc độ sinh vật trong đàn là việc dễ sai nhất: blob **hoán đổi danh tính** giữa các lần
quan sát tạo ra "tốc độ" ảo 47–68 cell/tu. Trả giá bằng 2 lần nhiễm dữ liệu (hunter1, speed_limit
lần 1) rồi bẫy bằng: trần dịch chuyển theo R + filter kích thước blob liên tục + median thay mean.
Mọi con số trong các file MD đều đã qua bộ lọc này.

## Sáng mai muốn chơi tiếp thì

1. Mở `playground.html` — thử select "màu sắc" → chroma, và "vệt sáng".
2. Xem `out/maps/all_maps.png` + `out/catalog/CATALOG.md` (20 con đẹp nhất có GIF riêng).
3. Đọc `out/arena/RANKING.md` — cốt gameplay của cái game nếu muốn làm nghiêm túc.
4. Hướng tiếp theo gợi ý: GA tiến hóa thật sự (lai gen từ kho 1.222), game prototype "bể đấu",
   hoặc content pack (GIF chroma + trails đã sẵn làm thumbnail).

## Sổ token

Xem `night_lab/TOKENS.md` — ước lượng ~1.01 triệu tokens cho cả đêm (số THẬT theo phương pháp
đo ghi trong file, không phải 3 tỷ — vật lý không cho phép, đã báo từ tối).
