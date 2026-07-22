#!/usr/bin/env python
"""
Quadrant Opposites (QuadOppos) Discovery Tool v1.0

Discover opposite word pairs based on quadrant structure (quadoppos),
not simple binary opposition.

Key insight: Many opposites are not binary (A vs B), but quadrant-based:
- A = X + Y (both positive)
- B = -X + Y (one negative)
- C = X - Y (one negative)
- D = -X - Y (both negative)

Diagonal pairs (A-D, B-C) are true opposites.

Usage:
    python quadoppos.py --task analyze
    python quadoppos.py --task discover
    python quadoppos.py --task verify
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import os
import argparse
import torch
import torch.nn.functional as F
import numpy as np
from pathlib import Path
from sklearn.decomposition import PCA
from transformers import AutoTokenizer, AutoModel
import yaml

# ============================================================================
# Config Loading
# ============================================================================

SCRIPT_DIR = Path(__file__).parent

def load_all_laws():
    """Load all law configs including quadrant.yaml."""
    laws = {}
    laws_dir = SCRIPT_DIR / "laws"
    if not laws_dir.exists():
        return laws

    for path in sorted(laws_dir.glob("*.yaml")):
        with open(path, 'r', encoding='utf-8') as f:
            law = yaml.safe_load(f)
            laws[path.stem] = law

    return laws


def get_vocabulary(laws_config):
    """Extract all vocabulary words including quadrant groups."""
    vocab = set()

    # From law configs
    for law in laws_config.values():
        for pair in law.get('positive_pairs', []):
            vocab.update(pair)
        for pair in law.get('opposite_pairs', []):
            vocab.update(pair)
        for ax_name, ax_config in law.get('semantic_axes', {}).items():
            vocab.update(ax_config.get('pos_words', []))
            vocab.update(ax_config.get('neg_words', []))

    # From quadrant groups
    quadrant_config = laws_config.get('quadrant', {})
    for group_name, group_config in quadrant_config.get('quadrant_groups', {}).items():
        vocab.update(group_config.get('words', []))
    vocab.update(quadrant_config.get('vocabulary_extension', []))

    return list(vocab)


# ============================================================================
# Core Algorithms
# ============================================================================

class VectorExtractor:
    """Extract semantic vectors from language models."""

    def __init__(self, model, tokenizer, device="cuda"):
        self.model = model
        self.tokenizer = tokenizer
        self.device = device

    def get_vector(self, text, layer=-1):
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)

        if hasattr(outputs, 'hidden_states') and outputs.hidden_states is not None:
            h = outputs.hidden_states
        else:
            return outputs.last_hidden_state.mean(dim=1)[0]

        mask = inputs["attention_mask"].unsqueeze(-1)

        if isinstance(layer, list):
            vecs = []
            for l in layer:
                layer_idx = len(h) + l if l < 0 else l
                if 0 <= layer_idx < len(h):
                    layer_h = h[layer_idx]
                    vec = (layer_h * mask).sum(dim=1) / mask.sum(dim=1)
                    vecs.append(vec[0])
            return torch.stack(vecs).mean(dim=0)

        layer_idx = len(h) + layer if layer < 0 else layer

        if 0 <= layer_idx < len(h):
            layer_h = h[layer_idx]
            vec = (layer_h * mask).sum(dim=1) / mask.sum(dim=1)
            return vec[0]

        return h[-1].mean(dim=1)[0]


def cosine_similarity(a, b):
    return F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()


def load_model(model_name):
    """Load model and tokenizer."""
    model_paths = {
        "qwen3.5-9b": r"C:\Users\hans\Desktop\models\qwen3.5-9b",
        "bert-base-chinese": "bert-base-chinese",
        "infoxlm-large": r"C:\Users\hans\Desktop\models\infoxlm-large",
        "qwen2.5-7b-instruct": r"C:\Users\hans\Desktop\models\qwen2.5-7b-instruct",
    }
    path = model_paths.get(model_name, model_name)
    tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
    model = AutoModel.from_pretrained(path, output_hidden_states=True, trust_remote_code=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)
    model.eval()
    return model, tokenizer, device


# ============================================================================
# Quadrant Space Analysis
# ============================================================================

class QuadrantSpaceAnalyzer:
    """
    Analyze concept space as quadrant structure.

    Key idea: Concepts are defined by two independent dimensions.
    Opposites are diagonal pairs in the 2D space.
    """

    def __init__(self, vocabulary, extractor, layer=-1):
        self.vocabulary = vocabulary
        self.extractor = extractor
        self.layer = layer
        self.device = extractor.device

        # Extract vectors
        print(f"Extracting vectors for {len(vocabulary)} words...")
        self.vectors = {w: extractor.get_vector(w, layer) for w in vocabulary}
        self.word_list = list(vocabulary)
        self.matrix = torch.stack([self.vectors[w].float() for w in self.word_list])
        self.mean_vec = self.matrix.mean(dim=0)
        self.centered = self.matrix - self.mean_vec

        # Define quadrant templates
        self.quadrant_templates = self._define_templates()

    def _define_templates(self):
        """Define quadrant concept templates from BINARY-CONCEPT-SPACE.md."""
        templates = {
            'order_freedom_slavery_chaos': {
                'words': ['秩序', '自由', '奴役', '放任'],
                'dimensions': ['已知', '二阶已知'],
                'quadrants': {
                    'order': ('已知', '二阶已知'),      # ++ = 秩序
                    'freedom': ('已知', '二阶未知'),    # +- = 自由
                    'slavery': ('未知', '二阶已知'),    # -+ = 奴役
                    'chaos': ('未知', '二阶未知'),      # -- = 放任
                },
                'diagonals': [('秩序', '放任'), ('自由', '奴役')],
                'adjacents': [('秩序', '自由'), ('秩序', '奴役'), ('自由', '放任'), ('奴役', '放任')]
            },
            'science_religion_engineering_philosophy': {
                'words': ['科学', '宗教', '工程', '哲学'],
                'dimensions': ['承诺', '兑现'],
                'quadrants': {
                    'science': ('有承诺', '有兑现'),
                    'religion': ('有承诺', '无兑现'),
                    'engineering': ('无承诺', '有兑现'),
                    'philosophy': ('无承诺', '无兑现'),
                },
                'diagonals': [('科学', '哲学'), ('宗教', '工程')],
                'adjacents': [('科学', '宗教'), ('科学', '工程'), ('宗教', '哲学'), ('工程', '哲学')]
            },
            'democracy_populism_autocracy_dictatorship': {
                'words': ['民主', '民粹', '专制', '独裁'],
                'dimensions': ['主体', '决策'],
                'quadrants': {
                    'democracy': ('群体', '秩序'),
                    'populism': ('群体', '放任'),
                    'autocracy': ('个体', '秩序'),
                    'dictatorship': ('个体', '放任'),
                },
                'diagonals': [('民主', '独裁'), ('民粹', '专制')],
                'adjacents': [('民主', '民粹'), ('民主', '专制'), ('民粹', '独裁'), ('专制', '独裁')]
            }
        }
        return templates

    def analyze_template(self, template_name):
        """Analyze a specific quadrant template."""
        template = self.quadrant_templates.get(template_name)
        if not template:
            print(f"Template '{template_name}' not found")
            return None

        words = template['words']
        print(f"\n{'='*70}")
        print(f"Quadrant Analysis: {template_name}")
        print(f"{'='*70}")

        # Check which words are in vocabulary
        available_words = [w for w in words if w in self.vectors]
        missing_words = [w for w in words if w not in self.vectors]

        if missing_words:
            print(f"\nMissing words: {missing_words}")

        if len(available_words) < 2:
            print("Not enough words available for analysis")
            return None

        # Analyze diagonal pairs (true opposites)
        print(f"\n--- Diagonal Pairs (True Opposites) ---")
        for w1, w2 in template['diagonals']:
            if w1 in self.vectors and w2 in self.vectors:
                sim = cosine_similarity(self.vectors[w1], self.vectors[w2])
                angle = np.degrees(np.arccos(max(-1, min(1, sim))))
                print(f"  {w1} ↔ {w2}: sim={sim:.3f}, angle={angle:.1f}°")

        # Analyze adjacent pairs (partial opposites)
        print(f"\n--- Adjacent Pairs (Partial Opposites) ---")
        for w1, w2 in template['adjacents']:
            if w1 in self.vectors and w2 in self.vectors:
                sim = cosine_similarity(self.vectors[w1], self.vectors[w2])
                angle = np.degrees(np.arccos(max(-1, min(1, sim))))
                print(f"  {w1} ↔ {w2}: sim={sim:.3f}, angle={angle:.1f}°")

        # Visualize quadrant positions
        self._visualize_quadrant(available_words, template)

        return template

    def _visualize_quadrant(self, words, template):
        """Visualize words in quadrant space using PCA."""
        if len(words) < 3:
            return

        # Get vectors for available words
        word_vectors = torch.stack([self.vectors[w].float() for w in words])
        word_vectors_centered = word_vectors - self.mean_vec

        # PCA to 2D
        pca = PCA(n_components=2)
        coords_2d = pca.fit_transform(word_vectors_centered.cpu().numpy())

        print(f"\n--- Quadrant Visualization (PCA 2D) ---")
        print(f"  Explained variance: PC1={pca.explained_variance_ratio_[0]*100:.1f}%, PC2={pca.explained_variance_ratio_[1]*100:.1f}%")
        print()

        for i, word in enumerate(words):
            x, y = coords_2d[i]
            quadrant = self._get_quadrant_name(word, template)
            print(f"  {word:8s}: ({x:+.2f}, {y:+.2f}) [{quadrant}]")

    def _get_quadrant_name(self, word, template):
        """Get quadrant name for a word."""
        for q_name, q_dims in template['quadrants'].items():
            if q_name.lower() in word.lower() or word.lower() in q_name.lower():
                return f"{q_name}: {q_dims[0]}/{q_dims[1]}"
        return "unknown"

    def discover_quadrant_opposites(self, top_k=20):
        """
        Discover potential quadrant-based opposite pairs.

        Strategy:
        1. Find two orthogonal semantic axes (dimensions)
        2. Project words onto both axes
        3. Find diagonal pairs (opposite signs on both axes)
        """
        print(f"\n{'='*70}")
        print("Discovering Quadrant-based Opposites")
        print(f"{'='*70}")

        # Use PCA to find first two components (independent dimensions)
        pca = PCA(n_components=2)
        pca.fit(self.centered.cpu().numpy())

        axis1 = torch.from_numpy(pca.components_[0]).float().to(self.device)
        axis2 = torch.from_numpy(pca.components_[1]).float().to(self.device)

        print(f"\nFound two semantic dimensions:")
        print(f"  PC1 explains {pca.explained_variance_ratio_[0]*100:.1f}% variance")
        print(f"  PC2 explains {pca.explained_variance_ratio_[1]*100:.1f}% variance")

        # Project all words onto both axes
        proj1 = (self.centered @ axis1).cpu().numpy()
        proj2 = (self.centered @ axis2).cpu().numpy()

        # Find diagonal pairs
        discovered = []

        for i, w1 in enumerate(self.word_list):
            for j, w2 in enumerate(self.word_list):
                if i >= j:
                    continue

                p1_1, p1_2 = proj1[i], proj2[i]
                p2_1, p2_2 = proj1[j], proj2[j]

                # Check if diagonal (opposite on both axes)
                diag1 = (p1_1 * p2_1 < 0) and (p1_2 * p2_2 < 0)  # ++ vs --
                diag2 = (p1_1 * p2_1 < 0) and (p1_2 * p2_2 > 0)  # +- vs -+

                if diag1 or diag2:
                    # Calculate opposite score
                    sep1 = abs(p1_1 - p2_1)
                    sep2 = abs(p1_2 - p2_2)
                    score = sep1 * sep2

                    discovered.append({
                        'pair': (w1, w2),
                        'proj1_sep': sep1,
                        'proj2_sep': sep2,
                        'score': score,
                        'type': 'diagonal_++--' if diag1 else 'diagonal_+--+'
                    })

        # Sort by score
        discovered.sort(key=lambda x: x['score'], reverse=True)

        print(f"\n--- Top Diagonal Pairs (Quadrant Opposites) ---")
        for i, item in enumerate(discovered[:top_k]):
            w1, w2 = item['pair']
            print(f"{i+1:2d}. {w1} ↔ {w2}: score={item['score']:.3f} [{item['type']}]")

        return discovered[:top_k]

    def compare_quadrant_vs_binary(self):
        """
        Compare quadrant-based opposites with binary opposites.

        Show that diagonal pairs have larger separation than adjacent pairs.
        """
        print(f"\n{'='*70}")
        print("Quadrant vs Binary Opposition Comparison")
        print(f"{'='*70}")

        for template_name, template in self.quadrant_templates.items():
            print(f"\n{template_name}:")
            print("-" * 50)

            # Diagonal pairs
            diag_sims = []
            for w1, w2 in template['diagonals']:
                if w1 in self.vectors and w2 in self.vectors:
                    sim = cosine_similarity(self.vectors[w1], self.vectors[w2])
                    diag_sims.append(sim)
                    print(f"  Diagonal: {w1} ↔ {w2}: sim={sim:.3f}")

            # Adjacent pairs
            adj_sims = []
            for w1, w2 in template['adjacents']:
                if w1 in self.vectors and w2 in self.vectors:
                    sim = cosine_similarity(self.vectors[w1], self.vectors[w2])
                    adj_sims.append(sim)
                    print(f"  Adjacent: {w1} ↔ {w2}: sim={sim:.3f}")

            # Compare
            if diag_sims and adj_sims:
                diag_avg = np.mean(diag_sims)
                adj_avg = np.mean(adj_sims)
                print(f"\n  Average similarity:")
                print(f"    Diagonal pairs: {diag_avg:.3f}")
                print(f"    Adjacent pairs: {adj_avg:.3f}")
                print(f"    Difference: {adj_avg - diag_avg:.3f}")

                if adj_avg > diag_avg:
                    print(f"  ✓ Diagonal pairs are MORE different (confirm quadrant structure)")
                else:
                    print(f"  ✗ Diagonal pairs are NOT more different")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Quadrant Concept Space Analysis Tool v1.0')
    parser.add_argument('--model', type=str, default='infoxlm-large', help='Model to use')
    parser.add_argument('--layer', type=str, default='0', help='Layer to use')
    parser.add_argument('--task', type=str, default='analyze',
                        choices=['analyze', 'discover', 'compare', 'all'],
                        help='Analysis task')

    args = parser.parse_args()

    if ',' in args.layer:
        layer = [int(l.strip()) for l in args.layer.split(',')]
    else:
        layer = int(args.layer)

    # Load data
    laws_config = load_all_laws()
    vocab = get_vocabulary(laws_config)

    # Load model
    print(f"Loading model: {args.model}...")
    model, tokenizer, device = load_model(args.model)
    extractor = VectorExtractor(model, tokenizer, device)

    # Create analyzer
    analyzer = QuadrantSpaceAnalyzer(vocab, extractor, layer)

    if args.task == 'analyze':
        # Analyze predefined templates
        for template_name in analyzer.quadrant_templates.keys():
            analyzer.analyze_template(template_name)

    elif args.task == 'discover':
        analyzer.discover_quadrant_opposites()

    elif args.task == 'compare':
        analyzer.compare_quadrant_vs_binary()

    else:  # all
        for template_name in analyzer.quadrant_templates.keys():
            analyzer.analyze_template(template_name)
        analyzer.discover_quadrant_opposites()
        analyzer.compare_quadrant_vs_binary()


if __name__ == '__main__':
    main()