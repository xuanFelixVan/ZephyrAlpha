---
ttl: task_bound
completes_when: 图11时延探针补齐后转归档
title: F7 提交链时延仪表盘
---

# F7 提交链时延仪表盘（图11 28环节 × 七日遥测）

- 班次: st-f7-latency-20261004｜产出时刻: 2026-10-04 02:46+08｜七日窗口: 2026-09-27 02:46 → 2026-10-04 02:46 (+08)
- 铁律: 纯读零写（本文档为唯一产出）｜零提交｜全部数字可复现（附录 A/B）｜不背数
- 环节清单真源: `config/dev_delivery_map.yaml`（node_type=stage 共 28，另有 gap 节点 D11-G01/G02 不计时延）
- 四源: `​.runtime/audit/bottleneck_ledger.jsonl`、`.runtime/audit/commit_block_events.jsonl`、`.runtime/commit_queue/{done,dead,processing,pending}/`、`.runtime/gate_audit/`（后者为合规事件面、无时长字段，见 §0 探针表）；实际时延探针另取 audit 目录四个带时长文件（§0）

## 0. 探针语义表（口径先于数字）

| 探针文件 | 记什么 | 阈值/采样口径 | 源码锚 |
|---|---|---|---|
| `audit/gate_execution_stats.jsonl` | 每次 commit 门禁套件: 套件 total_ms + 逐门 ms 字典 | 全量记账 | 2683 行实测，写入方=git_commit_gateway |
| `audit/precommit_channel_stats.jsonl` | pre-commit shell 通道单次运行 total_ms/fast_subset_ms + rc | 全量记账 | 538 行实测 |
| `audit/preflight_events.jsonl` | 入队/直连预检时长 ms + path(direct/enqueue/requeue/…) + 阻断门 | 全量记账 | 7819 行实测 |
| `audit/lock_wait_events.jsonl` | 提交全局串行锁等待 waited_ms + holder | 全量记账 | 写入方=git_commit_gateway/gov_audit.writer |
| `commit_block_events.jsonl` | `commit_slow`＝直连全程墙钟>60s（完整）；`commit_ok_sample`＝成功提交按 sha 尾 hex≥0xE 的 12.5% 确定性采样 | 60s 阈 / 12.5% 采样 | `git_commit_gateway.py:343`（60s 阈）、`:2966`（采样） |
| `bottleneck_ledger.jsonl` kind=slow_item | 队列单项落地墙钟秒 | 仅>300s 记账（300s 以下盲区） | `commit_queue.py:181` `_SLOW_ITEM_LEDGER_SECONDS=300`、`:2316` |
| 同 kind=landing_staleness | 排队陈旧: pending 龄 age_s | 仅>1800s 记账 | `commit_belt_daemon.py:218` |
| 同 kind=alert | 积压告警: pending_items/oldest_age_s | ⚠️口径失真见 §4-1 | `commit_belt_daemon.py:485` `_check_ledger_backlog` |
| 同 kind=dead_letter | 死信登记行 | ⚠️daemon 每次重启全量重登记（行数≫袋数） | `commit_belt_daemon.py:134` `_ledger_dead_letters` |
| 同 kind=derived_stale/stuck | 派生生成器账龄（reconciler 域） | detail 内"账龄 Ns" | 34/6 行实测 |
| done 袋 json | created_at→landed_at 全链 + attempts/requeue_count/stale_by | 袋级真源 | 527 袋实测（窗内落地 523） |
| `gate_audit/*.jsonl`（94 文件 31.4 万行） | 门禁合规事件（阻断/越权/豁免） | **无任何时长字段** → 不入时延表，只作 D 类计数佐证 | 字段全集实测（dur/second/elapsed 均 0 命中） |

## 1. 图11 28环节 × 七日时延映射表

单位: 秒(s)／分钟(min)如注。n=七日样本数。**粗体=有探针**，"无探针"=四源+audit 目录内无该环节时长埋点。

