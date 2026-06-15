---
title: Xây dựng khung đánh giá chất lượng và năng suất trong phát triển phần mềm
tags:
  - mindset
date: 2026-06-08
description: Từ Goodhart's Law đến thách thức AI, bài viết cung cấp khung tư duy để xây dựng hệ thống đo năng suất phần mềm chống gaming, với 4 nguyên lý nền tảng và ví dụ triển khai cụ thể cho từng vai trò trong quy trình phát triển.
categories:
  - Software development
---
# Khó khăn
Vì sao đây là một bài toán khó hơn vẻ ngoài?
Mọi người lãnh đạo công ty phần mềm đều muốn trả lời một câu tưởng đơn giản: _team của tôi đang làm tốt đến đâu?_ Nhưng phần mềm là **knowledge work** — công việc tri thức, sáng tạo, phi tuyến — chứ không phải dây chuyền lắp ráp. Một developer xóa đi 2.000 dòng code chết và làm hệ thống nhanh hơn 30% sẽ có "năng suất âm" nếu bạn đo bằng số dòng code viết ra. Đó là nghịch lý trung tâm.

Có ba lực cản mà bất kỳ hệ đo nào cũng phải đối mặt:

**Goodhart's Law.** Nhà kinh tế Charles Goodhart, qua cách diễn đạt của nhà nhân học Marilyn Strathern, để lại một câu kinh điển: _"Khi một thước đo trở thành mục tiêu, nó thôi là một thước đo tốt."_
Con người thông minh: hễ biết mình bị đánh giá bằng chỉ số nào, họ sẽ tối ưu chính chỉ số đó — thường bằng cách hy sinh điều mà chỉ số lẽ ra phải đại diện.

**Sự cố McKinsey 2023.** Khi McKinsey công bố bài _"Yes, you can measure software developer productivity"_, cộng đồng kỹ thuật đồng thuận bác bỏ. Lý do: phần lớn các chỉ số họ đề xuất đo _nỗ lực và sản lượng_ (khối lượng code, mức độ hoạt động, tần suất deploy) thay vì đo _kết quả và tác động_. Kent Beck và Gergely Orosz, trong bài phản biện nổi tiếng, nhắc lại đúng Goodhart's Law.

**Kỷ nguyên AI làm mọi sản lượng phình lên.** Đây là cạm bẫy mới. Nghiên cứu RCT năm 2025 của METR cho kết quả gây sốc: các developer giàu kinh nghiệm _tin rằng_ AI giúp họ nhanh hơn ~20%, nhưng đo thực tế họ lại _chậm hơn 19%_ khi dùng AI. Khoảng cách giữa cảm nhận và thực tế là gần 40%. Đồng thời, nhiều khảo sát cho thấy >75% developer dùng AI và nói mình làm nhanh hơn, nhưng tổ chức không thấy cải thiện đo được nào về tốc độ bàn giao sản phẩm. Nếu hệ đo của bạn dựa trên số PR hay số dòng code, AI sẽ thổi phồng các con số đó trong khi giá trị thực không đổi — và bạn sẽ mô hình hóa một ảo giác.

---
# Nguyên lí nền tảng trong thiết kế

Trước khi chạm vào bất kỳ vai trò cụ thể nào, hãy nắm bốn nguyên lý. Chúng là phần "bất biến" của khung; mọi thứ khác đều có thể điều chỉnh theo công ty bạn.

### Nguyên lý 1 — Outcome-first, không phải role-first

Sai lầm phổ biến nhất là bắt đầu từ "BA thì đo gì, QC thì đo gì". Cách này gần như chắc chắn sinh ra số liệu hoạt động theo vai trò_ — loại số liệu dễ bị gaming nhất.
Hãy đảo ngược: **xác định outcome mà công ty bán cho khách trước** (ví dụ: phần mềm chạy đúng, giao đúng hẹn, margin dương, khách gia hạn), rồi mới hỏi ngược lại _"vai trò này đóng góp vào outcome đó bằng cách nào"_. Câu hỏi đúng không phải "vai trò này làm nhiều ra sao" mà "vai trò này đóng góp như thế nào vào dòng giá trị cho khách hàng".

### Nguyên lý 2 — Đo để cải tiến, không đo để xếp hạng con người

