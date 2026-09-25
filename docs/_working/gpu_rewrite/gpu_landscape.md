---
ttl: task_bound
title: 【已并入】业界 GPU 回测/向量化方案全景（前一轮草稿指针）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
lane: LANE-GPU
family_id: GPU-REWRITE
superseded_by: docs/_working/gpu_rewrite/industry_gpu_landscape.md
---

# 本文件已被并入 industry_gpu_landscape.md

- 后继件：[`industry_gpu_landscape.md`](./industry_gpu_landscape.md)（本轮以 WebSearch/WebFetch 真查重采，关键结论各 ≥2 独立来源＋访问日期）。
- 改判留痕（防按旧引文施工）：其"vectorbt PRO 的 GPU 路线=JAX"与"QuantPits=GPU 暴力组合回测"两条本窗口复核失败，后继件 §四 分别降为**待验证**与**不采**；其"Spectre 77.7x/GPL/float32/look-ahead 警告"经复核成立并补年份与硬件口径。
- 新增入图（前一轮无）：RAPIDS 官方安装文档=**cuDF 不支持原生 Windows（仅 Linux/WSL2）**（决定性约束）；NVIDIA CCCL 确定性文（2026-03-05）＋CUDA FP 文档 v13.4（2026-09-13）＋PyTorch Reproducibility notes＝对拍分层三条公开依据；arXiv:2507.07107（2025，A 股涨跌停不可成交价污染＋GPU 因子批算 51x）。
- 受阻如实记录：NVIDIA 中文博客（A 股 RAPIDS 案例）404、cudf releases 403、Polars 官方 GPU 指南页 404——后继件 §四.3 逐条登记，未用聚合站内容充数。
- 并入核账（2026-09-26 双版合并，本条为真销口的凭据）：本草稿的**逐家实证表**（每家的 URL／发布方／年份／stars／许可证，挖矿 SOP 来源可溯闸）已整体补入后继件 **§一「结论 A 补 · 五家现成框架逐家实证表」**，
  含此前后继件完全缺失的 **LEAN** 一家，与前一轮独有的三条细证：qlib"GPU 只覆盖 ML 模型层、回测面 `Exchange`/`NestedExecutor` 无 GPU"、
  hftbacktest"**README 271 行零 GPU/CUDA 字样**＋官方教程页 233KB 零 GPU＋PyPI v2.4.4 `requires_dist` 仅 `numba~=0.61`"及其强项"L2/L3 tick 级全订单簿重建＋限价单排队位＋延迟建模"、
  vectorbt 开源版"**Numba CPU JIT 无 GPU**／自定义许可证 NOASSERTION／9.2k stars"；nautilus／LEAN 两家结论同表。总结论一句话（"五家现成框架回测核全是 CPU，改造它们改造不出 GPU；自研薄核＋CuPy 批量是正解，许可证面干净"）亦在该节。
- **部分并入判定（残留 3 条，逐条点名，禁含糊）**：本路径的**五家逐家实证表／自研 vs 改造裁定与总结论／来源清单 URL／Spectre 三宗罪／NVIDIA 114x 与 arXiv:2507.07107／JAX・taichi・numba 三载体判定结论**均已在案（见上两条）。
  但下列 3 条 A 版论断**未并入后继件**，本车道不在本窗口为其补证（其来源是二手 benchmark／会议页，按后继件"闸1 不采聚合站、复核失败即降级"的取证纪律本就无法入图，代并＝替它们作保），故本指针是**部分并入**而非全量：
  ①"cuDF 数值扫描类 ~30x（johal.in 2025 benchmark）／技术指标 rolling 类仅 ~2x（A6000，stockstats/TA benchmark 2025）→ GPU 不是免费午餐"；
  ②"Polars GPU engine 生产可用但表达式覆盖有洞（PyData London 2025 专场）"；
  ③"JAX＝PureJaxRL 系 33M steps/s 单 GPU 先例、`vmap` 批量=理论最优雅"（后继件 §二 末段已把 JAX/taichi 整体降为**待验证**，属有意降级非丢失，但该具体数未被保留）。
  **余下这三条见 git 历史 commit 37aeecedcd 的 `docs/_working/gpu_rewrite/gpu_landscape.md`（第 43、44、52 行）**；如需复活须按六向挖矿重采一手来源，**不得引本指针为据**。
- frontmatter 修正（2026-09-26）：本指针原带 `doc_type: index`、后继件原带 `doc_type: audit_report`，**两者一并清除为只带 `ttl: task_bound`**（豁免区新件禁 doc_type，EXEMPT-ZONE-FM 阻断门）。
- 原文去向：逐字比对见 git 历史 **commit 37aeecedcd 的 `docs/_working/gpu_rewrite/gpu_landscape.md`**（含其 §三 来源清单表；后继件行内已带同批 URL，独立表格形态未保留）。
