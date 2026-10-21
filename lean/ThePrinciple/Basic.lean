module

public import Mathlib.Basic.Real.Basic
public import Mathlib.Data.Set.Basic
public import Mathlib.Data.Nat.Basic

/-!
# The Principle — Basic layer

`Valuation` and the full environment `Env`: data carriers + axiom constraints.
All downstream modules (quadruples, justice, pruning, models, Gödel framework) depend on this module.
-/

@[expose] public section

inductive Valuation (α : Type) where
  | assigned : α → Valuation α
  | unassigned : Valuation α

/-- The full environment: data carriers + axiom constraints. -/
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

  /- Axiom 0: to exist is to differ -/
  axiom_0 : ∀ (s : System), Nonempty Boundary →
    ∃ σ τ : State, σ ∈ statesOf s ∧ τ ∈ statesOf s ∧ Differs σ τ
  /- Axiom 2: things tend toward completeness -/
  count_zero_iff_correct : ∀ (s : System) (t : Time),
    UnassignedCount s t = 0 ↔
      ∀ σ ∈ statesOf s, valuationAt s t σ ≠ Valuation.unassigned
  axiom_2_monotone : ∀ (s : System) (t₁ t₂ : Time),
    le t₁ t₂ → UnassignedCount s t₂ ≤ UnassignedCount s t₁
  axiom_2_tends_to_complete : ∀ (s : System) (n : ℕ),
    ∃ t : Time, UnassignedCount s t ≤ n
  /- Axiom 3: turbulence originates from information blocking -/
  turbulence_from_information_blocking :
    ∀ (s : System) (t₁ t₂ : Time),
      InformationBlocked s t₁ → MinorityGame s →
        traceOf (hasBoundary s) t₁ ≠ traceOf (hasBoundary s) t₂
  /- Axiom 5: justice is efficiency (Coase) -/
  axiom_5_coase : ∀ s : System,
    PropertyRightsClear s → TransactionCost s s = 0 → ParetoEfficient s
  /- Axiom 7: the principle is optimal (MDL) -/
  axiom_7 : ∀ s : System,
    DescribesCompletely (Principle s) s ∧
      ∀ d : Description, DescribesCompletely d s →
        DescriptionLength (Principle s) ≤ DescriptionLength d
  /- Boundary idempotence -/
  axiom_boundary_idempotent : ∀ b : Boundary,
    boundaryOf (boundaryOf b) = boundaryOf b
  /- Quadruple mutual exclusion: material/conscious -/
  material_conscious_exclusive :
    ∀ s : System, ¬ (IsMaterial s ∧ IsConscious s)
  /- Quadruple mutual exclusion: empirical/formal -/
  empirical_formal_exclusive :
    ∀ s : System, ¬ (IsEmpirical s ∧ IsFormal s)
  /- Justice measurement: the less inter-system friction, the higher the justice degree -/
  justice_measurement_theorem :
    ∀ s₁ s₂ : System,
      TransactionCost s₁ s₂ ≤ TransactionCost s₂ s₁ →
        JusticeDegree s₁ ≥ JusticeDegree s₂
  /- Self-reference must be complete (constrains only self-referring systems) -/
  self_reference_theorem :
    ∀ s : System, SelfReferring s → ∀ t : Time,
      ∀ σ ∈ statesOf s, valuationAt s t σ ≠ Valuation.unassigned
  /- Scientific invariance -/
  law_of_scientific_invariance :
    ∀ s : System, HasCommitment s → HasFulfillment s →
      ∀ t₁ t₂ : Time, ∀ σ ∈ statesOf s,
        valuationAt s t₁ σ = valuationAt s t₂ σ
  /- Secular science: no direct punishment -/
  law_of_secular_science :
    ∀ s target : System, HasCommitment s → HasFulfillment s →
      ¬ InflictsPhysicalPunishment s target

variable (E : Env)

/-- Correct: no undecided within the boundary. -/
def Correct (s : E.System) (t : E.Time) : Prop :=
  ∀ σ ∈ E.statesOf s, E.valuationAt s t σ ≠ Valuation.unassigned
