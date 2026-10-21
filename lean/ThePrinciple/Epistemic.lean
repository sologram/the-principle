module

public import ThePrinciple.Basic

/-!
# Epistemic quadruple

Free / order / slavery / license, with pairwise mutual-exclusion theorems.
-/

@[expose] public section
variable (E : Env)

/-! ### Epistemic quadruple -/

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
  obtain ⟨σ, hσ_mem, hσ_not⟩ := hl.2
  exact hσ_not (hs.2 σ hσ_mem)
