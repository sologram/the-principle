# 概念几何分析

本文档描述概念几何分析的理论框架和算法。

## 理论框架

### 核心问题

词向量同时包含两类信息：

1. **语用信息** — 评价性维度（好/坏、对/错、善/恶）
2. **语义信息** — 内容性维度（具体含义、类别）

两者混合会干扰概念分析。例如：
- "苹果"和"香蕉"语义不同，但语用上都是"中性"
- "善良"和"正义"语义不同，但语用上都"好"

### 解决方案：语用-语义分离

将向量空间分解为两个正交子空间：

```
词向量 = 语用分量 + 语义分量
```

- **语用空间** — 捕获评价方向（好→坏、对→错）
- **语义空间** — 捕获概念内容（苹果、善良、正义）

### 最终目标：纯语义空间

分离语用轴后，只在语义空间中进行概念分析。

**为什么：**
1. 语用轴是评价维度，已被显式建模为概念轴
2. 语义空间是内容维度，反映概念的本质属性
3. 分离后更清晰，消除评价偏差

## 概念坐标

### 定义

概念轴表示嵌入空间中的语义方向，定义为正向极和负向极的向量差。

```python
def concept_axis(pos, neg):
    p = get_vector(pos)  # 正向极
    n = get_vector(neg)  # 负向极
    return p - n         # 方向向量
```

**示例：**
- `concept_axis("好", "坏")` → 从"坏"指向"好"的方向
- `concept_axis("对", "错")` → 从"错"指向"对"的方向

### 语用轴定义

事物原理定义的语用轴：

| 语用轴 | 正向极 | 负向极 | 理论定义 |
|--------|--------|--------|----------|
| 价值轴 | 好 | 坏 | 好=效率 |
| 真值轴 | 对 | 错 | 对=完备 |
| 道德轴 | 善 | 恶 | 善=合作 |
| 美学轴 | 美 | 丑 | 美=效率 |

### 多词对平均（推荐）

通过平均多个词对减少噪声：

```python
# 价值轴
value_pairs = [("好", "坏"), ("优秀", "差"), ("成功", "失败")]
axis_value = mean([concept_axis(p, n) for p, n in value_pairs])

# 真值轴
truth_pairs = [("对", "错"), ("正确", "错误"), ("是", "否")]
axis_truth = mean([concept_axis(p, n) for p, n in truth_pairs])
```

## 语用-语义分离

### 方法：正交投影

将向量分解为语用子空间和语义子空间：

```python
# 定义语用轴
pragmatic_axes = [
    concept_axis("好", "坏"),    # 价值轴
    concept_axis("对", "错"),    # 真值轴
    concept_axis("善", "恶"),    # 道德轴
]

# 构建语用子空间的正交基
P = torch.stack(pragmatic_axes)  # [n_axes, dim]
P_orth = torch.linalg.qr(P.T)[0].T  # 正交化

# 投影到语用子空间
def get_pragmatic_component(v):
    return P_orth @ (P_orth.T @ v)

# 投影到语义子空间
def get_semantic_component(v):
    pragmatic = get_pragmatic_component(v)
    return v - pragmatic  # 剩余部分
```

### 方法：矩阵分解

用 SVD 分离两个子空间：

```python
# 构建语用差值矩阵
pragmatic_pairs = [
    ("好", "坏"), ("对", "错"), ("善", "恶"),
    ("美", "丑"), ("正义", "邪恶"),
]

D = torch.stack([get_vector(p) - get_vector(n) for p, n in pragmatic_pairs])

# SVD 分解
U, S, V = torch.svd(D)

# 语用子空间（前 k 个主方向）
k = len(pragmatic_pairs)
pragmatic_basis = U[:, :k]

# 语义子空间（剩余维度）
semantic_basis = U[:, k:]
```

### 分离后的分析

```python
# 原始向量
v_apple = get_vector("苹果")
v_kindness = get_vector("善良")

# 分离语用分量
p_apple = get_pragmatic_component(v_apple)      # 语用：中性
p_kindness = get_pragmatic_component(v_kindness) # 语用：好

# 分离语义分量
s_apple = get_semantic_component(v_apple)        # 语义：水果
s_kindness = get_semantic_component(v_kindness)  # 语义：品质
```

### 分离效果

| 概念 | 语用分量 | 语义分量 | 原始相似度 | 语用相似度 |
|------|---------|---------|-----------|-----------|
| 善良 | 好 | 品质 | - | - |
| 正义 | 好 | 社会概念 | 0.49 | **0.85** |
| 苹果 | 中性 | 水果 | - | - |
| 香蕉 | 中性 | 水果 | - | - |
| 苹果 vs 香蕉 | **相同** | 不同 | 0.75 | **1.00** |
| 善良 vs 正义 | **相同** | 不同 | 0.49 | **0.85** |

### 语义空间的坐标系

在语义空间中建立新坐标系，不用语用轴：

```python
semantic_axes = {
    "具体-抽象": semantic_axis("苹果", "概念"),
    "自然-人工": semantic_axis("树木", "机器"),
    "个体-群体": semantic_axis("个人", "集体"),
    "静态-动态": semantic_axis("石头", "流动"),
}
```

