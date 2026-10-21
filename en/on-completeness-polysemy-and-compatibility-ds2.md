# On the Polysemy, Non-Equivalence, and Compatibility of "Completeness"
— A Conceptual Analysis Across Mathematics, Logic, and Computation

**Abstract**:  
"Complete" appears frequently in mathematics, logic, computation, and statistics, but its meaning is not single: metric completeness means that Cauchy sequences converge; logical completeness means that semantically valid formulas are provable; completeness of a theory means that every sentence or its negation is provable; Turing completeness means the ability to simulate a Turing machine; statistical completeness means the injectivity of the expectation mapping; order completeness and category completeness mean closure under some class of suprema or limits. This paper argues: these definitions are not equivalent, most of them cannot be directly compared, but they are compatible with one another and can hold simultaneously. What they share is only a weak unifying schema: relative to some class of operations or limits, a system "has no gaps". This paper distinguishes deductive equivalence, semantic equivalence, and definitional equivalence, and points out that conflating different usages leads to category errors. The conclusion is: different senses of "complete" are not equivalent but compatible; genuine incompatibility arises only when one simultaneously affirms and denies within the same domain of discourse and the same sense.

**Keywords**: completeness; Cauchy sequences; logical completeness; completeness of a theory; Turing completeness; category completeness; family resemblance

---

## 1. Introduction

"Complete" is a word of high polysemy in academic language. A beginner in mathematical analysis is told that "the set of real numbers is complete"; a student of mathematical logic hears that "first-order logic is complete, but Peano arithmetic is not complete"; a student of computer science says that "such-and-such a language is Turing complete"; a statistician may discuss "complete statistics". All of these statements use the word "complete", but their definitions, objects, and theoretical backgrounds differ enormously.

Two natural questions thus arise:

1. Are all these definitions of "complete" equivalent?
2. Are they compatible with one another?

The central claim of this paper is: **not equivalent, but compatible.** More precisely:

- They are not different formulations of one concept, but several concepts under one word family;
- Within a single domain, certain completeness statements can be equivalent;
- Across domains, they generally cannot be derived from one another, and cannot even be compared;
- As distinct predicates, they can be simultaneously true without contradiction;
- Only by conflating different senses do apparent conflicts or category errors arise.

This paper first surveys several major definitions of "complete", then analyzes the meanings of "equivalent" and "compatible", and finally proposes a weak unifying schema.

---

## 2. Several Major Concepts of "Completeness"

### 2.1 Metric Completeness and Completeness of the Reals

In a metric space, completeness is defined as follows:

> A metric space $(X,d)$ is complete if and only if every Cauchy sequence in $X$ converges to some point of $X$.

Formally:

$$
\forall (x_n)\subseteq X,\ \text{if }(x_n)\text{ is a Cauchy sequence, then }\exists x\in X,\ x_n\to x.
$$

Intuitively, a complete space has no "missing limit points". The set of rational numbers $\mathbb{Q}$ is not complete: one can construct a Cauchy sequence of rationals converging to $\sqrt2$, but its limit does not lie in $\mathbb{Q}$. The set of real numbers $\mathbb{R}$ is complete, and $\mathbb{R}$ is the completion of $\mathbb{Q}$.

"Completeness of the reals", by contrast, usually refers to a family of equivalent theorems: the least-upper-bound principle, the monotone convergence theorem, the nested interval theorem, the finite cover theorem, the limit-point theorem, the Cauchy convergence criterion, and so on. These propositions are mutually equivalent within the real number system, but they form a family of equivalences within a single domain, and are not the same as the completeness of an arbitrary metric space.

### 2.2 Logical Completeness and Completeness of a Theory

"Complete" in logic has at least two common meanings.

First, **completeness of a logical system**. The strong completeness of first-order logic can be stated as:

$$
\Gamma\vDash \varphi \Rightarrow \Gamma\vdash \varphi.
$$

