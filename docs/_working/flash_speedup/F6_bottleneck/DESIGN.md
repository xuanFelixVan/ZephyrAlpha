---
ttl: task_bound
completes_when: F6 提交堵点治本已落地并复核
rule_form: data
verifiability: machine
title: F6 作业簿——堵点本全量排查修复（三本 3572 行四态归属·零无主）
owner: ZephyrAlpha-Owner
session: st-flashspeed-20260918
language: zh
created: 2026-09-18
status: aggregated_total_ledger_landed
---

# F6 作业簿 — 堵点本全量排查修复（判据书 F6 / 三本全量）

> **一句话结论**：三本全量 **3572 行**（bottleneck_ledger 2312 + commit_block_events 1260）
> **四态归属完毕，UNCLASSIFIED=0（零无主）✓ 判据达标**。其中 **(a) 已覆盖 1983 行**（本战役
> F1/F4/F9 已治本 ≈167 行，R-06 纯噪声 1095 行，余 R-02/R-04/R-12/R-08/R-09 有主待裁定）；
> **(b) 净新病灶仅 26 行**（gate_id 归因观测缺口，非吞吐阻断，登记留 Owner）；**(c) 门禁判定
> 正确=使用摩擦 1433 行**（全路由 F5，门禁语义不动）；**(d) 死信残留/性能基线 130 行**（维护班
> 清账）。**真 100/h 杠杆=门禁退役（§4.2）=Owner 门位、AI 禁用。** 一页全场总账=
> `docs/_working/kimi_audit/lane_reports/F6_堵点总账.md`（Owner 必交件）。

## 0. 病灶（第一性原理）

堵点本三本是「提交链哪里卡、为什么卡」的全量证据。F6 任务=把每一行堵点归到「谁负责修」——
四态：(a) 已有治本件覆盖 / (b) 净新病灶需修 / (c) 门禁判对=使用摩擦转 F5 / (d) 死信残留。
判据=**零「无主」**（每行必有归属，不许有「不知道谁的」堵点）。病根=堵点本若有无主条目，
维护班无法清账、真堵点被噪声掩盖（R-06 告警自激 1095 行占全场 31% 即此病）。

## 1. 六向寻路台账

| 向 | 探查 | 结论 |
|---|---|---|
| ①上游 | 谁写堵点本 | `bottleneck_ledger.jsonl`：队列 drain 死信（`kind=dead_letter`，落地失败回退）+ daemon 积压告警（`kind=alert`，`commit_belt_daemon._check_ledger_backlog`）。`commit_block_events.jsonl`：`GitCommitGateway._audit_commit_block_event`（阻断）/`_audit_commit_slow_event`（慢提交 >60s）/`commit_ok_sample`（基线采样） |
| ②下游 | 谁消费 | 维护班清账（dead_letter protocol=「专人专事：高模型维护班清账，施工 AI 勿修」）；`commit_perf_report.py` 聚合 TOP 阻断门禁；A2 lane report（堵点本归因 TOP10）；本 F6 总账（四态归属） |
| ③算法机制 | 四态归属 | 正则归一 reason/detail 签名 → 按 R 因/治本件/门禁语义分类 → 全量对账（每行恰归一态，total=3572，UNCLASSIFIED=0）。脚本 `.runtime/tmp/f6_classify.py`（pickle 落 `.runtime/tmp/f6_classified.pkl`） |
| ④后端 | 无 DB 写 | 纯读 jsonl 聚合，零 DB 写、零 git 写（观测件分析） |
| ⑤前端 | 无 | 纯后端账本分析 |
| ⑥数据字段 | 计数口径 | bottleneck_ledger schema={ts,kind,qid/session_id,reason/alert,protocol}；commit_block_events schema={timestamp,session_id,event,gate_id,files_count,gate_chain_ms/total_ms,detail}。`gate_id="-"`=commit_slow/commit_ok_sample 性能采样（**非阻断**，设计如此 L1661）；`gate_id="UNKNOWN"`=归因缺口（见 §3 (b)） |

## 2. 治本设计（四态归属 + 全量对账）

### 2.1 全场对账（零无主）

| 态 | bottleneck_ledger | commit_block_events | 合计 | 占比 |
|---|---|---|---|---|
| (a) 已覆盖 | 1620 | 363 | 1983 | 55.5% |
| (b) 净新病灶 | 0 | 26 | 26 | 0.7% |
| (c) 使用摩擦→F5 | 598 | 835 | 1433 | 40.1% |
| (d) 残留/基线 | 94 | 36 | 130 | 3.6% |
| **总计** | **2312** | **1260** | **3572** | **UNCLASSIFIED=0 ✓** |

### 2.2 本战役已治本簇（167 行，实证）

