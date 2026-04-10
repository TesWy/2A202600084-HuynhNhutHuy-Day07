# Golden Query Evaluation

- Generated at: `2026-04-10T16:41:59`
- Embedding backend: `mock embeddings fallback`
- Collection: `legal_full_structured`
- Strategy: `structured_legal`
- Parameters: `chunk_size=1400`, `overlap=150`, `max_sentences=4`, `top_k=3`
- Source files indexed: `8`
- Stored chunks: `1398`

- Warning: current run uses mock embeddings fallback, so semantic ranking quality is not representative of a real embedding backend.

## Mode: `no_filter`

- top1 exact rate: `0.0` | top3 exact rate: `0.0` | pass rate: `0.0` | avg keyword recall: `0.0333`

| ID | Query | Expected | Top-1 | Top-3 exact | Keyword recall | Pass |
|---|---|---|---|---|---:|---|
| q1 | Những phương thức bảo vệ quyền dân sự khi quyền dân sự bị xâm phạm là gì? | Bộ Luật dân sự 2015 / 11 | Bộ Luật dân sự 2015 / 361 | False | 0.1667 | False |
| q2 | Một tổ chức cần những điều kiện nào để được công nhận là pháp nhân? | Bộ Luật dân sự 2015 / 74 | Bộ Luật dân sự 2015 / 158 | False | 0.0 | False |
| q3 | When is Vietnam's Population Day? | Law on Population 2025 / 5 | Law on Population 2025 / 16 | False | 0.0 | False |
| q4 | Name three banned business lines under the Law on Investment 2025. | Law on Investment 2025 / 6 | Bộ Luật dân sự 2015 / 346 | False | 0.0 | False |
| q5 | In the Planning Law 2025, what is the national planning database? | Planning Law 2025 / 3 | Children Law 2016 / 74 | False | 0.0 | False |

### q1: Những phương thức bảo vệ quyền dân sự khi quyền dân sự bị xâm phạm là gì?

- Gold answer: Khi quyền dân sự bị xâm phạm, chủ thể có quyền tự bảo vệ hoặc yêu cầu cơ quan, tổ chức có thẩm quyền công nhận và bảo đảm quyền dân sự, buộc chấm dứt hành vi xâm phạm, buộc xin lỗi cải chính công khai, buộc thực hiện nghĩa vụ, buộc bồi thường thiệt hại, hủy quyết định cá biệt trái pháp luật và các yêu cầu khác theo luật.
- Metrics: top1_exact=`False`, top3_exact=`False`, keyword_recall=`0.1667`, pass=`False`
- Top-1: score=`0.4098`, title=`Bộ Luật dân sự 2015`, article=`361`, preview=`Phần thứ ba | NGHĨA VỤ VÀ HỢP ĐỒNG | Chương XV | QUY ĐỊNH CHUNG | Mục 4. TRÁCH NHIỆM DÂN SỰ Điều 361. Thiệt hại do vi phạm nghĩa vụ  1. Thiệt hại do vi phạm nghĩa vụ bao gồm thiệt hại về vật chất và thiệt hại về tinh thầ`
- Top-2: score=`0.3691`, title=`Planning Law 2025`, article=`58`, preview=`Chapter VI | IMPLEMENTATION CLAUSE Article 58. Transitional clauses  b) In case adjustments to a planning scheme were formulated as prescribed in Article 54 of the Planning Law No. 21/2017/QH14 before December 10, 2025 b`
- Top-3: score=`0.3643`, title=`Bộ Luật dân sự 2015`, article=`452`, preview=`Phần thứ ba | NGHĨA VỤ VÀ HỢP ĐỒNG | Chương XVI | MỘT SỐ HỢP ĐỒNG THÔNG DỤNG | Mục 1. HỢP ĐỒNG MUA BÁN TÀI SẢN Điều 452. Mua sau khi sử dụng thử  1. Các bên có thể thỏa thuận về việc bên mua được dùng thử vật mua trong m`

### q2: Một tổ chức cần những điều kiện nào để được công nhận là pháp nhân?