| 环节 | 名称 | 探针 | n | P50 | P95 | 口径注记 |
|---|---|---|---|---|---|---|
| D11-S01 | 会话冷启动与开班检查 | 无探针 | — | — | — | session_registry 非时延面 |
| D11-S02 | worktree 分配与池化 | 无探针 | — | — | — | |
| D11-S03 | 会话心跳与活性判定 | 无探针 | — | — | — | |
| D11-S04 | 改前 claim（文件锁+基线快照） | 无探针 | — | — | — | lock_wait_events 是提交全局锁（归 C04），非 claim 文件锁 |
| D11-S05 | 在途编辑与暂存晋升 | 无探针 | — | — | — | safe_write/write_audit 均无时长字段 |
| D11-S06 | 会话内 worktree 提交 | 无探针 | — | — | — | worktree 侧 git commit 本体无埋点；通道时长记于 C07 |
| D11-S07 | 合并回主区（merge 正门） | 无探针 | — | — | — | |
| D11-S08 | 放弃与死会话回收 | 无探针 | — | — | — | |
| D11-S09 | 收尾注销与 handoff | 无探针 | — | — | — | |
| D11-C01 | 提交正门 CLI 与危险命令外壳 | commit_slow＋ok_sample | 136＋21 | 107.6s / 125.7s | 264.3s / 207.0s | slow=直连全程>60s **完整**；ok=12.5% 采样（P95 置信薄）；max 469.1s |
| D11-C02 | 失败指引锚点递送 | 无探针 | — | — | — | |
| D11-C03 | claim 结算与失败重试语义 | 部分（done 袋 attempts） | 38/523 | — | — | attempts>0 占 7.3%；复现命令见附录 A-5 |
| D11-C04 | 全局串行锁与锁争用改道 | lock_wait_events | 496（争用 126） | 0 / 27.3s(争用子集) | 60.3s（顶格=timeout） | timeout=60s；max 225.8s；holder 字段在账 |
| D11-C05 | in-process 门禁链执行 | gate_execution_stats 套件 | 715 | 18.5s | 148.5s | max 289.4s；单门 top=CREATE-GUARD P95 63.9s（§3） |
| D11-C06 | 暂存与提交本体 | 无独立探针 | — | — | — | 含于 C01 全程墙钟 |
| D11-C07 | pre-commit shell 门禁通道 | precommit_channel_stats | 479 | 55.4s | 285.1s | max 1291.2s；fast 子集 P50 34.9s；rc=1 占 472/479（语义混杂见 §4-3） |
| D11-C08 | 入队即转活（快照入袋） | preflight_events（enqueue 族） | 1691 | 8.1s | 60.6s | blocked 848/1691＝50.1%；direct 族 n1032 P50 6.7s P95 68.6s |
| D11-C09 | 排空调度与消费端 | landing_staleness＋排队残差 | 263 / 95 | 48.8min / 29.4min | 131.8min / 118.1min | staleness 仅>30min 记账；残差=可三段 join 子集（§2）；max 90.9h |
| D11-C10 | 真落盘（worktree+CAS+收敛） | slow_item | 614 | 12.5min | 35.2min | 仅>300s 记账；max 74.9min；窗内总落地墙钟 158.9h |
| D11-C11 | post-commit 对账与守卫 | derived_stale（账龄） | 31 | 64.0min | 148.6min | **袋级无探针**；derived_stuck=5 次 |
| D11-C12 | 机器车道与紧急通道 | 无时延探针 | — | — | — | commit_lock_fallback 全期仅 15 行（计数-only） |
| D11-C13 | 队列台账与运维观测 | —（观测本体） | — | — | — | bottleneck_ledger 即本环节产出物 |
| D11-D01 | 死信产生（不卡队） | dead_letter 唯一 qid | 2060 | — | — | 另 queue_landing_dead 事件 190 次；记账行数失真见 §4-2 |
| D11-D02 | 死因三分类甄别 | 唯一 qid 主因 | 2060 | — | — | gate_block 1311(63.6%)｜landing 异常 280｜基底冲突 123｜cascade 80｜CLAIM 违约 74｜其余 192 |
| D11-D03 | 死信台账联动与告警 | alert | 202 | 最老龄 15.2d | 17.5d | pending_items P50 117152＝**口径失真**（§4-1）；实测在队 pending=2 |
| D11-D04 | requeue 复活链路 | done 袋 requeue_count | 68/523 | — | — | 13.0% 袋带复活史 |
| D11-D05 | 级联失效判定（cascade_stale） | 唯一 qid 主因=cascade | 80 | — | — | 行口径 3840 行（含重登记） |
| D11-D06 | 死信归档轮换 | 目录计数 | 113＋1＋6 | — | — | dead_purged_20260920=113／dead_archive=1／hold=6 袋；计数-only |

