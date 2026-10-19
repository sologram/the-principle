import Mathlib.Data.Real.Basic
import Mathlib.Data.Set.Basic
import Mathlib.Data.Nat.Basic

/-!
# The Principle — Lean 4 Formalization v7

相对 v6 的关键修复：

1. `nomatch` 改为 `cases`，确保编译。
2. `axioms_consistent` 改为 `Nonempty Env`，由 `nontrivialEnv` 见证。
3. `ShouldPrune` 第二项改为 `Order`，不再恒假。
4. 新增 `JustBetween`，统一 `Just` 与 `justice_measurement_theorem` 的摩擦概念。
5. 新增非平凡模型 `nontrivialEnv`。
6. `hegel_theorem` 移出 `Env`，改为独立 `HegelTheorem`。
7. 新增 `SelfReferring` 字段，修复 `self_reference_theorem` 与 `axiom_2` 的潜在冲突。
8. 补充民主四元组、真善美、主观/客观、信用、不存在等定义。

## 已形式化

- 公理 0, 2, 3, 5, 7；边界幂等；四元组互斥。
- 认识论四元组：自由 / 秩序 / 奴役 / 放任。
- 文化实践四元组：科学 / 哲学 / 宗教 / 工程。
- 科学四元组：自然科学 / 社会科学 / 数学 / 元科学。
- 民主四元组：民主 / 民粹 / 专制 / 独裁。
- 正义：`Just`（局部科斯）、`JustBetween`（系统间）、`JusticeDegree`。
- 意义：`Price` / `Meaning`。
- 剪枝：`ShouldPrune`。
- 哥德尔框架与 `HilbertProcessConjecture`（开放猜想）。

## 未形式化（后续计划）

- “不存在 = 错误”的完整语义（仅给出 `Nonexistent` / `Wrong` 骨架）。
- “第一价值 = 信用”的实质内容（仅用 `JusticeDegree` 近似）。
- “社会科学名义下极少是科学”的统计性断言。
- “美 = 竞争力”的实质内容（仅用 `HasPower` 近似）。
- 原子效用论、孪生市场模型、原理 SFT 语料等工程计划。

诚实标注：本文件是骨架，不是“哥德尔已解决”，也不是“统一科学已兑现”。
-/

inductive Valuation (α : Type) where
  | assigned : α → Valuation α
  | unassigned : Valuation α