Đây là ngã rẽ thiết kế quan trọng nhất. Nghiên cứu **Project Aristotle** của Google chỉ ra _psychological safety_ (an toàn tâm lý) là yếu tố dự báo số một cho hiệu suất nhóm — và chỉ số năng suất cấp cá nhân phá hủy chính sự an toàn đó.

Nhưng điều này dẫn tới một nghịch lý có thật: _không thể phát triển một người mà bạn từ chối đánh giá họ._ Lời giải của nguyên lí là **tách rời "cái gì được đo" khỏi "cách một người được đánh giá"** qua một kiến trúc ba lớp:

- **Lớp A — Vận hành (cấp team, tần suất cao):** các chỉ số liên quan tới workflow, hiệu suất của team / cá nhân. Mục đích của những chỉ số này dùng để điều chỉnh workflow thay vì phán xét một cá nhân hay một team.
- **Lớp B — Phát triển (cấp cá nhân, liên tục):** dùng **competency matrix / career ladder** — một công thức đánh giá tường minh "tốt ở mỗi cấp trông như thế nào". Chỉ số từ Lớp A chỉ vào đây ở vai trò _một bằng chứng trong nhiều bằng chứng_, không phải điểm số. Mục đích: _phát triển con người_.
- **Lớp C — Đánh giá (cấp cá nhân, tần suất thấp):** quyết định thăng tiến/lương qua **calibration** (họp so chuẩn chéo giữa các quản lý để giảm thiên kiến).

Nguyên tắc cốt lõi ở đây là _vẫn_ đánh giá cá nhân — nhưng đánh giá **năng lực và quỹ đạo phát triển bằng phán đoán con người bằng bộ chỉ tiêu ladder**, chứ không bằng dashboard năng suất. Dashboard ở lại Lớp A.

### Nguyên lý 3 — Cặp đối trọng - chống Goodhart

Chống gaming **không** phải là vấn đề của cách thu thập chỉ số (tự động hay thủ công). Tự động hóa việc đếm commit không giải quyết vấn đề; nó chỉ làm con số sai lệch trở nên _đáng tin một cách giả tạo_ hơn.

Phòng thủ thực sự nằm ở thiết kế quan hệ giữa các chỉ số. Đây chính là nguyên tắc cốt lõi của framework **DX Core 4**: mỗi chiều có một chỉ số chính được _đối trọng_ bởi một chỉ số đối nghịch, để không ai tối ưu một chiều bằng cách hy sinh chiều khác. 

Ví dụ: tốc độ (Speed) luôn phải đi kèm chất lượng (Change Failure Rate). Nếu bạn làm với tốc độ nhanh hơn nhưng tỷ lệ lỗi cũng tăng — đó không phải năng suất, đó là hỗn loạn.

> **Quy tắc:** nếu một chỉ số không có cặp đối trọng tự nhiên, nó chưa đủ an toàn để lên dashboard.

### Nguyên lý 4 — Ba tầng thu thập dữ liệu và khoảng cách cảm nhận thực tế

Mọi chỉ số rơi vào một trong ba tầng thu thập:

- **Tự động (telemetry thuần):** kéo từ tool có sẵn — Git, CI/CD, Jira, CRM, hệ thống ticket, Figma... Ít bị gaming kiểu "điền số", nhưng vẫn gameable qua hành vi.
- **Bán tự động (telemetry + gắn nhãn của người):** ví dụ "root-cause của lỗi này = requirement". **Đây là tầng quan trọng nhất**, vì nó cho phép _quy nguyên nhân ngược về vai trò_. Không có nó, bạn không bao giờ biết một lỗi xuất phát từ BA, designer hay dev. Đây có lẽ là một trong những phương pháp thu thập hiệu quả nhất để chống lại gaming hoá.
- **Thủ công / cảm nhận (survey, 360, quan sát quản lý):** dùng cho những thứ không instrument được (collaboration, độ rõ ràng). Nhưng nhớ bài học METR ở trên: **dữ liệu cảm nhận có sai lệch hệ thống** — luôn triangulate với dữ liệu hệ thống.

---

# Ví dụ triển khai theo vai trò của từng cá nhân

Áp dụng 4 nguyên lí trên, ta thử áp dụng vào các vị trí trong quy trình phát triển phần mềm. Những ví dụ dưới đây được sắp xếp mức độ đo lường từ dễ đến khó theo 3 tiêu chí:

- chỉ số càng phụ thuộc telemetry tự động thì càng dễ
- outcome càng khách quan thì càng dễ
- đóng góp càng nằm ở _thượng nguồn_ (gần với khách hàng) và càng _khuếch tán_ thì càng khó quy kết.

### 1. Customer Support

Với vị trí này, hệ thống ticket tự động ghi lại gần như mọi thứ, và chỉ số gắn trực tiếp với một outcome khách quan: khách có hài lòng không.

**Chỉ số:** CSAT/NPS (survey), First Contact Resolution (FCR), Mean Time to Resolution (MTTR), **ticket reopen rate**, tỷ lệ deflection (tự phục vụ).

**Thu thập:** chủ yếu _tự động_ từ hệ thống ticket; CSAT là _bán tự động_ (survey sau xử lý).

**Ví dụ:** Một agent đóng ticket trong 2 phút — MTTR tốt. Nhưng khách mở lại ticket đó sau 1 giờ vì vấn đề chưa thực sự được giải quyết. Nếu bạn chỉ nhìn MTTR, bạn đang khen thưởng hành vi đóng ticket vội.

**Cặp đối trọng:** MTTR phải đi với **reopen rate** và **CSAT**. Nhanh mà phải mở lại thì không phải nhanh.

### 2. QC / QA 

**Chỉ số:** **Defect Removal Efficiency (DRE)** / Defect Detection Percentage — tỷ lệ lỗi bắt được _trước_ khi release trên tổng số lỗi (trước + sau release). Đi kèm: defect leakage / escaped defects, requirements coverage, defect density.

**Thu thập:** _bán tự động_ từ bug tracker — bắt buộc có một trường "found in" (test hay production) để phân biệt lỗi bắt được sớm và lỗi lọt ra.

**Ví dụ:** Team A báo cáo tìm được 200 bug, team B tìm 50 bug. Ai làm tốt hơn? _Không thể biết_ — cho đến khi bạn biết bao nhiêu bug lọt ra production. Nếu team A để lọt 80 bug còn team B chỉ để lọt 5, thì team B mới là team test hiệu quả. Đó chính là điều DRE đo, còn "số bug tìm được" thì vô nghĩa khi đứng một mình.

**Cặp đối trọng:** DRE phải đi với **cycle time / tần suất release**. Nếu không, QA sẽ làm chậm mọi thứ lại để bắt nhiều lỗi hơn — tối ưu chất lượng bằng cách hy sinh tốc độ. Và đếm escaped defect nên _có trọng số theo severity_, không đếm thô.

**Lưu ý:** DRE không phải lúc nào cũng phù hợp (ví dụ sản phẩm rất mới, ít dữ liệu lịch sử). Khi đó bổ sung đánh giá định tính của team.

### 3. Developer

Telemetry của developer (Git, CI/CD) cực kỳ giàu và dễ thu thập — nhưng _đánh giá cá nhân_ developer lại là bài toán khó và gây tranh cãi nhất. Đây là nơi bạn buộc phải áp dụng Nguyên lý 2.

**Chỉ số cấp team (Lớp A):** bộ **DORA** (deployment frequency, lead time, change failure rate, time to restore; báo cáo 2025 bổ sung Rework Rate); chiều trải nghiệm theo **DevEx** (cognitive load, feedback loops) như leading indicator.

**Thu thập:** _tự động_ (DORA từ Git/CI) + _cảm nhận_ (DevEx qua survey, ví dụ DXI-style).

**Ví dụ:** Hãy nhớ lại nghịch lý đầu bài — developer xóa 2.000 dòng code chết, tăng tốc hệ thống 30%, nhưng "năng suất âm" theo thước đo LOC. 
Bài học: ở cấp cá nhân, **không** dùng diffs/commit/LOC làm điểm số. DX Core 4 nói rõ chỉ số "diffs per engineer" _không bao giờ_ được dùng ở cấp cá nhân hay gắn đánh giá hiệu suất.

**Vậy làm sao đánh giá một developer?** Qua **competency ladder** (Lớp B). Gergely Orosz tóm gọn: _bất cứ điều gì bạn muốn tối ưu đều nên nằm trong kỳ vọng năng lực, phân cấp theo seniority._ Bạn kỳ vọng senior tự lên kế hoạch, ước lượng, code, rollout và lắng nghe khách? Viết vào bộ tiêu chí đánh giá. Sau đó quản lý đánh giá _con người_ so với bộ tiêu chí, dùng dữ liệu Lớp A chỉ làm bối cảnh.

