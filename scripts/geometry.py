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
    # Chinese
    "value (zh): good-bad":
        concept_axis("好", "坏"),

    "morality (zh): good-evil":
        concept_axis("善", "恶"),

    "cooperation (zh): cooperation-conflict":
        concept_axis("合作", "冲突"),

    "truth (zh): correct-error":
        concept_axis("正确", "错误"),

    "truth-alt (zh): right-wrong":
        concept_axis("对", "错"),

    "existence (zh): yes-no":
        concept_axis("是", "否"),

    "efficiency (zh): efficient-inefficient":
        concept_axis("高效", "低效"),

    # English
    "value (en): good-bad":
        concept_axis("good", "bad"),

    "morality (en): good-evil":
        concept_axis("good", "evil"),

    "cooperation (en): cooperation-conflict":
        concept_axis("cooperation", "conflict"),

    "truth (en): correct-error":
        concept_axis("correct", "error"),

    "truth-alt (en): right-wrong":
        concept_axis("right", "wrong"),

    "existence (en): yes-no":
        concept_axis("yes", "no"),

    "efficiency (en): efficient-inefficient":
        concept_axis("efficient", "inefficient"),
}



# =========================
# Compare Concept Directions
# =========================

pairs = [
    # Within Chinese
    ("value (zh): good-bad", "cooperation (zh): cooperation-conflict"),
    ("value (zh): good-bad", "morality (zh): good-evil"),
    ("value (zh): good-bad", "truth (zh): correct-error"),
    ("value (zh): good-bad", "truth-alt (zh): right-wrong"),
    ("value (zh): good-bad", "existence (zh): yes-no"),
    ("value (zh): good-bad", "efficiency (zh): efficient-inefficient"),

    # Within English
    ("value (en): good-bad", "cooperation (en): cooperation-conflict"),
    ("value (en): good-bad", "morality (en): good-evil"),
    ("value (en): good-bad", "truth (en): correct-error"),
    ("value (en): good-bad", "truth-alt (en): right-wrong"),
    ("value (en): good-bad", "existence (en): yes-no"),
    ("value (en): good-bad", "efficiency (en): efficient-inefficient"),

    # Cross-language
    ("value (zh): good-bad", "value (en): good-bad"),
    ("morality (zh): good-evil", "morality (en): good-evil"),
    ("cooperation (zh): cooperation-conflict", "cooperation (en): cooperation-conflict"),
    ("truth (zh): correct-error", "truth (en): correct-error"),
    ("truth-alt (zh): right-wrong", "truth-alt (en): right-wrong"),
    ("existence (zh): yes-no", "existence (en): yes-no"),
    ("efficiency (zh): efficient-inefficient", "efficiency (en): efficient-inefficient"),
]

print(f"\n=== Concept direction similarity ===")
print(f"Model: {MODEL}, Rotation: {ROTATION_METHOD}")
if ROTATION_METHOD == "pca-align":
    print(f"Top-K components: {TOP_K}")

for a, b in pairs:
    sim = cosine(axes[a], axes[b])
    print(f"{a} <-> {b}: {sim:.4f}")

# =========================
# Similarity Matrix
# =========================

print(f"\n=== Similarity Matrix ===")

# Core concepts for columns and rows (Chinese)
col_concepts_zh = ["是", "否", "对", "错", "好", "坏", "善", "恶", "美", "丑", "正", "邪"]

# English equivalents for comparison
col_concepts_en = ["yes", "no", "right", "wrong", "good", "bad", "good", "evil", "beautiful", "ugly", "righteous", "evil"]

# All concepts for rows - expanded with law-related vocabulary
row_concepts = col_concepts_zh + [
    # 第零定律：存在即信息
    "存在", "信息", "实在", "虚拟", "真实", "虚假", "虚无",
    "物质", "意识", "符号", "编码", "数据", "信号",

    # 第一定律：完备即正确
    "完备", "正确", "错误", "确定", "不确定", "边界", "不完备",
    "有限", "无限", "客观", "主观", "真理", "谬误",

    # 第二定律：不完备终将湮灭
    "本能", "动机", "欲望", "需求", "目标", "趋势",
    "进化", "退化", "生存", "消亡", "竞争", "适应",

    # 第三定律：自由即无知
    "自由", "奴役", "放任", "秩序", "无知", "知识",
    "约束", "解放", "混乱", "熵",

    # 第四定律：正义即效率
    "正义", "效率", "公平", "不公", "道德", "法律",
    "投资", "消费", "成本", "收益", "财富", "贫穷", "低效",

    # 第五定律：意义即利益
    "意义", "利益", "价值", "目的", "幸福", "痛苦",
    "快乐", "悲伤", "满意", "失望", "成就", "失败", "无意义", "损失",

    # 额外核心概念
    "合作", "冲突", "信任", "欺骗",
    "帮助", "伤害", "创造", "破坏",
    "力量", "危机", "本质", "特征"
]

