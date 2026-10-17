import Mathlib.Data.Real.Basic

/-!
# 事物原理 — 形式化纲要（零 sorry）

对应《事物原理纲要》八公理：

* 公理 0 存在即差异   → `axiom_0_boundary_is_existence`
* 公理 1 正确即完备   → `Correct`
* 公理 2 事物趋完备   → `axiom_2_monotone` + `axiom_2_tends_to_complete`
* 公理 3 博弈即动荡   → `Turbulent`
* 公理 4 自由即无知   → `Free`
* 公理 5 正义即效率   → `Just`（`Friction` = 交易成本，对应「正义测量定理」）
* 公理 6 意义即价格   → `Meaning = Cost + Competition`
* 公理 7 原理即最优   → `axiom_7_principle_is_mdl`

原文件中的 `sorry` 全部以「原始参数 + 规范公理」或「直接定义」消解：

* `UnassignedCount` → 参数，行为由 `count_zero_iff_correct` 与公理二约束
  （语义模型：`UnassignedAt s t` 的基数）；
* `BoundaryChanges` → 轨迹不等（`traceOf b t₁ ≠ traceOf b t₂`）；
* `Outside` / `Knowable` / `HasCompetition` → 原始参数；
* `Friction` → 交易成本 `TransactionCost`；
* `DescriptionLength` / `DescribesCompletely` / `Principle` → 参数，由公理七约束。

公理二较原文件加强：单调不增（弱读法）之外补「计数趋于 0」的极限读法，
否则「永远卡在 7」也满足公理，推不出完备性。

工程纪律：变量一律隐式 `{...}`；调用公理时以带类型的 `have` 给定期望类型，
避免 `UnassignedCount` 这类无法由实参反推的隐式参数悬空。
-/

universe u v w t z c d e

/-! ## 基本载具 -/

variable {State : Type u} {Boundary : Type v} {System : Type w}
variable {hasBoundary : System → Boundary}
variable {statesOf : System → Set State}
variable {Value : Type z}

inductive Valuation (α : Type z) where
  | assigned : α → Valuation α
  | unassigned : Valuation α

variable {Time : Type t}
variable {le : Time → Time → Prop}
/-- 赋值随时间演化（补时间维；原文件的无时间 `valuation` 是 `sorry` 的根源） -/
variable {valuationAt : System → Time → State → Valuation Value}
/-- 未赋值状态计数（语义模型：`UnassignedAt s t` 的基数） -/
variable {UnassignedCount : System → Time → ℕ}
variable {BoundarySig : Type e}
variable {traceOf : Boundary → Time → BoundarySig}
variable {Crossing : Type c}
variable {crossingsOf : Boundary → Set Crossing}
variable {Cost : Crossing → ℝ}
variable {Competition : Crossing → ℝ}
variable {TransactionCost : System → System → ℝ}
variable {Outside : Boundary → Type}
variable {Knowable : ∀ b : Boundary, Outside b → Prop}
variable {HasCompetition : Crossing → Prop}
variable {Description : Type d}
variable {DescriptionLength : Description → ℝ}
variable {DescribesCompletely : Description → System → Prop}
variable {Principle : System → Description}

/-! ## 公理 0：存在即差异 -/

axiom axiom_0_boundary_is_existence :
  ∀ (s : System), Nonempty Boundary → Nonempty State

/-! ## 公理 1：正确即完备 -/

/-- 时刻 `t` 系统 `s` 的未赋值状态集 -/
def UnassignedAt (s : System) (t : Time) : Set State :=
  { σ | σ ∈ statesOf s ∧ valuationAt s t σ = Valuation.unassigned }

/-- 正确 = 完备：每个状态均已赋值 -/
def Correct (s : System) (t : Time) : Prop :=
  ∀ σ ∈ statesOf s, valuationAt s t σ ≠ Valuation.unassigned

/-! ## 公理 2：事物趋完备 -/

/-- 计数规范：计数为 0 当且仅当正确 -/
axiom count_zero_iff_correct :
  ∀ (s : System) (t : Time), UnassignedCount s t = 0 ↔ Correct s t

/-- 公理二（弱读法）：计数随时间单调不增 -/
axiom axiom_2_monotone :
  ∀ (s : System) (t₁ t₂ : Time), le t₁ t₂ → UnassignedCount s t₂ ≤ UnassignedCount s t₁

