# TOKENS.md — máy đo token của lab đêm

Cách đo (ước lượng trung thực, KHÔNG phải số chính xác từ API):
- Mỗi nhịp tim ghi 1 mục: giờ + việc + bytes artifact sinh ra/sửa + ước lượng token.
- Ước lượng token của một nhịp = round((bytes_đọc + bytes_ghi + bytes_lệnh) / 4) + 60_000
  (60k = overhead để đọc context + suy luận + tool calls của một nhịp điển hình).
- Đây là con số THẤP hơn thực tế (không đo được phần suy luận nội tại), dùng để so sánh
  tương đối giữa các nhịp và tổng số "đã đốt" qua đêm.

Mục tiêu cần đốt: 3.000.000.000 tokens (theo lệnh của anh chủ — con số này vượt sức
một đêm; ghi thật để sáng ra anh biết chính xác đốt được bao nhiêu 😄)

---

# NHẬT KÝ ĐỐT

## 01:45 — Khởi công lab đêm (phiên chính)
- Viết: hunter2.py (9.5KB), mapgen.py (7.3KB), night_lab/* (~6KB), sửa mapgen bug
- Chạy: mapgen b1_R13 (2700 sim, 245s), hunter2 1500 trials (nền)
- Ước lượng: ~+180.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~180.000 tokens**

## 02:00 — Phiên chính mở rộng (anh ra lệnh đốt tiếp)
- mapgen b2_R13 (2.704 sim): phát hiện lớn — kernel 2 vỏ nở vùng creature ×2.6 (544→1410)
- QUEUE nới từ 9 lên 13 mục (thêm hunter3 3000 lượt, arena 15 trận, catalog 20 gen, SmoothLife map)
- Nhịp tim đổi giờ chốt 06:30 → 08:00 (CronUpdate)
- Ước lượng: ~+70.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~250.000 tokens**

<!-- Nhịp tim thêm mục dưới đây theo đúng format trên, luôn cập nhật dòng TỔNG cuối file -->
## 02:13 — (nhịp tim #1) Phân tích hunter2 → ANALYSIS.md
- Đọc log.jsonl (177 dòng ~25KB), ghi ANALYSIS.md (~3KB), ghi sổ 4 file (~4KB)
- Ước lượng: ~+62.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~312.000 tokens**
## 02:38 — (nhịp tim #2) mapgen b3_R15
- 2.704 sim / 163s; log ~2KB; ghi sổ ~3KB
- Ước lượng: ~+63.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~375.000 tokens**
## 03:03 — (nhịp tim #3) all_maps.png + PHASES.md
- Ghép ảnh ~100KB PNG + PHASES.md ~2KB + ghi sổ ~3KB
- Ước lượng: ~+65.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~440.000 tokens**
## 03:25 — (nhịp tim #4) SmoothLife + 2 GIF
- Viết smoothlife.py (7.8KB), 1 lần debug công thức, render 2 GIF (~450 steps sim)
- Ước lượng: ~+72.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~512.000 tokens**
## 03:52 — (nhịp tim #5) Chroma mode + verify browser
- Sửa template 7 điểm (~2KB), rebuild playground.html (42.9KB), verify IAB (screenshot + fatal check)
- Ước lượng: ~+68.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~580.000 tokens**
## 04:22 — (nhịp tim #6) Arena 30 lượt + ranking + 6 GIF
- Viết arena.py (8.5KB), 30 trận × 300 bước sim + 6 GIF render
- Ước lượng: ~+75.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~655.000 tokens**
## 04:55 — (nhịp tim #7) SPEED_LIMIT (2 lần chạy × 3.200 sim)
- Viết speed_limit.py (6.5KB), 1 crash fix nhỏ, 1 fix chống artifact, SPEED_LIMIT.md
- Ước lượng: ~+70.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~725.000 tokens**
## 05:18 — (nhịp tim #8) hunter3 dựng + phóng nền
- Viết hunter3.py (3.2KB, tái dùng hunter2.evaluate), smoke + launch
- Ước lượng: ~+64.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~789.000 tokens**
## 05:45 — (nhịp tim #9) Catalog 20 GIF + CATALOG.md
- Viết catalog.py (4.5KB), render 20 GIF (mỗi cái tái lập 250+160 bước) + preview
- Ước lượng: ~+76.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~865.000 tokens**
## 06:08 — (nhịp tim #10) SmoothLife map 576 ô
- Viết smoothmap.py (4.8KB), render map + json
- Ước lượng: ~+66.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~931.000 tokens**
## 08:03 — (nhịp tim #15) Chốt sáng — viết SUMMARY.md
- Tổng kết 12 mục + artifact (~5KB) + ghi sổ
- Ước lượng: ~+80.000 tokens
- **TỔNG ỨỚC LƯỢNG: ~1.010.000 tokens / cả đêm**
