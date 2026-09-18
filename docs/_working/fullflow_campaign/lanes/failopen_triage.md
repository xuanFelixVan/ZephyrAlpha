---
ttl: task_bound
completes_when: 全流通战役收官且最终交付报告落盘
---

# failopen 车道 · BRK-049 吞异常分级 + BRK-047/048 fail-open 分档

> 车道 `st-ff-failopen-20260918`（总包 `st-fullflow-20260918`）。分级器
> `.runtime/tmp/ff-failopen/triage.py`（AST 口径），派生册
> `docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml`。

## 1. 口径先对齐（勿拿两个数当同一个东西）

| 口径 | 值 | 说明 |
|---|---|---|
| 普查 grep 复现（`except Exception` 次行 `pass`） | **145** | 普查记 144；本轮 +1（战役在途新代码），非口径分歧 |
| 普查 grep 复现（裸 `except Exception:`） | **67** | 普查记 62 → 同为在途增长 |
| **AST 严口径**（handler 唯一语句是 `pass` 且属 Exception 族，扫 `src/zephyr`+`scripts`） | **261** | 真分档基数。grep 只看次行，漏掉 `except` 与 `pass` 之间夹注释/跨行的情形 |

**结论**：144/145 是"次行偏移"口径，不是完备集。按风险施工必须用 AST 口径（261），
否则"改完 144 处"仍会漏同型缺陷——这本身就是一个新的假象来源。

## 2. 三轴分档（261 处，AST 口径）

轴 = ①所在环节（顶层包→FF-*）②是否在钱/决策路径（包白名单 + 函数/文件名关键词）
③吞掉后有无任何痕迹（handler 前后窗口是否出现 log/audit/metric/alert/raise）。

| 档 | 判据 | 件数 | 本轮处置与理由 |
|---|---|---|---|
| **T1** 钱/决策路径 + 零痕迹 | money ∧ ¬trace | **62** | **只改其中"告警/熔断/成员集自身被吞"的 7 处**（§3）；余 55 处登记处方 |
| T2 钱/决策路径 + 有痕 | money ∧ trace | 10 | 不动：已有痕迹，属可观测降级 |
| T3 非钱路径 + 零痕迹 | ¬money ∧ ¬trace | 168 | **本轮不动**，交 Max 波次。判据：吞错不改变资金/决策语义；批量改 168 处零收益、纯回归风险，且每处都欠一条能红测试钉 |
| T4 非钱路径 + 有痕 | ¬money ∧ trace | 21 | 不动 |
| 合计 | | **261** | |

T1 按包分布：`data` 33 / `governance` 20 / `gov_enforcement` 3 / `pf_core` 2 /
`pf_alloc` 1（**禁写他人独占，只登记**：`src/zephyr/pf_alloc/core/sector_distribution_comparator.py:77`）/
`scripts/git_commit.py` 1 / `scripts/governance/generate_project_depgraph.py` 1 / `d3_metadata` 1。
T3 按包分布：`scripts` 91 / `gov_enforcement` 33 / `frontend` 22 / 其余 22。

## 3. 本轮实改 7 处（改前 → 改后）

