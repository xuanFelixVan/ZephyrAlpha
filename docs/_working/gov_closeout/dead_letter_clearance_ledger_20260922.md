---
ttl: task_bound
session: st-gov-closeout-20260922
title: "死信清账台账（382 口径实测 388 件全量验尸处置）"
date: "2026-09-22"
---

# 死信清账台账（.runtime/commit_queue/dead/，班次 st-gov-closeout-20260922）

> 依据：通宵执行令分包4（裁定#398七+#399四授权链）。实测口径：dead/ 面 388 件 q-*.json（指令书"382"为时点数）。
> 处置三态判据：逐件快照 file list × `git ls-tree HEAD` × `git diff --cached` 集合比对（脚本 `.runtime/tmp/dead_letter_verdicts.py`，中间件本 `.runtime/sessions/st-gov-closeout-20260922/staging/`）。
> **终态更新（06:4x）**：本班后续又归档 16 件（本班自身死信链 0008-0019 全部有后继批次取代，manifest_pass3+台账附注），归档累计 **296**，剩 **133** 件留置（分布见 §三·v2）。

## 一、总账（终态）

| 处置 | 件数 | 说明 |
|---|---|---|
| 归档清出 | **296** | 迁入 `.runtime/commit_queue/dead_archive/20260922_closeout/`（可逆移动，零删除；manifest 三份+本班链 9 件附注） |
| 留置在办/活车道 | **133** | 逐件三态+去向见 §三（v2 重新统计） |
| dead/ 面瘦身 | 388→133 | **-66%**；其中本班贡献吸收型归档的判据=file 级 HEAD 比对（169 件全吸收实证） |

## 二、归档 280 件构成（manifest=dead_archive_manifest.json / _pass2.json）

1. **≤2026-09-18 已收口车道** 56 件：24 车道（auto-derived-sync 11、solo_agent 6、st-autopipeline 5、st-btfix-p14 4、st-altdata 3、qoder-sop-review 3、st-ailayer 3 等）——战役均已在册收口，内容过期。
2. **absorbed 型** 169 件：快照文件 100% 已在 HEAD（st-data-fix 65、st-dloop 33、st-workclean 15、st-taskcards-exec 23、st-disk-ch 14、st-residual 2 等）——内容已由后续批吸收，requeue 无意义。
3. **已取代/代偿型 MIXED** 55 件：st-ulib-20260921 38（被 st-ulib2→本班承接）、st-disk-ch-20260921 16（乙线 a3 批 96864d1add 代偿）、st-tdchain-20260917 1——部分吸收+部分重构，残余内容以快照 blob 为准可恢复。

## 三、留置 108 件去向（dead_letter_remaining.json 逐件三态）

| 车道 | 件数 | 三态 | 去向 |
|---|---|---|---|
| st-workclean-20260921 | 58 | MIXED（心跳活） | 移交原车道：58 件部分在 HEAD/部分仍 staged，由其收口时按 own-diff 处置 |
| st-code-doc-20260921 | 34 | MIXED | **本班在办**：批 F（最新快照 q-0050 链）+批 D（q-0011）由分包2 requeue；WO-12/WO-16 重试件（q-0001/0002/0006/0009/0012/0014/0017/0021）已被已落地 commit 2fd1ce8ac4/de9b795162/6a6e77c8f0/83329aef38 取代，随分包2 完成后归档 |
| st-tilib-clear-20260920 | 6 | MIXED（心跳活） | 移交原车道 |
| st-taskcards-exec-20260921 | 3 | ALIVE_STAGED | 内容仍活在本班共享暂存区，移交原车道随其批次落地 |
| st-dataqa-20260920 / st-collintake-20260920 | 3 | MIXED | 移交（09-20 无心跳但不满足收口铁证，保守留置） |
| st-ulib2-20260921 | 2 | MIXED | 被本班 q-0001..0004 取代，本班落地验收后归档 |
| st-ulib-20260921 | 1 | ALIVE_STAGED | 内容在暂存区（=本班 43 批内件），本班落地即吸收 |
| st-data-fix-20260921 | 1 | MIXED（心跳活） | 移交原车道 |

## 四、死因分布（388 件全量，验尸面）

