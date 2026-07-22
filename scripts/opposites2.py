#!/usr/bin/env python
"""
Opposite Word Discovery Tool v2.0

Fixed configuration: InfoXLM-large model, layer 0.
Simplified interface for finding synonyms and antonyms.

Usage:
    python opposites2.py find 荒野
    python opposites2.py evaluate
    python opposites2.py discover --top-k 20
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

# ============================================================================
# Fixed Configuration
# ============================================================================

SCRIPT_DIR = Path(__file__).parent
MODEL_PATH = r"C:\Users\hans\Desktop\models\infoxlm-large"  # Fixed local model path
LAYER = -1  # Use last layer (better for semantic opposition)
TEMPLATE = None  # No template (better results without it)

# ============================================================================
# Core Classes
# ============================================================================

class SemanticAxisLearner:
    """Learn semantic axes from opposite word pairs."""

    def __init__(self, opposite_pairs, model, tokenizer, device, weights=None):
        self.opposite_pairs = opposite_pairs
        self.weights = weights  # Optional weights per pair
        self.model = model
        self.tokenizer = tokenizer
        self.device = device
        self.axes = None
        self.mean_vec = None

        # For layer 0, use embedding layer directly (much faster)
        self.embedding_layer = self.model.embeddings.word_embeddings

        # Extract vectors for all words
        self.vectors = {}
        for w1, w2 in opposite_pairs:
            for w in [w1, w2]:
                if w not in self.vectors:
                    v = self._get_vector_fast(w)
                    if v is not None:
                        self.vectors[w] = v

        print(f"Loaded {len(self.vectors)} word vectors")

    def _get_vector_fast(self, word):
        """Extract vector from model with template context."""
        text = TEMPLATE.format(word) if TEMPLATE else word
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)

        if hasattr(outputs, 'hidden_states'):
            h = outputs.hidden_states[LAYER]
        else:
            h = outputs.last_hidden_state

        mask = inputs["attention_mask"].unsqueeze(-1)
        vec = (h * mask).sum(dim=1) / mask.sum(dim=1)
        return vec[0]

    def _get_vectors_batch(self, words, batch_size=512):
        """Extract vectors for multiple words in batches."""
        vectors = {}
        for i in range(0, len(words), batch_size):
            batch_words = words[i:i+batch_size]

            # Apply template
            if TEMPLATE:
                batch_texts = [TEMPLATE.format(w) for w in batch_words]
            else:
                batch_texts = batch_words

            # Tokenize batch
            inputs = self.tokenizer(
                batch_texts,
                return_tensors="pt",
                padding=True,
                truncation=True
            ).to(self.device)

            # Get hidden states
            with torch.no_grad():
                outputs = self.model(**inputs)

            if hasattr(outputs, 'hidden_states'):
                h = outputs.hidden_states[LAYER]
            else:
                h = outputs.last_hidden_state

            # Average over tokens
            mask = inputs["attention_mask"].unsqueeze(-1)
            batch_vecs = (h * mask).sum(dim=1) / mask.sum(dim=1)

            # Store results
            for j, word in enumerate(batch_words):
                vectors[word] = batch_vecs[j]

        return vectors

    def _get_vector(self, word):
        """Extract vector for a word (backward compatible)."""
        return self._get_vector_fast(word)

    def learn_axes(self, variance_ratio=0.95):
        """Learn semantic axes from opposite pairs with optional weights."""
        # Compute mean vector
        self.mean_vec = torch.stack(list(self.vectors.values())).mean(dim=0)

        # Compute weighted axis directions
        directions = []
        weights_list = []
        for i, (w1, w2) in enumerate(self.opposite_pairs):
            if w1 in self.vectors and w2 in self.vectors:
                axis_dir = (self.vectors[w1] - self.vectors[w2]) - self.mean_vec
                axis_dir = axis_dir / (axis_dir.norm() + 1e-8)
                directions.append(axis_dir)
                # Get weight for this pair
                w = self.weights[i] if self.weights and i < len(self.weights) else 1.0
                weights_list.append(w)

        if not directions:
            return

        directions = torch.stack(directions)
        weights_tensor = torch.tensor(weights_list, dtype=torch.float32)

        # Weighted PCA: compute weighted covariance and apply PCA
        # This preserves orthogonality of principal components
        from sklearn.decomposition import PCA

        # Weight each direction by sqrt(weight) for weighted PCA
        sqrt_weights = torch.sqrt(weights_tensor)
        weighted_directions = (directions.cpu() * sqrt_weights.unsqueeze(1)).numpy()

        # Apply PCA to weighted directions
        pca = PCA(n_components=min(len(weighted_directions), weighted_directions.shape[1]))
        pca.fit(weighted_directions)

        # Select axes by cumulative variance
        cumsum = np.cumsum(pca.explained_variance_ratio_)
        n_axes = np.searchsorted(cumsum, variance_ratio).item() + 1
        n_axes = max(1, min(n_axes, len(pca.components_)))

        self.axes = torch.from_numpy(pca.components_[:n_axes]).float().to(self.device)
        print(f"Learned {n_axes} semantic axes (cumulative variance: {cumsum[n_axes-1]:.1%})")

        return self.axes

    def get_separation(self, word1, word2):
        """Get semantic separation between two words."""
        v1 = self._get_vector(word1)
        v2 = self._get_vector(word2)

        if v1 is None or v2 is None or self.axes is None:
            return None

        v1_centered = v1 - self.mean_vec
        v2_centered = v2 - self.mean_vec

        proj1 = self.axes @ v1_centered
        proj2 = self.axes @ v2_centered

        separation = (proj1 - proj2).abs().max().item()
        return separation


class OppositeFinder:
    """Find synonyms and antonyms using semantic axes."""

    def __init__(self):
        print(f"Loading model from: {MODEL_PATH}...")
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(
            MODEL_PATH,
            output_hidden_states=True,
            trust_remote_code=True
        )
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        self.model.eval()

        # Cache embedding layer for fast access
        self.embedding_layer = self.model.embeddings.word_embeddings

        # Load known opposites
        self.opposite_pairs, self.weights = self._load_opposites()
        print(f"Loaded {len(self.opposite_pairs)} opposite pairs")

        # Learn semantic axes
        self.learner = SemanticAxisLearner(
            self.opposite_pairs, self.model, self.tokenizer, self.device,
            weights=self.weights
        )
        self.learner.learn_axes()

    def _load_opposites(self):
        """Load opposite pairs and weights from config."""
        path = SCRIPT_DIR / "configs" / "opposites.yaml"
        if not path.exists():
            return [], None

        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        pairs = []
        weights = []
        for pair in config.get('opposite_pairs', []):
            if isinstance(pair, (list, tuple)):
                if len(pair) == 2:
                    pairs.append(tuple(pair))
                    weights.append(1.0)  # Default weight
                elif len(pair) >= 3:
                    pairs.append((pair[0], pair[1]))
                    weights.append(float(pair[2]))  # Custom weight
        return pairs, weights

    def _get_vector(self, word):
        """Extract embedding vector (layer 0 optimization)."""
        inputs = self.tokenizer(word, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self.device)

        with torch.no_grad():
            vec = self.embedding_layer(input_ids)

        mask = inputs["attention_mask"].unsqueeze(-1).to(self.device)
        vec = (vec * mask).sum(dim=1) / mask.sum(dim=1)
        return vec[0]

    def find(self, word, top_k=20, use_full_vocab=False):
        """Find synonyms and antonyms for a word."""
        print(f"\n{'='*70}")
        print(f"Finding synonyms and antonyms for: {word}")
        print(f"{'='*70}")

        vec = self._get_vector(word)
        if vec is None:
            print(f"Word '{word}' not in vocabulary")
            return

        # Get vocabulary
        if use_full_vocab:
            print("Searching in full vocabulary...")
            all_tokens = list(self.tokenizer.get_vocab().keys())
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
            vocab = list(self.learner.vectors.keys())

        # Batch extract vectors
        print(f"Extracting embeddings in batches...")
        vocab_to_search = [w for w in vocab if w != word]
        batch_vectors = self.learner._get_vectors_batch(vocab_to_search)

        # Compute metrics
        print(f"Computing similarities...")
        results = []
        for vocab_word, v in batch_vectors.items():
            cosine = F.cosine_similarity(vec.unsqueeze(0), v.unsqueeze(0)).item()
            separation = self.learner.get_separation(word, vocab_word)

            results.append({
                'word': vocab_word,
                'cosine': cosine,
                'separation': separation if separation else 0,
            })

        # Sort by separation for antonyms
        by_separation = sorted(results, key=lambda x: -x['separation'])

        print(f"\n--- Antonyms ---")
        print(f"Top {top_k} (high separation = opposite on semantic axis):")
        for i, r in enumerate(by_separation[:top_k]):
            mark = ""
            for w1, w2 in self.opposite_pairs:
                if (r['word'] == w1 and word == w2) or (r['word'] == w2 and word == w1):
                    mark = " ✓ KNOWN"
                    break
            print(f"  {i+1}. {word}-{r['word']}: sep={r['separation']:.3f}, cos={r['cosine']:.3f}{mark}")

        # Sort by cosine for synonyms
        by_cosine = sorted(results, key=lambda x: -x['cosine'])

        print(f"\n--- Synonyms ---")
        print(f"Top {top_k} (high cosine = similar meaning):")
        for i, r in enumerate(by_cosine[:top_k]):
            print(f"  {i+1}. {word}-{r['word']}: cos={r['cosine']:.3f}, sep={r['separation']:.3f}")

    def evaluate(self):
        """Evaluate quality of known opposite pairs."""
        print(f"\n{'='*70}")
        print("Evaluating known opposite pairs")
        print(f"{'='*70}")

        # Compute separation for each pair
        results = []
        for w1, w2 in self.opposite_pairs:
            sep = self.learner.get_separation(w1, w2)
            if sep is not None:
                v1 = self._get_vector(w1)
                v2 = self._get_vector(w2)
                cos = F.cosine_similarity(v1.unsqueeze(0), v2.unsqueeze(0)).item()
                results.append({
                    'pair': (w1, w2),
                    'separation': sep,
                    'cosine': cos,
                })

        # Sort by separation
        results.sort(key=lambda x: -x['separation'])

        print(f"\nStrong pairs (high separation):")
        for r in results[:10]:
            print(f"  {r['pair'][0]}-{r['pair'][1]}: sep={r['separation']:.3f}, cos={r['cosine']:.3f}")

        print(f"\nWeak pairs (low separation):")
        for r in results[-10:]:
            print(f"  {r['pair'][0]}-{r['pair'][1]}: sep={r['separation']:.3f}, cos={r['cosine']:.3f}")

        # Statistics
        separations = [r['separation'] for r in results]
        cosines = [r['cosine'] for r in results]

        print(f"\nStatistics:")
        print(f"  Separation: mean={np.mean(separations):.3f}, std={np.std(separations):.3f}")
        print(f"  Cosine: mean={np.mean(cosines):.3f}, std={np.std(cosines):.3f}")

        strong = sum(1 for s in separations if s > 1.0)
        medium = sum(1 for s in separations if 0.5 <= s <= 1.0)
        weak = sum(1 for s in separations if s < 0.5)

        print(f"\n  Strong (sep > 1.0): {strong} ({100*strong/len(separations):.1f}%)")
        print(f"  Medium (0.5-1.0): {medium} ({100*medium/len(separations):.1f}%)")
        print(f"  Weak (< 0.5): {weak} ({100*weak/len(separations):.1f}%)")

    def discover(self, top_k=20):
        """Discover new opposite pairs."""
        print(f"\n{'='*70}")
        print("Discovering new opposite pairs")
        print(f"{'='*70}")

        # Get all vocabulary words
        vocab = list(self.learner.vectors.keys())
        print(f"Vocabulary size: {len(vocab)}")

        # Find all pairs
        pairs = []
        for i, w1 in enumerate(vocab):
            for w2 in vocab[i+1:]:
                sep = self.learner.get_separation(w1, w2)
                if sep and sep > 1.5:  # High separation threshold
                    v1 = self._get_vector(w1)
                    v2 = self._get_vector(w2)
                    cos = F.cosine_similarity(v1.unsqueeze(0), v2.unsqueeze(0)).item()
                    pairs.append({
                        'pair': (w1, w2),
                        'separation': sep,
                        'cosine': cos,
                    })

        # Sort by separation
        pairs.sort(key=lambda x: -x['separation'])

        print(f"\nDiscovered {len(pairs)} candidate pairs (sep > 1.5)")
        print(f"\nTop {top_k} candidates:")
        for i, r in enumerate(pairs[:top_k]):
            # Check if known
            mark = ""
            for w1, w2 in self.opposite_pairs:
                if (r['pair'][0] in [w1, w2] and r['pair'][1] in [w1, w2]):
                    mark = " ✓ KNOWN"
                    break
            print(f"  {i+1}. {r['pair'][0]}-{r['pair'][1]}: sep={r['separation']:.3f}, cos={r['cosine']:.3f}{mark}")


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Opposite Word Discovery Tool v2.0')
    parser.add_argument('command', choices=['find', 'evaluate', 'discover'],
                        help='Command to execute')
    parser.add_argument('word', nargs='?', default='', help='Word to analyze (for find command)')
    parser.add_argument('--top-k', type=int, default=20, help='Top K results')
    parser.add_argument('--full-vocab', action='store_true', help='Search in full vocabulary')

    args = parser.parse_args()

    finder = OppositeFinder()

    if args.command == 'find':
        if not args.word:
            print("Error: word argument required for find command")
            return
        finder.find(args.word, args.top_k, args.full_vocab)
    elif args.command == 'evaluate':
        finder.evaluate()
    elif args.command == 'discover':
        finder.discover(args.top_k)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
