module

public import ThePrinciple.Models.Nontrivial

/-!
# Gödel framework

Formal systems, Gödel sentences, the Hilbert core, and the open conjecture `HilbertProcessConjecture`.
-/

@[expose] public section

namespace Gödel

inductive ProofStatus where
  | proved_true  : ProofStatus
  | proved_false : ProofStatus

structure FormalSystem where
  Formula : Type
  Provable : Formula → Prop
  Refutable : Formula → Prop
  consistent : ∀ φ, ¬ (Provable φ ∧ Refutable φ)

open Classical in
noncomputable def systemValuation (S : FormalSystem) (φ : S.Formula) : Valuation ProofStatus :=
  if S.Provable φ then Valuation.assigned ProofStatus.proved_true
  else if S.Refutable φ then Valuation.assigned ProofStatus.proved_false
  else Valuation.unassigned

def IsGödel (S : FormalSystem) (φ : S.Formula) : Prop :=
  ¬ S.Provable φ ∧ ¬ S.Refutable φ

def HilbertCore (S : FormalSystem) : Set S.Formula :=
  { φ | S.Provable φ ∨ S.Refutable φ }

theorem godel_not_in_hilbert_core (S : FormalSystem) (G : S.Formula)
    (h : IsGödel S G) : G ∉ HilbertCore S := by
  intro hc
  cases hc with
  | inl hp => exact h.1 hp
  | inr hr => exact h.2 hr

/-- Open conjecture: the Gödel world can be injectively embedded into the Hilbert world.
    This is the honest statement of "Gödel-world minimization", not a solved theorem. -/
def HilbertProcessConjecture : Prop :=
  ∀ (S : FormalSystem),
    (∃ G : S.Formula, IsGödel S G) →
    ∃ (embed : S.Formula → S.Formula),
      (∀ φ, IsGödel S φ →
        S.Provable (embed φ) ∨ S.Refutable (embed φ)) ∧
      Function.Injective embed

end Gödel