| 治本件 | commit | 覆盖堵点 | 行数 |
|---|---|---|---|
| **F1** | `fe47296d` | R-01 派生写入（`rules_integrity_db.json`）：NOTHING_TO_COMMIT 假落地 ×87 + 入队基底冲突死信 ×58 + index.lock 互踩 ×77 的**根因**（派生提交并发） | 222（根因端掉） |
| **F9** | `3c853303da`（+#ARCH-330 `6ea82b9cfb`） | 队列 untracked 新文件落地死信：`pathspec ':(icase)<新文件>' did not match` ×11 + prestage add 警告 ×11 | 22 |
| **F4** | `025df945` | R-08 DEPGRAPH-FRESHNESS（15 生成器并发化，墙钟 57.4s→~28s） | 36 |

> **关键判定**：R-01 派生写入是**死信本最大真堵点簇（222 行）**——`rules_integrity_db.json`
> 被 golden-hash 保护 + 42 笔/24h 触碰 → 每笔 flush 无条件重登记 + 独立尾 commit → 派生写入
> 混入下一提交者 staged / 入队基底冲突 / index.lock 互踩。**F1（同 commit 原子化）已端掉根因。**
> 实测 index.lock 互踩 09-16T22 后零复现、NOTHING_TO_COMMIT 末次 09-17T05（F1 09-18 落地前）。

### 2.3 最大噪声簇（R-06，1095 行=全场 31%）

`bottleneck_backlog_threshold` 告警自激：`_check_ledger_backlog` 无状态变化检测，每 daemon tick
（积压≥阈值即）追加一行，间隔 P50=2.0s，09-16T08 单小时爆发 544 条。**纯噪声非真堵点**，抬高
维护班信噪比成本、掩盖真死信。治本=状态跃迁（正常→超阈）才落盘 + 同状态 30min 冷却窗
（S18-R1 噪声降级清单裁定范围，**待 Owner 签**）。

## 3. 四态明细（归属真源=总账 §2-§5）

- **(a) 1983 行**：R-06 ×1095 / R-04 claim ×227 / R-03 commit_slow ×192 / R-01 派生 ×145 /
  R-01-R05 index.lock ×77 / R-02 LOCK_TIMEOUT ×70 / R-12 DANGLING ×62 / R-08 DEPGRAPH ×78 /
  F9 pathspec ×22 / #ARCH-329 FOREIGN ×10 / R-09 PARSE ×5。**全部有主**（F1/F4/F9 已治本 or
  S18-R1~R4 裁定书 or 根因表登记）。
- **(b) 26 行（唯一净新病灶）**：`commit_block_events` gate_id 归因缺口（`UNKNOWN`）。机理=
  `_audit_commit_block_event` gate_id 判定链（`_STATUS_GATE_ID` 映射 > `门禁 XXX 阻断` 正则）
  未覆盖 **worktree/landing 路径**（session_worktree.py）消息格式：worktree base 过期 rebase 冲突 ×8 /
  pre-commit gate 阻断（worktree 路径）WORKTREE-REQUIRED ×4 / worktree base 对齐阻断 ×4 /
  FOREIGN_CHANGE_VIOLATION ×5 / 余 ×5。**判定=观测缺口（非吞吐阻断，阻断本身正确）**；2026-09-13
  「UNKNOWN×6 治本」只覆盖 gateway 路径=治本不完整。**处置=登记+设计已给，本战役不实现**：
  ①F6 判据（零无主）已达标（26 行经 detail 文本全部人工归因）；②修复=audit-only 正则/映射扩展
  （零行为变更）但触碰热保护文件 git_commit_gateway.py（altdata 并发中），低价值高风险比；
  ③治本设计=扩展判定链匹配 worktree 格式（`pre-commit gate 阻断.*?: ([A-Z\-]+):` +
  `（([A-Z_]+_VIOLATION)）` 映射 + landing 冲突归 `WORKTREE-BASE-CONFLICT` 伪门禁）。**留 Owner
  裁定是否纳入 S18-R1 同批。**
- **(c) 1433 行**：门禁判定正确=使用摩擦。语义型门禁真触发 ×1271（ALGO-NOTE-SYNC/CREATE-GUARD/
  MODULE-ID/SSOT/NO-BARE-SQL/TTL-METADATA/COMMIT-SCOPE/CAPABILITY-LOOKUP-REQUIRED/SESSION-REQUIRED
  等，A2 榜 TOP10 已逐项核「设计如此」）+ F5 靶点 DC ×62 + WORKTREE-REQUIRED ×55 + FOLDER-CAPACITY ×45。
  **全路由 F5**（前置提醒/文档化降摩擦），**门禁语义不动**（指令禁动判据）。
- **(d) 130 行**：死信残留/其他 ×77（含 `Author identity unknown` git config 环境 ×17，protocol=
  维护班清账）+ commit_ok_sample 性能基线 ×36（非堵点）。

## 4. 判据映射（S18_Flash施工包判据 F6）

