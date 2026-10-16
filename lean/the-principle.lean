universe u v w t z c

/- Basic carriers -/
variable (State : Type u)
variable (Boundary : Type v)
variable (System : Type w)

variable (hasBoundary : System → Boundary)
variable (statesOf : System → Set State)

variable (Value : Type z)
inductive Valuation

  | assigned : Value → Valuation
  | unassigned : Valuation

variable (valuation : System → State → Valuation)

variable (Time : Type t)
variable (le : Time → Time → Prop)

variable (Crossing : Type c)
variable (crossingsOf : Boundary → Set Crossing)

variable (Cost : Crossing → ℝ)
variable (Competition : Crossing → ℝ)

/- Axiom 0: Boundary is existence -/
axiom axiom_0_boundary_is_existence :
  ∀ (s : System), Nonempty (Boundary) → Nonempty (State)

/- Axiom 1: Correctness is completeness -/
def Correct (s : System) : Prop :=
  ∀ σ ∈ statesOf s, valuation s σ ≠ Valuation.unassigned

axiom axiom_1_correct_iff_complete :
  ∀ s : System, Correct s  ∀ σ ∈ statesOf s, valuation s σ ≠ Valuation.unassigned

/- Axiom 2: Things tend toward completeness -/
def UnassignedCount (s : System) (t : Time) : ℕ := sorry

axiom axiom_2_tends_to_complete :
  ∀ (s : System) (t₁ t₂ : Time),
    le t₁ t₂ →
    UnassignedCount s t₂ ≤ UnassignedCount s t₁

/- Axiom 3: Turbulence is boundary instability -/
def BoundaryChanges (b : Boundary) (t₁ t₂ : Time) : Prop := sorry

def Turbulent (s : System) (t₁ t₂ : Time) : Prop :=
  BoundaryChanges (hasBoundary s) t₁ t₂

axiom axiom_3_turbulence_iff_boundary_unstable :
  ∀ (s : System) (t₁ t₂ : Time),
    Turbulent s t₁ t₂  BoundaryChanges (hasBoundary s) t₁ t₂

/- Axiom 4: Freedom is ignorance -/
def Outside (b : Boundary) : Type := sorry
def Knowable (b : Boundary) (x : Outside b) : Prop := sorry
def HasCompetition (cr : Crossing) : Prop := sorry

def Free (s : System) : Prop :=
  ∃ x : Outside (hasBoundary s), ¬ Knowable (hasBoundary s) x ∧
    ∃ cr ∈ crossingsOf (hasBoundary s), HasCompetition cr

axiom axiom_4_free_iff_ignorance :
  ∀ s : System, Free s 
    ∃ x : Outside (hasBoundary s), ¬ Knowable (hasBoundary s) x ∧
      ∃ cr ∈ crossingsOf (hasBoundary s), HasCompetition cr

/- Axiom 5: Justice is minimizing boundary friction -/
def Friction (s₁ s₂ : System) : ℝ := sorry

def Just (s₁ s₂ : System) : Prop :=
  ∀ s₁' s₂', Friction s₁' s₂' ≥ Friction s₁ s₂

axiom axiom_5_justice_iff_min_friction :
  ∀ s₁ s₂, Just s₁ s₂ 
    ∀ s₁' s₂', Friction s₁' s₂' ≥ Friction s₁ s₂

/- Axiom 6: Meaning is boundary-crossing pricing -/
def Price (cr : Crossing) : ℝ :=
  Cost cr + Competition cr

def Meaning (cr : Crossing) : ℝ :=
  Price cr

axiom axiom_6_meaning_is_price :
  ∀ cr : Crossing, Meaning cr = Price cr

/- Axiom 7: Principle is optimality -/
def DescriptionLength (d : Description) : ℝ := sorry
def DescribesCompletely (d : Description) (s : System) : Prop := sorry

def Principle (s : System) : Description := sorry

axiom axiom_7_principle_is_mdl :
  ∀ s : System,
    DescribesCompletely (Principle s) s ∧
    ∀ d, DescribesCompletely d s → DescriptionLength (Principle s) ≤ DescriptionLength d
