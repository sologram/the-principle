# 概念几何分析工具

语义空间分析工具，用于验证事物原理六大定律。提供两个版本：

- **geometry.py** — 手动定义语义轴版本（v2.3）
- **geometry4.py** — 自动发现语义轴版本（v4.0，推荐）

## 快速开始

### v4.0 自动发现版本（推荐）

```bash
# 完整分析
python geometry4.py --task all

# 仅学习语义轴
python geometry4.py --task learn

# 仅验证反向词对
python geometry4.py --task opposites

# 仅验证定律
python geometry4.py --task verify
```

### v2.3 手动定义版本

```bash
# 完整分析
python geometry.py --task all

# 验证单个定律
python geometry.py --task law1
```

## 版本对比

| 特性 | v2.3 (geometry.py) | v4.0 (geometry4.py) |
|------|-------------------|---------------------|
| 语义轴来源 | 手动定义 | 从反向词对自动学习 |
| 验证方法 | 单一语义相似度 | 多方法组合（余弦、投影、角度） |
| 反向词对验证率 | 0-33% | **89%** |
| 定律验证通过 | 0/6 | **6/6** |
| 轴数量 | 固定4个 | 可配置（默认8个） |

## v4.0 命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--model` | str | `infoxlm-large` | 语言模型 |
| `--layer` | str | `0` | 提取层 |
| `--task` | str | `all` | 分析任务 |
| `--n-axes` | int | `8` | 学习的语义轴数量 |

### v4.0 任务类型

| 值 | 说明 |
|----|------|
| `learn` | 从反向词对学习语义轴 |
| `opposites` | 验证反向词对 |
| `positives` | 验证正向词对 |
| `verify` | 验证全部定律 |
| `all` | 完整分析流程 |

## v4.0 验证方法

使用三种方法组合验证反向词对：

1. **余弦相似度**：语义空间中相似度 < -0.3
2. **投影分离**：最佳轴上投影分离 > 0.5
3. **角度法**：语义空间中角度 > 90°

判定标准：至少两种方法通过。

## v4.0 输出示例

### 语义轴学习

```
Learning 8 semantic axes from 18 opposite pairs...

Learned Semantic Axes (Contrastive Learning)
======================================================================

无知-知识轴 (Explained Variance: 14.06%)
  Direction learned from opposite pairs

自由-奴役轴 (Explained Variance: 10.01%)
  Direction learned from opposite pairs

存在-虚无轴 (Explained Variance: 9.81%)
  Direction learned from opposite pairs
...
```

### 反向词对验证

```
真实-虚假: PASS
  Cosine: -0.026 ✗
  Projection: -1.276 (轴4) ✓
  Angle: 91.5° ✓

存在-虚无: PASS
  Cosine: -0.843 ✓
  Projection: 5.701 (轴1) ✓
  Angle: 147.4° ✓
```

### 定律验证

```
law0: 存在即信息
  Positive: 100%
  Opposite: 100%
  Total: 100% - verified

law1: 完备即正确
  Positive: 100%
  Opposite: 67%
  Total: 86% - verified
...
```

## 配置文件

定律配置位于 `laws/law*.yaml`：

```yaml
name: 完备即正确
theory: 任何正确不允许任何遗漏

positive_pairs:
  - [完备, 正确]
  - [确定, 客观]

opposite_pairs:
  - [完备, 不完备]
  - [正确, 错误]
```

### 配置项说明

| 字段 | 说明 |
|------|------|
| `name` | 定律名称 |
| `theory` | 理论陈述 |
| `positive_pairs` | 正向词对（应在原始空间中相似） |
| `opposite_pairs` | 对立词对（应在语义空间中方向相反） |

**注意**：v4.0 不需要 `semantic_axes` 和 `thresholds` 字段，语义轴从 `opposite_pairs` 自动学习。

## 验证状态

| 状态 | 验证率 | 说明 |
|------|--------|------|
| `verified` | ≥ 75% | 理论得到强支持 |
| `partial` | 50% - 74% | 部分支持 |
| `not supported` | < 50% | 未获得支持 |

## 模型配置

内置模型路径（Windows）：

| 模型名 | 路径 |
|--------|------|
| `qwen3.5-9b` | `C:\Users\hans\Desktop\models\qwen3.5-9b` |
| `infoxlm-large` | `C:\Users\hans\Desktop\models\infoxlm-large` |
| `qwen2.5-7b-instruct` | `C:\Users\hans\Desktop\models\qwen2.5-7b-instruct` |
| `bert-base-chinese` | HuggingFace 自动下载 |

## 参考

- [geometry.md](geometry.md) — 算法原理详解
- [THEORY.md](THEORY.md) — 实验结果与分析
- [../zh/GLOSSARIES-FULL.md](../zh/GLOSSARIES-FULL.md) — 术语定义