| 判据 | 验法 | 结果 |
|---|---|---|
| 每条堵点归四态之一 | §2.1 全量对账：3572 行 = (a)1983+(b)26+(c)1433+(d)130 | ✓ |
| **零「无主」条目** | `f6_classify.py` UNCLASSIFIED 计数 | ✓ **UNCLASSIFIED=0** |
| 已知疑点全部排查 | NOTHING_TO_COMMIT×87→(a)R-01/F1；git reset rc=128×48+18→(a)R-01/R-05；TTL-METADATA×90→(c)；WORKTREE-REQUIRED×55→(c)；HELD-OVERLAP×45→(a)R-04；block_events 空 gate_id×221→**性能采样 commit_slow/ok_sample（非堵点，疑点消解）** | ✓ 全排查 |
| 不拿 symptomatic 当治本 | 加大超时/重试/日志降级=只记账（根因表§止痛件表已载 index.lock×48/GATE-REGENERATE 180s/DEPGRAPH 阈值）；本簿治本=F1 原子化/F9 续租/F4 并发（均结构性） | ✓ |

## 5. 挖后自审闸（三态）

- **量尺**：终局 50-100 车道并发，堵点本可读性=维护班清账效率=提交链健康度。
- **三态裁定**：
  - **施工（已完成）**：三本全量四态归属 + 零无主对账 + 一页全场总账（Owner 必交件）落地。
    本战役已治本簇（F1/F4/F9=167 行）实证登记。
  - **登记（不可自裁定/低价值）**：(b) gate_id 归因缺口 ×26（设计已给，热文件风险，留 Owner）；
    R-06 告警自激 ×1095（S18-R1 裁定）；R-04/R-02（S18-R3 裁定）；门禁退役（§4.2 Owner 门位）。
  - **转 F5**：(c) 1433 行使用摩擦（DC/FOLDER-CAPACITY/WORKTREE-REQUIRED 162 行可前置化）。
- **过度工程三问**：①是否消灭人工参与？是（四态自动归属 + 零无主对账，维护班按态清账）。②是否
  引入第二真源？否（复用 R-01~R-12 根因表 + A2 归因 + 既有治本件 commit，单一真源=堵点本 jsonl）。
  ③现状规模小是否成为封矿理由？否（按终局 100 车道判：堵点本行数随车道线性增长，四态归属框架
  + 零无主对账是可复用的清账基建，非一次性）。

## 6. 施工日志

| 时间 | 动作 | 结论 |
|---|---|---|
| 2026-09-18 | 读三本 schema + R-01~R-12 根因表 + A2 lane report | 确认四态分类口径 + 已知疑点清单 |
| 2026-09-18 | 写 `f6_aggregate.py` 聚合（kind/gate_id/reason 签名） | bottleneck=dead_letter 1217+alert 1095；block_events 按 gate_id（`-`×228 疑点） |
| 2026-09-18 | 排查 `gate_id="-"`×228 + `UNKNOWN`×26 | `-`=commit_slow 192+ok_sample 36 性能采样（**非堵点，疑点消解**）；UNKNOWN=worktree 路径归因缺口 |
| 2026-09-18 | 排查 (b) 候选时间线（git_reset/nothing_to_commit/pathspec/conflict） | 全部 09-16/09-17 止，根因=`rules_integrity_db.json` 派生写入（R-01）→ F1 已治本；pathspec→F9 已治本 |
| 2026-09-18 | 写 `f6_classify.py` 四态归属 + 全量对账 | 3572 行 UNCLASSIFIED=0 ✓；(a)1983/(b)26/(c)1433/(d)130 |
| 2026-09-18 | 落一页全场总账 `lane_reports/F6_堵点总账.md`（Owner 必交件） | 四态归属 + 已治本簇 + 噪声簇 + Owner 裁定项 5 件 |
| 2026-09-18 | 三态裁定 | 施工完成（归属+对账+总账）+ 登记（(b)/R-06/R-04/R-02/退役）+ 转 F5（(c)1433） |

### 验收结论（F6）

| 判据 | 结果 |
|---|---|
| 每条堵点归四态 | ✓ 3572 行全归属 |
| 零「无主」 | ✓ UNCLASSIFIED=0 |
| 已知疑点全排查 | ✓ NOTHING_TO_COMMIT/git reset/TTL-METADATA/WORKTREE-REQUIRED/HELD-OVERLAP/空 gate_id 全归位 |
| 一页全场总账（Owner 必交件） | ✓ `lane_reports/F6_堵点总账.md` |
| 不拿 symptomatic 当治本 | ✓ 治本=F1/F4/F9 结构性件；超时/重试/日志只记账 |

### 留给 F5 的实证（(c) 路由）
DC ×62 + FOLDER-CAPACITY ×45 + WORKTREE-REQUIRED ×55 = 162 行可前置化（preflight 提醒）；
余 1271 行=施工者不看报错即重试（A2 §3.1 成因链），治本在报错文案精确化 + 队列同 qid 同原因合并死信。
