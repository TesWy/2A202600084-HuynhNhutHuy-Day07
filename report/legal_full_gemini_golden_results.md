# Golden Query Evaluation

- Generated at: `2026-04-10T17:41:52`
- Embedding backend: `models/gemini-embedding-2-preview`
- Collection: `legal_full_gemini`
- Strategy: `structured_legal`
- Parameters: `chunk_size=1400`, `overlap=150`, `max_sentences=4`, `top_k=3`
- Source files indexed: `8`
- Stored chunks: `1398`

## Mode: `no_filter`

- top1 exact rate: `0.8` | top3 exact rate: `1.0` | pass rate: `1.0` | avg keyword recall: `1.0`

| ID | Query | Expected | Top-1 | Top-3 exact | Keyword recall | Pass |
|---|---|---|---|---|---:|---|
| q1 | Những phương thức bảo vệ quyền dân sự khi quyền dân sự bị xâm phạm là gì? | Bộ Luật dân sự 2015 / 11 | Bộ Luật dân sự 2015 / 11 | True | 1.0 | True |
| q2 | Một tổ chức cần những điều kiện nào để được công nhận là pháp nhân? | Bộ Luật dân sự 2015 / 74 | Bộ Luật dân sự 2015 / 74 | True | 1.0 | True |
| q3 | When is Vietnam's Population Day? | Law on Population 2025 / 5 | Law on Population 2025 / 5 | True | 1.0 | True |
| q4 | Name three banned business lines under the Law on Investment 2025. | Law on Investment 2025 / 6 | Law on Investment 2025 / 6 | True | 1.0 | True |
| q5 | In the Planning Law 2025, what is the national planning database? | Planning Law 2025 / 3 | Planning Law 2025 / 45 | True | 1.0 | True |

### q1: Những phương thức bảo vệ quyền dân sự khi quyền dân sự bị xâm phạm là gì?

- Gold answer: Khi quyền dân sự bị xâm phạm, chủ thể có quyền tự bảo vệ hoặc yêu cầu cơ quan, tổ chức có thẩm quyền công nhận và bảo đảm quyền dân sự, buộc chấm dứt hành vi xâm phạm, buộc xin lỗi cải chính công khai, buộc thực hiện nghĩa vụ, buộc bồi thường thiệt hại, hủy quyết định cá biệt trái pháp luật và các yêu cầu khác theo luật.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.8031`, title=`Bộ Luật dân sự 2015`, article=`11`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương II | XÁC LẬP, THỰC HIỆN VÀ BẢO VỆ QUYỀN DÂN SỰ Điều 11. Các phương thức bảo vệ quyền dân sự  Khi quyền dân sự của cá nhân, pháp nhân bị xâm phạm thì chủ thể đó có quyền tự bảo vệ t`
- Top-2: score=`0.7497`, title=`Bộ Luật dân sự 2015`, article=`14`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương II | XÁC LẬP, THỰC HIỆN VÀ BẢO VỆ QUYỀN DÂN SỰ Điều 14. Bảo vệ quyền dân sự thông qua cơ quan có thẩm quyền  1. Tòa án, cơ quan có thẩm quyền khác có trách nhiệm tôn trọng, bảo vệ `
- Top-3: score=`0.7350`, title=`Bộ Luật dân sự 2015`, article=`164`, preview=`Phần thứ hai | QUYỀN SỞ HỮU VÀ QUYỀN KHÁC ĐỐI VỚI TÀI SẢN | Chương XI | QUY ĐỊNH CHUNG | Mục 2. BẢO VỆ QUYỀN SỞ HỮU, QUYỀN KHÁC ĐỐI VỚI TÀI SẢN Điều 164. Biện pháp bảo vệ quyền sở hữu, quyền khác đối với tài sản  1. Chủ `

### q2: Một tổ chức cần những điều kiện nào để được công nhận là pháp nhân?

- Gold answer: Một tổ chức được công nhận là pháp nhân khi được thành lập theo luật, có cơ cấu tổ chức, có tài sản độc lập và tự chịu trách nhiệm bằng tài sản của mình, và nhân danh mình tham gia quan hệ pháp luật một cách độc lập.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.7863`, title=`Bộ Luật dân sự 2015`, article=`74`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương IV | PHÁP NHÂN Điều 74. Pháp nhân  1. Một tổ chức được công nhận là pháp nhân khi có đủ các điều kiện sau đây:  a) Được thành lập theo quy định của Bộ luật này, luật khác có liên q`
- Top-2: score=`0.7263`, title=`Bộ Luật dân sự 2015`, article=`86`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương IV | PHÁP NHÂN Điều 86. Năng lực pháp luật dân sự của pháp nhân  1. Năng lực pháp luật dân sự của pháp nhân là khả năng của pháp nhân có các quyền, nghĩa vụ dân sự. Năng lực pháp l`
- Top-3: score=`0.7204`, title=`Bộ Luật dân sự 2015`, article=`83`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương IV | PHÁP NHÂN Điều 83. Cơ cấu tổ chức của pháp nhân  1. Pháp nhân phải có cơ quan điều hành. Tổ chức, nhiệm vụ và quyền hạn của cơ quan điều hành của pháp nhân được quy định trong`

### q3: When is Vietnam's Population Day?

- Gold answer: Vietnam's Population Day is December 26 each year.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.8548`, title=`Law on Population 2025`, article=`5`, preview=`Chapter I | GENERAL PROVISIONS Article 5. Vietnam’s Population Day, National Action Month on Population  1. Vietnam’s Population Day is December 26 each year.  ...  ...  ...`
- Top-2: score=`0.7368`, title=`Law on Population 2025`, article=`30`, preview=`Chapter VIII | IMPLEMENTATION Article 30. Entry into force  ...  ...  ...  2. Regulations under Point c and Point d Clause 1 Article 14 of this Law come into force from January 1, 2027.  3. Ordinance for Population No. 0`
- Top-3: score=`0.7194`, title=`Law on Population 2025`, article=`7`, preview=`Chapter I | GENERAL PROVISIONS Article 7. Government policies regarding population  1. Population is the leading factor in construction, development, and protection of the country. Exercise population and growth policies`

