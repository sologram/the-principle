module

public import ThePrinciple.Pruning

/-!
# Degenerate model

A `Unit` system with `Knows = False`, for fast validation.
-/

@[expose] public section

/-- Degenerate model: a `Unit` system with `Knows = False`, for fast validation. -/
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
    intro _ _ _ _ _ _ _; rfl
  law_of_secular_science := by
    intro _ _ _ _ h; exact False.elim h
