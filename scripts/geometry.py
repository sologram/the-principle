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
    "力量", "危机", "本质", "特征",

    # 多词对扩展：价值轴
    "好", "坏", "优秀", "差", "成功", "失败",
    "有益", "有害", "正面", "负面", "优秀", "低劣",
    "正确", "错误", "好", "不好", "良", "不良",

    # 多词对扩展：真值轴
    "对", "错", "正确", "错误", "真实", "虚假",
    "是", "否", "确定", "不确定", "真", "假",
    "准确", "不准确", "成立", "不成立",

    # 多词对扩展：道德轴
    "善", "恶", "善良", "邪恶", "正义", "不义",
    "道德", "不道德", "正当", "不正当", "好", "坏",
    "仁", "不仁", "义", "不义",

    # 多词对扩展：美学轴
    "美", "丑", "漂亮", "难看", "优雅", "粗俗",
    "和谐", "混乱", "精致", "粗糙", "美", "不美",
    "好看", "难看", "美丽", "丑陋",

    # 多词对扩展：合作轴
    "合作", "冲突", "协作", "对抗", "团结", "分裂",
    "友好", "敌对", "和平", "战争", "信任", "欺骗",

    # 多词对扩展：自由轴
    "自由", "奴役", "解放", "束缚", "独立", "依赖",
    "自主", "控制", "宽松", "严格",
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

print(f"{'='*60}")
print("MULTI-PAIR AVERAGING FOR CONCEPT AXES")
print(f"{'='*60}")

# Define concept axes with multiple word pairs
concept_definitions = {
    "value": {
        "pairs": [
            ("好", "坏"),
            ("优秀", "差"),
            ("成功", "失败"),
            ("有益", "有害"),
            ("正面", "负面"),
        ],
        "description": "Good-Bad value axis"
    },
    "truth": {
        "pairs": [
            ("对", "错"),
            ("正确", "错误"),
            ("真实", "虚假"),
            ("是", "否"),
            ("确定", "不确定"),
        ],
        "description": "True-False truth axis"
    },
    "moral": {
        "pairs": [
            ("善", "恶"),
            ("善良", "邪恶"),
            ("正义", "不义"),
            ("道德", "不道德"),
            ("正当", "不正当"),
        ],
        "description": "Good-Evil moral axis"
    },
    "aesthetic": {
        "pairs": [
            ("美", "丑"),
            ("漂亮", "难看"),
            ("优雅", "粗俗"),
            ("和谐", "混乱"),
            ("精致", "粗糙"),
        ],
        "description": "Beautiful-Ugly aesthetic axis"
    },
}

print("\nConstructing concept axes with multi-pair averaging:")

multi_axes = {}
for axis_name, axis_info in concept_definitions.items():
    print(f"\n{axis_name.upper()} axis ({axis_info['description']}):")

    available_pairs = []
    for pos, neg in axis_info["pairs"]:
        if pos in concept_vectors and neg in concept_vectors:
            available_pairs.append((pos, neg))
            print(f"  {pos}-{neg}: available")
        else:
            print(f"  {pos}-{neg}: NOT in vocabulary")

    if available_pairs:
        # Compute individual axes
        individual_axes = []
        individual_sims = []
        for pos, neg in available_pairs:
            axis = concept_vectors[pos].float() - concept_vectors[neg].float()
            individual_axes.append(axis)
            # Self-similarity check
            sim = cosine(concept_vectors[pos], axis) - cosine(concept_vectors[neg], axis)
            individual_sims.append(sim)

        # Average axis
        avg_axis = torch.stack(individual_axes).mean(dim=0)

        # Compute separation with averaged axis
        separations = []
        for pos, neg in available_pairs:
            sep = cosine(concept_vectors[pos], avg_axis) - cosine(concept_vectors[neg], avg_axis)
            separations.append(sep)

        print(f"  Individual separations: {[f'{s:.3f}' for s in individual_sims]}")
        print(f"  Averaged axis separation: mean={np.mean(separations):.3f}, std={np.std(separations):.3f}")

        multi_axes[axis_name] = avg_axis
    else:
        print(f"  No available pairs!")

