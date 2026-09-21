---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-WIRING-RECON-CHANNEL
completes_when: Owner 择挂法+批 broker/run_id 语义后施工（本稿只出申请单不代批）
---

# wiring_proposals recon_runner 15:40 假通道补挂设计（C 类申请单）

## 一、现状实证（文件:行号）

- `src/zephyr/data/config/schedule.yaml:200-204`：`eod_reconciliation` 槽存在
  （cron `40 15 * * 0-4`，描述明写"recon_runner.run_daily_reconciliation 三账核对"）。
- `src/zephyr/data/config/tasks.yaml`（全 3746 行）：grep `recon` = **0 行任务**——
  槽位无任务可滤 → `src/zephyr/data/scheduler.py:2154-2156`
  `schedule_tasks` 为空即 `log.warning("时段 %s 无任务")` + `return {}`：静默空转、
  以"成功"形态返回。**该通道从未自动跑过，= R-021 假通道形态**
  （schedule.yaml:214-216 对 R-021 的自证注释恰在本文件内）。
- 唯一入口 `src/zephyr/trading/recon_runner.py:392-398`：
  `run_daily_reconciliation(trade_date, run_id, broker, ...)` 三参必填——
  `run_id`=当日同信号回测跑批 artifact（:406 `data/backtest_artifacts/{run_id}.json`）；
  `broker`=实盘侧数据源，生产=已 connect 的 `MiniQmtBroker`（:407，
  构造先例 `recon_runner.py:30-33`，凭据走 `config/.env.qmt`）。
- 挂法先例：`src/zephyr/data/scheduler.py:272`（nightly_sentiment）、:341（consensus_crosscheck）
  均为 `_run_special_schedule` 内 if 分支 internal handler（白名单硬编码，schedule.yaml:214 自认
  "scheduler.py 非本车道可写面"）。
- QMT 降级先例：`scripts/run_post_settlement.py:8` INVARIANTS 原文——"QMT 不在线降级为
  仅系统侧+显式标注（不伪造'券商侧为空'的假比对）"；:38-40 展开原因（空券商侧硬对会把
  系统侧全部成交误判 MISSING_IN_BROKER 假 DRIFT）。

## 二、设计（两条挂法，择一）

### 挂法 A：tasks.yaml internal 任务行草案（声明式，需 scheduler 先支持 internal handler 路由）

```yaml
eod_reconciliation_runner:
  schedule: eod_reconciliation
  source: internal          # 非 Provider 采集任务
  handler: zephyr.trading.recon_runner_entry.run_scheduled   # 需新增薄入口件
  params: { trade_date: latest_trading_day }
```

前置成本：现行 `run_task` 面向 Provider 采集+CH 写入，无 `source: internal` 自定义
handler 路由——须先给 scheduler 增加 internal handler 路由机制（改 scheduler.py），
**一次性机制改动换后续所有 internal 件声明式挂载**。

### 挂法 B：scheduler.py `_run_special_schedule` 加白名单分支（先例同款，推荐）

与 :272/:341 完全同构，分支草案：

```python
if schedule_name == "eod_reconciliation":
    from zephyr.trading.recon_runner import run_daily_reconciliation
    from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker
    _flag = Path(__file__).resolve().parents[3] / "data" / "runtime" / "eod_reconciliation.disabled"
    if _flag.exists():  # 服务总闸惯例（nightly_sentiment :275 同款）
        return {"eod_reconciliation": False}
    try:
        broker = MiniQmtBroker.from_env_qmt(); broker.connect()
    except Exception:
        broker = None
    run_id = _resolve_latest_run_id(today)   # data/backtest_artifacts 当日最新，无→None
    if broker is None or run_id is None:
        scheduler._alerter.notify("eod_reconciliation",
            "QMT 不在线或当日回测 run_id 缺席——日终对账整步 SKIPPED（显式降级，不伪造比对）",
            level="WARN", source="eod_reconciliation")
        return {"eod_reconciliation": False}
    result = run_daily_reconciliation(today, run_id, broker)
    if result.c_anomalies:  # C 类清单当日告警（56号文 §5）
        scheduler._alerter.notify(..., level="ERROR", source="eod_reconciliation")
    return {"eod_reconciliation": True}
```

### QMT 不在线降级语义（抄 run_post_settlement.py:8 先例）

券商侧不可得 ⇒ 整步 SKIPPED + 告警出声 + 状态留痕，**绝不拿空券商侧硬对**；
run_id 缺席同语义（缺回测侧=同假对风险）。两降级源分开设名，fetch_perf 留痕可区分。

## 三、Owner 批点清单（逐项）

1. **挂法二选一**：A=tasks.yaml 任务行（tasks.yaml 禁碰=Owner 门）但须先给 scheduler 建
   internal handler 路由机制；B=scheduler.py 白名单加分支（scheduler.py 核心写面，
   :272/:341 先例充分）。**建议 B**，A 作为机制成熟后的迁移项。
2. **broker 语义**：MiniQmtBroker 谁构造/connect/close（建议 handler 内短连用完即关，
   不复用常驻）；凭据通道确认为 `config/.env.qmt`（RULE-SECRETS 三道 gate 覆盖核查）。
3. **run_id 解析口径**：`data/backtest_artifacts` 当日最新自动选（有跑批竞争日的歧义）
   vs 上游回测任务显式回执传参（准但要改上游）；建议首版自动选+source_run_id 留痕。
4. **时序确认**：15:40 槽先于 L4 daily_kline 16:30（schedule.yaml:194-196 排班理由），
   但回测 artifact 产出时点须早于 15:40 才有 run_id 可读——须 Owner 确认当日回测跑批
   完成时点，否则降级日高频化。
5. **写面追认**：recon_runner 差异落库 governance.db（:383-388 sqlite 直写差异表）+
   C 类告警通道名——调度化后写入频率从手动变每日，属既有函数行为，报备追认即可。

## 四、不批的后果

- eod_reconciliation 槽继续每个交易日 15:40 静默空转并以成功形态返回，
  "三账核对"（柜台/内部/持仓）永远没跑过——R-021 假通道清单继续挂账。
- 56 号文 §5 步骤③④日终对账长期依赖手动触发，漏跑无人知（正是本次挖矿才发现的形态）。
- 滑点/部分成交/拒单缺失（C 类）差异无人当日捕获，对账差异跨日累积，
  事后归因失真——闷声出事典型位。