That is: every formula that follows semantically from $\Gamma$ can be proved in the proof system. The Gödel completeness theorem states precisely the completeness of first-order logic in this sense.

Second, **completeness of a theory**. A formal theory $T$ is complete if and only if for every sentence $\varphi$:

$$
T\vdash \varphi \quad \text{or} \quad T\vdash \neg\varphi.
$$

That is, the theory decides every sentence. Gödel's first incompleteness theorem states that any sufficiently strong, recursively axiomatized, and consistent theory, such as Peano arithmetic, is incomplete.

These two "completeness" notions are frequently confused. In fact, first-order logic as a logical system is complete, while Peano arithmetic as a theory is incomplete; the two do not contradict each other, because they describe properties at different levels.

### 2.3 Computational Completeness: Turing Completeness and NP-Completeness

In the theory of computation, "Turing complete" means that a computational system can simulate a Turing machine, and hence can compute all computable functions. Most general-purpose programming languages are Turing complete. Turing completeness does not mean being able to solve all problems, since the halting problem and the like are not computable.

"NP-complete", meanwhile, is a different sense of "complete". A problem $L$ is NP-complete if:

1. $L\in \mathrm{NP}$;
2. For every $L'\in \mathrm{NP}$, $L'\le_p L$.

Here "complete" is closer to "representing the whole class under reduction" than to "closure under limits". It is a peripheral member of the "completeness" word family, and is not on the same level as Turing completeness.

### 2.4 Statistical Completeness

In statistical inference, a statistic $T$ is complete if for every measurable function $g$:

$$
E_\theta[g(T)]=0,\ \forall \theta \in \Theta
\Rightarrow g(T)=0 \quad \text{almost everywhere}.
$$

Intuitively, a complete statistic contains no "redundant zero information" about the parameter. It has no direct implication relation to metric completeness or logical completeness.

### 2.5 Order Completeness and Category Completeness

In order theory, a partially ordered set can be Dedekind complete: every nonempty subset with an upper bound has a supremum. A complete lattice requires that every subset have both a supremum and an infimum. Order completeness has various variants, each requiring an explicit definition.

In category theory, a category is complete if all small limits exist; cocomplete means that all small colimits exist. Here "small" means that the indexing category of the limit is small, not that the limit itself is small. The categorical language can unify certain "closure under limits" intuitions, but its conditions differ from metric completeness and logical completeness.

---

## 3. Are These Definitions Equivalent?

The answer depends on what "equivalent" means. At least three kinds of equivalence can be distinguished:

### 3.1 Deductive Equivalence

Two propositions can be derived from each other within the same formal system. For example, in the real number system, the least-upper-bound principle and the monotone convergence theorem are equivalent. This is within-domain equivalence.

### 3.2 Semantic Equivalence

Two propositions have the same truth value within the same class of models. For example, in the theory of metric spaces, the formulations "Cauchy sequences converge", "nested closed balls", "completion", and so on can be mutually equivalent.

### 3.3 Definitional Equivalence

Two terms have the same meaning and can be used interchangeably. Cross-domain uses of "complete" clearly do not satisfy this.

Therefore:

- **Within a domain**: certain completeness statements are indeed equivalent. For example, the various theorems of completeness of the reals are equivalent in $\mathbb{R}$; the many characterizations of completeness of a metric space are equivalent.
- **Across domains**: generally not equivalent, and not mutually derivable.
- **Across objects**: not even comparable.

A few counterexamples:

1. **Metric completeness does not imply complete lattices.** Endow any set $X$ with the discrete metric: it is metrically complete; but if $|X|\ge 2$ and $X$ is viewed as a discrete partial order, it is generally not a complete lattice, because $\{a,b\}$ has no supremum. It may still be Dedekind complete, since "nonempty subsets with an upper bound" are extremely rare; so strictly speaking what does not follow is "complete lattice", not all order completeness.
2. **Logical completeness does not imply completeness of a theory.** First-order logic is logically complete, but Peano arithmetic as a theory is incomplete.
3. **Turing completeness does not imply logical completeness.** A programming language can be Turing complete while its type system or logic need not be complete.
4. **Statistical completeness and category completeness are unrelated.** A statistic can be complete while its sample space, viewed as a category, need not be closed under small limits.

