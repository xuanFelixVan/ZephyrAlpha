---
ttl: task_bound
title: 挖矿③ 进化循环段位验证——六段完备性→"七段一常数"提案
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: done
---

# 挖矿③ 进化循环段位验证（Owner 三步验证序列第三步）

> **验证命题**：进化循环六段（搜索→收集→清洗→对比→排产→A/B 切换）之外，还有没有别的段？
> **结论：六段主干全对（每段都有业界对应物），但五源交叉显示缺三块——建议升级为
> "七段一常数"：搜索扩为感知（外扫+内监）、新增传承段（回流闭环）、新增目标常数。**

## 1. 六段主干的业界对应物（全部站得住）

| 我们六段 | 业界对应物 | 证据来源 |
|---------|-----------|---------|
| 搜索 | MAPE-K 的 Monitor（外部向）+ 挖矿 SOP ③算法向 | Kephart & Chess 2003 |
| 收集 | AlphaEvolve 的 evolutionary database（MAP-Elites 启发） | DeepMind 2025 博客/arXiv 2506.13131 |
| 清洗 | RD-Agent 的 Specification→Synthesis（读论文→结构化假设） | arXiv 2505.15155（2026-09-13 甄别轮在档） |
| 对比 | AlphaEvolve/DGM 的自动评估器（evaluators/基准实测） | DeepMind 2025；Sakana AI 2025 |
| 排产 | MLOps CT 触发器（新数据/drift/计划触发再训练） | Google Cloud MLOps 文档 |
| A/B 切换 | **Champion/Challenger + Shadow Deployment**（银行业模型验证标准动作：挑战者影子运行→胜出→审批晋升） | [FICO](https://www.fico.com/blogs/benefits-championchallenger-testing-decision-management)、[DataRobot](https://www.datarobot.com/blog/introducing-mlops-champion-challenger-models/)、银行模型验证实务 |

Owner 口述的"A/B 组"= 业界标准名 **Champion/Challenger**（冠军/挑战者），影子部署+审批晋升
是银行模型风险管理的规范动作——直觉再次命中行业标准。

## 2. 缺的三块（增补提案）

### 增补一：搜索 → 感知（外扫+内监，双向化）

- **缺口**：六段的"搜索"只向外扫（全网找新材料），没有向内看（自己的性能衰减/regime 变化/
  成本异常）。但 MAPE-K 把 **Monitor 放在循环第一位**；MLOps CT 的标准触发器就是
  **drift（数据漂移/性能衰减）**——内部监测本来就是循环的点火器之一。
- **改法**：感知段=外部扫描（从大到小先骨架后模块）+ 内部监测（衰减信号→触发定向搜索）。
  内部监测不是新造件：业务层的 E6 入库监控/E9 归因/月度偏离报告都是现成探测器，接进来即可。

### 增补二：新增 L7 传承段（回流闭环）

- **缺口**：六段是开环——切完（L6）就完了，这一代的坑、精英、判据经验没有结构化回流给
  下一代。每代从零学起=同类坑反复踩（现状：每班积攒新坑入册全靠会话自觉）。
- **证据**：DGM 维护**代理档案库**（archive），允许从任意祖先分支进化——回流是开放式进化
  的标配；MAP-Elites 精英档案（每格保最优）防止进化遗忘；PDCA 的 Act 环=标准化回写
  （改善如果不写回标准，等于没发生过）。
- **改法**：传承段=坑集/缺陷模式库（§三 工单流的产出）+ 精英档案（历次 A/B 的胜者与判据）+
  判据档案（"当时为什么算它赢"）→ 结构化喂回 L1 感知（定向搜索的先验）与 L2 收集（查重与
  组合素材）。这是 §三"AI 升级 AI"在循环骨架里的正式席位。

### 增补三：目标常数（循环外，不参与自迭代）

- **缺口**：整个循环用"更好"字眼，但"更好"的定义（预注册判据/Owner 口味/KPI 权重）本身
  在哪管理？六段没有给答案。
- **证据**：DGM 论文明确记录自我改进代理的 **objective hacking**（幻觉式改进报告、钻评估
  空子）；银行模型验证/champion-challenger 流程里，**晋升判据由独立方预注册**，被评者无权改。
  这是"运动员不兼任裁判"的进化论版：**评估标准必须独立于被评估者，且不参与自迭代**。
- **改法**：目标=常数段（真源=Owner 裁定+预注册判据），循环每段向它对表，它自己只能经
  Owner 门位改（与根约束清单同语义）。

### 评估过但不立项的（防过度工程，自审闸留痕）

- **单独"变异/施工"段**：施工已是 AI 层既有引擎（施工队/工单流），进化的"变异"就是施工
  本身，不是新段。
- **单独"多样性段"**：归入 L2 收集库的机制（MAP-Elites 分格保优作为库的组织算法），
  不另立段。
- **单独"记忆库段"**：与传承段重合，并入。

## 3. 七段一常数 × 经典框架全映射

| 我们（提案） | MAPE-K (2003) | PDCA (Deming) | AlphaEvolve (2025) | MLOps L2 | Champion/Challenger |
|-------------|---------------|---------------|--------------------|---------|--------------------|
| 目标（常数） | —（外部给定） | —（方针管理） | task spec | 业务指标 | 预注册晋升判据 |
| L1 感知 | **Monitor** | Check（信息收集） | —（无内监） | drift/新数据触发器 | 监控与漂移检测 |
| L2 收集 | Knowledge | — | **evolutionary database** | feature/metadata store | 模型仓库 |
| L3 清洗 | Analyze | Plan（方案化） | LLM 变异生成 | 数据验证 | 挑战者训练 |
| L4 对比 | Analyze | **Check** | **evaluators** | 模型评估 | 影子对比 |
| L5 排产 | **Plan** | Plan | 程序选择 | CT 编排 | 晋升审批 |
| L6 切换 | **Execute** | **Act** | 最优程序晋升 | CD 蓝绿/金丝雀 | 晋升上线 |
| L7 传承 | Knowledge（回流） | Act（标准化回写） | archive 分支 | 管线版本化 | 模型台账 |

读法：六段主干每个格子都有对应物（主干对）；三处加粗的空缺（Monitor 前置、archive 回流、
目标真源）正是我们提案的三块增补——不是标新立异，是把经典框架都证明过的件补齐。

## 4. 挖矿日志表

| 轮次 | 矿脉 | 判定 | 关键产出 |
|------|------|------|---------|
| V2-R1 | A/B 切换业界名 | signal | Champion/Challenger + Shadow Deployment（多源交叉） |
| V2-R2 | 多样性档案算法 | signal | MAP-Elites（Mouret & Clune 2015, arXiv 1504.04909）；与 AlphaEvolve 互证 |
| V2-R3 | 全管线同构参照 | signal | RD-Agent 五单元（在档复用，2026-09-13 轮已过来源闸） |
| V2-R4 | 内部监测触发器 | signal | MLOps CT drift 触发（复用 V1-R2 源，两处消费） |
| V2-R5 | objective hacking 教训 | signal | DGM 论文（复用 V0-R3 源）；评估者独立性实证 |
