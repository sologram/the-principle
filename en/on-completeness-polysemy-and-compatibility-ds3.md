# On the Polysemy of "Complete" and a Unified Meta-Framework — with the Concept of Completeness in The Principle of Things

## Abstract

"Complete" appears widely in everyday language, engineering practice, mathematical analysis, mathematical logic, model theory, and the ontology of The Principle of Things. These uses superficially share the naive intuition of "no omission, no escape," but each domain has its own independent formal definition, and they cannot be directly equated. This paper surveys five classes of completeness concepts, analyzing their domains, judgment rules, and core meanings; it proposes a triple $(S,R,C)$ meta-framework that subsumes the different versions of completeness as special cases for comparison. With this framework, the paper repositions Gödel's incompleteness theorems: they describe the failure of closure of a particular formal system relative to a particular semantic standard, not "the incompleteness of objective existence itself." Finally, the paper discusses the presuppositions, circularity risks, and theoretical value of the meta-framework, and explains that the view of completeness in The Principle of Things is an ontological theoretical commitment that cannot be directly derived from — or refuted by — Gödel's theorems.

**Keywords**: completeness; complete space; formal-system completeness; model theory; The Principle of Things; boundary; escape; Gödel's theorems

## 1. Introduction

Across different branches of knowledge, "complete" is a high-frequency term. In engineering we speak of complete documentation and complete testing; real analysis has complete metric spaces; mathematical logic distinguishes semantic completeness, syntactic completeness, and theory completeness; model theory defines complete theories; and The Principle of Things defines completeness at the ontological level.

The academic community usually assumes by default that these are instances of polysemy, sharing only a vague intuition and possessing no unified form. But we may ask: do these "completeness" notions share a common structure? Can we construct a meta-definition that places the completeness of ontology, mathematics, logic, and engineering under the same language for comparison?

This paper will set out the definitions of each version of completeness in turn, then establish a unified framework, contrast the differences, clarify the position of Gödel's incompleteness theorems within the meta-framework, and the unique position of the completeness view of The Principle of Things. It should be stated in advance: the "The Principle of Things" discussed in this paper is an ontological theoretical commitment, not a theorem of mathematical logic; its delimitation of completeness requires independent justification and cannot be derived from Gödel's theorems alone.

## 2. Definitions of "Complete" across Domains

### 2.1 Completeness in Engineering and Everyday Contexts

**Definition**: With respect to a given task goal, all the elements required to accomplish that task are included, with no necessary item missing.

- Set $S$: the set of elements required to complete the task;
- Rule $R$: the screening rule for elements needed by the task;
- Judgment criterion $C$: the human goal requirement, i.e., which elements "ought to belong to $S$";
- Completeness judgment: every object judged by $C$ to be a task-essential element belongs to $S$.

Characteristics: the boundary $S$ is drawn by humans; the concept is qualitative and practical, without strict formalization. Completeness or incompleteness depends on human needs; there is no absolute completeness detached from a goal.

Example: a complete requirements document means that all the constraints, interfaces, and scenarios needed for project development have been written down.

### 2.2 Real Analysis: Complete Metric Spaces

**Definition**: A metric space $(S,d)$ is complete if and only if the limit of every Cauchy sequence in the space belongs to the set $S$.

- Set $S$: the point set of the space;
- Rule $R$: the operation of taking limits of Cauchy sequences;
- Judgment criterion $C$: determined by the metric structure, that "limit points ought to belong to the space";
- Completeness judgment: the limits of all Cauchy sequences do not escape $S$.

Example: the set of rational numbers $\mathbb{Q}$ is not complete — there exist Cauchy sequences converging to $\sqrt{2}$, and $\sqrt{2}\notin S$; the set of real numbers $\mathbb{R}$ is complete — the limit of every Cauchy sequence of real numbers is still a real number.

Key point: completeness is the closure of a set with respect to **the limit operation on Cauchy sequences**, and has nothing to do with propositions or proofs.

### 2.3 Mathematical Logic: Completeness Theorems and Incompleteness Theorems

In mathematical logic, at least three layers of "complete" need to be distinguished.

#### (1) Semantic completeness of a logical system: the Gödel completeness theorem

The proof system of first-order predicate calculus is semantically complete:

$$
\Gamma \models \varphi \;\Rightarrow\; \Gamma \vdash \varphi .
$$

