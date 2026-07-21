# 概念几何分析工具

本目录包含用于概念几何分析的工具脚本。

## geometry.py

基于预训练语言模型的隐藏状态，分析概念在语义空间中的方向关系。

### 环境配置

```bash
pip install torch transformers
```

### 核心函数

#### `get_vector(text, layer=-1)`

获取文本的语义向量。

- **参数**
  - `text`: 输入文本
  - `layer`: 模型层索引，-1 表示最后一层，0 表示 embedding 层
- **返回**: 语义向量（经 mean pooling）

#### `concept_axis(pos, neg)`

构造概念轴（正负方向向量差）。

- **参数**
  - `pos`: 正向词（如 "好"）
  - `neg`: 负向词（如 "坏"）
- **返回**: 概念方向向量

#### `cosine(a, b)`

计算两个向量的余弦相似度。

- **返回**: -1 到 1 之间的相似度值

### 使用示例

```python
# 构造概念轴
axis_good_bad = concept_axis("好", "坏")
axis_efficient = concept_axis("高效", "低效")

# 比较概念方向相似度
similarity = cosine(axis_good_bad, axis_efficient)
print(f"好-坏 轴与 高效-低效 轴的相似度: {similarity}")

# 投影分析
words = ["合作", "信任", "欺骗", "破坏"]
for word in words:
    vec = get_vector(word)
    score = cosine(vec, axis_good_bad)
    print(f"{word}: {score}")
```

### 模型选择

脚本默认使用 `bert-base-chinese`，可通过修改 `MODEL` 变量切换：

| 模型 | 特点 |
|------|------|
| `bert-base-chinese` | 12层，768维，通用中文模型 |
| `BAAI/bge-large-zh-v1.5` | 专门优化的中文 embedding 模型，效果更好 |
| `Qwen/Qwen2.5-7B` | 大模型，语义理解更强，需要更多资源 |
| `hfl/chinese-roberta-wwm-ext` | 全词遮罩预训练，中文理解更准确 |

### 改进方向

1. **多词对平均** - 用多对正反义词定义概念轴，减少单词噪声
2. **Layer 选择** - 中间层（如 -6 ~ -4）可能比最后一层更"语义"
3. **Pooling 策略** - 对长句可考虑 CLS token 或去掉 `[CLS]`/`[SEP]` 后再 pooling
4. **词表约束** - 优先选择模型词表中完整存在的词

## 理论关联

详见 [THEORY.md](THEORY.md)，说明概念几何分析与事物原理的关联。