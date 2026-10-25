# NIGHT LAB — lab đêm tự chạy của Lenia

Máy đang ngủ. Nhịp tim cron (mỗi 25 phút) dậy chạy MỘT mục trong `QUEUE.md`.

## Luật chơi của mỗi nhịp tim

1. Đọc `STATE.md` (tiến độ tổng) và `QUEUE.md` (hàng đợi).
2. Nếu giờ địa phương **≥ 06:30**: viết/chỉnh `SUMMARY.md` tổng kết mọi thứ làm được đêm nay
   (liệt kê artifact + kết quả chính), đánh dấu QUEUE còn lại thành `SKIP (sáng)`, rồi KẾT THÚC
   không làm thêm gì.
3. Ngược lại: lấy mục đầu tiên chưa `DONE` trong QUEUE, làm xong (hoặc thử tối đa 2 lần —
   lỗi 2 lần thì đánh dấu `BLOCKED: <lý do ngắn>` và chuyển mục tiếp theo).
4. Ghi nhận vào `journal.md`: giờ, việc đã làm, artifact sinh ra, kết quả ngắn.
5. Cập nhật `TOKENS.md` (máy đo token — xem công thức trong file đó).
6. Cập nhật `STATE.md` (dòng status cuối) và QUEUE item thành `DONE`/`BLOCKED`.

## Quy tắc cứng

- KHÔNG tạo automation/cron mới. KHÔNG hỏi câu hỏi — tự quyết. KHÔNG sửa `playground.html`
  nếu chưa rebuild từ template (`_playground_template.html` + `_presets.json` → thay
  `__PRESETS__` → ghi `playground.html`).
- File lớn (GIF/PNG) để trong `out/`. Kết quả phân tích viết vào `out/<tên>/ANALYSIS.md`
  hoặc chính QUEUE item.
- Nếu nhịp trước còn chạy dở (STATE.md có mục IN PROGRESS chưa xong): kiểm tra log
  nền/nhắc lại kết quả; nếu process chết thì chạy lại ở mức ưu tiên thấp hơn.

## Trạng thái hiện tại (cập nhật mỗi nhịp)

- **ĐÊM KẾT THÚC lúc 08:03** — 15 nhịp tim, 12 mục nghiên cứu DONE, 1 SKIP (trùng), 0 BLOCKED.
  Xem night_lab/SUMMARY.md để bắt đầu buổi sáng. Nhịp tim cron vẫn active — muốn dừng thì
  xóa/tắt automation "Nhịp tim 25 phút — lab đêm Lenia tự chạy nghiên cứu" trong tab Automations.
