---
ttl: task_bound
title: 【已并入】等价性验证框架（前一轮草稿指针）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
lane: LANE-GPU
family_id: GPU-REWRITE
superseded_by: docs/_working/gpu_rewrite/verification_framework.md
---

# 本文件已被并入 verification_framework.md

- 后继件：[`verification_framework.md`](./verification_framework.md)。
- 继承有效：层1 逐位（只对不改浮点序的 L1）／层2 统计量容差／层3 排名严格 的三段制；边界格思路；fail-closed 与"争议格 FP64 仲裁"通道；"判定函数两侧共用同一实现"。
- 本轮补强：①三层判据各配公开数值文献（CUDA FP v13.4／NVIDIA CCCL 2026-03-05／PyTorch Reproducibility），不再以工程偏好立线；②边界格由 7 类扩至 E-1…E-10 并给出实测料量（all_a 窗口封板 118,207/47,968 格、`stk_limit` NULL 0.058%、权重非零 47.9%）；③新增两条守护测试——"0bp 档与 5bp 档 net 必不同"与"滑点档禁位置传参"（后者是仓内真实事故：五档恒同值=门形同虚设）。
- 未改项（纪律）：17 号文与 `config/exam_scale_cost_gate.yaml` 的口径、阈值、档位真源一律引用不改写；本框架只增"实现等价性"一维，不替代多校链。
- 并入核账（2026-09-26 双版合并，本条为真销口的凭据）：本草稿的**对拍容差冻结值**已在后继件 **§一·补「对拍容差冻结值」表**逐条核账并全部在案——
  net 序列逐日相对容差 ≤**1e-5**（FP32 路径）／≤**1e-8**（FP64 路径）、sharpe 与 **ann_return** 绝对差各 ≤**0.005**、max_drawdown 相对差 ≤1e-4、期末净值差 ≤**2bp**、离散量 **100% 精确一致**；
  其中 **ann_return 的 0.005 在合并前于后继件 §二 层2 判据格里未单列**（只具名 sharpe）→ 已补入该行；
  同节并入 **FP32 累积误差定量预检**（1,650 日 `cumprod` 的 FP32 vs FP64 期末净值差实测，**>2bp 即判 L2 方案不达标**、升级"关键累计段 FP64"并重签容差线）——
  预检窗口以后继件①文实测 **1,622 评估日**为准，1,650 作历史口径存档（差＝窗口切法，非结论冲突）。
  另：本框架的**硬件红线（3090 FP64=FP32 的 1/64）**在合并前只存在于③文，现已在后继件 §一·补落为容差线的"因"（同节并记 18GB 配额／单卡独占／`exclusive_group=gpu_default` 与本地 LLM 互斥三条）。
- 全量并入判定：本路径（三层判据、边界格思路、fail-closed 与 FP64 仲裁通道、判定函数两侧共用同一实现、§四 框架自身止损线）证据全部在案；边界格由本稿 7 类扩为后继件 E-1…E-10 并配实测料量，属**超集非替换**；
  本稿"业界标准 1e-8~1e-6 通行误差带"与"cuFFT determinism docs"两句系二手/含混引法，后继件已以三条一手来源替换（CUDA FP 文档 v13.4／NVIDIA CCCL 2026-03-05／PyTorch Reproducibility notes，见其 §一 表），
  并在 §八 挖矿日志 R7 如实记"检索未见规范化公开协议（受阻/查无）"——**该两句不随本指针冒充依据，属取证升级非内容丢失**；逐字比对见 git 历史 **commit 37aeecedcd 的 `docs/_working/gpu_rewrite/validation_framework.md`**。
- frontmatter 修正（2026-09-26）：本指针原带 `doc_type: index`、后继件原带 `doc_type: blueprint`，**一并清除为只带 `ttl: task_bound`**（豁免区新件禁 doc_type，EXEMPT-ZONE-FM 阻断门）。
- 原文去向：见上条 commit 指针。
