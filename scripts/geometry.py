import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import argparse
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel
import numpy as np
from sklearn.decomposition import PCA


# =========================
# Command Line Arguments
# =========================

parser = argparse.ArgumentParser(description='Concept Geometry Analysis')
parser.add_argument('--model', type=str, default='qwen3.5-9b',
                    choices=['bert-base-chinese', 'infoxlm-large', 'qwen3.5-9b'],
                    help='Model to use (default: qwen3.5-9b)')
parser.add_argument('--rotation', type=str, default='none',
                    choices=['none', 'pca', 'pca-align'],
                    help='Rotation method: none, pca (rotate to PC space), pca-align (align axes to PCs)')
parser.add_argument('--top-k', type=int, default=5,
                    help='Number of top principal components for pca-align (default: 5)')
args = parser.parse_args()

MODEL = args.model
ROTATION_METHOD = args.rotation
TOP_K = args.top_k
MODEL_PATH = r"C:\Users\hans\Desktop\models"

# Local model mapping
LOCAL_MODELS = {
    "infoxlm-large": f"{MODEL_PATH}\\infoxlm-large",
    "qwen3.5-9b": f"{MODEL_PATH}\\qwen3.5-9b",
}


device = "cuda" if torch.cuda.is_available() else "cpu"


# Load model from local path or Hugging Face
if MODEL in LOCAL_MODELS:
    model_path = LOCAL_MODELS[MODEL]
else:
    model_path = MODEL

print(f"Loading model: {MODEL}...")
tokenizer = AutoTokenizer.from_pretrained(
    model_path,
    trust_remote_code=True
)

model = AutoModel.from_pretrained(
    model_path,
    output_hidden_states=True,
    trust_remote_code=True
).to(device)

model.eval()

# Ensure hidden states are returned
if hasattr(model, 'config'):
    model.config.output_hidden_states = True


# =========================
# Vector Extraction
# =========================

def get_vector_raw(text):
    """
    Get raw vector without rotation.
    """
    inputs = tokenizer(
        text,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)

    if hasattr(outputs, 'hidden_states') and outputs.hidden_states is not None:
        h = outputs.hidden_states[-1]
    else:
        h = outputs.last_hidden_state

    mask = inputs["attention_mask"]
    mask = mask.unsqueeze(-1)
    vec = (h * mask).sum(dim=1) / mask.sum(dim=1)

    return vec[0]


# =========================
# PCA Rotation Methods
# =========================

_pca_rotation = None
_pca_components = None


def init_pca(word_list):
    """
    Initialize PCA for rotation methods.
    """
    global _pca_rotation, _pca_components

    print(f"Initializing PCA on {len(word_list)} words...")
    vectors = torch.stack([get_vector_raw(w) for w in word_list])
    n_components = min(vectors.shape[0], vectors.shape[1])
    _pca_rotation = PCA(n_components=n_components)
    _pca_rotation.fit(vectors.float().cpu().numpy())
    _pca_components = torch.from_numpy(_pca_rotation.components_[:TOP_K]).float().to(device)
    print(f"PCA initialized with {n_components} components")


def get_vector(text):
    """
    Get vector with optional rotation.
    """
    global _pca_rotation, _pca_components

    vec = get_vector_raw(text)

    if ROTATION_METHOD == "none":
        return vec

    if _pca_rotation is None:
        init_words = [
            "好", "坏", "善", "恶", "合作", "冲突",
            "正确", "错误", "高效", "低效",
            "信任", "帮助", "创造", "善良", "效率", "财富", "力量",
            "欺骗", "破坏", "伤害", "战争"
        ]
        init_pca(init_words)

    if ROTATION_METHOD == "pca":
        # Rotate vector to PCA space
        vec_np = vec.float().cpu().numpy().reshape(1, -1)
        vec_rotated = _pca_rotation.transform(vec_np)
        return torch.from_numpy(vec_rotated[0]).float().to(device)

    return vec


def align_axis_to_pcs(axis):
    """
    Align a concept axis to top principal components.
    """
    # Project axis onto principal directions
    axis_float = axis.float()
    projection = torch.mm(axis_float.unsqueeze(0), _pca_components.T).squeeze()
    # Reconstruct in original space
    aligned = torch.mm(projection.unsqueeze(0), _pca_components).squeeze()
    return aligned



# =========================
# Concept Axis
# =========================

def concept_axis(pos, neg):
    p = get_vector(pos)
    n = get_vector(neg)

    axis = p - n

    if ROTATION_METHOD == "pca-align":
        # Align axis to principal components
        if _pca_rotation is None:
            init_words = [
                "好", "坏", "善", "恶", "合作", "冲突",
                "正确", "错误", "高效", "低效",
                "信任", "帮助", "创造", "善良", "效率", "财富", "力量",
                "欺骗", "破坏", "伤害", "战争"
            ]
            init_pca(init_words)
        axis = align_axis_to_pcs(axis)

    return axis



# =========================
# Cosine Similarity
# =========================

def cosine(a, b):
    return F.cosine_similarity(
        a.unsqueeze(0),
        b.unsqueeze(0)
    ).item()



# =========================
# Construct Concept Axes
# =========================

print(f"\nConstructing concept axes (rotation: {ROTATION_METHOD})...")

axes = {
    "value: good-bad":
        concept_axis("好", "坏"),

    "morality: good-evil":
        concept_axis("善", "恶"),

    "cooperation: cooperation-conflict":
        concept_axis("合作", "冲突"),

    "truth: correct-error":
        concept_axis("正确", "错误"),

    "truth-alt: right-wrong":
        concept_axis("对", "错"),

    "existence: yes-no":
        concept_axis("是", "否"),

    "efficiency: efficient-inefficient":
        concept_axis("高效", "低效")
}



# =========================
# Compare Concept Directions
# =========================

pairs = [
    ("value: good-bad", "cooperation: cooperation-conflict"),
    ("value: good-bad", "morality: good-evil"),
    ("value: good-bad", "truth: correct-error"),
    ("value: good-bad", "truth-alt: right-wrong"),
    ("value: good-bad", "existence: yes-no"),
    ("value: good-bad", "efficiency: efficient-inefficient"),
    ("truth: correct-error", "truth-alt: right-wrong"),
    ("truth: correct-error", "existence: yes-no"),
    ("truth-alt: right-wrong", "existence: yes-no"),
]

print(f"\n=== Concept direction similarity ===")
print(f"Model: {MODEL}, Rotation: {ROTATION_METHOD}")
if ROTATION_METHOD == "pca-align":
    print(f"Top-K components: {TOP_K}")

for a, b in pairs:
    sim = cosine(axes[a], axes[b])
    print(f"{a} <-> {b}: {sim:.4f}")



# =========================
# Project Words onto GOOD Axis
# =========================

good_axis = axes["value: good-bad"]

words = [
    "合作", "信任", "帮助", "创造", "善良", "效率", "财富", "力量",
    "欺骗", "破坏", "冲突", "伤害", "战争"
]

print(f"\n=== Projection on GOOD axis ===")

for w in words:
    v = get_vector(w)
    score = cosine(v, good_axis)
    print(f"{w:6s}: {score:.4f}")
