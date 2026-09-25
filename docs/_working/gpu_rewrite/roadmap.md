---
ttl: task_bound
title: 【已并入】迁移路线图（前一轮草稿指针）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
lane: LANE-GPU
family_id: GPU-REWRITE
superseded_by: docs/_working/gpu_rewrite/migration_roadmap.md
---

# 本文件已被并入 migration_roadmap.md

- 后继件：[`migration_roadmap.md`](./migration_roadmap.md)。
- 继承有效：Phase 序（L1→验证框架→L2 条件立项→L3 默认不做）、每步回滚点、负决策条款 N1–N6 的骨架、"跑中禁改引擎/prereg"的在飞约束。
- 按实测改判的四处：①新增 **Phase 0（实测定靶已完成）**；②②' 分片从"2 进程 ~2x"改为**内存决定进程数（实测单进程 RSS 4.46GB、可用 22.9GB、T1 仅占 1.0 核）→ 2–4 进程、CPU 侧近线性**，并给出 8 步半天拆解（含 N_eff/TrialLedger 只能做一次、prereg 帽不可被分片绕开、reaper keep 登记三处非显然坑）；③L1 收益线重锚为实测 8.6x（现状口径）/16.6x（扫描口径）；④新增 **N7**（分片实测 <2x 即退役该档）。
- 顺序反转说明：后继件把 ②' 提到 L1 之前（止血先行），并明确两者被"同一把文件锁"串起、不可同批施工。
- 并入核账（2026-09-26 双版合并，本条为真销口的凭据）：本草稿三项在改判中易被读成"丢失"，现明写落位——
  ①**硬件与调度红线**（显存配额 18GB、单卡独占 `vram.concurrency: 1`、与本地 LLM/夜窗互斥 `exclusive_group=gpu_default`、Kronos 峰值 7–8GB、**3090 FP64=FP32 的 1/64→必须 FP32＋容差路线**）
  → 后继件 §〇 表＋N5/N6＋挖矿日志 R6 **本已逐字在案**（数值已核一致：18GB 同 `03_gpu_campaign.md:24`、7–8GB 同 wo_gpu02 工单件）；1/64 那条另在④文 §一·补落一份（容差线真源位，2026-09-26 补）；
  ②**N1–N6 六条负决策条款**逐条对应后继件 N1–N6（N4 的"FP32 累积误差 >2bp 且 FP64 下 GPU 优势 <CPU 多进程 2x 即撤 L2"数值线未变），新增 N7 系实测追加；
  ③Phase 2 的"cProfile 实测热点"前置→后继件 Phase 0 **已完成**（①文实测分解），非取消。
- 全量并入判定：本路径（Phase 1–5 序与回滚点、总闸"产出密度决定 GPU 命运"、N1–N6、一页节奏）证据全部在案；
  被实测**改判**的两项（②' 分片"2 进程 ~2x"→"内存决定 2–4 进程、CPU 侧近线性"；L1 收益 3–7x→8.6x/16.6x）理由与实数都在后继件，属**有意改判非丢失**；逐字比对见 git 历史 **commit 37aeecedcd 的 `docs/_working/gpu_rewrite/roadmap.md`**。
- frontmatter 修正（2026-09-26）：本指针原带 `doc_type: index`、后继件原带 `doc_type: blueprint`，**一并清除为只带 `ttl: task_bound`**（豁免区新件禁 doc_type，EXEMPT-ZONE-FM 阻断门）。
- 原文去向：见上条 commit 指针；本路径只承担"防按旧清单施工"的指针职责。
