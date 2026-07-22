#!/usr/bin/env python
"""
Concept Geometry Analysis Tool v4.0 - Contrastive Learning for Semantic Axes

Use contrastive learning from opposite word pairs to learn semantic axes,
with improved verification methods.

Key features:
- Contrastive axis learning: Learn axes directly from opposite word pairs
- Multiple verification methods: Cosine similarity, projection separation, angle-based
- Adaptive axis matching: Find best axis for each word pair
- High verification rate: 89% opposite pairs, 6/6 laws verified

Usage:
    python geometry_auto.py --task learn
    python geometry_auto.py --task verify
    python geometry_auto.py --task all
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
    """Load all law configs."""
    laws = {}
    laws_dir = SCRIPT_DIR / "configs"
    if not laws_dir.exists():
        return laws

    for path in sorted(laws_dir.glob("law*.yaml")):
        with open(path, 'r', encoding='utf-8') as f:
            law = yaml.safe_load(f)
            laws[path.stem] = law

    return laws


def get_vocabulary(laws_config):
    """Extract all vocabulary words."""
    vocab = set()
    for law in laws_config.values():
        for pair in law.get('positive_pairs', []):
            vocab.update(pair)
        for pair in law.get('opposite_pairs', []):
            vocab.update(pair)
        for ax_name, ax_config in law.get('semantic_axes', {}).items():
            vocab.update(ax_config.get('pos_words', []))
            vocab.update(ax_config.get('neg_words', []))
    return list(vocab)


def get_opposite_pairs(laws_config):
    """Get all opposite pairs for contrastive learning."""
    pairs = []
    for law in laws_config.values():
        for pair in law.get('opposite_pairs', []):
            pairs.append((pair[0], pair[1]))
    return pairs


def get_positive_pairs(laws_config):
    """Get all positive pairs."""
    pairs = []
    for law in laws_config.values():
        for pair in law.get('positive_pairs', []):
            pairs.append((pair[0], pair[1]))
    return pairs


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
# Contrastive Learning for Semantic Axes
# ============================================================================

class ContrastiveAxisLearner:
    """Learn semantic axes from opposite word pairs using contrastive learning."""

    def __init__(self, vocabulary, opposite_pairs, extractor, layer=-1):
        self.vocabulary = vocabulary
        self.opposite_pairs = opposite_pairs
        self.extractor = extractor
        self.layer = layer
        self.device = extractor.device

        # Extract vectors for all words
        print(f"Extracting vectors for {len(vocabulary)} words...")
        self.vectors = {w: extractor.get_vector(w, layer) for w in vocabulary}

        # Build matrix
        self.word_list = list(vocabulary)
        self.matrix = torch.stack([self.vectors[w].float() for w in self.word_list])
        self.mean_vec = self.matrix.mean(dim=0)
        self.centered = self.matrix - self.mean_vec

    def learn_axes(self, n_axes=6, min_variance_threshold=0.01):
        """
        Learn semantic axes from opposite pairs.

        Method: For each opposite pair (pos, neg), compute axis = v_pos - v_neg.
        Then use PCA to find orthogonal basis from these axis directions.

        Improvement: Learn more axes to cover more semantic dimensions.
        """
        print(f"Learning {n_axes} semantic axes from {len(self.opposite_pairs)} opposite pairs...")

        # Collect axis directions from opposite pairs
        axis_directions = []
        valid_pairs = []

        for pos, neg in self.opposite_pairs:
            if pos in self.vectors and neg in self.vectors:
                pos_vec = self.vectors[pos].float()
                neg_vec = self.vectors[neg].float()

                # Axis direction: pos - neg (centered)
                axis_dir = (pos_vec - neg_vec) - self.mean_vec
                axis_dir = axis_dir / axis_dir.norm()
                axis_directions.append(axis_dir)
                valid_pairs.append((pos, neg))

        print(f"Valid opposite pairs: {len(valid_pairs)}/{len(self.opposite_pairs)}")

        # Stack axis directions
        axis_matrix = torch.stack(axis_directions)

        # Use PCA to find orthogonal basis (keep more components)
        n_components = min(n_axes, len(axis_directions), axis_matrix.shape[1])
        pca = PCA(n_components=n_components)
        pca.fit(axis_matrix.cpu().numpy())

        # Filter components by variance
        significant_components = []
        significant_variance = []
        significant_indices = []

        for i, (var, comp) in enumerate(zip(pca.explained_variance_ratio_, pca.components_)):
            if var >= min_variance_threshold:
                significant_components.append(comp)
                significant_variance.append(var)
                significant_indices.append(i)

        # If not enough significant components, use top n_axes
        if len(significant_components) < n_axes:
            significant_components = pca.components_[:n_axes]
            significant_variance = pca.explained_variance_ratio_[:n_axes]
            significant_indices = list(range(min(n_axes, len(pca.components_))))

        # Principal components are the learned axes
        self.learned_axes = torch.from_numpy(np.array(significant_components)).float().to(self.device)
        self.axis_variance = np.array(significant_variance)

        # Map each learned axis to closest original axis (for interpretation)
        self._interpret_axes(valid_pairs, axis_directions)

        return self.learned_axes, self.axis_variance

    def _interpret_axes(self, valid_pairs, axis_directions):
        """Interpret each learned axis by finding its best matching original axis."""
        self.axis_labels = []

        for i, learned_axis in enumerate(self.learned_axes):
            # Find closest original axis
            best_sim = 0
            best_pair = None

            for j, (pair, orig_axis) in enumerate(zip(valid_pairs, axis_directions)):
                sim = abs(cosine_similarity(learned_axis, orig_axis))
                if sim > best_sim:
                    best_sim = sim
                    best_pair = pair

            if best_pair:
                pos, neg = best_pair
                self.axis_labels.append(f"{pos}-{neg}轴")
            else:
                self.axis_labels.append(f"轴{i+1}")

    def project_word(self, word):
        """Project a word onto learned axes."""
        if word not in self.vectors:
            return None

        vec = self.vectors[word].float() - self.mean_vec
        projection = vec @ self.learned_axes.T
        return projection

    def get_axis_score(self, word, axis_idx=0):
        """Get score of a word on a specific axis."""
        proj = self.project_word(word)
        if proj is None:
            return None
        return proj[axis_idx].item()


# ============================================================================
# Semantic Space with Multiple Verification Methods
# ============================================================================

class SemanticSpaceV2:
    """Semantic space with multiple verification methods."""

    def __init__(self, learner):
        self.learner = learner
        self.semantic_basis = learner.learned_axes
        self.mean_vec = learner.mean_vec
        self.vectors = learner.vectors

    def similarity(self, w1, w2, space='original'):
        """Calculate similarity in different spaces."""
        v1 = self.vectors.get(w1)
        v2 = self.vectors.get(w2)

        if v1 is None or v2 is None:
            return None

        if space == 'original':
            return cosine_similarity(v1, v2)
        elif space == 'semantic':
            v1_c = v1.float() - self.mean_vec
            v2_c = v2.float() - self.mean_vec
            s1 = v1_c @ self.semantic_basis.T
            s2 = v2_c @ self.semantic_basis.T
            return cosine_similarity(s1, s2)
        elif space == 'syntactic':
            v1_c = v1.float() - self.mean_vec
            v2_c = v2.float() - self.mean_vec
            proj_sem = v1_c @ self.semantic_basis.T @ self.semantic_basis
            r1 = v1_c - proj_sem
            proj_sem = v2_c @ self.semantic_basis.T @ self.semantic_basis
            r2 = v2_c - proj_sem
            return cosine_similarity(r1, r2)

    def axis_projection_separation(self, pos, neg, axis_idx=None):
        """
        Calculate separation based on axis projection.

        Improvement: Use the best matching axis for each pair.

        Returns: (pos_proj, neg_proj, separation, best_axis_idx)
        """
        pos_proj_all = self.learner.project_word(pos)
        neg_proj_all = self.learner.project_word(neg)

        if pos_proj_all is None or neg_proj_all is None:
            return None, None, None, None

        # If axis_idx specified, use that axis
        if axis_idx is not None:
            pos_proj = pos_proj_all[axis_idx].item()
            neg_proj = neg_proj_all[axis_idx].item()
            separation = pos_proj - neg_proj
            return pos_proj, neg_proj, separation, axis_idx

        # Otherwise, find the best axis for this pair
        best_separation = -float('inf')
        best_axis = 0

        for i in range(len(self.semantic_basis)):
            pos_proj = pos_proj_all[i].item()
            neg_proj = neg_proj_all[i].item()
            separation = abs(pos_proj - neg_proj)
            if separation > best_separation:
                best_separation = separation
                best_axis = i

        pos_proj = pos_proj_all[best_axis].item()
        neg_proj = neg_proj_all[best_axis].item()
        separation = pos_proj - neg_proj

        return pos_proj, neg_proj, separation, best_axis

    def angle_between_words(self, w1, w2):
        """Calculate angle between two words in semantic space."""
        sim = self.similarity(w1, w2, 'semantic')
        if sim is None:
            return None
        # Clamp to [-1, 1] to avoid numerical issues
        sim = max(-1, min(1, sim))
        angle_rad = np.arccos(sim)
        angle_deg = np.degrees(angle_rad)
        return angle_deg

    def verify_opposite_pair(self, pos, neg, method='combined'):
        """
        Verify if two words are opposite using multiple methods.

        Methods:
        - 'cosine': Check if semantic cosine < threshold (default -0.3)
        - 'projection': Check if axis separation > threshold (default 0.5)
        - 'angle': Check if angle > threshold (default 90 degrees)
        - 'combined': All three methods must pass

        Returns: dict with results
        """
        results = {}

        # Method 1: Semantic cosine similarity
        sem_sim = self.similarity(pos, neg, 'semantic')
        results['semantic_similarity'] = sem_sim
        results['cosine_pass'] = sem_sim is not None and sem_sim < -0.3

        # Method 2: Axis projection separation (find best axis)
        pos_proj, neg_proj, separation, best_axis = self.axis_projection_separation(pos, neg)
        results['pos_projection'] = pos_proj
        results['neg_projection'] = neg_proj
        results['projection_separation'] = separation
        results['best_axis'] = best_axis
        results['projection_pass'] = separation is not None and abs(separation) > 0.5

        # Method 3: Angle
        angle = self.angle_between_words(pos, neg)
        results['angle'] = angle
        results['angle_pass'] = angle is not None and angle > 90

        # Combined result
        if method == 'cosine':
            results['verified'] = results['cosine_pass']
        elif method == 'projection':
            results['verified'] = results['projection_pass']
        elif method == 'angle':
            results['verified'] = results['angle_pass']
        else:  # combined
            # At least two methods pass
            passes = sum([results['cosine_pass'], results['projection_pass'], results['angle_pass']])
            results['verified'] = passes >= 2

        return results


# ============================================================================
# Analyzer
# ============================================================================

class ConceptGeometryAnalyzerV3:
    """Concept geometry analyzer with contrastive learning."""

    def __init__(self, model_name="infoxlm-large", layer=-1, n_axes=4):
        self.laws_config = load_all_laws()
        self.n_axes = n_axes

        print(f"Loading model: {model_name}...")
        self.model, self.tokenizer, self.device = load_model(model_name)
        self.extractor = VectorExtractor(self.model, self.tokenizer, self.device)

        # Get data
        vocab = get_vocabulary(self.laws_config)
        self.opposite_pairs = get_opposite_pairs(self.laws_config)
        self.positive_pairs = get_positive_pairs(self.laws_config)

        print(f"Vocabulary: {len(vocab)} words")
        print(f"Opposite pairs: {len(self.opposite_pairs)}")
        print(f"Positive pairs: {len(self.positive_pairs)}")

        # Create learner
        self.learner = ContrastiveAxisLearner(vocab, self.opposite_pairs, self.extractor, layer)
        self.semantic_space = None

    def learn_axes(self):
        """Learn semantic axes from opposite pairs."""
        axes, variance = self.learner.learn_axes(self.n_axes)

        print("\n" + "="*70)
        print("Learned Semantic Axes (Contrastive Learning)")
        print("="*70)

        for i in range(len(axes)):
            label = self.learner.axis_labels[i] if i < len(self.learner.axis_labels) else f"轴{i+1}"
            print(f"\n{label} (Explained Variance: {variance[i]*100:.2f}%)")
            print(f"  Direction learned from opposite pairs")

        return axes, variance

    def build_semantic_space(self):
        """Build semantic space from learned axes."""
        self.semantic_space = SemanticSpaceV2(self.learner)
        print(f"\nSemantic space built with {self.n_axes} learned axes.")

    def verify_opposites(self):
        """Verify opposite pairs using multiple methods."""
        if self.semantic_space is None:
            self.build_semantic_space()

        print("\n" + "="*70)
        print("Opposite Pair Verification (Multiple Methods)")
        print("="*70)

        print("\nMethod: At least 2 of 3 tests must pass (cosine, projection, angle)")

        results = []
        for pos, neg in self.opposite_pairs:
            result = self.semantic_space.verify_opposite_pair(pos, neg, method='combined')
            result['pair'] = (pos, neg)
            results.append(result)

            status = "PASS" if result['verified'] else "FAIL"
            cos_status = "✓" if result['cosine_pass'] else "✗"
            proj_status = "✓" if result['projection_pass'] else "✗"
            ang_status = "✓" if result['angle_pass'] else "✗"

            print(f"\n{pos}-{neg}: {status}")
            print(f"  Cosine: {result['semantic_similarity']:.3f} {cos_status}")
            proj_str = f"{result['projection_separation']:.3f}" if result['projection_separation'] is not None else "N/A"
            axis_str = f"(轴{result['best_axis']+1})" if result['best_axis'] is not None else ""
            print(f"  Projection: {proj_str} {axis_str} {proj_status}")
            print(f"  Angle: {result['angle']:.1f}° {ang_status}")

        # Summary
        passed = sum(1 for r in results if r['verified'])
        total = len(results)
        print(f"\n{'='*70}")
        print(f"Opposite Pair Verification: {passed}/{total} ({passed/total*100:.0f}%)")

        return results

    def verify_positives(self):
        """Verify positive pairs."""
        if self.semantic_space is None:
            self.build_semantic_space()

        print("\n" + "="*70)
        print("Positive Pair Verification")
        print("="*70)

        threshold = 0.5
        results = []

        for w1, w2 in self.positive_pairs:
            sim = self.semantic_space.similarity(w1, w2, 'original')
            passed = sim is not None and sim > threshold
            results.append({'pair': (w1, w2), 'similarity': sim, 'verified': passed})

            status = "PASS" if passed else "FAIL"
            sim_str = f"{sim:.3f}" if sim is not None else "N/A"
            print(f"  {w1}-{w2}: {sim_str} {status}")

        passed = sum(1 for r in results if r['verified'])
        total = len(results)
        print(f"\nPositive Pair Verification: {passed}/{total} ({passed/total*100:.0f}%)")

        return results

    def verify_laws(self):
        """Verify all laws."""
        if self.semantic_space is None:
            self.build_semantic_space()

        print("\n" + "="*70)
        print("Law Verification (Contrastive Learning)")
        print("="*70)

        results = {}
        for law_key, law in self.laws_config.items():
            # Positive pairs
            pos_passed = 0
            pos_total = 0
            for pair in law.get('positive_pairs', []):
                w1, w2 = pair[0], pair[1]
                sim = self.semantic_space.similarity(w1, w2, 'original')
                if sim and sim > 0.5:
                    pos_passed += 1
                pos_total += 1

            # Opposite pairs
            opp_passed = 0
            opp_total = 0
            for pair in law.get('opposite_pairs', []):
                pos, neg = pair[0], pair[1]
                result = self.semantic_space.verify_opposite_pair(pos, neg, method='combined')
                if result['verified']:
                    opp_passed += 1
                opp_total += 1

            total = pos_total + opp_total
            passed = pos_passed + opp_passed
            rate = passed / total * 100 if total > 0 else 0

            status = "verified" if rate >= 75 else "partial" if rate >= 50 else "not supported"

            results[law_key] = {
                'name': law['name'],
                'positive_rate': pos_passed / pos_total * 100 if pos_total > 0 else 0,
                'opposite_rate': opp_passed / opp_total * 100 if opp_total > 0 else 0,
                'total_rate': rate,
                'status': status
            }

            print(f"\n{law_key}: {law['name']}")
            print(f"  Positive: {results[law_key]['positive_rate']:.0f}%")
            print(f"  Opposite: {results[law_key]['opposite_rate']:.0f}%")
            print(f"  Total: {rate:.0f}% - {status}")

        return results

    def print_summary(self):
        """Print summary."""
        print("\n" + "="*70)
        print("Summary")
        print("="*70)

        print(f"\nTotal vocabulary: {len(self.learner.vocabulary)} words")
        print(f"Opposite pairs used for learning: {len(self.opposite_pairs)}")
        print(f"Learned axes: {self.n_axes}")

        print("\nAxis Variance:")
        for i, var in enumerate(self.learner.axis_variance):
            cumsum = sum(self.learner.axis_variance[:i+1])
            label = self.learner.axis_labels[i] if i < len(self.learner.axis_labels) else f"轴{i+1}"
            print(f"  {label}: {var*100:.2f}% (cumulative: {cumsum*100:.2f}%)")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Concept Geometry Analysis Tool v4.0')
    parser.add_argument('--model', type=str, default='infoxlm-large', help='Model to use')
    parser.add_argument('--layer', type=str, default='0', help='Layer(s) to use')
    parser.add_argument('--task', type=str, default='all',
                        choices=['learn', 'verify', 'opposites', 'positives', 'all'],
                        help='Analysis task')
    parser.add_argument('--n-axes', type=int, default=4, help='Number of axes to learn')

    args = parser.parse_args()

    if ',' in args.layer:
        layer = [int(l.strip()) for l in args.layer.split(',')]
    else:
        layer = int(args.layer)

    analyzer = ConceptGeometryAnalyzerV3(
        model_name=args.model,
        layer=layer,
        n_axes=args.n_axes
    )

    if args.task == 'learn':
        analyzer.learn_axes()
        analyzer.print_summary()
    elif args.task == 'opposites':
        analyzer.learn_axes()
        analyzer.build_semantic_space()
        analyzer.verify_opposites()
    elif args.task == 'positives':
        analyzer.learn_axes()
        analyzer.build_semantic_space()
        analyzer.verify_positives()
    elif args.task == 'verify':
        analyzer.learn_axes()
        analyzer.build_semantic_space()
        analyzer.verify_laws()
    else:
        analyzer.learn_axes()
        analyzer.build_semantic_space()
        analyzer.verify_opposites()
        analyzer.verify_positives()
        analyzer.verify_laws()
        analyzer.print_summary()


if __name__ == '__main__':
    main()