/-- 完整环境：数据载体 + 公理约束。 -/
structure Env where
  State : Type
  Boundary : Type
  System : Type
  Time : Type
  Value : Type
  BoundarySig : Type
  Crossing : Type
  Description : Type

  hasBoundary : System → Boundary
  boundaryOf : Boundary → Boundary
  statesOf : System → Set State
  le : Time → Time → Prop
  valuationAt : System → Time → State → Valuation Value
  UnassignedCount : System → Time → ℕ
  traceOf : Boundary → Time → BoundarySig
  crossingsOf : Boundary → Set Crossing
  Cost : Crossing → ℝ
  Competition : Crossing → ℝ
  TransactionCost : System → System → ℝ
  Knows : System → Time → State → Prop
  DescriptionLength : Description → ℝ
  DescribesCompletely : Description → System → Prop
  Principle : System → Description
  Differs : State → State → Prop
  InformationBlocked : System → Time → Prop
  MinorityGame : System → Prop
  PropertyRightsClear : System → Prop
  ParetoEfficient : System → Prop
  IsCollective : System → Prop
  IsIndividual : System → Prop
  HasCommitment : System → Prop
  HasFulfillment : System → Prop
  IsMaterial : System → Prop
  IsConscious : System → Prop
  IsEmpirical : System → Prop
  IsFormal : System → Prop
  Judgment : System → System → Prop
  HasPower : System → Prop
  GovernedByPrinciple : System → Time → Prop
  LearnsFromHistory : System → Prop
  MassIgnoranceAuthorization : System → Prop
  DialecticalEffectiveness : System → Prop
  DialecticianPower : System → Prop
  TraceableToAxioms : System → Prop
  TrustworthyDeduction : System → Prop
  Contradicts : System → System → Prop
  ChallengesScience : System → System → Prop
  InflictsPhysicalPunishment : System → System → Prop
  JusticeDegree : System → ℝ
  SelfReferring : System → Prop

  /- 公理 0：存在即差异 -/
  axiom_0 : ∀ (s : System), Nonempty Boundary →
    ∃ σ τ : State, σ ∈ statesOf s ∧ τ ∈ statesOf s ∧ Differs σ τ
  /- 公理 2：事物趋完备 -/
  count_zero_iff_correct : ∀ (s : System) (t : Time),
    UnassignedCount s t = 0 ↔
      ∀ σ ∈ statesOf s, valuationAt s t σ ≠ Valuation.unassigned
  axiom_2_monotone : ∀ (s : System) (t₁ t₂ : Time),
    le t₁ t₂ → UnassignedCount s t₂ ≤ UnassignedCount s t₁
  axiom_2_tends_to_complete : ∀ (s : System) (n : ℕ),
    ∃ t : Time, UnassignedCount s t ≤ n
  /- 公理 3：动荡源自信息阻塞 -/
  turbulence_from_information_blocking :
    ∀ (s : System) (t₁ t₂ : Time),
      InformationBlocked s t₁ → MinorityGame s →
        traceOf (hasBoundary s) t₁ ≠ traceOf (hasBoundary s) t₂
  /- 公理 5：正义即效率（Coase） -/
  axiom_5_coase : ∀ s : System,
    PropertyRightsClear s → TransactionCost s s = 0 → ParetoEfficient s
  /- 公理 7：原理即最优（MDL） -/
  axiom_7 : ∀ s : System,
    DescribesCompletely (Principle s) s ∧
      ∀ d : Description, DescribesCompletely d s →
        DescriptionLength (Principle s) ≤ DescriptionLength d
  /- 边界幂等 -/
  axiom_boundary_idempotent : ∀ b : Boundary,
    boundaryOf (boundaryOf b) = boundaryOf b
  /- 四元组互斥：物质/意识 -/
  material_conscious_exclusive :
    ∀ s : System, ¬ (IsMaterial s ∧ IsConscious s)
  /- 四元组互斥：经验/形式 -/
  empirical_formal_exclusive :
    ∀ s : System, ¬ (IsEmpirical s ∧ IsFormal s)
  /- 正义测量：系统间摩擦越小，正义度越高 -/
  justice_measurement_theorem :
    ∀ s₁ s₂ : System,
      TransactionCost s₁ s₂ ≤ TransactionCost s₂ s₁ →
        JusticeDegree s₁ ≥ JusticeDegree s₂
  /- 自指必须完备（仅约束自指系统） -/
  self_reference_theorem :
    ∀ s : System, SelfReferring s → ∀ t : Time,
      ∀ σ ∈ statesOf s, valuationAt s t σ ≠ Valuation.unassigned
  /- 科学不变性 -/
  law_of_scientific_invariance :
    ∀ s : System, HasCommitment s → HasFulfillment s →
      ∀ t₁ t₂ : Time, ∀ σ ∈ statesOf s,
        valuationAt s t₁ σ = valuationAt s t₂ σ
  /- 科学世俗：不直接惩罚 -/
  law_of_secular_science :
    ∀ s target : System, HasCommitment s → HasFulfillment s →
      ¬ InflictsPhysicalPunishment s target

variable (E : Env)

/-! ## 定义 -/

def Correct (s : E.System) (t : E.Time) : Prop :=
  ∀ σ ∈ E.statesOf s, E.valuationAt s t σ ≠ Valuation.unassigned

/-! ### 认识论四元组 -/

