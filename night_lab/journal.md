# JOURNAL — nhật ký lab đêm

## 01:45 — Khởi công
- hunter2 calibrate OK: orbium → colony HIT (0.17–0.30 cell/tu), scutium tĩnh → MISS đúng.
- hunter2 1500 trials phóng nền (exec_152cb8e8).
- mapgen b1_R13 xong sau khi fix bug đo tốc độ trên khung cuối: map đầu tiên có cấu trúc pha rõ
  (creature vàng ở σ/μ cao, static xanh đậm ở σ/μ hẹp, dead mép μ thấp).
- Night lab dựng xong, nhịp tim 25 phút bắt đầu từ ~02:05.

## 02:01 — hunter2 1500 trials HOÀN TẤT (nền)
- Kết quả: **177 hits / 1500 lượt / 822 giây** (~11.8% hit rate, gấp ~2.4 lần hunter1).
- Tốc độ đo được toàn hợp lý (≤ ~1.5 cell/tu) — lọc transient + tracking đa blob đã diệt artifact.
- Log đầy đủ: out/discoveries2/log.jsonl (177 dòng JSON, tag single/colony).
- Nhịp tim kế tiếp làm QUEUE mục 1 (phân tích) không cần đợi nữa.

## 02:00 — Phát hiện lớn từ bản đồ thứ 2 + mở rộng lệnh đêm
- mapgen b2_R13 (kernel 2 vỏ b=0.5+1): creature zone **544 → 1410 ô (×2.6)**, static 875 → 109.
  → Kernel nhiều vỏ không chỉ đổi hình sinh vật mà NỞ RỘNG vùng sự sống của vũ trụ gen.
  out/maps/map_b2_R13.png
- Anh ra lệnh "chưa 3 tỷ token đừng dừng": QUEUE nới lên 13 mục (hunter3 3000 lượt tinh chỉnh,
  arena đấu vòng tròn 15 trận, catalog 20 gen đẹp, SmoothLife map), giờ chốt sáng dời 06:30 → 08:00.
- Ghi chú trung thực vào TOKENS.md: tổng đốt thực tế một đêm cỡ triệu, không tới tỷ — số ghi là số thật.

## 02:13 — (nhịp tim #1) Phân tích hunter2
- out/discoveries2/ANALYSIS.md: 177 hits / 0 artifact; colony 127, single 50.
- Kernel 2 vỏ = 80/177 hits — khớp phát hiện map b2 (vùng creature ×2.6).
- Top speed 5.71 cell/tu. hunter3 sẽ nghiêng b=2 vỏ, R∈{10,16}, m∈[0.19,0.33].

## 02:38 — (nhịp tim #2) mapgen b3_R15 — bộ 3 bản đồ hoàn chỉnh
- out/maps/map_b3_R15.png: creature 877, drift 1330 (đỉnh), static 163.
- Chuỗi theo số vỏ kernel: creature 544 → 1410 → 877; drift 1010 → 892 → 1330.
  1 vỏ = đóng băng nhiều; 2 vỏ = đỉnh sinh vật di động; 3 vỏ = đỉnh kẻ trôi chậm.

## 03:03 — (nhịp tim #3) Ghép all_maps + nhận xét pha
- out/maps/all_maps.png (462×1464, 3 tầng) + out/maps/PHASES.md.
- 5 nhận xét: static sụp 875→109 ở 2 vỏ; 2 vỏ = đỉnh di động; 3 vỏ = đỉnh drift;
  vùng dead bám mép μ thấp bất biến với kernel; săn nhanh nên dò mép vàng/ngọc của map 2 vỏ.

## 03:25 — (nhịp tim #4) SmoothLife dựng xong
- smoothlife.py (FFT 2 miền: đĩa trong ri=3 + vành ro=10, dt=0.115, tham số kinh điển Rafler).
- LỖI đã sửa: công thức dạng tích nhớ từ memory làm mass→0; đổi sang dạng tổng theo ngữ nghĩa
  Life (survival band khi m>0.5, birth band khi m<0.5, trộn sigmoid) — mass ổn định ~3830/600 bước.
- out/smoothlife_soup.gif (mê cung giun), out/smoothlife_glider.gif (sinh vật mê cung lớn —
  không phải glider đơn, SmoothLife cần bộ tham số khác cho glider thật; ghi chú cho mục 13).

