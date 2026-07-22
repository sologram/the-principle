# 概念几何分析原理

本文档说明语义空间分析的数学原理和算法实现。

## 核心问题

词向量同时包含两类信息：

- **语义信息**：概念内容、关系、评价方向（好/坏、对/错、善/恶）
- **语法信息**：语言形式化表达（句法结构、词形、上下文分布）

两者混合导致反义词（如"好-坏"）显示高相似度，与传统几何直觉矛盾。

```
cosine(好, 坏) ≈ 0.9
```

原因：反义词共享大量语法上下文，仅在语义方向上有差异。原始空间距离反映"使用环境相似性"，不反映"逻辑关系中的相反性"。

## 解决方案：语义空间分解

### 空间定义

将原始词向量空间 V 分解为两个正交子空间：

```
原始空间 V
    |
    +----------------+
    |                |
语义空间 P       语法空间 S
(评价方向)       (语义正交补)
```

- **原始空间 V**：模型直接输出的隐藏表示，包含所有混合信息
- **语义空间 P**：由多个评价轴构成的低维子空间，捕获价值、真假、道德、美学等维度
- **语法空间 S**：语义空间的正交补，S = V - P，表示去除评价后的概念内容

### 语义轴定义

语义轴表示评价空间中的基本方向，由正负概念对定义：

```
axis = v_pos - v_neg
```

| 语义轴 | 正极 | 负极 | 理论依据 |
|--------|------|------|----------|
| 价值轴 | 好 | 坏 | 好 = 效率 |
| 真值轴 | 对 | 错 | 对 = 完备 |
| 道德轴 | 善 | 恶 | 善 = 合作 |
| 美学轴 | 美 | 丑 | 美 = 效率 |

多个轴共同构成语义空间。

## 空间分解算法

### 1. 计算语义基

收集所有语义轴方向，进行正交化：

```python
# 收集各轴方向向量
semantic_dirs = [ax.axis for ax in semantic_axes]

# QR 正交化得到正交基
P = torch.stack(semantic_dirs)
P_orth, _ = torch.linalg.qr(P.T)
semantic_basis = P_orth.T
```

### 2. 构建语法残差基

语义轴不能覆盖所有语义信息，剩余部分用 PCA 提取：

```python
# 计算语义投影后的残差
proj_sem = centered @ semantic_basis.T @ semantic_basis
semantic_residuals = centered - proj_sem

# PCA 提取主要残差方向
pca = PCA(n_components=n_semantic)
pca.fit(semantic_residuals)
residual_basis = pca.components_
```

### 3. 向量分解

对于任意词向量 v：

```python
# 中心化
v_centered = v - mean_vec

# 语义投影
v_sem = v_centered @ semantic_basis.T

# 语法投影（语义残差空间）
proj_sem = v_centered @ semantic_basis.T @ semantic_basis
v_syn = (v_centered - proj_sem) @ residual_basis.T
```

## 相似度计算

对于两个词 w1, w2：

| 空间 | 计算方法 | 含义 |
|------|---------|------|
| 原始空间 | `cosine(v1, v2)` | 整体相似度 |
| 语义空间 | `cosine(v1_sem, v2_sem)` | 评价方向相似度 |
| 语法空间 | `cosine(v1_syn, v2_syn)` | 去除评价后的相似度 |

### 关键几何解释

在原始空间：
```
好 ≈ 共同语法 + 正评价
坏 ≈ 共同语法 + 负评价
```
由于共同语法占据主要维度，`cosine(好, 坏) > 0`。

经过语义投影：
```
好_sem ≈ +1（在价值轴正方向）
坏_sem ≈ -1（在价值轴负方向）
```
因此 `cosine(好_sem, 坏_sem) < 0`。

**结论**：反义关系不是不存在，而是被隐藏在高维混合空间中的某个方向。

## 验证方法

### 正向关系验证

理论假设：同一原理中的正向概念应在原始空间中保持相关。

```python
cosine(w1, w2) > 0.5  # 正向相似度阈值
```

### 对立关系验证

理论假设：对立概念应在语义空间中方向相反。

```python
cosine(w1_sem, w2_sem) < -0.3  # 语义相似度阈值（负值）
```

### 轴质量评价

定义轴分离度：

```
D = cos(pos_vec, axis) - cos(neg_vec, axis)
```

评价标准：
- `excellent`：D > 1.0
- `good`：D > 0.5
- `poor`：D ≤ 0.5

### 定律验证状态

| 状态 | 验证率 |
|------|--------|
| verified | ≥ 75% |
| partial | 50% - 74% |
| not supported | < 50% |

## 向量提取

从 Transformer 模型隐藏层获取表示：

```python
def get_vector(text, layer=0):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs, output_hidden_states=True)

    # 获取指定层隐藏状态
    hidden = outputs.hidden_states[layer]

    # 注意力掩码加权平均
    mask = inputs["attention_mask"].unsqueeze(-1)
    vec = (hidden * mask).sum(dim=1) / mask.sum(dim=1)

    return vec[0]
```

### 多层融合

如果 layer 是列表，融合多层表示：

```python
if isinstance(layer, list):
    vecs = [get_layer_vec(l) for l in layer]
    return torch.stack(vecs).mean(dim=0)
```

## 实现细节

### 类结构

```
VectorExtractor      - 向量提取
    └── get_vector() - 从模型获取词向量

ConceptAxis          - 语义轴定义
    ├── _compute_axis() - 计算轴方向
    └── self_separation() - 轴分离度

SemanticSpace        - 语义空间管理
    ├── _build_space() - 构建空间分解
    └── similarity() - 计算三种相似度

ConceptGeometryAnalyzer - 分析器
    ├── analyze_axis_quality() - 轴质量分析
    ├── analyze_opposites() - 反义词分析
    └── verify_law() - 定律验证
```

### 数据流程

```
laws/*.yaml
    ↓
加载配置（positive_pairs, opposite_pairs, semantic_axes, thresholds）
    ↓
构建语义轴（ConceptAxis）
    ↓
构建语义空间（SemanticSpace）
    ↓
计算相似度（original, semantic, syntactic）
    ↓
验证定律（阈值判断）
    ↓
输出报告
```

## 局限性

1. **依赖人工定义轴**：需要人工提供正负概念，可能引入主观偏差
2. **线性假设**：假设语义结构可由线性子空间表达，可能无法捕获复杂关系
3. **模型依赖**：不同模型学习到不同的语义结构，结果可能差异较大
4. **词汇量限制**：小词汇表可能导致 PCA 分解不稳定

## 改进方向

1. **自动发现语义轴**：PCA、ICA、对比学习
2. **非线性语义空间**：核方法、神经网络投影、流形学习
3. **多语言语义对齐**：验证跨文化语义空间一致性
4. **扩大词表**：提高子空间分解稳定性

## 参考

- [README-zh.md](README-zh.md) — 工具使用说明
- [THEORY.md](THEORY.md) — 实验结果与分析
