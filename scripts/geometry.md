# Concept Geometry Analysis Algorithms

This document describes the algorithms used in `geometry.py` for concept geometry analysis.

## 1. Vector Extraction

### Mean Pooling

Extract semantic vectors from transformer models using mean pooling over hidden states.

```python
def get_vector(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    
    # Get last hidden state
    h = outputs.last_hidden_state  # shape: [1, seq_len, hidden_dim]
    
    # Mean pooling over tokens
    mask = inputs["attention_mask"].unsqueeze(-1)
    vec = (h * mask).sum(dim=1) / mask.sum(dim=1)
    
    return vec[0]  # shape: [hidden_dim]
```

**Why mean pooling:**
- CLS token is task-specific (classification fine-tuning)
- Mean pooling captures all token information
- Weighted by attention mask to ignore padding tokens

**Limitations:**
- Single characters may not have rich semantics
- Longer texts dilute meaning across tokens
- Layer selection affects semantic purity

## 2. Concept Axis Construction

### Definition

A concept axis represents a semantic direction in embedding space, defined as the vector difference between positive and negative poles.

```python
def concept_axis(pos, neg):
    p = get_vector(pos)  # positive pole
    n = get_vector(neg)  # negative pole
    return p - n         # direction vector
```

**Example:**
- `concept_axis("好", "坏")` → direction from "bad" towards "good"
- `concept_axis("对", "错")` → direction from "wrong" towards "right"

**Properties:**
- Normalized cosine similarity with axis indicates position along the dimension
- Positive score → closer to positive pole
- Negative score → closer to negative pole

### Multi-Pair Averaging (Recommended)

Reduce noise by averaging multiple word pairs:

```python
pairs = [("好", "坏"), ("优秀", "差"), ("成功", "失败")]
axis = mean([concept_axis(p, n) for p, n in pairs])
```

## 3. Similarity Metrics

### Cosine Similarity

Measure semantic relatedness between vectors:

```python
def cosine(a, b):
    return F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()
```

**Interpretation:**
- 1.0 = identical direction
- 0.0 = orthogonal (unrelated)
- -1.0 = opposite direction

**Why cosine:**
- Magnitude-independent (compares direction only)
- Robust to embedding scaling
- Standard metric in NLP

## 4. Opposition Metrics

### 4.1 Simple Opposition (1 - Similarity)

```python
opposition = 1 - similarity
```

**Range:** 0 (identical) to 1 (orthogonal) to 2 (opposite)

**Limitation:** Assumes opposition at similarity = 0, not considering negative similarities well.

### 4.2 Angle-Based Opposition

```python
angle = arccos(similarity) * 180 / π  # degrees
normalized_angle = angle / 180  # range [0, 1]
```

**Interpretation:**
- 0° = identical
- 90° = orthogonal
- 180° = opposite

**Advantage:** Geometrically intuitive, handles negative similarities.

### 4.3 Axis Projection Separation

Project words onto their own concept axis:

```python
axis = vector(pos) - vector(neg)
proj_pos = cosine(vector(pos), axis)  # should be positive
proj_neg = cosine(vector(neg), axis)  # should be negative
separation = proj_pos - proj_neg      # larger = better separation
```

**Interpretation:**
- Well-separated pairs: positive projection on positive pole, negative on negative pole
- Separation > 1.0 indicates good opposition
- Captures directional opposition even with high similarity

**Example Results:**
| Pair | Similarity | Separation | Interpretation |
|------|-----------|------------|----------------|
| 对-错 | 0.44 | 1.06 | Good opposition |
| 好-坏 | 0.63 | 0.86 | Moderate opposition |
| 客观-主观 | 0.77 | ~0.50 | Poor opposition |

## 5. Rotation Methods

### 5.1 None (Baseline)

Use raw embeddings without transformation.

### 5.2 PCA Rotation

Rotate embedding space to principal component axes:

```python
from sklearn.decomposition import PCA

# Fit PCA on vocabulary
vectors = stack([get_vector(w) for w in vocabulary])
pca = PCA(n_components=len(vocabulary))
pca.fit(vectors)

# Transform vectors
rotated = pca.transform(vector)
```

**Effect:**
- Orthogonal transformation (preserves angles)
- Slight improvement in separation
- No bias introduced

### 5.3 PCA Alignment (Experimental)

Project concept axes onto top principal components:

```python
top_components = pca.components_[:k]  # top-k PCs
projection = axis @ top_components.T
aligned = projection @ top_components
```

**Effect:**
- Significantly improves similarity scores
- May introduce artificial correlation
- Use with caution for validation

## 6. Cross-Language Analysis

### Concept Alignment

Compare concept axes across languages:

```python
axis_zh = concept_axis("好", "坏")
axis_en = concept_axis("good", "bad")
alignment = cosine(axis_zh, axis_en)
```

**Findings:**
- good-bad: 0.90 (highly aligned)
- correct-error: 0.90 (highly aligned)
- yes-no: 0.15 (poorly aligned)

### Vocabulary Mapping

| Chinese | English | Note |
|---------|---------|------|
| 善 | good/kind | Different from "good" (好) |
| 正 | righteous | Different from "right" (对) |
| 邪 | wicked | Different from "evil" (恶) |

## 7. Statistical Considerations

### Sample Size

PCA requires more samples than dimensions:
- BERT: 768 dimensions → need >768 words
- Qwen: 4096 dimensions → need >4096 words
- Current: ~60 words → unreliable PCA

### Noise Sources

1. **Tokenization:** Single characters may split into subwords
2. **Polysemy:** Words with multiple meanings
3. **Context independence:** No sentence context for disambiguation
4. **Model bias:** Training data cultural biases

### Recommended Practices

1. Use multi-pair averaging for concept axes
2. Test across multiple models
3. Validate with human judgments
4. Report confidence intervals

## 8. Theoretical Interpretation

### Why Opposition is Rarely Observed

Opposite concepts often share semantic features:
- "hot" and "cold" share "temperature" feature
- "good" and "bad" share "value judgment" feature
- Opposition is directional, not positional

**Implication:**
- Low opposition scores don't invalidate the theory
- Concept axes capture direction, not absolute position
- Separation is the key metric, not similarity

### Concept Geometry vs. Concept Logic

| Aspect | Geometry | Logic |
|--------|----------|-------|
| Representation | Vector space | Formal symbols |
| Opposition | Directional (180°) | Logical negation |
| Similarity | Cosine similarity | Set intersection |
| Advantage | Continuous, measurable | Precise, discrete |

**Integration:**
- Geometry provides empirical validation
- Logic provides normative definition
- Both needed for complete understanding
