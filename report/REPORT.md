# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Anh Trí | 2A202602730 | Cá nhân: harness, runner, curator, thí nghiệm, báo cáo |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: DeepSeek qua endpoint tương thích OpenAI (`LAB_BASE_URL=https://api.deepseek.com`), `LAB_MODEL=deepseek-flash`, `LAB_TEMPERATURE=0`, `recursion_limit=60`. Khóa API chỉ nằm trong `.env` (đã bỏ qua bởi git).
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, Python 3.14, Linux, chạy trực tiếp trong `.venv` (không dùng Docker).
- Số lần chạy tác vụ đã dùng / ngân sách: đến hết Phần 3 đã dùng **9 lần chạy** (3 baseline learn, 3 subagents learn, 3 skills-auto learn) + 1 lần gọi curator. Ngân sách: dùng khóa DeepSeek cá nhân, không giới hạn cứng.
- Commit của tag `freeze`: (chưa đóng băng - điền ở Phần 4.1).

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

> Dự đoán điều kiện nào đạt điểm cao nhất trên **tác vụ đánh giá** và vì sao. Nêu căn cứ từ phân loại lỗi (mục 4) và từ tài liệu tham khảo. Điền cả ba dòng; `verify_freeze.py` kiểm tra điều này.

- H1 (subagents so với baseline): Trên **tác vụ đánh giá**, `subagents` **không cao hơn** `baseline` (dự đoán bằng hoặc thấp hơn), với chi phí token cao hơn. Căn cứ: ở tác vụ học, `subagents` đạt technical 18/18 như `baseline` nhưng house rules chỉ 1/9 (so với 4/9) và tốn 400.770 so với 309.084 token/lần; lỗi chủ đạo là nhóm E (quy ước ẩn) mà việc giao việc không khôi phục được do context isolation (data-learn: lời giao việc còn khẳng định sai là không có quy ước Acme).
- H2 (skills-auto so với baseline): `skills-auto` sẽ **không cải thiện đáng kể** điểm tác vụ đánh giá so với `baseline` (chênh lệch trong khoảng nhiễu), dù có thể giúp một phần các check dạng chuẩn hóa/sắp xếp/metadata mà `output-schema-and-normalization` mô tả. Căn cứ: ở tác vụ học, cả hai skill đều được đọc (`skills_read=2`) nhưng chỉ `code-learn` tăng (8→9/10), `data-learn` giảm (8→5/8); tài liệu SkillsBench ghi nhận skill do mô hình tự sinh trung bình không có lợi và SkillEvolBench ghi nhận lợi ích trên tác vụ học thường không chuyển sang tác vụ mới (quá khớp). Quy ước **mới** của tác vụ đánh giá chưa từng xuất hiện trong tác vụ học nên skill khó phủ.
- H3 (tác vụ học so với tác vụ đánh giá): Điểm **tác vụ đánh giá thấp hơn** tác vụ học ở cả ba điều kiện, vì tác vụ đánh giá thêm một quy ước mới. Khoảng cách (mean learn − mean eval) lớn nhất ở điều kiện nào "học" tốt nhất trên tác vụ học mà không khái quát được — nếu `skills-auto` cải thiện learn mà không cải thiện eval thì đó là bằng chứng quá khớp; ngược lại nếu `baseline` (không skill) có khoảng cách nhỏ nhất thì "học" không mang lại lợi ích chuyển giao.

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có các công cụ: công cụ tệp `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`; công cụ shell `execute`; công cụ giao việc `task`. Công cụ chạy lệnh là `execute` (backend shell, ví dụ `LocalShellBackend`).
2. Mô tả `task` nói subagent `general-purpose` là tác tử đa dụng để nghiên cứu câu hỏi phức tạp, tìm tệp/nội dung và thực thi tác vụ nhiều bước; nó có quyền dùng **mọi công cụ như tác tử chính**. Theo mặc định mỗi lần gọi là phi trạng thái (stateless): subagent `general-purpose` **không** thấy ngữ cảnh/hội thoại của tác tử chính, chỉ thấy nội dung prompt được gửi và trả về một báo cáo cuối.
3. Từ mô tả `task` (hành vi giao việc): "Put full detail in the prompt and state exactly what it should return." Từ mô tả `execute` (hành vi shell): "Quote paths containing spaces (e.g. cd \"/path/with spaces\")."

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

> Chỉ dùng tác vụ học. Mỗi dòng là một check thất bại.

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| code-learn | rule_regression_tests | E | `RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass.` |
| code-learn | rule_changelog | E | `RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>'` |
| logs-learn | rule_service_names | E | `RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service).` |
| logs-learn | rule_sorted_errors | E | `RULE: errors is sorted by service, then by timestamp_utc, ascending.` |
| logs-learn | rule_schema_header | E | `RULE: the top-level object has "schema_version": 2 and "generated_by": "log-triage".` |

