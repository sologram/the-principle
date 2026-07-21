# 概念几何分析

概念几何分析的理论框架、算法实现和验证结果。

## 快速开始

```bash
python geometry.py --task all
python geometry.py --task law --law law1
```

详细验证结果见 [THEORY.md](THEORY.md)。

## 核心问题

词向量同时包含两类信息：

1. **语用信息** — 评价性维度（好/坏、对/错、善/恶）
2. **语法信息** — 语言形式化表达（我们不关心）

两者混合导致相反词（如"好-坏"）显示**高相似度**，这与直觉矛盾。

## 解决方案：语用空间分析

分离出**语用空间**，在语用空间中，相反词显示**负相似度**（方向相反）。

## 语用轴定义

| 语用轴 | 正向极 | 负向极 | 理论定义 |
|--------|--------|--------|----------|
| 价值轴 | 好 | 坏 | 好=效率 |
| 真值轴 | 对 | 错 | 对=完备 |
| 道德轴 | 善 | 恶 | 善=合作 |
| 美学轴 | 美 | 丑 | 美=效率 |

## 配置文件

每个定律配置 (`laws/law*.yaml`) 包含：

```yaml
name: 完备即正确
theory: 任何正确不允许任何遗漏
positive_pairs: [[完备, 正确]]
opposite_pairs: [[完备, 不完备]]
pragmatic_axes:
  价值轴:
    pos_words: [好, 优秀]
    neg_words: [坏, 差]
thresholds:
  positive_similarity: 0.5
  opposite_pragmatic: -0.3
```

## 添加新定律

创建 `laws/law6.yaml` 后运行：

```bash
python geometry.py --task law --law law6
```

## 参考

- [THEORY.md](THEORY.md) — 详细验证结果
- [../zh/GLOSSARIES-FULL.md](../zh/GLOSSARIES-FULL.md) — 术语定义