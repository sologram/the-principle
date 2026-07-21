# 概念几何分析算法

本文档描述 `geometry.py` 中使用的概念几何分析方法。

## 1. 向量提取

### Mean Pooling

从 Transformer 模型提取语义向量，使用隐藏状态的均值池化。

```python
def get_vector(text):
    inputs = tokenizer(text, return_tensors="pt")
    outputs = model(**inputs)
    
    # 获取最后隐藏层
    h = outputs.last_hidden_state  # 形状: [1, seq_len, hidden_dim]
    
    # 对 token 进行均值池化
    mask = inputs["attention_mask"].unsqueeze(-1)
    vec = (h * mask).sum(dim=1) / mask.sum(dim=1)
    
    return vec[0]  # 形状: [hidden_dim]
```

**为什么用 mean pooling：**
- CLS token 是任务特定的（分类微调）
- Mean pooling 捕获所有 token 信息
- 用 attention mask 加权，忽略 padding token

**局限性：**
- 单字可能语义不够丰富
- 长文本会稀释含义
- 层选择影响语义纯度

## 2. 概念轴构造

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

**性质：**
- 与轴的 cosine 相似度表示在该维度上的位置
- 正分 → 靠近正向极
- 负分 → 靠近负向极

### 多词对平均（推荐）

通过平均多个词对减少噪声：

```python
pairs = [("好", "坏"), ("优秀", "差"), ("成功", "失败")]
axis = mean([concept_axis(p, n) for p, n in pairs])
```

## 3. 相似度度量

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

**为什么用 cosine：**
- 与幅度无关（只比较方向）
- 对嵌入缩放不敏感
- NLP 中的标准度量

## 4. 相逆度度量

### 4.1 简单相逆度（1 - 相似度）

```python
opposition = 1 - similarity
```

**范围：** 0（相同）到 1（正交）到 2（相反）

**局限：** 假设相似度为 0 时为相反，未考虑负相似度。

### 4.2 角度法

```python
angle = arccos(similarity) * 180 / π  # 角度
normalized_angle = angle / 180  # 归一化到 [0, 1]
```

**解释：**
- 0° = 相同
- 90° = 正交
- 180° = 相反

**优点：** 几何直观，能处理负相似度。

### 4.3 轴投影分离度

将词投影到其自身概念轴上：

```python
axis = vector(pos) - vector(neg)
proj_pos = cosine(vector(pos), axis)  # 应为正
proj_neg = cosine(vector(neg), axis)  # 应为负
separation = proj_pos - proj_neg      # 越大分离越好
```

**解释：**
- 分离好的词对：正向极投影为正，负向极投影为负
- 分离度 > 1.0 表示相逆性好
- 即使相似度高也能捕获方向上的相逆

**实验结果：**
| 词对 | 相似度 | 分离度 | 解释 |
|------|--------|--------|------|
| 对-错 | 0.44 | 1.06 | 相逆性好 |
| 好-坏 | 0.63 | 0.86 | 相逆性中等 |
| 客观-主观 | 0.77 | ~0.50 | 相逆性差 |

## 5. 旋转方法

### 5.1 无旋转（基线）

直接使用原始嵌入，不做变换。

### 5.2 PCA 旋转

将嵌入空间旋转到主成分轴：

```python
from sklearn.decomposition import PCA

# 在词汇表上拟合 PCA
vectors = stack([get_vector(w) for w in vocabulary])
pca = PCA(n_components=len(vectors))
pca.fit(vectors)

# 变换向量
rotated = pca.transform(vector)
```

**效果：**
- 正交变换（保持角度）
- 轻微改善分离度
- 不引入偏差

### 5.3 PCA 对齐（实验性）

将概念轴投影到顶级主成分：

```python
top_components = pca.components_[:k]  # 前 k 个主成分
projection = axis @ top_components.T
aligned = projection @ top_components
```

**效果：**
- 显著提高相似度
- 可能引入人为相关性
- 验证时需谨慎使用

## 6. 跨语言分析

### 概念对齐

比较不同语言的概念轴：

```python
axis_zh = concept_axis("好", "坏")
axis_en = concept_axis("good", "bad")
alignment = cosine(axis_zh, axis_en)
```

**发现：**
- good-bad: 0.90（高度对齐）
- correct-error: 0.90（高度对齐）
- yes-no: 0.15（对齐差）

### 词汇映射

| 中文 | 英文 | 说明 |
|------|------|------|
| 善 | good/kind | 不同于"good"（好）|
| 正 | righteous | 不同于"right"（对）|
| 邪 | wicked | 不同于"evil"（恶）|

## 7. 统计考虑

### 样本量

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

## 8. 理论解释

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