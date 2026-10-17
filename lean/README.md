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

- **[the-principle.lean](the-principle.lean)**：核心形式化源码（**Zero sorry** 完整闭合规范）
  - **基础载体**：状态（State）、边界（Boundary）、系统（System）、跨界（Crossing）、时序演化赋值（`valuationAt`）；
  - **八大公理规制**：存在公理（0）、正确公理（1）、意图公理（2，双层读法 + 极限趋完备定理 `exists_correct_time`）、博弈公理（3）、自由公理（4）、正义公理（5）、意义公理（6）、最优公理（7，MDL）；
  - **`FormalDeduction` 命名空间**：将元科学公理实例化规制形式演绎系统，包含严格证明的定理与元定理：
    - `undecided_sentence_refutes_correctness`：证明包含不可判定命题的理论在第一公理下必为 $\neg \text{Correct}$；
    - `hilbert_process_restores_correctness`：证明通过边界约束收缩至希尔伯特核心，理论恢复正确性；
    - `theoryValuation_ne_unassigned_iff`：追查判据的可操作化等价定理（已判定 $\iff$ 可证 $\lor$ 可驳）；
    - `theoryCorrect_iff_domain_traceable`：元语句机械化，证明理论正确性等价于域内全命题可追查；
    - `domain_counterexample_breaks_consistency`：核心反例元定理，证明任何追溯到公理的域内反例（`Challenge`）必致体系一致性瓦解（$T \vdash \bot$），兑现“一个反例即可证伪”的法庭承诺。
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