def Free (s : E.System) (t : E.Time) : Prop :=
  Correct E s t ∧ ∃ σ ∈ E.statesOf s, ¬ E.Knows s t σ

def Order (s : E.System) (t : E.Time) : Prop :=
  Correct E s t ∧ ∀ σ ∈ E.statesOf s, E.Knows s t σ

def Slavery (s : E.System) (t : E.Time) : Prop :=
  ¬ Correct E s t ∧ ∀ σ ∈ E.statesOf s, E.Knows s t σ

def License (s : E.System) (t : E.Time) : Prop :=
  ¬ Correct E s t ∧ ∃ σ ∈ E.statesOf s, ¬ E.Knows s t σ

theorem free_order_exclusive (s : E.System) (t : E.Time) :
    ¬ (Free E s t ∧ Order E s t) := by
  intro ⟨hf, ho⟩
  obtain ⟨σ, hσ_mem, hσ_not⟩ := hf.2
  exact hσ_not (ho.2 σ hσ_mem)

theorem free_slavery_exclusive (s : E.System) (t : E.Time) :
    ¬ (Free E s t ∧ Slavery E s t) := by
  intro ⟨hf, hs⟩
  exact hs.1 hf.1

theorem free_license_exclusive (s : E.System) (t : E.Time) :
    ¬ (Free E s t ∧ License E s t) := by
  intro ⟨hf, hl⟩
  exact hl.1 hf.1

theorem order_slavery_exclusive (s : E.System) (t : E.Time) :
    ¬ (Order E s t ∧ Slavery E s t) := by
  intro ⟨ho, hs⟩
  exact hs.1 ho.1

theorem order_license_exclusive (s : E.System) (t : E.Time) :
    ¬ (Order E s t ∧ License E s t) := by
  intro ⟨ho, hl⟩
  exact hl.1 ho.1

theorem slavery_license_exclusive (s : E.System) (t : E.Time) :
    ¬ (Slavery E s t ∧ License E s t) := by
  intro ⟨hs, hl⟩
  exact hl.1 hs.1

/-! ### 文化实践四元组 -/

def Science (s : E.System) : Prop := E.HasCommitment s ∧ E.HasFulfillment s
def Religion (s : E.System) : Prop := E.HasCommitment s ∧ ¬ E.HasFulfillment s
def Engineering (s : E.System) : Prop := ¬ E.HasCommitment s ∧ E.HasFulfillment s
def Philosophy (s : E.System) : Prop := ¬ E.HasCommitment s ∧ ¬ E.HasFulfillment s

theorem science_religion_exclusive (s : E.System) : ¬ (Science E s ∧ Religion E s) := by
  intro ⟨⟨_, hf⟩, ⟨_, hnf⟩⟩; exact hnf hf

theorem science_engineering_exclusive (s : E.System) : ¬ (Science E s ∧ Engineering E s) := by
  intro ⟨⟨hc, _⟩, ⟨hnc, _⟩⟩; exact hnc hc

theorem science_philosophy_exclusive (s : E.System) : ¬ (Science E s ∧ Philosophy E s) := by
  intro ⟨⟨hc, _⟩, ⟨hnc, _⟩⟩; exact hnc hc

/-! ### 科学四元组 -/

def NaturalScience (s : E.System) : Prop := E.IsMaterial s ∧ E.IsEmpirical s
def SocialScience (s : E.System) : Prop := E.IsConscious s ∧ E.IsEmpirical s
def Mathematics (s : E.System) : Prop := E.IsMaterial s ∧ E.IsFormal s
def MetaScience (s : E.System) : Prop := E.IsConscious s ∧ E.IsFormal s

theorem natural_social_exclusive (s : E.System) :
    ¬ (NaturalScience E s ∧ SocialScience E s) := by
  intro ⟨⟨hm, _⟩, ⟨hc, _⟩⟩
  exact E.material_conscious_exclusive s ⟨hm, hc⟩

