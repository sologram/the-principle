# Concept Geometry Analysis

Semantic space analysis tool for verifying the six laws of Principle of Things.

Two versions available:
- **geometry.py** — Manual semantic axes (v2.3)
- **geometry4.py** — Auto-discovered semantic axes (v4.0, recommended)

## Quick Start

### v4.0 Auto-discovery (Recommended)

```bash
# Full analysis
python geometry4.py --task all

# Learn semantic axes only
python geometry4.py --task learn

# Verify opposite pairs
python geometry4.py --task opposites

# Verify laws
python geometry4.py --task verify
```

### v2.3 Manual Version

```bash
# Full analysis
python geometry.py --task all

# Verify single law
python geometry.py --task law1
```

## Version Comparison

| Feature | v2.3 (geometry.py) | v4.0 (geometry4.py) |
|---------|-------------------|---------------------|
| Semantic Axes | Manually defined | Auto-learned from opposite pairs |
| Verification Method | Single cosine similarity | Multi-method (cosine, projection, angle) |
| Opposite Pair Rate | 0-33% | **89%** |
| Laws Verified | 0/6 | **6/6** |
| Axis Count | Fixed 4 | Configurable (default 8) |

## v4.0 Command Line Arguments

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--model` | str | `infoxlm-large` | Language model |
| `--layer` | str | `0` | Extraction layer |
| `--task` | str | `all` | Analysis task |
| `--n-axes` | int | `8` | Number of semantic axes to learn |

### v4.0 Task Types

| Value | Description |
|-------|-------------|
| `learn` | Learn semantic axes from opposite pairs |
| `opposites` | Verify opposite word pairs |
| `positives` | Verify positive word pairs |
| `verify` | Verify all laws |
| `all` | Full analysis pipeline |

## v4.0 Verification Methods

Three methods combined for opposite pair verification:

1. **Cosine similarity**: Similarity < -0.3 in semantic space
2. **Projection separation**: Separation > 0.5 on best-matching axis
3. **Angle method**: Angle > 90° in semantic space

Criteria: At least two methods must pass.

## Configuration Files

Law configurations in `laws/law*.yaml`:

```yaml
name: Complete is Correct
theory: No correctness allows any omission

positive_pairs:
  - [complete, correct]
  - [determined, objective]

opposite_pairs:
  - [complete, incomplete]
  - [correct, error]
```

**Note**: v4.0 doesn't need `semantic_axes` or `thresholds` fields.

## Verification Status

| Status | Rate | Description |
|--------|------|-------------|
| `verified` | ≥ 75% | Strong support |
| `partial` | 50% - 74% | Partial support |
| `not supported` | < 50% | Not supported |

## Reference

- [geometry.md](geometry.md) — Algorithm principles (Chinese)
- [THEORY.md](THEORY.md) — Experimental results (Chinese)
- [README-zh.md](README-zh.md) — Chinese documentation