---
ttl: task_bound
completes_when: 台账与实物袋计数对平且两轮循环检查零问题
---
# 死信清偿专案 · 台账（生成器产出，禁手工维护）

- 生成：2026-10-09T05:31:28｜锚点 HEAD=`193dc9db3602`｜账面=**1704** 件（1701 袋 JSON+空壳 1+.bak-orig 1+后继 1）
- 实物分布：
  - dead: 1344
  - campaign_archived: 359
  - absent: 1

## 四终态账面计数

| 终态 | disposition | 袋数 |
|---|---|---:|
| ①复活工单在册 | `revive_with_ticket` | 1185 |
| ②归档留痕 | `archived_superseded` | 358 |
| ①新增件工单（需 token） | `revive_additive_new` | 89 |
| 呈报 Owner 门位 | `pending_owner` | 40 |
| ①重投在途 | `revive_requeue` | 14 |
| ④属主退回 | `returned_to_owner` | 12 |
| ③判废留痕 | `scrapped_recorded` | 5 |
| ①复活已落地 | `revive_landed` | 1 |

## 复核命令原文

```bash
cd /d/ZephyrAlpha
ls .runtime/commit_queue/dead/q-*.json | wc -l
ls .runtime/commit_queue/dead_archive_20261009_deadcure/ | grep -c '^q-'
cat .runtime/commit_queue/dead_archive_20261009_deadcure/manifest.jsonl | wc -l
python .runtime/tmp/st-deadcure-20261009/tools/account.py
python .runtime/tmp/st-deadcure-20261009/tools/verify_lanes.py
python .runtime/tmp/st-deadcure-20261009/tools/deadcure.py restore --qid <QID>
```
