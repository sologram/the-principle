# On the Polysemy of "Completeness" and a Unified Meta-Framework — With a Discussion of the Concept of Completeness in The Principle (of Things)

## Abstract
"Complete" appears widely in everyday language, engineering practice, mathematical analysis, mathematical logic, model theory, and the ontology of The Principle (of Things). On the surface these share the naive intuition of "nothing missing, nothing escaping," but each field has its own independent formal definition, and they cannot be directly equated. This paper surveys five classes of complete concepts, clarifying their domains, judgment rules, and core meanings; it then proposes a general meta-definition that accommodates all versions of completeness as special cases within one framework. Using this meta-framework, the paper contrasts the incompleteness results of traditional mathematics and logic with the view of completeness of The Principle (of Things), and points out that incompleteness is always a composite property of a **boundary set $S$ plus its corresponding operational rules**, not a property inherent in existence itself. Finally, the paper discusses the presuppositions, circularity risks, and theoretical value of the meta-framework.

**Keywords**: completeness; complete space; completeness of formal systems; model theory; The Principle (of Things); boundary; escape

## 1. Introduction
Across branches of knowledge, "complete" is a high-frequency term. In engineering one speaks of complete documentation and complete testing; real analysis has complete metric spaces; mathematical logic distinguishes semantic completeness and syntactic completeness; model theory defines complete theories; The Principle (of Things) defines completeness at the ontological level.
Scholars usually take these to be polysemy — same name, different meanings — sharing only a vague intuition with no unified form. But we may ask: do these "completenesses" share a common structure? Can we construct a meta-definition that places the completeness of ontology, mathematics, logic, and engineering under the same language for comparison?
This paper develops the definitions of each version of completeness in turn, then builds a unified framework, contrasts their differences, clarifies the position of Gödel's incompleteness theorems within the meta-framework, and identifies the distinctive position of the view of completeness held by The Principle (of Things).

## 2. Definitions of "Completeness" Across Fields
### 2.1 Completeness in Engineering and Everyday Contexts
**Definition**: With respect to a given task goal, all elements needed to accomplish the task are included, with no required item missing.
- Set $S$: the set of elements required to complete the task;
- Rule: the screening rule for task-required elements;
- Completeness judgment: all task-essential elements belong to $S$.

Characteristics: the boundary $S$ is drawn by human choice; the concept is qualitative and practical, without strict formalization. Whether something is complete depends on human needs; there is no absolute completeness.
Example: a complete requirements document means all constraints, interfaces, and scenarios needed for project development have been spelled out.

### 2.2 Real Analysis: Complete Metric Spaces
**Definition**: A metric space $(S,d)$ is complete if and only if the limit of every Cauchy sequence in the space belongs to the set $S$.
- Set $S$: the set of points of the space;
- Rule: the operation of taking limits of Cauchy sequences;
- Completeness judgment: the limits of all Cauchy sequences do not escape $S$.

Example: the set of rationals $\mathbb{Q}$ is not complete — there exist Cauchy sequences converging to $\sqrt{2}$, and $\sqrt{2}\notin S$; the set of reals $\mathbb{R}$ is complete — the limit of every Cauchy sequence of reals is still a real number.
Key point: completeness here is the closure of a set under the **limit operation**, unrelated to propositions or proofs.

### 2.3 Mathematical Logic: Completeness of Formal Systems
Distinguishing semantic completeness from syntactic completeness.
1. **Semantic completeness**: For a formal system, every well-formed formula true in a model can be proved within the system.
    - $S$: the set of provable propositions within the system;
    - Rule: semantic valuation (truth in a model);
    - Completeness judgment: all propositions true in models belong to the provable set $S$.
2. **Syntactic completeness**: For any proposition $P$, the system can prove at least one of $P$ or $\neg P$.

Gödel's incompleteness theorems: **a sufficiently strong, consistent formal system containing elementary arithmetic cannot be semantically complete**.
In this logic, incompleteness means: there exists a proposition true in a model that escapes the set $S$ of provable propositions.
Note: this incompleteness is not a lack of facts in the model/world, but that **the proof apparatus internal to the system is insufficient to capture all semantically true propositions**.

