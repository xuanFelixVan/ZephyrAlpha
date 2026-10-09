---
ttl: permanent
doc_type: policy
rule_form: procedural
verifiability: manual
title: 场外区检索边界 SOP——工棚卷宗不入馆的边界登记与三源检索通道（F2 裁决落地）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-10-09
topic: library_sop
related: [docs/03_modules/_domain_library/blueprint.md, src/zephyr/library/collectors/fs_collector.py, docs/01_policies_and_standards/rules/trae_065_capability_lookup_required.yaml]
---

# 场外区检索边界 SOP（F2 裁决落地）

> **一句话**：`docs/_working/` 是 Owner 令的场外区（梵蒂冈条款），**按设计不入馆**——馆查不到不是病，病的是没人告诉检索者去哪查；本册登记边界+检索通道，宣判"图书馆致盲"案（GPU 摊销误报"未做"）的制度性根治。
> **裁决**：边界登记（b 案），**非**重收录（a 案）——a 案在逻辑上不可执行：给场外区文件补 `doc_type` 会被 EXEMPT-ZONE-FM 闸阻断（`exempt_zone_frontmatter_gate.py:8,52-57` "豁免区文件带 frontmatter doc_type 阻断"），且采集器按路径成分跳过 `_working`（`fs_collector.py:36,139`）根本不读 frontmatter。

## 1. 边界登记（收录判据真源指针）

| 事实 | 真源锚点 |
|---|---|
| `docs/_working/` 与一切临时区 = 场外区：免索书号、免 token、免 per-file 门禁；**不逐件入总账** | `docs/03_modules/_domain_library/blueprint.md` 场外区条款（梵蒂冈条款，Owner 2026-09-21 令） |
| 采集器按路径成分硬跳过 `_working`（不看任何 frontmatter） | `src/zephyr/library/collectors/fs_collector.py` `_SKIP_DIRS`（:36）+ 跳判（:139） |
| 场外区文件带 `doc_type` 反而是提交违规 | `src/zephyr/gov_enforcement/commit_gates/exempt_zone_frontmatter_gate.py:8,52-57` |
| 对账事实：跳过规则 2026-09-22 落地（de2d8df0664）后 `_working` 新增即 2816 件（2026-10-09 普查），全部按本设计不入馆 | `git log --since=2026-09-22 --name-only -- docs/_working/` |

## 2. 检索通道（对场外区资产作状态断言前的正查义务）

对任何资产作"未做/不存在/无此类"负存在断言前，MUST 走三源正查（trae_065 `asset_state_assertion` 触发面，F3 同批生效）：

1. **正门（一条命令）**：`python -m zephyr.library.lookup state "<关键词>"` ——三源证据包=①馆索引命中 ②git log --grep/-S 近 90 天 ③`docs/_working/`+config 工棚面扫描（F1 件，MOD 见 lookup 模块头；只读零副作用）。
2. **手工阶梯（F1 不可用时的降级序）**：
   - `git log --all --oneline --grep -i <关键词> --since=90.days`（中文兼容）
   - `git log --all --oneline -S <关键词去空格> --since=90.days`（pickaxe 补充通道）
   - `git log --since=<窗口> --name-only -- docs/_working/` + 对命中目录做内容 grep
3. **晋升通道**：场外卷宗确有长期价值 → 走晋升转正流程迁入正式区，迁入后自动入馆（梵蒂冈条款原文："晋升（转正）时才过门禁办 fully 身份"）。

## 3. 盲区对账形态（周期纪律）

- 盲区对账载体=blueprint 已预留的**盲册候选**面；本 SOP 不新建对账注册表（净零纪律）。
- 对账判据：`docs/_working/` 已提交文档（git log --diff-filter=A）凡检索通道可达（git log/grep 命中）=通道覆盖，非盲区；"馆查不到"本身不构成缺陷登记事由。
- 本案（GPU 摊销误报）复盘入 casebook_registry（F5 同批，case_id=0 开册）。

## 切换记录

- 2026-10-09 v1.0.0 首立（F2 裁决 b 案落地；与 F1 lookup state / F3 trae_065 触发面 / F4 挖矿 SOP 补节同战役批）。
