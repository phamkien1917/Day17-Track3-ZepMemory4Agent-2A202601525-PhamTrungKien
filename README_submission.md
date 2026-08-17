# README Submission - Lab 17

## 1. Phân tích Benchmark
- **Layer có hit rate thấp nhất (khi không có memory):** Long-term, Episodic và Semantic đều có hit rate 0% trong bài no-memory (chỉ có Short-term pass do thông tin vẫn nằm trong buffer hiện tại). Do đó, Long-term/Episodic/Semantic là những layer đặc biệt quan trọng nhất để Agent duy trì trí nhớ qua các session.
- **Query retrieve nhiều token nhất:** Case **E02** và **E03** (layer Long-term) tiêu tốn nhiều token nhất (khoảng 930+ tokens), do chúng gọi Context Block chứa tổng hợp toàn bộ fact, entity và summary của user.
- **Case mixed E07:** Case E07 đòi hỏi kết hợp **Long-term** (biết user thích Python) và **Semantic** (biết quy tắc retry payment API phải có `Idempotency-Key`). Thiếu một trong hai sẽ bị đánh FAIL.
- **Token reduction và No-Memory:** Mô hình no-memory đạt mức token reduction gần 100% nhưng hit rate lại cực thấp (chỉ 18.2%), lý do đơn giản là vì nó "không lấy lên context nào cả". Việc cắt giảm token chỉ có ý nghĩa khi vẫn giữ nguyên được độ chính xác (hit rate) của retrieval.

## 2. Ghi chú thêm về Compaction (E10) và Recency (E08)
- **Compaction (E10):** Việc tóm tắt (compaction) giúp giải phóng token nhưng vẫn phải đảm bảo giữ lại các ràng buộc (constraint), ví dụ như deadline "16:00 Friday". Buffer thuần túy sẽ làm trôi mất thông tin này khi quá số lượng tin nhắn, nên Durable Notes là cần thiết.
- **Recency (E08):** Xử lý xung đột thông tin. Gần đây user đổi sang dùng TypeScript/NestJS cho dự án công ty, do đó Fact mới nhất (recency) phải ghi đè/được ưu tiên lên trên Fact cũ để đảm bảo câu trả lời luôn khớp với hiện trạng.

## 3. Câu hỏi lý thuyết 
- **Trade-off giữa Zep (Context Block) vs Redis + Qdrant:** Dùng Zep giúp tự động quản lý graph, summary, compaction và duy trì ngữ cảnh cross-session một cách minh bạch (managed memory). Nếu tự build bằng Redis+Qdrant, lập trình viên sẽ phải tốn rất nhiều nỗ lực để tự quản lý vòng đời (TTL), logic tóm tắt, và luồng embedding vector.
- **Guardrail chống Memory Poisoning:** Các thông tin trước khi đưa vào trí nhớ cần thông qua các rào chắn (như Heartbeat validation, Consent/Opt-in). Không thể cho phép user hoặc dữ liệu bên ngoài chèn trực tiếp các rule hệ thống (system prompt override) vào memory một cách mù quáng, tránh việc model bị "đầu độc" (prompt injection thông qua memory).
