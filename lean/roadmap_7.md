# The Principle — Roadmap

> 版本：v7 配套路线图  
> 状态：v7 骨架已产出，待编译验证与开源  
> 原则：诚实标注。不宣称“哥德尔已解决”，不宣称“统一科学已兑现”。

---

## 0. 当前状态

v7 已具备：

- 8 条公理中的 0、2、3、5、7 已作为 `Env` 字段形式化，可由具体模型逐条验证。
- 边界幂等、四元组互斥（物质/意识、经验/形式）已形式化。
- 认识论四元组：自由 / 秩序 / 奴役 / 放任。
- 文化实践四元组：科学 / 哲学 / 宗教 / 工程。
- 科学四元组：自然科学 / 社会科学 / 数学 / 元科学。
- 民主四元组：民主 / 民粹 / 专制 / 独裁。
- 正义：`Just`（局部科斯）、`JustBetween`（系统间）、`JusticeDegree`。
- 意义：`Price` / `Meaning`。
- 剪枝：`ShouldPrune`。
- 两个一致性模型：`canonicalEnv`（退化）与 `nontrivialEnv`（非平凡，两系统两时间）。
- 哥德尔框架 `Gödel.FormalSystem` 与开放猜想 `HilbertProcessConjecture`。

v7 尚未具备：

- 实际编译验证与 CI。
- 每条公理“删除后反例”的必要性证明。
- 哥德尔进程的实质推进（仅有猜想骨架）。
- 原理自指（元科学）的形式化。
- 应用层（LLM、经济学、数学、孪生市场）的 Lean 接口。

---

## 1. 路线图总览

| 层级 | 代号 | 主题 | 时间 | 优先级 |
|---|---|---|---|---|
| 工程收尾 | A | 编译、CI、文档 | 1–2 天 | P0 |
| 形式化加强 | B | 非平凡模型、反例搜索、补齐定义 | 1–2 周 | P1 |
| 哥德尔进程 | C | 希尔伯特进程、哥德尔世界极小化 | 1–2 月 | P2 |
| 原理自指 | D | 元科学、域外执法、可信任演绎 | 1–2 月 | P3 |
| 纲领推进 | E | LLM、经济学、数学、孪生市场 | 持续 | P4 |
| 发布协作 | F | 开源、征集反例、工程报告 | 持续 | P5 |

---

## 2. A — 工程收尾（P0）

### A.1 编译通过

- **目标**：`lake build` 零错误。
- **动作**：
  - 补 `import Mathlib.Tactic`（`omega`、`norm_num`、`simp` 所需）。
  - 检查 `canonicalEnv` 中 `axiom_5_coase := by intro _ _ _; trivial` 是否关闭目标。
  - 用 `#print axioms` 确认无意外依赖。
- **验收**：`lake build` 成功，无 `sorry`，无 `admit`。

### A.2 CI

- **目标**：每次提交自动编译。
- **动作**：GitHub Actions + `leanprover/lean-action`。
- **验收**：PR 上出现绿色 check。

### A.3 文档化

- **目标**：仓库自解释。
- **动作**：
  - `README.md`：公理表、已形式化/未形式化清单、编译方法、提反例方法。
  - `docs/outline.md`：《事物原理纲要》原文。
  - `docs/formalization-map.md`：文本条目 ↔ Lean 定义对照表。
- **验收**：新人 30 分钟内能编译并找到任一公理对应的 Lean 代码。

---

## 3. B — 形式化加强（P1）

### B.1 非平凡模型扩展

- **目标**：每个四元组至少一个非平凡实例，不靠“另一构造子恒假”。
- **动作**：
  - `System := Fin 4`，覆盖四元组四个位置。
  - `Time := Fin 3`，让 `Knows` 随时间变化。
  - `TransactionCost` 用真实矩阵，验证 `justice_measurement_theorem` 非平凡成立。
- **验收**：`nontrivialEnv` 中 `Free`、`Order`、`Slavery`、`License` 各有实例；`Democracy`、`Populism`、`Autocracy`、`Dictatorship` 各有实例。

### B.2 反例搜索（公理必要性）

- **目标**：证明每条公理不是装饰。
- **动作**：为每条公理写“删除后”的模型：
  - 删 `material_conscious_exclusive` → 构造 `IsMaterial ∧ IsConscious` 同时为真的模型，证明互斥定理依赖它。
  - 删 `axiom_5_coase` → 构造 `PropertyRightsClear ∧ TC=0 ∧ ¬ParetoEfficient` 的模型。
  - 删 `axiom_7` → 构造描述长度更短的完全描述，证明最优性依赖它。
