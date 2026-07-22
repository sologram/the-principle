# 概念几何分析原理

## 核心问题

现代语言模型生成的词向量通常同时编码多种信息，其中包含两类关键成分：
  
- 语义信息：表示概念本身的内容、关系和指称
- 语法信息：语言形式信息（语法、词形等）

这里主要关注语义与语法的分离问题。由于不同信息混合在同一个向量空间中，会产生一个反直觉现象：语义相反的词，在向量空间中可能表现出较高的相似度。

例如：

cosine(好, 坏) ≈ 0.9

从传统几何直觉看，相反概念应该具有相反方向；然而词向量空间却可能表现为高度接近。

## 反义词高相似度的原因

词向量通常基于分布假设学习：出现在相似上下文中的词，其向量表示趋于接近。

例如：

- 这是一个好主意
- 这是一个坏主意
- 今天是好天气
- 今天是坏天气

“好”和“坏”具有高度重叠的上下文环境。

因此模型学习到的是：

- 好 ≈ 共同语法结构 + 正向评价
- 坏 ≈ 共同语法结构 + 负向评价

二者共享大量语法信息，仅在评价方向上存在差异。因此原始空间中的距离反映“使用环境相似性”不一定反映“逻辑关系中的相反性”

## 解决方案：语用空间分析

核心思想：

将词向量空间中的语用维度显式分离，在独立的语用空间中分析评价关系。

整体结构：

原始向量空间
        |
        |
        +----------------+
        |                |
    语用空间          语义空间
(评价方向子空间)   (语用正交补空间)

定义：

原始空间（Original Space）

模型直接输出的隐藏表示：

V

包含所有混合信息。

语用空间（Pragmatic Space）

由多个评价轴构成的低维子空间：

P⊂V

捕获价值、真假、道德、美学等评价维度。

语义空间（Semantic Space）

语用空间的正交补：

S=V−P

用于表示去除评价后的概念内容。

## 语用轴定义

语用轴表示评价空间中的基本方向。

一个轴由正负概念定义：

axis=v
pos
	​

−v
neg
	​


例如：

语用维度	正极	负极	理论解释
价值轴	好	坏	好对应更高效率
真值轴	对	错	正确对应更完备
道德轴	善	恶	善对应更合作
美学轴	美	丑	美对应更高效率

多个轴共同构成语用空间。

## 空间分解算法

### 计算语用基

首先收集所有语用轴：

axes = [
    value_axis,
    truth_axis,
    moral_axis,
    aesthetic_axis
]

然后进行正交化：

pragmatic_basis = orthogonalize(axes)

得到语用空间基。

### 投影分解

对于任意词向量：

v

计算：

语用部分
v
p
	​

=Projection(v,P)

代码：

v_prag = project(v, pragmatic_basis)
语义部分
v
s
	​

=v−v
p
	​


代码：

v_sem = v - v_prag

## 相似度计算

对于两个词：

w
1
	​

,w
2
	​


得到：

v1_prag = project(v1, pragmatic_basis)
v2_prag = project(v2, pragmatic_basis)

v1_sem = v1 - v1_prag
v2_sem = v2 - v2_prag

分别计算：

原始相似度
sim(v
1
	​

,v
2
	​

)
语用相似度
sim(v
1p
	​

,v
2p
	​

)
语义相似度
sim(v
1s
	​

,v
2s
	​

)

## 关键几何解释

在原始空间：

好 =
共同语义 + 正评价

坏 =
共同语义 + 负评价

由于共同语义占据主要维度：

cosine(好,坏)>0

甚至可能很高。

经过语用投影：

好_prag ≈ +1

坏_prag ≈ -1

二者位于评价轴两侧：

cosine(好
p
	​

,坏
p
	​

)<0

因此：

反义关系不是不存在，而是被隐藏在高维混合空间中的某个方向。

## 数学解释

设评价轴：

a=v
好
	​

−v
坏
	​


则：

cosine(v
好
	​

,a)>0

而：

