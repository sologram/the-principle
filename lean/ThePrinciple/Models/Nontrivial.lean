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

def ntSocialCost : Bool → ℝ
  | true => 0
  | false => 2

def ntClaimsJustice (_ : Bool) : Prop := True
def ntPareto (s : Bool) : Prop := s = true

def ntCollective (s : Bool) : Prop := s = true

theorem ntCollective_false : ¬ ntCollective false := by simp [ntCollective]
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
  SocialCost := ntSocialCost
  ClaimsJustice := ntClaimsJustice
  Knows := ntKnows
  DescriptionLength _ := 0
  DescribesCompletely _ _ := True
  Principle _ := ()
  Differs a b := a ≠ b
  Evolving _ := True
  InformationBlocked := ntInformationBlocked
  MinorityGame := ntMinorityGame
  PropertyRightsClear := ntCollective
  ParetoEfficient := ntPareto
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

  axiom_0 := fun _ h => ⟨⟨⟩⟩
  count_zero_iff_correct := by
    intro s t
    by_cases h : s = false ∧ t = 0
    · simp [ntUC, ntVal, h]
    · simp [ntUC, ntVal, h]
  axiom_2_trend := by
    intro s _ n
    refine ⟨1, ?_⟩
    simp [ntUC]
  turbulence_from_information_blocking := by
    intro _ _ _ h _; exact False.elim h
  axiom_5_coase := by
    intro s hpr _
    cases s
    · exact absurd hpr ntCollective_false
    · rfl
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

/-- The pseudo-just `false` (claims justice, not Pareto-efficient in aggregate) is pruned. -/
theorem nontrivial_pseudo_just_pruned : PruneInefficient nontrivialEnv false :=
  ⟨True.intro, by simp [nontrivialEnv, ntPareto]⟩

/-- The license state `false @ t = 0` is pruned by the first judgment
(incorrect), not the second — 放任 is cut for incompleteness, 伪自由 for order. -/
theorem nontrivial_license_pruned_incorrect :
    PruneIncorrect nontrivialEnv false 0 := fun h =>
  nontrivial_license_exists.1 h