- Gold answer: Một tổ chức được công nhận là pháp nhân khi được thành lập theo luật, có cơ cấu tổ chức, có tài sản độc lập và tự chịu trách nhiệm bằng tài sản của mình, và nhân danh mình tham gia quan hệ pháp luật một cách độc lập.
- Metrics: top1_exact=`False`, top3_exact=`False`, keyword_recall=`0.0`, pass=`False`
- Top-1: score=`0.4687`, title=`Bộ Luật dân sự 2015`, article=`158`, preview=`Phần thứ hai | QUYỀN SỞ HỮU VÀ QUYỀN KHÁC ĐỐI VỚI TÀI SẢN | Chương XI | QUY ĐỊNH CHUNG | Mục 1. NGUYÊN TẮC XÁC LẬP, THỰC HIỆN QUYỀN SỞ HỮU, QUYỀN KHÁC ĐỐI VỚI TÀI SẢN Điều 158. Quyền sở hữu  Quyền sở hữu bao gồm quyền ch`
- Top-2: score=`0.3881`, title=`Bộ Luật dân sự 2015`, article=`30`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương III | CÁ NHÂN | Mục 2. QUYỀN NHÂN THÂN Điều 30. Quyền được khai sinh, khai tử  1. Cá nhân từ khi sinh ra có quyền được khai sinh.  2. Cá nhân chết phải được khai tử.  3. Trẻ em sin`
- Top-3: score=`0.3845`, title=`Law on Educators 2025`, article=`40`, preview=`Chapter IX | IMPLEMENTATION CLAUSE Article 40. Amendments to Article 66 of Law on Social Insurance No. 41/2024/QH15  Addition of clause 3a after clause 3 Article 66:  “3a. The monthly pension rate for entities prescribed`

### q3: When is Vietnam's Population Day?

- Gold answer: Vietnam's Population Day is December 26 each year.
- Metrics: top1_exact=`False`, top3_exact=`False`, keyword_recall=`0.0`, pass=`False`
- Top-1: score=`0.3900`, title=`Law on Population 2025`, article=`16`, preview=`Chapter IV | ADAPTATION TO POPULATION AGEING Article 16. Solutions for adapting to population ageing  1. Preparation for old age.  2. Care for the elderly.  3. Development of human resources for providing care for the el`
- Top-2: score=`0.3543`, title=`Law on Press 2025`, article=`15`, preview=`Chapter II | PRESS ORGANIZATION | Section 2. PRESS AGENCIES Article 15. Press agencies  1. Press agencies perform one or more press types, have one or more press products, and may have subordinate press agencies in accor`
- Top-3: score=`0.3535`, title=`Bộ Luật dân sự 2015`, article=`604`, preview=`Phần thứ ba | NGHĨA VỤ VÀ HỢP ĐỒNG | Chương XX | TRÁCH NHIỆM BỒI THƯỜNG THIỆT HẠI NGOÀI HỢP ĐỒNG | Mục 3. BỒI THƯỜNG THIỆT HẠI TRONG MỘT SỐ TRƯỜNG HỢP CỤ THỂ Điều 604. Bồi thường thiệt hại do cây cối gây ra  Chủ sở hữu, `

### q4: Name three banned business lines under the Law on Investment 2025.

- Gold answer: Examples of banned business lines include business in narcotic substances, prostitution business, human trafficking and trade in human tissues or organs, business activities pertaining to asexual human reproduction, trade in firecrackers, debt collection services, national treasures, relics and antiques, and electronic cigarettes or heated tobacco products.
- Metrics: top1_exact=`False`, top3_exact=`False`, keyword_recall=`0.0`, pass=`False`
- Top-1: score=`0.4348`, title=`Bộ Luật dân sự 2015`, article=`346`, preview=`Phần thứ ba | NGHĨA VỤ VÀ HỢP ĐỒNG | Chương XV | QUY ĐỊNH CHUNG | Mục 3. BẢO ĐẢM THỰC HIỆN NGHĨA VỤ Điều 346. Cầm giữ tài sản  Cầm giữ tài sản là việc bên có quyền (sau đây gọi là bên cầm giữ) đang nắm giữ hợp pháp tài s`
- Top-2: score=`0.3812`, title=`Children Law 2016`, article=`34`, preview=`Chapter II | CHILDREN’S RIGHTS AND RESPONSIBILITIES | Section 1. CHILDREN’S RIGHTS Article 34. Right to state opinions and attend meeting  Children have the right to state their opinions and expectations about children i`
- Top-3: score=`0.3666`, title=`Law on Investment 2025`, article=`14`, preview=`Chapter III | INVESTMENT INCENTIVES AND SUPPORT Article 14. Investment incentives and investment support  d) Accelerated depreciation, increasing the deductible expenses upon calculation of taxable income;  dd) Other for`

### q5: In the Planning Law 2025, what is the national planning database?

- Gold answer: The national planning database is a collection of planning databases, planning-related information and data, arranged and organized to meet requirements for access, exploitation, sharing, management and updating.
- Metrics: top1_exact=`False`, top3_exact=`False`, keyword_recall=`0.0`, pass=`False`
- Top-1: score=`0.3904`, title=`Children Law 2016`, article=`74`, preview=`Chapter IV | CHILD PROTECTION | Section 4. MEASURES FOR PROTECTING CHILDREN IN THE COURSE OF PROCEEDING, TAKING OF ACTIONS AGAINST ADMINISTRATIVE VIOLATIONS, REHABILITATION/ RECOVERY AND SOCIAL INCLUSION Article 74. Scop`
- Top-2: score=`0.3742`, title=`Bộ Luật dân sự 2015`, article=`436`, preview=`Phần thứ ba | NGHĨA VỤ VÀ HỢP ĐỒNG | Chương XVI | MỘT SỐ HỢP ĐỒNG THÔNG DỤNG | Mục 1. HỢP ĐỒNG MUA BÁN TÀI SẢN Điều 436. Phương thức giao tài sản  1. Tài sản được giao theo phương thức do các bên thỏa thuận; nếu không có`
- Top-3: score=`0.3424`, title=`Law on Population 2025`, article=`17`, preview=`Chapter IV | ADAPTATION TO POPULATION AGEING Article 17. Active preparation for old age  1. Individuals shall actively prepare for old age when young via:  a) Preparation of health, finance, and psychology;  b) Participa`

## Mode: `gold_filter`

- top1 exact rate: `1.0` | top3 exact rate: `1.0` | pass rate: `0.8` | avg keyword recall: `0.8333`

| ID | Query | Expected | Top-1 | Top-3 exact | Keyword recall | Pass |
|---|---|---|---|---|---:|---|
| q1 | Những phương thức bảo vệ quyền dân sự khi quyền dân sự bị xâm phạm là gì? | Bộ Luật dân sự 2015 / 11 | Bộ Luật dân sự 2015 / 11 | True | 1.0 | True |
| q2 | Một tổ chức cần những điều kiện nào để được công nhận là pháp nhân? | Bộ Luật dân sự 2015 / 74 | Bộ Luật dân sự 2015 / 74 | True | 1.0 | True |
| q3 | When is Vietnam's Population Day? | Law on Population 2025 / 5 | Law on Population 2025 / 5 | True | 1.0 | True |
| q4 | Name three banned business lines under the Law on Investment 2025. | Law on Investment 2025 / 6 | Law on Investment 2025 / 6 | True | 1.0 | True |
| q5 | In the Planning Law 2025, what is the national planning database? | Planning Law 2025 / 3 | Planning Law 2025 / 3 | True | 0.1667 | False |

### q1: Những phương thức bảo vệ quyền dân sự khi quyền dân sự bị xâm phạm là gì?

- Metadata filter: `{'document_title': 'Bộ Luật dân sự 2015', 'article_number': '11', 'language': 'vi'}`
- Gold answer: Khi quyền dân sự bị xâm phạm, chủ thể có quyền tự bảo vệ hoặc yêu cầu cơ quan, tổ chức có thẩm quyền công nhận và bảo đảm quyền dân sự, buộc chấm dứt hành vi xâm phạm, buộc xin lỗi cải chính công khai, buộc thực hiện nghĩa vụ, buộc bồi thường thiệt hại, hủy quyết định cá biệt trái pháp luật và các yêu cầu khác theo luật.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`-0.0594`, title=`Bộ Luật dân sự 2015`, article=`11`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương II | XÁC LẬP, THỰC HIỆN VÀ BẢO VỆ QUYỀN DÂN SỰ Điều 11. Các phương thức bảo vệ quyền dân sự  Khi quyền dân sự của cá nhân, pháp nhân bị xâm phạm thì chủ thể đó có quyền tự bảo vệ t`

