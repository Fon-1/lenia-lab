# LENIA PETRI — Nuôi · Đấu · Lai tiến hóa

Mỗi con vật trong game này là **một công thức toán học chạy thật trên GPU của bạn** — không phải sprite vẽ sẵn.

## Chơi gì?
- 🍜 **Săn** — rót một "bể hoang" với gen ngẫu nhiên. Nếu sự sống tự tổ chức nổi lên, bắt về codex.
- ⚔ **Đấu** — creature của bạn đánh trận GPU thật với đối thủ hoang dã. Thắng ăn năng lượng.
- 🧬 **Lai** — trộn 2 gen thành con mới. Con có thể ra huyền thoại... hoặc chết non ngay trong bể ươm.
- 📤 **Share gen** — xuất creature của bạn thành 1 dòng code, gửi bạn bè nhập vào codex của họ.

## Mục tiêu
Thu thập đủ 30 gen để lên danh hiệu "Thần Lenia". Gen hiếm chỉ ra qua nhiều thế hệ lai — cộng đồng sẽ quyết định gen nào là "quý".

## Kỹ thuật (cho nerds)
Automata tế bào **Liên tục** (Lenia, Bert Chan 2018): không gian-thời gian-trạng thái liên tục, kernel vỏ đồng tâm + growth mapping, tích chập FFT… ở đây chạy bằng WebGL2 fragment shader ping-pong RG32F. Toàn bộ game = 1 file HTML, không server, không asset.

## Ghi chú
Cần trình duyệt hỗ trợ WebGL2 (Chrome/Edge/Firefox mới). Mở trên desktop để có FPS tốt nhất.
