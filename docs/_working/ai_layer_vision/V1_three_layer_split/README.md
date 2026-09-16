---
ttl: task_bound
title: 挖矿② 三层划分验证——治理/业务/AI 的切分本身对不对
owner: ZephyrAlpha-Owner
session: st-ailayer-20260917
date: 2026-09-17
status: done
---

# 挖矿② 三层划分验证（Owner 三步验证序列第二步）

> **验证命题**：大层定义对，那"治理层/业务层/AI 层"这个切分本身对不对？
> **结论：站得住。一条关键定位精化：AI 层=平台型横切引擎。业界给了它精确坐标：
> 把 MLOps Level 2 的自动化对象从"模型"扩到"整个系统"。**

## 1. 对标证据

| # | 证据 | 来源 | 对应关系 |
|---|------|------|---------|
| 1 | **MLOps 成熟度模型**：Level 0（手动）→ Level 1（管线自动化+连续训练 CT，由新数据/drift 触发）→ Level 2（完整 CI/CD/CT，训练和部署管线本身也自动化） | Google Cloud 官方架构文档 [MLOps: Continuous delivery and automation pipelines in ML](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)；[Practitioners Guide to MLOps 白皮书](https://services.google.com/fh/files/misc/practitioners_guide_to_mlops_whitepaper.pdf) | **AI 层的业界坐标=Level 2 推广**：Google 的 Level 2 只自动化"模型管线"，我们的 AI 层把自动化对象扩到治理规则/模块代码/骨架本身——范围更大，范式相同 |
| 2 | **量化机构功能分离**：research/technology/risk/execution 各自独立团队+信息屏障；顶级基金两大形态=平台型集中（中央研究/技术设施）与 pod 型 | [Hudson & Thames](https://hudsonthames.org/how-to-build-a-world-class-quant-team/)、[Chen 2024](https://www.sciencedirect.com/science/article/abs/pii/S1042957324000172)、[QRT 案例研究](https://medium.com/@navnoorbawa/how-qrt-built-28b-through-centralized-allocation-not-star-portfolio-managers-6de8c3ab6c9d) | 治理/业务切分=行业实证；AI 层="平台型"的那块中央基础设施（我们的 AI 层就是这个平台的无人版） |
| 3 | **Three Lines Model**（交叉引用 V0 报告证据 1） | IIA 2020 | 三线模型本身没有第四线——但三线之外有董事会/外部监督。对应我们：Owner 门位在三线模型框架里本来就在"层外"，不必成为第四层 |

## 2. 关键洞察：AI 层不是第四条线，是"平台"

- 三线模型回答"谁保证谁"，平台模式回答"谁供养谁"。我们的切分同时用了两个轴：
  **治理 vs 业务**是保证轴（三线模型），**AI 层**是供养轴（平台）——它向两层供应
  进化能力（搜索/清洗/对比/切换），自己不承载业务内容也不承载控制逻辑。
- 运行时咬合：AI 层的进化循环跑在业务层的数据和考试上（对比器用 C4 双窗），
  也跑在治理层的门禁上（红蓝对抗检验门禁）。组织独立（有自己的 KPI=进化速度），
  运行时寄生——这正是平台型机构的形状（QRT 的中央研究平台模式）。

## 3. 反方意见两驳

1. **"AI 层不就是 MLOps/DevOps 换皮？"** → 驳：范围差异是本质的——MLOps 的自动化对象
   到"模型管线"为止，不管治理规则本身的进化、不管骨架增删、不管门禁参数调优；
   我们的对象清单含全部三类，且带蓝绿切换与根约束不变量（MLOps 无此概念）。
   准确说法：MLOps Level 2 是 AI 层在"模型"子域的特例。
2. **"数据要不要单拆一层？"** → 驳：见 V0 报告 §3-1。留触发条件（多机/多市场重评）。

## 4. 挖矿日志表

| 轮次 | 矿脉 | 判定 | 关键产出 |
|------|------|------|---------|
| V1-R1 | 量化机构组织分层 | signal | 功能分离+平台型集中模式两路证据 |
| V1-R2 | MLOps 成熟度 | signal | Google Cloud 官方 Level 0-2 框架 |
| V1-R3 | 三线模型交叉 | signal | 复用 V0-R1（同一来源两处消费，交叉验证闸满足） |
