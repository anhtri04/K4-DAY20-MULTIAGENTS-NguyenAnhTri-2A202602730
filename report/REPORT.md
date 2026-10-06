# Báo cáo Lab: Self evolving Agentic

> Sao chép tệp này thành `report/REPORT.md` (đã làm ở Phần 0) và điền dần qua các Phần của lab. Xóa các dòng hướng dẫn dạng trích dẫn (bắt đầu bằng `>`). Văn phong kỹ thuật, ngắn gọn, mọi nhận định đi kèm số liệu hoặc bằng chứng. Trong buổi học: điền mục 1 đến 7 (bản nháp). Sau buổi học: hoàn thiện mục 8 đến 10.

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Nguyễn Anh Trí | 2A202602730 | Cá nhân: harness, runner, curator, thí nghiệm, báo cáo |

- Nhà cung cấp và mô hình (`LAB_MODEL`, không ghi khóa API), nhiệt độ (`LAB_TEMPERATURE`), `recursion_limit`: DeepSeek qua endpoint tương thích OpenAI (`LAB_BASE_URL=https://api.deepseek.com`), `LAB_MODEL=deepseek-flash`, `LAB_TEMPERATURE=0`, `recursion_limit=60`. Khóa API chỉ nằm trong `.env` (đã bỏ qua bởi git).
- Phiên bản Deep Agents (`pip show deepagents`), hệ điều hành, chạy trực tiếp hay trong Docker: deepagents 0.7.21, Python 3.14, Linux, chạy trực tiếp trong `.venv` (không dùng Docker).
- Số lần chạy tác vụ đã dùng / ngân sách: đến hết Phần 3 đã dùng **9 lần chạy** (3 baseline learn, 3 subagents learn, 3 skills-auto learn) + 1 lần gọi curator. Ngân sách: dùng khóa DeepSeek cá nhân, không giới hạn cứng.
- Commit của tag `freeze`: `1335eeb` (tag `freeze`, tạo 2026-10-06T16:09:29+07:00); commit `hypotheses` ngay trước là `916bcdf`.

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

`report/table.md` (`python -m lab.compare`):

```text
| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 8/10 | 8/10 | 9/10 |
| data-learn | 8/8 | 5/8 | 8/8 |
| logs-learn | 6/9 | 6/9 | 6/9 |
| code-eval | 8/11 | 7/11 | 10/11 |
| data-eval | 5/9 | 5/9 | 6/9 |
| logs-eval | 10/10 | 6/10 | 6/10 |
| **Mean score - learning tasks** | 0.82 | 0.70 | 0.86 |
| **Mean score - evaluation tasks** | 0.76 | 0.60 | 0.73 |
| **Mean tokens per run** | 302,006 | 382,653 | 302,856 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |
```

