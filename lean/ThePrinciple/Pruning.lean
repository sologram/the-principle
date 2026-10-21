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

/-- Prune the non-ignorant "free": full knowledge claimed as freedom
(= order in disguise). -/
def PruneOmniscient (s : E.System) (t : E.Time) : Prop := Order E s t

/-- Prune the inefficient "just": zero self-friction without Pareto efficiency.
Per Axiom 5 (`axiom_5_coase`) this never fires on a Coase-valid system; the
branch is kept to mirror the text's fifth pruning and stays falsifiable. -/
def PruneInefficient (s : E.System) : Prop :=
  E.TransactionCost s s = 0 ∧ ¬ E.ParetoEfficient s

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