theorem math_meta_exclusive (s : E.System) :
    ¬ (Mathematics E s ∧ MetaScience E s) := by
  intro ⟨⟨hm, _⟩, ⟨hc, _⟩⟩
  exact E.material_conscious_exclusive s ⟨hm, hc⟩

theorem natural_math_exclusive (s : E.System) :
    ¬ (NaturalScience E s ∧ Mathematics E s) := by
  intro ⟨⟨_, he⟩, ⟨_, hf⟩⟩
  exact E.empirical_formal_exclusive s ⟨he, hf⟩

theorem social_meta_exclusive (s : E.System) :
    ¬ (SocialScience E s ∧ MetaScience E s) := by
  intro ⟨⟨_, he⟩, ⟨_, hf⟩⟩
  exact E.empirical_formal_exclusive s ⟨he, hf⟩

/-! ### 民主四元组 -/

def Democracy (s : E.System) (t : E.Time) : Prop :=
  E.IsCollective s ∧ Order E s t
def Populism (s : E.System) (t : E.Time) : Prop :=
  E.IsCollective s ∧ License E s t
def Autocracy (s : E.System) (t : E.Time) : Prop :=
  E.IsIndividual s ∧ Order E s t
def Dictatorship (s : E.System) (t : E.Time) : Prop :=
  E.IsIndividual s ∧ License E s t

/-! ### 真善美（简化） -/

def Truthful (s : E.System) (t : E.Time) : Prop := Correct E s t
def Good (s : E.System) : Prop := E.IsCollective s
def Beautiful (s : E.System) : Prop := E.HasPower s

/-! ### 主观/客观 -/

def Agree (s₁ s₂ : E.System) (t : E.Time) : Prop :=
  ∀ σ ∈ E.statesOf s₁, E.valuationAt s₁ t σ = E.valuationAt s₂ t σ
def Objective (s₁ s₂ : E.System) (t : E.Time) : Prop := Agree E s₁ s₂ t
def Subjective (s₁ s₂ : E.System) (t : E.Time) : Prop := ¬ Agree E s₁ s₂ t

/-! ### 信用与不存在 -/

def Credit (s : E.System) : ℝ := E.JusticeDegree s
def Nonexistent (s : E.System) : Prop := ¬ (E.statesOf s).Nonempty
def Wrong (s : E.System) (t : E.Time) : Prop := ¬ Correct E s t

/-! ### 动荡 -/

def Turbulent (s : E.System) (t₁ t₂ : E.Time) : Prop :=
  E.traceOf (E.hasBoundary s) t₁ ≠ E.traceOf (E.hasBoundary s) t₂

theorem game_theorem (s : E.System) (t₁ t₂ : E.Time)
    (hib : E.InformationBlocked s t₁) (hmg : E.MinorityGame s) :
    Turbulent E s t₁ t₂ :=
  E.turbulence_from_information_blocking s t₁ t₂ hib hmg

/-! ### 正义 -/

def Friction (s₁ s₂ : E.System) : ℝ := E.TransactionCost s₁ s₂

def Just (s : E.System) : Prop :=
  E.PropertyRightsClear s ∧ Friction E s s = 0 ∧ E.ParetoEfficient s

def JustBetween (s₁ s₂ : E.System) : Prop :=
  E.TransactionCost s₁ s₂ ≤ E.TransactionCost s₂ s₁

theorem coase_implies_just (s : E.System)
    (h_pr : E.PropertyRightsClear s) (h_fr : Friction E s s = 0) :
    Just E s :=
  ⟨h_pr, h_fr, E.axiom_5_coase s h_pr h_fr⟩

theorem justice_measurement_theorem' (s₁ s₂ : E.System)
    (h : JustBetween E s₁ s₂) : E.JusticeDegree s₁ ≥ E.JusticeDegree s₂ :=
  E.justice_measurement_theorem s₁ s₂ h

/-! ### 意义 -/