## 03:52 — (nhịp tim #5) Chroma mode cho playground
- State texture R32F → RG32F (G = tiềm năng U); simfs ghi kèm U; brushfs giữ U khi tô;
  dispfs thêm hsv2rgb (hue = 0.66 − U·0.62, sáng theo A^0.75); UI select "màu sắc".
- Rebuild từ template (42.9KB) + node --check OK + verify browser: không fatal overlay,
  Orbium sống, màu biến thiên theo U. Sẵn sàng cho anh sáng mai mở là thấy 2 chế độ màu.

## 04:22 — (nhịp tim #6) Arena — 30 lượt đối đầu
- arena.py: mỗi cặp đấu 2 lượt (mỗi loài làm chủ nhà cung cấp luật) — công bằng hơn kế hoạch gốc.
- Vô địch OG2g 9/10 (90%); Orbium huyền thoại tệ nhất 2/10 (20%). 2PG1v/2S1f/S3s đồng hạng 2 (60%).
- out/arena/RANKING.md + 6 GIF hay nhất (chấm theo độ "drama" của phán quyết).
- Ý nghĩa: độ nổi tiếng ≠ độ sống sót trong hỗn chiến — hạt nhân gameplay cho cái game.

## 04:55 — (nhịp tim #7) Speed-of-information
- speed_limit.py quét 6.400 thế giới. Lần 1 nhiễm artifact blob-hoán-danh-tính (max 68 cell/tu);
  thêm trần dịch chuyển theo R → sạch: max 2.35–6.18 cell/tu (0.23–0.62 cell/bước).
- Kết luận: tốc độ KHÔNG tăng theo R; nút cổ chai là động lực học growth (phải giữ hình khi di chuyển),
  không phải tầm nhìn kernel. out/maps/SPEED_LIMIT.md

## 05:18 — (nhịp tim #8) hunter3 phóng nền
- hunter3.py: sampler nghiêng vùng giàu hit theo ANALYSIS.md. Smoke 40 → 13 hits (32.5%).
- 3000 lượt chạy nền (exec_1f83451b), dự kiến ~11 phút — xong trước nhịp kế.

## 05:30 — hunter3 HOÀN TẤT (nền)
- Kết quả: **1005 hits / 3000 lượt / 697 giây** (33.5% — sampler tinh chỉnh đỉnh thật).
- out/discoveries3/log.jsonl: 1005 gen (b 1-2 vỏ, R∈{10,13,16}, m∈[0.19,0.33]).
- Tổng kho 3 đợt săn: 40 + 177 + 1005 = **1222 gen sống** — nguyên liệu khổng lồ cho catalog.

## 05:45 — (nhịp tim #9) Catalog 20 gen đẹp
- catalog.py: lọc 1222 gen (speed ≤ 2, single trước, đa dạng), tái lập từ seed → 20 GIF chuẩn
  out/catalog/ + CATALOG.md. Preview 2×2: bọt bong bóng, bánh răng, vỏ xoáy — đa dạng bất ngờ.

## 06:08 — (nhịp tim #10) SmoothLife map
- smoothmap.py quét 576 ô: active 302 / frozen 267 / dead 6. Pha là dải DỌC theo b2 —
  khác biên chéo của Lenia; dead chỉ ở góc b1 cao. out/maps/map_SmoothLife.png
- Mục 9 chuyển thành time-gated rõ ràng cho các nhịp 06:30–07:45.

## 06:23 — (nhịp tim #11) chưa tới 08:00, nhịp rảnh — hàng đợi đã xong hết, chờ chốt sáng.

## 06:55 — (nhịp tim #12) chưa tới 08:00, nhịp rảnh — chờ chốt sáng.

## 07:15 — (nhịp tim #13) chưa tới 08:00, nhịp rảnh — chờ chốt sáng.

## 07:38 — (nhịp tim #14) chưa tới 08:00, nhịp rảnh — nhịp kế sẽ chốt sổ.

## 08:03 — (nhịp tim #15) CHỐT SỔ
- night_lab/SUMMARY.md viết xong. Đêm kết thúc: 15 nhịp, 12 mục nghiên cứu DONE, 1 SKIP (trùng),
  3 nhịp rảnh theo time-gate. Toàn bộ artifact trong out/, sổ token đầy đủ.

## 08:28 — (nhịp tim #16) đêm đã kết thúc từ 08:03 — nhịp rảnh, không có việc.