concept_vectors = {c: get_vector(c) for c in row_concepts}

# Chinese matrix
print("\nChinese concept similarity matrix (rows: all concepts, cols: core concepts):")
print("      ", end="")
for c in col_concepts_zh:
    print(f"{c:6s}", end=" ")
print()
for a in row_concepts:
    print(f"{a:4s} ", end="")
    for b in col_concepts_zh:
        sim = cosine(concept_vectors[a], concept_vectors[b])
        print(f"{sim:6.2f}", end=" ")
    print()

# English matrix
print("\nEnglish concept similarity matrix:")
en_concepts = ["yes", "no", "right", "wrong", "good", "bad", "good", "evil", "beautiful", "ugly", "righteous", "wicked"]
concept_vectors_en = {c: get_vector(c) for c in en_concepts}

# Add English row concepts
row_concepts_en = en_concepts + [
    "cooperation", "conflict", "trust", "deceive",
    "help", "harm", "create", "destroy",
    "efficiency", "correct", "error", "power", "wealth",
    "justice", "freedom", "order", "investment", "consumption"
]
for c in row_concepts_en:
    if c not in concept_vectors_en:
        concept_vectors_en[c] = get_vector(c)

print("      ", end="")
for c in en_concepts:
    print(f"{c:10s}", end=" ")
print()
for a in row_concepts_en:
    print(f"{a:10s} ", end="")
    for b in en_concepts:
        sim = cosine(concept_vectors_en[a], concept_vectors_en[b])
        print(f"{sim:10.2f}", end=" ")
    print()

# =========================
# Similarity + Opposition Analysis
# =========================

print(f"\n=== Similarity & Opposition Analysis ===")
print("Comparing each concept with its expected opposite")
print()

opposite_pairs = [
    ("是", "否"),
    ("对", "错"),
    ("好", "坏"),
    ("善", "恶"),
    ("合作", "冲突"),
    ("信任", "欺骗"),
    ("帮助", "伤害"),
    ("创造", "破坏"),
    ("自由", "奴役"),
    ("秩序", "放任"),
    ("正义", "危机"),
    ("投资", "消费"),
    ("正确", "错误"),
    ("客观", "主观"),
    ("存在", "危机"),
    ("美", "丑"),
    ("正", "邪"),
]

print(f"{'Concept 1':8s} {'Concept 2':8s} {'Sim':>6s} {'Opp':>6s} {'Angle':>7s} {'Opp?':>6s}")
print("-" * 50)
for pos, neg in opposite_pairs:
    if pos in concept_vectors and neg in concept_vectors:
        sim = cosine(concept_vectors[pos], concept_vectors[neg])
        opposition = 1 - sim
        angle = np.arccos(np.clip(sim, -1, 1)) * 180 / np.pi
        is_opposite = "Yes" if sim < 0.5 else "No"
        print(f"{pos:8s} {neg:8s} {sim:6.2f} {opposition:6.2f} {angle:7.1f}° {is_opposite:>6s}")
    else:
        print(f"{pos:8s} {neg:8s} {'N/A':>6s} {'N/A':>6s} {'N/A':>7s} {'N/A':>6s}")

# =========================
# Axis Projection Separation
# =========================

print(f"\n=== Axis Projection Separation ===")
print("Measuring opposite pairs on their own concept axis")
print()

print(f"{'Pair':12s} {'Pos-proj':>10s} {'Neg-proj':>10s} {'Separation':>12s}")
print("-" * 50)

for pos, neg in opposite_pairs[:8]:  # Top 8 pairs
    if pos in concept_vectors and neg in concept_vectors:
        # Create axis from the pair
        axis = concept_vectors[pos] - concept_vectors[neg]

        # Project both words onto their own axis
        proj_pos = cosine(concept_vectors[pos], axis)
        proj_neg = cosine(concept_vectors[neg], axis)
        separation = proj_pos - proj_neg

        print(f"{pos}-{neg:12s} {proj_pos:10.4f} {proj_neg:10.4f} {separation:12.4f}")

