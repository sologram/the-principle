# zh/ Directory Review Report and Cleanup Recommendations

> Scope of review: all 44 Markdown files under [zh/](../zh/) (read in full on 2026-10-15).
> This document is a read-only review conclusion. No reviewed file was modified; confirm the plan before executing the cleanup.

---

## I. Global Structural Problems and Diagnosis

### 1. Three Generations of Axiom/Law Numbering Mixed Together (the Most Core Self-Consistency Defect)

Three generations of different numbering systems coexist in the repository, and several key axiom pages have an **empty body or a missing statement**, directly weakening the system's declared "correctness is completeness":

| Generation | Scale | Axiom/Law Mapping | Typical Residual Files |
|---|---|---|---|
| **First generation (five laws)** | 0–4, 5 in total | 0 existence, 1 correctness, 2 intention (tends toward completeness), 3 freedom (ignorance), 4 justice (efficiency) | [order-out-of-chaos.md](order-out-of-chaos.md), [q-n-a.md](q-n-a.md), [dephilosophizing.md](dephilosophizing.md), [related-theories.md](related-theories.md), [glossaries-full.md](glossaries-full.md) |
| **Second generation (seven axioms/laws)** | 0–6, 7 in total | 0 existence, 1 correctness, 2 intention, 3 freedom, 4 justice, 5 meaning (price), 6 optimality | [preface-0.md](preface-0.md), [science.md](science.md), [boundary.md](boundary.md), [democracy-freedom.md](democracy-freedom.md) |
| **Third generation (eight axioms, authoritative version)** | 0–7, 8 in total | 0 existence, 1 correctness, 2 intention, **3 games**, 4 freedom, 5 justice, 6 meaning, 7 optimality | [outline.md](outline.md), [toc.md](toc.md), [preface.md](preface.md), [preface-2.md](preface-2.md), [preface-3.md](preface-3.md), [rsi-natural-to-conscious.md](rsi-natural-to-conscious.md) |

**Particularly severe concrete fractures**:

- [the-2nd-axiom.md](the-2nd-axiom.md): the entire file contains only `# 第二 (意图) 公理`; the **body is completely empty** (the statement "things tend toward completeness" and its development are lost).
- [the-4th-axiom.md](the-4th-axiom.md): the entire file contains only `# 第四 (自由) 公理`; the **body is completely empty** (the statement "freedom is ignorance" and its development are lost).
- [the-0th-axiom.md](the-0th-axiom.md): the body's first sentence is "expression over deduction", whereas the authoritative statement in [outline.md](outline.md) and [preface.md](preface.md) is "existence is difference".
- [the-6th-axiom.md](the-6th-axiom.md): the body is an essay about markets and Darwinian evolution; the explicit statement "meaning is price" and its source discussion are missing.
- [democracy-freedom.md](democracy-freedom.md): the body contains `第五公理：意义即价格` and `按第四公理接受效率检验` — these are **second-generation (seven-axiom version)** numbers, and under the current eight-axiom system they should be "Sixth Axiom" and "Fifth Axiom".
- [glossaries-full.md](glossaries-full.md): the foreword says "based on the five laws of The Principle", and the internal definitions (such as the freedom entry, "according to the Third Law") are all first-generation numbering.
- [the-5th-axiom.md](the-5th-axiom.md): the body is only the single sentence "Justice is efficiency.", and it lacks a trailing newline; [the-3rd-axiom.md](the-3rd-axiom.md) and [the-7th-axiom.md](the-7th-axiom.md) are likewise single-sentence files.

**Sole authoritative source for the numbering**: the eight-axiom table in [outline.md](outline.md) (Zeroth existence / First correctness / Second intention / Third games / Fourth freedom / Fifth justice / Sixth meaning / Seventh optimality), consistent with Part II [A0]–[A7] in [toc.md](toc.md). All cleanup work should use that table as its baseline.

---

### 2. Severe Fragmentation and Version Stacking in the Preface System (7 Preface Files)

There are currently as many as 7 preface-related files under zh/, whose positioning and content overlap with each other; readers will easily lose their way:

| File | Current State and Main Features | Recommended Handling |
|---|---|---|
| [preface.md](preface.md) | The formal six-section version (Twilight of the Guild / A Little Superstition / Powerful and Universal / Ordinary Common Sense / A Great Mass of Superstition / Ignorance and Barbarism), mature in style, covering the eight axioms | **Retain as the book's only formal Preface and place it at the top** |
| [preface-0.md](preface-0.md) | The earliest Zhihu answer draft (Serre/Zhang Fa introduction, Zhihu links, the 5/7 laws, a challenge table) | Archive as historical material or as an appendix |
| [preface-2.md](preface-2.md) | "From the Fog of Human Cognition to Absolute Science" (ontology of science vs. the science of human cognition, including the eight-axiom table) | Convert into an introductory chapter of the main text (aligned with Part I of [toc.md](toc.md)) |
| [preface-3.md](preface-3.md) | "Science has always been running" (common sense and engineering, "the stupid method survives") | The content has partly been absorbed into [preface.md](preface.md); it can serve as an introductory subsection or a prelude to the afterword |
| [preface-4.md](preface-4.md) | "Resolving doubts, and what kind of system this is" (system boundaries and clarifications) | Merge into the Q&A / common objections section |
| [preface-5.md](preface-5.md) | "The Emperor's New Clothes and Academic Feudalism" | Merge into Part Six, "De-philosophizing / Critique of the Guild" |
| [preface-6.md](preface-6.md) | A survey of Tao's 2026 open letter and the OpenAI 722-manuscript incident | Highly duplicative of [twilight-of-the-guild-ds.md](twilight-of-the-guild-ds.md); cleanup is recommended |

---

### 3. Duplicates and Unconstrained Expansion of Multi-Model Generated Files

The repository is full of parallel files on the same topic, generated by different models (DeepSeek / Qwen / Doubao / Wenxin / Gemini), with no unified standard:

1. **The "completeness" long essay has 5 copies**:
   - [on-completeness-polysemy-and-compatibility.md](on-completeness-polysemy-and-compatibility.md) (484 lines, the most complete; triple $(S,R,C_S)$ + rejection of falsificationism + references — already a formal trunk paper).
   - `-ds.md` (262 lines) and `-ds2.md` (262 lines): the two are nearly identical (the diff is only a bit over 70 lines, all wording tweaks).
   - `-ds3.md` (231 lines) and `-db.md` (140 lines): early drafts, with titles different from the trunk ("On the Polysemy of 'Completeness' and a Unified Meta-framework").
   - **Recommendation**: keep only the trunk version; archive the other 4 variants to `archive/` or bring them under unified management.
