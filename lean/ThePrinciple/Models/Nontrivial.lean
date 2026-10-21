module

public import ThePrinciple.Models.Canonical

/-!
# Nontrivial model

Two systems: `true` (order/democracy) and `false` (initially license/dictatorship, later free).
-/

@[expose] public section

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

/-- Nontrivial model:
- Two systems: `true` (order/democracy) and `false` (initially license/dictatorship, later free).
- `true` is correct and known at all times; `false` is unassigned and unknown at `t = 0`,
  correct but unknown for `t > 0`.
- Asymmetric transaction costs: `TC true false = 1`, `TC false true = 2`.
- Justice degrees: `JD true = 1`, `JD false = 0`. -/
@[reducible]
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
    · cases hm
    · cases hc
  empirical_formal_exclusive := by
    intro s ⟨he, hf⟩
    cases s
    · cases he
    · cases hf
  justice_measurement_theorem := by
    intro s₁ s₂ h
    cases s₁ <;> cases s₂ <;> simp [ntTC, ntJD] at h ⊢
  self_reference_theorem := by
    intro s h t σ _ hval
    cases s
    · cases h
    · simp [ntVal] at hval
  law_of_scientific_invariance := by
    intro s hc hf t₁ t₂ σ _
    cases s
    · cases hc
    · simp [ntVal]
  law_of_secular_science := by
    intro _ _ _ _ h; exact False.elim h

/-! ## Consistency theorem -/

/-- The axiom set is satisfiable, witnessed clause-by-clause by `nontrivialEnv`. -/
theorem axioms_consistent : Nonempty Env := ⟨nontrivialEnv⟩

/-! ## Nontriviality checks -/

theorem nontrivial_free_exists : Free nontrivialEnv false 1 := by
  constructor
  · intro σ _ h; cases h
  · refine ⟨true, by simp, ?_⟩
    simp [ntKnows]

theorem nontrivial_order_exists : Order nontrivialEnv true 0 := by
  constructor
  · intro σ _ h; cases h
  · intro σ _; simp [ntKnows]

theorem nontrivial_license_exists : License nontrivialEnv false 0 := by
  constructor
  · intro h
    have := h true (by simp)
    simp [nontrivialEnv, ntVal] at this
  · refine ⟨true, by simp, ?_⟩
    simp [ntKnows]

theorem nontrivial_democracy_exists : Democracy nontrivialEnv true 0 :=
  ⟨by simp [ntCollective], nontrivial_order_exists⟩

theorem nontrivial_dictatorship_exists : Dictatorship nontrivialEnv false 0 :=
  ⟨by simp [ntIndividual], nontrivial_license_exists⟩

theorem nontrivial_free_not_order :
    ¬ (Free nontrivialEnv false 1 ∧ Order nontrivialEnv false 1) :=
  free_order_exclusive nontrivialEnv false 1