# Compare single-pair vs multi-pair axes
print(f"\n--- Single-Pair vs Multi-Pair Comparison ---")

# Single-pair axes (baseline)
single_axes = {
    "value": concept_vectors["好"].float() - concept_vectors["坏"].float(),
    "truth": concept_vectors["对"].float() - concept_vectors["错"].float(),
    "moral": concept_vectors["善"].float() - concept_vectors["恶"].float(),
    "aesthetic": concept_vectors["美"].float() - concept_vectors["丑"].float(),
}

# Test words
test_words = ["合作", "信任", "效率", "善良", "正义", "欺骗", "破坏", "冲突"]

print(f"\n{'Word':8s} {'Single-Value':>12s} {'Multi-Value':>12s} {'Single-Truth':>12s} {'Multi-Truth':>12s}")
print("-" * 60)

for w in test_words:
    if w in concept_vectors:
        v = concept_vectors[w].float()

        # Value axis
        score_single_val = cosine(v, single_axes["value"])
        score_multi_val = cosine(v, multi_axes["value"])

        # Truth axis
        score_single_truth = cosine(v, single_axes["truth"])
        score_multi_truth = cosine(v, multi_axes["truth"])

        print(f"{w:8s} {score_single_val:12.4f} {score_multi_val:12.4f} {score_single_truth:12.4f} {score_multi_truth:12.4f}")

# Opposition analysis with multi-pair axes
print(f"\n--- Opposition Analysis with Multi-Pair Axes ---")

opposition_test_pairs = [
    ("合作", "冲突"),
    ("帮助", "伤害"),
    ("创造", "破坏"),
    ("信任", "欺骗"),
    ("正义", "不义"),
    ("自由", "奴役"),
]

print(f"\n{'Pair':<15s} {'Original':>10s} {'Single-Sep':>12s} {'Multi-Sep':>12s} {'Improvement':>12s}")
print("-" * 65)

for w1, w2 in opposition_test_pairs:
    if w1 in concept_vectors and w2 in concept_vectors:
        v1 = concept_vectors[w1].float()
        v2 = concept_vectors[w2].float()

        # Original similarity
        sim_orig = cosine(v1, v2)

        # Single-pair axis separation
        axis_single = v1 - v2
        sep_single = cosine(v1, axis_single) - cosine(v2, axis_single)

        # Multi-pair value axis separation
        sep_multi = cosine(v1, multi_axes["value"]) - cosine(v2, multi_axes["value"])

        improvement = sep_multi - sep_single

        print(f"{w1}-{w2:<12s} {sim_orig:10.4f} {sep_single:12.4f} {sep_multi:12.4f} {improvement:+12.4f}")

print(f"\n{'='*60}")
print("PRAGMATIC-SEMANTIC SEPARATION")
print(f"{'='*60}")

# Define pragmatic axes
pragmatic_pairs = [
    ("好", "坏"),  # Value axis
    ("对", "错"),  # Truth axis
    ("善", "恶"),  # Moral axis
    ("美", "丑"),  # Aesthetic axis
]

# Build pragmatic difference matrix
print("\nBuilding pragmatic subspace...")
pragmatic_diffs = []
for pos, neg in pragmatic_pairs:
    if pos in concept_vectors and neg in concept_vectors:
        pragmatic_diffs.append(concept_vectors[pos].float() - concept_vectors[neg].float())

D_pragmatic = torch.stack(pragmatic_diffs)

# Get all vocabulary vectors for full SVD (not just 4 pairs)
all_vocab_vectors = torch.stack([concept_vectors[w].float() for w in row_concepts])

# Center the data
mean_vec = all_vocab_vectors.mean(dim=0)
centered_vectors = all_vocab_vectors - mean_vec

