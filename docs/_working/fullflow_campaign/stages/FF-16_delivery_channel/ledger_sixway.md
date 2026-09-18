---
ttl: task_bound
completes_when: FF-16 交付通道六向台账填满且外发通道双验证证据在案
---

# FF-16 交付通道 · 六向台账（车道 st-ff-alarm-20260918，2026-09-18）

> 规范真源 `../../FLOWTHROUGH_ACCEPTANCE_SPEC.md` §1。每格 = 实测数字或精确路径。
> **施工前复测（R-019）** 已执行，结果见 §2；普查记载与实测有出入者以实测为准（R-020）。

## 1. 六向台账

> **按 R-024/R-025 的显式声明（防把自报当签发）**：本台账是**车道自报**（每格带可重跑命令），
> **不**是 `flowthrough_verifier` 的机器签发结论——总包已裁该尺子"`--prove-red` 4/6 精确指名、
> 2/6 被聚合层吞掉且误导归因"，修复前所有"某环节已打通"的申报一律标 **未验收**。
> 本件⑤⑥向证据是**人工实测**（真桩 + 真落盘 + 5 变异），非尺子产出；尺子修好后须重跑并回填。

| 子模块 | ①入口有料 | ②转化能跑 | ③出口有货 | ④下游能取 | ⑤哨兵在岗 | ⑥失败会响 | 三态 |
|---|---|---|---|---|---|---|---|
| `zephyr.data.alert_webhook_dispatch`（机器侧外发） | `data/failures/*.json` 实测 **12965 件**，其中 `level=CRITICAL` **990 件** / `ERROR` 11975（命令见 §3-C1）；触发源二 kill_switch 探针实测 `state=normal`（§6.5 reaper 输出 `emergency_track_state=normal breaches=1`） | `PYTHONPATH=src python -m zephyr.data.alert_webhook_dispatch --health` → **rc=0**，输出 JSON 含 `status/detail/endpoints/auto_escalation`；`--scan-only` 走全目录扫描路径（CLI 面） | 三处出口均读回核实：①trail `data/runtime/alert_webhook_trail.jsonl` 实测 **3 行**（`kind=blocked`，§3-C4）②状态文件 `state.json`（测试内 `delivered_keys` 长度 1，读回断言）③通知板 `.runtime/ops_notifications/notifications.jsonl` 末行实测 `key=alert-webhook/channel-unavailable severity=critical title=告警外发通道不可用（fail-closed）` | **alerter 事件钩子**：`src/zephyr/data/alerter.py:182`（`_fanout_critical` 定义）+ `:168` 调用点（`_write_failure_file` 落盘成功分支）；alerter 的消费者=`zephyr.data.scheduler`（在册 [CONSUMERS]）→ 追到生产调度入口。另 CLI `main()` 为人工复推面 | 通道自身健康=可机读：`channel_health()` → `status ∈ {available, blocked, failing, unreadable}`；实测当前生产态 = **`blocked`**（`enabled=false`，因 Owner 凭据未给=BRK-055 门位）。投影面复用既有 `OpsAlertFeed`→`GET /api/ops-notifications`→promotion 页横幅（`src/zephyr/frontend/dashboard/api_server.py:4398`，零改动复用） | 5 个变异探针全部转红（§4），且**未 mock 被验防线自身**（poster=真 urllib、trail/state=真文件、板=真 OpsAlertFeed）；关接收端→`sent=0/failed=1` + trail `ok=false` + 通知板 critical；接收端返 500→同上；未送达不进去重表→下轮自动重试 | **黄-门位** |

**三态说明（禁把黄说成绿）**：①~⑥ 全部有实测证据，唯一缺口是**没有任何真实外部接收方**——
`config/alert_webhook.yaml` 的 `endpoints: []` 且 `enabled: false`，因为**推送凭据属 Owner 四类事**
（`BRK-055`，`COORDINATION_LEDGER.md` §7 已列门位）。按规范 §2 诚实条款，凭据门位项
判 **黄-门位**（登记即闭环，不计入未完成），**不判绿**——机器侧出口机制已通，
"最后一公里接到谁的手机上"不属本车道可自证范围。

## 2. R-019 施工前复测（逐条重跑普查原始命令）