### q4: Name three banned business lines under the Law on Investment 2025.

- Gold answer: Examples of banned business lines include business in narcotic substances, prostitution business, human trafficking and trade in human tissues or organs, business activities pertaining to asexual human reproduction, trade in firecrackers, debt collection services, national treasures, relics and antiques, and electronic cigarettes or heated tobacco products.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.8183`, title=`Law on Investment 2025`, article=`6`, preview=`Chapter I | GENERAL PROVISIONS Article 6. Banned business lines  1. The business investment activities below are banned:  a) Business in narcotic substances as specified in Appendix I to this Law;  ...  ...  ...  c) Busi`
- Top-2: score=`0.7766`, title=`Law on Investment 2025`, article=`52`, preview=`Chapter VII | IMPLEMENTATION CLAUSE Article 52. Transitional provisions  17. The Government shall elaborate this Article.  This Law was passed by the 15th National Assembly of the Socialist Republic of Vietnam on this 11`
- Top-3: score=`0.7636`, title=`Law on Investment 2025`, article=`40`, preview=`Chapter V | OUTWARD INVESTMENT ACTIVITIES Article 40. Business lines banned from outward investment  ...  ...  ...  2. Business lines with technologies and products banned from export in accordance with the law on foreig`

### q5: In the Planning Law 2025, what is the national planning database?

- Gold answer: The national planning database is a collection of planning databases, planning-related information and data, arranged and organized to meet requirements for access, exploitation, sharing, management and updating.
- Metrics: top1_exact=`False`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.8124`, title=`Planning Law 2025`, article=`45`, preview=`Chapter III | APPRAISAL, DECISION ON OR APPROVAL OF PLANNING SCHEMES | Section 1. ANNOUNCEMENT AND PROVISION OF INFORMATION ON PLANNING SCHEMES Article 45. National planning database  1. A national planning database shal`
- Top-2: score=`0.7806`, title=`Planning Law 2025`, article=`3`, preview=`Chapter I | GENERAL PROVISIONS Article 3. Definitions  13. “authority organizing planning scheme formulation” is the Government, Ministry or provincial People’s Committee which has the responsibility to organize formulat`
- Top-3: score=`0.7626`, title=`Planning Law 2025`, article=`44`, preview=`Chapter III | APPRAISAL, DECISION ON OR APPROVAL OF PLANNING SCHEMES | Section 1. ANNOUNCEMENT AND PROVISION OF INFORMATION ON PLANNING SCHEMES Article 44. National planning information system  1. The national planning i`

## Mode: `gold_filter`

- top1 exact rate: `1.0` | top3 exact rate: `1.0` | pass rate: `1.0` | avg keyword recall: `1.0`

| ID | Query | Expected | Top-1 | Top-3 exact | Keyword recall | Pass |
|---|---|---|---|---|---:|---|
| q1 | Những phương thức bảo vệ quyền dân sự khi quyền dân sự bị xâm phạm là gì? | Bộ Luật dân sự 2015 / 11 | Bộ Luật dân sự 2015 / 11 | True | 1.0 | True |
| q2 | Một tổ chức cần những điều kiện nào để được công nhận là pháp nhân? | Bộ Luật dân sự 2015 / 74 | Bộ Luật dân sự 2015 / 74 | True | 1.0 | True |
| q3 | When is Vietnam's Population Day? | Law on Population 2025 / 5 | Law on Population 2025 / 5 | True | 1.0 | True |
| q4 | Name three banned business lines under the Law on Investment 2025. | Law on Investment 2025 / 6 | Law on Investment 2025 / 6 | True | 1.0 | True |
| q5 | In the Planning Law 2025, what is the national planning database? | Planning Law 2025 / 3 | Planning Law 2025 / 3 | True | 1.0 | True |

