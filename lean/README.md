# The Principle in Lean 4 / 事物原理的 Lean 4 形式化

本项目是《[事物原理](../zh/outline.md)》（The Principle）在交互式定理证明器 **Lean 4** 中的形式化规范工程。

事物原理在此并非作为传统数学的分支或内部演绎体系存在，而是作为**元科学层的规范体系（Normative System / Specification）**，为包括数学形式演绎系统在内的全域系统确立宪法级的规制标准（法庭判准）。

---

## 核心架构与定位

1. **规范体系 vs 演绎体系**：
   - 传统数学（如 ZFC 或一阶逻辑）只关注推理规则的合式性与保真性，将哥德尔不完备等不可判定状态视为客观不可避免的局限；
   - 事物原理确立**法庭判准**：“A 即 B”是终极衡量标尺（正确即完备、正义即效率、意义即价格……）。形式系统若容忍悬空不可判定的独立命题，依法直接裁定为违规（$\neg \text{Correct}$）。

2. **希尔伯特进程与哥德尔世界极小化**：
   - 形式系统不能以“不完备”为由逃避正确性责任；
   - 依据**边界定理**与**达尔文边界原理**，系统必须启动“希尔伯特进程”，重新划定管辖域，剪除不可赋值的哥德尔域 $G$，在纯净的希尔伯特核心 $H$ 上依法恢复完备与正确。

---

## 文件结构

### 正典（参与构建）

- **[the_principle.lean](the_principle.lean)**：**唯一的正典形式化源码**，`lake build` 的库根模块（`lakefile.toml` 中 `defaultTargets = ["the_principle"]`）。
  - 采用 Lean 模块系统（文件头 `module`，导入为 `public import`），下游可直接 `import the_principle` 使用其公开 API。
  - **基础载体与态射**：
    - `Valuation`（赋值 / 未赋值）、`Env`（完整环境：数据载体 + 公理约束）；
    - 状态（`State`）、边界（`Boundary`）、系统（`System`）、时间（`Time`）、跨界（`Crossing`）、描述（`Description`）；
    - 边界自指映射（`boundaryOf`）、跨界集合（`crossingsOf`）、时序演化赋值（`valuationAt`）、知识算子（`Knows`）。
  - **公理字段（作为 `Env` 的字段，可由具体模型逐条验证）**：
    - 公理 0（存在即差异）：`axiom_0`；
    - 公理 1（正确即完备）：`count_zero_iff_correct`（`UnassignedCount = 0` ⟺ 全状态已赋值）；
    - 公理 2（事物趋完备）：`axiom_2_monotone`（单调）+ `axiom_2_tends_to_complete`（极限）；
    - 公理 3（博弈即动荡）：`turbulence_from_information_blocking`（信息阻塞 + 少数者博弈 ⟹ 边界变动）；
    - 公理 5（正义即效率）：`axiom_5_coase`（科斯产权风格：产权清晰 + 零交易成本 ⟹ 帕累托最优）；
    - 公理 7（原理即最优）：`axiom_7`（MDL / 奥卡姆剃刀）；
    - 边界幂等：`axiom_boundary_idempotent`；
    - 四元组互斥：`material_conscious_exclusive`、`empirical_formal_exclusive`；
    - 正义测量：`justice_measurement_theorem`（系统间摩擦越小，正义度越高）；
    - 自指定理：`self_reference_theorem`（仅约束自指系统，避开与公理 2 的冲突）；
    - 科学不变性：`law_of_scientific_invariance`；科学世俗：`law_of_secular_science`。
  - **二元概念空间（BCS / Binary Concept Space）**：
    - 正确性：`Correct`；不存在即错误：`Nonexistent` / `Wrong`；
    - 认识论四元组：自由（`Free`）/ 秩序（`Order`）/ 奴役（`Slavery`）/ 放任（`License`），六条两两互斥定理（`free_order_exclusive` 等）；
    - 文化实践四元组：科学（`Science`）/ 宗教（`Religion`）/ 工程（`Engineering`）/ 哲学（`Philosophy`），三条互斥定理；
    - 科学分支四元组：自然科学（`NaturalScience`）/ 社会科学（`SocialScience`）/ 数学（`Mathematics`）/ 元科学（`MetaScience`），四条互斥定理；
    - 民主四元组：民主（`Democracy`）/ 民粹（`Populism`）/ 专制（`Autocracy`）/ 独裁（`Dictatorship`）；
    - 真善美：`Truthful` / `Good` / `Beautiful`；
    - 主观与客观：`Agree` / `Objective` / `Subjective`；
    - 信用：`Credit`。
  - **定理**：
    - 博弈定理（`game_theorem`）、正义定理（`coase_implies_just`、`justice_measurement_theorem'`）、剪枝定理（`pruning_incorrect`）；
    - 存在即错误、黑格尔定理（`HegelTheorem`，已移出 `Env` 以避免与 `LearnsFromHistory` 冲突）。
  - **一致性模型**：
    - `canonicalEnv`：退化模型（`Unit` 系统，`Knows = False`），用于快速逐条验证；
    - `nontrivialEnv`：**非平凡模型**（两系统 `true` / `false` × `ℕ` 时间，交易成本非对称 `TC true false = 1` < `TC false true = 2`，正义度 `1` / `0`）；
    - `axioms_consistent : Nonempty Env`（由 `nontrivialEnv` 见证）；
    - 非平凡性验证：`nontrivial_free_exists`、`nontrivial_order_exists`、`nontrivial_license_exists`、`nontrivial_democracy_exists`、`nontrivial_dictatorship_exists`、`nontrivial_free_not_order`。
  - **`Gödel` 命名空间**：
    - `FormalSystem`（公式 / 可证 / 可驳 / 一致性）、`ProofStatus`、`systemValuation`；
    - `IsGödel`、`HilbertCore`；
    - `godel_not_in_hilbert_core`：严格引理，哥德尔独立命题不属于希尔伯特核心（零公理依赖）；
    - `HilbertProcessConjecture`：学术诚实界定，将“哥德尔世界极小化”形式化为**开放猜想**（非已解决定理）。