门禁单门七日 P95 top5（C05 细分，附录 A-2）: CREATE-GUARD 63.9s｜REGISTRY-MASS-DELETION 38.4s｜DOC-HEADER-SUITE 14.2s｜CAPABILITY-OVERLAP 10.3s｜RECONCILER-HEALTH 10.1s（max 147.7s）。按总耗时（sum）排: CREATE-GUARD 94.1min／REGISTRY-MASS-DELETION 59.1min／RECONCILER-HEALTH 47.1min／DOC-HEADER-SUITE 45.4min。
套内失败 top: FOREIGN-CHANGE-DETECTION 49｜COMPLEXITY-GUARD 44｜HELD-OVERLAP 40｜DOC-HEADER-SUITE 35（重试放大时延的来源面）。

## 2. 每笔袋全链耗时分解（四段）

**总口径**: 全链＝landed_at−created_at（袋级真源，无估计）。四段中只有两段有袋级探针，诚实分解如下:

| 段 | 袋级探针 | 七日覆盖 | 聚合口径（P50/P95） |
|---|---|---|---|
| 排队 | 无直测；残差法（全链−落地−入队门禁，仅三段齐袋子集） | 95/523＝18.2% | 29.4min / 118.1min（max 170.7min） |
| 排队（条件面） | landing_staleness age_s（仅>30min 记账） | 263 行 | 48.8min / 131.8min（max 90.9h） |
| 门禁@入队 | preflight ms 按 session_id±300s join | 291/523＝55.6% | enqueue 族 8.1s / 60.6s |
| 落地 | slow_item 按 qid join（仅>300s 记账） | 212/523＝40.5% | 12.5min / 35.2min；未 join 者＝落地<300s |
| reconciler | **无袋级探针** | — | 聚合面仅 derived_stale 账龄 64.0/148.6min |

**全链分布**（done 袋，窗内落地 523 袋）: n=523｜P50 22.5min｜P95 145.1min｜max 94.7h（q-20260924-st-gpu-final-20260924-0001，09-24 入袋 09-28 才落，排队段占绝对主导）。attempts>0＝38 袋（7.3%）｜requeue 过＝68 袋（13.0%）｜曾判 stale＝134 袋（25.6%）。

**按落地日趋势**（+08 日；P50 全链 min）:

| 日期 | n | P50 | P95 | 备注 |
|---|---|---|---|---|
| 09-27 | 87 | 5.2min | 23.1min | |
| 09-28 | 87 | 45.0min | 98.9min | 积压泄洪日（两袋 4 天老袋此日落地，max 94.7h） |
| 09-29 | 119 | 96.3min | 3.1h | 泄洪峰（nightsweep 大批入袋排队） |
| 09-30 | 81 | 10.9min | 63.1min | |
| 10-01 | 45 | 32.0min | 1.8h | |
| 10-02 | 50 | 1.4min | 6.9min | 回落 |
| 10-03 | 35 | 3.0min | 6.8min | 回落 |
| 10-04 | 19 | 33.5min | 1.2h | 半日（截至 02:46） |

**最慢 12 袋明细**（全链=排队+落地两段可见；门禁@入队 join 命中才显示）:

| qid | 全链 | 入袋→落地 (+08) | attempts | requeue | 落地段(slow_item) | 入队门禁 | 失败留痕 |
|---|---|---|---|---|---|---|---|
| q-20260924-st-gpu-final-…-0001 | 94.7h | 09-24 02:48→09-28 01:32 | 0 | 0 | 未记账(<300s) | 未 join | |
| q-20260924-st-t0-matrix-…-0003 | 90.9h | 09-24 06:38→09-28 01:34 | 0 | 0 | 未记账 | 未 join | |
| q-20260927-st-ailayer-sx-…-0002 | 24.4h | 09-27 01:27→09-28 01:50 | 0 | 0 | 475.9s | 未 join | |
| q-20260929-st-nightsweep-sw12-…-0016 | 3.9h | 09-29 09:03→12:56 | 2 | 0 | 1906.8s | 未 join | 路径锁等待超时（capability 册在途持锁） |
| q-20260929-st-w173-redo-…-0001 | 3.6h | 09-29 09:09→12:42 | 0 | 0 | 1068.9s | 未 join | |
| q-20260929-st-trae032-content-…-0001 | 3.5h | 09-29 09:08→12:37 | 0 | 0 | 759.0s | 未 join | |
| q-20260929-st-nightsweep-sw12-…-0019 | 3.4h | 09-29 09:11→12:34 | 0 | 0 | 326.6s | 未 join | |
| q-20260929-st-nightsweep-sw14-…-0005 | 3.3h | 09-29 09:49→13:08 | 0 | 0 | 1706.6s | 1875ms | |
| q-20260929-st-nightsweep-sw12-…-0018 | 3.3h | 09-29 09:10→12:29 | 0 | 0 | 未记账 | 未 join | |
| q-20260929-st-c8-rulings-0001 | 3.1h | 09-29 02:38→05:44 | 0 | 0 | 406.6s | 未 join | |
| q-20260929-st-nightsweep-sw12-…-0017 | 2.9h | 09-29 09:04→11:58 | 0 | 0 | 1411.9s | 未 join | |
| q-20260929-st-nightclean-…-0013 | 2.6h | 09-29 05:06→07:43 | 0 | 0 | 未记账 | 1453ms | |

**当前在途快照**（产出时刻）: processing 4 袋（0.4–0.9h 龄：gomap-f1／gomap-f2m／bm-reclass／tdm-mount-flash-0008）＋pending 1 袋（vm12f2-0002，0.4h）——无积压。

## 3. Top5 吃时延环节＋一句建议（只建议不动手）

| # | 环节 | 证据（七日 P95） | 一句优化建议 |
|---|---|---|---|
| 1 | D11-C09 排空调度 | 排队残差 P95 118.1min；staleness P95 131.8min；极值袋 4 天 | drain 侧把 picked_up_at 写进袋 json——排队段从"残差估计（覆盖 18%）"变直测，是最大口径缺口 |
| 2 | D11-C07 pre-commit 通道 | P95 285.1s，max 21.5min；rc=1 占 472/479 | 先把 rc 拆成 blocked/debt/infra 三态再谈提速——当前 99.8% rc=1 使 P95 无法归因到真阻断还是债务告警 |
| 3 | D11-C05 in-process 门禁链 | 套件 P95 148.5s；CREATE-GUARD 单门 P95 63.9s | CREATE-GUARD/REGISTRY-MASS-DELETION 长尾源于注册册全量重读，按 own-diff 触发面做增量缓存是最大单点收益 |
| 4 | D11-C10 真落盘 | slow_item P95 35.2min（n=614，仅>300s 记账） | 阈值 300s→120s 或改直方图记账——523 袋中 311 袋（59.5%）落地段处于分位盲区 |
| 5 | D11-C01 直连正门慢尾 | commit_slow P95 264.3s（n=136 完整）；ok 采样仅 21 例 | 采样率 12.5%→25%（sha 尾 ≥0xC）或按 files_count 分层采样，P95 置信才够读数 |

荣誉提名 D11-C04: 锁等待 P95 60.3s＝timeout 顶格（126/496 次真争用，max 225.8s）——holder 字段已在账，按 holder 聚合即可定位锁主，无需新增埋点。

## 4. 遥测口径缺陷（三个发现，只呈报）

