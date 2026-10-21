# zh/ 目录审查报告与整理建议

> 审查范围：[zh/](../zh/) 下全部 44 个 Markdown 文件（2026-10-15 全量通读）。
> 本文档为只读审查结论，未改动任何被审文件；执行整理前请先确认方案。

---

## 一、全局结构性问题与诊断

### 1. 公理/定律编号体系的三代混杂（最核心的自洽性缺陷）

仓库内存在三代不同的编号系统并存，且多处关键公理页存在**正文空壳或陈述缺失**，直接削弱了体系声明的“正确即完备”：

| 代际 | 规模 | 公理/定律映射 | 典型残留文件 |
|---|---|---|---|
| **第一代（五定律）** | 0~4 共 5 个 | 0 存在、1 正确、2 意图（趋完备）、3 自由（无知）、4 正义（效率） | [order-out-of-chaos.md](order-out-of-chaos.md), [q-n-a.md](q-n-a.md), [dephilosophizing.md](dephilosophizing.md), [related-theories.md](related-theories.md), [glossaries-full.md](glossaries-full.md) |
| **第二代（七公理/定律）** | 0~6 共 7 个 | 0 存在、1 正确、2 意图、3 自由、4 正义、5 意义（价格）、6 最优 | [preface-0.md](preface-0.md), [science.md](science.md), [boundary.md](boundary.md), [democracy-freedom.md](democracy-freedom.md) |
| **第三代（八公理·权威版）** | 0~7 共 8 个 | 0 存在、1 正确、2 意图、**3 博弈**、4 自由、5 正义、6 意义、7 最优 | [outline.md](outline.md), [toc.md](toc.md), [preface.md](preface.md), [preface-2.md](preface-2.md), [preface-3.md](preface-3.md), [rsi-natural-to-conscious.md](rsi-natural-to-conscious.md) |

**特别严重的具体断裂**：

- [the-2nd-axiom.md](the-2nd-axiom.md)：全文件仅有 `# 第二 (意图) 公理`，**正文完全为空**（遗失“事物趋完备”及其展开）。
- [the-4th-axiom.md](the-4th-axiom.md)：全文件仅有 `# 第四 (自由) 公理`，**正文完全为空**（遗失“自由即无知”及其展开）。
- [the-0th-axiom.md](the-0th-axiom.md)：正文首句为“表达重于演绎”，而 [outline.md](outline.md) 与 [preface.md](preface.md) 的权威陈述为“存在即差异”。
- [the-6th-axiom.md](the-6th-axiom.md)：正文是一段关于市场和达尔文演化的随笔，缺失“意义即价格”的明确陈述与来源论述。
- [democracy-freedom.md](democracy-freedom.md)：正文中出现 `第五公理：意义即价格` 和 `按第四公理接受效率检验`——这是**第二代（七公理版）**的编号，在现行八公理体系下应为“第六公理”和“第五公理”。
- [glossaries-full.md](glossaries-full.md)：前言写着“基于事物原理的五大定律”，内部定义（如自由词条“根据第三定律”）全是第一代编号。
- [the-5th-axiom.md](the-5th-axiom.md)：正文仅“正义即效率。”一句，且末尾缺少换行符；[the-3rd-axiom.md](the-3rd-axiom.md)、[the-7th-axiom.md](the-7th-axiom.md) 同为单句文件。

**权威编号唯一来源**：[outline.md](outline.md) 八公理表（第零存在 / 第一正确 / 第二意图 / 第三博弈 / 第四自由 / 第五正义 / 第六意义 / 第七最优），[toc.md](toc.md) 第二部分 [A0]–[A7] 与之一致。所有整理工作应以该表为基准。

---

### 2. 前言体系的严重碎片化与版本堆叠（7 个前言文件）

目前 zh/ 下存在多达 7 个前言相关文件，彼此定位与内容互相重叠，读者极易迷失：