cosine(v
坏
	​

,a)<0

因此二者关于该轴具有相反投影：

projection(v
好
	​

,a)⋅projection(v
坏
	​

,a)<0

## 

### 正向关系验证

理论假设：

同一原理中的正向概念应该在原始空间中保持相关。

例如：

positive_pairs:
  - [完备, 正确]
  - [正义, 效率]

验证：

cosine(w
1
	​

,w
2
	​

)>0.5

### 对立关系验证

理论假设：

对立概念应在语用空间中表现为方向相反。

例如：

opposite_pairs:
  - [完备, 不完备]
  - [正义, 不公]

验证：

cosine(w
1p
	​

,w
2p
	​

)<−0.3

## 验证等级

状态	标准
verified	验证率 ≥75%
partial	50%-74%
not supported	<50%

## 配置结构

示例：

name: 完备即正确

theory:
  任何正确不允许遗漏信息

positive_pairs:
  - [完备, 正确]

opposite_pairs:
  - [完备, 不完备]

pragmatic_axes:

  value:
    positive:
      - good
      - excellent
      - success

    negative:
      - bad
      - failure
      - harmful


thresholds:

  positive_similarity: 0.5

  opposite_pragmatic: -0.3
  
## 向量提取

从模型隐藏层获取表示：

def get_vector(text, layer=0):

    inputs = tokenizer(text)

    outputs = model(
        **inputs,
        output_hidden_states=True
    )

    hidden = outputs.hidden_states[layer]

    mask = attention_mask.unsqueeze(-1)

    vec = (
        hidden * mask
    ).sum(dim=1) / mask.sum(dim=1)

    return vec
    
## 语用轴计算

def compute_axis(pos_words, neg_words, extractor):

    pos_vecs = [
        extractor.get_vector(w)
        for w in pos_words
    ]

    neg_vecs = [
        extractor.get_vector(w)
        for w in neg_words
    ]

    return mean(pos_vecs)-mean(neg_vecs)
    
## 轴质量评价

定义轴分离度：

D=cos(pos,a)−cos(neg,a)

代码：

def separation(axis):

    pos_proj = cosine(axis.pos_vec, axis)

    neg_proj = cosine(axis.neg_vec, axis)

    return pos_proj-neg_proj

评价：

等级	分离度
excellent	>1.0
good	>0.5
poor	≤0.5

## 模型比较

不同模型可能表现不同：

模型	原始相似度	语用分离	验证表现
InfoXLM-large	高	中等	较好
Qwen3.5-9B	中等	较弱	较低

一种可能解释：

多语言模型更强调跨语言概念对齐，因此抽象评价维度更明显；
通用生成模型更强调上下文预测，评价方向可能被分散。

## 层选择

Transformer 不同层表示不同信息：

层级	特点
Embedding层	词形与基础评价信息
中间层	语义组合
高层	任务相关抽象

初步实验显示：

较低层表示可能保留更明显的语用方向，因此可作为默认分析层。

但最终需要通过系统实验确定最佳层。

## 局限与未来方向

当前限制
依赖人工定义轴

需要人工提供正负概念。

线性假设

假设语用结构可以由线性子空间表达。

模型依赖

不同模型可能学习到不同评价结构。

未来方向
1. 自动发现语用轴

方法：

PCA
ICA
Contrastive Learning
Representation Autoencoder
2. 非线性语用空间

利用：

Kernel methods
Neural projection
Manifold learning
3. 多语言语用对齐

利用多语言模型：

对齐不同语言中的评价结构；
验证跨文化语用空间一致性。
参考
THEORY.md — 理论说明与实验结果
README-zh.md — 工具使用说明

整体评价：这个版本更像一篇表示学习 / 语言模型可解释性方向的技术论文草稿。核心思想“反义词关系存在于低维评价子空间，而不是整体语义空间”是清晰的，实验设计也已经具备可证伪结构。下一步最关键的是把“语用轴是否稳定存在”从假设变成大规模实验。
