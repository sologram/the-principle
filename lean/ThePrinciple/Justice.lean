module

public import ThePrinciple.Quadruples

/-!
# Justice

`Just` (local Coase), `JustBetween` (between systems), the justice measurement theorem.
-/

@[expose] public section
variable (E : Env)

/-! ### Justice -/

def Friction (s₁ s₂ : E.System) : ℝ := E.TransactionCost s₁ s₂

def Just (s : E.System) : Prop :=
  E.PropertyRightsClear s ∧ Friction E s s = 0 ∧ E.ParetoEfficient s

def JustBetween (s₁ s₂ : E.System) : Prop :=
  E.TransactionCost s₁ s₂ ≤ E.TransactionCost s₂ s₁

theorem coase_implies_just (s : E.System)
    (h_pr : E.PropertyRightsClear s) (h_fr : Friction E s s = 0) :
    Just E s :=
  ⟨h_pr, h_fr, E.axiom_5_coase s h_pr h_fr⟩

theorem justice_measurement_theorem' (s₁ s₂ : E.System)
    (h : JustBetween E s₁ s₂) : E.JusticeDegree s₁ ≥ E.JusticeDegree s₂ :=
  E.justice_measurement_theorem s₁ s₂ h

/-! ## Hegel's theorem (moved out of `Env`) -/

def HegelTheorem (E : Env) : Prop := ∀ s, ¬ E.LearnsFromHistory s