**Cặp đối trọng:** Speed (DORA) ⟷ Quality (Change Failure Rate); Activity ⟷ Satisfaction/DevEx.

**Bẫy AI:** vì AI thổi phồng output, đừng để biến tiềm ẩn "điểm năng suất" của bạn dựa vào số PR/dòng code. Neo vào outcome.

### 4. Presale 

Vị trí này tương đối khó trong việc đánh giá vì chỉ số rõ ràng, nhưng cần _liên kết chéo hệ thống_ — nối dữ liệu lúc bán (CRM) với dữ liệu thực tế lúc giao (PSA/quản lý dự án).

**Chỉ số:** win rate (deal thắng / đề xuất), **estimation accuracy** (ước lượng effort/cost lúc bán so với thực tế lúc đóng dự án), **margin của deal thắng**, proposal cycle time.

**Thu thập:** _bán tự động_ — ghép số CRM với số thực tế từ hệ thống quản lý dự án.

**Ví dụ dễ hiểu:** Một presale thắng 90% deal. Cho đến khi phát hiện các deal đó đều được ước lượng thấp hơn thực tế 40%, và phần lớn dự án về sau _lỗ margin_. Người này không tạo giá trị; họ chuyển rủi ro xuống cho team delivery.

**Cặp đối trọng:** win rate ⟷ **estimation accuracy + realized margin**. Đây là cặp đối trọng tốt: win rate đơn lẻ khuyến khích bỏ thầu giá thấp; margin thực tế giữ nó trung thực. Như giới professional services hay nói: _không phải mọi doanh thu đều ngang giá_ — một dự án 500K margin 65% tốt hơn hợp đồng 1 triệu margin 30%.

### 5. Designer 

Vị trí này thực sự khó đo, một phần đo được tự động, nhưng _chất lượng thiết kế_ mang tính chủ quan và outcome (trải nghiệm người dùng) cần đo riêng.

**Chỉ số:** design rework rate (số vòng lặp sau handoff), design-origin defect (UX bug truy về thiết kế), design system adoption / component reuse, và metric outcome khả dụng (task success rate, SUS score).

**Thu thập:** _bán tự động_ (rework từ lịch sử version Figma + ticket tracker; adoption từ Figma/codebase) + _thủ công_ (usability testing).

**Ví dụ :** Một designer giao mockup mà _không cần sửa lần nào_. Có thể hiệu suất và chất lượng người đó tốt? Tuy nhiên, cũng có thể không ai dám phản biện, hoặc thiết kế chưa từng được test với người dùng thật. Rework thấp có thể là dấu hiệu tốt — cũng có thể là dấu hiệu của một quy trình không có phản hồi.

**Cặp đối trọng:** rework rate ⟷ **usability outcome**. Ít sửa nhưng người dùng không hoàn thành được tác vụ thì thiết kế đó vẫn thất bại.

### 6. Business Analyst (BA)

Vai trò khó quy kết nhất vì đóng góp của BA nằm gần với khách hàng và _khuếch tán_ khắp vòng đời dự án. Một lỗi cuối nguồn có thể bắt nguồn từ spec mơ hồ — nhưng để chứng minh điều đó, bạn cần hạ tầng dữ liệu mà hầu hết công ty chưa có.

**Chỉ số:** requirement volatility / churn (% yêu cầu đổi/thêm sau sign-off), **requirement-origin defect density** (bản BA của escaped-defect: lỗi có root-cause là spec), requirements coverage (leading indicator), rework do spec.

**Thu thập:** _bán tự động_, và phụ thuộc hoàn toàn vào tầng **gắn nhãn root-cause**.

**Ví dụ:** Production lỗi: nút thanh toán hành xử sai. Do dev code ẩu, hay do spec không nói rõ điều gì xảy ra khi thẻ bị từ chối? Nếu không có nhãn root-cause trên defect. Nhãn root-cause biến một cuộc tranh cãi cảm tính thành một dữ liệu.

**Cặp đối trọng:** requirement churn ⟷ **client satisfaction về scope**. Đừng phạt mọi thay đổi — một phần thay đổi là khám phá lành mạnh; chỉ churn _do làm ẩu ban đầu_ mới là vấn đề.
> Lưu ý: nếu muốn đo đóng góp của BA và designer vào chất lượng, bạn _buộc_ phải đầu tư một taxonomy gắn nhãn nguyên nhân gốc rễ một cách kỉ luật và rõ ràng trên issue trạcker. Đây cũng chính là dữ liệu cho phép mô hình thống kê học được các tương tác liên vai trò