def Price (cr : E.Crossing) : ℝ := E.Cost cr + E.Competition cr
def Meaning (cr : E.Crossing) : ℝ := Price E cr

/-! ### 剪枝 -/

def ShouldPrune (s : E.System) (t : E.Time) : Prop :=
  (¬ Correct E s t) ∨
  Order E s t ∨
  (Just E s ∧ ¬ E.ParetoEfficient s)

theorem pruning_incorrect (s : E.System) (t : E.Time)
    (h : ¬ Correct E s t) : ShouldPrune E s t :=
  Or.inl h

/-! ## 黑格尔定理（移出 `Env`） -/

def HegelTheorem (E : Env) : Prop := ∀ s, ¬ E.LearnsFromHistory s

/-! ## 一致性模型 -/

/-- 退化模型：`Unit` 系统，`Knows = False`，用于快速验证。 -/
def canonicalEnv : Env where
  State := Bool
  Boundary := Unit
  System := Unit
  Time := ℕ
  Value := Unit
  BoundarySig := Unit
  Crossing := Unit
  Description := Unit

  hasBoundary _ := ()
  boundaryOf b := b
  statesOf _ := {true, false}
  le := (· ≤ ·)
  valuationAt _ _ _ := Valuation.assigned ()
  UnassignedCount _ _ := 0
  traceOf _ _ := ()
  crossingsOf _ := {()}
  Cost _ := 1
  Competition _ := 1
  TransactionCost _ _ := 0
  Knows _ _ _ := False
  DescriptionLength _ := 0
  DescribesCompletely _ _ := True
  Principle _ := ()
  Differs a b := a ≠ b
  InformationBlocked _ _ := False
  MinorityGame _ := False
  PropertyRightsClear _ := True
  ParetoEfficient _ := True
  IsCollective _ := True
  IsIndividual _ := False
  HasCommitment _ := True
  HasFulfillment _ := True
  IsMaterial _ := True
  IsConscious _ := False
  IsEmpirical _ := True
  IsFormal _ := False
  Judgment _ _ := True
  HasPower _ := True
  GovernedByPrinciple _ _ := True
  LearnsFromHistory _ := False
  MassIgnoranceAuthorization _ := False
  DialecticalEffectiveness _ := False
  DialecticianPower _ := False
  TraceableToAxioms _ := True
  TrustworthyDeduction _ := True
  Contradicts _ _ := False
  ChallengesScience _ _ := False
  InflictsPhysicalPunishment _ _ := False
  JusticeDegree _ := 0
  SelfReferring _ := False

  axiom_0 := by
    intro _ _
    exact ⟨true, false, by simp, by simp, by decide⟩
  count_zero_iff_correct := by
    intro _ _
    constructor
    · intro _ σ _ h; cases h
    · intro _; rfl
  axiom_2_monotone := by
    intro _ _ _ _; exact Nat.le_refl 0
  axiom_2_tends_to_complete := by
    intro _ n
    exact ⟨0, Nat.zero_le n⟩
  turbulence_from_information_blocking := by
    intro _ _ _ h _; exact False.elim h
  axiom_5_coase := by
    intro _ _ _; trivial
  axiom_7 := by
    intro _
    exact ⟨trivial, fun _ _ => le_refl 0⟩
  axiom_boundary_idempotent := by
    intro _; rfl
  material_conscious_exclusive := by
    intro _ ⟨_, hc⟩; exact hc
  empirical_formal_exclusive := by
    intro _ ⟨_, hf⟩; exact hf
  justice_measurement_theorem := by
    intro _ _ _; exact le_refl 0
  self_reference_theorem := by
    intro _ h; exact False.elim h
  law_of_scientific_invariance := by
    intro _ _ _ _ _ _; rfl
  law_of_secular_science := by
    intro _ _ _ _ h; exact False.elim h

/-! ### 非平凡模型 -/

