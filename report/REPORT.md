# Báo Cáo Lab 7: Embedding & Vector Store

**Họ tên:** Huỳnh Nhựt Huy
**Nhóm:** 07
**Ngày:** 10/4/2026

---

## 1. Warm-up (5 điểm)

### Cosine Similarity (Ex 1.1)
No math required — explain conceptually:

**High cosine similarity nghĩa là gì?**
> *Viết 1-2 câu:*
High cosine similarity nghĩa là hai text chunks có semantic content tương tự nhau, được biểu diễn bởi các embedding vectors pointing trong gần như cùng vị trí (direction) trong không gian nhiều chiều

**Ví dụ HIGH similarity:**
- Sentence A: Trọng lực là lực hút của Trái Đất.
- Sentence B: Trọng lực của Trái Đất là lý do khiến quả táo rơi xuống.
- Tại sao tương đồng: Cùng chủ đề là gravity, cùng semantic meaning (Trọng lực, Trái Đất => nên là vector gần nhau hơn về hướng)

**Ví dụ LOW similarity:**
- Sentence A: Đèn đỏ thì tất cả các phương tiện tham gia giao thông phải dừng lại.
- Sentence B: AI Agentic đang là xu hướng của thế giới
- Tại sao khác: Chủ đề hoàn toàn khác nhau (luật giao thông và xu hướng của AI), các vector orthogonal (tức là vuông góc trong không gian, cosine similarity ~ 0)

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**
> *Viết 1-2 câu:*
-Không phụ thuộc vào độ dài của vector: Cosine chỉ quan tâm đến góc (angle), không bị ảnh hưởng bởi độ dài text. Điều này quan trọng vì text dài hơn không cần có nghĩa là khác sematic.
- Normalization độ dài của text: Trong NLP, document dài thì thường có embedding magnitude (độ lớn của vector biểu diễn) lớn hơn do nhiều từ hơn. Cosine sẽ normalize cái này (chia lại cho |u|.|v|)
- Semantic focus: Cosine sẽ capture các pattern của nội dung (từ nào quan trọng hơn) thay vì dùng các absolute distance
=> Cosine quan tâm góc, Euclidean quan tâm độ dài.
### Chunking Math (Ex 1.2)

**Document 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> *Trình bày phép tính:* num_chunks = ceil((doc_length - overlap) / (chunk_size - overlap))
=> ceil(10.000-50)/(500-50) ~ 22.11111 = 23
> *Đáp án:*
=> Đáp án là 23

**Nếu overlap tăng lên 100, chunk count thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**
> *Viết 1-2 câu:*
Nếu tăng overlap lên áp dụng công thức tương tự, ta có ceil(10.000-100)/(500-100) ~ 24.75 = 25
Chunk count sẽ tăng lên khi mà chúng ta tăng overlap.
Muốn overlap nhiều hơn để đảm bảo tính liên tục của ngữ cảnh giữa các chunk, tránh mất những thông tin quan trọng ở ranh giới của các chunk, thông tin không bị cắt đột ngột ở các boundary, nếu ít chunk hơn có thể bị mất context ở giữa các chunk và retrieval kém. Tuy nhiên, overlap cao thì số lượng chunk cũng tăng theo, dẫn đến chi phí lưu trữ và tính toán sẽ tốn nhiều hơn.
---

## 2. Document Selection — Nhóm (10 điểm)

### Domain & Lý Do Chọn

**Domain:** [ví dụ: Customer support FAQ, Vietnamese law, cooking recipes, ...]

**Tại sao nhóm chọn domain này?**
> *Viết 2-3 câu:*

### Data Inventory

| # | Tên tài liệu | Nguồn | Số ký tự | Metadata đã gán |
|---|--------------|-------|----------|-----------------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

### Metadata Schema

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|----------------|------|---------------|-------------------------------|
| | | | |
| | | | |

---

## 3. Chunking Strategy — Cá nhân chọn, nhóm so sánh (15 điểm)