That is, if a formula $\varphi$ is true in all models satisfying $\Gamma$, then $\varphi$ can be formally proved from $\Gamma$. This is the result of Gödel's 1929 doctoral dissertation, usually called the **Gödel completeness theorem**.

- Set $S$: the set of formulas provable from $\Gamma$;
- Rule $R$: formal proof;
- Judgment criterion $C$: logical validity, i.e., truth in all relevant models;
- Completeness judgment: all logically valid formulas belong to $S$.

#### (2) Syntactic completeness of a theory

A first-order theory $T$ is called syntactically complete if and only if, for every sentence $\varphi$,

$$
T \vdash \varphi \quad \text{or} \quad T \vdash \neg \varphi .
$$

That is, the theory passes judgment on every sentence.

#### (3) Semantic completeness of a theory relative to its models

A theory $T$ is called semantically complete relative to its class of models if and only if all sentences true in all models of $T$ are provable in $T$. For first-order theories, syntactic completeness and this semantic completeness are equivalent under common conditions.

#### (4) Gödel's incompleteness theorems

The precise statement of Gödel's first incompleteness theorem is:

> Any recursively axiomatized, consistent formal theory $T$ containing enough arithmetic (such as Robinson arithmetic $Q$ or Peano arithmetic $PA$) has a sentence $G$ such that $T \nvdash G$ and $T \nvdash \neg G$. In Gödel's original form, if $T$ is $\omega$-consistent, both $G$ and $\neg G$ are unprovable; after Rosser's improvement, an undecidable sentence can be obtained requiring only that $T$ be consistent.

Gödel's second incompleteness theorem says:

> Any recursively axiomatized, consistent theory $T$ containing enough arithmetic cannot prove its own consistency $\mathrm{Con}(T)$ within $T$.

In this logical setting, the meaning of incompleteness is: there exist propositions that are true by the semantic standard but escape the set $S$ of provable propositions. This incompleteness is not a matter of the model or the world lacking facts, but of **the proof tools inside the system being insufficient to capture all semantically true propositions**.

### 2.4 Model Theory: Complete Theories

**Definition**: A first-order theory $T$ is called a complete theory if and only if any two models of the theory satisfy exactly the same first-order sentences; equivalently, for each first-order sentence $\varphi$, $T \vdash \varphi$ or $T \vdash \neg \varphi$.

- Set $S$: the set of theorems of the theory $T$;
- Rule $R$: first-order logical deduction;
- Judgment criterion $C$: truth in all models of $T$;
- Completeness judgment: no sentence can be written in the language that distinguishes any two models of $T$.

The role of a complete theory: the theory fixes the truth values of all sentences at the level of its language. Note that this essentially coincides with the syntactic completeness of Section 2.3, differing only in the angle of formulation.

### 2.5 Completeness in the System of The Principle of Things

The system of The Principle of Things puts forward an ontological postulate:

> **Correctness is completeness.**

Its concept of completeness can be stated as:

**Definition**: A descriptive system or proposition is complete if and only if the system contains **all the relevant differences** corresponding to the object under discussion, and no difference falling within the scope of discussion lies outside the system.

- Set $S$: the set of all differences relevant to the object;
- Rule $R$: the generation of all relevant differences of the object;
- Judgment criterion $C$: objective relevance, i.e., which differences belong to the object under discussion;
- Completeness judgment: all relevant differences are within $S$, and no difference escapes.

This is completeness at the ontological level. The meaning of incompleteness here is: the descriptive system has missed real differences.

It must be emphasized that, from the perspective of The Principle of Things, the incompleteness Gödel speaks of is not that existence itself is incomplete; it is merely that the artificially chosen boundary $S$ of the formal system causes some true propositions to escape. At the ontological level, the totality of differences of existence is complete. But this claim is itself a theoretical commitment of The Principle of Things and requires independent argument; it cannot be directly derived from Gödel's theorems, nor is it a logical negation of them.

## 3. A Unified Meta-Framework: The Triple Definition of Completeness

> **Meta-definition**: Given an object domain $X$, a boundary set $S \subseteq X$, a generative rule $R$, and an external judgment criterion $C: X \to \{\text{ought to belong to }S,\ \text{ought not to belong to }S\}$. If all objects generated by $R$ and judged by $C$ to "ought to belong to $S$" actually fall within $S$, then the triple $(S,R,C)$ is said to be complete.

Formally:

$$
\forall x \in X,\quad \bigl( R(x) \ \text{and}\ C(x)=\text{ought to belong to }S \bigr) \;\Rightarrow\; x \in S .
$$

Completeness is **not a property of the set $S$ alone, but a property of the triple $(S,R,C)$**. Changing the boundary $S$, the generative rule $R$, or the judgment criterion $C$ can directly flip completeness.

We convert all five classes of completeness above into special cases of the meta-framework:

1. **Everyday engineering completeness**: $S$ = the set of task elements; $R$ = task decomposition and screening; $C$ = judgment of task necessity; complete: all essential elements $\in S$.
2. **Complete metric space**: $S$ = the point set of the space; $R$ = taking limits of Cauchy sequences; $C$ = limit points ought to belong to the space; complete: all Cauchy limits $\in S$.
3. **Semantic completeness of a formal system**: $S$ = the set of provable propositions; $R$ = formal proof; $C$ = logical validity or truth in all models; complete: all semantically true propositions $\in S$.
4. **Model-theoretic complete theory**: $S$ = the set of theorems of the theory; $R$ = first-order deduction; $C$ = truth in all models of the theory; complete: sentences satisfied by every model $\in S$.
5. **Completeness of The Principle of Things**: $S$ = the totality of differences relevant to the object; $R$ = difference generation; $C$ = objective relevance; complete: all relevant differences $\in S$.

### 3.1 The Core Shared Intuition

All completeness concepts share the same underlying intuition: **closure, no escape**. What is generated by the rules and ought to belong to the scope does not run outside the set.

### 3.2 The Key Difference: the Source of "Ought to Belong to $S$"

This is the most important fork among the versions of completeness:

1. Mathematical analysis: "ought to belong to $S$" comes from the sequence itself, with the limit defined by the metric structure;
2. Mathematical logic: "ought to belong to $S$" comes from external semantic models, which supply the truth values of propositions;
3. Model theory: "ought to belong to $S$" comes from all models of the theory;
4. The Principle of Things: "ought to belong to $S$" comes from the totality of differences inherent in objective existence;
5. Engineering: "ought to belong to $S$" comes from human goal requirements.

That is to say, **completeness always depends on an external judgment criterion $C$**, used to judge which objects "ought to belong to $S$."

## 4. Comparison and Compatibility Analysis under the Meta-Framework

### 4.1 At the Level of Strict Definitions: Not Mutually Derivable

Different completenesses are properties of different $(S,R,C)$ triples.

- That a formal system is semantically complete does not mean the model corresponding to it is a complete metric space;
- The completeness of a metric space has no relation of logical derivation with a model-theoretic complete theory.

They are not equivalent propositions and cannot be used interchangeably. The word is the same; the domains are entirely different.

### 4.2 At the Structural Level: A Shared Abstract Closure Pattern, but Not Strict Isomorphism

At the level of the meta-framework's structure, all completeness concepts share the same closure paradigm: relative to some boundary, rule, and judgment criterion, there is no object that "ought to belong but escapes." This is why humans use the same word, "complete," to name them.

But this is not "isomorphism" in the mathematical sense. Isomorphism requires a structure-preserving bijection; completeness concepts from different domains are merely embeddable into the same abstract framework, not strictly isomorphic. A more accurate formulation is therefore:

> The verbal intuitions are compatible, the formal definitions are not interchangeable; the structural paradigms are compatible, the concrete meanings are not equivalent.

### 4.3 Reinterpreting Gödel's Incompleteness Theorems

Fit into the meta-framework, the triple Gödel discusses is:

- $S$ = the set of propositions provable within the formal system;
- $R$ = formal proof;
- $C$ = truth in the standard model of arithmetic.

Conclusion: when the system is strong enough, recursively axiomatized, and consistent, there exist objects (true propositions) that by the rule $C$ ought to belong to $S$ but are not in $S$. Therefore $(S,R,C)$ is incomplete.