- **[lakefile.toml](lakefile.toml)**：Lake 构建配置文件，声明对 `mathlib` 的依赖与库根模块 `the_principle`；
- **[lean-toolchain](lean-toolchain)**：工具链版本锁定（`leanprover/lean4:v4.35.0`）。

### 历史迭代稿（不参与构建）

以下文件为历史版本，**不随正典版同步修复**，仅作演进留档：

| 文件 | 说明 | 编译状态 |
|---|---|---|
| [the_principle_1.lean](the_principle_1.lean) | 前任正典：宪法级定律全量版（25 条 `axiom`、科学宪法六定律、`FormalDeduction` 命名空间、`counterexample_breaks_consistency`） | 0 错误（不含 `module` 头） |
| [the_principle_2.lean](the_principle_2.lean) | 早期骨架稿 | 9 错误 |
| [the_principle_3.lean](the_principle_3.lean) | 早期骨架稿 | 17 错误 |
| [the_principle_4.lean](the_principle_4.lean) | 早期骨架稿 | 42 错误 |
| [the_principle_5.lean](the_principle_5.lean) | 过渡稿 | 4 错误 |
| [the_principle_6.lean](the_principle_6.lean) | 过渡稿 | 8 错误 |
| [the_principle_7.lean](the_principle_7.lean) | v7 稿（[review_8.md](review_8.md) 的修复对象） | 26 错误 |

配套文档：

- [review_7.md](review_7.md)：v7 轮审查报告（漏检约 27 处证明级错误）；
- [review_8.md](review_8.md)：v8 轮审查报告（`the_principle_7.lean` 的 10 类修复清单；其修复成果已扶正为 [the_principle.lean](the_principle.lean)）；
- [roadmap_7.md](roadmap_7.md)：v7 配套路线图（A 工程收尾 / B 形式化加强 / C 哥德尔进程 / D 原理自指 / E 纲领推进 / F 发布协作）。

---

## 环境要求与构建

### 1. 安装工具链
确保系统已安装 `elan`（Lean 版本管理器）：
```bash
# macOS
brew install elan
```
进入本目录后，elan 会按 `lean-toolchain` 自动切换或下载对应的 Lean 4 版本。

### 2. 依赖管理与共享
为了避免多个 Lean 项目重复拉取庞大的 Mathlib 依赖（~185 MB 源码及 ~2-3 GB 预编译缓存），推荐建立全局共享池：
```bash
# 若首次建立共享目录
mkdir -p ~/.lean-shared/packages

# 在本工程的 .lake 目录下建立软链接
mkdir -p .lake
ln -s ~/.lean-shared/packages .lake/packages
```

### 3. 构建与验证
```bash
lake update              # 拉取依赖并生成 lake-manifest.json（首次必跑）
lake exe cache get       # 下载 mathlib 预编译缓存（数 GB，一次性）
lake build               # 编译库根模块 the_principle.lean
lake env lean the_principle.lean   # 或单独类型检查该文件
```

---

## 参考文献与背景记录

- [ChatGPT 研讨记录 1](https://chatgpt.com/share/6aa94cb2-0f50-83ec-aae5-d7360d906273)
- [ChatGPT 研讨记录 2](https://chatgpt.com/share/6aa9566d-b95c-83ec-b04f-6277ed069c71)
- [ChatGPT 研讨记录 3](https://chatgpt.com/share/6aa9566a-7ee4-83ec-a79d-07604c83029d)
- [ChatGPT 研讨记录 4](https://chatgpt.com/share/6aaa8067-9ce4-83ec-bf68-5ed5986acb4e)
- [arXiv:2609.13780](https://arxiv.org/abs/2609.13780)
- [DeepSeek 研讨记录](https://chat.deepseek.com/share/x6to7t8yefs6xuw6km)
