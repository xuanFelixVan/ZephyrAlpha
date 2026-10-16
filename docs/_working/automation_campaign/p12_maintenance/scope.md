---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: ⑫后勤席·输入清单与写域
---

# ⑫ 后勤席 · 输入清单 / 写域 / 分母在册

## 1 写域（本席可写，改前 claim、毕后 release）

- `docs/_working/automation_campaign/p12_maintenance/instruction.md`
- `docs/_working/automation_campaign/p12_maintenance/scope.md`
- `docs/_working/automation_campaign/p12_maintenance/checkpoint.md`
- `docs/_working/automation_campaign/p12_maintenance/ledger.md`
- 本班在 `.runtime/tmp/p12_<NN>/` 的临时件（收班前必须清零）

**禁写面（越界即归属篡改/挪门柱）**：他席四件套与信箱面（`dispatch/`、`pulse/`、`feedback/`）、判据门柱与冻结值、分数册 only-add 面（`docs/04_research_records/backtest/scores/`）、SOP 本体、`config/` 图与判据 YAML、`scripts/` 与 `src/` 码面（工具修复一律开修改单转⑤席/工具班，本席不自改）。

## 2 输入口与实测分母（1016-01 班起手现测，date 2026-10-16 11:0x）

| 输入口 | 尺 | 起手读数 |
|---|---|---|
| 11 席台账 [BLOCKER] 全量 | `grep -rn "\[BLOCKER\]" docs/_working/automation_campaign/p*/ledger.md \| wc -l` | 188 行（⑤8／⑨13／⑩167／其余八席 0） |
| 当日（2026-10-16）[BLOCKER] | 同上再筛日期 | 尺 B（同行含 BLOCKER 且含 2026-10-16）＝157 行，全属⑩155＋⑤1＋⑨1（尺与⑩1016-13 班在册两尺同源） |
| ⑩晨报点名项 | `docs/_working/automation_campaign/dispatch/daily_dispatch.md` | 在册最新单＝2026-10-15 首单＋第十二单段（⑩按班追加） |
| 断链台账 | `docs/04_research_records/governance/working_ref_sweep_20261015/broken_records.yaml`（字段 file/line/target/batch/suggest/note，无 target_new） | 本班实测见台账 §3 |
| 队列四态 | `.runtime/commit_queue/{pending,processing,done,dead}` | 起手实测见台账 §4 |

## 3 巡检四维权重（合规巡检每班至少跑满一维全量）

1. 会话名规范：尺＝`session_registry.json` 条目 sid ∪ 队列袋 sid ∪ 台账自报 sid，正则 `^st-qoder-p(0[1-9]|1[0-2])-<MMDD>-<NN>$`；跑者位（非 p 前缀 sid）单独列册不自罚。
2. 输出内容格式：[BLOCKER] 行是否符合 §8-A-2 七段式（日期|席+班号|类型五选一|描述|证据锚点|要谁做什么|严重度）与零问题"无"行。
3. 存放位置合规（04 vs _working 两问制）：Q1 是否研究资产（成绩/卡/结论）→04；Q2 是否任务期运行面→`_working`；frontmatter `ttl` 只允许 permanent/task_bound，禁 doc_type。
4. 收班八件完成度：逐席按可观测面量（pid 文件／heartbeat.jsonl 末行／tmp 残留／worktree／[BLOCKER] 行有无）。

## 4 复发族登记册（同类第二次=立法候选报⑩，禁第三次）

| 族签名 | 首次在册 | 第二次 | 本席处置 |
|---|---|---|---|
| scaffold 裁定通道 CLI 缺失（alias 碰撞阻断新 .md，无 --force-override 腿） | 1016-01 本席直证 | 待下班复量 | 修改单转⑤席＋本席在册绕行（批量 token 通道） |
| heartbeat「注销」面与进程本体脱节 | ⑩1016-10（高）／1016-11（中） | 1016-10 与 1016-11 连续两班＝已第二次 | 立法候选，报⑩进 SOP 收班②措辞 |
| 主区 index 落后 HEAD 快照（落地收尾不回写） | ⑩1016-12 §30.2 | 1016-13 第十八件复现＝第二次 | 立法候选，报⑩；本席不代复位 |
| POOL-REGRESSION-DIRECTION 同签名跨席成串判死 | ⑩1016-02（14 枚/18 分） | 1016-04（18 枚/10 分「双侧皆改」）＝同域续现 | 已升级⑩呈批面，本席复量登记 |
