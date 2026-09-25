---
ttl: task_bound
title: 【已并入】计算热点普查（前一轮草稿指针）
created: "2026-09-25"
sid: st-gpu-rewrite-mining-20260925
lane: LANE-GPU
family_id: GPU-REWRITE
superseded_by: docs/_working/gpu_rewrite/hotspot_census.md
---

# 本文件已被并入 hotspot_census.md

LANE-GPU 车道前一轮（同名义、未落地）草稿路径。本轮重挖后按内收原则收敛为唯一真源，本路径只保留指针，防后人按旧清单施工。

- 后继件：[`hotspot_census.md`](./hotspot_census.md)
- 并入核账（2026-09-26 双版合并，本条为真销口的凭据）：本草稿两条量化口径**已补入真源**——
  ①"每格 **7 次引擎 pass**"的构成（五档各自全量重算 reindex/pct_change/涨跌停闸/gross/turnover＋`factory_grid_executor.py:777-778` 两连调重复＋掩码重复构建零缓存＝14 次 CH 往返＋7 次全量行循环）→ 后继件 **§二·补 口径①**；
  ②"**83% 热点的一半其实是'重复'而非'算力**"＋"纯代码整理（hoisting）即得 3–7 倍"→ 后继件 **§二·补 口径②**（同节记实测改判：83% 分母口径不成立、"重复"定性成立、收益上修 8.6x/16.6x）。
  硬件锚（3090 **FP64=FP32 的 1/64**、显存配额 **18GB**）→ 后继件④文 `verification_framework.md` **§一·补**（本家族容差线的真源位）。
- 全量并入判定：本路径的证据类内容（F1–F13 族清单与 file:line、锚定事实表、普查结论三句话、上述两条口径与硬件锚）**已全部在后继件或其同级真源在案**，故此指针成立；逐字比对原行文见 git 历史 **commit 37aeecedcd 的 `docs/_working/gpu_rewrite/compute_inventory.md`**。
- frontmatter 修正（2026-09-26）：本指针原带 `doc_type: index`、后继件原带 `doc_type: audit_report`，**两者一并清除为只带 `ttl: task_bound`**——豁免区（`docs/_working/`）新件禁 doc_type（EXEMPT-ZONE-FM 阻断门），留则整袋死门。
- 原文去向：除上述已在案项外无独有结论遗留在外；未经实测的推断（"稀疏权重 ≤2GB 显存"等）被本机分段计时＋cProfile 判否，判否理由在 successor §三/§四，不随本草稿复活。