The Principle of Things emphasizes: this incompleteness is **the result of the chosen boundary $S$, the deduction rules $R$, and the semantic standard $C$**, not that objective existence — the totality of differences — is itself incomplete. At the ontological level, the totality of differences corresponding to existence constitutes another triple $(S',R',C')$, and The Principle of Things commits that this ontological set is complete.

But caution is required here: if the "ontological completeness" of The Principle of Things is also relative to some $S',R',C'$, then it is still a relative completeness, only with its boundary set to "existence itself." It therefore does not contradict "all completeness is relative," but pushes the frame of reference of the "relative" up to the ontological level. If The Principle of Things claims an absolute completeness, additional argument is needed, along with an explanation of how it avoids the conclusion that "all completeness is relative."

> This is the deepest divergence between The Principle of Things and traditional philosophy of mathematics: traditional mathematical logic usually discusses completeness only within formal systems and does not directly make ontological assertions; The Principle of Things further claims that incompleteness is always an effect of boundary choice, while the totality of differences of existence itself is complete. The latter is an ontological stance, not a logical corollary of Gödel's theorems.

## 5. Problems with the Meta-Framework

### 5.1 The Presupposition Problem of "Ought to Belong to $S$"

The meta-definition relies on the external judgment criterion $C$ of "ought to belong to $S$." Does this criterion itself need to be complete? Once we use another set to define what "ought to belong to $S$" means, there is a risk of infinite regress.

Example: in The Principle of Things, "relevant differences" require delimiting in advance the scope of the object under discussion, distinguishing which differences are relevant and which are not. The delimitation of the boundary is itself a prior choice.

### 5.2 The Risk of Self-Referential Circularity

When $S$ contains propositions describing itself, a self-referential structure arises. The unprovable proposition constructed by Gödel is an indirect self-reference achieved through arithmetic coding. Under the meta-framework, self-reference is only a special case under the combination of boundary $S$, rule $R$, and judgment criterion $C$, not a necessary ontological property.

### 5.3 The Relation between Consistency and Completeness

- **Consistency**: within the set $S$ there are no mutually contradictory elements (it cannot simultaneously admit $P$ and $\neg P$).
- **Completeness**: all elements that, by rule $R$ and criterion $C$, ought to enter are within $S$.

These are independent properties:

- One can be consistent but incomplete (Gödel's arithmetical systems);
- One can be complete but inconsistent (an inconsistent system, in which all propositions are provable — syntactically complete).

## 6. Conclusion

1. The "complete" of everyday usage, analysis, mathematical logic, model theory, and The Principle of Things are instances of polysemy: their strict definitions cannot be substituted for one another; but they share a unified structural paradigm and can be encapsulated in the $(S,R,C)$ meta-definition: **given a boundary set $S$, a generative rule $R$, and a judgment criterion $C$, if all objects that by $C$ ought to belong to $S$ and are generated by $R$ fall within $S$, then $(S,R,C)$ is complete**.
2. All completeness is a relative concept; there is no absolute completeness detached from boundary, rule, and judgment criterion. Changing $S$, $R$, or $C$ can change completeness.
3. Gödel's incompleteness theorems describe the escape phenomenon of a particular $(S,R,C)$ triple — **the failure of closure of the proof set relative to a semantic model** — and cannot be generalized to the incompleteness of objective existence itself. This is the footing of the completeness view of The Principle of Things: the universe consisting of all relevant differences corresponding to existence is complete at the level of ontological commitment; incompleteness occurs only in artificially excerpted, finite descriptive systems.
4. The main shortcoming of the meta-framework lies in its dependence on an external judgment criterion $C$, with the problems of the prior choice in boundary definition and infinite regress. This is a direction for further research.
5. The "correctness is completeness" of The Principle of Things is an ontological postulate, not a direct corollary of Gödel's theorems. To make it a rigorous theory, one must further define "correct," "relevant differences," and "objective relevance," and explain its mode of justification independent of formal systems.

## References

[1] Gödel, K. *Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I*. Monatshefte für Mathematik und Physik, 1931.  
[2] Gödel, K. *Über die Vollständigkeit des Logikkalküls*. Dissertation, 1929.  
[3] Franzén, T. *Gödel's Theorem: An Incomplete Guide to Its Use and Abuse*. A K Peters, 2005.  
[4] Enderton, H. B. *A Mathematical Introduction to Logic*. 2nd ed., Academic Press, 2001.  
[5] Kunen, K. *Set Theory: An Introduction to Independence Proofs*. North-Holland, 1980.  
[6] Hao Zhaokuan. *Mathematical Logic: An Introduction to Proof Theory* [M]. Fudan University Press.  
[7] Zorich, V. A. *Mathematical Analysis* [M]. Higher Education Press.  
[8] Zhang Yi. *Foundations of Model Theory* [M]. Science Press.  
[9] Theory manuscripts of The Principle of Things.