# SVD on full vocabulary to get proper subspace decomposition
U_full, S_full, V_full = torch.svd(centered_vectors)

# Pragmatic basis: project pragmatic axes onto top principal components
# Use the top k components that explain most variance
k_components = min(50, len(row_concepts))  # Use more components for semantic space
V_top = V_full[:, :k_components]

# Project pragmatic differences onto principal components
pragmatic_proj = D_pragmatic @ V_top  # Project to PC space

# Find dimensions most aligned with pragmatic axes
pragmatic_importance = pragmatic_proj.abs().sum(dim=0)
top_pragmatic_dims = pragmatic_importance.argsort(descending=True)[:len(pragmatic_pairs)]

print(f"Vocabulary size: {len(row_concepts)}")
print(f"Using {k_components} principal components")
print(f"Pragmatic subspace: {len(pragmatic_pairs)} dimensions")
print(f"Semantic subspace: {k_components - len(pragmatic_pairs)} dimensions")

# Build pragmatic and semantic projectors
pragmatic_mask = torch.zeros(k_components, dtype=torch.bool)
pragmatic_mask[top_pragmatic_dims] = True
semantic_mask = ~pragmatic_mask

# Projection functions
def to_pragmatic_space(v):
    """Project vector to pragmatic subspace"""
    v_centered = v.float() - mean_vec
    proj = v_centered @ V_top
    proj[semantic_mask] = 0
    return proj

def to_semantic_space(v):
    """Project vector to semantic subspace"""
    v_centered = v.float() - mean_vec
    proj = v_centered @ V_top
    proj[pragmatic_mask] = 0
    return proj

def similarity_in_space(v1, v2, space='original'):
    """Compute similarity in specified space"""
    if space == 'original':
        return cosine(v1, v2)
    elif space == 'pragmatic':
        v1_proj = to_pragmatic_space(v1)
        v2_proj = to_pragmatic_space(v2)
        return cosine(v1_proj, v2_proj)
    elif space == 'semantic':
        v1_proj = to_semantic_space(v1)
        v2_proj = to_semantic_space(v2)
        return cosine(v1_proj, v2_proj)

# Test separation
print("\n--- Testing Pragmatic-Semantic Separation ---")

test_words = ["好", "坏", "苹果", "香蕉", "善良", "正义", "对", "错"]
print(f"\n{'Word':8s} {'Original':>10s} {'Pragmatic':>10s} {'Semantic':>10s}")
print("-" * 45)

for w in test_words:
    if w in concept_vectors:
        v = concept_vectors[w]
        norm_orig = v.norm().item()
        v_prag = to_pragmatic_space(v)
        v_sem = to_semantic_space(v)
        norm_prag = v_prag.norm().item()
        norm_sem = v_sem.norm().item()

        print(f"{w:8s} {norm_orig:10.4f} {norm_prag:10.4f} {norm_sem:10.4f}")

# Compare similarity in different spaces
print("\n--- Similarity in Different Spaces ---")

comparison_pairs = [
    ("苹果", "香蕉"),
    ("善良", "正义"),
    ("好", "坏"),
    ("对", "错"),
    ("合作", "冲突"),
    ("自由", "奴役"),
]

print(f"\n{'Pair':<15s} {'Original':>10s} {'Pragmatic':>10s} {'Semantic':>10s}")
print("-" * 50)

results = []
for w1, w2 in comparison_pairs:
    if w1 in concept_vectors and w2 in concept_vectors:
        v1 = concept_vectors[w1]
        v2 = concept_vectors[w2]

        sim_orig = similarity_in_space(v1, v2, 'original')
        sim_prag = similarity_in_space(v1, v2, 'pragmatic')
        sim_sem = similarity_in_space(v1, v2, 'semantic')

        results.append((w1, w2, sim_orig, sim_prag, sim_sem))
        print(f"{w1}-{w2:<12s} {sim_orig:10.4f} {sim_prag:10.4f} {sim_sem:10.4f}")

