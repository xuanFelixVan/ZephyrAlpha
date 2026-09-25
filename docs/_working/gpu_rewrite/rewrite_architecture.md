---
ttl: task_bound
title: 【已并入】重写架构三层 L1/L2/L3（前一轮草稿指针）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
lane: LANE-GPU
family_id: GPU-REWRITE
superseded_by: docs/_working/gpu_rewrite/rewrite_architecture_three_tiers.md
---

# 本文件已被并入 rewrite_architecture_three_tiers.md

- 后继件：[`rewrite_architecture_three_tiers.md`](./rewrite_architecture_three_tiers.md)（替换点全部带 file:line，收益区间锚在实测）。
- 按实测改判的三处：①L1 的靶从"五档扫描向量化"改为**消除封板掩码重建的重复与行物化**（实测掩码占单 pass 74–78%，张量面仅 2.8–3.6%）；②L2 载体由"cuDF 或 CuPy"改判 **CuPy 单选**（cuDF/Polars-GPU 不支持原生 Windows）；③"稀疏权重 ≤2GB 显存"假设被实测权重非零占比 47.9% 撤回，显存预算改按稠密。
- 继承有效的部分：L1 三处结构性冗余（档位间/函数间/掩码重建）判定、L2 "批量维=格点、时间维串行"几何、L3 "真前置是口径统一不是 GPU"的结论。
- 并入核账（2026-09-26 双版合并，本条为真销口的凭据）：本草稿被后继件按实测改判的三处**结论本身不丢**，其证据已在真源在案——
  ①L1"三处结构性冗余（档位间／函数间／掩码重建零缓存）"的**量化构成（每格 7 次 pass、14 次 CH 往返、7 次全量行循环）**与前一轮收益线"**hoisting 即得 3–7 倍**"→ ①文 `hotspot_census.md` **§二·补**（口径①②，含实测上修 8.6x/16.6x 与"在飞 T1 未开扫描→真实 pass=2"限定）；
  ②硬件红线"**FP64≈FP32 的 1/64**→必须走 FP32＋对拍容差路线"＋显存配额 18GB／单卡独占／与本地 LLM 互斥（`exclusive_group=gpu_default`）→ ④文 `verification_framework.md` **§一·补**（③文 §二 原有条同一并保留，不重复堆叠）；
  ③L2"批量维＝格点、时间维串行"几何与"禁 TF32/FP16"、L3"真前置是口径统一不是 GPU"、判定位永不动 CPU → ③文 §二/§三 逐条在案。
- 全量并入判定：本路径（L1 改动面表＋数据流＋bitwise 验证策略＋1–2 天工时估算／L2 面板驻留与显存推演／L3 边界／Phase 序）证据已全部在后继件或其同级真源在案；
  被实测**撤回**的两项（"稀疏权重 ≤2GB 显存"、"cuDF 或 CuPy 双载体"）在③文 §〇 与 §二 记着撤回理由，属**有意改判非丢失**；逐字比对见 git 历史 **commit 37aeecedcd 的 `docs/_working/gpu_rewrite/rewrite_architecture.md`**。
- frontmatter 修正（2026-09-26）：本指针原带 `doc_type: index`、后继件原带 `doc_type: architecture_view`，**一并清除为只带 `ttl: task_bound`**（豁免区新件禁 doc_type，EXEMPT-ZONE-FM 阻断门）。
- 原文去向：见上条 commit 指针；本路径不再承载任何"只有旧文才有"的结论。