def ntVal (s : Bool) (t : ℕ) (_ : Bool) : Valuation Unit :=
  if s = false ∧ t = 0 then Valuation.unassigned else Valuation.assigned ()

def ntUC (s : Bool) (t : ℕ) : ℕ :=
  if s = false ∧ t = 0 then 1 else 0

def ntKnows (s : Bool) (_ : ℕ) (_ : Bool) : Prop := s = true

def ntTC : Bool → Bool → ℝ
  | true, true => 0
  | true, false => 1
  | false, true => 2
  | false, false => 0

def ntJD : Bool → ℝ
  | true => 1
  | false => 0

def ntCollective (s : Bool) : Prop := s = true
def ntIndividual (s : Bool) : Prop := s = false
def ntHasCommitment (s : Bool) : Prop := s = true
def ntHasFulfillment (s : Bool) : Prop := s = true
def ntIsMaterial (s : Bool) : Prop := s = true
def ntIsConscious (s : Bool) : Prop := s = false
def ntIsEmpirical (s : Bool) : Prop := s = true
def ntIsFormal (s : Bool) : Prop := s = false
def ntSelfRef (s : Bool) : Prop := s = true

def ntInformationBlocked (_ : Bool) (_ : ℕ) : Prop := False
def ntMinorityGame (_ : Bool) : Prop := False
def ntInflictsPhysicalPunishment (_ _ : Bool) : Prop := False

/-- 非平凡模型：
- 两个系统 `true`（秩序/民主）与 `false`（初始放任/独裁，之后自由）。
- `true` 在所有时刻正确且已知；`false` 在 `t = 0` 时未赋值且未知，`t > 0` 时正确但未知。
- 交易成本非对称：`TC true false = 1`，`TC false true = 2`。
- 正义度：`JD true = 1`，`JD false = 0`。 -/
def nontrivialEnv : Env where
  State := Bool
  Boundary := Unit
  System := Bool
  Time := ℕ
  Value := Unit
  BoundarySig := Unit
  Crossing := Unit
  Description := Unit

  hasBoundary _ := ()
  boundaryOf b := b
  statesOf _ := {true, false}
  le := (· ≤ ·)
  valuationAt := ntVal
  UnassignedCount := ntUC
  traceOf _ _ := ()
  crossingsOf _ := {()}
  Cost _ := 1
  Competition _ := 1
  TransactionCost := ntTC
  Knows := ntKnows
  DescriptionLength _ := 0
  DescribesCompletely _ _ := True
  Principle _ := ()
  Differs a b := a ≠ b
  InformationBlocked := ntInformationBlocked
  MinorityGame := ntMinorityGame
  PropertyRightsClear _ := True
  ParetoEfficient _ := True
  IsCollective := ntCollective
  IsIndividual := ntIndividual
  HasCommitment := ntHasCommitment
  HasFulfillment := ntHasFulfillment
  IsMaterial := ntIsMaterial
  IsConscious := ntIsConscious
  IsEmpirical := ntIsEmpirical
  IsFormal := ntIsFormal
  Judgment _ _ := True
  HasPower _ := True
  GovernedByPrinciple _ _ := True
  LearnsFromHistory _ := False
  MassIgnoranceAuthorization _ := False
  DialecticalEffectiveness _ := False
  DialecticianPower _ := False
  TraceableToAxioms _ := True
  TrustworthyDeduction _ := True
  Contradicts _ _ := False
  ChallengesScience _ _ := False
  InflictsPhysicalPunishment := ntInflictsPhysicalPunishment
  JusticeDegree := ntJD
  SelfReferring := ntSelfRef

  axiom_0 := by
    intro _ _
    exact ⟨true, false, by simp, by simp, by decide⟩
  count_zero_iff_correct := by
    intro s t
    by_cases h : s = false ∧ t = 0
    · simp [ntUC, ntVal, h]
    · simp [ntUC, ntVal, h]
  axiom_2_monotone := by
    intro s t₁ t₂ hle
    by_cases h1 : s = false ∧ t₁ = 0
    · have : ntUC s t₂ ≤ 1 := by
        unfold ntUC
        split <;> omega
      simpa [ntUC, h1] using this
    · have h2 : ¬(s = false ∧ t₂ = 0) := by
        intro h2
        apply h1
        exact ⟨h2.1, by omega⟩
      simp [ntUC, h1, h2]
  axiom_2_tends_to_complete := by
    intro s n
    refine ⟨1, ?_⟩
    simp [ntUC]
    omega
  turbulence_from_information_blocking := by
    intro _ _ _ h _; exact False.elim h
  axiom_5_coase := by
    intro _ _ _; trivial
  axiom_7 := by
    intro _
    exact ⟨trivial, fun _ _ => le_refl 0⟩
  axiom_boundary_idempotent := by
    intro _; rfl
  material_conscious_exclusive := by
    intro s ⟨hm, hc⟩
    cases s
    · cases hc
    · cases hm
  empirical_formal_exclusive := by
    intro s ⟨he, hf⟩
    cases s
    · cases hf
    · cases he
  justice_measurement_theorem := by
    intro s₁ s₂ h
    cases s₁ <;> cases s₂ <;>
      simp [ntTC, ntJD] at h ⊢ <;> norm_num at h ⊢
  self_reference_theorem := by
    intro s h t σ _ hval
    cases s
    · simp [ntVal] at hval ⊢
    · cases h
  law_of_scientific_invariance := by
    intro s hc hf t₁ t₂ σ _
    cases s
    · simp [ntVal]
    · cases hc
  law_of_secular_science := by
    intro _ _ _ _ h; exact False.elim h