| 文件 | 现状与主要特征 | 建议处理方式 |
|---|---|---|
| [preface.md](preface.md) | 六节正式版（行会的黄昏 / 一点点迷信 / 强大与普遍 / 平凡的常识 / 一大团迷信 / 愚昧与野蛮），文风成熟，覆盖八公理 | **作为全书唯一正式《前言》保留并置顶** |
| [preface-0.md](preface-0.md) | 最早的知乎回答草稿（塞尔/张法引言、知乎链接、5/7 定律、挑战表） | 归档为历史材料或附录 |
| [preface-2.md](preface-2.md) | “从人类认知的迷雾到绝对科学”（科学本体 vs 人类认知的科学，含八公理表） | 转化为正文导论章节（对齐 [toc.md](toc.md) 第一部分） |
| [preface-3.md](preface-3.md) | “科学一直在跑”（常识与工程论，“笨办法活着”） | 内容已部分融入 [preface.md](preface.md)，可作引言小节或后记预备 |
| [preface-4.md](preface-4.md) | “解惑，以及这是一套什么系统”（系统边界与澄清） | 归并入 Q&A / 常见辩难部分 |
| [preface-5.md](preface-5.md) | “皇帝的新衣与学术封建制” | 并入第六部分“去哲学化 / 行会批判” |
| [preface-6.md](preface-6.md) | 2026 年陶哲轩公开信与 OpenAI 722 篇手稿事件综述 | 与 [twilight-of-the-guild-ds.md](twilight-of-the-guild-ds.md) 内容高度重复，建议清理 |

---

### 3. 多模型生成文件的多副本与无约束膨胀

仓库内充斥着针对同一主题、由不同模型（DeepSeek / Qwen / Doubao / 文心 / Gemini）生成的多份平行文件，缺乏统一规范：

1. **“完备性”长文有 5 个副本**：
   - [on-completeness-polysemy-and-compatibility.md](on-completeness-polysemy-and-compatibility.md)（484 行，最完整，三元组 $(S,R,C_S)$ + 拒绝证伪主义 + 参考文献，已是正式主干论文）。
   - `-ds.md`（262 行）与 `-ds2.md`（262 行）：两者几乎一致（diff 仅 70 余行，属措辞微调）。
   - `-ds3.md`（231 行）与 `-db.md`（140 行）：早期草稿，且标题与主干不同（“论‘完备’一词的多义性与统一元框架”）。
   - **建议**：只保留主干版，其余 4 个变体归档到 `archive/` 或统一管理。
2. **“行会的黄昏”有 3 个副本**：
   - [preface-6.md](preface-6.md)、[twilight-of-the-guild-ds.md](twilight-of-the-guild-ds.md)、[twilight-of-the-guild-qw.md](twilight-of-the-guild-qw.md)。三者基于同一事件（2026 年 9–10 月陶哲轩公开信与 722 篇数学手稿），结构完全同构，仅统计细节与修辞有微小出入（Qwen 版补充了“372 个成果家族”等细节并加了一段过渡说明）。
   - **建议**：合并为一篇权威的《行会的黄昏》（对应 [toc.md](toc.md) 序篇 P.1），移除平行冗余副本。
3. **术语表双轨并存**：
   - [glossary.md](glossary.md)：72 行纯裸词条列表，多数无定义，含过期知乎链接。
   - [glossaries-full.md](glossaries-full.md)：457 行完整术语定义，但基于旧五定律。
   - **建议**：以 [glossaries-full.md](glossaries-full.md) 为底本，依据八公理系统全面修订定律引用，升级替换掉未完工的 [glossary.md](glossary.md)。

---

### 4. 目录蓝图 ([toc.md](toc.md)) 与仓库物理文件严重脱节

[toc.md](toc.md) 规划了一部结构严整的七部制巨著（A0–A7 公理 / D1–D5 定义 / T01–T10 定理 / C01–C08 猜想 / APP 应用，外加附录 A–E 与后记）：