### 2.4 Model Theory: Complete Theories
**Definition**: A first-order theory $T$ is called a complete theory if and only if any two models of the theory satisfy exactly the same first-order sentences.
- $S$: the set of sentences expressible by the theory $T$;
- Rule: a model satisfies a sentence;
- Completeness judgment: no sentence in the language can distinguish any two models of the theory.

The role of a complete theory: at the level of its language, the theory fixes the truth value of all sentences.

### 2.5 Completeness in The Principle (of Things)
The axiom of The Principle (of Things): **correctness is completeness**.
**Definition**: A descriptive system or proposition is complete if and only if the system contains **all relevant differences** corresponding to the object under discussion, and no difference within the scope of the discussion falls outside the system.
- $S$: the set of all differences relevant to the object;
- Rule: generating all relevant differences of the object;
- Completeness judgment: all relevant differences are within $S$, with no difference escaping.

This is completeness at the ontological level. Incompleteness here means: the descriptive system has omitted real differences.
> From the perspective of The Principle (of Things): the incompleteness Gödel spoke of is not an incompleteness of existence itself; it arises only from an artificially chosen formal-system boundary $S$, which causes some true propositions to escape. At the ontological level, the totality of differences of existence is complete.

## 3. The Unified Meta-Framework: A General Meta-Definition of Completeness

> **Meta-definition**: Given a boundary set $S$ and a set of corresponding generation/judgment rules $R$; if all objects that, according to the rules $R$, "ought to belong to $S$" in fact fall inside $S$, then $(S,R)$ is complete.

Completeness **is not a property of the set $S$ alone, but a property of the pair $(S,R)$**. Change the boundary $S$, or change the rules $R$, and completeness can flip outright.

We convert all five preceding classes of completeness into special cases of the meta-framework:
1. Everyday engineering completeness: $S$ = the set of task elements; $R$ = screening of task-essential elements; complete: all essential elements $\in S$.
2. Complete metric space: $S$ = the set of points of the space; $R$ = taking limits of Cauchy sequences; complete: all Cauchy limits $\in S$.
3. Semantic completeness of formal systems: $S$ = the set of provable propositions; $R$ = semantic truth in a model; complete: all semantically true propositions $\in S$.
4. Model-theoretic complete theory: $S$ = the set of sentences of the theory; $R$ = a model satisfies a sentence; complete: sentences satisfied by any model $\in S$.
5. Completeness of The Principle (of Things): $S$ = the totality of differences relevant to the object; $R$ = generating all relevant differences of the object; complete: all relevant differences $\in S$.

### 3.1 The Core Shared Intuition
All concepts of completeness share the same underlying intuition: **closure, no escape**.
Things generated by the rules that ought to belong to the scope do not run outside the set.

### 3.2 The Key Difference: the Source of "Ought to Belong to $S$"
This is the most important fork among the versions of completeness:
1. Mathematical analysis: "ought to belong to $S$" comes from the sequence itself, with the limit defined by the metric structure;
2. Mathematical logic: "ought to belong to $S$" comes from the external semantic model, with the model giving the truth values of propositions;
3. The Principle (of Things): "ought to belong to $S$" comes from the totality of differences inherent in objective existence;
4. Engineering: "ought to belong to $S$" comes from human goals and needs.

In other words, **completeness always depends on an external criterion of judgment**, used to decide which objects "ought to belong to $S$".

## 4. Comparison and Compatibility Analysis Within the Meta-Framework
### 4.1 At the Level of Strict Definition: Not Mutually Derivable
Different completenesses are properties of different pairs $(S,R)$.
- That a formal system is semantically complete does not mean its corresponding model is a complete metric space;
- The completeness of a metric space has no logical derivation relation to model-theoretic complete theories.

They are not equivalent propositions and cannot be used interchangeably. The word is the same; the domains are entirely different.

