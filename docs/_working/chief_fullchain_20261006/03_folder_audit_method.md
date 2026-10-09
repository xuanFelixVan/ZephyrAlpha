---
ttl: task_bound
completes_when: 战役收尾（99_final_delivery 落账）后随役归档 archive/2026-10
---

# [BLUEPRINT] | docs/_working/chief_fullchain_20261006/03_folder_audit_method.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

# docs/_working 战役文件夹审计方法（试点校准版）——st-workingchief-20261006

> 试点：10 役（map_build/circulation_chief/total_command_closeout/fullflow_mine/night_sweep/automation/registry_migration/commit_speedup_campaign/decision_map_campaign/meta_question_answers）→ 分布 CLOSED 1 / ACTIVE 3 / MIXED 6。

## §1 可靠信号（按强度）

1. `ttl: task_bound` + `completes_when` frontmatter——每役自带可机检完成判据，批量裁定第一锚。
2. 编号最大终局件的显式状态词：定稿/终局/收官/验收 PASS + 具体读数（"有具体读数的验收段 > 有 final 文件名"）。
3. 抢救归档痕迹：ledgers_archive/MANIFEST.md（sha256+冷库指针）=已进收编流程。
4. mtime 新近度+内容日期互证判 ACTIVE（排除批量落地）。
5. 交接令（HANDOFF/HANDOVER）+在-folder 无继任收口件 = MIXED。

## §2 不可靠信号

1. 文件夹名完全不可信（total_command_closeout 是最活跃的役；"closeout"是使命不是状态）。
2. 文件头部状态行会过期（circulation_chief 终报头与正文自相矛盾）——必须读到终局件正文结论段。
3. 仅凭 mtime 误判（批量落地把整目录 touch 成同一天）。
4. 自动生成 index.md 的 `status: active` 是模板噪音。
5. 文件计数会漂移（名义 33 实为 331 含子目录）——计数用字段实查。

## §3 裁定规则（推广到 113 役）

- **CLOSED** 需同时 4 条：①终局件+显式状态词；②completes_when 满足或具名继任接管；③≥7 天零变动（归档动作除外）；④无未执行工作包（开口项仅 Owner 呈批或已注册他役）。
- **ACTIVE**：≤2 天改动且内容吻合；或被他役引用为现行真源。
- **MIXED**：有终局报但 completes_when 未满足／wave-2 工作包未做／交接令无继任收口。
- **批量序**：mtime 排序→Grep `定稿|终局|收官|验收 PASS|MANIFEST` 采 CLOSED 候选→其余抽 ≤5 件精读。
- **处置**：CLOSED+archive_ready → `git mv` 整役至 docs/_working/archive/2026-10/<役名>/ + 终局件表头盖结案报告 + index 重建；MIXED/ACTIVE → 不动，登记 05 台账（其开口项已在役内自有追踪面，本役台账只留指针防双真源）。

## §4 个件盖章规约

- 章格式（沿用 st-fullchain-20260914 惯例）：`> ## 结案报告（2026-10-06 由 st-workingchief-20261006 核验）` + 总结论/已完成/未完成/核验方式/处置建议。
- 编辑纪律：lock_files claim → safe 写入 → release；他队 claim 冲突→跳过登记（R-1）。
