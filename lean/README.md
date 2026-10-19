# The Principle in Lean 4 / 事物原理的 Lean 4 形式化

本项目是《事物原理》（The Principle）在交互式定理证明器 **Lean 4** 中的形式化规范工程。

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

- **[ThePrinciple.lean](ThePrinciple.lean)**：核心形式化源码（**Zero sorry** 完整闭合规范，全英文注释 Canonical 集大成版本，`lake build` 的库根模块）
  - **基础载体与态射**：状态（State）、边界（Boundary）、系统（System）、边界自指映射（`boundaryOf`）、跨界（Crossing）、时序演化赋值（`valuationAt`）；
  - **八大公理规制（Axioms 0–7）**：
    - 公理 0（存在即差异）：以 `Differs` 谓词严格界定内部相异状态对的存在性；
    - 公理 1（正确即完备）：全状态赋值，定义非存在即错误；
    - 公理 2（事物趋完备）：单调弱读法 + 极限强读法，并严格证明 `exists_correct_time`；
    - 公理 3（博弈即动荡）：动荡内生化为边界变动、信息阻塞与少数者博弈，并证明推论；
    - 公理 4（自由即无知）：内部完备且外部保持开放；
    - 公理 5（正义即效率）：科斯产权风格（`PropertyRightsClear` + 零交易成本 $\implies$ 帕累托最优），严格证明 `coase_implies_just`；
    - 公理 6（意义即价格）：跨界价格恒等于成本与竞争之和；
    - 公理 7（原理即最优）：最小描述长度（MDL）/ 奥卡姆剃刀；
  - **二元概念空间（BCS / Binary Concept Space）与全面定义**：
    - 不存在即错误（`nonexistent_iff_incorrect`）；
    - 边界的自指闭包（`boundary_of_boundary_is_boundary`）；
    - 认知四元组：自由（`Free`）/ 秩序（`Order`）/ 奴役（`Slavery`）/ 放任（`License`）；
    - 社会政治四元组：民主（`Democracy`）/ 民粹（`Populism`）/ 专制（`Autocracy`）/ 独裁（`Dictatorship`）；
    - 文化实践四元组：科学（`Science`）/ 宗教（`Religion`）/ 工程（`Engineering`）/ 哲学（`Philosophy`）；
    - 科学分支四元组：自然科学（`NaturalScience`）/ 社会科学（`SocialScience`）/ 数学（`Mathematics`）/ 元科学（`MetaScience`）；
    - 评价二元对：对与错（`Right`/`Wrong`）、好与坏（`Good`/`Bad`）、真善美（`Truth`/`Goodness`/`Beauty`）；
    - 主观与客观：评价分歧度（`Subjective`/`Objective`）；
  - **全套基础定理与宪法级定律**：
    - 边界定理（`boundary_theorem`）、自指定理（`self_reference_theorem`）、绝对真理定理（`absolute_truth_theorem`）；
    - 叠加定理（`superposition_theorem`）、剪枝定理（`pruning_theorem`）、自私定理（`selfish_theorem`）、理性定理（`rationality_theorem`）；
    - 博弈定理（`game_theorem`）、第一价值（信用）定理（`first_value_is_credit`）、正义测量定理（`justice_measurement_theorem`）；
    - 民主权力定理（`democracy_is_power`）、域外执法定理（`extraterritoriality_theorem`）、黑格尔定理（`hegel_theorem`）；
    - 爱智慧四定律（哲学批判）：罗素边界定律（`russell_boundary_law`）、自由定律（`philosophical_freedom_law`）、民主定律、专制定律；
    - 达尔文边界原理（`darwinian_boundary_principle`）与可信演绎公理化；
    - 科学宪法六定律：真理定律、承诺定律（`law_of_scientific_commitment`）、永恒定律、体系强一致定律、演绎定律、世俗定律；
  - **公理一致性定理（`axioms_consistent`）**：构造一阶模型 `trivialModel`（State = Bool），在数学上严格证明全部公理与规范相容一致；
  - **`FormalDeduction` 命名空间**：
    - `systemValuation_ne_unassigned_iff`：追查判据等价定理（已判定 $\iff$ 可证 $\lor$ 可驳）；
    - `undecided_iff_not_in_hilbert_core`：未判定命题与离开希尔伯特核心的充要等价；
    - `godel_sentence_not_in_hilbert_core`：严格引理，哥德尔独立命题不属于希尔伯特核心；
    - `counterexample_breaks_consistency`：核心反例元定理，证明任何追查到公理的域内反例（`Challenge`）必致体系一致性瓦解（$S \vdash \bot$），兑现“一个反例即可证伪”的法庭承诺；
    - `HilbertProcessConjecture`：学术诚实界定，将测度意义上的 $G/H \to 0$ 希尔伯特进程形式化为开放猜想。
- **[lakefile.toml](lakefile.toml)**：Lake 构建配置文件，声明对 `mathlib` 的依赖；
- **[lean-toolchain](lean-toolchain)**：工具链版本锁定（`leanprover/lean4:v4.35.0`）。

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
lake update
lake build
```

---

## 参考文献与背景记录

- [ChatGPT 研讨记录 1](https://chatgpt.com/share/6aa94cb2-0f50-83ec-aae5-d7360d906273)
- [ChatGPT 研讨记录 2](https://chatgpt.com/share/6aa9566d-b95c-83ec-b04f-6277ed069c71)
- [ChatGPT 研讨记录 3](https://chatgpt.com/share/6aa956a0-7ee4-83ec-a79d-07604c83029d)
- [ChatGPT 研讨记录 4](https://chatgpt.com/share/6aaa8067-9ce4-83ec-bf68-5ed5986acb4e)
- [arXiv:2609.13780](https://arxiv.org/abs/2609.13780)
- [DeepSeek 研讨记录](https://chat.deepseek.com/share/x6to7t8yefs6xuw6km)

## 构建与验证

前置：[elan](https://github.com/leanprover/elan)（Lean 工具链管理器）。工具链与 mathlib 版本已分别锁定在 `lean-toolchain`（v4.35.0）与 `lakefile.toml`（`rev = "v4.35.0"`）。

```bash
lake update              # 拉取依赖并生成 lake-manifest.json（首次必跑）
lake exe cache get       # 下载 mathlib 预编译缓存（数 GB，一次性）
lake build               # 编译库根模块 ThePrinciple.lean
lake env lean ThePrinciple.lean   # 或单独类型检查该文件
```

当前状态：`ThePrinciple.lean` **0 错误 / 0 警告 / 0 sorry**（mathlib v4.35.0 实测通过）。
`the-principle-2/3/4.lean` 为历史迭代稿，不参与构建，未随正典版同步修复。