`python scripts/check_breakdown.py` (tách check kỹ thuật và check quy ước `rule_`):

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         5/12         294,927      0/3
baseline      learn    18/18         4/9          309,084      0/3
subagents     eval     18/18         0/12         364,537      0/3
subagents     learn    18/18         1/9          400,770      0/3
skills-auto   eval     18/18         4/12         274,667      3/3
skills-auto   learn    18/18         5/9          331,045      3/3
```

`python scripts/verify_freeze.py`: **OK** (6 lần chạy `skills-auto`; hash skill khớp bộ đóng băng, `skills_modified=false`, mọi lần chạy sau tag). Không có lần chạy nào có `error` khác `None` và không có lần nào `skills_modified=true`.

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. **Tác vụ học:** chỉ `skills-auto` cải thiện so với `baseline` (mean 0.86 so với 0.82, +0.04); `subagents` giảm còn 0.70 (−0.12). **Tác vụ đánh giá:** không điều kiện nào cao hơn `baseline` (`baseline` 0.76; `skills-auto` 0.73; `subagents` 0.60). `skills-auto` cải thiện tác vụ **học** nhưng không cải thiện tác vụ **đánh giá** (khoảng cách learn−eval lớn nhất: 0.13 so với 0.06 của baseline và 0.10 của subagents) — đây là **dấu hiệu quá khớp**: lợi ích trên tác vụ học không chuyển sang tác vụ mới, đúng như SkillEvolBench dự đoán.
2. Check kỹ thuật đạt **18/18 ở mọi điều kiện và mọi vai trò**, nên mọi khác biệt đều nằm ở check quy ước `rule_`. `skills-auto` nâng house rules tác vụ học 4/9 → 5/9 nhưng hạ nhẹ ở đánh giá (baseline 5/12 → 4/12). Cụ thể skill giúp: `code-eval` sửa được `rule_regression_tests` và `rule_changelog`; `data-eval` sửa được `rule_sorted_keys_format`. Quy ước **mới** của tác vụ đánh giá (`rule_version_bump` ở code; `rule_source_line` ở logs) **không được skill giúp**, vì các quy ước này chưa từng xuất hiện trong tác vụ học nên curator không thể sinh chỉ dẫn cho chúng — đúng với lập luận trong H2.
3. **Check skill giúp đạt:** `code-eval` `rule_regression_tests`. `skills_read=2`; vết `results/skills-auto/code-eval/trace.md` có 12 lần nhắc `tests/test_regressions.py` và 8 lần `CHANGELOG.md` (baseline `skills_read=0` và trượt cả hai check) — tác tử đã theo skill `bugfix-regression-changelog`. **Check skill không giúp:** `data-eval` `rule_money_in_cents`. `skills_read=2` (đã đọc `output-schema-and-normalization`), nhưng tác tử vẫn ghi `"north_q1_revenue": 3130.24` (USD thập phân) thay vì integer cents và không tạo `clean.csv` → **đọc nhưng không làm theo**, do skill chỉ nói chung "units" chứ không nêu "cent".
4. Chi phí: token trung bình/lần chạy `baseline` 302.006, `subagents` 382.653 (+27%), `skills-auto` 302.856. Trên tác vụ đánh giá: 294.927 / 364.537 / 274.667 token. Hiệu quả điểm trên token (đánh giá): `skills-auto` ≈ 0.264 điểm/100k token, `baseline` ≈ 0.258, `subagents` ≈ 0.164. **Đa tác tử không đáng chi phí** trong thí nghiệm này: điểm thấp hơn ở cả hai vai trò mà tốn token nhất.
5. Không có **rò rỉ**: `validate_skill` từ chối mọi skill chứa `eval_markers()` và cả 2 skill đều hợp lệ (không có tên tác vụ đánh giá). Có **quá khớp**: mean learn tăng 0.82 → 0.86 trong khi mean eval giảm 0.76 → 0.73, và khoảng cách learn−eval của `skills-auto` lớn nhất; thêm nữa `logs-eval` rơi từ 10/10 (baseline) xuống 6/10 ở cả hai điều kiện có can thiệp.
6. Nhiễu: cùng bộ skill, so `results/skills-auto-dev/` (Phần 3.4) với chạy sau đóng băng: `code-learn` 9/10 = 9/10, `logs-learn` 6/9 = 6/9, nhưng `data-learn` **5/8 so với 8/8 — lệch 3 check (~0.38 điểm)**. Mức nhiễu này **lớn hơn** phần lớn chênh lệch trong bảng mục 7 (ví dụ `skills-auto` − `baseline` ở eval chỉ 0.03), nên các khác biệt nhỏ giữa điều kiện là **không đáng tin** với n=1. Chỉ hiệu ứng lớn (như `subagents` logs-eval 10/10 → 6/10) mới gợi ý thật.

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1. Chỉ **3 tác vụ mỗi vai trò** và **mỗi cấu hình chạy một lần**; nhiễu giữa hai lần chạy cùng cấu hình lên tới ~0.38 điểm (`data-learn`). Vì vậy chỉ nên tin các hiệu ứng lớn; các chênh lệch nhỏ giữa điều kiện chưa kết luận được.
2. Tác vụ do giảng viên thiết kế với quy ước ẩn (nhóm E); tác vụ đánh giá thêm một quy ước **mới chưa từng thấy**. Điều này bất lợi có hệ thống cho skill tự sinh (không thể suy ra quy ước chưa gặp) và có thể thiên vị `baseline` may mắn (logs-eval 10/10).
3. Chỉ dùng **một mô hình** (`deepseek-flash`, temperature 0) và một phiên bản deepagents; kết luận về "đa tác tử" và "skill tự sinh" không suy rộng được sang mô hình khác.
4. **Chi phí token bị chi phối bởi ngữ cảnh tích lũy** (mỗi lần gọi gửi lại toàn bộ lịch sử), nên token/lần chạy biến động mạnh và không phản ánh trực tiếp "công sức suy luận"; so sánh token giữa điều kiện vì thế chỉ mang tính tương đối.
5. **Curator chạy một lần** và có tính ngẫu nhiên: bộ skill là một mẫu duy nhất, không lặp lại; không loại trừ việc chạy lại curator cho bộ skill tốt hơn hoặc tệ hơn.

## 10. Kết luận

Trên bộ 6 tác vụ này, kỹ thuật đạt 18/18 ở mọi điều kiện nên toàn bộ khác biệt nằm ở các quy ước tổ chức ẩn. Đa tác tử (`subagents`) làm giảm điểm ở cả hai vai trò (learn 0.70, eval 0.60) trong khi tốn thêm ~27% token so với baseline, nên không đáng chi phí. Skill tự sinh (`skills-auto`) cải thiện nhẹ tác vụ học (0.82 → 0.86) nhưng không cải thiện tác vụ đánh giá (0.76 → 0.73) và khoảng cách học−đánh giá lớn nhất — dấu hiệu quá khớp, khớp với SkillsBench/SkillEvolBench. Vì nhiễu một lần chạy lên tới ~0.38 điểm, các kết luận này chỉ mang tính gợi ý. Đề xuất tiếp theo: lặp mỗi điều kiện ≥ 3 lần trên tác vụ đánh giá (hướng 6e) để tách tín hiệu khỏi nhiễu, và bổ sung cơ chế giúp tác tử chủ động truy tìm quy ước ẩn thay vì chỉ dựa vào skill tự sinh.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest` (toàn bộ: 32 test đạt, sau khi hoàn tất 4 tệp).
  2. `python -m lab.runner --condition baseline --tasks data-learn`
  3. `python -m lab.runner --condition baseline --tasks code-learn logs-learn`
  4. `python -m lab.runner --condition subagents --tasks learn`
  5. `python -m lab.curator`
  6. `python -m lab.runner --condition skills-auto --tasks learn`
  7. `git commit -m hypotheses`; `mv results/skills-auto results/skills-auto-dev`; `git commit -m "freeze skills"`; `git tag freeze`
  8. `python -m lab.runner --condition baseline --tasks eval`
  9. `python -m lab.runner --condition subagents --tasks eval`
  10. `python -m lab.runner --condition skills-auto --tasks all`
  11. `python scripts/verify_freeze.py` (OK); `python -m lab.compare > report/table.md`; `python scripts/check_breakdown.py`.
- Thử thách mở rộng (nếu có): không thực hiện.
- Ghi chú khác: khóa API chỉ nằm trong `.env` (đã bỏ qua bởi git); đã quét `results/`, `report/`, `skills/` xác nhận không lộ khóa. Bộ skill Phần 3.4 được sao lưu tại `results/skills-auto-dev/` để so nhiễu.