Nhận xét: **toàn bộ 5 check thất bại của baseline thuộc nhóm E (vi phạm quy ước tổ chức)**; đây là các check có tên `rule_` và `detail` mở đầu bằng `RULE:`, không được nêu trong đề. Bằng chứng phủ định cho nhóm A-D: `scripts/check_breakdown.py` báo baseline (learn) đạt **18/18 check kỹ thuật** nhưng chỉ **4/9 check quy ước** — tác tử luôn đọc README/docstring và kiểm chứng kết quả (nhóm A-D đạt), chỉ thiếu các quy ước ẩn. Một skill có thể phòng ngừa nhóm E: một checklist buộc tác tử tìm và áp dụng quy ước tổ chức ẩn (tệp CHANGELOG, tệp test hồi quy, khối `meta`, đơn vị tiền, `schema_version`, thứ tự sắp xếp) trước khi kết thúc. `data-learn` baseline đạt 8/8 nên không có dòng lỗi; ở điều kiện `subagents` nó tụt còn 5/8 (cùng nhóm E) — xem mục 5.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế): `explorer` (đọc README/docstring/mẫu dữ liệu, chỉ báo cáo, không sửa — tách việc thu thập yêu cầu khỏi việc sửa); `implementer` (thực hiện thay đổi và chạy test — tách việc sinh mã); `reviewer` (kiểm tra độc lập kết quả và trường hợp biên, không sửa — tạo "cặp mắt thứ hai"). Ba vai trò tách biệt để giảm việc một ngữ cảnh vừa viết vừa tự chấm.
- `subagent_calls` ở từng tác vụ và nhận xét: **bằng 1 ở cả ba tác vụ học** (code-learn, data-learn, logs-learn). Ở cả ba, tác tử chính gọi đúng subagent `reviewer` để kiểm tra độc lập (`### Tool call: task`, mô tả mở đầu "Independently review/verify..."), không dùng `explorer`/`implementer`. Tác tử chính tự làm phần chính rồi mới giao khâu kiểm tra.
- Thông tin thiếu hoặc thừa khi giao việc: lời giao việc rất chi tiết và có nêu quy ước đường dẫn tương đối, đúng tinh thần context isolation. Tuy nhiên ở `data-learn`, lời giao việc **khẳng định sai** rằng "There is no 'Acme reporting conventions' document anywhere in the sandbox", nên cả nhóm bỏ qua 3 quy ước ẩn (`rule_money_in_cents`, `rule_meta_block`, `rule_clean_csv`) và điểm tụt từ 8/8 (baseline) xuống 5/8. Báo cáo của `reviewer` có được kiểm tra và dùng, nhưng bản thân nó cũng không biết quy ước.
- Ảnh hưởng đến token và thời gian: `subagents` tốn trung bình **400.770 token/lần** so với **309.084 token/lần** của baseline trên tác vụ học (khoảng +30%) và thời gian cao hơn (code-learn 171,5s so với 109,2s; logs-learn 160,2s so với 28,1s). Đa tác tử **không cải thiện điểm** (house rules thậm chí giảm 4/9 → 1/9; technical giữ 18/18) nên không đáng chi phí trong thí nghiệm này.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do: chạy curator **1 lần**, sinh **2 skill hợp lệ**, **không xóa** và **không chạy lại** (cả hai đều hợp lệ về định dạng và không rò rỉ định danh tác vụ đánh giá theo `validate_skill`). Không sửa tay nội dung skill.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `bugfix-regression-changelog` | Tổng quát: nói về việc sửa lỗi, viết test hồi quy và ghi changelog, không nêu tên tệp/hàm/con số của tác vụ học | Đúng về ý chính (test hồi quy cho từng lỗi, chạy cả suite, ghi changelog đúng heading, tối thiểu số bullet). Chưa chính xác ở ví dụ định dạng bullet `type(scope): ...` trong khi quy ước thật là `fix(<function name>): ...`; vị trí tệp test nói chung chung ("required location"). Không gây hại. | 13 dòng; `description`: "Use when a task asks you to fix bugs in code and record or verify the changes."; được đọc ở **cả 3** tác vụ học (`skills_read=2`) |
| `output-schema-and-normalization` | Tổng quát: nói về đầu ra có cấu trúc (JSON/CSV/log) với quy ước tên, sắp xếp, schema; không rò rỉ dữ liệu | Đúng và trúng: đối chiếu đúng các lỗi nhóm E (`rule_`) — chuẩn hóa định danh (hoa/thường, dấu phân cách), đơn vị/thời gian, sắp xếp theo khóa, thêm trường metadata/version bắt buộc, tự kiểm tra tệp cuối. Không có chỉ dẫn sai. | 13 dòng; `description`: "Use when producing structured output such as JSON, CSV, or logs that must follow explicit naming, sorting, or schema conventions."; được đọc ở **cả 3** tác vụ học (`skills_read=2`) |

Nhận xét Phần 3.4: cả hai skill đều được **đọc** ở mọi tác vụ (`skills_read=2`), nhưng kết quả không đồng nhất: `code-learn` tăng 8/10 → 9/10, `logs-learn` giữ 6/9, còn `data-learn` **giảm 8/8 → 5/8** (mất cả 3 `rule_`). Đây là dấu hiệu "đọc nhưng không làm theo toàn bộ" (05_skill_quality mục 5) và của nhiễu giữa các lần chạy.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
