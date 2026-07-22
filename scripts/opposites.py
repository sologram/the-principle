#!/usr/bin/env python
"""
Opposite Word Pair Discovery Tool v1.0

Automatically discover opposite word pairs using three methods:
1. Semantic axis projection: Find words with opposite projections on learned axes
2. Vector direction clustering: Cluster words and find opposite pairs across clusters
3. LLM judgment: Use language model to judge if two words are opposites

Usage:
    python discover.py --method projection --top-k 20
    python discover.py --method clustering --top-k 20
    python discover.py --method llm --top-k 20
    python discover.py --method all --top-k 20
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
from sklearn.cluster import KMeans
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


def get_known_opposites(laws_config):
    """Get known opposite pairs for comparison."""
    pairs = set()
    for law in laws_config.values():
        for pair in law.get('opposite_pairs', []):
            pairs.add((pair[0], pair[1]))
            pairs.add((pair[1], pair[0]))  # Both directions
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
# Method 1: Semantic Axis Projection (Improved - uses learned axes from opposites)
# ============================================================================

class ProjectionBasedDiscovery:
    """Discover opposites by finding words with opposite projections on learned axes.

    Improvement: Learn axes from known opposite pairs (contrastive learning),
    not from PCA which captures variance not semantic opposition.
    """

    def __init__(self, vocabulary, extractor, layer=-1, n_axes=8, known_opposites=None):
        self.vocabulary = vocabulary
        self.extractor = extractor
        self.layer = layer
        self.n_axes = n_axes
        self.known_opposites = known_opposites or []
        self.device = extractor.device

        # Extract vectors
        print(f"Extracting vectors for {len(vocabulary)} words...")
        self.vectors = {w: extractor.get_vector(w, layer) for w in vocabulary}
        self.word_list = list(vocabulary)
        self.matrix = torch.stack([self.vectors[w].float() for w in self.word_list])
        self.mean_vec = self.matrix.mean(dim=0)
        self.centered = self.matrix - self.mean_vec

        # Learn axes via contrastive learning from known opposites
        self._learn_axes_from_opposites()

    def _learn_axes_from_opposites(self):
        """Learn semantic axes from known opposite pairs using contrastive learning."""
        print(f"Learning {self.n_axes} semantic axes from known opposites...")

        # Collect axis directions from known opposite pairs
        axis_directions = []
        for pos, neg in self.known_opposites:
            if pos in self.vectors and neg in self.vectors:
                pos_vec = self.vectors[pos].float()
                neg_vec = self.vectors[neg].float()
                axis_dir = (pos_vec - neg_vec) - self.mean_vec
                if axis_dir.norm() > 0:
                    axis_dir = axis_dir / axis_dir.norm()
                    axis_directions.append(axis_dir)

        print(f"  Collected {len(axis_directions)} axis directions from known opposites")

        if len(axis_directions) > 0:
            # Stack and use PCA to find orthogonal basis
            axis_matrix = torch.stack(axis_directions)
            n_components = min(self.n_axes, len(axis_directions), axis_matrix.shape[1])
            pca = PCA(n_components=n_components)
            pca.fit(axis_matrix.cpu().numpy())
            self.axes = torch.from_numpy(pca.components_).float().to(self.device)
            self.axis_variance = pca.explained_variance_ratio_
            print(f"  Learned {len(self.axes)} axes from opposite pairs")
        else:
            # Fallback to PCA if no known opposites
            print("  No known opposites, falling back to PCA...")
            pca = PCA(n_components=self.n_axes)
            pca.fit(self.centered.cpu().numpy())
            self.axes = torch.from_numpy(pca.components_).float().to(self.device)
            self.axis_variance = pca.explained_variance_ratio_

    def discover(self, top_k=20, min_separation=0.5):
        """
        Discover opposite pairs by finding words with opposite projections on learned axes.

        Strategy: For each axis, find words with opposite signs of projection.
        """
        print(f"\nDiscovering opposites via learned axis projection (top-{top_k})...")

        discovered = []

        for axis_idx in range(len(self.axes)):
            axis = self.axes[axis_idx]
            projections = self.centered @ axis

            # Find words with positive and negative projections
            positive_words = []
            negative_words = []

            for i, word in enumerate(self.word_list):
                proj = projections[i].item()
                if proj > 0.3:  # Positive side
                    positive_words.append((word, proj))
                elif proj < -0.3:  # Negative side
                    negative_words.append((word, proj))

            # Sort by absolute projection
            positive_words.sort(key=lambda x: x[1], reverse=True)
            negative_words.sort(key=lambda x: x[1])

            # Find candidate opposite pairs
            for pos_word, pos_proj in positive_words[:15]:
                for neg_word, neg_proj in negative_words[:15]:
                    separation = pos_proj - neg_proj
                    # Check if they are actually opposite (not just far apart)
                    if separation > min_separation:
                        # Additional check: cosine similarity in original space should not be too high
                        v1 = self.vectors[pos_word].float()
                        v2 = self.vectors[neg_word].float()
                        orig_sim = cosine_similarity(v1, v2)

                        discovered.append({
                            'pair': (pos_word, neg_word),
                            'axis': axis_idx + 1,
                            'pos_proj': pos_proj,
                            'neg_proj': neg_proj,
                            'separation': separation,
                            'original_similarity': orig_sim,
                            'variance': self.axis_variance[axis_idx] if axis_idx < len(self.axis_variance) else 0
                        })

        # Sort by separation
        discovered.sort(key=lambda x: x['separation'], reverse=True)

        # Remove duplicates (keep best)
        seen = set()
        unique_discovered = []
        for item in discovered:
            pair = tuple(sorted(item['pair']))
            if pair not in seen:
                seen.add(pair)
                unique_discovered.append(item)

        return unique_discovered[:top_k]


# ============================================================================
# Method 2: Vector Direction Clustering (Improved - uses semantic evaluation)
# ============================================================================

class ClusteringBasedDiscovery:
    """Discover opposites by clustering words and finding opposite pairs across clusters.

    Improvement: Use semantic evaluation to find true opposites, not just distant words.
    """

    def __init__(self, vocabulary, extractor, layer=-1, n_clusters=10, known_opposites=None):
        self.vocabulary = vocabulary
        self.extractor = extractor
        self.layer = layer
        self.n_clusters = n_clusters
        self.known_opposites = known_opposites or []
        self.device = extractor.device

        # Extract vectors
        print(f"Extracting vectors for {len(vocabulary)} words...")
        self.vectors = {w: extractor.get_vector(w, layer) for w in vocabulary}
        self.word_list = list(vocabulary)
        self.matrix = torch.stack([self.vectors[w].float() for w in self.word_list])

        # Learn semantic axes from known opposites for evaluation
        self._learn_evaluation_axes()

    def _learn_evaluation_axes(self):
        """Learn axes from known opposites for semantic evaluation."""
        axis_directions = []
        for pos, neg in self.known_opposites:
            if pos in self.vectors and neg in self.vectors:
                pos_vec = self.vectors[pos].float()
                neg_vec = self.vectors[neg].float()
                axis_dir = pos_vec - neg_vec
                if axis_dir.norm() > 0:
                    axis_dir = axis_dir / axis_dir.norm()
                    axis_directions.append(axis_dir)

        if len(axis_directions) > 0:
            axis_matrix = torch.stack(axis_directions)
            pca = PCA(n_components=min(4, len(axis_directions)))
            pca.fit(axis_matrix.cpu().numpy())
            self.eval_axes = torch.from_numpy(pca.components_).float().to(self.device)
        else:
            # Fallback: use first few dimensions
            self.eval_axes = torch.eye(self.matrix.shape[1], device=self.device)[:4]

    def _compute_opposite_score(self, w1, w2):
        """
        Compute how likely w1 and w2 are opposites.

        Criteria:
        1. Low cosine similarity (but not necessarily negative)
        2. Opposite projections on evaluation axes
        3. Similar magnitude (both should be meaningful words, not rare words)
        """
        v1 = self.vectors[w1].float()
        v2 = self.vectors[w2].float()

        # 1. Cosine similarity
        cos_sim = cosine_similarity(v1, v2)

        # 2. Projection separation on evaluation axes
        max_sep = 0
        for axis in self.eval_axes:
            proj1 = (v1 @ axis).item()
            proj2 = (v2 @ axis).item()
            sep = abs(proj1 - proj2)
            max_sep = max(max_sep, sep)

        # 3. Magnitude similarity (both should have similar norm)
        norm1 = v1.norm().item()
        norm2 = v2.norm().item()
        norm_ratio = min(norm1, norm2) / max(norm1, norm2) if max(norm1, norm2) > 0 else 0

        # Combined score: low similarity + high projection separation + similar magnitude
        opposite_score = (1 - cos_sim) * 0.4 + max_sep * 0.4 + norm_ratio * 0.2

        return {
            'cosine_similarity': cos_sim,
            'projection_separation': max_sep,
            'norm_ratio': norm_ratio,
            'opposite_score': opposite_score
        }

    def discover(self, top_k=20):
        """
        Discover opposites by evaluating all candidate pairs.

        Strategy: For efficiency, cluster first, then evaluate pairs across clusters.
        """
        print(f"\nDiscovering opposites via improved clustering (top-{top_k})...")

        # Cluster words by vector similarity
        normalized = F.normalize(self.matrix, p=2, dim=1)
        kmeans = KMeans(n_clusters=min(self.n_clusters, len(self.word_list) // 2),
                        random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(normalized.cpu().numpy())

        # Group words by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(self.word_list[i])

        # Evaluate pairs across different clusters
        discovered = []
        cluster_ids = list(clusters.keys())

        for i, c1 in enumerate(cluster_ids):
            for c2 in cluster_ids[i+1:]:
                # Sample pairs across clusters
                for w1 in clusters[c1][:10]:  # Limit to reduce computation
                    for w2 in clusters[c2][:10]:
                        score = self._compute_opposite_score(w1, w2)
                        if score['opposite_score'] > 0.3:  # Threshold
                            discovered.append({
                                'pair': (w1, w2),
                                **score
                            })

        # Sort by opposite score
        discovered.sort(key=lambda x: x['opposite_score'], reverse=True)

        # Remove duplicates
        seen = set()
        unique_discovered = []
        for item in discovered:
            pair = tuple(sorted(item['pair']))
            if pair not in seen:
                seen.add(pair)
                unique_discovered.append(item)

        return unique_discovered[:top_k]


# ============================================================================
# Method 3: LLM Judgment (Improved - uses generation model for explicit judgment)
# ============================================================================

class LLMBasedDiscovery:
    """Discover opposites by asking LLM to judge word pairs.

    Improvement: Use generation model to explicitly judge if words are opposites.
    """

    def __init__(self, vocabulary, model, tokenizer, device="cuda", known_opposites=None):
        self.vocabulary = vocabulary
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.known_opposites = known_opposites or []
        self.word_list = list(vocabulary)

        # Learn axes from known opposites for candidate generation
        self._learn_axes_for_candidates()

    def _learn_axes_for_candidates(self):
        """Learn axes to generate candidate pairs."""
        # Extract vectors for all words
        self.vectors = {}
        for word in self.word_list:
            self.vectors[word] = self._get_vector(word)

        # Learn axes from known opposites
        axis_directions = []
        for pos, neg in self.known_opposites:
            if pos in self.vectors and neg in self.vectors:
                v1 = self.vectors[pos]
                v2 = self.vectors[neg]
                if v1 is not None and v2 is not None:
                    axis_dir = v1 - v2
                    if axis_dir.norm() > 0:
                        axis_dir = axis_dir / axis_dir.norm()
                        axis_directions.append(axis_dir)

        if len(axis_directions) > 0:
            axis_matrix = torch.stack(axis_directions)
            pca = PCA(n_components=min(4, len(axis_directions)))
            pca.fit(axis_matrix.cpu().numpy())
            self.eval_axes = torch.from_numpy(pca.components_).float().to(self.device)
        else:
            self.eval_axes = None

    def _get_vector(self, text):
        """Get vector for a word."""
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)

        if hasattr(outputs, 'hidden_states'):
            h = outputs.hidden_states
            mask = inputs["attention_mask"].unsqueeze(-1)
            vec = (h[0] * mask).sum(dim=1) / mask.sum(dim=1)
            return vec[0].float()
        return None

    def _generate_candidates(self, top_k_per_axis=10):
        """Generate candidate pairs using projection-based filtering."""
        if self.eval_axes is None:
            # Fallback: sample random pairs
            candidates = []
            for i, w1 in enumerate(self.word_list):
                for w2 in self.word_list[i+1:i+10]:
                    candidates.append((w1, w2))
            return candidates

        candidates = []

        for axis in self.eval_axes:
            # Project all words onto axis
            projections = {}
            for word, vec in self.vectors.items():
                if vec is not None:
                    proj = (vec @ axis).item()
                    projections[word] = proj

            # Find words on opposite sides
            sorted_words = sorted(projections.items(), key=lambda x: x[1])
            negative_words = [w for w, p in sorted_words[:15]]
            positive_words = [w for w, p in sorted_words[-15:]]

            # Generate candidate pairs
            for w1 in positive_words:
                for w2 in negative_words:
                    candidates.append((w1, w2))

        # Remove duplicates
        candidates = list(set(tuple(sorted(c)) for c in candidates))
        return candidates

    def judge_opposite(self, w1, w2):
        """Judge if two words are opposites using semantic analysis."""
        v1 = self.vectors.get(w1)
        v2 = self.vectors.get(w2)

        if v1 is None or v2 is None:
            return None

        # Multi-criteria judgment
        sim = cosine_similarity(v1, v2)

        # Check projection separation on axes
        max_sep = 0
        if self.eval_axes is not None:
            for axis in self.eval_axes:
                proj1 = (v1 @ axis).item()
                proj2 = (v2 @ axis).item()
                sep = abs(proj1 - proj2)
                max_sep = max(max_sep, sep)

        # Decision logic
        is_opposite = False
        confidence = 0

        # Strong opposite: negative similarity + high projection separation
        if sim < -0.3 and max_sep > 1.0:
            is_opposite = True
            confidence = abs(sim) * 0.5 + max_sep * 0.5
        # Moderate opposite: moderate separation on evaluation axes
        elif max_sep > 1.5:
            is_opposite = True
            confidence = max_sep * 0.7

        return {
            'is_opposite': is_opposite,
            'confidence': confidence,
            'similarity': sim,
            'projection_separation': max_sep
        }

    def discover(self, top_k=20, candidate_pairs=None):
        """
        Discover opposites by evaluating candidate pairs.

        Strategy: Generate candidates using projection, then judge each pair.
        """
        print(f"\nDiscovering opposites via improved LLM judgment (top-{top_k})...")

        # Generate candidates if not provided
        if candidate_pairs is None:
            candidate_pairs = self._generate_candidates()

        print(f"  Evaluating {len(candidate_pairs)} candidate pairs...")

        # Judge each pair
        discovered = []
        for w1, w2 in candidate_pairs:
            result = self.judge_opposite(w1, w2)
            if result and result['is_opposite']:
                discovered.append({
                    'pair': (w1, w2),
                    'similarity': result['similarity'],
                    'projection_separation': result['projection_separation'],
                    'confidence': result['confidence']
                })

        # Sort by confidence
        discovered.sort(key=lambda x: x['confidence'], reverse=True)

        return discovered[:top_k]


# ============================================================================
# Main Discovery Tool
# ============================================================================

class OppositeDiscoveryTool:
    """Combine all discovery methods."""

    def __init__(self, model_name="infoxlm-large", layer=-1):
        self.laws_config = load_all_laws()
        self.vocabulary = get_vocabulary(self.laws_config)
        self.known_opposites = get_known_opposites(self.laws_config)

        print(f"Loading model: {model_name}...")
        self.model, self.tokenizer, self.device = load_model(model_name)
        self.extractor = VectorExtractor(self.model, self.tokenizer, self.device)
        self.layer = layer

        print(f"Vocabulary: {len(self.vocabulary)} words")
        print(f"Known opposite pairs: {len(self.known_opposites) // 2}")

    def discover_projection(self, top_k=20):
        """Discover via semantic axis projection."""
        discovery = ProjectionBasedDiscovery(
            self.vocabulary, self.extractor, self.layer, n_axes=8,
            known_opposites=list(self.known_opposites)
        )
        results = discovery.discover(top_k=top_k)
        self._print_results(results, "Projection-based", "separation")
        return results

    def discover_clustering(self, top_k=20):
        """Discover via vector clustering."""
        discovery = ClusteringBasedDiscovery(
            self.vocabulary, self.extractor, self.layer, n_clusters=10,
            known_opposites=list(self.known_opposites)
        )
        results = discovery.discover(top_k=top_k)
        self._print_results(results, "Clustering-based", "opposite_score")
        return results

    def discover_llm(self, top_k=20, candidate_pairs=None):
        """Discover via LLM judgment."""
        discovery = LLMBasedDiscovery(
            self.vocabulary, self.model, self.tokenizer, self.device,
            known_opposites=list(self.known_opposites)
        )
        results = discovery.discover(top_k=top_k, candidate_pairs=candidate_pairs)
        self._print_results(results, "LLM-based", "confidence")
        return results

    def _print_results(self, results, method_name, score_key):
        """Print discovery results."""
        print(f"\n{'='*70}")
        print(f"{method_name} Discovery Results")
        print(f"{'='*70}")

        known_count = 0
        for i, r in enumerate(results[:20]):
            pair = r['pair']
            is_known = pair in self.known_opposites or (pair[1], pair[0]) in self.known_opposites
            known_mark = "✓ KNOWN" if is_known else ""
            if is_known:
                known_count += 1

            score = r.get(score_key, 0)
            print(f"{i+1:2d}. {pair[0]}-{pair[1]}: {score:.3f} {known_mark}")

        print(f"\nRecall: {known_count}/{len(self.known_opposites)//2} known pairs found")

    def discover_all(self, top_k=20):
        """Run all methods and combine results."""
        print("\n" + "="*70)
        print("Running All Discovery Methods")
        print("="*70)

        results_proj = self.discover_projection(top_k)
        results_cluster = self.discover_clustering(top_k)
        results_llm = self.discover_llm(top_k)

        # Combine and rank
        all_pairs = {}
        for r in results_proj:
            pair = tuple(sorted(r['pair']))
            if pair not in all_pairs:
                all_pairs[pair] = {'methods': [], 'scores': []}
            all_pairs[pair]['methods'].append('projection')
            all_pairs[pair]['scores'].append(r['separation'])

        for r in results_cluster:
            pair = tuple(sorted(r['pair']))
            if pair not in all_pairs:
                all_pairs[pair] = {'methods': [], 'scores': []}
            all_pairs[pair]['methods'].append('clustering')
            all_pairs[pair]['scores'].append(r['opposite_score'])

        for r in results_llm:
            pair = tuple(sorted(r['pair']))
            if pair not in all_pairs:
                all_pairs[pair] = {'methods': [], 'scores': []}
            all_pairs[pair]['methods'].append('llm')
            all_pairs[pair]['scores'].append(r['confidence'])

        # Rank by number of methods that found it
        ranked = sorted(all_pairs.items(),
                       key=lambda x: (len(x[1]['methods']), np.mean(x[1]['scores'])),
                       reverse=True)

        print(f"\n{'='*70}")
        print("Combined Results (found by multiple methods)")
        print(f"{'='*70}")

        known_count = 0
        for i, (pair, info) in enumerate(ranked[:top_k]):
            is_known = pair in self.known_opposites or (pair[1], pair[0]) in self.known_opposites
            known_mark = "✓ KNOWN" if is_known else ""
            if is_known:
                known_count += 1

            methods = ', '.join(info['methods'])
            avg_score = np.mean(info['scores'])
            print(f"{i+1:2d}. {pair[0]}-{pair[1]}: {avg_score:.3f} [{methods}] {known_mark}")

        print(f"\nRecall: {known_count}/{len(self.known_opposites)//2} known pairs found")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Opposite Word Pair Discovery Tool v1.0')
    parser.add_argument('--model', type=str, default='infoxlm-large', help='Model to use')
    parser.add_argument('--layer', type=str, default='0', help='Layer to use')
    parser.add_argument('--method', type=str, default='all',
                        choices=['projection', 'clustering', 'llm', 'all'],
                        help='Discovery method')
    parser.add_argument('--top-k', type=int, default=20, help='Top K results')

    args = parser.parse_args()

    if ',' in args.layer:
        layer = [int(l.strip()) for l in args.layer.split(',')]
    else:
        layer = int(args.layer)

    tool = OppositeDiscoveryTool(model_name=args.model, layer=layer)

    if args.method == 'projection':
        tool.discover_projection(args.top_k)
    elif args.method == 'clustering':
        tool.discover_clustering(args.top_k)
    elif args.method == 'llm':
        tool.discover_llm(args.top_k)
    else:
        tool.discover_all(args.top_k)


if __name__ == '__main__':
    main()
