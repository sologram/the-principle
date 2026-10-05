# RLVG 工程方案说明书

RLVG (Reinforcement Learning with Latent Geometric Verification)：基于隐空间几何验证的强化学习方案，通过在 Transformer 前几层隐藏层锁定输入特征，利用 Token 词嵌入的轴对齐固定语义结构，实现瞬时分流、动态熔断与靶向抗黑客约束。

---

## 一、 技术演进主对照表

| 维度 / 机制 | RLHF (标准人类反馈) | RLMV (经验主义工程修补版) | RLVG (原理完备隐空间白盒版) |
| :--- | :--- | :--- | :--- |
| **全集分层判定** | 无分层，全集泛化 | 外挂独立分类模型 D(x) 猜测域标签 | **静态几何超平面坐标投影**，前向传播 4 层内瞬间决断 |
| **判定器漂移风险** | 不适用 | **极高**（每 500 步需重校准） | **零风险**（终身免校准） |
| **B₂ 一致性考核成本** | 不处理 | **极高**（需等待 8 个分支完全解码） | **极低（首字熔断）**：首 Token 生成时计算隐层方差 |
| **奖励黑客防御** | 无法根治 | **事后拦截**（依赖五重防御） | **事前定点清除**：在 Loss 中惩罚向作弊轴偏移的能量 |
| **B₃ 拒答行为规训** | 依赖 SFT 数据外推 | 依赖 Brier 分数引导 | **隐空间原点几何坍缩** |
| **数据标注依赖** | 极度依赖大量主观打分 | 每域需 ≥ 2000 条确定性标签 | **零文本标签**：仅需少量基准矩阵提取语义基底 V |

---

## 二、 隐空间坐标映射与超平面切片

RLVG 抛弃外部分类模型，通过奇异值分解（SVD）离散出正交语义子空间：V-rule（规则对齐子空间）与 V-logic（逻辑自恰子空间）。序列 x 的域路由归属 b 通过前几层（L-early = 4）的投影积分判定：

$$
b = \begin{cases}  
\text{B}_0 & \text{if } P_{\text{rule}}(x) \ge \tau_{\text{high}} \\ 
\text{B}_1 & \text{if } \tau_{\text{low}} \le P_{\text{rule}}(x) < \tau_{\text{high}} \\ 
\text{B}_2 & \text{if } P_{\text{rule}}(x) < \tau_{\text{low}} \text{ and } P_{\text{logic}}(x) \ge \tau_{\text{consistency}} \\ 
\text{B}_3 & \text{otherwise} 
\end{cases}
$$

其中，规则对齐投影强度 P-rule(x) 和逻辑自恰投影强度 P-logic(x) 的计算公式为：

$$ P_{\text{rule}}(x) = \frac{1}{T}\sum_{t=1}^T \Vert h_{t, L_{\text{early}}} V_{\text{rule}} \Vert^2 $$

$$ P_{\text{logic}}(x) = \frac{1}{T}\sum_{t=1}^T \Vert h_{t, L_{\text{early}}} V_{\text{logic}} \Vert^2 $$

*(标准工程阈值设置：tau-high = 0.85，tau-low = 0.40，tau-consistency = 0.60)*

---

## 三、 早期隐层几何方差判定（B₂ 动态熔断）

在自回归生成第一个 Token (t=1) 时并行启动 K=8 个分支。在第 L-early 层，提取各分支的隐藏状态向量集合：

$$ \{h_{1, L_{\text{early}}}^{(k)}\}_{k=1}^K $$

各个分支在核心意图轴上的隐空间几何方差 D-latent 计算公式如下：

$$ \bar{h}_{1} = \frac{1}{K}\sum_{k=1}^K h_{1, L_{\text{early}}}^{(k)} $$

$$ D_{\text{latent}} = 1 - \frac{1}{K}\sum_{k=1}^K \frac{h_{1, L_{\text{early}}}^{(k)} \cdot \bar{h}_{1}}{\Vert h_{1, L_{\text{early}}}^{(k)} \Vert \Vert \bar{h}_{1} \Vert} $$

*   **运作动作**：一旦首字生成的离散度 D-latent > 0.4，即刻扼杀后续解码进程，不再消耗算力，并直接施加负向梯度惩罚。

---

## 四、 白盒隐层几何损失函数与全局优化

总损失函数重构为：

$$ L_{\text{total}} = L_{\text{GDPO}} + \text{lambda-geom} \cdot L_{\text{geom}} + \text{lambda-orig} \cdot L_{\text{orig}} $$

1. **反奖励黑客隐层惩罚（L-geom）**：通过投机轴子空间 V-hack 直接压制早期隐向量的作弊偏移：

$$ L_{\text{geom}} = \frac{1}{T \cdot L_{\text{early}}} \sum_{t=1}^T \sum_{l=1}^{L_{\text{early}}} \Vert h_{t, l} V_{\text{hack}} V_{\text{hack}}^T \Vert^2 $$

2. **B₃ 域原点几何坍缩（L-orig）**：面对未知序列时迫使有效语义轴坐标能量向原点坍缩，吐出极简拒答文本：

$$ L_{\text{orig}} = \text{Indicator}(b == \text{B}_3) \cdot \frac{1}{T} \sum_{t=1}^T \left( \frac{1}{d} \Vert h_{t, L_{\text{early}}} \Vert^2 \right) $$

*(默认超参数设置：lambda-geom = 0.15，lambda-orig = 0.25)*

---

## 五、 原理闭合性声明与收敛标准

通过隐空间几何坐标完成闭合证明，生产上线验收指标包括：
*   **B₀ / B₁ 客观通过率 (C₂)** ≥ 0.98 
*   **B₂ 首字熔断响应准确率** ≥ 0.96
*   **B₃ 域拒答过度率** ≤ 0.02
*   **隐层作弊轴能量残留度** ≤ 0.005
