---
ttl: task_bound
---

# 车道C 二轨立项申请书：LLM 智能体挖矿轨（原"AlphaGen 立项"重新划界 v1）

> 2026-09-14 策略工厂后端施工班（st-facbe-20260914）起草，待 Owner 批复。
> 性质：**立项申请书**（批准后才进施工闭环）；本稿本身即交付物。

## 一、为什么重新划界（全网检索结论，2026-09-14）

原设计稿 §二 把二轨锚定在 AlphaGen（RL 拼公式，KDD 2023）。2026-09 检索实证：该赛道已
两代更迭，纯 RL 路线已成"上一代"：

| 代际 | 代表 | 机制 | 状态 |
|---|---|---|---|
| 一代 2023 | AlphaGen | RL 逐因子生成 | 已过时（固定权重组合是其公认短板） |
| 二代 2024 | AlphaForge（AAAI 2025） | 生成式-预测式网络+**动态组合** | 基线参照 |
| 三代 2025-26 | **AlphaAgent**（KDD，arXiv 2502.16789）/ AlphaMuse（AAAI 2026，LLM+MCTS）/ Chain-of-Alpha（arXiv 2508.06312）/ AlphaAgentEvo | LLM 智能体+搜索/自进化+**抗衰减正则** | 当前前沿 |

来源：AlphaAgent arxiv.org/abs/2502.16789；AlphaMuse ojs.aaai.org/index.php/AAAI/article/view/37069
（arXiv 2505.11122）；Chain-of-Alpha arXiv 2508.06312；FAFM 基准 openreview.net/pdf?id=d97Q8r7ZKZ；
综述 FITEE jzus.zju.edu.cn（doi 10.1631/FITEE.2500386）；清单 github.com/Sasha-Cui/Awesome-Applied-Agents-for-Investment。

**关键发现（本项目的机会窗口）**：AlphaAgent 的三大正则——原创性（防重复挖）、经济逻辑
（讲人话）、简洁性（防过拟合）——与本项目已建件**一一对应**：E5 协同去重=原创性正则、
E2 假说预审=经济逻辑正则、init_depth+parsimony=简洁性正则。**业界的"正则化智体挖矿"
在我们厂里就是"智体产货+现有质检厂"**。二轨的正确姿势不是搬一台 AlphaGen 发动机，
而是给现有质检厂接一个 LLM 智能体产货口。

## 二、立项范围（批准后施工）

- **P0（半天）**：精读 AlphaAgent/AlphaMuse 论文+跑通其开源码（若在库），产出对照笔记；
- **P1（一个夜班）**：MVP 接线——LLM 产货口复用车道 B 管线形态（MOD-BT-150 模式）：
  主题种子→假说/公式生成（经 LSG）→正则约束写进生成 prompt（原创性=与现有因子池
  相关性上限、经济逻辑=必须给出机制自述、简洁=算子数上限）→卸 lane_c2 台账→E2/E4/E5 现行质检；
- **P2**：与 gplearn 轨赛马（同一考试、同一及格线），按 E4+E5 幸存率定主辅。

## 三、资源与决策点（等 Owner）

1. 批准本立项（范围=上表 P0/P1）；
2. GPU/时窗：P1 全程 CPU+本地 8B 可扛，无需新算力（与 gplearn 轨共享 E0 闸夜窗）；
3. 赛马及格线：两轨同线（E4 现行冻结阈值+DSR），不因技术路线新而放宽——"量越大及格线
   越狠"铁律不破。

## 四、与 gplearn 轨的关系

互补不替代：gplearn 轨=受控算子空间的机械搜索（便宜、稳定、已投产）；
智能体轨=开放式假说生成（贵、杂、上限高）。两轨货同走 E2→E4→E5 一条咽喉，
幸存者同入 factor_registry。
