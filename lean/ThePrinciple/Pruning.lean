module

public import ThePrinciple.Justice

/-!
# Pruning

`ShouldPrune`: prune the incomplete "correct", the non-ignorant "free",
and the inefficient "just".
-/

@[expose] public section
variable (E : Env)

/-! ### Pruning -/

/-- Prune the incomplete "correct": anything not correct within its boundary
(= having holes, per Axiom 1). -/
def PruneIncorrect (s : E.System) (t : E.Time) : Prop := ¬ Correct E s t

/-- Prune the pseudo-free: full knowledge claimed as freedom (= order in
disguise). 放任 (real license) is kept — the fourth pruning targets 伪自由. -/
def PruneOmniscient (s : E.System) (t : E.Time) : Prop := Order E s t

/-- Prune the pseudo-just: the system claims justice while lacking Pareto
efficiency (伪正义 = 声称正义、实增摩擦). -/
def PruneInefficient (s : E.System) : Prop :=
  E.ClaimsJustice s ∧ ¬ E.ParetoEfficient s

/-- Prune the priceless "meaning": a crossing with neither cost nor competition. -/
def PrunePriceless (s : E.System) (cr : E.Crossing) : Prop :=
  cr ∈ E.crossingsOf (E.hasBoundary s) ∧ Price E cr = 0

/-- Auxiliary: the first three prunings, used to define `PruneAimless`
without circularity. -/
def ShouldPruneCore (s : E.System) (t : E.Time) : Prop :=
  PruneIncorrect E s t ∨
  PruneOmniscient E s t ∨
  PruneInefficient E s

/-- Prune the aimless "evolution": no principle governs, and nothing is pruned. -/
def PruneAimless (s : E.System) (t : E.Time) : Prop :=
  ¬ E.GovernedByPrinciple s t ∧ ¬ ShouldPruneCore E s t

/-- The five prunings, per the pruning theorem. -/
def ShouldPrune (s : E.System) (t : E.Time) : Prop :=
  PruneIncorrect E s t ∨
  PruneOmniscient E s t ∨
  PruneInefficient E s ∨
  (∃ cr, PrunePriceless E s cr) ∨
  PruneAimless E s t

theorem pruning_incorrect (s : E.System) (t : E.Time)
    (h : ¬ Correct E s t) : ShouldPrune E s t :=
  Or.inl h

/-- Pruning theorem (fifth judgment, engineering layer): the pseudo-just is cut. -/
theorem pruning_pseudo_just (s : E.System) (t : E.Time)
    (h : E.ClaimsJustice s) (hpe : ¬ E.ParetoEfficient s) :
    ShouldPrune E s t :=
  Or.inr (Or.inr (Or.inl ⟨h, hpe⟩))

/-- 放任 (license) is not cut by the second judgment — only 秩序 masquerading
as freedom is. -/
theorem license_not_pruned_as_free (s : E.System) (t : E.Time)
    (h : License E s t) : ¬ PruneOmniscient E s t := fun ho =>
  order_license_exclusive E s t ⟨ho, h⟩

/-! ### 剪枝定理 (the pruning theorem) -/

/-- The pruning theorem: `ShouldPrune` is exactly the disjunction of the five
judgments, each cutting one pseudo-form of one criterion —
不完全的"正确"、放任伪装的"自由"(=秩序)、增摩擦的"正义"(伪正义)、
无价格的"意义"、无目的的"演化". -/
theorem pruning_theorem (s : E.System) (t : E.Time) :
    ShouldPrune E s t ↔
      PruneIncorrect E s t ∨ PruneOmniscient E s t ∨ PruneInefficient E s ∨
      (∃ cr, PrunePriceless E s cr) ∨ PruneAimless E s t := Iff.rfl

theorem pruning_pseudo_free (s : E.System) (t : E.Time)
    (h : Order E s t) : ShouldPrune E s t :=
  Or.inr (Or.inl h)

theorem pruning_priceless (s : E.System) (cr : E.Crossing)
    (h : PrunePriceless E s cr) : ∀ t : E.Time, ShouldPrune E s t :=
  fun _ => Or.inr (Or.inr (Or.inr (Or.inl ⟨cr, h⟩)))

theorem pruning_aimless (s : E.System) (t : E.Time)
    (h : PruneAimless E s t) : ShouldPrune E s t :=
  Or.inr (Or.inr (Or.inr (Or.inr h)))

/-! ### 域外执法定理 (extraterritorial enforcement) -/

/-- The court criterion is universal: every system is measured by the same
zero-unassigned test, wherever it stands. -/
theorem judgment_via_count (s : E.System) (t : E.Time) :
    Correct E s t ↔ E.UnassignedCount s t = 0 :=
  (E.count_zero_iff_correct s t).symm.trans ⟨fun h => h, fun h => h⟩

/-- Yet enquiry is local: a system's correctness only quantifies over its own
states — no system is judged by another's states. Enforcement of the criterion
is universal; the enquiry that satisfies it is bounded by each system's own
boundary. -/
theorem jurisdiction_local (s₁ s₂ : E.System) (t : E.Time)
    (hσ : ∀ σ, σ ∉ E.statesOf s₁) :
    (∀ σ ∈ E.statesOf s₂, E.valuationAt s₂ t σ ≠ Valuation.unassigned) →
    ∀ σ ∈ E.statesOf s₁, E.valuationAt s₁ t σ ≠ Valuation.unassigned := by
  intro _ σ hσ₁
  exact absurd hσ₁ (hσ σ)