### q2: Một tổ chức cần những điều kiện nào để được công nhận là pháp nhân?

- Metadata filter: `{'document_title': 'Bộ Luật dân sự 2015', 'article_number': '74', 'language': 'vi'}`
- Gold answer: Một tổ chức được công nhận là pháp nhân khi được thành lập theo luật, có cơ cấu tổ chức, có tài sản độc lập và tự chịu trách nhiệm bằng tài sản của mình, và nhân danh mình tham gia quan hệ pháp luật một cách độc lập.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`-0.0619`, title=`Bộ Luật dân sự 2015`, article=`74`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương IV | PHÁP NHÂN Điều 74. Pháp nhân  1. Một tổ chức được công nhận là pháp nhân khi có đủ các điều kiện sau đây:  a) Được thành lập theo quy định của Bộ luật này, luật khác có liên q`

### q3: When is Vietnam's Population Day?

- Metadata filter: `{'document_title': 'Law on Population 2025', 'article_number': '5', 'language': 'en'}`
- Gold answer: Vietnam's Population Day is December 26 each year.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`-0.1170`, title=`Law on Population 2025`, article=`5`, preview=`Chapter I | GENERAL PROVISIONS Article 5. Vietnam’s Population Day, National Action Month on Population  1. Vietnam’s Population Day is December 26 each year.  ...  ...  ...`

### q4: Name three banned business lines under the Law on Investment 2025.

- Metadata filter: `{'document_title': 'Law on Investment 2025', 'article_number': '6', 'language': 'en'}`
- Gold answer: Examples of banned business lines include business in narcotic substances, prostitution business, human trafficking and trade in human tissues or organs, business activities pertaining to asexual human reproduction, trade in firecrackers, debt collection services, national treasures, relics and antiques, and electronic cigarettes or heated tobacco products.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`-0.0087`, title=`Law on Investment 2025`, article=`6`, preview=`Chapter I | GENERAL PROVISIONS Article 6. Banned business lines  1. The business investment activities below are banned:  a) Business in narcotic substances as specified in Appendix I to this Law;  ...  ...  ...  c) Busi`

### q5: In the Planning Law 2025, what is the national planning database?

- Metadata filter: `{'document_title': 'Planning Law 2025', 'article_number': '3', 'language': 'en'}`
- Gold answer: The national planning database is a collection of planning databases, planning-related information and data, arranged and organized to meet requirements for access, exploitation, sharing, management and updating.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`0.1667`, pass=`False`
- Top-1: score=`0.2151`, title=`Planning Law 2025`, article=`3`, preview=`Chapter I | GENERAL PROVISIONS Article 3. Definitions  3. “national marine spatial planning scheme” means a national-level planning scheme which concretizes the national master planning scheme in terms of the orientation`
- Top-2: score=`0.1967`, title=`Planning Law 2025`, article=`3`, preview=`Chapter I | GENERAL PROVISIONS Article 3. Definitions  17. “planning map” means a map that presents principal contents of a planning scheme at a specified scale. Planned geographical features are shown on the map with an`
- Top-3: score=`-0.0705`, title=`Planning Law 2025`, article=`3`, preview=`Chapter I | GENERAL PROVISIONS Article 3. Definitions  6. “region” means part of a national territory that embraces some adjacent provinces and cities which are formed on the basis of the geographical, economic, social, `