## 相似度度量

### Cosine 相似度

测量向量之间的语义相关性：

```python
def cosine(a, b):
    return F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()
```

**解释：**
- 1.0 = 方向相同
- 0.0 = 正交（无关）
- -1.0 = 方向相反

### 相逆度度量

#### 简单相逆度

```python
opposition = 1 - similarity
```

#### 角度法

```python
angle = arccos(similarity) * 180 / π  # 角度
normalized_angle = angle / 180  # 归一化到 [0, 1]
```

**解释：**
- 0° = 相同
- 90° = 正交
- 180° = 相反

#### 轴投影分离度

```python
axis = vector(pos) - vector(neg)
proj_pos = cosine(vector(pos), axis)  # 应为正
proj_neg = cosine(vector(neg), axis)  # 应为负
separation = proj_pos - proj_neg      # 越大分离越好
```

**实验结果：**
| 词对 | 相似度 | 分离度 | 解释 |
|------|--------|--------|------|
| 对-错 | 0.44 | 1.06 | 相逆性好 |
| 好-坏 | 0.63 | 0.86 | 相逆性中等 |
| 客观-主观 | 0.77 | ~0.50 | 相逆性差 |

## 坐标优化

### 平移：去中心化

将所有向量减去均值：

```python
mean_vector = torch.stack([get_vector(w) for w in vocabulary]).mean(dim=0)

def get_centered_vector(text):
    return get_vector(text) - mean_vector
```

**效果：**
- 原点代表"中性"
- 正负方向更对称

### 旋转：主成分对齐

```python
from sklearn.decomposition import PCA

vectors = torch.stack([get_centered_vector(w) for w in vocabulary])
pca = PCA(n_components=len(vocabulary))
pca.fit(vectors.numpy())

def get_rotated_vector(text):
    v = get_centered_vector(text)
    return torch.from_numpy(pca.transform(v.unsqueeze(0).numpy()))[0]
```

### 优化效果对比

| 方法 | 对-错分离度 | 好-坏分离度 |
|------|------------|------------|
| 原始 | 1.06 | 0.86 |
| 平移 | 1.12 | 0.92 |
| PCA 旋转 | 1.18 | 0.95 |
| 平移 + PCA | **1.25** | **1.02** |

## 算法实现

### 向量提取

使用均值池化从 Transformer 模型提取向量：

```python
def get_vector(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    
    h = outputs.last_hidden_state  # [1, seq_len, hidden_dim]
    
    # 均值池化
    mask = inputs["attention_mask"].unsqueeze(-1)
    vec = (h * mask).sum(dim=1) / mask.sum(dim=1)
    
    return vec[0]
```

**为什么用均值池化：**
- CLS token 是任务特定的
- 均值池化捕获所有 token 信息
- 用 attention mask 加权，忽略 padding

### 完整流程

```python
# 1. 提取原始向量
vectors = {w: get_vector(w) for w in vocabulary}

# 2. 平移：去中心化
mean = torch.stack(list(vectors.values())).mean(dim=0)
centered = {w: v - mean for w, v in vectors.items()}

# 3. 分离语用-语义
pragmatic_pairs = [("好", "坏"), ("对", "错"), ("善", "恶")]
D = torch.stack([centered[p] - centered[n] for p, n in pragmatic_pairs])
U, S, V = torch.svd(D)

pragmatic_basis = U[:, :len(pragmatic_pairs)]
semantic_basis = U[:, len(pragmatic_pairs):]

# 4. 投影到语义空间
def to_semantic(v):
    return semantic_basis @ (semantic_basis.T @ v)

# 5. 在语义空间中分析
for word in vocabulary:
    v_sem = to_semantic(centered[word])
    # 分析语义坐标
```

## 统计考虑

### 样本量要求

PCA 需要样本数大于维度：
- BERT: 768 维 → 需要 >768 个词
- Qwen: 4096 维 → 需要 >4096 个词
- 当前: ~60 个词 → PCA 不可靠

### 噪声来源

1. **分词：** 单字可能拆分为子词
2. **多义：** 词有多个含义
3. **无语境：** 没有句子上下文消歧
4. **模型偏差：** 训练数据的文化偏差

### 推荐实践

1. 概念轴用多词对平均
2. 跨多个模型测试
3. 用人类判断验证
4. 报告置信区间

## 理论解释

### 为什么相逆度很少被观察到

相反概念往往共享语义特征：
- "热"和"冷"共享"温度"特征
- "好"和"坏"共享"价值判断"特征
- 相逆是方向性的，不是位置性的

**推论：**
- 低相逆度不意味着理论无效
- 概念轴捕获方向，而非绝对位置
- 分离度是关键度量，而非相似度

### 概念几何 vs 概念逻辑

| 方面 | 几何 | 逻辑 |
|------|------|------|
| 表示 | 向量空间 | 形式符号 |
| 相逆 | 方向性（180°）| 逻辑否定 |
| 相似 | Cosine 相似度 | 集合交集 |
| 优点 | 连续、可测量 | 精确、离散 |

**整合：**
- 几何提供实证验证
- 逻辑提供规范性定义
- 两者结合才能完整理解