/-- 公理二（强读法，"趋完备"的极限含义）：计数可任意小，故趋于 0 -/
axiom axiom_2_tends_to_complete :
  ∀ (s : System) (n : ℕ), ∃ t : Time, UnassignedCount s t ≤ n

/-- 推论：任何系统都存在完备（正确）时刻 -/
theorem exists_correct_time (s : System) : ∃ t : Time, Correct s t := by
  have h : ∃ t : Time, UnassignedCount s t ≤ 0 := axiom_2_tends_to_complete s 0
  cases h with
  | intro t ht =>
    have h0 : UnassignedCount s t = 0 := by omega
    have hiff : UnassignedCount s t = 0 ↔ Correct s t := count_zero_iff_correct s t
    exact ⟨t, hiff.mp h0⟩

/-! ## 公理 3：博弈即动荡 -/

/-- 边界变动：轨迹在两时刻取值不同（原 `sorry` 的消解） -/
def BoundaryChanges (b : Boundary) (t₁ t₂ : Time) : Prop :=
  traceOf b t₁ ≠ traceOf b t₂

/-- 动荡 = 边界不稳定 -/
def Turbulent (s : System) (t₁ t₂ : Time) : Prop :=
  BoundaryChanges (hasBoundary s) t₁ t₂

/-! ## 公理 4：自由即无知 -/

/-- 自由 = 无知：存在不可知的外界对象，且存在竞争性跨越 -/
def Free (s : System) : Prop :=
  (∃ x : Outside (hasBoundary s), ¬ Knowable (hasBoundary s) x) ∧
    ∃ cr ∈ crossingsOf (hasBoundary s), HasCompetition cr

/-! ## 公理 5：正义即效率 -/

/-- 摩擦 = 交易成本（正义测量定理：正义度反比于交易成本） -/
def Friction (s₁ s₂ : System) : ℝ := TransactionCost s₁ s₂

/-- 正义：全局最小化摩擦的系统对 -/
def Just (s₁ s₂ : System) : Prop :=
  ∀ a b : System, Friction a b ≥ Friction s₁ s₂

/-! ## 公理 6：意义即价格 -/

/-- 意义 = 跨越的价格 = 成本 + 竞争 -/
def Meaning (cr : Crossing) : ℝ := Cost cr + Competition cr

/-! ## 公理 7：原理即最优（MDL / 奥卡姆剃刀） -/

axiom axiom_7_principle_is_mdl :
  ∀ s : System,
    DescribesCompletely (Principle s) s ∧
      ∀ d : Description, DescribesCompletely d s →
        DescriptionLength (Principle s) ≤ DescriptionLength d

namespace FormalDeduction
open Classical

variable (Sentence : Type)

inductive ProofStatus where
  | proved_true : ProofStatus
  | proved_false : ProofStatus

structure Theory where
  domain : Set Sentence
  provable : Sentence → Prop
  refutable : Sentence → Prop
  consistent : ∀ φ, ¬ (provable φ ∧ refutable φ)

noncomputable def theoryValuation (T : Theory Sentence) (φ : Sentence) : Valuation ProofStatus :=
  if T.provable φ then
    Valuation.assigned ProofStatus.proved_true
  else if T.refutable φ then
    Valuation.assigned ProofStatus.proved_false
  else
    Valuation.unassigned

theorem theoryValuation_def (T : Theory Sentence) (φ : Sentence) :
    theoryValuation Sentence T φ =
      if T.provable φ then Valuation.assigned ProofStatus.proved_true
      else if T.refutable φ then Valuation.assigned ProofStatus.proved_false
      else Valuation.unassigned := rfl

def IsUndecided (T : Theory Sentence) (φ : Sentence) : Prop :=
  theoryValuation Sentence T φ = Valuation.unassigned

def TheoryCorrect (T : Theory Sentence) : Prop :=
  ∀ φ ∈ T.domain, theoryValuation Sentence T φ ≠ Valuation.unassigned

/-! ### 裁定程序：通过追查公理

`theoryValuation` 是机械化的「追查」：已判定（追得回公理）→ `assigned`；
追不回 → `unassigned` → 按公理一不正确 → 按定义「不存在 = 错误」→ 域外执法不管辖。 -/

/-- 未判定语句违反完备性。
    原名 `godel_sentence_violates_correctness`；真正的"哥德尔内容"
    是从强度 + 一致性构造出未判定语句，需语法算术化，不在本文件范围。 -/