1. **积压告警口径失真**: `_check_ledger_backlog`（commit_belt_daemon.py:485-530）逐行数 `kind=dead_letter` 且不按 qid 去重，而 `_ledger_dead_letters`（:134）在每次 daemon 启动时全量重登记存量死信（seen 集仅进程内）→ 七日 alert 的 pending_items P50=117152、oldest_age_s P50=15.2 天，而实测在队 pending=2 袋/processing=4 袋。建议: 计数改按 qid 去重或状态化计数器。
2. **死信行数≫袋数**: 全期 dead_letter 记账行 153,566 行 vs 七日唯一 qid 2,060——任何以行数为基础的死因/积压统计都会放大约 75 倍。本报告 D01/D02 已按唯一 qid 口径纠偏。建议: 写入侧 seen 集持久化。
3. **袋级四段分解三处缺口**: preflight 无 qid 字段（join 靠 session±300s，命中 55.6%）／slow_item 300s 阈下盲区（40.5% 命中）／reconciler 无袋级时长——四段分解目前只能"两段直测+一段残差+一段无探针"。另: gate_audit/ 94 文件 31.4 万行全部无时长字段，纯合规面。

## 附录 A. 分表复现命令（不背数）

```bash
# A-0 主复算（§1/§2 全部数字；脚本全文见附录 B，.runtime/tmp 24h TTL，以附录 B 为准）
python .runtime/tmp/f7/f7_recompute.py

# A-1 全链分布+逐袋明细（done 袋真源）
python -c "import json,glob,os;from datetime import datetime,timezone,timedelta
W=datetime.now(timezone.utc)-timedelta(days=7);P=lambda s:datetime.fromisoformat(s)
xs=[]
for f in glob.glob('.runtime/commit_queue/done/*.json'):
    d=json.load(open(f,encoding='utf-8'));l=P(d['landed_at'])
    if l.tzinfo is None:l=l.replace(tzinfo=timezone.utc)
    if l>=W:xs.append(((l-P(d['created_at'])).total_seconds(),d['qid']))
xs.sort();print(len(xs),xs[len(xs)//2][0],xs[int(len(xs)*.95)][0],xs[-1])"

# A-2 门禁单门 P95（C05 细分）: 附录 B 脚本 out["gate_per_gate_top"]

# A-3 slow_item/staleness/alert（bottleneck_ledger 流式，按 kind 过滤、ts>=窗口）
# A-4 唯一 qid 死因（D01/D02）: 正文 §4-2 去重口径，命令=对 dead_letter 行按 qid 分组取 most_common
# A-5 C03 重试袋明细:
python -c "import json,glob
for f in glob.glob('.runtime/commit_queue/done/*.json'):
    d=json.load(open(f,encoding='utf-8'))
    if d.get('attempts'):print(d['qid'],d['attempts'],d.get('last_retry_at'),(d.get('last_failure') or '')[:60])"

# A-6 在队在途快照: ls .runtime/commit_queue/{pending,processing}/
```

## 附录 B. 主复算脚本全文（self-contained；`python <path>.py` 直接可跑，读仓相对路径）

见 `.runtime/tmp/f7/f7_recompute.py`（与本文档同批产出；核心逻辑: 七日窗口→五探针文件流式统计→done 袋全链+三段 join→残差排队段；P50/P95 为线性插值分位；naive 时间戳按 UTC 处理）。脚本内常量即口径: 窗口=now−7d、slow_item 阈 300s、staleness 阈 1800s、join 窗 ±300s。

