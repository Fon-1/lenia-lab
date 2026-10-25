# KINHDOANH.md — từ đống token đến đồng tiền (kế hoạch thực tế, không vẽmo)

Tình trạng: có **prototype game chơi được** (`lenia-petri.html`), **playground demo đ eye-candy**
(`playground.html`), **kho 1.222 gen sống** + 4 bản đồ tham số + arena rankings. Chưa có: người chơi,
kênh phân phối, doanh thu. Đây là kế hoạch 3 đường, xếp theo xác suất ra tiền.

## Đường 1 — Game prototype lên itch.io (khuyến nghị bắt đầu ngay)

**Vì sao trước:** chi phí = 0 (itch.io miễn phí, không cần duyệt), đo phản ứng thị trường thật
bằng lượt chơi + comment, và mọi thứ khác (YouTube, Steam) lấy chất liệu từ đây.

Các bước còn thiếu (làm tuần tự, mỗi bước 1 buổi):
1. ✅ Vòng lặp gameplay: săn → đấu → lai (ĐÃ CÓ v0.1)
2. [ ] Thêm mục tiêu: "thu thập 20 loài trong codex" + bảng hiếm (gen hiếm = gặp ngẫu nhiên thấp)
3. [ ] Nút "Share gen" — xuất chuỗi base64 của creature để người chơi trao đổi (viral loop rẻ nhất)
4. [ ] Trang hướng dẫn 1 màn hình + icon + cover ảnh (dùng chính GIF chroma)
5. [ ] Đăng itch.io (file tĩnh, chalk tên "Lenia Petri — evolution pet"), giá: free + donate
6. [ ] Đo: 100 lượt chơi / comment đầu tiên / retention — nếu có signals mới đi tiếp Steam

Kỳ vọng thật: itch.io free-donate ra rất ít tiền trực tiếp. Giá trị thật = **bằng chứng nhu cầu**
trước khi đầu tư 6-12 tháng làm bản Steam đầy đủ (tham chiếu: The Bibites sống bằng Patreon
~1-2k$/tháng; Species: ALRE bán ổn trên Steam — thị trường evolution-sim niche nhưng thật).

## Đường 2 — Content ngắn (chạy song song, chi phí thấp)

- Nguyên liệu đã sẵn: GIF/clip chroma + comet trail (đẹp, lạ, ai cũng dừng xem 3 giây).
- Công thức video 30-60s: "Tôi tạo sự sống bằng 1 công thức toán" → clip Orbium lướt với
  vệt plasma → clip soup tự phát sinh đàn → kêu xem thử link itch.io.
- Đăng: TikTok/Shorts (VN + EN song song). Kỳ vọng thật: 3 tháng đầu ≈ 0đ; giá trị là
  traffic dẫn về itch.io + kênh cá nhân. Cần:マイк + capcut + kỷ luật đăng — phần này là
  việc của người, không phải của model.

## Đường 3 — Portfolio/freelance (báo đảm nhất, gián tiếp)

- Playground WebGL2 + night-lab automation (cron tự chạy nghiên cứu qua đêm, 15 nhịp 0 BLOCKED)
  là bằng chứng năng lực: GPU compute trên browser, mô phỏng khoa học, tool tự động.
- Ứng dụng thật của cùng skill set: interactive data-viz cho báo chí/doanh nghiệp, mô phỏng
  cho event/web khách hàng, tool giáo dục STEM. Đơn giá freelance creative-coding 20-80$/giờ.

## Những gì KHÔNG nên làm

- ❌ Bán NFT gen-art: thị trường chết, danh tiếng rủi ro.
- ❌ Bán "research" (bản đồ, 1222 gen): không ai mua đồ nghiên cứu của người lạ.
- ❌ Đặt quảng cáo Adsense lên trang toy: traffic chưa có, tiền lẻ không đáng sự bẩn.

## Số học kỳ vọng (minh bạch)

| Kịch bản | Xác suất | Tiền 6 tháng |
|---|---|---|
| Chỉ giữ làm toy | 100% | 0đ |
| Itch.io + 2-3 video đo reaction | ~50% ra signal | 0-50$ (donate) |
| Signal tốt → Steam EA sau 6-12 tháng | ~10-20% | vài nghìn $ nếu ổn |
| Không signal → chuyển portfolio kiếm freelance | chắc chắn có giá trị gián tiếp | theo đơn giá thị trường |

Điều kiện tiên quyết của MỌI đường: **anh phải là người bấm đăng** (tài khoản, giọng nói,
mặt/name) — model không thể tự phát hành thay. Phần kỹ thuật + nội dung, em gánh.