| 普查条目 | 复跑命令 | 实测输出 | 三态判定 |
|---|---|---|---|
| BRK-052 告警不自动升级 | `python -c "import yaml,json;print(json.dumps(yaml.safe_load(open('config/flags.yaml',encoding='utf-8'))['flags']['alerts'],ensure_ascii=False))"` | `{"enabled": true, "description": "告警规则评估 (基础条件解析可用，Multi-Window 未实现)", "auto_escalation": false}` | **仍成立，但根因比记载更糟**：`auto_escalation` 全仓**零读者**（`grep -rn "auto_escalation" --include=*.py --include=*.yaml src scripts config tests` 只命中 `config/flags.yaml:60` 一处）。即"翻 true 零效果"，属 BRK-005/R-021 同型的**只写不读假通道**。本批已建唯一读者（`read_auto_escalation_flag`），详见 `escalation_flip_prereq.md` |
| BRK-053 遥测归档未实现 | 同上，键 `archive` | `{"enabled": false, ..., "implementation_status": "not_started"}` | **仍成立**（归属 z-failopen，本车道未动） |
| BRK-054 Schema 校验宽松+无死信 | 同上，键 `schema_validation` | `{"enabled": true, ..., "strict_mode": false, "dlq_enabled": false}` | **仍成立**（归属 z-failopen，本车道未动）。同 BRK-052 根因：嵌套子键不进 FlagRegistry，`load_flags_from_yaml` 只注册顶层 `enabled`（`src/zephyr/shared/foundation/flags.py:344-357` 实测） |
| BRK-055 告警推送凭据缺失 | `COORDINATION_LEDGER.md` §7 | 明列"需 Owner 提供凭据（E7 告警推送 webhook 四类凭据）" | **仍成立=Owner 门位**。本车道按 R-K4 只做机制，**未自行找/写任何凭据** |
| 骨架对 FF-16 的隐含前提"webhook 已不存在" | `grep -rn "maybe_dispatch_alerts\|alert_webhook_dispatch" --include=*.py src tests scripts` | 接管前实测 **0 命中**（模块自身除外）——即该模块 untracked、零消费方、零测试 | **归属错/新形态**：不是"缺模块"，是"**有模块但没人读、没测试、且 [CONSUMERS] 头自称挂在 `pipeline_events`，实测该文件从未 import 它**"。已按 R-021 上报（`adjudications/req_alarm_01.md`） |

## 3. 复现命令（Max 可直接跑）

- **C1 触发源体量**：`python -c "import json,glob,collections;c=collections.Counter();[c.update([json.load(open(f,encoding='utf-8')).get('level')]) for f in glob.glob('data/failures/*.json')];print(dict(c))"` → `{'ERROR': 11975, 'CRITICAL': 990}`
- **C2 双验证（桩真收到 + 文件真落盘）**：`python -m pytest tests/data/test_alert_webhook_dispatch.py -q -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning" --basetemp=.runtime/tmp/ff-alarm-pc` → **17 passed**；关键钉 `test_dual_verification_stub_received_and_files_landed`（断言 127.0.0.1 桩 `received` 长度=1 且 payload 含 `schema/alerts[0].task_id/level=CRITICAL`，并读回 trail+state 文件）
- **C3 auto_escalation 零读者**：`grep -rn "auto_escalation" --include=*.py src scripts config | head`
- **C4 生产 trail 行数**：`wc -l data/runtime/alert_webhook_trail.jsonl` → 3（来源见 §5 注）
- **C5 通道健康（fail-closed 可观测）**：`PYTHONPATH=src python -m zephyr.data.alert_webhook_dispatch --health`
- **C6 通知板投影**：`tail -1 .runtime/ops_notifications/notifications.jsonl` → 含 `alert-webhook/channel-unavailable`

## 4. 能红证据（5 个变异，全部按字节还原 `identical=True`）

| 变异 | 改法 | 结果 |
|---|---|---|
| M1 退回共享指纹去重 | `_delivered_key(ep.name,` → `_delivered_key("ALL",` | **2 failed** |
| M2 blocked 不留痕（改键名使读不到） | `"kind": "blocked"` → `"kind": "blocked_moved"` | **1 failed** |
| M3 失败也消费去重指纹 | `if newly:` → `if True:` | **3 failed** |
| M5 成功不落去重状态 | `newly.extend(keys[i] for i in fresh_idx)` → `pass` | **4 failed** |
| M6 断开 alerter 事件钩子 | `self._fanout_critical(record, filepath.name)` → `pass` | **1 failed** |

回归：`tests/zephyr/data/test_alerter.py` → **17 passed**（钩子插入未破坏告警器既有契约）。

## 5. 如实记录（未达成/存疑）

1. **trail 生产 3 行的来源未归因清楚**（亲验：我的 17 件测试跑完后该文件行数 3→3 不变，故非测试所写；
   19:30:56-57 三次 `blocked` 与 `git_commit.py --enqueue` 预检同窗，疑为预检子进程 import 后的一次
   真实 CRITICAL 告警外发）。属**推断**，Max 可用 `C4` + `git reflog`/预检日志对时。
2. 本车道**未改** `config/flags.yaml`（Owner 门位 R-022③）、未改 `resilience_governance/**`（z-wire-safety 独占）、
   未改 `risk/**`（z-land2 独占）；`pipeline_events.py` 上他会话未提交 WIP 未代修（宪法 §3.4）。
3. `alerter.py` 本批提交**连带吸收**了他车道（z-failopen）已 staged 的 7 行 BRK-049 兜底日志改动
   ——非本车道产物，按 §2.5 如实登记。