- **验收**：每条公理一个 `CounterexampleEnv` 文件，附定理“删除该公理后某定理不成立”。

### B.3 补齐原文未形式化项

- **目标**：缩小文本与 Lean 的差距。
- **动作**：
  - `Nonexistent` / `Wrong` 的实质语义（原文“不存在=错误”）。
  - `Credit` 作为“第一价值”的独立字段，而非 `JusticeDegree` 别名。
  - `Good = 协作`、`Beautiful = 竞争力` 的实质定义（需 `Cooperation`、`Competitiveness` 字段）。
  - “社会科学名义下极少是科学”作为统计性 `Prop`，标注“未证明”。
- **验收**：`docs/formalization-map.md` 中“未形式化”条目减少至少一半。

### B.4 `SelfReferring` 实质化

- **目标**：让 `self_reference_theorem` 有内容。
- **动作**：定义 `SelfReferring s := DescribesCompletely (Principle s) s ∧ ...` 的自指闭包。
- **验收**：`self_reference_theorem` 不再是裸公理，而是可从定义推出的定理，或明确标注为公理。

---

## 4. C — 哥德尔进程（P2）

### C.1 `HilbertProcessConjecture` 诚实化

- **动作**：
  - 加基数条件注释：`embed` 单射要求 `HilbertCore S` 基数 ≥ 哥德尔句子集基数。
  - 在具体 `FormalSystem`（如命题逻辑、简化 PA）上构造 `embed`，哪怕有限片段。
- **验收**：至少一个具体 `FormalSystem` 上 `HilbertProcessConjecture` 的有限版本被证明。

### C.2 “哥德尔世界极小化”形式化

- **动作**：
  - `GödelWorld S := {φ | IsGödel S φ}`。
  - `HilbertWorld S := HilbertCore S`。
  - 猜想 `G/H → 0` 写成“存在嵌入使哥德尔句子被可证/可反驳句子覆盖，覆盖比例趋于 1”。
- **验收**：独立文件 `Principle/Godel/Minimization.lean`，含定义、猜想、有限片段定理。

### C.3 与 `Env` 的接口

- **动作**：证明若 `Env` 中某系统编码 `FormalSystem`，则 `Correct` 对应 `HilbertCore` 覆盖。
- **验收**：定理 `env_correct_iff_hilbert_core`，连接“科学原理必须绝对正确”与哥德尔框架。

---

## 5. D — 原理自指（P3）

### D.1 原理检验自身

- **动作**：把 `Env` 本身视为 `System`，问 `Principle Env` 是否 `DescribesCompletely`。
- **验收**：`MetaConsistency : Prop`，诚实标注“开放”。

### D.2 域外执法定理

- **动作**：形式化 `¬ Correct s t → ¬ GovernedByPrinciple s t`，检查与 `axiom_2` 是否冲突。
- **验收**：定理或反例，二者之一。

### D.3 可信任演绎必须基于公理

- **动作**：`TrustworthyDeduction s → TraceableToAxioms s`，作为公理或定理。
- **验收**：明确其地位（公理/定理/猜想）。

---

## 6. E — 纲领推进（P4）

### E.1 LLM（原理 SFT 语料）

- **动作**：把公理、四元组、定理写成 JSONL SFT 数据；用 v7 Lean 定义作金标准生成问答对。
- **验收**：`data/sft/` 至少 200 条，含 Lean 代码 + 自然语言双模态。

### E.2 经济学（原子效用论）

- **动作**：定义 `Utility : System → ℝ`，把 `axiom_5_coase` 与 `justice_measurement_theorem` 接到效用函数。
- **验收**：科斯定理在 `Env` 公理下成为定理而非假设。

### E.3 数学（希尔伯特进程）

- **动作**：见 C.2。先做命题逻辑 `FormalSystem`，构造 `embed` 并证明单射。
- **验收**：`Principle/Applications/Logic.lean` 编译通过。

### E.4 孪生市场模型

- **动作**：两个 `Env` 实例（市场 A/B），`TransactionCost` 矩阵模拟，验证 `JusticeDegree` 排序。
- **验收**：`Principle/Applications/Market.lean`，含非平凡排序定理。

---

## 7. F — 发布协作（P5）

### F.1 仓库结构