2. **"Twilight of the Guild" has 3 copies**:
   - [preface-6.md](preface-6.md), [twilight-of-the-guild-ds.md](twilight-of-the-guild-ds.md), [twilight-of-the-guild-qw.md](twilight-of-the-guild-qw.md). All three are based on the same event (Tao's 2026 open letter of September–October and the 722 mathematics manuscripts), their structures are exactly isomorphic, and only the statistical details and rhetoric differ slightly (the Qwen version adds details such as "372 result families" plus a paragraph of transitional explanation).
   - **Recommendation**: merge into a single authoritative "Twilight of the Guild" (corresponding to P.1 in the prologue of [toc.md](toc.md)), and remove the parallel redundant copies.
3. **Two parallel glossary tracks coexist**:
   - [glossary.md](glossary.md): a 72-line bare term list, most entries without definitions, containing outdated Zhihu links.
   - [glossaries-full.md](glossaries-full.md): 457 lines of complete term definitions, but based on the old five laws.
   - **Recommendation**: take [glossaries-full.md](glossaries-full.md) as the base, comprehensively revise the law references against the eight-axiom system, and upgrade it to replace the unfinished [glossary.md](glossary.md).

---

### 4. The Table-of-Contents Blueprint ([toc.md](toc.md)) Is Severely Out of Sync with the Repository's Physical Files

[toc.md](toc.md) plans a rigorously structured seven-part monumental work (A0–A7 axioms / D1–D5 definitions / T01–T10 theorems / C01–C08 conjectures / APP applications, plus appendices A–E and an afterword):

- **Current state**: the repository contains not a single file organized along that table-of-contents tree; a large number of theoretical nodes exist only as title lists in [outline.md](outline.md) and [toc.md](toc.md).
- **Front page**: [README.md](README.md) does not link to [toc.md](toc.md), the axiom subsection names are plain text, the "## 应用" (Applications) section is empty, the H1 `# 事物原理` duplicates [outline.md](outline.md), and a temporary "GLM5.1 / ChatGPT" conversation link hangs at the end of the document.

---

## II. File-by-File Review Comments and Recommendation List

| No. | Filename | Current-State Assessment | Targeted Revision Recommendations |
|---|---|---|---|
| 1 | [README.md](README.md) | Front-page navigation is missing; no link to toc; axiom subsection names are plain text; applications section is empty | Rebuild the front page: link the eight axioms, toc.md, outline.md; include application cases such as democracy and Palestine; remove the temporary external chat links |
| 2 | [outline.md](outline.md) | System outline, the most complete in definitions/theorems/conjectures; the H1 is `# 事物原理`, duplicating the README | Change the H1 to `# 事物原理体系大纲`; align the theorem/conjecture numbering with toc.md |
| 3 | [toc.md](toc.md) | A structurally clear ultimate blueprint (a whole-book table-of-contents plan) | Serve as the top-level architectural baseline and the single index for later file restructuring and naming |
| 4 | [the-0th-axiom.md](the-0th-axiom.md) | The body's first sentence "expression over deduction" is inconsistent with the outline's "existence is difference" | Add the standard statement "existence is difference" and include "expression over deduction" as a corollary |
| 5 | [the-1st-axiom.md](the-1st-axiom.md) | Substantial content (scientific completeness, the geocentrism rebuttal, asymmetry) | Keep it, and strengthen the generalization source of the Rationality theorem and the bridging to the triple $(S,R,C_S)$ |
| 6 | [the-2nd-axiom.md](the-2nd-axiom.md) | **Severe defect: the body is completely empty** | Write "things tend toward completeness": generalized Darwinism, evolutionary pressure, elimination mechanisms, the definition of intention |
| 7 | [the-3rd-axiom.md](the-3rd-axiom.md) | The body is only the single sentence "Games are turbulence" | Expand: the minority game, information blockage, the emergence of fluctuation and market dynamics |
| 8 | [the-4th-axiom.md](the-4th-axiom.md) | **Severe defect: the body is completely empty** | Write "freedom is ignorance": the maximum entropy principle, exploration on the ignorance side, a redefinition of free will |
| 9 | [the-5th-axiom.md](the-5th-axiom.md) | The body is only the single sentence "Justice is efficiency", and it lacks a trailing newline | Expand: the Coase theorem, transaction costs, institutional evolution, and a materialist deconstruction of "good" and "bad" |
| 10 | [the-6th-axiom.md](the-6th-axiom.md) | Missing the core statement, goes straight to markets | Add the opening sentence "Meaning is price", and discuss the supply-and-demand principle and distributed continuous pricing |
| 11 | [the-7th-axiom.md](the-7th-axiom.md) | The body is only the single sentence "Principle is optimality" | Expand: Occam's razor, the shortest description (Kolmogorov complexity), and aesthetic criteria |
| 12 | [preface.md](preface.md) | The highest-quality formal six-section preface | Retain as the single main Preface |
| 13 | [preface-0.md](preface-0.md) | Early Zhihu Q&A and the old 5/7 law draft | Move into `archive/` or make it a historical appendix |
| 14 | [preface-2.md](preface-2.md) | Ontology of science vs. the science of human cognition | Turn into an introductory chapter of Part One |
| 15 | [preface-3.md](preface-3.md) | Science survives by the stupid method | Integrate into the introduction or the afterword |
| 16 | [preface-4.md](preface-4.md) | System positioning and doubt-resolving | Integrate into the objections and rebuttals Q&A of Part Six |
| 17 | [preface-5.md](preface-5.md) | Critique of academic feudalism | Integrate into Part Six, "De-philosophizing / De-academization" |
| 18 | [preface-6.md](preface-6.md) | Highly duplicative of twilight | Delete it, or merge it with twilight into a single prologue |
| 19 | [twilight-of-the-guild-ds.md](twilight-of-the-guild-ds.md) / [twilight-of-the-guild-qw.md](twilight-of-the-guild-qw.md) | Parallel copies from two models | Absorb the Qwen version's statistical details and merge into a single `twilight-of-the-guild.md` |
| 20 | [democracy-freedom.md](democracy-freedom.md) | An extremely high-quality reduction of political mechanisms, but residual old axiom numbering (Fifth = meaning, Fourth = justice) | Correct the numbering throughout to the eight-axiom system (Sixth = meaning, Fifth = justice) |
| 21 | [democracy-freedom-orphan-protocol.md](democracy-freedom-orphan-protocol.md) | A highly piercing deconstructive style (Gemini's "orphan protocol" perspective) | Retain it as the "commentary / critique" piece of the democracy-and-freedom part |
| 22 | [palestine-without-politics.md](palestine-without-politics.md) | An application case (the Coase theorem and games applied) | Retain it, and establish formal links to it as an application instance in the README and toc |
| 23 | [on-completeness-polysemy-and-compatibility.md](on-completeness-polysemy-and-compatibility.md) | 484 lines, the most rigorous meta-science trunk paper | **Retain and strengthen it as the theoretical flagship** |
| 24 | on-completeness-\*-ds / ds2 / ds3 / db (4 files) | Historically generated drafts and variant copies | Archive and clean up, to avoid retrieval and maintenance noise |
| 25 | [expel-godel-ds.md](expel-godel-ds.md) | Expelling Gödel: the discourse on definitional authority and RSI, logically incisive | Drop the model suffix and rename to `expel-godel.md`, as the core file for 6.2 |
| 26 | [order-out-of-chaos.md](order-out-of-chaos.md) | An early 5-law framework containing many empty conceptual heading stubs | Restructure it wholesale into an 8-axiom framework; fill in or remove the empty heading stubs |
| 27 | [dephilosophizing.md](dephilosophizing.md) | The body copies order-out-of-chaos extensively | Strip the duplicated content and focus on the "four laws of the love of wisdom" and the criteria against philosophy |
| 28 | [q-n-a.md](q-n-a.md) | Rich content, but still uses "the five laws" and an old falsification table | Update to the eight-axiom system and absorb the latest Q&A clarifications at the end of the outline |
| 29 | [science.md](science.md) | The quadruple of science and the law of science; the axiom table is stuck at 7 axioms (no games) | Add the "Third Axiom (Axiom of Games)" and align it with the eight axioms |
| 30 | [binary-concept-space.md](binary-concept-space.md) | The four-quadruple space construction method (BCS) | Keep it, and strengthen its standing as the core definitions D1–D5 of Part Three |
| 31 | [boundary.md](boundary.md) | The theory of boundaries, deep and good, but with residual old numbering "Fourth Axiom: justice = efficiency" | Update it to "Fifth Axiom: justice is efficiency" |
| 32 | [related-theories.md](related-theories.md) | A table of relations to existing theories, running on "the five laws" throughout | Expand it into a complete comparison of the eight axioms against existing theories |
| 33 | [the-principle-vs-others.md](the-principle-vs-others.md) | A four-model philosophical comparison matrix (Doubao/DeepSeek/Qwen/GLM), opening with `## Doubao` and no H1 | Add the missing H1 title, distill the synthesis table, and make it a core appendix |
| 34 | [battleground-overview.md](battleground-overview.md) | A rhetorically sharp overview of the battlefield (butt and head, NSR, manifold collapse), containing a format-broken "table" | Normalize the table format and the signature; make it the system's declaration-of-war chapter |
| 35 | [rsi-natural-to-conscious.md](rsi-natural-to-conscious.md) | RSI from nature to consciousness: injection of eight-axiom coordinates, internal markets of machines, high in conception (signed Wenxin); contains many `&zwnj;` zero-width non-joiner entities | Clean up the `&zwnj;` typographic residue; retain it as the core trunk article of Part Five |
| 36 | [silence-and-signatures.md](silence-and-signatures.md) | The incentive mechanism analysis of silence when Gödel is misused and of signatures when AI threatens vested interests | Keep it, as a sister piece to "Twilight of the Guild" |
| 37 | [superstition-and-arrogance.md](superstition-and-arrogance.md) | Dissects Gödel's limits and the Hilbert path ("a little superstition, a little arrogance") | The content has partly been absorbed by the preface; it can be kept standalone as a short piece of philosophy of science |
| 38 | [gentle-persuasion.md](gentle-persuasion.md) | Persuasion across species: the machine runs the H-lib demo on Lean/Mathlib to show humans | Keep it and list it under the sections on machine intelligence and conjectures |
| 39 | [glossaries-full.md](glossaries-full.md) | A 457-line glossary table with rich definitions, but based on the old five laws | Replace all law references wholesale (five laws → eight axioms) and let it directly replace glossary.md |
| 40 | [glossary.md](glossary.md) | A 72-line placeholder of bare terms, containing Zhihu links | Discard it, or let the upgraded glossaries-full cover it |

---

## III. Recommended Four-Step Execution Roadmap

Each step can be verified locally and then `git commit` (per project convention: commit directly to master, push only when explicitly requested).

### Step 1: Fill the Empty Axiom Shells and Unify the Numbering (fundamental fix)
1. Complete [the-2nd-axiom.md](the-2nd-axiom.md) (things tend toward completeness) and [the-4th-axiom.md](the-4th-axiom.md) (freedom is ignorance).
2. Expand [the-0th-axiom.md](the-0th-axiom.md) (calibrate it to "existence is difference"), [the-3rd-axiom.md](the-3rd-axiom.md), [the-5th-axiom.md](the-5th-axiom.md), [the-6th-axiom.md](the-6th-axiom.md), and [the-7th-axiom.md](the-7th-axiom.md), so that they reach a scale of exposition comparable to [the-1st-axiom.md](the-1st-axiom.md) (statement / source / boundary / corollary).
3. Correct the axiom number misalignments in [democracy-freedom.md](democracy-freedom.md), [boundary.md](boundary.md), and [science.md](science.md).
4. Upgrade [glossaries-full.md](glossaries-full.md), replacing the "five laws" and the specific law references with the eight-axiom system.

### Step 2: Clean Up Multi-Model Duplicate Variants and Establish an Archive (slimming)
1. Move the 4 on-completeness variants into `zh/archive/`, with the trunk uniformly pointing to [on-completeness-polysemy-and-compatibility.md](on-completeness-polysemy-and-compatibility.md).
2. Merge [preface-6.md](preface-6.md), [twilight-of-the-guild-ds.md](twilight-of-the-guild-ds.md), and [twilight-of-the-guild-qw.md](twilight-of-the-guild-qw.md) into a unified "Twilight of the Guild" (with the model suffixes dropped).
3. Replace the placeholder [glossary.md](glossary.md) with the improved [glossaries-full.md](glossaries-full.md).

### Step 3: Reorganize the Preface Matrix and Reduce Noise (straightening out the entry point)
1. Establish [preface.md](preface.md) as the sole formal Preface (keeping its six-section structure).
2. Archive [preface-0.md](preface-0.md); turn [preface-2.md](preface-2.md) into an introductory chapter; split [preface-4.md](preface-4.md) and [preface-5.md](preface-5.md) into the objections and critique chapters.

### Step 4: Reshape the Front-Page Navigation and Realize the toc Plan
1. **Update [README.md](README.md)**: link the eight axioms and add their Chinese names; link [toc.md](toc.md) and [outline.md](outline.md); hang democracy-freedom, palestine-without-politics, and rsi-natural-to-conscious off the "Applications" section; remove the temporary external chat links at the end.
2. Eliminate the empty heading placeholders in [order-out-of-chaos.md](order-out-of-chaos.md) and [dephilosophizing.md](dephilosophizing.md), and close the loop of the whole book's table-of-contents links.
