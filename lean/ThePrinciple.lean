module

public import ThePrinciple.Basic
public import ThePrinciple.Epistemic
public import ThePrinciple.Quadruples
public import ThePrinciple.Justice
public import ThePrinciple.Pruning
public import ThePrinciple.Models.Canonical
public import ThePrinciple.Models.Nontrivial
public import ThePrinciple.Godel

/-!
# The Principle — Lean 4 Formalization (Canonical v8)

This file is the root library module of `lake build`
(`defaultTargets = ["the_principle"]` in `lakefile.toml`), i.e. the sole
canonical formalization entry point of this project. `the_principle_1.lean`
and `_2`–`_7` are historical drafts and do not participate in the build.

## Module structure

- `ThePrinciple.Basic`: `Valuation` and the full environment `Env`
  (data carriers + axiom constraints) + `Correct`.
- `ThePrinciple.Epistemic`: epistemic quadruple (free/order/slavery/license)
  and mutual-exclusion theorems.
- `ThePrinciple.Quadruples`: cultural-practice / scientific / democratic
  quadruples, truth-goodness-beauty, subjective/objective,
  credit and nonexistence, turbulence, meaning.
- `ThePrinciple.Justice`: `Just` / `JustBetween` / `JusticeDegree`,
  Hegel's theorem.
- `ThePrinciple.Pruning`: `ShouldPrune`.
- `ThePrinciple.Models.Canonical`: degenerate model (fast validation).
- `ThePrinciple.Models.Nontrivial`: nontrivial model + consistency theorem
  + nontriviality checks.
- `ThePrinciple.Godel`: Gödel framework and `HilbertProcessConjecture`
  (open conjecture).

## Formalized

- Axioms 0, 2, 3, 5, 7; boundary idempotence; quadruple mutual exclusion.
- Epistemic quadruple: free / order / slavery / license.
- Cultural-practice quadruple: science / philosophy / religion / engineering.
- Scientific quadruple: natural science / social science / mathematics / metascience.
- Democratic quadruple: democracy / populism / autocracy / dictatorship.
- Justice: `Just` (local Coase), `JustBetween` (between systems), `JusticeDegree`.
- Meaning: `Price` (engineering layer) / `Meaning` (definition layer, a Prop).
- Truth-goodness-beauty: `Truthful` = correct; `Good` = efficiency;
  `Cooperative` = 善; `Beautiful` = competitiveness on a crossing.
- Credit: `Credit` = commitment ∧ fulfillment (a record, not a degree).
- Pruning: the five prunings + the pruning theorem
  (`pruning_theorem`, `pruning_pseudo_just`, `pruning_pseudo_free`, …).
- Extraterritorial enforcement: `judgment_via_count` / `jurisdiction_local`.
- Axiom 2 as a statistical trend (`axiom_2_trend`, evolving systems only).
- Gödel framework and `HilbertProcessConjecture` (open conjecture).

## Not yet formalized (future work)

- Full semantics of "nonexistent = wrongly existing"
  (only the `Nonexistent` / `Wrong` skeletons are given).
- Substantive content of "credit as the first value"
  (`Credit` is the binary record; the numeric ledger is future work).
- The statistical claim that "very little of what is called social science is science".
- Engineering plans such as atomic utility theory, the twin-market model,
  and the Principle SFT corpus.

Honest disclaimer: this is a skeleton — neither "Gödel solved"
nor "unified science delivered".
-/