### Baseline Analysis

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Strategy | Chunk Count | Avg Length | Preserves Context? |
|-----------|----------|-------------|------------|-------------------|
| Bộ Luật dân sự 2015 | FixedSizeChunker (`fixed_size`) | 297 | 1398.03 | Trung bình, full coverage nhưng hay cắt ngang ranh giới Điều |
| Bộ Luật dân sự 2015 | SentenceChunker (`by_sentences`) | 1017 | 362.02 | Trung bình thấp, chỉ giữ được khoảng 31.64% article coverage |
| Bộ Luật dân sự 2015 | RecursiveChunker (`recursive`) | 2957 | 123.45 | Thấp, chunk quá vụn và làm loãng ngữ cảnh pháp lý |
| Law on Investment 2025 | FixedSizeChunker (`fixed_size`) | 85 | 1399.45 | Trung bình, ít chunk nhưng không bám theo cấu trúc Điều |
| Law on Investment 2025 | SentenceChunker (`by_sentences`) | 216 | 487.07 | Trung bình thấp, article coverage chỉ khoảng 51.06% |
| Law on Investment 2025 | RecursiveChunker (`recursive`) | 1214 | 85.29 | Thấp, quá nhiều chunk nhỏ nên retrieval kém ổn định |
| Planning Law 2025 | FixedSizeChunker (`fixed_size`) | 102 | 1397.79 | Trung bình, còn giữ coverage nhưng hay lệch khỏi heading quan trọng |
| Planning Law 2025 | SentenceChunker (`by_sentences`) | 248 | 509.15 | Thấp, article coverage chỉ khoảng 27.78% |
| Planning Law 2025 | RecursiveChunker (`recursive`) | 1077 | 115.99 | Thấp, chunk nhỏ và phân mảnh ngữ cảnh |

### Strategy Của Tôi

**Loại:** custom strategy `structured_legal`

**Mô tả cách hoạt động:**
> *Viết 3-4 câu: strategy chunk thế nào? Dựa trên dấu hiệu gì?*
Strategy này nhận diện cấu trúc pháp lý song ngữ Việt/Anh theo các mốc `Phần/Chương/Mục/Điều` và `Part/Chapter/Section/Article`, sau đó cắt văn bản theo từng Điều thay vì theo kích thước thuần túy. Với các Điều quá dài, nó tiếp tục tách theo khoản/điểm để giữ mỗi chunk nằm trong budget mà vẫn không làm vỡ cấu trúc lập luận. Ngoài nội dung chính, mỗi chunk còn giữ breadcrumb như chapter/section/article title để tăng độ chính xác khi retrieval. Cách làm này phù hợp với luật vì thông tin quan trọng thường gắn trực tiếp với ranh giới Điều.

**Tại sao tôi chọn strategy này cho domain nhóm?**
> *Viết 2-3 câu: domain có pattern gì mà strategy khai thác?*
Domain luật có cấu trúc rất rõ theo Điều, Khoản, Mục và phần lớn câu trả lời truy vấn đều bám vào đúng một Điều cụ thể. Nếu chunking không tôn trọng ranh giới Điều thì retrieval dễ trả về đoạn có semantic gần nhưng sai căn cứ pháp lý. `structured_legal` tận dụng đúng pattern này, đồng thời xử lý được cả tài liệu tiếng Việt lẫn tiếng Anh trong cùng corpus.

**Code snippet (nếu custom):**
```python
# structured_legal:
# 1. detect Part/Chapter/Section/Article headings
# 2. split by legal article first
# 3. split long articles by clauses/points when needed
# 4. keep breadcrumb + article metadata for retrieval
```

### So Sánh: Strategy của tôi vs Baseline

| Tài liệu | Strategy | Chunk Count | Avg Length | Retrieval Quality? |
|-----------|----------|-------------|------------|--------------------|
| Bộ Luật dân sự 2015 | best baseline = `fixed_size` | 297 | 1398.03 | Khá, nhưng còn cắt ngang Điều và khó truy vết căn cứ |
| Bộ Luật dân sự 2015 | **của tôi = structured_legal** | 715 | 623.75 | Tốt hơn rõ rệt, giữ 100% article coverage và bám đúng Điều |
| Law on Investment 2025 | best baseline = `fixed_size` | 85 | 1399.45 | Khá, nhưng mất ranh giới các điều cấm/điều kiện |
| Law on Investment 2025 | **của tôi = structured_legal** | 114 | 1044.65 | Rất tốt, 0 oversized chunks, heading-start ratio = 1.0 |
| Planning Law 2025 | best baseline = `fixed_size` | 102 | 1397.79 | Khá, nhưng dễ trả về chunk đúng chủ đề mà chưa đúng định nghĩa |
| Planning Law 2025 | **của tôi = structured_legal** | 135 | 1068.76 | Tốt nhất cho domain này, top-3 relevant đạt 100% trên benchmark Gemini |

