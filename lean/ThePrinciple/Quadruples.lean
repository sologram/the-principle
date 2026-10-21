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

/-- 真 = 正确即完备 (axiom 1). -/
def Truthful (s : E.System) (t : E.Time) : Prop := Correct E s t

/-- 好 = 效率：无内摩擦且帕累托有效 (axiom 5's "A 即 B"). -/
def Good (s : E.System) : Prop :=
  E.TransactionCost s s = 0 ∧ E.ParetoEfficient s

/-- 善 = 协作：产权明晰且对他者交易成本不高（可合作）. -/
def Cooperative (s : E.System) : Prop :=
  E.PropertyRightsClear s ∧ ∀ s₂ : E.System, E.TransactionCost s s₂ ≤ E.TransactionCost s₂ s

/-- 美 = 竞争力：在跨界上承受真实竞争而仍存活（工程层标注于 `Competition`）. -/
def Beautiful (s : E.System) : Prop :=
  ∃ cr ∈ E.crossingsOf (E.hasBoundary s), E.Competition cr > 0

/-! ### Subjective/objective -/

def Agree (s₁ s₂ : E.System) (t : E.Time) : Prop :=
  ∀ σ ∈ E.statesOf s₁, E.valuationAt s₁ t σ = E.valuationAt s₂ t σ
def Objective (s₁ s₂ : E.System) (t : E.Time) : Prop := Agree E s₁ s₂ t
def Subjective (s₁ s₂ : E.System) (t : E.Time) : Prop := ¬ Agree E s₁ s₂ t

/-! ### Credit and nonexistence -/

/-- 信用 = 承诺/兑现的记录：有承诺且兑现（工程层以二值记录起步）. -/
def Credit (s : E.System) : Prop := E.HasCommitment s ∧ E.HasFulfillment s
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

/-- 价格 = 供需均衡的工程层标注：成本（供给侧）+ 竞争（需求侧约束）. -/
def Price (cr : E.Crossing) : ℝ := E.Cost cr + E.Competition cr

/-- 意义是二值范畴：跨界产生选择倾向即有意义（定义层）；价格是其工程层数值. -/
def Meaning (cr : E.Crossing) : Prop := cr ∈ setOf fun c => Price E c > 0

theorem meaningful_of_price_pos (cr : E.Crossing) (h : Price E cr > 0) :
    Meaning E cr := h

theorem price_of_meaning_pos (cr : E.Crossing) (h : Meaning E cr) :
    Price E cr > 0 := h