### q1: Những phương thức bảo vệ quyền dân sự khi quyền dân sự bị xâm phạm là gì?

- Metadata filter: `{'document_title': 'Bộ Luật dân sự 2015', 'article_number': '11', 'language': 'vi'}`
- Gold answer: Khi quyền dân sự bị xâm phạm, chủ thể có quyền tự bảo vệ hoặc yêu cầu cơ quan, tổ chức có thẩm quyền công nhận và bảo đảm quyền dân sự, buộc chấm dứt hành vi xâm phạm, buộc xin lỗi cải chính công khai, buộc thực hiện nghĩa vụ, buộc bồi thường thiệt hại, hủy quyết định cá biệt trái pháp luật và các yêu cầu khác theo luật.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.8031`, title=`Bộ Luật dân sự 2015`, article=`11`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương II | XÁC LẬP, THỰC HIỆN VÀ BẢO VỆ QUYỀN DÂN SỰ Điều 11. Các phương thức bảo vệ quyền dân sự  Khi quyền dân sự của cá nhân, pháp nhân bị xâm phạm thì chủ thể đó có quyền tự bảo vệ t`

### q2: Một tổ chức cần những điều kiện nào để được công nhận là pháp nhân?

- Metadata filter: `{'document_title': 'Bộ Luật dân sự 2015', 'article_number': '74', 'language': 'vi'}`
- Gold answer: Một tổ chức được công nhận là pháp nhân khi được thành lập theo luật, có cơ cấu tổ chức, có tài sản độc lập và tự chịu trách nhiệm bằng tài sản của mình, và nhân danh mình tham gia quan hệ pháp luật một cách độc lập.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.7863`, title=`Bộ Luật dân sự 2015`, article=`74`, preview=`Phần thứ nhất | QUY ĐỊNH CHUNG | Chương IV | PHÁP NHÂN Điều 74. Pháp nhân  1. Một tổ chức được công nhận là pháp nhân khi có đủ các điều kiện sau đây:  a) Được thành lập theo quy định của Bộ luật này, luật khác có liên q`

### q3: When is Vietnam's Population Day?

- Metadata filter: `{'document_title': 'Law on Population 2025', 'article_number': '5', 'language': 'en'}`
- Gold answer: Vietnam's Population Day is December 26 each year.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.8548`, title=`Law on Population 2025`, article=`5`, preview=`Chapter I | GENERAL PROVISIONS Article 5. Vietnam’s Population Day, National Action Month on Population  1. Vietnam’s Population Day is December 26 each year.  ...  ...  ...`

### q4: Name three banned business lines under the Law on Investment 2025.

- Metadata filter: `{'document_title': 'Law on Investment 2025', 'article_number': '6', 'language': 'en'}`
- Gold answer: Examples of banned business lines include business in narcotic substances, prostitution business, human trafficking and trade in human tissues or organs, business activities pertaining to asexual human reproduction, trade in firecrackers, debt collection services, national treasures, relics and antiques, and electronic cigarettes or heated tobacco products.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.8183`, title=`Law on Investment 2025`, article=`6`, preview=`Chapter I | GENERAL PROVISIONS Article 6. Banned business lines  1. The business investment activities below are banned:  a) Business in narcotic substances as specified in Appendix I to this Law;  ...  ...  ...  c) Busi`

### q5: In the Planning Law 2025, what is the national planning database?

- Metadata filter: `{'document_title': 'Planning Law 2025', 'article_number': '3', 'language': 'en'}`
- Gold answer: The national planning database is a collection of planning databases, planning-related information and data, arranged and organized to meet requirements for access, exploitation, sharing, management and updating.
- Metrics: top1_exact=`True`, top3_exact=`True`, keyword_recall=`1.0`, pass=`True`
- Top-1: score=`0.7806`, title=`Planning Law 2025`, article=`3`, preview=`Chapter I | GENERAL PROVISIONS Article 3. Definitions  13. “authority organizing planning scheme formulation” is the Government, Ministry or provincial People’s Committee which has the responsibility to organize formulat`
- Top-2: score=`0.7535`, title=`Planning Law 2025`, article=`3`, preview=`Chapter I | GENERAL PROVISIONS Article 3. Definitions  For the purposes of this Law, the terms below shall be construed as follows:  1. “planning” means the orientations for development, arrangement and distribution of s`
- Top-3: score=`0.7285`, title=`Planning Law 2025`, article=`3`, preview=`Chapter I | GENERAL PROVISIONS Article 3. Definitions  10. “planning integration” means an integrated approach and comprehensive cooperation in addressing cross-sectoral, inter-regional, and inter-provincial issues relat`