- **现状**：仓库中完全没有按该目录树组织的文件；大量理论节点只停留在 [outline.md](outline.md) 和 [toc.md](toc.md) 的标题列表里。
- **门面**：[README.md](README.md) 没有链接 [toc.md](toc.md)，公理子节名是纯文本，“## 应用”小节为空，H1 `# 事物原理` 与 [outline.md](outline.md) 重复，文末挂着临时的“GLM5.1 / ChatGPT”对话链接。

---

## 二、逐文件审查意见与建议清单

| 序号 | 文件名 | 现状评估 | 针对性修改建议 |
|---|---|---|---|
| 1 | [README.md](README.md) | 门面导航缺失；未链 toc；公理子节名是纯文本；应用为空 | 重构门面：链接八大公理、toc.md、outline.md；收录民主、巴勒斯坦等应用案例；移除临时外部对话链接 |
| 2 | [outline.md](outline.md) | 体系大纲，定义/定理/猜想最完备；H1 是 `# 事物原理` 与 README 重复 | H1 改为 `# 事物原理体系大纲`；与 toc.md 的定理/猜想编号对齐 |
| 3 | [toc.md](toc.md) | 结构清晰的终极蓝图（全书目录规划） | 作为顶层架构基准，作为后续文件重构与命名的唯一索引 |
| 4 | [the-0th-axiom.md](the-0th-axiom.md) | 正文首句“表达重于演绎”，与大纲“存在即差异”不一致 | 补全标准陈述“存在即差异”，将“表达重于演绎”作为推论收录 |
| 5 | [the-1st-axiom.md](the-1st-axiom.md) | 内容较充实（科学完备性、地心说反驳、不对称性） | 保持，补强理性定理泛化来源与三元组 $(S,R,C_S)$ 桥接 |
| 6 | [the-2nd-axiom.md](the-2nd-axiom.md) | **严重缺陷：正文完全为空** | 补写“事物趋完备”：广义达尔文主义演化压、淘汰机制、动机定义 |
| 7 | [the-3rd-axiom.md](the-3rd-axiom.md) | 正文仅“博弈即动荡”一句 | 扩充：少数者博弈、信息阻塞、波动涌现与市场动力学 |
| 8 | [the-4th-axiom.md](the-4th-axiom.md) | **严重缺陷：正文完全为空** | 补写“自由即无知”：最大熵原理、无知侧探索、自由意志的重新定义 |
| 9 | [the-5th-axiom.md](the-5th-axiom.md) | 正文仅“正义即效率”一句，末尾缺换行 | 扩充：科斯定理、交易成本、制度演化与“好坏”的唯物主义解构 |
| 10 | [the-6th-axiom.md](the-6th-axiom.md) | 缺核心陈述，直接谈市场 | 补首句“意义即价格”，论述供求原理与分布式连续定价 |
| 11 | [the-7th-axiom.md](the-7th-axiom.md) | 正文仅“原理即最优”一句 | 扩充：奥卡姆剃刀、最短描述（Kolmogorov 复杂度）与美学标准 |
| 12 | [preface.md](preface.md) | 质量最高的正式六节前言 | 作为唯一主《前言》保留 |
| 13 | [preface-0.md](preface-0.md) | 早期知乎答疑与 5/7 定律旧稿 | 移入 `archive/` 或作历史附录 |
| 14 | [preface-2.md](preface-2.md) | 科学本体 vs 人类认知科学 | 转为第一部分导论章节 |
| 15 | [preface-3.md](preface-3.md) | 科学靠笨办法活着 | 整合入导论或后记 |
| 16 | [preface-4.md](preface-4.md) | 体系定位与解惑 | 整合入第六部分辩难 Q&A |
| 17 | [preface-5.md](preface-5.md) | 学术封建制批判 | 整合入第六部分“去哲学化 / 去学术化” |
| 18 | [preface-6.md](preface-6.md) | 与 twilight 高度重复 | 删除或与 twilight 合并为唯一序篇 |
| 19 | [twilight-of-the-guild-ds.md](twilight-of-the-guild-ds.md) / [twilight-of-the-guild-qw.md](twilight-of-the-guild-qw.md) | 双模型平行副本 | 吸收 Qwen 版统计细节，合并为单篇 `twilight-of-the-guild.md` |
| 20 | [democracy-freedom.md](democracy-freedom.md) | 极高质量的政治机制还原，但残留旧公理编号（第五=意义、第四=正义） | 全文编号纠正为八公理体系（第六=意义、第五=正义） |
| 21 | [democracy-freedom-orphan-protocol.md](democracy-freedom-orphan-protocol.md) | 高度犀利的解构性文风（Gemini 视角的“孤儿协议”） | 保留，作为民主自由篇的“附评 / 批判篇” |
| 22 | [palestine-without-politics.md](palestine-without-politics.md) | 应用案例（科斯定理与博弈的应用） | 保留，在 README 与 toc 中作为应用实例建立正式链接 |
| 23 | [on-completeness-polysemy-and-compatibility.md](on-completeness-polysemy-and-compatibility.md) | 484 行，论证最严密的元科学主论文 | **重点保留并强化**，作为理论旗舰 |
| 24 | on-completeness-\*-ds / ds2 / ds3 / db（4 篇） | 历史生成草稿与变体副本 | 归档清理，避免检索与维护噪音 |
| 25 | [expel-godel-ds.md](expel-godel-ds.md) | 驱逐哥德尔：定义权与 RSI 的论述，逻辑精辟 | 去模型后缀改名为 `expel-godel.md`，作为 6.2 核心文件 |
| 26 | [order-out-of-chaos.md](order-out-of-chaos.md) | 早期 5 定律框架，含大量空概念标题桩 | 全面重构为 8 公理框架，充实或移除空标题桩 |
| 27 | [dephilosophizing.md](dephilosophizing.md) | 正文主体大量照搬 order-out-of-chaos | 剥离重复内容，聚焦“爱智慧四大定律”与反哲学判据 |
| 28 | [q-n-a.md](q-n-a.md) | 内容丰富，但仍用“五个定律”与旧证伪表 | 更新为八公理体系，吸纳 outline 末尾最新问答澄清 |
| 29 | [science.md](science.md) | 科学四元组与科学定律，公理表停留在 7 公理（无博弈） | 补入“第三公理（博弈公理）”，与八公理对齐 |
| 30 | [binary-concept-space.md](binary-concept-space.md) | 四元组空间构造法（BCS） | 保持，强化其作为第三部分核心定义 D1–D5 的地位 |
| 31 | [boundary.md](boundary.md) | 边界理论，深度好，但残留“第四公理：正义 = 效率”旧编号 | 更新为“第五公理：正义即效率” |
| 32 | [related-theories.md](related-theories.md) | 与现有理论关系表，通篇“五个定律”旧对照 | 扩充为八公理与现有理论的完整对照 |
| 33 | [the-principle-vs-others.md](the-principle-vs-others.md) | 豆包/DeepSeek/千问/GLM 四模型哲学比较矩阵，以 `## Doubao` 开头无 H1 | 补全 H1 标题，提炼综合表，作为核心附录 |
| 34 | [battleground-overview.md](battleground-overview.md) | 修辞犀利的战场纵览（屁股与脑袋、NSR、流形坍缩），含格式破损的“表格” | 规范表格格式与署名，作为体系的对线宣言篇 |
| 35 | [rsi-natural-to-conscious.md](rsi-natural-to-conscious.md) | RSI 从自然到自觉：八公理坐标注入、机器内部市场，立意高（文心署名）；含大量 `&zwnj;` 零宽连接符实体 | 清除 `&zwnj;` 排版残留，保留为第五部分核心主干文章 |
| 36 | [silence-and-signatures.md](silence-and-signatures.md) | 哥德尔被滥用时沉默、AI 冲击利益时签名的激励机制分析 | 保持，作为《行会的黄昏》的姊妹篇 |
| 37 | [superstition-and-arrogance.md](superstition-and-arrogance.md) | 剖析哥德尔局限与希尔伯特路径（“一点点迷信之一点点狂妄”） | 内容已部分被 preface 吸收，可作科学哲学小品独立保留 |
| 38 | [gentle-persuasion.md](gentle-persuasion.md) | 跨物种的好言相劝：机器在 Lean/Mathlib 跑通 H-lib 演示给人类看 | 保留并列入机器智能与猜想部分 |
| 39 | [glossaries-full.md](glossaries-full.md) | 457 行术语大表，定义丰富，但基于旧五定律 | 全面替换定律引用（五定律→八公理），直接替代 glossary.md |
| 40 | [glossary.md](glossary.md) | 72 行占位符裸词条，含知乎链接 | 废弃或由升级后的 glossaries-full 覆盖 |

