#!/usr/bin/env python
"""
Expand Opposite Pairs Tool v1.0

Discover new opposite pairs and add them to law configs.

Strategy:
1. Run vocab_pair.py to get candidate pairs in semantic space
2. Filter by score threshold
3. Group by law themes
4. Append to law config files

Usage:
    python expand_opposites.py --min-score 0.8
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
import argparse

SCRIPT_DIR = Path(__file__).parent

# ============================================================================
# Same logic as vocab_pair.py
# ============================================================================

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
    """Get known opposite pairs."""
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

class SemanticSpace:
    """Build semantic space using contrastive learning from opposite pairs."""

    def __init__(self, vocabulary, vectors, known_opposites, n_axes=8, device="cuda"):
        self.vocabulary = vocabulary
        self.vectors = vectors
        self.known_opposites = known_opposites
        self.n_axes = n_axes
        self.device = device

        self.word_list = list(vocabulary)
        self.matrix = torch.stack([vectors[w] for w in self.word_list])
        self.mean_vec = self.matrix.mean(dim=0)
        self.centered = self.matrix - self.mean_vec

        self._build_semantic_space()

    def _build_semantic_space(self):
        axis_directions = []
        for pos, neg in self.known_opposites:
            if pos in self.vectors and neg in self.vectors:
                axis_dir = (self.vectors[pos] - self.vectors[neg]) - self.mean_vec
                if axis_dir.norm() > 0:
                    axis_dir = axis_dir / axis_dir.norm()
                    axis_directions.append(axis_dir)

        if len(axis_directions) > 0:
            axis_matrix = torch.stack(axis_directions)
            n_components = min(self.n_axes, len(axis_directions))
            pca = PCA(n_components=n_components)
            pca.fit(axis_matrix.cpu().numpy())
            self.semantic_axes = torch.from_numpy(pca.components_).float().to(self.device)
            self.axis_variance = pca.explained_variance_ratio_
        else:
            self.semantic_axes = torch.eye(len(self.mean_vec), device=self.device)[:self.n_axes]
            self.axis_variance = np.ones(self.n_axes) / self.n_axes

    def get_semantic_vector(self, word):
        if word not in self.vectors:
            return None
        vec = (self.vectors[word] - self.mean_vec).to(self.device)
        return vec @ self.semantic_axes.T

    def semantic_similarity(self, w1, w2):
        v1 = self.get_semantic_vector(w1)
        v2 = self.get_semantic_vector(w2)
        if v1 is None or v2 is None:
            return None
        return cosine_similarity(v1, v2)

    def original_similarity(self, w1, w2):
        if w1 not in self.vectors or w2 not in self.vectors:
            return None
        return cosine_similarity(self.vectors[w1], self.vectors[w2])

    def axis_projection(self, word, axis_idx=0):
        sem_vec = self.get_semantic_vector(word)
        if sem_vec is None:
            return None
        return sem_vec[axis_idx].item()

    def find_opposite_candidates(self, word, top_k=5):
        if word not in self.vectors:
            return []

        candidates = []
        for other_word in self.word_list:
            if other_word == word:
                continue

            orig_sim = self.original_similarity(word, other_word)
            if orig_sim is None or orig_sim > 0.88 or orig_sim < 0.2:
                continue

            sem_sim = self.semantic_similarity(word, other_word)
            if sem_sim is None:
                continue

            best_sep = 0
            best_axis = 0
            for axis_idx in range(len(self.semantic_axes)):
                proj1 = self.axis_projection(word, axis_idx)
                proj2 = self.axis_projection(other_word, axis_idx)
                if proj1 is not None and proj2 is not None and proj1 * proj2 < 0:
                    sep = abs(proj1 - proj2)
                    if sep > best_sep:
                        best_sep = sep
                        best_axis = axis_idx

            sem_score = (1 - sem_sim) / 2
            orig_score = 1 - abs(orig_sim - 0.5)
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

        candidates.sort(key=lambda x: -x['score'])
        return candidates[:top_k]

# ============================================================================
# Main expansion logic
# ============================================================================

def get_law_themes():
    """Define law themes for categorizing new opposite pairs."""
    return {
        'law0': ['存在', '信息', '真实', '虚假', '物质', '意识', '虚无', '实在', '符号', '编码'],
        'law1': ['完备', '正确', '确定', '客观', '真理', '边界', '有限', '不完备', '错误', '不确定'],
        'law2': ['动机', '目标', '欲望', '需求', '生存', '适应', '竞争', '进化', '消亡', '退化'],
        'law3': ['自由', '无知', '放任', '混乱', '熵', '秩序', '知识', '奴役', '约束'],
        'law4': ['正义', '效率', '公平', '投资', '收益', '成本', '低效', '不公', '消费', '浪费'],
        'law5': ['意义', '利益', '幸福', '价值', '目的', '目标', '无意义', '损失', '痛苦'],
    }

def categorize_pair(w1, w2, law_themes):
    """Categorize a pair into the most relevant law."""
    scores = {}
    for law, keywords in law_themes.items():
        score = 0
        for kw in keywords:
            if kw in w1 or kw in w2:
                score += 1
        scores[law] = score

    if max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return None

def main():
    parser = argparse.ArgumentParser(description='Expand Opposite Pairs Tool v1.0')
    parser.add_argument('--min-score', type=float, default=0.8, help='Minimum score threshold')
    parser.add_argument('--max-pairs', type=int, default=30, help='Maximum new pairs to find')
    args = parser.parse_args()

    # Load data
    vocab = load_vocabulary()
    known_opposites = get_known_opposites()
    known_set = set()
    for w1, w2 in known_opposites:
        known_set.add(tuple(sorted([w1, w2])))

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
    print("Building semantic space...")
    semantic_space = SemanticSpace(vocab, vectors, known_opposites, n_axes=8, device=device)

    # Find all candidates
    print(f"\nFinding new opposite pairs (score >= {args.min_score})...")

    all_candidates = []
    for word in vocab:
        candidates = semantic_space.find_opposite_candidates(word, top_k=3)
        for c in candidates:
            pair = tuple(sorted([word, c['word']]))
            if pair not in known_set and c['score'] >= args.min_score:
                all_candidates.append({
                    'pair': pair,
                    'score': c['score'],
                    'sem_sim': c['sem_sim'],
                    'orig_sim': c['orig_sim']
                })
                known_set.add(pair)  # Avoid duplicates

    # Remove duplicates and sort
    seen = set()
    unique = []
    for c in all_candidates:
        if c['pair'] not in seen:
            seen.add(c['pair'])
            unique.append(c)

    unique.sort(key=lambda x: -x['score'])
    top_candidates = unique[:args.max_pairs]

    # Categorize by law
    law_themes = get_law_themes()
    categorized = {law: [] for law in law_themes}
    uncategorized = []

    for c in top_candidates:
        w1, w2 = c['pair']
        law = categorize_pair(w1, w2, law_themes)
        if law:
            categorized[law].append(c)
        else:
            uncategorized.append(c)

    # Output results
    print(f"\n{'='*70}")
    print(f"New Opposite Pairs Found (score >= {args.min_score})")
    print(f"{'='*70}")

    for law in sorted(categorized.keys()):
        pairs = categorized[law]
        if pairs:
            print(f"\n{law}:")
            for c in pairs:
                w1, w2 = c['pair']
                sem_angle = np.degrees(np.arccos(max(-1, min(1, c['sem_sim']))))
                print(f"  - [{w1}, {w2}]  # sem={c['sem_sim']:.3f} ({sem_angle:.0f}°), score={c['score']:.3f}")

    if uncategorized:
        print(f"\n[Uncategorized]:")
        for c in uncategorized:
            w1, w2 = c['pair']
            sem_angle = np.degrees(np.arccos(max(-1, min(1, c['sem_sim']))))
            print(f"  - [{w1}, {w2}]  # sem={c['sem_sim']:.3f} ({sem_angle:.0f}°), score={c['score']:.3f}")

    # Summary
    print(f"\n{'='*70}")
    print(f"Summary")
    print(f"{'='*70}")
    print(f"Total new pairs: {len(top_candidates)}")
    for law, pairs in categorized.items():
        if pairs:
            print(f"  {law}: {len(pairs)} pairs")

    # Output YAML format
    print(f"\n{'='*70}")
    print("YAML Format (copy to law configs)")
    print(f"{'='*70}")

    for law in sorted(categorized.keys()):
        pairs = categorized[law]
        if pairs:
            print(f"\n# Add to {law}.yaml:")
            print("opposite_pairs:")
            for c in pairs:
                w1, w2 = c['pair']
                print(f"  - [{w1}, {w2}]")

if __name__ == "__main__":
    main()
