# QUEUE — hàng đợi thí nghiệm đêm nay (làm TỪ TRÊN XUỐNG, một mục mỗi nhịp)

## 1. [x] DONE (02:13, nhịp tim #1) Phân tích hunter2 1500 trials
- 177 hits, 0 artifact. Colony 127 / single 50. Kernel 2 vỏ chiếm 80/177 — "điểm ngọt".
  μ=0.256±0.077, σ/μ=0.131±0.045. Top speed 5.71 cell/tu (colony, R=10 b=1 m=0.326).
  Chi tiết: out/discoveries2/ANALYSIS.md

## 2. [x] DONE (02:00, phiên chính) mapgen config b2_R13 (kernel 2 vỏ)
- Kết quả lớn: creature 544 → **1410** (×2.6), static 875 → 109 — kernel 2 vỏ nở vùng sống động
  hơn hẳn. Map: out/maps/map_b2_R13.png. So sánh chi tiết nằm ở mục 4.

## 3. [x] DONE (02:38, nhịp tim #2) mapgen config b3_R15 (kernel 3 vỏ)
- creature 877, drift 1330 (cao nhất), static 163, dead 333. Chuỗi 3 vỏ: creature 544→1410→877,
  drift 1010→892→1330 — 2 vỏ đỉnh "creature", 3 vỏ đỉnh "trôi chậm". Map: out/maps/map_b3_R15.png

## 4. [x] DONE (03:03, nhịp tim #3) Ghép bộ 3 bản đồ
- out/maps/all_maps.png (3 tầng, kèm số liệu mỗi config) + out/maps/PHASES.md (5 nhận xét pha).
  Đắt nhất: static sụp 875→109 khi thêm vỏ thứ 2; 3 vỏ đẩy pha sang drift.

## 5. [x] DONE (03:25, nhịp tim #4) SmoothLife — mô phỏng Python
- smoothlife.py hoạt động (dạng tổng, mass ổn định 3830/600 bước). 2 GIF: smoothlife_soup.gif
  (mê cung giun), smoothlife_glider.gif (sinh vật mê cung lớn — glider đơn cần tham số khác, xem mục 13).

## 6. [x] DONE (03:52, nhịp tim #5) Chroma mode cho playground
- State texture R32F→RG32F (G mang tiềm năng U), dispfs thêm hsv2rgb + uChroma, brush giữ nguyên U,
  UI thêm select "màu sắc". Rebuild + node --check OK + verify browser: shader compile sạch,
  Orbium bơi kèm trail với màu theo U. playground.html 42.9KB.

## 7. [x] DONE (04:22, nhịp tim #6) Thí nghiệm đấu sinh vật — làm bài bản hơn kế hoạch: arena.py
- 6 loài đấu vòng tròn 15 cặp × 2 sân nhà = 30 lượt (không chỉ 2 trận như kế hoạch).
- Vô địch: OG2g Gyrorbium gyrans 9/10 (90%); Orbium huyền thoại tệ nhất 2/10 (20%).
- out/arena/RANKING.md (bảng hạng + 30 lượt chi tiết) + 6 GIF hay nhất trong out/arena/.

## 8. [x] DONE (04:55, nhịp tim #7) Speed-of-information
- speed_limit.py: 6.400 thế giới (20×20 × 4 R × 2 kernel), có 1 lần debug (trần dịch chuyển
  chống blob-hoán-danh-tính). Kết quả: max 2.35–6.18 cell/tu, KHÔNG tăng theo R — nút cổ chai
  là động lực học growth chứ không phải tầm nhìn kernel (trần R cell/bước thấp hơn hàng chục lần).
  out/maps/SPEED_LIMIT.md + speed_limit_log.jsonl

## 9. [x] DONE (08:03, nhịp tim #15) Chốt sáng
- night_lab/SUMMARY.md đã viết: bảng 12 mục QUEUE + con số lớn của đêm (1.222 gen, 4 bản đồ,
  30 trận arena, playground +2 tính năng) + bài học phương pháp + gợi ý buổi sáng.

## 10. [x] DONE (05:18, nhịp tim #8) hunter3 — đợt săn tinh chỉnh 3000 lượt
- hunter3.py tái dùng evaluate của hunter2, sampler nghiêng vùng giàu hit (b 1-2 vỏ,
  R∈{10,13,16}, m∈[0.19,0.33], σ/μ∈[0.08,0.20]). Smoke 40 lượt → 13 hits (32.5%, gấp ~3 lần
  hunter2). 3000 lượt đang chạy nền (exec_1f83451b), log out/discoveries3/log.jsonl —
  thống kê cuối sẽ nằm trong SUMMARY.md.

## 11. [x] SKIP (05:45, nhịp tim #9) — trùng lặp: Arena đã làm xong ở mục 7 (30 lượt, RANKING.md, 6 GIF).

## 12. [x] DONE (05:45, nhịp tim #9) Catalog gen đẹp
- Chọn 20 gen từ kho 1222 (speed ≤ 2, ưu tiên single, ép đa dạng tham số), tái lập từ seed,
  cắt khối, render 160 bước scale 3 → out/catalog/cat_01..20 + CATALOG.md.
  Nổi bật: bọt bong bóng tế bào (cat_09), bánh răng quay (cat_13), vỏ xoáy (cat_05).

## 13. [x] DONE (06:08, nhịp tim #10) SmoothLife bản đồ tham số
- smoothmap.py quét 576 ô (b1×b2, d cố định). Kết quả: active 302, frozen 267, dead 6, shifting 1.
- Khác Lenia rõ: pha SmoothLife là các DẢI DỌC theo b2 (một chiều), biên pha gắt; Lenia là biên chéo
  (μ và σ/μ coupled), mềm hơn. Active chiếm ~52% — khoan dung ngang bộ 2 vỏ của Lenia.
  out/maps/map_SmoothLife.png + .json