### So Sánh Với Thành Viên Khác

| Thành viên | Strategy | Retrieval Score (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| Tôi (Huỳnh Nhựt Huy - 2A202600084) | `structured_legal` | 9.5/10 | Giữ được 100% article coverage, bám rất sát cấu trúc luật song ngữ và retrieval ổn định trên mixed legal corpus | Tốn thời gian hơn ở bước embedding/index toàn bộ tài liệu |
| Nguyễn Ngọc Khánh Duy - 2A202600189 | `LegalArticleChunker` | 9/10 | Giữ trọn vẹn bối cảnh Điều luật, giảm khoảng 4x số chunks nên tiết kiệm chi phí | Avg cosine score thấp hơn do chunk dài; cần chỉnh regex nếu format header thay đổi |
| Nguyễn Ngọc Hưng - 2A202600188 | `RecursiveChunker (tuned)` | 8/10 | Tôn trọng cấu trúc markdown, chunk coherent | Chunk count cao hơn, tốn memory và dễ phân mảnh với luật dài |
| Huỳnh Lê Xuân Ánh - 2A202600083 | `sentence` | 8.5/10 | Chunk size cân đối, similarity score đồng đều, đủ tốt với tài liệu không quá dài | Không tối ưu cho tài liệu luật rất dài hoặc nhiều Điều dài |

**Strategy nào tốt nhất cho domain này? Tại sao?**
> *Viết 2-3 câu:*
Trong domain luật, tôi đánh giá `structured_legal` là strategy tốt nhất về tổng thể vì nó vừa giữ đúng cấu trúc Điều luật, vừa tránh oversized chunks, đồng thời hoạt động ổn trên corpus song ngữ Việt/Anh. `LegalArticleChunker` của Duy là phương án rất tốt nếu ưu tiên giảm chi phí và số chunk, nhưng `structured_legal` cân bằng tốt hơn giữa article coverage, độ chính xác retrieval và khả năng xử lý các Điều dài.

---

## 4. My Approach — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi implement các phần chính trong package `src`.

### Chunking Functions

**`SentenceChunker.chunk`** — approach:
> *Viết 2-3 câu: dùng regex gì để detect sentence? Xử lý edge case nào?*
Sử dụng regex r'(?<=[.!?])\s+' với positive lookbehind để tách tại dấu câu mà không mất dấu câu trong kết quả. Edge cases xử lý: empty input trả về list rỗng; text không có dấu câu trả về single chunk; sentences được strip whitespace trước khi gom thành chunk. Mỗi chunk chứa tối đa max_sentences_per_chunk câu, đảm bảo tính ngữ pháp hoàn chỉnh.

**`RecursiveChunker.chunk` / `_split`** — approach:
> *Viết 2-3 câu: algorithm hoạt động thế nào? Base case là gì?*
Về logic: 
    Thử tách text bằng separator theo thứ tự ưu tiên: đoạn -> Câu -> từ -> Ký tự
    Nếu tách được, xử lý đệ quy cho từng phần
    Nếu không tách được hoặc phần tách vẫn dài, thử separator tiếp theo

Giải thích: Algorithm hoạt động theo chiến lược divide-and-conquer: thử tách text bằng separator theo thứ tự ưu tiên (đoạn → câu → từ → ký tự), nếu tách được thì đệ quy xử lý từng phần, nếu không thì thử separator tiếp theo. Base case là khi len(current_text) <= chunk_size hoặc hết separator (force split by character). RecursiveChunker ưu tiên giữ cấu trúc semantic của văn bản bằng cách thử tách tại ranh giới tự nhiên trước khi xuống mức từ hoặc ký tự.

### EmbeddingStore

**`add_documents` + `search`** — approach:
> *Viết 2-3 câu: lưu trữ thế nào? Tính similarity ra sao?*
Lưu trữ dạng vector embeddings được tính bằng embedding_fn cho mỗi document content. ChromaDB được ưu tiên nếu available (persistent, scalable), ngược lại fallback về in-memory list of dicts. Similarity được tính bằng dot product giữa query embedding và stored embeddings — vì embeddings đã được normalize (hoặc dùng cosine similarity tương đương), dot product đủ để ranking. Kết quả được sort descending theo score và giới hạn bởi top_k.

**`search_with_filter` + `delete_document`** — approach:
> *Viết 2-3 câu: filter trước hay sau? Delete bằng cách nào?*
Filter được áp dụng trước similarity search: lọc records trong store theo metadata key-value match, sau đó chỉ search trong subset đã lọc. Điều này tăng precision nhưng có thể giảm recall nếu filter quá chặt. Delete hoạt động bằng cách xóa tất cả records có metadata['doc_id'] khớp với target doc_id — trong ChromaDB dùng where filter để lấy IDs rồi xóa, trong in-memory dùng list comprehension để rebuild store excluding matched records.

### KnowledgeBaseAgent

**`answer`** — approach:
> *Viết 2-3 câu: prompt structure? Cách inject context?*
Prompt structure theo RAG pattern: system instruction + retrieved context được format với index markers [1], [2]... + user question. Context được inject bằng cách nối top-k chunks với separator \n\n, mỗi chunk prefix bằng index để dễ traceability. LLM được instruct rõ ràng: "If the answer cannot be found in the context, say 'I don't have enough information'" để tránh hallucination. Final prompt được pass vào llm_fn để generate answer.

### Test Results

```
# Paste output of: pytest tests/ -v
```
=========================================== test session starts ============================================
platform win32 -- Python 3.10.0, pytest-9.0.3, pluggy-1.6.0 -- D:\VinUni\assignments\Day_7_Lab_data\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: D:\VinUni\assignments\Day_7_Lab_data
collected 42 items                                                                                          

tests/test_solution.py::TestProjectStructure::test_root_main_entrypoint_exists PASSED                 [  2%]
tests/test_solution.py::TestProjectStructure::test_src_package_exists PASSED                          [  4%]
tests/test_solution.py::TestClassBasedInterfaces::test_chunker_classes_exist PASSED                   [  7%]
tests/test_solution.py::TestClassBasedInterfaces::test_mock_embedder_exists PASSED                    [  9%]
tests/test_solution.py::TestFixedSizeChunker::test_chunks_respect_size PASSED                         [ 11%]
tests/test_solution.py::TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED         [ 14%]
tests/test_solution.py::TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED               [ 16%]
tests/test_solution.py::TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED                [ 19%]
tests/test_solution.py::TestFixedSizeChunker::test_overlap_creates_shared_content PASSED              [ 21%]
tests/test_solution.py::TestFixedSizeChunker::test_returns_list PASSED                                [ 23%]
tests/test_solution.py::TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED                [ 26%]
tests/test_solution.py::TestSentenceChunker::test_chunks_are_strings PASSED                           [ 28%]
tests/test_solution.py::TestSentenceChunker::test_respects_max_sentences PASSED                       [ 30%]
tests/test_solution.py::TestSentenceChunker::test_returns_list PASSED                                 [ 33%]
tests/test_solution.py::TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED        [ 35%]
tests/test_solution.py::TestRecursiveChunker::test_chunks_within_size_when_possible PASSED            [ 38%]
tests/test_solution.py::TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED      [ 40%]
tests/test_solution.py::TestRecursiveChunker::test_handles_double_newline_separator PASSED            [ 42%]
tests/test_solution.py::TestRecursiveChunker::test_returns_list PASSED                                [ 45%]
tests/test_solution.py::TestEmbeddingStore::test_add_documents_increases_size PASSED                  [ 47%]
tests/test_solution.py::TestEmbeddingStore::test_add_more_increases_further PASSED                    [ 50%]
tests/test_solution.py::TestEmbeddingStore::test_initial_size_is_zero PASSED                          [ 52%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_content_key PASSED               [ 54%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_have_score_key PASSED                 [ 57%]
tests/test_solution.py::TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED     [ 59%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_at_most_top_k PASSED                  [ 61%]
tests/test_solution.py::TestEmbeddingStore::test_search_returns_list PASSED                           [ 64%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_non_empty PASSED                          [ 66%]
tests/test_solution.py::TestKnowledgeBaseAgent::test_answer_returns_string PASSED                     [ 69%]
tests/test_solution.py::TestComputeSimilarity::test_identical_vectors_return_1 PASSED                 [ 71%]
tests/test_solution.py::TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED            [ 73%]
tests/test_solution.py::TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED                [ 76%]
tests/test_solution.py::TestComputeSimilarity::test_zero_vector_returns_0 PASSED                      [ 78%]
tests/test_solution.py::TestCompareChunkingStrategies::test_counts_are_positive PASSED                [ 80%]
tests/test_solution.py::TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED [ 83%]
tests/test_solution.py::TestCompareChunkingStrategies::test_returns_three_strategies PASSED           [ 85%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED          [ 88%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED [ 90%]
tests/test_solution.py::TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED         [ 92%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED  [ 95%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED [ 97%]
tests/test_solution.py::TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED [100%]

============================================ 42 passed in 0.15s ============================================

**Số tests pass:** 42 / 42

---

## 5. Similarity Predictions — Cá nhân (5 điểm)

| Pair | Sentence A | Sentence B | Dự đoán | Actual Score | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Trí tuệ nhân tạo đang thay đổi cách chúng ta làm việc | AI đang cách mạng hóa workflow hiện đại | high | | |
| 2 |Hà Nội là thủ đô của Việt Nam | Phở là món ăn truyền thống Việt Nam| low | | |
| 3 |Máy tính lượng tử sử dụng qubit thay vì bit |Quantum computer dùng qubit instead of classical bit | high | | |
| 4 | Nhiệt độ hôm nay là 30 độ C|Thời tiết nóng 30°C | high | | |
| 5 | Chính phủ ban hành luật mới về thuế thu thập cá nhân| Công ty Apple ra mắt iPhone 16| low | | |

Khi dùng mockEmbedder: Gần như là không bắt được ngữ nghĩa
Similarity Predictions
================================================================================
Embedding backend: mock embeddings fallback
--------------------------------------------------------------------------------
Pair 1
Sentence A : Python is a popular programming language for data analysis.
Sentence B : Python is widely used to analyze data and build software.
Prediction : high
Actual score: 0.0155
Actual label: low
Match      : no
--------------------------------------------------------------------------------
Pair 2
Sentence A : Machine learning models learn patterns from historical data.
Sentence B : Cooking pasta requires boiling water and adding salt.
Prediction : low
Actual score: -0.1054
Actual label: low
Match      : yes
--------------------------------------------------------------------------------
Pair 3
Sentence A : Vector databases help retrieve similar embeddings quickly.
Sentence B : Embedding stores are useful for similarity search in RAG systems.
Prediction : high
Actual score: -0.0285
Actual label: low
Match      : no
--------------------------------------------------------------------------------
Pair 4
Sentence A : The customer support guide explains refund procedures.
Sentence B : Neural networks are trained with gradient-based optimization.
Prediction : low
Actual score: 0.0753
Actual label: low
Match      : yes
--------------------------------------------------------------------------------
Pair 5
Sentence A : Sentence chunking groups text based on sentence boundaries.
Sentence B : Recursive chunking also splits text, but follows separator priority.
Prediction : high
Actual score: 0.1874
Actual label: low
Match      : no
--------------------------------------------------------------------------------
Embedding backend: models/gemini-embedding-2-preview
--------------------------------------------------------------------------------
Pair 1
Sentence A : Trí tuệ nhân tạo đang thay đổi cách chúng ta làm việc
Sentence B : AI đang cách mạng hóa workflow hiện đại
Prediction : high
Actual score: 0.7816
Actual label: high
Match      : yes
--------------------------------------------------------------------------------
Pair 2
Sentence A : Hà Nội là thủ đô của Việt Nam
Sentence B : Phở là món ăn truyền thống Việt Nam
Prediction : low
Actual score: 0.7111
Actual label: low
Match      : yes
--------------------------------------------------------------------------------
Pair 3
Sentence A : Máy tính lượng tử sử dụng qubit thay vì bit
Sentence B : Quantum computer dùng qubit instead of classical bit
Prediction : high
Actual score: 0.8366
Actual label: high
Match      : yes
--------------------------------------------------------------------------------
Pair 4
Sentence A : Nhiệt độ hôm nay là 30 độ C
Sentence B : Thời tiết nóng 30°C
Prediction : high
Actual score: 0.8461
Actual label: high
Match      : yes
--------------------------------------------------------------------------------
Pair 5
Sentence A : Chính phủ ban hành luật mới về thuế thu thập cá nhân
Sentence B : Công ty Apple ra mắt iPhone 16
Prediction : low
Actual score: 0.5745
Actual label: low
Match      : yes

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn nghĩa?**
> *Viết 2-3 câu:*
Kết quả bất ngờ nhất mà tôi nhận thấy là khi nhìn vào Pair 1,3,4. Ở pair thứ nhất và pair thứ 3 gần như ý nghĩa giống nhau 100% giữa 2 sentence tuy nhiên thì điểm nó lại không quá cao, điều này có thể là do embeddings chưa hoạt động hoàn hảo trên multilingual. Và đối với pair 5, embeddings biểu diễn nghĩa rất hay khi mà biết được rằng cả 2 chủ thể điều cùng cho ra một cái gì đó mới nhưng vẫn đủ thấp để không lẫn lộn.
---

## 6. Results — Cá nhân (10 điểm)

Chạy 5 benchmark queries của nhóm trên implementation cá nhân của bạn trong package `src`. **5 queries phải trùng với các thành viên cùng nhóm.**

### Benchmark Queries & Gold Answers (nhóm thống nhất)

| # | Query | Gold Answer |
|---|-------|-------------|
| 1 |What is the scope of regulation under Law on Press | This law provides for freedo of the press, citizens' freedome of expression in the press. (Not for Vietnamese)|
| 2 |According to this Children Law, what age is considered a child| A child is a human being below the age of 16|
| 3 |When is Vietnam's Population Day?|Vietnam's Population Day is December 26 each year.|
| 4 |Name three banned business lines under the Law on Investment 2025.|Examples of banned business lines include business in narcotic substances, prostitution business, human trafficking and trade in human tissues or organs, business activities pertaining to asexual human reproduction, trade in firecrackers, debt collection services, national treasures, relics and antiques, and electronic cigarettes or heated tobacco products.|
| 5 |In the Planning Law 2025, what is the national planning database?|The national planning database is a collection of planning databases, planning-related information and data, arranged and organized to meet requirements for access, exploitation, sharing, management and updating.|

### Kết Quả Của Tôi

| # | Query | Top-1 Retrieved Chunk (tóm tắt) | Score | Relevant? | Agent Answer (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | What is the scope of regulation under Law on Press | Law on Press 2025, Article 1: quy định phạm vi điều chỉnh gồm tự do báo chí, quyền tự do ngôn luận trên báo chí, tổ chức và hoạt động báo chí, quyền nghĩa vụ của các chủ thể liên quan và quản lý nhà nước về báo chí. | 0.8615 | Yes | Law on Press regulates freedom of the press, citizens' freedom of expression in the press, organization and operation of the press, rights and obligations of related agencies/individuals, and state management of the press. |
| 2 | According to this Children Law, what age is considered a child | Children Law 2016, Article 1: định nghĩa child là con người dưới 16 tuổi. | 0.8268 | Yes | A child is a human being below the age of 16. |
| 3 | When is Vietnam's Population Day? | Law on Population 2025, Article 5: quy định Vietnam's Population Day là ngày 26/12 hằng năm. | 0.8548 | Yes | Vietnam's Population Day is December 26 each year. |
| 4 | Name three banned business lines under the Law on Investment 2025. | Law on Investment 2025, Article 6: liệt kê các ngành nghề cấm đầu tư kinh doanh. | 0.8183 | Yes | Three banned business lines include prostitution business, trade in firecrackers, and debt collection services. |
| 5 | In the Planning Law 2025, what is the national planning database? | Planning Law 2025, Article 45: mô tả cơ sở dữ liệu quy hoạch quốc gia và các thành phần của nó. | 0.8124 | Yes | The national planning database is a collection of planning databases and planning-related data organized for access, exploitation, sharing, management, and updating. |

**Bao nhiêu queries trả về chunk relevant trong top-3?** 5 / 5

---

## 7. What I Learned (5 điểm — Demo)

**Điều hay nhất tôi học được từ thành viên khác trong nhóm:**
> *Viết 2-3 câu:*

**Điều hay nhất tôi học được từ nhóm khác (qua demo):**
> *Viết 2-3 câu:*

**Nếu làm lại, tôi sẽ thay đổi gì trong data strategy?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá

| Tiêu chí | Loại | Điểm tự đánh giá |
|----------|------|-------------------|
| Warm-up | Cá nhân | / 5 |
| Document selection | Nhóm | / 10 |
| Chunking strategy | Nhóm | / 15 |
| My approach | Cá nhân | / 10 |
| Similarity predictions | Cá nhân | / 5 |
| Results | Cá nhân | / 10 |
| Core implementation (tests) | Cá nhân | / 30 |
| Demo | Nhóm | / 5 |
| **Tổng** | | **/ 100** |
