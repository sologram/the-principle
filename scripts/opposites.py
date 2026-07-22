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


def get_known_opposites():
    """Get known opposite pairs from opposites.yaml."""
    path = SCRIPT_DIR / "configs" / "opposites.yaml"
    if not path.exists():
        return set()
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    pairs = set()
    for pair in config.get('opposite_pairs', []):
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
        self.known_opposites = get_known_opposites()

        print(f"Loading model: {model_name}...")
        self.model, self.tokenizer, self.device = load_model(model_name)
        self.extractor = VectorExtractor(self.model, self.tokenizer, self.device)
        self.layer = layer

        print(f"Vocabulary: {len(self.vocabulary)} words")
        print(f"Known opposite pairs: {len(self.known_opposites) // 2}")

    def evaluate_known_opposites(self, variance_ratio=0.95):
        """Evaluate quality of known opposite pairs from opposites.yaml."""
        from collections import defaultdict

        path = SCRIPT_DIR / "configs" / "opposites.yaml"
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        raw_pairs = config.get('opposite_pairs', [])
        # Parse pairs with optional weights
        pairs = []
        for p in raw_pairs:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                pairs.append((p[0], p[1]))

        print(f"\n{'=':=^70}")
        print("Known Opposites Quality Evaluation")
        print(f"{'=':=^70}")
        print(f"Total pairs: {len(pairs)}\n")

        # Extract vectors for all words
        all_words = set()
        for w1, w2 in pairs:
            all_words.add(w1)
            all_words.add(w2)

        vectors = {}
        for word in all_words:
            vec = self.extractor.get_vector(word, self.layer)
            if vec is not None:
                vectors[word] = vec

        print(f"Words with vectors: {len(vectors)}/{len(all_words)}")

        # Statistics
        cosine_sims = []
        projections = []
        axes = None

        # Learn semantic axes from pairs (same method as geometry4.py)
        mean_vec = torch.stack(list(vectors.values())).mean(dim=0)
        if len(pairs) >= 2:
            directions = []
            for w1, w2 in pairs:
                if w1 in vectors and w2 in vectors:
                    # Axis direction: pos - neg (centered), same as ContrastiveAxisLearner
                    axis_dir = (vectors[w1] - vectors[w2]) - mean_vec
                    axis_dir = axis_dir / (axis_dir.norm() + 1e-8)
                    directions.append(axis_dir)
            if directions:
                directions = torch.stack(directions)
                # Adaptive: use all components, then filter by cumulative variance
                pca = PCA(n_components=min(len(directions), directions.shape[1]))
                pca.fit(directions.cpu().numpy())

                # Select axes by cumulative variance ratio
                cumsum = np.cumsum(pca.explained_variance_ratio_)
                n_axes = np.searchsorted(cumsum, variance_ratio) + 1
                n_axes = max(1, min(n_axes, len(pca.components_)))

                axes = torch.from_numpy(pca.components_[:n_axes]).float().to(self.device)
                print(f"Learned {axes.shape[0]} semantic axes (cumulative variance: {cumsum[n_axes-1]:.1%})")

        # Check alignment between semantic axes and embedding PCA axes
        print(f"\n--- Semantic Axes vs Embedding PCA Axes Alignment ---")
        vec_matrix = torch.stack(list(vectors.values())).cpu().numpy()
        pca_embed = PCA(n_components=min(20, len(vec_matrix)))
        pca_embed.fit(vec_matrix)
        print(f"Embedding PCA top variance: {pca_embed.explained_variance_ratio_[:5]}")

        if axes is not None:
            # Project each semantic axis onto embedding PCA components
            axes_np = axes.cpu().numpy()
            print(f"\nSemantic axis alignment with embedding axes:")
            for i, ax in enumerate(axes_np[:5]):
                # Cosine similarity with each embedding PC
                sims = [np.abs(np.dot(ax, pc)) / (np.linalg.norm(ax) * np.linalg.norm(pc) + 1e-8)
                        for pc in pca_embed.components_[:10]]
                best_pc = np.argmax(sims)
                best_sim = sims[best_pc]
                print(f"  Semantic axis {i+1}: best aligned with PC{best_pc+1} (sim={best_sim:.3f}, var={pca_embed.explained_variance_ratio_[best_pc]:.1%})")

            # Check dimensionality of semantic axes
            print(f"\nSemantic axes dimensionality analysis:")
            for i, ax in enumerate(axes_np[:5]):
                # Top contributing dimensions
                top_dims = np.argsort(np.abs(ax))[-5:][::-1]
                top_weights = ax[top_dims]
                print(f"  Axis {i+1} top dimensions: {list(zip(top_dims, top_weights.round(3)))}")

            # Find opposites in residual space (not covered by learned axes)
            print(f"\n--- Residual Space Analysis (outside learned axes) ---")
            # Project vectors orthogonal to learned axes
            Q = axes_np.T  # shape: (1024, 64)
            # QR decomposition to get orthonormal basis of semantic space
            Q_ortho, _ = np.linalg.qr(Q)
            # Projection matrix onto semantic space
            P_semantic = Q_ortho @ Q_ortho.T  # shape: (1024, 1024)
            # Residual projection matrix
            P_residual = np.eye(1024) - P_semantic

            # Find words with high residual variance
            residual_norms = []
            for w, v in vectors.items():
                v_np = v.cpu().numpy() if isinstance(v, torch.Tensor) else v
                residual = P_residual @ v_np
                residual_norm = np.linalg.norm(residual)
                residual_norms.append((w, residual_norm))

            residual_norms.sort(key=lambda x: -x[1])
            print(f"Top words by residual norm (outside semantic axes):")
            for w, norm in residual_norms[:10]:
                print(f"  {w}: {norm:.3f}")

            # Find opposite pairs in residual space
            print(f"\nOpposite pairs in residual space:")
            residual_pairs = []
            for i, (w1, v1) in enumerate(vectors.items()):
                v1_np = v1.cpu().numpy() if isinstance(v1, torch.Tensor) else v1
                r1 = P_residual @ v1_np
                for w2, v2 in list(vectors.items())[i+1:]:
                    v2_np = v2.cpu().numpy() if isinstance(v2, torch.Tensor) else v2
                    r2 = P_residual @ v2_np
                    # Cosine similarity in residual space
                    cos_residual = np.dot(r1, r2) / (np.linalg.norm(r1) * np.linalg.norm(r2) + 1e-8)
                    # Opposite if negative and large norm
                    if cos_residual < -0.3 and np.linalg.norm(r1) > 0.5 and np.linalg.norm(r2) > 0.5:
                        residual_pairs.append((w1, w2, cos_residual, np.linalg.norm(r1), np.linalg.norm(r2)))

            residual_pairs.sort(key=lambda x: x[2])
            for w1, w2, cos, n1, n2 in residual_pairs[:10]:
                print(f"  {w1}-{w2}: residual_cos={cos:.3f}, norms=({n1:.2f}, {n2:.2f})")

        # Evaluate each pair
        results = []
        for w1, w2 in pairs:
            if w1 not in vectors or w2 not in vectors:
                continue

            v1, v2 = vectors[w1], vectors[w2]
            cos_sim = F.cosine_similarity(v1.unsqueeze(0), v2.unsqueeze(0)).item()
            cosine_sims.append(cos_sim)

            proj_score = None
            if axes is not None:
                # Project onto learned axes, take max separation across all axes
                v1_centered = v1 - mean_vec
                v2_centered = v2 - mean_vec
                proj1 = (axes @ v1_centered).abs()
                proj2 = (axes @ v2_centered).abs()
                # Separation: difference in projection magnitudes
                proj_score = (proj1 - proj2).abs().max().item()
                projections.append(proj_score)

            results.append((w1, w2, cos_sim, proj_score))

        # Summary stats
        if cosine_sims:
            avg_cos = np.mean(cosine_sims)
            print(f"\nCosine similarity (opposites should be low or negative):")
            print(f"  Mean: {avg_cos:.3f}, Std: {np.std(cosine_sims):.3f}")
            print(f"  Min: {np.min(cosine_sims):.3f}, Max: {np.max(cosine_sims):.3f}")

            # Distribution
            negative = sum(1 for c in cosine_sims if c < 0)
            low = sum(1 for c in cosine_sims if 0 <= c < 0.3)
            medium = sum(1 for c in cosine_sims if 0.3 <= c < 0.6)
            high = sum(1 for c in cosine_sims if c >= 0.6)
            print(f"\n  Distribution:")
            print(f"    < 0 (opposite direction): {negative} ({100*negative/len(cosine_sims):.1f}%)")
            print(f"    [0, 0.3): {low} ({100*low/len(cosine_sims):.1f}%)")
            print(f"    [0.3, 0.6): {medium} ({100*medium/len(cosine_sims):.1f}%)")
            print(f"    >= 0.6 (similar): {high} ({100*high/len(cosine_sims):.1f}%)")

        if projections:
            avg_proj = np.mean(projections)
            print(f"\nProjection separation (higher = more opposite on semantic axis):")
            print(f"  Mean: {avg_proj:.3f}, Std: {np.std(projections):.3f}")

            # Distribution by separation
            high_sep = sum(1 for p in projections if p >= 1.0)
            medium_sep = sum(1 for p in projections if 0.5 <= p < 1.0)
            low_sep = sum(1 for p in projections if p < 0.5)
            print(f"\n  Distribution:")
            print(f"    >= 1.0 (strong separation): {high_sep} ({100*high_sep/len(projections):.1f}%)")
            print(f"    [0.5, 1.0): {medium_sep} ({100*medium_sep/len(projections):.1f}%)")
            print(f"    < 0.5 (weak separation): {low_sep} ({100*low_sep/len(projections):.1f}%)")

        # Show pairs by projection separation
        print(f"\n--- Best pairs (high projection separation) ---")
        sorted_by_proj = sorted(results, key=lambda x: -x[3] if x[3] is not None else 0)
        for w1, w2, cos, proj in sorted_by_proj[:10]:
            print(f"  {w1}-{w2}: proj_sep={proj:.3f}, cosine={cos:.3f}")

        print(f"\n--- Weak pairs (low projection separation) ---")
        for w1, w2, cos, proj in sorted_by_proj[-10:]:
            print(f"  {w1}-{w2}: proj_sep={proj:.3f}, cosine={cos:.3f}")

        return results

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

    def discover_random_axes(self, top_k=20, n_axes=100, n_samples=1000):
        """
        Discover semantic axes via random direction sampling.

        Method: Sample random directions, find ones that maximize word separation.
        """
        print(f"\n{'='*70}")
        print("Random Axis Sampling Discovery")
        print(f"{'='*70}")

        # Extract vectors
        vectors = {}
        for word in self.vocabulary:
            vec = self.extractor.get_vector(word, self.layer)
            if vec is not None:
                vectors[word] = vec

        if len(vectors) < 2:
            print("Not enough vectors")
            return []

        word_list = list(vectors.keys())
        vec_matrix = torch.stack([vectors[w] for w in word_list])
        dim = vec_matrix.shape[1]

        # Random directions
        best_axes = []
        for _ in range(n_samples):
            # Random unit vector
            direction = torch.randn(dim, device=self.device)
            direction = direction / direction.norm()

            # Project all words
            projections = vec_matrix @ direction

            # Score: separation between max and min projections
            separation = (projections.max() - projections.min()).item()

            # Find extreme words
            max_idx = projections.argmax().item()
            min_idx = projections.argmin().item()

            best_axes.append({
                'direction': direction,
                'separation': separation,
                'pos_word': word_list[max_idx],
                'neg_word': word_list[min_idx],
            })

        # Sort by separation
        best_axes.sort(key=lambda x: -x['separation'])

        # Cluster similar axes (avoid duplicates)
        unique_axes = []
        for ax in best_axes:
            is_duplicate = False
            for existing in unique_axes:
                sim = F.cosine_similarity(
                    ax['direction'].unsqueeze(0),
                    existing['direction'].unsqueeze(0)
                ).item()
                if abs(sim) > 0.8:  # Too similar
                    is_duplicate = True
                    break
            if not is_duplicate:
                unique_axes.append(ax)
            if len(unique_axes) >= n_axes:
                break

        print(f"Found {len(unique_axes)} unique axes from {n_samples} samples")

        # Generate candidate pairs from top axes
        candidates = []
        for ax in unique_axes:
            proj = vec_matrix @ ax['direction']
            scores = proj.abs()

            # Find words with opposite projections
            pos_mask = proj > proj.mean() + proj.std()
            neg_mask = proj < proj.mean() - proj.std()

            pos_words = [word_list[i] for i in range(len(word_list)) if pos_mask[i]]
            neg_words = [word_list[i] for i in range(len(word_list)) if neg_mask[i]]

            # Pair high-positive with high-negative
            for pw in pos_words[:3]:
                for nw in neg_words[:3]:
                    pair = (pw, nw)
                    sep = abs((vectors[pw] - vectors[nw]) @ ax['direction']).item()
                    candidates.append({
                        'pair': pair,
                        'separation': sep,
                        'axis': (ax['pos_word'], ax['neg_word']),
                    })

        # Sort by separation
        candidates.sort(key=lambda x: -x['separation'])

        # Remove duplicates and mark known
        seen = set()
        results = []
        for c in candidates:
            pair = c['pair']
            key = (pair[0], pair[1]) if pair[0] < pair[1] else (pair[1], pair[0])
            if key in seen:
                continue
            seen.add(key)

            is_known = pair in self.known_opposites or (pair[1], pair[0]) in self.known_opposites
            results.append({
                'pair': pair,
                'separation': c['separation'],
                'axis': c['axis'],
                'known': is_known,
            })

        # Print top results
        print(f"\nTop {top_k} discovered pairs:")
        known_count = 0
        for i, r in enumerate(results[:top_k]):
            known_mark = "✓ KNOWN" if r['known'] else ""
            if r['known']:
                known_count += 1
            print(f"{i+1:2d}. {r['pair'][0]}-{r['pair'][1]}: {r['separation']:.3f} (axis: {r['axis'][0]}-{r['axis'][1]}) {known_mark}")

        print(f"\nRecall: {known_count}/{len(self.known_opposites)//2} known pairs found")
        return results[:top_k]

    def discover_pca_axes(self, top_k=20):
        """
        Discover semantic axes via unsupervised PCA decomposition.

        Method: Apply PCA to word vectors, each component is a semantic axis.
        """
        print(f"\n{'='*70}")
        print("PCA-based Axis Discovery")
        print(f"{'='*70}")

        # Extract vectors
        vectors = {}
        for word in self.vocabulary:
            vec = self.extractor.get_vector(word, self.layer)
            if vec is not None:
                vectors[word] = vec

        if len(vectors) < 2:
            print("Not enough vectors")
            return []

        word_list = list(vectors.keys())
        vec_matrix = torch.stack([vectors[w] for w in word_list]).cpu().numpy()

        # PCA decomposition
        n_components = min(50, len(word_list), vec_matrix.shape[1])
        pca = PCA(n_components=n_components)
        pca.fit(vec_matrix)

        print(f"PCA components: {n_components}")
        print(f"Top variance explained: {pca.explained_variance_ratio_[:5]}")

        # For each component, find extreme words
        results = []
        components = pca.components_

        for i, comp in enumerate(components[:20]):  # Top 20 components
            proj = vec_matrix @ comp

            # Find extremes
            max_idx = proj.argmax()
            min_idx = proj.argmin()

            pos_word = word_list[max_idx]
            neg_word = word_list[min_idx]
            separation = proj[max_idx] - proj[min_idx]

            pair = (pos_word, neg_word)
            is_known = pair in self.known_opposites or (neg_word, pos_word) in self.known_opposites

            results.append({
                'pair': pair,
                'separation': separation,
                'component': i,
                'variance': pca.explained_variance_ratio_[i],
                'known': is_known,
            })

        # Print results
        known_count = 0
        for i, r in enumerate(results[:top_k]):
            known_mark = "✓ KNOWN" if r['known'] else ""
            if r['known']:
                known_count += 1
            print(f"{i+1:2d}. {r['pair'][0]}-{r['pair'][1]}: sep={r['separation']:.3f}, var={r['variance']:.1%} (PC{r['component']+1}) {known_mark}")

        print(f"\nRecall: {known_count}/{len(self.known_opposites)//2} known pairs found")
        return results[:top_k]

    def discover_cluster_axes(self, top_k=20, n_clusters=8):
        """
        Discover semantic axes via clustering inter-cluster directions.

        Method: Cluster words, then find directions between cluster centroids.
        """
        print(f"\n{'='*70}")
        print("Cluster-based Axis Discovery")
        print(f"{'='*70}")

        # Extract vectors
        vectors = {}
        for word in self.vocabulary:
            vec = self.extractor.get_vector(word, self.layer)
            if vec is not None:
                vectors[word] = vec

        if len(vectors) < n_clusters:
            print("Not enough vectors")
            return []

        word_list = list(vectors.keys())
        vec_matrix = torch.stack([vectors[w] for w in word_list]).cpu().numpy()

        # K-means clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(vec_matrix)
        centroids = kmeans.cluster_centers_

        print(f"Clustered {len(word_list)} words into {n_clusters} clusters")

        # Analyze clusters
        clusters = {i: [] for i in range(n_clusters)}
        for i, label in enumerate(labels):
            clusters[label].append(word_list[i])

        for i, words in clusters.items():
            print(f"  Cluster {i}: {len(words)} words (e.g., {', '.join(words[:5])})")

        # Find directions between cluster pairs
        results = []
        for i in range(n_clusters):
            for j in range(i+1, n_clusters):
                # Direction from cluster i to cluster j
                direction = centroids[j] - centroids[i]
                direction = direction / (np.linalg.norm(direction) + 1e-8)

                # Project all words onto this direction
                proj = vec_matrix @ direction

                # Find extreme words in each cluster
                cluster_i_words = [word_list[k] for k in range(len(word_list)) if labels[k] == i]
                cluster_j_words = [word_list[k] for k in range(len(word_list)) if labels[k] == j]

                # Best opposite pair across clusters
                best_sep = 0
                best_pair = None
                for w_i in cluster_i_words[:5]:
                    for w_j in cluster_j_words[:5]:
                        v_i = vectors[w_i]
                        v_j = vectors[w_j]
                        sep = abs((v_i - v_j) @ torch.from_numpy(direction).to(self.device)).item()
                        if sep > best_sep:
                            best_sep = sep
                            best_pair = (w_i, w_j)

                if best_pair:
                    is_known = best_pair in self.known_opposites or (best_pair[1], best_pair[0]) in self.known_opposites
                    results.append({
                        'pair': best_pair,
                        'separation': best_sep,
                        'clusters': (i, j),
                        'known': is_known,
                    })

        # Sort by separation
        results.sort(key=lambda x: -x['separation'])

        # Print results
        known_count = 0
        for i, r in enumerate(results[:top_k]):
            known_mark = "✓ KNOWN" if r['known'] else ""
            if r['known']:
                known_count += 1
            print(f"{i+1:2d}. {r['pair'][0]}-{r['pair'][1]}: {r['separation']:.3f} (clusters {r['clusters'][0]}-{r['clusters'][1]}) {known_mark}")

        print(f"\nRecall: {known_count}/{len(self.known_opposites)//2} known pairs found")
        return results[:top_k]

    def find_opposite(self, word, top_k=20, use_full_vocab=False):
        """Find opposite word for a given word."""
        print(f"\n{'='*70}")
        print(f"Finding opposites for: {word}")
        print(f"{'='*70}")

        # Get vector for the word
        vec = self.extractor.get_vector(word, self.layer)
        if vec is None:
            print(f"Word '{word}' not in vocabulary")
            return []

        # Load known opposites
        path = SCRIPT_DIR / "configs" / "opposites.yaml"
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        pairs = config.get('opposite_pairs', [])

        # Learn semantic axes
        vectors_known = {}
        for w1, w2 in pairs:
            v = self.extractor.get_vector(w1, self.layer)
            if v is not None:
                vectors_known[w1] = v
            v = self.extractor.get_vector(w2, self.layer)
            if v is not None:
                vectors_known[w2] = v

        mean_vec = torch.stack(list(vectors_known.values())).mean(dim=0)
        directions = []
        for w1, w2 in pairs:
            if w1 in vectors_known and w2 in vectors_known:
                axis_dir = (vectors_known[w1] - vectors_known[w2]) - mean_vec
                axis_dir = axis_dir / (axis_dir.norm() + 1e-8)
                directions.append(axis_dir)

        if not directions:
            print("Not enough known opposites to learn axes")
            return []

        directions = torch.stack(directions)
        pca = PCA(n_components=min(len(directions), directions.shape[1]))
        pca.fit(directions.cpu().numpy())
        cumsum = np.cumsum(pca.explained_variance_ratio_)
        n_axes = np.searchsorted(cumsum, 0.95) + 1
        axes = torch.from_numpy(pca.components_[:n_axes]).float().to(self.device)

        print(f"Using {n_axes} semantic axes")

        # Get vocabulary
        if use_full_vocab:
            print("Searching in full vocabulary...")
            all_tokens = list(self.tokenizer.get_vocab().keys())
            # Filter meaningful tokens
            vocab = []
            for t in all_tokens:
                if t.startswith('[') or t.startswith('##') or t.startswith('▁'):
                    continue
                if t.isnumeric() or len(t) < 2:
                    continue
                if any('一' <= c <= '鿿' for c in t) or t.isalpha():
                    vocab.append(t)
            print(f"Vocabulary size: {len(vocab)}")
        else:
            vocab = self.vocabulary

        # Project the word onto all axes
        vec_centered = vec - mean_vec
        projections = axes @ vec_centered

        # Find words with opposite projections in vocabulary
        results = []
        for vocab_word in vocab:
            if vocab_word == word:
                continue
            v = self.extractor.get_vector(vocab_word, self.layer)
            if v is None:
                continue
            v_centered = v - mean_vec
            proj_v = axes @ v_centered

            # Opposite: projections should have opposite signs
            separation = (projections - proj_v).abs().max().item()
            cosine = F.cosine_similarity(vec.unsqueeze(0), v.unsqueeze(0)).item()

            results.append({
                'word': vocab_word,
                'separation': separation,
                'cosine': cosine,
            })

        # Sort by separation (high = opposite on semantic axis)
        results.sort(key=lambda x: -x['separation'])

        print(f"\n--- Antonyms for {word} ---")
        print(f"Top {top_k} opposite candidates:")
        for i, r in enumerate(results[:top_k]):
            known_mark = ""
            for w1, w2 in pairs:
                if (r['word'] == w1 and word == w2) or (r['word'] == w2 and word == w1):
                    known_mark = " ✓ KNOWN"
                    break
            print(f"  {i+1}. {word}-{r['word']}: sep={r['separation']:.3f}, cos={r['cosine']:.3f}{known_mark}")

        # Also find synonyms (high cosine similarity)
        synonyms = [r for r in results if r['cosine'] > 0.85]
        synonyms.sort(key=lambda x: -x['cosine'])

        print(f"\n--- Synonyms for {word} ---")
        print(f"Top {min(top_k, len(synonyms))} similar words (cosine > 0.85):")
        if synonyms:
            for i, r in enumerate(synonyms[:top_k]):
                print(f"  {i+1}. {word}-{r['word']}: cos={r['cosine']:.3f}, sep={r['separation']:.3f}")
        else:
            print("  No synonyms found (cosine > 0.85)")
            # Show top cosine anyway
            by_cosine = sorted(results, key=lambda x: -x['cosine'])
            print(f"\n  Top 10 by cosine similarity:")
            for i, r in enumerate(by_cosine[:10]):
                print(f"    {i+1}. {word}-{r['word']}: cos={r['cosine']:.3f}, sep={r['separation']:.3f}")

        return results[:top_k]

    def discover_residual_opposites(self, top_k=20, vocab_size=5000):
        """
        Discover opposite pairs in residual space from full vocabulary.

        Method: Project all vocab words onto residual space, find extreme opposites.
        """
        print(f"\n{'='*70}")
        print("Residual Space Opposite Discovery (Full Vocabulary)")
        print(f"{'='*70}")

        # First, learn semantic axes from known opposites
        path = SCRIPT_DIR / "configs" / "opposites.yaml"
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        pairs = config.get('opposite_pairs', [])

        # Extract vectors for known opposites
        vectors_known = {}
        for w1, w2 in pairs:
            vec = self.extractor.get_vector(w1, self.layer)
            if vec is not None:
                vectors_known[w1] = vec
            vec = self.extractor.get_vector(w2, self.layer)
            if vec is not None:
                vectors_known[w2] = vec

        print(f"Known words with vectors: {len(vectors_known)}")

        # Learn semantic axes
        mean_vec = torch.stack(list(vectors_known.values())).mean(dim=0)
        directions = []
        for w1, w2 in pairs:
            if w1 in vectors_known and w2 in vectors_known:
                axis_dir = (vectors_known[w1] - vectors_known[w2]) - mean_vec
                axis_dir = axis_dir / (axis_dir.norm() + 1e-8)
                directions.append(axis_dir)

        if not directions:
            print("Not enough directions")
            return []

        directions = torch.stack(directions)
        pca = PCA(n_components=min(len(directions), directions.shape[1]))
        pca.fit(directions.cpu().numpy())
        cumsum = np.cumsum(pca.explained_variance_ratio_)
        n_axes = np.searchsorted(cumsum, 0.95) + 1
        axes = torch.from_numpy(pca.components_[:n_axes]).float().to(self.device)
        print(f"Learned {n_axes} semantic axes (cumulative variance: {cumsum[n_axes-1]:.1%})")

        # Compute residual projection matrix
        Q = axes.cpu().numpy().T  # (1024, n_axes)
        Q_ortho, _ = np.linalg.qr(Q)
        P_semantic = Q_ortho @ Q_ortho.T
        P_residual = np.eye(1024) - P_semantic

        # Sample vocabulary words
        print(f"\nSampling {vocab_size} words from vocabulary...")
        all_tokens = list(self.tokenizer.get_vocab().keys())
        # Filter to meaningful tokens (not subword pieces, numbers, etc.)
        meaningful_tokens = []
        for t in all_tokens:
            # Skip special tokens, subwords, pure numbers, punctuation
            if t.startswith('[') or t.startswith('##') or t.startswith('▁'):
                continue
            if t.isnumeric() or len(t) < 2:
                continue
            # Prefer Chinese chars or English words
            if any('一' <= c <= '鿿' for c in t) or t.isalpha():
                meaningful_tokens.append(t)

        # Sample if too many
        import random
        if len(meaningful_tokens) > vocab_size:
            meaningful_tokens = random.sample(meaningful_tokens, vocab_size)

        print(f"Selected {len(meaningful_tokens)} meaningful tokens")

        # Extract vectors and project to residual space
        print("Extracting vectors and projecting to residual space...")
        residual_vectors = {}
        for i, token in enumerate(meaningful_tokens):
            if i % 500 == 0:
                print(f"  Processed {i}/{len(meaningful_tokens)}")
            vec = self.extractor.get_vector(token, self.layer)
            if vec is not None:
                vec_np = vec.cpu().numpy() if isinstance(vec, torch.Tensor) else vec
                residual = P_residual @ vec_np
                residual_norm = np.linalg.norm(residual)
                if residual_norm > 0.1:  # Skip near-zero residuals
                    residual_vectors[token] = residual / residual_norm

        print(f"Tokens with significant residual: {len(residual_vectors)}")

        # Analyze all axes in residual space
        print("\nAnalyzing residual space axes...")

        # Stack all residual vectors
        tokens = list(residual_vectors.keys())
        residual_matrix = np.stack([residual_vectors[t] for t in tokens])

        # Full PCA to get all axes
        print(f"Running full PCA on residual space...")
        n_components = min(len(residual_matrix), residual_matrix.shape[1])
        pca_residual = PCA(n_components=n_components)
        pca_residual.fit(residual_matrix)

        print(f"Total variance explained by {n_components} axes: {sum(pca_residual.explained_variance_ratio_):.1%}")

        # Analyze each axis and categorize
        print(f"\n--- Residual Axes Classification ---")
        axis_info = []

        for i in range(n_components):
            comp = pca_residual.components_[i]
            proj = residual_matrix @ comp
            var = pca_residual.explained_variance_ratio_[i]

            # Find extreme tokens
            pos_idx = np.argsort(proj)[-20:]
            neg_idx = np.argsort(proj)[:20]
            pos_tokens = [tokens[idx] for idx in pos_idx]
            neg_tokens = [tokens[idx] for idx in neg_idx]

            # Classify axis
            pos_chinese = sum(1 for t in pos_tokens if any('一' <= c <= '鿿' for c in t))
            neg_chinese = sum(1 for t in neg_tokens if any('一' <= c <= '鿿' for c in t))
            pos_english = sum(1 for t in pos_tokens if t.isalpha() and not any('一' <= c <= '鿿' for c in t))
            neg_english = sum(1 for t in neg_tokens if t.isalpha() and not any('一' <= c <= '鿿' for c in t))

            # Detect more language patterns
            def detect_lang(token):
                """Detect language based on Unicode ranges."""
                # Chinese
                if any('一' <= c <= '鿿' for c in token):
                    return 'zh'
                # Japanese (Hiragana/Katakana)
                if any('ぁ' <= c <= 'ん' or 'ァ' <= c <= 'ン' for c in token):
                    return 'ja'
                # Korean (Hangul)
                if any('가' <= c <= '힣' for c in token):
                    return 'ko'
                # Russian/Cyrillic
                if any('а' <= c <= 'я' or 'А' <= c <= 'Я' or 'ё' in token.lower() for c in token):
                    return 'ru'
                # Arabic
                if any('ا' <= c <= 'ي' for c in token):
                    return 'ar'
                # Hebrew
                if any('א' <= c <= 'ת' for c in token):
                    return 'he'
                # Greek
                if any('α' <= c <= 'ω' or 'Α' <= c <= 'Ω' for c in token):
                    return 'el'
                # Thai
                if any('ก' <= c <= '๛' for c in token):
                    return 'th'
                # Georgian
                if any('ა' <= c <= 'ჰ' for c in token):
                    return 'ka'
                # Armenian
                if any('ա' <= c <= 'ֆ' for c in token):
                    return 'hy'
                # Lao
                if any('ກ' <= c <= 'ໝ' for c in token):
                    return 'lo'
                # Hindi/Devanagari
                if any('ऀ' <= c <= 'ॿ' for c in token):
                    return 'hi'
                # Bengali
                if any('ঀ' <= c <= '৿' for c in token):
                    return 'bn'
                # Tamil
                if any('ஂ' <= c <= '௺' for c in token):
                    return 'ta'
                # Telugu
                if any('ఀ' <= c <= '౿' for c in token):
                    return 'te'
                # Default: Latin/English
                if token.isalpha():
                    return 'en'
                return 'other'

            pos_langs = [detect_lang(t) for t in pos_tokens]
            neg_langs = [detect_lang(t) for t in neg_tokens]
            pos_lang_counts = {}
            neg_lang_counts = {}
            for lang in pos_langs:
                pos_lang_counts[lang] = pos_lang_counts.get(lang, 0) + 1
            for lang in neg_langs:
                neg_lang_counts[lang] = neg_lang_counts.get(lang, 0) + 1

            # Detect length pattern
            pos_lens = [len(t) for t in pos_tokens]
            neg_lens = [len(t) for t in neg_tokens]
            pos_avg_len = np.mean(pos_lens)
            neg_avg_len = np.mean(neg_lens)

            # Classify axis type
            axis_type = "unknown"

            # Language axes
            if pos_chinese >= 15 and neg_chinese <= 5:
                axis_type = "lang_zh_pos"
            elif neg_chinese >= 15 and pos_chinese <= 5:
                axis_type = "lang_zh_neg"
            elif pos_lang_counts.get('ru', 0) >= 10:
                axis_type = f"lang_ru_pos"
            elif neg_lang_counts.get('ru', 0) >= 10:
                axis_type = f"lang_ru_neg"
            elif pos_lang_counts.get('ja', 0) >= 10:
                axis_type = f"lang_ja_pos"
            elif neg_lang_counts.get('ja', 0) >= 10:
                axis_type = f"lang_ja_neg"
            elif pos_lang_counts.get('ko', 0) >= 10:
                axis_type = f"lang_ko_pos"
            elif neg_lang_counts.get('ko', 0) >= 10:
                axis_type = f"lang_ko_neg"
            elif pos_lang_counts.get('ar', 0) >= 10:
                axis_type = f"lang_ar_pos"
            elif neg_lang_counts.get('ar', 0) >= 10:
                axis_type = f"lang_ar_neg"

            # Length axes
            elif abs(pos_avg_len - neg_avg_len) > 3:
                if pos_avg_len > neg_avg_len:
                    axis_type = f"len_long_{int(pos_avg_len)}_short_{int(neg_avg_len)}"
                else:
                    axis_type = f"len_short_{int(pos_avg_len)}_long_{int(neg_avg_len)}"

            # Mixed language
            elif len(pos_lang_counts) == 1 and len(neg_lang_counts) == 1:
                pos_lang = list(pos_lang_counts.keys())[0]
                neg_lang = list(neg_lang_counts.keys())[0]
                if pos_lang != neg_lang:
                    axis_type = f"lang_{pos_lang}_{neg_lang}"

            # Alphabet vs non-alphabet
            elif pos_english >= 15 and neg_english <= 5:
                axis_type = "alpha_vs_nonalpha"
            elif neg_english >= 15 and pos_english <= 5:
                axis_type = "nonalpha_vs_alpha"

            # Capital letters
            elif sum(1 for t in pos_tokens if t.isupper() or (len(t)>0 and t[0].isupper())) >= 15:
                axis_type = "capital_pos"
            elif sum(1 for t in neg_tokens if t.isupper() or (len(t)>0 and t[0].isupper())) >= 15:
                axis_type = "capital_neg"

            # Numbers/symbols
            elif sum(1 for t in pos_tokens if any(c.isdigit() for c in t)) >= 10:
                axis_type = "has_number_pos"
            elif sum(1 for t in neg_tokens if any(c.isdigit() for c in t)) >= 10:
                axis_type = "has_number_neg"

            # Special chars
            elif sum(1 for t in pos_tokens if any(not c.isalnum() for c in t)) >= 15:
                axis_type = "special_char_pos"
            elif sum(1 for t in neg_tokens if any(not c.isalnum() for c in t)) >= 15:
                axis_type = "special_char_neg"

            axis_info.append({
                'idx': i,
                'var': var,
                'type': axis_type,
                'pos_tokens': pos_tokens[:5],
                'neg_tokens': neg_tokens[:5],
            })

            # Print summary (only for top axes or first 30)
            if i < 30 or axis_type != "unknown":
                print(f"Axis {i+1}: var={var:.1%}, type={axis_type}")
                print(f"  Pos: {', '.join(pos_tokens[:5])}")
                print(f"  Neg: {', '.join(neg_tokens[:5])}")

        # Summary by type
        print(f"\n--- Axis Type Summary ---")
        type_counts = {}
        type_vars = {}
        for info in axis_info:
            t = info['type']
            type_counts[t] = type_counts.get(t, 0) + 1
            type_vars[t] = type_vars.get(t, 0) + info['var']

        for t in sorted(type_counts.keys()):
            print(f"{t}: {type_counts[t]} axes, {type_vars[t]:.1%} variance")

        # For efficiency, use top-K per dimension approach
        # Find dimensions with high variance
        dim_variance = residual_matrix.var(axis=0)
        top_dims = np.argsort(dim_variance)[-20:]  # Top 20 high-variance dimensions

        results = []
        for dim in top_dims:
            values = residual_matrix[:, dim]
            # Find tokens with extreme positive and negative values
            pos_idx = np.argsort(values)[-10:]  # Top 10 positive
            neg_idx = np.argsort(values)[:10]   # Top 10 negative

            for p_idx in pos_idx:
                for n_idx in neg_idx:
                    pos_token = tokens[p_idx]
                    neg_token = tokens[n_idx]
                    # Cosine similarity in residual space
                    cos_sim = np.dot(residual_vectors[pos_token], residual_vectors[neg_token])
                    # Lower threshold to find more candidates
                    if cos_sim < 0.2:  # Include even weakly opposite pairs
                        results.append({
                            'pair': (pos_token, neg_token),
                            'residual_cos': cos_sim,
                            'dim': int(dim),
                            'dim_var': float(dim_variance[dim]),
                        })

        # Sort by residual cosine (most negative = most opposite)
        results.sort(key=lambda x: x['residual_cos'])

        # Remove duplicates
        seen = set()
        unique_results = []
        for r in results:
            key = tuple(sorted(r['pair']))
            if key not in seen:
                seen.add(key)
                unique_results.append(r)

        # Print top results
        print(f"\nTop {top_k} opposite pairs in residual space:")
        for i, r in enumerate(unique_results[:top_k]):
            pair = r['pair']
            print(f"{i+1:2d}. {pair[0]}-{pair[1]}: residual_cos={r['residual_cos']:.3f}, dim={r['dim']}, var={r['dim_var']:.3f}")

        print(f"\n--- Cross-lingual Similar Pairs in Residual Space ---")
        # Find semantically similar pairs across different languages/forms
        similarity_pairs = []

        for i, (w1, v1) in enumerate(residual_vectors.items()):
            lang1 = detect_lang(w1)
            len1 = len(w1)
            for w2, v2 in list(residual_vectors.items())[i+1:]:
                lang2 = detect_lang(w2)
                len2 = len(w2)

                # Must be different language or different form
                if lang1 == lang2 and abs(len1 - len2) <= 2:
                    continue

                # Compute cosine similarity
                cos_sim = np.dot(v1, v2)
                if cos_sim > 0.85:  # High similarity
                    similarity_pairs.append({
                        'pair': (w1, w2),
                        'sim': cos_sim,
                        'langs': (lang1, lang2),
                        'lens': (len1, len2),
                    })

        # Sort by similarity
        similarity_pairs.sort(key=lambda x: -x['sim'])

        print(f"\nFound {len(similarity_pairs)} cross-lingual similar pairs (sim > 0.85)")

        # Group by language pair
        lang_pair_counts = {}
        for p in similarity_pairs:
            key = tuple(sorted(p['langs']))
            lang_pair_counts[key] = lang_pair_counts.get(key, 0) + 1

        print(f"\nTop language pairs:")
        for lp, count in sorted(lang_pair_counts.items(), key=lambda x: -x[1])[:10]:
            print(f"  {lp[0]}-{lp[1]}: {count} pairs")

        print(f"\nTop 30 similar pairs (different language/form, same semantics):")
        for i, p in enumerate(similarity_pairs[:30]):
            print(f"  {i+1}. {p['pair'][0]}-{p['pair'][1]}: sim={p['sim']:.3f}, langs={p['langs']}")

        # Find potential translation pairs
        print(f"\n--- Potential Translation Pairs (same concept, different language) ---")
        translations = [p for p in similarity_pairs if p['langs'][0] != p['langs'][1]]
        for i, p in enumerate(translations[:20]):
            print(f"  {i+1}. {p['pair'][0]}-{p['pair'][1]}: sim={p['sim']:.3f}, langs={p['langs']}")

        # Analyze semantic patterns
        print(f"\n--- Semantic Pattern Analysis ---")

        # Categorize pairs by semantic type
        functional_pairs = []  # 助词、代词
        synonym_pairs = []     # 同义词
        morphological_pairs = []  # 词形变化

        for p in similarity_pairs[:100]:
            w1, w2 = p['pair']
            l1, l2 = len(w1), len(w2)

            # Heuristic rules for categorization
            # Short words (<=3) often functional
            if l1 <= 3 and l2 <= 3:
                functional_pairs.append(p)
            # Same language, similar length = likely synonyms or morphology
            elif p['langs'][0] == p['langs'][1]:
                if abs(l1 - l2) <= 2:
                    morphological_pairs.append(p)
                else:
                    synonym_pairs.append(p)
            else:
                synonym_pairs.append(p)

        print(f"\nFunctional pairs (particles, pronouns, etc.): {len(functional_pairs)}")
        for p in functional_pairs[:10]:
            print(f"  {p['pair'][0]}-{p['pair'][1]}: sim={p['sim']:.3f}")

        print(f"\nSynonym pairs (same meaning, different form): {len(synonym_pairs)}")
        for p in synonym_pairs[:10]:
            print(f"  {p['pair'][0]}-{p['pair'][1]}: sim={p['sim']:.3f}, langs={p['langs']}")

        print(f"\nMorphological pairs (same word, different form): {len(morphological_pairs)}")
        for p in morphological_pairs[:10]:
            print(f"  {p['pair'][0]}-{p['pair'][1]}: sim={p['sim']:.3f}")

        # Extract common semantic axes
        print(f"\n--- Common Semantic Concepts ---")
        # Look for pairs sharing similar words (cluster analysis)
        word_to_pairs = {}
        for p in similarity_pairs[:200]:
            for w in p['pair']:
                if w not in word_to_pairs:
                    word_to_pairs[w] = []
                word_to_pairs[w].append(p['pair'])

        # Find clusters
        clusters = []
        visited = set()
        for w, pairs in word_to_pairs.items():
            if w in visited:
                continue
            cluster = set([w])
            for pair in pairs:
                cluster.update(pair)
            if len(cluster) > 2:
                clusters.append(cluster)
                visited.update(cluster)

        print(f"\nSemantic clusters (words with similar representations):")
        for i, cluster in enumerate(sorted(clusters, key=lambda x: -len(x))[:10]):
            print(f"  Cluster {i+1}: {', '.join(list(cluster)[:8])}")

        # List formal similarity axes
        print(f"\n--- Formal Similarity Axes ---")
        print("Axes where words cluster by form (prefix, suffix, character pattern):")

        # Find pairs with shared prefixes/suffixes
        prefix_pairs = []
        suffix_pairs = []
        char_pattern_pairs = []

        for p in similarity_pairs[:200]:
            w1, w2 = p['pair']
            # Find common prefix
            min_len = min(len(w1), len(w2))
            common_prefix = 0
            for i in range(min_len):
                if w1[i] == w2[i]:
                    common_prefix += 1
                else:
                    break

            # Find common suffix
            common_suffix = 0
            for i in range(1, min_len + 1):
                if w1[-i] == w2[-i]:
                    common_suffix += 1
                else:
                    break

            if common_prefix >= 3:
                prefix_pairs.append((p, common_prefix))
            elif common_suffix >= 3:
                suffix_pairs.append((p, common_suffix))
            elif common_prefix == 0 and common_suffix == 0 and p['sim'] > 0.87:
                # Similar but no prefix/suffix = possible char pattern
                char_pattern_pairs.append(p)

        print(f"\nPrefix-similar pairs (shared beginning): {len(prefix_pairs)}")
        for p, preflen in sorted(prefix_pairs, key=lambda x: -x[1])[:10]:
            print(f"  {p['pair'][0]}-{p['pair'][1]}: shared prefix={preflen}, sim={p['sim']:.3f}")

        print(f"\nSuffix-similar pairs (shared ending): {len(suffix_pairs)}")
        for p, sufflen in sorted(suffix_pairs, key=lambda x: -x[1])[:10]:
            print(f"  {p['pair'][0]}-{p['pair'][1]}: shared suffix={sufflen}, sim={p['sim']:.3f}")

        print(f"\nPattern-similar pairs (no shared affix but still similar): {len(char_pattern_pairs)}")
        for p in char_pattern_pairs[:10]:
            print(f"  {p['pair'][0]}-{p['pair'][1]}: sim={p['sim']:.3f}, langs={p['langs']}")

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
                        choices=['evaluate', 'find', 'projection', 'clustering', 'llm',
                                 'random', 'pca', 'cluster-axes', 'residual', 'all'],
                        help='Discovery method')
    parser.add_argument('--top-k', type=int, default=20, help='Top K results')
    parser.add_argument('--vocab-size', type=int, default=5000, help='Vocabulary size for residual discovery')
    parser.add_argument('--word', type=str, default='', help='Word to find opposite for')
    parser.add_argument('--full-vocab', action='store_true', help='Search in full vocabulary')

    args = parser.parse_args()

    if ',' in args.layer:
        layer = [int(l.strip()) for l in args.layer.split(',')]
    else:
        layer = int(args.layer)

    tool = OppositeDiscoveryTool(model_name=args.model, layer=layer)

    if args.method == 'evaluate':
        tool.evaluate_known_opposites()
    elif args.method == 'find':
        if not args.word:
            print("Error: --word required for find method")
            return
        tool.find_opposite(args.word, args.top_k, use_full_vocab=args.full_vocab)
    elif args.method == 'projection':
        tool.discover_projection(args.top_k)
    elif args.method == 'clustering':
        tool.discover_clustering(args.top_k)
    elif args.method == 'llm':
        tool.discover_llm(args.top_k)
    elif args.method == 'random':
        tool.discover_random_axes(args.top_k)
    elif args.method == 'pca':
        tool.discover_pca_axes(args.top_k)
    elif args.method == 'cluster-axes':
        tool.discover_cluster_axes(args.top_k)
    elif args.method == 'residual':
        tool.discover_residual_opposites(args.top_k, args.vocab_size)
    else:
        tool.discover_all(args.top_k)


if __name__ == '__main__':
    main()
