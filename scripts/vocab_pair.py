#!/usr/bin/env python
"""
Vocabulary Space Pairing Tool v3.0

For each word in vocabulary, find potential opposite pairs in SEMANTIC SPACE.

Key insight from geometry4.py:
- Word vectors mix semantic (evaluation) and syntactic (context) information
- Opposites share syntactic context but differ in evaluation direction
- Must separate semantic space from syntactic space first

Strategy:
1. Load all vocabulary from law configs
2. Build semantic space using contrastive learning from known opposites
3. For each word, find candidates based on:
   - Low similarity in SEMANTIC space (opposite evaluation)
   - Medium similarity in ORIGINAL space (share context)
   - Large projection separation on learned axes

Usage:
    python vocab_pair.py
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from sklearn.decomposition import PCA
from transformers import AutoTokenizer, AutoModel
import yaml

SCRIPT_DIR = Path(__file__).parent

def load_vocabulary():
    """Load all vocabulary from law configs."""
    vocab = set()
    laws_dir = SCRIPT_DIR / "configs"

    for path in sorted(laws_dir.glob("*.yaml")):
        with open(path, 'r', encoding='utf-8') as f:
            law = yaml.safe_load(f)

        for pair in law.get('positive_pairs', []):
            vocab.update(pair)
        for pair in law.get('opposite_pairs', []):
            vocab.update(pair)
        for ax_config in law.get('semantic_axes', {}).values():
            vocab.update(ax_config.get('pos_words', []))
            vocab.update(ax_config.get('neg_words', []))

        for group in law.get('quadrant_groups', {}).values():
            vocab.update(group.get('words', []))
        vocab.update(law.get('vocabulary_extension', []))

    return sorted(vocab)

def get_known_opposites():
    """Get known opposite pairs for contrastive learning."""
    pairs = []
    laws_dir = SCRIPT_DIR / "configs"

    for path in sorted(laws_dir.glob("law*.yaml")):
        with open(path, 'r', encoding='utf-8') as f:
            law = yaml.safe_load(f)
        for pair in law.get('opposite_pairs', []):
            pairs.append((pair[0], pair[1]))

    return pairs

def load_model(model_name):
    """Load model and tokenizer."""
    model_paths = {
        "qwen3.5-9b": r"C:\Users\hans\Desktop\models\qwen3.5-9b",
        "bert-base-chinese": "bert-base-chinese",
        "infoxlm-large": r"C:\Users\hans\Desktop\models\infoxlm-large",
    }
    path = model_paths.get(model_name, model_name)
    tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    model = AutoModel.from_pretrained(path, output_hidden_states=True, trust_remote_code=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    return model, tokenizer, device

def get_vector(model, tokenizer, device, text, layer=0):
    """Get vector for a word."""
    inputs = tokenizer(text, return_tensors="pt").to(device)
    with torch.no_grad():
        outputs = model(**inputs, output_hidden_states=True)

    h = outputs.hidden_states
    mask = inputs["attention_mask"].unsqueeze(-1)
    vec = (h[layer] * mask).sum(dim=1) / mask.sum(dim=1)
    return vec[0].float()

def cosine_similarity(a, b):
    return F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()

# ============================================================================
# Semantic Space Construction (from geometry4.py)
# ============================================================================

class SemanticSpace:
    """
    Build semantic space using contrastive learning from opposite pairs.

    This separates evaluation direction (semantic) from context distribution (syntactic).
    """

    def __init__(self, vocabulary, vectors, known_opposites, n_axes=8, device="cuda"):
        self.vocabulary = vocabulary
        self.vectors = vectors
        self.known_opposites = known_opposites
        self.n_axes = n_axes
        self.device = device

        # Build matrix
        self.word_list = list(vocabulary)
        self.matrix = torch.stack([vectors[w] for w in self.word_list])
        self.mean_vec = self.matrix.mean(dim=0)
        self.centered = self.matrix - self.mean_vec

        # Build semantic space
        self._build_semantic_space()

    def _build_semantic_space(self):
        """Build semantic space from known opposites using contrastive learning."""
        print(f"Building semantic space from {len(self.known_opposites)} known opposite pairs...")

        # Step 1: Collect axis directions from known opposites
        axis_directions = []
        valid_pairs = []

        for pos, neg in self.known_opposites:
            if pos in self.vectors and neg in self.vectors:
                pos_vec = self.vectors[pos]
                neg_vec = self.vectors[neg]

                # Axis direction: positive - negative (centered)
                axis_dir = (pos_vec - neg_vec) - self.mean_vec
                if axis_dir.norm() > 0:
                    axis_dir = axis_dir / axis_dir.norm()
                    axis_directions.append(axis_dir)
                    valid_pairs.append((pos, neg))

        print(f"  Collected {len(axis_directions)} axis directions")

        # Step 2: Orthogonalize using PCA
        if len(axis_directions) > 0:
            axis_matrix = torch.stack(axis_directions)
            n_components = min(self.n_axes, len(axis_directions))
            pca = PCA(n_components=n_components)
            pca.fit(axis_matrix.cpu().numpy())

            self.semantic_axes = torch.from_numpy(pca.components_).float().to(self.device)
            self.axis_variance = pca.explained_variance_ratio_
        else:
            # Fallback
            self.semantic_axes = torch.eye(len(self.mean_vec), device=self.device)[:self.n_axes]
            self.axis_variance = np.ones(self.n_axes) / self.n_axes

        print(f"  Built {len(self.semantic_axes)} semantic axes")

    def get_semantic_vector(self, word):
        """Get word representation in semantic space."""
        if word not in self.vectors:
            return None

        vec = (self.vectors[word] - self.mean_vec).to(self.device)
        # Project onto semantic axes
        semantic_vec = vec @ self.semantic_axes.T
        return semantic_vec

    def semantic_similarity(self, w1, w2):
        """Calculate similarity in semantic space."""
        v1 = self.get_semantic_vector(w1)
        v2 = self.get_semantic_vector(w2)

        if v1 is None or v2 is None:
            return None

        return cosine_similarity(v1, v2)

    def original_similarity(self, w1, w2):
        """Calculate similarity in original space."""
        if w1 not in self.vectors or w2 not in self.vectors:
            return None
        return cosine_similarity(self.vectors[w1], self.vectors[w2])

    def axis_projection(self, word, axis_idx=0):
        """Get projection of word on a specific semantic axis."""
        sem_vec = self.get_semantic_vector(word)
        if sem_vec is None:
            return None
        return sem_vec[axis_idx].item()

    def find_opposite_candidates(self, word, top_k=5):
        """
        Find potential opposites for a word.

        Criteria:
        1. Low semantic similarity (opposite evaluation)
        2. Medium original similarity (share context)
        3. Opposite projections on semantic axes
        """
        if word not in self.vectors:
            return []

        orig_sim_w = self.original_similarity(self.vectors.get(word, torch.zeros_like(self.mean_vec)),
                                              self.vectors.get(word, torch.zeros_like(self.mean_vec)))

        candidates = []

        for other_word in self.word_list:
            if other_word == word:
                continue

            # Criterion 1: Original similarity (should be medium, 0.3-0.85)
            orig_sim = self.original_similarity(word, other_word)
            if orig_sim is None or orig_sim > 0.88 or orig_sim < 0.2:
                continue

            # Criterion 2: Semantic similarity (should be LOW or NEGATIVE)
            sem_sim = self.semantic_similarity(word, other_word)
            if sem_sim is None:
                continue

            # Criterion 3: Projection separation on axes
            # Find best axis where they have opposite projections
            best_sep = 0
            best_axis = 0

            for axis_idx in range(len(self.semantic_axes)):
                proj1 = self.axis_projection(word, axis_idx)
                proj2 = self.axis_projection(other_word, axis_idx)

                if proj1 is not None and proj2 is not None:
                    # Opposite signs?
                    if proj1 * proj2 < 0:
                        sep = abs(proj1 - proj2)
                        if sep > best_sep:
                            best_sep = sep
                            best_axis = axis_idx

            # Calculate opposite score
            # Higher score = more likely opposite
            # - Low semantic similarity (negative is best)
            # - Medium original similarity
            # - High projection separation

            sem_score = (1 - sem_sim) / 2  # Normalize from [-1,1] to [0,1]
            orig_score = 1 - abs(orig_sim - 0.5)  # Best at 0.5
            sep_score = best_sep / 5.0

            combined_score = sem_score * 0.5 + orig_score * 0.2 + sep_score * 0.3

            candidates.append({
                'word': other_word,
                'orig_sim': orig_sim,
                'sem_sim': sem_sim,
                'proj_sep': best_sep,
                'best_axis': best_axis + 1,
                'score': combined_score
            })

        # Sort by score
        candidates.sort(key=lambda x: -x['score'])

        return candidates[:top_k]

def main():
    # Load vocabulary
    vocab = load_vocabulary()
    known_opposites = get_known_opposites()
    print(f"Vocabulary: {len(vocab)} words")
    print(f"Known opposite pairs: {len(known_opposites)}")

    # Load model
    print("Loading model...")
    model, tokenizer, device = load_model("infoxlm-large")

    # Extract vectors
    print("Extracting vectors...")
    vectors = {}
    for word in vocab:
        vectors[word] = get_vector(model, tokenizer, device, word)

    # Build semantic space
    print("\n" + "="*70)
    print("Building Semantic Space")
    print("="*70)
    semantic_space = SemanticSpace(vocab, vectors, known_opposites, n_axes=8, device=device)

    # Find opposite candidates for each word
    print("\n" + "="*70)
    print("Vocabulary Pairing in Semantic Space")
    print("="*70)

    results = {}

    for word in vocab:
        candidates = semantic_space.find_opposite_candidates(word, top_k=5)
        if candidates:
            results[word] = candidates

    # Output results
    for word, opposites in results.items():
        if opposites:
            print(f"\n{word}:")
            for c in opposites[:3]:
                sem_angle = np.degrees(np.arccos(max(-1, min(1, c['sem_sim']))))
                print(f"  ↔ {c['word']}: sem_sim={c['sem_sim']:.3f} ({sem_angle:.0f}°), orig_sim={c['orig_sim']:.2f}, sep={c['proj_sep']:.2f} (axis {c['best_axis']}), score={c['score']:.3f}")

    # Summary
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")
    print(f"Words with potential opposites: {len(results)}")

    # Count unique pairs
    all_pairs = set()
    for word, opposites in results.items():
        for c in opposites:
            pair = tuple(sorted([word, c['word']]))
            all_pairs.add(pair)

    print(f"Unique candidate pairs: {len(all_pairs)}")

    # Check recall on known opposites
    found_known = 0
    for pos, neg in known_opposites:
        pair = tuple(sorted([pos, neg]))
        if pair in all_pairs:
            found_known += 1

    print(f"Recall on known opposites: {found_known}/{len(known_opposites)} ({found_known/len(known_opposites)*100:.0f}%)")

    # Show best findings
    print(f"\n{'='*70}")
    print("Top Opposite Pairs (sorted by score)")
    print(f"{'='*70}")

    all_candidates = []
    for word, opposites in results.items():
        for c in opposites:
            pair = tuple(sorted([word, c['word']]))
            all_candidates.append({
                'pair': pair,
                'score': c['score'],
                'sem_sim': c['sem_sim'],
                'orig_sim': c['orig_sim']
            })

    # Remove duplicates
    seen = set()
    unique = []
    for c in all_candidates:
        if c['pair'] not in seen:
            seen.add(c['pair'])
            unique.append(c)

    unique.sort(key=lambda x: -x['score'])

    for i, c in enumerate(unique[:20]):
        w1, w2 = c['pair']
        is_known = "✓ KNOWN" if (w1, w2) in [(p, n) for p, n in known_opposites] or \
                                     (w2, w1) in [(p, n) for p, n in known_opposites] else ""
        sem_angle = np.degrees(np.arccos(max(-1, min(1, c['sem_sim']))))
        print(f"{i+1:2d}. {w1} ↔ {w2}: sem={c['sem_sim']:.3f} ({sem_angle:.0f}°), orig={c['orig_sim']:.2f}, score={c['score']:.3f} {is_known}")

if __name__ == "__main__":
    main()