# =========================
# Law Verification Analysis
# =========================

print(f"\n{'='*60}")
print("LAW VERIFICATION ANALYSIS")
print(f"{'='*60}")

# Law-specific vocabulary pairs for verification
law_concepts = {
    "第零定律-存在即信息": [
        ("存在", "信息"),
        ("实在", "真实"),
        ("物质", "意识"),
        ("符号", "编码"),
        ("信号", "数据"),
    ],
    "第一定律-完备即正确": [
        ("完备", "正确"),
        ("确定", "客观"),
        ("真理", "正确"),
        ("边界", "有限"),
    ],
    "第二定律-不完备湮灭": [
        ("动机", "目标"),
        ("欲望", "需求"),
        ("生存", "适应"),
        ("竞争", "进化"),
    ],
    "第三定律-自由即无知": [
        ("自由", "无知"),
        ("约束", "知识"),
        ("放任", "混乱"),
        ("秩序", "确定"),
    ],
    "第四定律-正义即效率": [
        ("正义", "效率"),
        ("公平", "效率"),
        ("投资", "收益"),
        ("成本", "效率"),
    ],
    "第五定律-意义即利益": [
        ("意义", "利益"),
        ("价值", "利益"),
        ("幸福", "利益"),
        ("目的", "目标"),
    ],
}

print("\nLaw-specific concept pair similarities:")
for law_name, pairs in law_concepts.items():
    print(f"\n{law_name}:")
    for pos, neg in pairs:
        if pos in concept_vectors and neg in concept_vectors:
            sim = cosine(concept_vectors[pos], concept_vectors[neg])
            print(f"  {pos:8s} - {neg:8s}: {sim:.4f}")

# Opposition pairs for each law
print(f"\n{'='*60}")
print("LAW OPPOSITION ANALYSIS")
print(f"{'='*60}")

law_opposites = {
    "第零定律": [("真实", "虚假"), ("物质", "意识"), ("存在", "虚无")],
    "第一定律": [("完备", "不完备"), ("正确", "错误"), ("确定", "不确定")],
    "第二定律": [("生存", "消亡"), ("进化", "退化"), ("竞争", "合作")],
    "第三定律": [("自由", "奴役"), ("无知", "知识"), ("秩序", "混乱")],
    "第四定律": [("正义", "不公"), ("效率", "低效"), ("投资", "消费")],
    "第五定律": [("意义", "无意义"), ("利益", "损失"), ("幸福", "痛苦")],
}

for law_name, pairs in law_opposites.items():
    print(f"\n{law_name}:")
    print(f"  {'Pair':<15s} {'Sim':>6s} {'Opp':>6s} {'Angle':>7s}")
    print(f"  {'-'*40}")
    for pos, neg in pairs:
        vec_pos = concept_vectors.get(pos)
        vec_neg = concept_vectors.get(neg)
        if vec_pos is not None and vec_neg is not None:
            sim = cosine(vec_pos, vec_neg)
            opp = 1 - sim
            angle = np.arccos(np.clip(sim, -1, 1)) * 180 / np.pi
            print(f"  {pos:8s}-{neg:8s} {sim:6.2f} {opp:6.2f} {angle:7.1f}°")
        else:
            print(f"  {pos:8s}-{neg:8s} {'N/A':>6s} {'N/A':>6s} {'N/A':>7s}")



# =========================
# Project Words onto GOOD Axis
# =========================

good_axis_zh = axes["value (zh): good-bad"]
good_axis_en = axes["value (en): good-bad"]

words_zh = [
    "合作", "信任", "帮助", "创造", "善良", "效率", "财富", "力量",
    "欺骗", "破坏", "冲突", "伤害", "战争"
]

words_en = [
    "cooperation", "trust", "help", "create", "kind", "efficiency", "wealth", "power",
    "deceive", "destroy", "conflict", "harm", "war"
]

print(f"\n=== Projection on GOOD axis (Chinese) ===")
for w in words_zh:
    v = get_vector(w)
    score_zh = cosine(v, good_axis_zh)
    score_en = cosine(v, good_axis_en)
    print(f"{w:6s}: zh-axis={score_zh:.4f}, en-axis={score_en:.4f}")

print(f"\n=== Projection on GOOD axis (English) ===")
for w in words_en:
    v = get_vector(w)
    score_zh = cosine(v, good_axis_zh)
    score_en = cosine(v, good_axis_en)
    print(f"{w:12s}: zh-axis={score_zh:.4f}, en-axis={score_en:.4f}")
