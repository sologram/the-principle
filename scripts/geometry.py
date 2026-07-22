#!/usr/bin/env python
"""
Concept Geometry Analysis Tool v2.3

Semantic space analysis for verifying the six laws of Principle of Things.

Usage:
    python geometry.py --task all
    python geometry.py --task law --law law1
    python geometry.py --task axis
    python geometry.py --task opposites

Config:
    configs/law*.yaml - Law configurations with semantic axes and thresholds
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
    """Load all law configs and merge semantic axes and thresholds."""
    laws = {}
    laws_dir = SCRIPT_DIR / "configs"
    if not laws_dir.exists():
        return laws

    for path in sorted(laws_dir.glob("law*.yaml")):
        with open(path, 'r', encoding='utf-8') as f:
            law = yaml.safe_load(f)
            laws[path.stem] = law

    return laws


def merge_semantic_axes(laws_config):
    """Merge semantic axes from all laws (deduplicate)."""
    merged = {}
    for law in laws_config.values():
        for ax_name, ax_config in law.get('semantic_axes', {}).items():
            if ax_name not in merged:
                merged[ax_name] = ax_config
    return merged


def merge_thresholds(laws_config):
    """Merge thresholds from all laws (use first)."""
    for law in laws_config.values():
        if 'thresholds' in law:
            return law['thresholds']
    return {
        'positive_similarity': 0.5,
        'opposite_semantic': -0.3,
        'axis_separation_good': 1.0,
        'axis_separation_fair': 0.5,
        'law_verified': 75,
        'law_partial': 50
    }


def get_vocabulary(laws_config):
    """Extract all vocabulary words."""
    vocab = set()
    for law in laws_config.values():
        for pair in law.get('positive_pairs', []):
            vocab.update(pair)
        for pair in law.get('opposite_pairs', []):
            vocab.update(pair)
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

        # 多层融合：如果 layer 是列表，融合多层
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


class ConceptAxis:
    """Concept axis defined by positive and negative poles."""

    def __init__(self, name, pos_words, neg_words, extractor, layer=-1):
        self.name = name
        self.pos_words = pos_words if isinstance(pos_words, list) else [pos_words]
        self.neg_words = neg_words if isinstance(neg_words, list) else [neg_words]
        self.extractor = extractor
        self.layer = layer
        self._compute_axis()

    def _compute_axis(self):
        pos_vecs = [self.extractor.get_vector(w, self.layer) for w in self.pos_words]
        neg_vecs = [self.extractor.get_vector(w, self.layer) for w in self.neg_words]

        pos_vecs = [v.float() for v in pos_vecs]
        neg_vecs = [v.float() for v in neg_vecs]

        self.pos_vec = torch.stack(pos_vecs).mean(dim=0)
        self.neg_vec = torch.stack(neg_vecs).mean(dim=0)
        self.axis = self.pos_vec - self.neg_vec

    def self_separation(self):
        pos_proj = cosine_similarity(self.pos_vec, self.axis)
        neg_proj = cosine_similarity(self.neg_vec, self.axis)
        return pos_proj - neg_proj


class SemanticSpace:
    """Semantic space with orthogonal decomposition."""

    def __init__(self, semantic_axes, vocabulary, extractor, layer=-1):
        self.semantic_axes = semantic_axes
        self.vocabulary = vocabulary
        self.extractor = extractor
        self.layer = layer
        self._build_space()

    def _build_space(self):
        self.vectors = {w: self.extractor.get_vector(w, self.layer) for w in self.vocabulary}

        all_vecs = torch.stack([v.float() for v in self.vectors.values()])
        self.mean_vec = all_vecs.mean(dim=0)
        centered = all_vecs - self.mean_vec

        semantic_dirs = [ax.axis.float() for ax in self.semantic_axes]
        P = torch.stack(semantic_dirs)
        P_orth, _ = torch.linalg.qr(P.T)
        self.semantic_basis = P_orth.T

        proj_sem = centered @ self.semantic_basis.T @ self.semantic_basis
        semantic_residuals = centered - proj_sem

        n_semantic = min(50, len(self.vocabulary) - len(self.semantic_axes) - 1)
        pca = PCA(n_components=max(1, n_semantic))
        pca.fit(semantic_residuals.float().cpu().numpy())
        self.residual_basis = torch.from_numpy(pca.components_[:min(20, n_semantic)]).float().to(self.extractor.device)

    def similarity(self, w1, w2, space='original'):
        v1 = self.vectors.get(w1, self.extractor.get_vector(w1, self.layer))
        v2 = self.vectors.get(w2, self.extractor.get_vector(w2, self.layer))

        if space == 'original':
            return cosine_similarity(v1, v2)
        elif space == 'semantic':
            s1 = (v1.float() - self.mean_vec) @ self.semantic_basis.T
            s2 = (v2.float() - self.mean_vec) @ self.semantic_basis.T
            return cosine_similarity(s1, s2)
        elif space == 'syntactic':
            v1_c = v1.float() - self.mean_vec
            v2_c = v2.float() - self.mean_vec
            proj_sem = v1_c @ self.semantic_basis.T @ self.semantic_basis
            r1 = (v1_c - proj_sem) @ self.residual_basis.T
            proj_sem = v2_c @ self.semantic_basis.T @ self.semantic_basis
            r2 = (v2_c - proj_sem) @ self.residual_basis.T
            return cosine_similarity(r1, r2)


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
# Analyzer
# ============================================================================

class ConceptGeometryAnalyzer:
    """Concept geometry analyzer."""

    def __init__(self, model_name="qwen3.5-9b", layer=-1):
        self.laws_config = load_all_laws()
        self.semantic_axes_config = merge_semantic_axes(self.laws_config)
        self.thresholds = merge_thresholds(self.laws_config)
        self.layer = layer

        print(f"Loading model: {model_name}...")
        self.model, self.tokenizer, self.device = load_model(model_name)
        self.extractor = VectorExtractor(self.model, self.tokenizer, self.device)

        # Build semantic axes
        self.semantic_axes = []
        for name, ax_config in self.semantic_axes_config.items():
            self.semantic_axes.append(ConceptAxis(
                name=name,
                pos_words=ax_config['pos_words'],
                neg_words=ax_config['neg_words'],
                extractor=self.extractor,
                layer=layer
            ))

        # Build semantic space
        vocab = get_vocabulary(self.laws_config)
        self.semantic_space = SemanticSpace(self.semantic_axes, vocab, self.extractor, layer)
        print(f"Model loaded. Laws: {len(self.laws_config)}, Vocabulary: {len(vocab)}")

    def analyze_axis_quality(self):
        results = {}
        for axis in self.semantic_axes:
            sep = axis.self_separation()
            quality = "excellent" if sep > self.thresholds.get('axis_separation_good', 1.0) else \
                      "good" if sep > self.thresholds.get('axis_separation_fair', 0.5) else "poor"
            results[axis.name] = {"separation": sep, "quality": quality}
        return results

    def analyze_opposites(self):
        results = []
        for law in self.laws_config.values():
            for pair in law.get('opposite_pairs', []):
                pos, neg = pair[0], pair[1]
                sim_orig = self.semantic_space.similarity(pos, neg, 'original')
                sim_sem = self.semantic_space.similarity(pos, neg, 'semantic')
                sim_syn = self.semantic_space.similarity(pos, neg, 'syntactic')
                quality = "supported" if sim_sem < self.thresholds.get('opposite_semantic', -0.3) else \
                          "orthogonal" if abs(sim_sem) < 0.3 else "not supported"
                results.append((pos, neg, sim_orig, sim_sem, sim_syn, quality))
        return results

    def verify_law(self, law_key):
        law = self.laws_config.get(law_key)
        if not law:
            return None

        positive_results = []
        for pair in law.get('positive_pairs', []):
            w1, w2 = pair[0], pair[1]
            sim = self.semantic_space.similarity(w1, w2, 'original')
            supported = sim > self.thresholds.get('positive_similarity', 0.5)
            positive_results.append({"pair": (w1, w2), "similarity": sim, "supported": supported})

        opposite_results = []
        for pair in law.get('opposite_pairs', []):
            pos, neg = pair[0], pair[1]
            sim_sem = self.semantic_space.similarity(pos, neg, 'semantic')
            supported = sim_sem < self.thresholds.get('opposite_semantic', -0.3)
            opposite_results.append({"pair": (pos, neg), "sim_semantic": sim_sem, "supported": supported})

        pos_supported = sum(1 for r in positive_results if r["supported"])
        opp_supported = sum(1 for r in opposite_results if r["supported"])
        total = len(positive_results) + len(opposite_results)

        rate = (pos_supported + opp_supported) / total * 100 if total > 0 else 0
        status = "verified" if rate >= self.thresholds.get('law_verified', 75) else \
                 "partial" if rate >= self.thresholds.get('law_partial', 50) else "not supported"

        return {
            "key": law_key,
            "name": law['name'],
            "theory": law['theory'],
            "positive_results": positive_results,
            "opposite_results": opposite_results,
            "positive_rate": pos_supported / len(positive_results) * 100 if positive_results else 0,
            "opposite_rate": opp_supported / len(opposite_results) * 100 if opposite_results else 0,
            "total_rate": rate,
            "status": status
        }

    def print_axis_report(self):
        print("\n" + "="*60)
        print("Semantic Axis Quality Analysis")
        print("="*60)
        print(f"\n{'Axis':8s} {'Separation':>12s} {'Quality':>10s}")
        print("-" * 35)
        for name, result in self.analyze_axis_quality().items():
            print(f"{name:8s} {result['separation']:12.4f} {result['quality']:>10s}")

    def print_opposites_report(self):
        print("\n" + "="*60)
        print("Opposite Words Directionality Analysis")
        print("="*60)
        print("\nKey finding: opposite words should show negative similarity in semantic space")
        print(f"\n{'Pair':<12s} {'Original':>10s} {'Semantic':>10s} {'Syntactic':>10s} {'Quality':>12s}")
        print("-" * 60)
        for pos, neg, sim_orig, sim_sem, sim_syn, quality in self.analyze_opposites():
            print(f"{pos}-{neg:<8s} {sim_orig:10.4f} {sim_sem:10.4f} {sim_syn:10.4f} {quality:>12s}")

    def print_law_report(self, law_key):
        result = self.verify_law(law_key)
        if not result:
            return

        print("\n" + "="*60)
        print(f"{law_key}: {result['name']}")
        print("="*60)
        print(f"\nTheory: {result['theory']}")

        print("\n[Positive Pairs] Similarity Test:")
        for r in result["positive_results"]:
            w1, w2 = r["pair"]
            status = "PASS" if r["supported"] else "FAIL"
            print(f"  {w1}-{w2}: {r['similarity']:.4f} {status}")

        print("\n[Opposite Pairs] Semantic Space Test:")
        for r in result["opposite_results"]:
            pos, neg = r["pair"]
            status = "PASS" if r["supported"] else "FAIL"
            print(f"  {pos}-{neg}: semantic={r['sim_semantic']:.4f} {status}")

        print(f"\nPositive: {result['positive_rate']:.0f}%")
        print(f"Opposite: {result['opposite_rate']:.0f}%")
        print(f"Total: {result['total_rate']:.0f}% - {result['status']}")

    def print_all_laws_report(self):
        print("\n" + "="*70)
        print("All Laws Verification")
        print("="*70)

        for law_key in self.laws_config:
            self.print_law_report(law_key)

        print("\n" + "="*70)
        print("Summary")
        print("="*70)

        results = {key: self.verify_law(key) for key in self.laws_config}

        print(f"\n{'Law':<10s} {'Positive':>10s} {'Opposite':>10s} {'Total':>10s} {'Status':>12s}")
        print("-" * 55)

        verified = 0
        for law_key, result in results.items():
            print(f"{law_key:<10s} {result['positive_rate']:>9.0f}% {result['opposite_rate']:>9.0f}% {result['total_rate']:>9.0f}% {result['status']:>12s}")
            if result['total_rate'] >= self.thresholds.get('law_verified', 75):
                verified += 1

        print(f"\nTotal: {verified}/{len(self.laws_config)} laws verified")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Concept Geometry Analysis Tool v2.3')
    parser.add_argument('--model', type=str, default='infoxlm-large', help='Model to use')
    parser.add_argument('--layer', type=str, default='0',
                        help='Layer(s) to use. Single layer: 0. Multi-layer fusion: 0,1,2')
    parser.add_argument('--task', type=str, default='all',
                        choices=['axis', 'opposites', 'law', 'law1', 'law2', 'law3', 'law4', 'law5', 'all'],
                        help='Analysis task')

    args = parser.parse_args()

    # 解析层参数
    if ',' in args.layer:
        layer = [int(l.strip()) for l in args.layer.split(',')]
    else:
        layer = int(args.layer)

    analyzer = ConceptGeometryAnalyzer(model_name=args.model, layer=layer)

    if args.task == 'axis':
        analyzer.print_axis_report()
    elif args.task == 'opposites':
        analyzer.print_opposites_report()
    elif args.task == 'law':
        analyzer.print_all_laws_report()
    elif args.task.startswith('law'):
        analyzer.print_law_report(args.task)
    else:
        analyzer.print_axis_report()
        analyzer.print_opposites_report()
        analyzer.print_all_laws_report()


if __name__ == '__main__':
    main()