---

# Phân tích số liệu

1. **Mô tả và phân rã phương sai trước.** Chỉ số nào _đồng biến_ với nhau? Đây là nhân tố xác định các phân tích ở mức khám phá — tìm cấu trúc trước khi diễn giải.
2. **Cẩn trọng với "biến tiềm ẩn năng suất".** Ngành đã có hiện thân của ý tưởng này: chỉ số DXI của DX là một latent construct dựng từ 14 mục survey (Cronbach's alpha ~0.87). Nhưng nó kế thừa _vấn đề construct validity_: "năng suất thực" là biến không quan sát được, bạn chỉ suy ra từ các chỉ báo có thể sai lệch (nhớ METR).
3. **Tôn trọng quan hệ thời gian.** DevEx là _leading_, DORA là _lagging_ — khi developer báo cáo cognitive load cao, vấn đề thường biểu hiện trên DORA sau đó hàng tuần tới hàng tháng. Mô hình của bạn phải có độ trễ, nếu không bạn sẽ nhầm nhân-quả.
4. **Validate vào outcome cứng, khó gaming.** Một nhân tố ẩn chỉ có ý nghĩa nếu nó tương quan với escaped defects, tỷ lệ rework, hay tỷ lệ khách gia hạn. Nếu không, nó chỉ là nhiễu đã được toán học hóa.
 5. **Khai thác tương tác liên vai trò.** Đây là tác dụng của tầng gắn nhãn: ví dụ "requirement churn cao (BA) có dự báo escaped defect ở phía sau (QA) không?" — một feature interaction xuyên vai trò mà dashboard silo không bao giờ thấy được.

Một lưu ý: hầu hết công ty chỉ có 10–40 team, không phải hàng nghìn quan sát độc lập. Yếu tố ẩn ở quy mô đó _sẽ không ổn định_. Hãy dừng lại ở bước thống kê.

---

# Ưu điểm và hạn chế

### Ưu điểm:
- **Chống Goodhart,** cơ chế cặp đối trọng làm việc gaming trở nên _tự mâu thuẫn_: tối ưu một chỉ số sẽ làm xấu chỉ số đối trọng của nó.
- **An toàn về mặt tâm lý.** việc tách rời chỉ số năng suất khỏi đánh giá cá nhân (kiến trúc ba lớp) giữ được điều mà Project Aristotle cho là quan trọng nhất.
- **Bao phủ cả vị trí không phải developer**, vùng mà SPACE/DORA/DevEx/DX Core 4 không chạm tới.
- **Triển khai tăng dần**, giảm rủi ro: bắt đầu từ vai trò dễ, xây năng lực và lòng tin trước khi vào vùng khó.
- **Có đường tiến hóa rõ ràng** từ chỉ số rời rạc tới mô hình thống kê có kiểm chứng.

### Hạn chế

- **Không phải lời giải đúng hoàn toàn cho bài toán cá nhân.** Calibration tốn kém; phán đoán quản lý vẫn thiên lệch; và tách biệt chỉ số đánh giá cá nhân _sẽ gây rò ri_ — khi người ta biết chỉ số X là bằng chứng thăng tiến, Goodhart quay lại một phần. Phòng thủ duy nhất là dùng một _tập bằng chứng_ đủ rộng để không chỉ số nào đơn lẻ mang tính quyết định.
- **Tầng gắn nhãn bán tự động tự nó là một điểm vào của thiên kiến và gaming.** Cần một taxonomy thống nhất và calibrate người gắn nhãn định kỳ.
- **Dữ liệu cảm nhận sai lệch hệ thống** (METR). Đừng tin survey một mình; luôn triangulate.
- **Rủi ro thống kê ở công ty nhỏ:** không đủ quan sát cho mô hình biến ẩn ổn định.
- **Chi phí thiết lập và văn hóa.** Hệ này đòi hỏi sự đồng thuận. Nghiên cứu cho thấy developer trong team _đồng thuận_ về việc đo gì thường báo cáo năng suất cảm nhận cao hơn — nên hãy đồng thiết kế với chính người làm, không chỉ với trưởng bộ phận. Metric áp đặt và metric đồng thuận có hiệu ứng tâm lý ngược nhau.

---

# Quy trình năm bước để xây dựng hệ thống đo đạc

Đây là _quy trình_ để tự sinh ra bộ KPI của riêng từng tổ chức:

1. **Định nghĩa outcome của công ty** (cái khách thực sự trả tiền cho).
2. **Với mỗi vai trò và chỉ số, nó tác động tới outcome đó như thế nào** — không hỏi nó "nhiều" ra sao.
3. **Chọn chỉ số kèm cặp đối trọng** cho mỗi chỉ số. Không có đối trọng thì chưa lên dashboard.
4. **Xác định tầng thu thập** (tự động / bán tự động / thủ công) và đầu tư vào tầng gắn nhãn root-cause nếu cần quy kết liên vai trò.
5. **Phân tích từ mô tả tới mô hình**, validate vào outcome cứng, và _cố gắng tách_ mọi chỉ số khỏi đánh giá cá nhân.

Lặp lại quy trình này theo thứ tự vai trò từ dễ tới khó, điều chỉnh cho bối cảnh của từng công ty.

Câu hỏi đúng không phải _"đo năng suất thế nào?"_ mà là _"đo để làm gì?"_. Nếu bạn đo để **xếp hạng con người**, mọi hệ thống tinh vi nhất rồi cũng bị gaming và phá hủy văn hóa. Nếu bạn đo để **cải tiến hệ thống**, ngay cả những chỉ số khiêm tốn cũng trở thành công cụ chẩn đoán có giá trị.

Không tồn tại một framework đúng cho mọi công ty. Bài viết này chỉ cuung cấp một _cách tư duy_ — và phần còn lại là việc bạn áp dụng nó vào bối cảnh của mình.

---

# Tham chiếu

- Forsgren, N., Storey, M.-A., Maddila, C., Zimmermann, T., Houck, B., & Butler, J. (2021). _The SPACE of Developer Productivity_. ACM Queue. (Cũng đăng trên Communications of the ACM.)
- Forsgren, N., Humble, J., & Kim, G. (2018). _Accelerate: The Science of Lean Software and DevOps_. IT Revolution Press. — nền tảng của các chỉ số DORA.
- DORA / Google Cloud. _State of DevOps Report_ (2024–2025) — bao gồm bổ sung chỉ số Rework Rate. [https://dora.dev](https://dora.dev)
- Noda, A., Storey, M.-A., Forsgren, N., & Greiler, M. (2023). _DevEx: What Actually Drives Productivity_. ACM Queue.
- Tacho, L., & Noda, A. (2024). _Introducing the DX Core 4_. DX. [https://getdx.com/research/measuring-developer-productivity-with-the-dx-core-4/](https://getdx.com/research/measuring-developer-productivity-with-the-dx-core-4/)
- McKinsey & Company (2023). _Yes, you can measure software developer productivity._
- Beck, K., & Orosz, G. (2023). _Measuring developer productivity? A response to McKinsey._ The Pragmatic Engineer. [https://newsletter.pragmaticengineer.com/p/measuring-developer-productivity-part-2](https://newsletter.pragmaticengineer.com/p/measuring-developer-productivity-part-2)
- Orosz, G. _Can You Really Measure Individual Developer Productivity?_ The Pragmatic Engineer. [https://blog.pragmaticengineer.com/can-you-measure-developer-productivity/](https://blog.pragmaticengineer.com/can-you-measure-developer-productivity/)
- Becker, J., Rush, N., Barnes, E., & Rein, D. (2025). _Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity._ METR. arXiv:2507.09089. [https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- Google re:Work. _Project Aristotle_ — nghiên cứu về psychological safety và hiệu suất nhóm.
- Goodhart, C. (1975); diễn đạt theo Strathern, M. (1997). _"Improving ratings": audit in the British University system._
- Tricentis. _Essential Testing Metrics for Measuring Quality Assurance Success_ — về Defect Removal Efficiency / defect containment. [https://www.tricentis.com/blog/64-essential-testing-metrics-for-measuring-quality-assurance-success](https://www.tricentis.com/blog/64-essential-testing-metrics-for-measuring-quality-assurance-success)
- Velosio / SPI Research. _Professional Services KPIs_ — billable utilization, project margin, revenue leakage cho mô hình outsourcing.