| # | file:line | 改前 | 改后（真处置 / 显式降级留痕） |
|---|---|---|---|
| 1 | `src/zephyr/data/scheduler.py:746-762` CH 健康探活 CRITICAL 告警 | 先无条件 `_ch_probe_alerted_dead = True`，再 `try: notify except: pass` | `= self._deliver_alert_with_latch(...)`：**真落盘才置闩**，未落盘保留未告警态并在下一轮探活重试 |
| 2 | `src/zephyr/data/scheduler.py:732-744` 恢复（DEAD→ALIVE）通知 | 先无条件清闩再 try/notify/pass | `if self._deliver_alert_with_latch(...)` 成立才清闩 |
| 3 | `src/zephyr/data/scheduler.py:1376-1388` `_warn_if_table_missing` DDL 缺失告警 | **告警之前**就写 4h 去重戳，异常与 False 全 pass → 未落地也被去重静默 | 投递成功才记去重戳；未落地不记、下轮任务重试 |
| 4 | `src/zephyr/data/source_circuit_breaker.py:151-153` 熔断跳闸升级回调 | `except Exception: pass`（零痕迹） | 状态机**不回滚**（OPEN 保持、`allow_request` 仍 False = 不放松），新增 `trip_callback_failures` + `last_trip_callback_error`（真实类型串）+ ERROR 日志带 `exc_info` |
| 5 | `src/zephyr/data/alerter.py:165-167` 告警落盘兜底 | `log.error("写失败汇总文件异常: %s", e)`（无类型名、丢栈） | `type(e).__name__: e` 进正文 + `exc_info=True`，**不预设失败类别** |
| 6 | `src/zephyr/pf_core/strategy_engine/framework_composer.py:1689,1699` 策略自动发现 | `except Exception: pass` ×2 → 成员集不完整静默，而成员集决定 `reconcile_composed_nav` 的日频/tick 判定 | 保留降级不抛，`logger.warning` 带真实类型名 + `exc_info`，消息显式声明"成员集可能不完整" |
| 7 | `src/zephyr/gov_enforcement/commit_gates/reconciler_health_gate.py:110,115` 告警去重状态 | 两处 `except Exception: pass` 零痕迹 | 首处窄化为 `FileNotFoundError`（真·正常路径，不产噪音），其余降级留 `logger.warning` + 类型名 + `exc_info` |

1/2/3 共用新增 helper `IntegratorScheduler._deliver_alert_with_latch`（`src/zephyr/data/scheduler.py:686` 前）。

### 关键发现：#1 是 R-K6「假处置」教科书案例（比无处置更危险）

`Alerter.notify` **自己不抛异常，而以返回值表态**（`-> bool`；写盘失败/冷却期返回 False）。
原实现既 `except: pass` 又**丢弃返回值**、还**先置闩**，三重叠加：
CH 真断供 → 探活正确判 DEAD → CRITICAL 告警从未落盘 → `_ch_probe_alerted_dead=True`
**永久压制重试** → 本进程余生不再尝试通知任何人。哨兵自身静默失明。
第 3 处同一病灶（去重戳写在告警之前）。

### 能红证据（不 mock 防线自身）

`tests/zephyr/data/test_failopen_brk049.py`（11 条，真对象 + `tmp_path` 作 root）：
- 告警闩用**真 `Alerter`**，故障由"failures 目录父段是一个普通文件"制造真 `NotADirectoryError`；
- 熔断用**真 `SourceCircuitBreaker`**，回调是真会 `1/0` 的函数；
- 去重状态用**真 `_should_print_warn`**，故障是真损坏的 JSON / 真不可写的 `.runtime`；
- 哨兵用**真 `check_tables()`**。
变异实测：把 5 个源文件按字节还原为改前 → **8 红 / 3 过**；把哨兵 YAML 还原为改前 →
sentinel 组 **2 红 / 1 过**。重放补丁器后 11 条复过。
回归：`test_alerter.py` + `test_source_circuit_breaker.py` + `test_data_scheduler.py` +
`tests/governance/commit_gates/test_reconciler_health_gate.py` 共 **92 条通过，无因加严转红件**
（即本轮没有测试在依赖被吞的旧行为——这与"改 fail-closed 必致红"的常见担心相反，如实记录）。

## 4. fail-open 登记册（BRK-047）

- 生成器 `scripts/governance/d7_code/generate_fail_open_register.py`；
  派生册 `docs/01_policies_and_standards/_registry/catalogs/fail_open_register.yaml`。
- 实测 **`total_fail_open: 1595`** / 265 文件（口径=扫 `src/zephyr`+`scripts`，含 `fail-open`
  连字符与注释形态；普查 1405 = 仅 `src/zephyr` 的同一正则口径，本轮已复现 1405 对齐）。
- 分档：`hardcoded_default_permit` **5** / `money_path_no_trace` **176** /
  `designed_degradation_with_trace` **735** / `undeclared_needs_review` **679**。
