# Concept Geometry Analysis

Pragmatic space analysis for verifying the six laws of Principle of Things.

## Quick Start

```bash
python geometry.py --task all
python geometry.py --task law --law law1
```

See [THEORY.md](THEORY.md) for detailed verification results.

## Core Problem

Word vectors contain two types of information:

1. **Pragmatic information** — Evaluative dimensions (good/bad, right/wrong, good/evil)
2. **Syntactic information** — Formal linguistic representation (not our concern)

When mixed, opposite words (e.g., "good-bad") show **high similarity**, contradicting intuition.

## Solution: Pragmatic Space Analysis

Extract the **pragmatic space**, where opposite words show **negative similarity** (opposite directions).

## Pragmatic Axes

| Axis | Positive | Negative | Theory |
|------|----------|----------|--------|
| Value | good | bad | good = efficiency |
| Truth | right | wrong | right = complete |
| Moral | kind | evil | kind = cooperation |
| Aesthetic | beautiful | ugly | beautiful = efficiency |

## Config Files

Each law config (`laws/law*.yaml`) contains:

```yaml
name: Complete is Correct
theory: No correctness allows any omission
positive_pairs: [[complete, correct]]
opposite_pairs: [[complete, incomplete]]
pragmatic_axes:
  value:
    pos_words: [good, excellent]
    neg_words: [bad, poor]
thresholds:
  positive_similarity: 0.5
  opposite_pragmatic: -0.3
```

## Adding New Laws

Create `laws/law6.yaml` then run:

```bash
python geometry.py --task law --law law6
```

## Reference

- [THEORY.md](THEORY.md) — Detailed verification results
- [../zh/GLOSSARIES-FULL.md](../zh/GLOSSARIES-FULL.md) — Term definitions