# Verify pragmatic axes separation
print("\n--- Verifying Pragmatic Axes Separation ---")
print("Pragmatic axes should have high pragmatic similarity, low semantic similarity:")

for pos, neg in pragmatic_pairs:
    if pos in concept_vectors and neg in concept_vectors:
        v_pos = concept_vectors[pos]
        v_neg = concept_vectors[neg]

        sim_orig = similarity_in_space(v_pos, v_neg, 'original')
        sim_prag = similarity_in_space(v_pos, v_neg, 'pragmatic')
        sim_sem = similarity_in_space(v_pos, v_neg, 'semantic')

        print(f"  {pos}-{neg}: original={sim_orig:.3f}, pragmatic={sim_prag:.3f}, semantic={sim_sem:.3f}")

# =========================
# All Six Laws Verification
# =========================

print(f"\n{'='*60}")
print("ALL SIX LAWS VERIFICATION")
print(f"{'='*60}")

laws = {
    "Law 0": {
        "name": "存在即信息",
        "tests": [
            ("存在", "信息", "HIGH"),
            ("存在", "是", "HIGH"),
            ("真实", "信息", "HIGH"),
            ("物质", "意识", "CORRELATED"),
        ]
    },
    "Law 1": {
        "name": "完备即正确",
        "tests": [
            ("完备", "正确", "HIGH"),
            ("确定", "客观", "HIGH"),
            ("真理", "正确", "HIGH"),
            ("正确", "错误", "OPPOSITE"),
        ]
    },
    "Law 2": {
        "name": "不完备湮灭",
        "tests": [
            ("生存", "适应", "HIGH"),
            ("动机", "目标", "HIGH"),
            ("进化", "退化", "OPPOSITE"),
            ("竞争", "合作", "OPPOSITE"),
        ]
    },
    "Law 3": {
        "name": "自由即无知",
        "tests": [
            ("自由", "无知", "HIGH"),
            ("熵", "自由", "HIGH"),
            ("自由", "知识", "LOW"),
            ("自由", "奴役", "OPPOSITE"),
        ]
    },
    "Law 4": {
        "name": "正义即效率",
        "tests": [
            ("正义", "效率", "HIGH"),
            ("公平", "效率", "HIGH"),
            ("投资", "收益", "HIGH"),
            ("成本", "效率", "CORRELATED"),
        ]
    },
    "Law 5": {
        "name": "意义即利益",
        "tests": [
            ("意义", "利益", "HIGH"),
            ("价值", "利益", "HIGH"),
            ("幸福", "利益", "HIGH"),
            ("目的", "目标", "HIGH"),
        ]
    }
}

for law_id, law_info in laws.items():
    print(f"\n{law_id}: {law_info['name']}")
    print("-" * 40)

    results = []
    for w1, w2, pred in law_info["tests"]:
        if w1 in concept_vectors and w2 in concept_vectors:
            sim = cosine(concept_vectors[w1], concept_vectors[w2])

            # Evaluate prediction
            if pred == "HIGH" and sim > 0.5:
                status = "✓"
            elif pred == "LOW" and sim < 0.5:
                status = "✓"
            elif pred == "OPPOSITE" and sim < 0.5:
                status = "✓"
            elif pred == "CORRELATED":
                status = "~"
            else:
                status = "✗"

            results.append((w1, w2, sim, pred, status))
            print(f"  {w1}-{w2}: {sim:.3f} ({pred}) {status}")
        else:
            print(f"  {w1}-{w2}: N/A")

    # Summary for this law
    passed = sum(1 for r in results if r[4] == "✓")
    total = len(results)
    print(f"  → {passed}/{total} predictions supported")

# Overall summary
print(f"\n{'='*60}")
print("OVERALL SUMMARY")
print(f"{'='*60}")

summary_data = []

