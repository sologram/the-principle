# 概念几何分析原理

## 核心问题

词向量同时包含两类信息：

1. **语用信息** — 评价性维度（好/坏、对/错、善/恶）
2. **语法信息** — 语言形式化表达（我们不关心）

两者的混合导致一个反直觉现象：语义相反的词（如"好-坏"）在向量空间中显示**高相似度**。

```
cosine(好, 坏) ≈ 0.9  # 高相似度！
```

这与我们对"相反"的直觉理解矛盾：相反的事物应该距离远、方向相反。

### 为什么会这样？

词向量通过分布假设训练：出现在相似上下文中的词获得相似的向量。

"好"和"坏"的上下文高度重叠：
- "这是个**好**主意" vs "这是个**坏**主意"
- "**好**天气" vs "**坏**天气"

因此它们被映射到相近的方向，差异仅在于评价极性。

## 解决方案：语用空间分析

核心思想：**分离出语用维度，在语用空间中重新计算相似度**。

### 三空间模型

```
原始空间 → [语用空间 + 语义空间]
```

1. **原始空间**：模型输出的完整向量空间
2. **语用空间**：由语用轴张成的子空间，捕获评价性信息
3. **语义空间**：语用空间的正交补，捕获概念本身的含义

### 语用轴定义

语用轴是定义在向量空间中的方向，由正负极词确定：

```
axis = pos_vec - neg_vec
```

| 语用轴 | 正向极 | 负向极 | 理论定义 |
|--------|--------|--------|----------|
| 价值轴 | 好 | 坏 | 好=效率 |
| 真值轴 | 对 | 错 | 对=完备 |
| 道德轴 | 善 | 恶 | 善=合作 |
| 美学轴 | 美 | 丑 | 美=效率 |

### 空间分解算法

```python
# 1. 收集语用轴方向
axes = [价值轴, 真值轴, 道德轴, 美学轴]

# 2. 正交化（Gram-Schmidt）
pragmatic_basis = orthogonalize(axes)

# 3. 投影到语用空间
v_prag = project(v, pragmatic_basis)

# 4. 残差为语义空间
v_sem = v - v_prag
```

### 相似度计算

对任意两个词 w1、w2：

```python
# 原始相似度
sim_original = cosine(v1, v2)

# 语用相似度
v1_prag = project(v1, pragmatic_basis)
v2_prag = project(v2, pragmatic_basis)
sim_pragmatic = cosine(v1_prag, v2_prag)

# 语义相似度
v1_sem = v1 - v1_prag
v2_sem = v2 - v2_prag
sim_semantic = cosine(v1_sem, v2_sem)
```

## 关键洞察

### 为什么反义词在语用空间显示负相似度？

在原始空间中：
```
好 ≈ [语义成分] + [正向评价]
坏 ≈ [语义成分] + [负向评价]
```

语义成分相似度高（都是评价性词），所以整体相似度高。

在语用空间中：
```
好_prag ≈ [+1]（沿轴正方向）
坏_prag ≈ [-1]（沿轴负方向）
```

投影后只剩下评价极性，方向相反，相似度为负。

### 数学直觉

设价值轴方向为 `a = 好 - 坏`，则：

```
cosine(好, a) > 0  # 好在轴的正侧
cosine(坏, a) < 0  # 坏在轴的负侧
```

两个词在该轴上的投影值符号相反，导致语用相似度为负。

## 定律验证方法

### 正向词对验证

理论预言相关的概念应该在原始空间中相似：

```yaml
positive_pairs:
  - [完备, 正确]  # 完备即正确
  - [正义, 效率]  # 正义即效率
```

验证条件：`cosine(w1, w2) > 0.5`

### 反向词对验证

理论预言相反的概念应该在语用空间中显示负相似度：

```yaml
opposite_pairs:
  - [完备, 不完备]
  - [正义, 不公]
```

验证条件：`cosine(w1_prag, w2_prag) < -0.3`

### 定律通过标准

- **verified**：验证率 ≥ 75%
- **partial**：验证率 50%-74%
- **not supported**：验证率 < 50%

## 配置文件结构

每个定律配置 (`laws/law*.yaml`) 包含：

```yaml
name: 完备即正确
theory: 任何正确不允许任何遗漏

positive_pairs:
  - [完备, 正确]

opposite_pairs:
  - [完备, 不完备]

pragmatic_axes:
  价值轴:
    pos_words: [good, excellent, success, beneficial]
    neg_words: [bad, poor, failure, harmful]

thresholds:
  positive_similarity: 0.5    # 正向词对相似度阈值
  opposite_pragmatic: -0.3    # 反向词对语用相似度阈值
```

## 算法实现细节

### 向量提取

从语言模型的指定层提取词向量：

```python
def get_vector(text, layer=0):
    inputs = tokenizer(text)
    outputs = model(**inputs)
    hidden_states = outputs.hidden_states  # 各层输出

    # 取指定层
    h = hidden_states[layer]

    # 平均池化（排除 padding）
    mask = attention_mask.unsqueeze(-1)
    vec = (h * mask).sum(dim=1) / mask.sum(dim=1)

    return vec
```

### 语用轴计算

```python
def compute_axis(pos_words, neg_words, extractor):
    pos_vecs = [extractor.get_vector(w) for w in pos_words]
    neg_vecs = [extractor.get_vector(w) for w in neg_words]

    pos_vec = mean(pos_vecs)
    neg_vec = mean(neg_vecs)

    return pos_vec - neg_vec
```

### 轴质量评估

轴的"分离度"衡量其区分正负极的能力：

```python
def separation(axis):
    pos_proj = cosine(axis.pos_vec, axis.axis)
    neg_proj = cosine(axis.neg_vec, axis.axis)
    return pos_proj - neg_proj
```

分离度越高，轴质量越好：
- **excellent**：> 1.0
- **good**：> 0.5
- **poor**：≤ 0.5

## 模型选择

不同模型的特性：

| 模型 | 原始相似度 | 语用分离度 | 定律验证 |
|------|-----------|-----------|---------|
| InfoXLM-large | 高 (0.8-0.9) | 中等 | 3/6 |
| Qwen3.5-9b | 低 (0.5-0.7) | 较弱 | 2/6 |

InfoXLM 作为多语言模型，对跨语言概念的表示更统一，但语用差异在底层更明显。

Qwen 作为中文模型，语义表示更精准，但语用极性在各层差异不大。

## 层选择

不同层的向量捕获不同粒度的信息：

- **层 0**（embedding 层）：最原始的词表示，语用差异更明显
- **中间层**：语义信息逐渐丰富
- **顶层**：任务相关的抽象表示

实验表明，层 0 在语用轴分离度上表现最好，建议作为默认选择。

## 局限性与未来方向

### 当前局限

1. **轴定义依赖先验知识**：需要人工选择正负极词
2. **线性假设**：假设语用差异是线性的（可能过于简化）
3. **模型偏差**：不同模型的验证结果差异较大

### 可能的改进

1. **自动发现语用轴**：通过 PCA 或 contrastive learning 自动发现语用方向
2. **非线性建模**：用神经网络学习更复杂的语用表示
3. **多语言对齐**：利用多语言模型的对齐能力改进跨语言验证

## 参考

- [THEORY.md](THEORY.md) — 详细验证结果
- [README-zh.md](README-zh.md) — 工具使用说明