/-! ## 一致性定理 -/

/-- 公理集可满足：由 `nontrivialEnv` 逐条验证。 -/
theorem axioms_consistent : Nonempty Env := ⟨nontrivialEnv⟩

/-! ## 非平凡性验证 -/

theorem nontrivial_free_exists : Free nontrivialEnv false 1 := by
  constructor
  · intro σ _ h; cases h
  · refine ⟨true, by simp, ?_⟩
    simp [nontrivialEnv, ntKnows]

theorem nontrivial_order_exists : Order nontrivialEnv true 0 := by
  constructor
  · intro σ _ h; cases h
  · intro σ _; simp [nontrivialEnv, ntKnows]

theorem nontrivial_license_exists : License nontrivialEnv false 0 := by
  constructor
  · intro h
    have := h true (by simp)
    simp [nontrivialEnv, ntVal] at this
  · refine ⟨true, by simp, ?_⟩
    simp [nontrivialEnv, ntKnows]

theorem nontrivial_democracy_exists : Democracy nontrivialEnv true 0 :=
  ⟨by simp [nontrivialEnv, ntCollective], nontrivial_order_exists⟩

theorem nontrivial_dictatorship_exists : Dictatorship nontrivialEnv false 0 :=
  ⟨by simp [nontrivialEnv, ntIndividual], nontrivial_license_exists⟩

theorem nontrivial_free_not_order :
    ¬ (Free nontrivialEnv false 1 ∧ Order nontrivialEnv false 1) :=
  free_order_exclusive nontrivialEnv false 1

/-! ## 哥德尔框架 -/

namespace Gödel

inductive ProofStatus where
  | proved_true  : ProofStatus
  | proved_false : ProofStatus

structure FormalSystem where
  Formula : Type
  Provable : Formula → Prop
  Refutable : Formula → Prop
  consistent : ∀ φ, ¬ (Provable φ ∧ Refutable φ)

def systemValuation (S : FormalSystem) (φ : S.Formula) : Valuation ProofStatus :=
  if S.Provable φ then Valuation.assigned ProofStatus.proved_true
  else if S.Refutable φ then Valuation.assigned ProofStatus.proved_false
  else Valuation.unass
