# TEST INKA2

---
1. Explain ranking of results based on Diminishing Returns (RRF)
> ### Algorithm Breakdown:
> For each `chunk_id`:
> 1. **Initialize a score**: Set the initial score to 0.
> 2. **Check in semantic ranking**:
>
> $$
> \text{score} = \text{semantic_weight} \times \frac{1}{\text{index} + 1}
> $$
>
> 3. **Check in BM25 ranking**:
>
> $$
> \text{score} = \text{bm25_weight} \times \frac{1}{\text{index} + 1}
> $$
>
> The total score for a `chunk_id` is computed as:
>
> $$
> \text{Total Score} =
> \begin{cases}
> \text{semantic_weight} \times \frac{1}{\text{semantic_index} + 1}, & \text{if chunk is in semantic ranking} \\
> \text{bm25_weight} \times \frac{1}{\text{bm25_index} + 1}, & \text{if chunk is in BM25 ranking}
> \end{cases}
> $$
>
> ### Why This Makes Sense:
> ### Why This Makes Sense:
> 1. **Weighted Combination**: The algorithm combines two different ranking systems (semantic search and BM25), which may capture different aspects of relevance:
>    - **Semantic Search**: Captures meaning and context, useful for understanding the intent of a query.
>    - This scoring method, $ \frac{1}{\text{index} + 1} $, ensures that higher-ranked results
>    - This scoring method, $\frac{1}{\text{index} + 1}$, ensures that higher-ranked results
>
> 4. **Robust to Different Search Methods**: By combining different methods with their respective weights, the algorithm balances precision (semantic search) and recall (BM25).
> [Reciprocal Rank Fusion (RRF)](https://medium.com/@devalshah1619/mathematical-intuition-behind-reciprocal-rank-fusion-rrf-explained-in-2-mins-002df0cc5e2a)

---

