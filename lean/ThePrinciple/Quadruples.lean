module

public import ThePrinciple.Epistemic

/-!
# Quadruples and concept definitions

Cultural-practice quadruple (science/philosophy/religion/engineering),
scientific quadruple, democratic quadruple, truth-goodness-beauty,
subjective/objective, credit and nonexistence, turbulence, meaning.
-/

@[expose] public section
variable (E : Env)

/-! ### Cultural-practice quadruple -/

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

/-! ### Scientific quadruple -/

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

/-! ### Democratic quadruple -/

def Democracy (s : E.System) (t : E.Time) : Prop :=
  E.IsCollective s ∧ Order E s t
def Populism (s : E.System) (t : E.Time) : Prop :=
  E.IsCollective s ∧ License E s t
def Autocracy (s : E.System) (t : E.Time) : Prop :=
  E.IsIndividual s ∧ Order E s t
def Dictatorship (s : E.System) (t : E.Time) : Prop :=
  E.IsIndividual s ∧ License E s t

/-! ### Truth, goodness, beauty (simplified) -/

def Truthful (s : E.System) (t : E.Time) : Prop := Correct E s t
def Good (s : E.System) : Prop := E.IsCollective s
def Beautiful (s : E.System) : Prop := E.HasPower s

/-! ### Subjective/objective -/

def Agree (s₁ s₂ : E.System) (t : E.Time) : Prop :=
  ∀ σ ∈ E.statesOf s₁, E.valuationAt s₁ t σ = E.valuationAt s₂ t σ
def Objective (s₁ s₂ : E.System) (t : E.Time) : Prop := Agree E s₁ s₂ t
def Subjective (s₁ s₂ : E.System) (t : E.Time) : Prop := ¬ Agree E s₁ s₂ t

/-! ### Credit and nonexistence -/

def Credit (s : E.System) : ℝ := E.JusticeDegree s
def Nonexistent (s : E.System) : Prop := ¬ (E.statesOf s).Nonempty
def Wrong (s : E.System) (t : E.Time) : Prop := ¬ Correct E s t

/-! ### Turbulence -/

def Turbulent (s : E.System) (t₁ t₂ : E.Time) : Prop :=
  E.traceOf (E.hasBoundary s) t₁ ≠ E.traceOf (E.hasBoundary s) t₂

theorem game_theorem (s : E.System) (t₁ t₂ : E.Time)
    (hib : E.InformationBlocked s t₁) (hmg : E.MinorityGame s) :
    Turbulent E s t₁ t₂ :=
  E.turbulence_from_information_blocking s t₁ t₂ hib hmg

/-! ### Meaning -/

def Price (cr : E.Crossing) : ℝ := E.Cost cr + E.Competition cr
def Meaning (cr : E.Crossing) : ℝ := Price E cr