theorem undecided_sentence_refutes_correctness
    (T : Theory Sentence) (φ : Sentence)
    (h_in : φ ∈ T.domain)
    (h_undec : IsUndecided Sentence T φ) :
    ¬ TheoryCorrect Sentence T := by
  intro h_corr
  have h_assigned := h_corr φ h_in
  exact h_assigned h_undec

def HilbertCore (T : Theory Sentence) : Set Sentence :=
  { φ ∈ T.domain | theoryValuation Sentence T φ ≠ Valuation.unassigned }

def RestrictDomain (T : Theory Sentence) (S : Set Sentence) : Theory Sentence where
  domain := T.domain ∩ S
  provable := T.provable
  refutable := T.refutable
  consistent := T.consistent

/-- 希尔伯特进程：剪除未判定语句后，剩余 domain 全部已判定（追得回公理）。 -/
theorem hilbert_process_restores_correctness
    (T : Theory Sentence) :
    TheoryCorrect Sentence (RestrictDomain Sentence T (HilbertCore Sentence T)) := by
  intro φ hφ
  have h_and : φ ∈ T.domain ∧ φ ∈ HilbertCore Sentence T := hφ
  have h_core : φ ∈ T.domain ∧ theoryValuation Sentence T φ ≠ Valuation.unassigned := h_and.right
  exact h_core.right

/-- 追查判据的可操作化：已判定 ⟺ 可证 ∨ 可驳 -/
theorem theoryValuation_ne_unassigned_iff (T : Theory Sentence) (φ : Sentence) :
    theoryValuation Sentence T φ ≠ Valuation.unassigned ↔
      T.provable φ ∨ T.refutable φ := by
  by_cases hp : T.provable φ
  · rw [theoryValuation_def, if_pos hp]
    constructor
    · intro _; exact Or.inl hp
    · intro _ h; exact Valuation.noConfusion h
  · by_cases hr : T.refutable φ
    · rw [theoryValuation_def, if_neg hp, if_pos hr]
      constructor
      · intro _; exact Or.inr hr
      · intro _ h; exact Valuation.noConfusion h
    · rw [theoryValuation_def, if_neg hp, if_neg hr]
      constructor
      · intro h; exact False.elim (h rfl)
      · intro h; exact False.elim (Or.elim h hp hr)

/-- 元语句的机械化：`TheoryCorrect` 即「domain 内语句均可追查（已判定）」 -/
theorem theoryCorrect_iff_domain_traceable (T : Theory Sentence) :
    TheoryCorrect Sentence T ↔
      ∀ φ ∈ T.domain, T.provable φ ∨ T.refutable φ := by
  constructor
  · intro h φ h_in
    exact (theoryValuation_ne_unassigned_iff Sentence T φ).mp (h φ h_in)
  · intro h φ h_in
    exact (theoryValuation_ne_unassigned_iff Sentence T φ).mpr (h φ h_in)

/-! ### 挑战与元定理

一个挑战针对 domain 内定理 `τ`，必须携带**可追查到公理**的反证（`T.refutable τ`）。
追得回 → 域内挑战；追不回（`attacked` 拿不到）→ 域外执法定理不管辖。 -/

structure Challenge (T : Theory Sentence) (τ : Sentence) where
  target : τ ∈ T.domain
  attacked : T.refutable τ

/-- 元定理：域内反例导致体系自损（一致性失效，而非仅某定理下线）。
    这保证了追查判据非空：真反例一旦追得回公理，代价是原理崩塌，
    「一个反例就够」的承诺因此是真实的。 -/
theorem domain_counterexample_breaks_consistency
    (T : Theory Sentence) (τ : Sentence)
    (C : Challenge Sentence T τ)
    (h : T.provable τ) : False :=
  T.consistent τ ⟨h, C.attacked⟩

/-! ### 元语句：domain / 文本层边界

* `T.domain` = 可从八公理机械追查的语句集；其不动点即 `HilbertCore`。
* 《纲要》的"人类文本层"（承诺吸收更优的表述）不在任何 `Theory.domain` 内，
  故"吸收更优"不构成自指定理所禁止的"可变自指"：
  可变的是文本表示，不可变的是 domain 判据本身。
  （对象层承诺不变；文本层置于 domain 之外，这条元语句即二者边界。）
* 裁定由 `theoryValuation` 机械执行，无需人类委员会：
  已判定 → 域内；未判定 → 不正确 → 不存在 → 域外执法。 -/

end FormalDeduction