So, if "equivalent" means "mutually derivable" or "having the same meaning", the answer is: **not equivalent**.

---

## 4. Are These Definitions Compatible?

"Compatible" here takes its everyday and metatheoretical sense: **able to hold simultaneously, without contradiction, able to coexist within the same theory or the same body of discourse**. It is not the same as the consistency of a formal system, but is related to it.

### 4.1 Predicates of Different Meanings Can Be Simultaneously True

The "completeness" of different domains are different predicates. Let $C_1(x)$ mean "$x$ is metrically complete" and $C_2(x)$ mean "$x$ is logically complete". They apply to different objects, and therefore generally do not conflict.

For example:

- $\mathbb{R}$ is metrically complete;
- $\mathbb{R}$ as an ordered set is also order complete;
- First-order logic is logically complete;
- Peano arithmetic is not complete as a theory;
- Some programming language is Turing complete;
- Some statistic is complete.

These propositions can all be simultaneously true. There is no contradiction among them.

### 4.2 The Same Object Can Satisfy Multiple Kinds of Completeness

Take the set of real numbers $\mathbb{R}$ as an example:

- It is metrically complete;
- It is order complete;
- The various theorems of completeness of the reals hold for it;
- Its theory $\mathrm{Th}(\mathbb{R})$ is complete as a first-order theory.

These "completenesses" are not synonymous, but they can hold simultaneously. This shows that "not equivalent" is not the same as "incompatible".

### 4.3 The Compatibility of Logical Completeness and Incompleteness of a Theory

The most easily misunderstood case concerns Gödel's two theorems:

- The Gödel completeness theorem: first-order logic is complete;
- The Gödel incompleteness theorem: sufficiently strong arithmetic theories are incomplete.

The two do not contradict each other:

- The former says that the proof system is strong enough to prove all semantically valid formulas;
- The latter says that a particular theory cannot decide all sentences.

One is "completeness of a logical system", the other "completeness of a theory". They operate at different levels, and are therefore compatible.

### 4.4 Genuine Incompatibility

Genuine incompatibility occurs only when one simultaneously asserts $P$ and $\neg P$ within the same domain of discourse and the same sense. For example:

- "This metric space is complete" and "this metric space is not complete" are incompatible;
- "The theory $T$ is complete" and "the theory $T$ is not complete" are incompatible.

But these are contradictions internal to a single concept of completeness, not conflicts between different concepts of completeness.

Therefore, different senses of "complete" are compatible; only by mistaking them for a single concept can apparent contradictions arise.

---

## 5. A Weak Unifying Schema: Family Resemblance Rather than a Single Definition

Although these "completenesses" are not equivalent, they are not without connection. They share an abstract schema:

> A system $S$ is complete relative to a class of operations $O$ if the limits, outcomes, proofs, or computations required by $O$ can all be realized within $S$ or captured by $S$.

This can be understood formally as:

$$
\text{Completeness} = \text{Closure} + \text{Existence/Attainability}.
$$

It must be emphasized that this is an **after-the-fact descriptive generalization**, not an **up-front definitional essence**. It does not seek a common essence; it only characterizes the network of overlaps within a family resemblance. Different domains choose different $O$:

| Domain | System $S$ | Operations $O$ | Meaning of completeness |
|---|---|---|---|
| Metric spaces | Metric space | Cauchy limits | Every Cauchy sequence converges within the space |
| Reals | Real number system | Suprema, limits, covers | The least-upper-bound principle and the like hold |
| Logic | Proof system | Semantic consequence | Valid formulas are provable |
| Theory | Formal theory | Decision | Every sentence or its negation is provable |
| Computation | Computational model | Computable functions | Can simulate a Turing machine |
| Statistics | Statistic | Expectation-zero functions | Expectation mapping is injective |
| Order theory | Partial order | Suprema/infima | The relevant subsets have bounds |
| Category theory | Category | Small limits | All small limits exist |

This schema is one of "family resemblance": the members share overlapping features, but there is no single common essence that governs all the uses. A Wittgensteinian "family resemblance" fits well here: they are not one concept, but one word family.

---

## 6. Methodological Consequences

First, **interdisciplinary communication requires explicit definitions**. When saying "this system is complete", one must specify whether this means metric completeness, logical completeness, Turing completeness, or something else.

Second, **avoid category errors**. Asking "which is more complete, Turing completeness or logical completeness" is like asking "which is more mature, an apple or a person". They are not in the same category.

Third, **distinguish logical completeness from completeness of a theory**. The Gödel completeness theorem and the incompleteness theorems do not conflict; they target different objects.

Fourth, **Turing completeness is not omnipotence**. It only means being able to compute all computable functions, not being able to solve incomputable problems.

Fifth, **within-domain equivalence is not cross-domain equivalence**. The theorems of completeness of the reals are equivalent because they share the structure of the real numbers; this equivalence cannot be extrapolated to all uses of "complete".

---

## 7. Conclusion

This paper has examined the principal uses of "complete" in mathematical analysis, logic, computation, statistics, order theory, and category theory. The conclusions are as follows:

1. **These definitions are not equivalent.** They describe different properties of different objects; across domains they generally cannot be derived from one another, and are not even comparable.
2. **They are compatible with one another.** As distinct predicates, they can be simultaneously true and used side by side, without contradiction.
3. **Within a single domain there may exist equivalent formulations.** Examples include the theorems of completeness of the reals and the various characterizations of completeness of a metric space.
4. **Genuine incompatibility arises only when one simultaneously affirms and denies within the same domain of discourse and the same sense.**
5. **They share a weak unifying schema: having no gaps relative to some class of operations.** But this is a family resemblance, not a single definition.

Therefore, the most accurate answer to "Are all these definitions of 'complete' equivalent? Are they compatible?" is:

> **Not equivalent, but compatible. They are polysemous — the same name with different meanings — forming a family of resemblant concepts; incompatibility arises only when affirmation and denial are asserted simultaneously under the same meaning.**

---

## References

1. Rudin, W. *Principles of Mathematical Analysis*. 3rd ed. New York: McGraw-Hill, 1976.
2. Munkres, J. R. *Topology*. 2nd ed. Upper Saddle River: Prentice Hall, 2000.
3. Enderton, H. B. *A Mathematical Introduction to Logic*. 2nd ed. San Diego: Harcourt/Academic Press, 2001.
4. Gödel, K. “Über formal unentscheidbare Sätze der Principia Mathematica und verwandter Systeme I.” *Monatshefte für Mathematik und Physik* 38 (1931): 173–198.
5. Hopcroft, J. E., R. Motwani, and J. D. Ullman. *Introduction to Automata Theory, Languages, and Computation*. 3rd ed. Boston: Pearson Addison-Wesley, 2006.
6. Casella, G., and R. L. Berger. *Statistical Inference*. 2nd ed. Pacific Grove: Duxbury/Thomson Learning, 2002.
7. Mac Lane, S. *Categories for the Working Mathematician*. 2nd ed. New York: Springer, 1998.
8. Awodey, S. *Category Theory*. 2nd ed. Oxford: Oxford University Press, 2010.
9. Davey, B. A., and H. A. Priestley. *Introduction to Lattices and Order*. 2nd ed. Cambridge: Cambridge University Press, 2002.
10. Wittgenstein, L. *Philosophical Investigations*. Oxford: Basil Blackwell, 1953.
