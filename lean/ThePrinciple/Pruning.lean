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

def ShouldPrune (s : E.System) (t : E.Time) : Prop :=
  (¬ Correct E s t) ∨
  Order E s t ∨
  (Just E s ∧ ¬ E.ParetoEfficient s)

theorem pruning_incorrect (s : E.System) (t : E.Time)
    (h : ¬ Correct E s t) : ShouldPrune E s t :=
  Or.inl h