- 按环节：FF-14 1027 / GLOBAL 222 / FF-07 107 / FF-01 65 / FF-16 41 / FF-06 35 / FF-15 33 /
  FF-11 25 / FF-02 22 / FF-04 10 / FF-09 4 / FF-05 2 / FF-10 2。
  —— **64% 的 fail-open 面在治理层（FF-14），不在赚钱链路**；这是"1405/1595 处不得无差别改造"
  的机械证据（原判断的第一性理由得到数据支持）。
- `--check` 模式供门禁调：派生册 `content_sha256` 与现扫不符即退出码 1（宪法 §9.5 生成器真源）。

## 5. BRK-048 五处逐处判定

实测：**5 处 grep 命中 = 1 个定义 + 4 个使用点，全在同一个构造上**
（`src/zephyr/security/llm_defense/llm_security/gateway.py`，LSG 网关）：

| file:line | 内容 | 判定 |
|---|---|---|
| `:123` | `FAIL_OPEN_LAYERS = {"l6_observability", "l7_validation"}` | **设计意图，保留**：七层防御仅"可观测性/输出校验"两层允许失效放行；L1-L5（注入检测、权限、脱敏、审计…）不在集合内 → 那五层 fail-**closed** |
| `:307`/`:343`/`:364` | `if name in self.FAIL_OPEN_LAYERS:` | 同一构造的消费点 |
| `:327` | `_classify_layer_decision(name, result, self.FAIL_OPEN_LAYERS)` | 同上，且降级走 decision 记录=有痕 |

→ **本轮不改**，但普查把"1 个构造"报成"5 个独立放行点"属**归因放大**（R-013 同型），
已在登记册里点名进 `hardcoded_default_permit` 档 → 今后任何新增默认放行都会被
`--check` 与派生册 diff 抓出。不改的反向理由：把 L6/L7 改 fail-closed 会让
"观测链路故障"阻断整个 LLM 网关 = 加严名义下的反向误伤。

## 6. BRK-046 哨兵白名单收口（实跑前后）

| 阶段 | checked | breached |
|---|---|---|
| 收口前（12 张 `allow_empty`） | 35 | **0** |
| 收口后（11 张撤豁免 / 1 张保留并登记理由） | 35 | **0** |

**breach 未上升，这本身就是结论**：逐张实测行数与日期纵深后，12 张被豁免的表**当日全部有数**
（`hl_funding_history` 4,655,619 行 / `cftc_positioning` 81,270 行 / `gold_etf_holdings` 2,871 行 /
`sector_fund_flow` 1,467 行 / …，max(date) 均在阈值内）→ 这些"新建表首轮回填前宽限"
**早已过期却无人撤**，是纯死重量；而它们唯一会起作用的那天（表真变空）恰是最需要响的那天。

- 保留豁免 1 张：`c1_market.market_convertible_bond_clause`（条款类=事件驱动稀疏供数），
  同行强制登记 `rationale_zh` + `reviewed_at` + `reviewed_by`；
  结构性测试钉 `test_sentinel_allow_empty_requires_written_rationale` 拦无凭据豁免、
  并把豁免数上限钉成 1（白名单不得再膨胀）。
- 与 BRK-029 对照：`sector_fund_flow` 普查时"从未灌入一行"，现 1,467 行 / 4 个快照日
  （09-15..18）→ 已被在途车道补线，故撤豁免安全；"从未有数"这类病今后会被哨兵抓到。
- 阈值一律未放宽（撤豁免 ≠ 撤检测 ≠ 放宽 `max_lag_days`），
  由 `test_sentinel_real_tables_no_longer_whitelisted` 钉住。
- **新点亮盲点的真伪核实不靠今日数字**，靠 `test_sentinel_empty_table_alarms_without_whitelist`
  （真 `check_tables()` + 不存在的表 → `breached == 1`）。
- 移交 z-datagap：`c1_market.hl_liquidation_raw` 全表仅 **1 行**、`ingest_ts` 单一值，
  高频清算流近乎未上线 = "任务在册、链路假通"；采集实现属他人独占文件，本车道只登记处方。