### 4.2 At the Structural Level: Isomorphic, Compatible
At the structural level of the meta-framework, all concepts of completeness are **isomorphic**: they all fit the $(S,R)$ closure paradigm.
This is why humanity names them all with the same word, "complete".
> Distinction: word intuition is compatible, formal definitions are not; the structural paradigm is compatible, the concrete meanings are not equivalent.

### 4.3 Reinterpreting Gödel's Incompleteness Theorems
Plugging into the meta-framework:
The pair $(S,R)$ Gödel discussed:
$S$ = the set of propositions provable within the formal system;
$R$ = truth in the arithmetic model.

Conclusion: when the system is sufficiently strong and consistent, there exist objects (true propositions) that, by the rules $R$, ought to belong to $S$, yet are not in $S$.
Therefore $(S,R)$ is incomplete.
The Principle (of Things) emphasizes: this incompleteness is **the result of the chosen boundary $S$ and derivation rules $R$**, not an incompleteness of objective existence or of the totality of differences itself.
At the ontological level, the totality of differences corresponding to existence constitutes another pair $(S',R')$, and this ontological set is complete.
> This is the deepest divergence between The Principle (of Things) and traditional philosophy of mathematics: the traditional view tends to regard incompleteness as an inherent limitation of formal systems as such; The Principle holds that incompleteness is always an effect produced by the choice of boundary.

## 5. Problems With the Meta-Framework
### 5.1 The Presupposition Problem of "Ought to Belong to $S$"
The meta-definition relies on the external criterion "ought to belong to $S$". Does this criterion itself need to be complete?
Once we use another set to define what "ought to belong to $S$" means, there is a risk of infinite regress.
Example: in The Principle (of Things), "relevant differences" require a pre-drawn scope of the object under discussion, distinguishing which differences are relevant and which are not. Drawing the boundary is itself an antecedent choice.

### 5.2 The Risk of Self-Referential Circularity
When $S$ contains propositions describing itself, a self-referential structure appears. The unprovable proposition constructed by Gödel is precisely self-referential.
Under the meta-framework, self-reference is only a special case under the combination of the boundary $S$ and the rules $R$, not a necessary ontological property.

### 5.3 The Relation Between Consistency and Completeness
Consistency: within the set $S$ there are no mutually contradictory elements (it cannot simultaneously contain $P$ and $\neg P$).
Completeness: elements that ought to enter by the rules $R$ are all within $S$.
The two are independent properties.
- One can be consistent but incomplete (Gödel's arithmetic system);
- One can be complete but inconsistent (contradictory systems, in which all propositions are provable — syntactically complete).

## 6. Conclusion
1. The "completeness" of everyday life, analysis, mathematical logic, model theory, and The Principle (of Things) is polysemy: the strict definitions cannot substitute for one another; yet they share a unified structural paradigm and can be encapsulated in the $(S,R)$ meta-definition: **given a boundary set $S$ and rules $R$, if all objects that by $R$ ought to belong to $S$ fall within $S$, then $(S,R)$ is complete**.
2. All completeness is a relative concept; there is no absolute completeness apart from boundaries and rules. Changing $S$ or $R$ can change completeness.
3. Gödel's incompleteness theorems describe the escape phenomenon of a particular pair $(S,R)$ — **the failure of closure of the proof set relative to the semantic model** — and cannot be generalized to say that objective existence itself is incomplete. This is the footing of the view of completeness of The Principle (of Things): the totality constituted by all relevant differences corresponding to existence is complete at the ontological level; incompleteness occurs only in the finite descriptive system artificially carved out of it.
4. The main shortcoming of the meta-framework lies in its dependence on the external criterion "ought to belong to $S$", with the problem of the antecedent choice involved in defining the boundary; this is a direction for further research.

## References (placeholder examples)
[1] Hao Zhaokuan. Mathematical Logic: An Introduction to Proof Theory [M]. Fudan University Press.\
[2] Zorich. Mathematical Analysis [M]. Higher Education Press.\
[3] Zhang Yi. Foundations of Model Theory [M]. Science Press.\
[4] Theoretical manuscripts of The Principle (of Things).
