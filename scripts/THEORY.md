# 概念几何与事物原理

本文档说明 `geometry.py` 脚本与 [事物原理](../README.md) 理论框架的关联。

## 核心概念对照

脚本中的概念轴与事物原理的术语定义直接对应：

| 概念轴 | 事物原理定义 | 来源 |
|--------|--------------|------|
| 好-坏 | 好即效率，坏即不效率 | [GLOSSARIES-FULL.md](../zh/GLOSSARIES-FULL.md#h) |
| 善-恶 | 善即合作，恶即不合作或反合作 | [GLOSSARIES-FULL.md](../zh/GLOSSARIES-FULL.md#s) |
| 合作-冲突 | 合作是个体之间为达成共同目标而进行的协调行动 | [GLOSSARIES-FULL.md](../zh/GLOSSARIES-FULL.md#h) |
| 正确-错误 | 正确即完备，错误即不完备 | [GLOSSARIES-FULL.md](../zh/GLOSSARIES-FULL.md#z) |
| 高效-低效 | 效率是用最小资源达成目标的能力 | [GLOSSARIES-FULL.md](../zh/GLOSSARIES-FULL.md#x) |

## 可验证的理论预测

基于事物原理的定义，可以预测概念轴之间的方向关系：

### 预测 1：好-坏 ≈ 高效-低效

**理论依据**：好 = 效率

**验证方法**：
```python
axis_good = concept_axis("好", "坏")
axis_efficiency = concept_axis("高效", "低效")
cosine(axis_good, axis_efficiency)  # 应接近 1
```

### 预测 2：善-恶 ≈ 合作-冲突

**理论依据**：善 = 合作

**验证方法**：
```python
axis_good = concept_axis("善", "恶")
axis_cooperation = concept_axis("合作", "冲突")
cosine(axis_good, axis_cooperation)  # 应接近 1
```

### 预测 3：好-坏 与 善-恶 相关但不重合

**理论依据**：好（效率）与善（合作）相关但不同。合作提高效率，但效率不仅来自合作。

**验证方法**：
```python
axis_good = concept_axis("好", "坏")
axis_kind = concept_axis("善", "恶")
cosine(axis_good, axis_kind)  # 应为正但小于 1
```

## 实验设计建议

### 多词对验证

用多对词定义概念轴，提高稳健性：

```python
# 好的定义：效率
good_pairs = [
    ("好", "坏"),
    ("优秀", "差"),
    ("成功", "失败"),
    ("高效", "低效"),
    ("有用", "无用"),
]

axis_good = sum(concept_axis(p, n) for p, n in good_pairs) / len(good_pairs)

# 善的定义：合作
kind_pairs = [
    ("善", "恶"),
    ("合作", "冲突"),
    ("帮助", "伤害"),
    ("信任", "欺骗"),
    ("友好", "敌对"),
]

axis_kind = sum(concept_axis(p, n) for p, n in kind_pairs) / len(kind_pairs)
```

### 层次分析

比较不同层的语义表示：

```python
for layer in [-1, -2, -4, -6, -8]:
    vec = get_vector("好", layer=layer)
    # 分析哪一层最符合理论预测
```

### 术语投影

将 [GLOSSARIES-FULL.md](../zh/GLOSSARIES-FULL.md) 中定义的核心术语投影到概念轴：

```python
terms = ["效率", "合作", "正确", "正义", "自由", "秩序"]
axis_good = concept_axis("好", "坏")

for term in terms:
    vec = get_vector(term)
    score = cosine(vec, axis_good)
    print(f"{term}: {score}")
```

理论预测结果：效率、合作、正确、正义 > 0；自由、秩序 方向不确定（取决于具体语境）。

## 理论意义

1. **验证概念定义的自洽性** - 如果模型学到概念方向与理论定义一致，说明理论符合语言直觉
2. **发现潜在关联** - 意外的相似度可能揭示尚未理论化的概念关联
3. **量化概念关系** - 将抽象概念转化为可测量的几何关系

## 注意事项

- 单词对定义轴噪声较大，建议多词对平均
- 不同模型的表示空间不同，结果可能差异较大
- 语义相似 ≠ 概念等价，cosine 相似度只是参考指标
- 模型的训练数据可能包含偏差，影响概念方向