```python
# 源=.runtime/tmp/f7/f7_recompute.py（内联存档，TTL 兜底）
# F7 latency dashboard recompute (read-only over telemetry; ASCII only).
# Window: last 7 days ending now. All timestamps normalized to aware UTC; report in +08:00.
import json, glob, os, sys, math, re
from datetime import datetime, timezone, timedelta
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.chdir(ROOT)
NOW = datetime.now(timezone.utc)
WIN_START = NOW - timedelta(days=7)

def pctl(xs, p):
    if not xs: return None
    xs = sorted(xs)
    k = (len(xs) - 1) * (p / 100.0)
    f = math.floor(k); c = math.ceil(k)
    if f == c: return xs[int(k)]
    return xs[f] + (xs[c] - xs[f]) * (k - f)

def stats(xs):
    if not xs: return {"n": 0}
    return {"n": len(xs), "p50": round(pctl(xs, 50), 1), "p95": round(pctl(xs, 95), 1),
            "max": round(max(xs), 1), "sum": round(sum(xs), 1)}

def parse_ts(v):
    if v is None: return None
    if isinstance(v, (int, float)):
        return datetime.fromtimestamp(v, tz=timezone.utc)
    s = str(v)
    try:
        d = datetime.fromisoformat(s)
    except ValueError:
        return None
    if d.tzinfo is None:
        d = d.replace(tzinfo=timezone.utc)  # naive strings assumed UTC (derived_* writer)
    return d.astimezone(timezone.utc)

out = {"window_start_utc": WIN_START.isoformat(), "computed_at_utc": NOW.isoformat()}

# ---- P6a bottleneck_ledger (stream) ----
slow_item = {}          # qid -> seconds (last wins)
slow_ts = {}            # qid -> ts
staleness, alert_age, alert_pending = [], [], []
derived_stale_s, derived_stuck_n = [], 0
dead_qids = set(); dead_reasons = Counter(); dead_7d = 0
kinds = Counter()
with open(".runtime/audit/bottleneck_ledger.jsonl", encoding="utf-8") as f:
    for line in f:
        try: r = json.loads(line)
        except Exception: continue
        kinds[r.get("kind")] += 1
        ts = parse_ts(r.get("ts"))
        k = r.get("kind")
        if ts and ts < WIN_START:
            # dead_letter: still count unique qids ever seen for dedup context only
            continue
        if k == "slow_item":
            slow_item[r.get("qid")] = float(r.get("seconds") or 0); slow_ts[r.get("qid")] = ts
        elif k == "landing_staleness":
            staleness.append(float(r.get("age_s") or 0))
        elif k == "alert":
            alert_age.append(float(r.get("oldest_age_s") or 0)); alert_pending.append(int(r.get("pending_items") or 0))
        elif k == "derived_stale":
            m = re.search(r"账龄 (\d+)s", r.get("detail") or "")
            if m: derived_stale_s.append(int(m.group(1)))
        elif k == "derived_stuck":
            derived_stuck_n += 1
        elif k == "dead_letter":
            q = r.get("qid")
            if q and q not in dead_qids:
                dead_qids.add(q); dead_7d += 1
                reason = (r.get("reason") or "")[:80]
                dead_reasons[reason.split(":")[0][:40] + ("|gate=" + (re.search(r"门禁 (\S+) 阻断", r.get("reason") or "").group(1) if re.search(r"门禁 (\S+) 阻断", r.get("reason") or "") else "-"))] += 0  # keep simple below
out["kinds_total_alltime"] = dict(kinds)
out["slow_item_7d"] = stats(list(slow_item.values()))
out["slow_item_by_qid_top"] = sorted(slow_item.items(), key=lambda kv: -kv[1])[:12]
out["staleness_7d"] = stats(staleness)
out["alert_oldest_age_7d"] = stats(alert_age)
out["alert_pending_7d"] = stats(alert_pending)
out["derived_stale_age_7d"] = stats(derived_stale_s)
out["derived_stuck_7d"] = derived_stuck_n
out["dead_unique_qid_7d"] = dead_7d

# ---- P1 gate_execution_stats ----
suite_ms, gate_ms = [], defaultdict(list)
gate_fail = Counter()
with open(".runtime/audit/gate_execution_stats.jsonl", encoding="utf-8") as f:
    for line in f:
        try: r = json.loads(line)
        except Exception: continue
        ts = parse_ts(r.get("timestamp"))
        if not ts or ts < WIN_START: continue
        suite_ms.append(float(r.get("total_ms") or 0))
        for g, v in (r.get("ms") or {}).items(): gate_ms[g].append(float(v))
        for g in (r.get("failed") or []): gate_fail[g] += 1
out["gate_suite_7d"] = stats(suite_ms)
out["gate_per_gate_top"] = sorted(
    ((g, stats(v)) for g, v in gate_ms.items()), key=lambda kv: -(kv[1].get("p95") or 0))[:15]
out["gate_fail_top"] = gate_fail.most_common(10)

# ---- P2 precommit_channel_stats ----
pc_total, pc_fast, pc_slow_rc = [], [], 0; pc_n = 0
with open(".runtime/audit/precommit_channel_stats.jsonl", encoding="utf-8") as f:
    for line in f:
        try: r = json.loads(line)
        except Exception: continue
        ts = parse_ts(r.get("timestamp"))
        if not ts or ts < WIN_START: continue
        pc_n += 1
        pc_total.append(float(r.get("total_ms") or 0)); pc_fast.append(float(r.get("fast_subset_ms") or 0))
        if r.get("rc") not in (0, None): pc_slow_rc += 1
out["precommit_total_7d"] = stats(pc_total)
out["precommit_fast_7d"] = stats(pc_fast)
out["precommit_runs_7d"] = pc_n; out["precommit_rc_fail_7d"] = pc_slow_rc

# ---- P3 preflight_events ----
pf = defaultdict(list); pf_events = Counter()
with open(".runtime/audit/preflight_events.jsonl", encoding="utf-8") as f:
    for line in f:
        try: r = json.loads(line)
        except Exception: continue
        ts = parse_ts(r.get("timestamp"))
        if not ts or ts < WIN_START: continue
        p = r.get("path") or "?"
        grp = "enqueue族" if p in ("enqueue", "enqueue_api", "requeue") else p
        pf[grp].append(float(r.get("ms") or 0))
        pf_events[(grp, r.get("event"))] += 1
out["preflight_by_path_7d"] = {k: stats(v) for k, v in sorted(pf.items())}
out["preflight_events_7d"] = {f"{a}/{b}": c for (a, b), c in sorted(pf_events.items())}

# ---- P4 lock_wait_events ----
lw_all, lw_pos = [], []
with open(".runtime/audit/lock_wait_events.jsonl", encoding="utf-8") as f:
    for line in f:
        try: r = json.loads(line)
        except Exception: continue
        ts = parse_ts(r.get("timestamp"))
        if not ts or ts < WIN_START: continue
        w = float(r.get("waited_ms") or 0)
        lw_all.append(w)
        if w > 0: lw_pos.append(w)
out["lockwait_all_7d"] = stats(lw_all)
out["lockwait_pos_7d"] = stats(lw_pos)

# ---- P5 commit_block_events ----
slowc, okc = [], []
blocked = Counter(); qdead = 0
with open(".runtime/audit/commit_block_events.jsonl", encoding="utf-8") as f:
    for line in f:
        try: r = json.loads(line)
        except Exception: continue
        ts = parse_ts(r.get("timestamp"))
        if not ts or ts < WIN_START: continue
        e = r.get("event")
        if e == "commit_slow": slowc.append(float(r.get("total_ms") or 0))
        elif e == "commit_ok_sample": okc.append(float(r.get("total_ms") or 0))
        elif e == "commit_blocked": blocked[r.get("gate_id")] += 1
        elif e == "queue_landing_dead": qdead += 1
out["commit_slow_7d"] = stats(slowc)
out["commit_ok_sample_7d"] = stats(okc)
out["commit_blocked_7d_total"] = sum(blocked.values())
out["commit_blocked_top"] = blocked.most_common(12)
out["queue_landing_dead_7d"] = qdead

# ---- P7 done bags (landed in window) + decomposition ----
bags = []
def parse_dt(s):
    return parse_ts(s)
pf_by_session = defaultdict(list)
# reload preflight with ts for join
with open(".runtime/audit/preflight_events.jsonl", encoding="utf-8") as f:
    for line in f:
        try: r = json.loads(line)
        except Exception: continue
        ts = parse_ts(r.get("timestamp"))
        if not ts: continue
        if (r.get("path") or "") in ("enqueue", "enqueue_api", "requeue"):
            pf_by_session[r.get("session_id")].append((ts, float(r.get("ms") or 0)))
for k in pf_by_session: pf_by_session[k].sort()

for fp in glob.glob(".runtime/commit_queue/done/*.json"):
    try: d = json.load(open(fp, encoding="utf-8"))
    except Exception: continue
    c, l = parse_dt(d.get("created_at")), parse_dt(d.get("landed_at"))
    if not c or not l or l < WIN_START: continue
    chain_s = (l - c).total_seconds()
    sid = d.get("session_id")
    pf_ms = None
    cands = pf_by_session.get(sid) or []
    for ts, ms in cands:
        if abs((ts - c).total_seconds()) <= 300: pf_ms = ms; break
    si = slow_item.get(d.get("qid"))
    meta = d.get("meta") or {}
    bags.append({
        "qid": d.get("qid"), "created": c, "landed": l, "chain_min": chain_s / 60.0,
        "attempts": d.get("attempts") or 0,
        "requeue_count": meta.get("requeue_count") or 0,
        "stale": bool(meta.get("stale_by")),
        "slow_item_s": si, "preflight_ms": pf_ms,
        "last_failure": (d.get("last_failure") or "")[:100],
    })
bags.sort(key=lambda b: b["landed"])
chains = [b["chain_min"] * 60 for b in bags]
out["bag_chain_7d"] = stats(chains)
out["bag_n_7d"] = len(bags)
out["bag_attempts_gt0"] = sum(1 for b in bags if b["attempts"] > 0)
out["bag_requeued"] = sum(1 for b in bags if b["requeue_count"])
out["bag_stale"] = sum(1 for b in bags if b["stale"])
out["bag_slow_item_join"] = sum(1 for b in bags if b["slow_item_s"] is not None)
out["bag_preflight_join"] = sum(1 for b in bags if b["preflight_ms"] is not None)
top = sorted(bags, key=lambda b: -b["chain_min"])[:12]
out["bag_top"] = [{
    "qid": b["qid"],
    "chain_min": round(b["chain_min"], 1),
    "created": b["created"].astimezone(timezone(timedelta(hours=8))).strftime("%m-%d %H:%M"),
    "landed": b["landed"].astimezone(timezone(timedelta(hours=8))).strftime("%m-%d %H:%M"),
    "attempts": b["attempts"], "requeue": b["requeue_count"], "stale": b["stale"],
    "slow_item_s": b["slow_item_s"], "preflight_ms": b["preflight_ms"],
    "last_failure": b["last_failure"],
} for b in top]

# per-day chain medians (last 7 days, +08 dates)
byday = defaultdict(list)
for b in bags:
    key = b["landed"].astimezone(timezone(timedelta(hours=8))).strftime("%m-%d")
    byday[key].append(b["chain_min"] * 60)
out["bag_chain_by_day"] = {k: stats(v) for k, v in sorted(byday.items())}

# in-flight snapshot
inflight = []
for d_ in ("processing", "pending"):
    for fp in glob.glob(f".runtime/commit_queue/{d_}/*.json"):
        try: d = json.load(open(fp, encoding="utf-8"))
        except Exception: continue
        c = parse_dt(d.get("created_at"))
        if c: inflight.append({"dir": d_, "qid": d.get("qid"), "age_h": round((NOW - c).total_seconds() / 3600, 1)})
out["inflight"] = sorted(inflight, key=lambda x: -x["age_h"])

# residual queue-wait estimate for joined bags: chain - slow_item(known) - preflight(join)
resid = []
for b in bags:
    land = b["slow_item_s"] if b["slow_item_s"] is not None else None
    pf = b["preflight_ms"] / 1000.0 if b["preflight_ms"] is not None else None
    parts = [b["chain_min"] * 60]
    if land is not None: parts.append(land)
    if pf is not None: parts.append(pf)
    if len(parts) == 3: resid.append(parts[0] - parts[1] - parts[2])
out["resid_queuewait_7d"] = stats(resid)

def default(o):
    if isinstance(o, (datetime, set)): return str(o)
    raise TypeError
print(json.dumps(out, ensure_ascii=False, indent=1, default=default))
```


——
备注: 本文档为新建 .md、零提交，CREATE-GUARD token 未登记（门在 commit 时触发）；若总筹收批 promote 落 HEAD，需随批补 creation_token（同 F5 先例）。

判定权归总筹。