GATE-PRECOMMIT-RUN 70 ｜ CREATE-GUARD 41 ｜ DIRECTORY-CONTRACT 28 ｜ landing 异常 24 ｜ RULING-REFERENCE 18 ｜ NO-BARE-SQL 17 ｜ ALGO-FLOW-LINK 14 ｜ TTL-METADATA 13 ｜ EXEMPT-ZONE-FM 13 ｜ FOLDER-CAPACITY 11 ｜ 落盘失败杂项 11 ｜ TRANSLATION-COVERAGE 10 ｜ 其余（NEW-FILE-DEPGRAPH/CAPABILITY-OVERLAP/IMPORT-INTEGRITY/ORPHAN-MODULE/SESSION-REQUIRED 等）合计约 106。逐件 dead_reason 原文在档（各 q-*.json `dead_reason` 字段，归档件在归档舱同字段可查）。

## 五、结构性发现（供治理归口）

1. **零 absorbed 假象已破**：COMMIT_FAILED 主死因（352 件）表层全"NONE_IN_HEAD"，实为多文件批部分吸收——以 file 级比对为准，169 件实为全吸收。
2. **09-21 拥堵日**占 285 件：多会话共享暂存区竞争（丙线报告 §三 实锤的门禁注册半成品占位）是主根因，正门队列串行化已缓解。
3. **复活机制完好**：全部快照含 blob_sha256+blob_ref，`commit_queue.py requeue <qid>` 可复活任一归档件。
4. **本班实战场记账（附注）**：本班自身死信链 0001-0028 共 17 件（含重排件），全部逐条验尸对症修复合入后继批次——处方已沉淀：①gate+__init__ 注册对必须同 commit（ORPHAN-MODULE/IMPORT-INTEGRITY 双向）；②CREATE-GUARD 落地读 HEAD 册→token 批必须先行单独落地；③入队面 NO-BARE-SQL inline 预检无 AST 常量豁免（与锁内权威判据错位，逃生=行级 noqa 或原生通道）；④ALGO-FLOW-LINK 锚/yaml 双向原子约束必须同 commit；⑤CloneGuard 对同文件同名 Protocol 桩归一化误报，白名单无法抑制（同名单元素退化键），需结构分叉；⑥热册快照竞速：并发会话会整册重写（主区改注册表必死先例再证），token 批先行落地是唯一稳定序；⑦ALGO-NOTE-SYNC 的 note_confirmed 必须与实现触碰同 commit（HEAD 已有不算）；⑧GIT-DANGEROUS 全文扫描会命中"文档化危险命令"的历史 SOP/政策/归档文档（本班剔 5 件记欠账移交治理归口）。

## 五A、丙线批 D 残余（q-0028 死信快照保全，未清账项）

- 批 F（87 件修账+A14 生成器重建）已落地：**d9a09b2764** ✓
- 批 D（196 件归置）本班代落地修复四层机械死因（IMPORT-INTEGRITY/ALGO-NOTE-SYNC/BLUEPRINT-FORMAT×18 头部/GIT-DANGEROUS×5 文档），终态残余=**内容级违规**（ALGO-FLOW 缺锚 ex_core/okx_broker.py、ruff、debt-bridge、any-abuse）——按宪法 §3.4 owner 责任制不代修内容，快照保全于 dead/q-20260922-st-gov-closeout-20260922-0028.json（185 件含 blob），建议由内容作者车道修复后 requeue。
- 引用改齐欠账移交：agent_constitution_legacy_v1.md、industry_chain_data_audit_policy.md、construction_workflow_policy.md、document_review_and_optimization_policy.md、merge_conflict_resolution_policy.md（5 件历史文档正文含危险命令字样，本班剔除）+3 件 risk core（MOD-RK-20B/05C/05D grand-fathered 头部，无可落地差异）。

## 六、复核命令

```bash
ls .runtime/commit_queue/dead/*.json | wc -l          # 应=108
ls .runtime/commit_queue/dead_archive/20260922_closeout/ | wc -l  # 应=280
python .runtime/tmp/dead_letter_verdicts.py            # 复算三态（复跑前先重生成 verdicts 输入）
```