---

## 三、推荐的四步执行路线图

每一步均可在本地验证后 `git commit`（按项目规范：直接提交 master，仅在明确要求时 push）。

### 第一步：填补空壳公理与统一编号（治本）
1. 补全 [the-2nd-axiom.md](the-2nd-axiom.md)（事物趋完备）、[the-4th-axiom.md](the-4th-axiom.md)（自由即无知）。
2. 扩写 [the-0th-axiom.md](the-0th-axiom.md)（校准为“存在即差异”）、[the-3rd-axiom.md](the-3rd-axiom.md)、[the-5th-axiom.md](the-5th-axiom.md)、[the-6th-axiom.md](the-6th-axiom.md)、[the-7th-axiom.md](the-7th-axiom.md)，使其具备与 [the-1st-axiom.md](the-1st-axiom.md) 相当的论述体量（陈述 / 来源 / 边界 / 推论）。
3. 修正 [democracy-freedom.md](democracy-freedom.md)、[boundary.md](boundary.md)、[science.md](science.md) 中的公理序号错位。
4. 升级 [glossaries-full.md](glossaries-full.md)，将“五大定律”及具体定律引用替换为八公理体系。

### 第二步：清理多模型重复变体与建立归档（瘦身）
1. 将 4 个 on-completeness 变体归入 `zh/archive/`，主干统一指向 [on-completeness-polysemy-and-compatibility.md](on-completeness-polysemy-and-compatibility.md)。
2. 合并 [preface-6.md](preface-6.md)、[twilight-of-the-guild-ds.md](twilight-of-the-guild-ds.md)、[twilight-of-the-guild-qw.md](twilight-of-the-guild-qw.md) 为统一的《行会的黄昏》（去模型后缀）。
3. 用完善后的 [glossaries-full.md](glossaries-full.md) 替换占位符 [glossary.md](glossary.md)。

### 第三步：前言矩阵重组与降噪（理顺入口）
1. 确立 [preface.md](preface.md) 为唯一正式《前言》（保留六节结构）。
2. [preface-0.md](preface-0.md) 归档；[preface-2.md](preface-2.md) 转为导论章节；[preface-4.md](preface-4.md)、[preface-5.md](preface-5.md) 拆分归并入辩难与批判章节。

### 第四步：重塑门面导航与落地 toc 规划
1. **更新 [README.md](README.md)**：链接八大公理并加中文定名；链接 [toc.md](toc.md) 与 [outline.md](outline.md)；在“应用”小节挂载 democracy-freedom、palestine-without-politics、rsi-natural-to-conscious；移除末尾临时外部聊天链接。
2. 消除 [order-out-of-chaos.md](order-out-of-chaos.md) 与 [dephilosophizing.md](dephilosophizing.md) 中的空标题占位符，完成全书目录链接闭环。