for law_id, law_info in laws.items():
    print(f"\n{law_id}: {law_info['name']}")

    tests = law_info["tests"]
    supported = 0
    total = 0

    for w1, w2, pred in tests:
        if w1 in concept_vectors and w2 in concept_vectors:
            sim = cosine(concept_vectors[w1], concept_vectors[w2])
            total += 1

            if pred == "HIGH" and sim > 0.5:
                supported += 1
            elif pred == "LOW" and sim < 0.5:
                supported += 1
            elif pred == "OPPOSITE" and sim < 0.5:
                supported += 1

    pct = supported/total*100 if total > 0 else 0
    summary_data.append((law_id, law_info['name'], supported, total, pct))

    if pct >= 75:
        status = "✅ VERIFIED"
    elif pct >= 50:
        status = "⚠️ PARTIAL"
    else:
        status = "❌ NOT SUPPORTED"

    print(f"  {supported}/{total} predictions supported ({pct:.0f}%) {status}")

# Final verdict
print(f"\n{'='*60}")
print("FINAL VERDICT")
print(f"{'='*60}")

verified = sum(1 for d in summary_data if d[4] >= 75)
partial = sum(1 for d in summary_data if 50 <= d[4] < 75)
not_supported = sum(1 for d in summary_data if d[4] < 50)

print(f"\nVerified (≥75%): {verified}/6 laws")
print(f"Partial (50-74%): {partial}/6 laws")
print(f"Not supported (<50%): {not_supported}/6 laws")

print("\nDetailed breakdown:")
for law_id, name, s, t, p in summary_data:
    print(f"  {law_id} ({name}): {s}/{t} = {p:.0f}%")

print(f"\n{'='*60}")
print("LAW 3 VERIFICATION: FREEDOM = IGNORANCE")
print(f"{'='*60}")

print("\n--- Direct Similarity Test ---")
print(f"{'Pair':<20s} {'Similarity':>12s} {'Prediction':>30s}")
print("-" * 65)

law3_pairs = [
    ("自由", "无知", "HIGH (Freedom = Ignorance)"),
    ("自由", "知识", "LOW (Knowledge opposite to freedom)"),
    ("自由", "奴役", "OPPOSITE"),
    ("无知", "知识", "OPPOSITE"),
    ("熵", "自由", "HIGH (Entropy = max freedom)"),
    ("混乱", "自由", "HIGH (Chaos = freedom)"),
    ("秩序", "知识", "HIGH (Order = knowledge)"),
]

for w1, w2, pred in law3_pairs:
    if w1 in concept_vectors and w2 in concept_vectors:
        sim = cosine(concept_vectors[w1], concept_vectors[w2])
        print(f"{w1}-{w2:<15s} {sim:12.4f} {pred:>30s}")

# Freedom axis projections
print("\n--- Freedom Axis (自由 - 奴役) Projections ---")

if "自由" in concept_vectors and "奴役" in concept_vectors:
    freedom_axis = concept_vectors["自由"].float() - concept_vectors["奴役"].float()

    words = ["自由", "无知", "知识", "约束", "混乱", "秩序", "奴役", "熵", "解放"]

    print(f"{'Word':<12s} {'Projection':>12s}")
    print("-" * 30)

    for w in words:
        if w in concept_vectors:
            proj = cosine(concept_vectors[w], freedom_axis)
            print(f"{w:<12s} {proj:12.4f}")

# Summary
print("\n--- Law 3 Summary ---")
if "自由" in concept_vectors and "无知" in concept_vectors:
    sim = cosine(concept_vectors["自由"], concept_vectors["无知"])
    if sim > 0.5:
        print(f"自由-无知 similarity = {sim:.3f} → SUPPORTS Law 3 (自由即无知)")
    else:
        print(f"自由-无知 similarity = {sim:.3f} → WEAK support for Law 3")

if "熵" in concept_vectors and "自由" in concept_vectors:
    sim = cosine(concept_vectors["熵"], concept_vectors["自由"])
    print(f"熵-自由 similarity = {sim:.3f}")

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
