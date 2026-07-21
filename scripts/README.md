# Concept Geometry Analysis Tools

This directory contains tools for concept geometry analysis.

## geometry.py

Analyzes directional relationships between concepts in semantic space using hidden states from pretrained language models.

### Setup

```bash
pip install torch transformers scikit-learn
```

### Usage

```bash
# Basic usage (no rotation)
python geometry.py --model qwen3.5-9b --rotation none

# With PCA rotation
python geometry.py --model qwen3.5-9b --rotation pca

# With PCA alignment (recommended for better SNR)
python geometry.py --model qwen3.5-9b --rotation pca-align --top-k 5
```

### Command Line Options

| Option | Values | Default | Description |
|--------|--------|---------|-------------|
| `--model` | `bert-base-chinese`, `infoxlm-large`, `qwen3.5-9b` | `qwen3.5-9b` | Model to use |
| `--rotation` | `none`, `pca`, `pca-align` | `none` | Rotation method |
| `--top-k` | integer | `5` | Number of PCs for `pca-align` |

### Core Functions

#### `get_vector(text)`

Get semantic vector for text.

- **Parameters**: `text` (input text)
- **Returns**: Semantic vector (mean pooled)

#### `concept_axis(pos, neg)`

Construct concept axis (vector difference between positive and negative directions).

- **Parameters**: `pos` (positive word), `neg` (negative word)
- **Returns**: Concept direction vector

#### `cosine(a, b)`

Compute cosine similarity between two vectors.

- **Returns**: Similarity value between -1 and 1

### Example

```python
# Construct concept axes
axis_good_bad = concept_axis("好", "坏")
axis_efficient = concept_axis("高效", "低效")

# Compare concept directions
similarity = cosine(axis_good_bad, axis_efficient)
print(f"good-bad <-> efficient-inefficient: {similarity}")

# Projection analysis
words = ["合作", "信任", "欺骗", "破坏"]
for word in words:
    vec = get_vector(word)
    score = cosine(vec, axis_good_bad)
    print(f"{word}: {score}")
```

### Models

| Model | Description |
|-------|-------------|
| `bert-base-chinese` | 12-layer, 768-dim, general Chinese model (online) |
| `infoxlm-large` | Multilingual XLM, stronger Chinese understanding (local) |
| `qwen3.5-9b` | Qwen, strongest semantic understanding, requires more resources (local) |

Local models are located at `C:\Users\hans\Desktop\models`.

### Rotation Methods

| Method | Description | Effect |
|--------|-------------|--------|
| `none` | No rotation | Baseline |
| `pca` | Rotate to PCA space | Minimal effect on cosine similarity |
| `pca-align` | Align axes to top principal components | Significantly improves SNR, but may introduce bias |

### Improvement Suggestions

1. **Multi-pair averaging** — Define concept axes using multiple word pairs to reduce noise
2. **Layer selection** — Middle layers (e.g., -6 to -4) may be more "semantic" than the last layer
3. **Pooling strategy** — Consider CLS token or exclude `[CLS]`/`[SEP]` for longer sentences
4. **Vocabulary constraint** — Prefer words that exist as complete tokens in the model vocabulary

## Theory

See [THEORY.md](THEORY.md) for the relationship between concept geometry and the Principle of Things framework.
