---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-WIRING-COHORT-T4
completes_when: Owner 逐项批点后按批施工（本稿只出申请单不代批）
---

# wiring_proposals cohort_daily_ledger 写入器 + plan_deviation_monitor T4 对接（双设计，C 类申请单）

## A. cohort_daily_ledger 写入器

### 现状实证（文件:行号）

- `src/zephyr/alt_data/cohort_daily_ledger.py:392` `build_cohort_daily(day)` 纯计算零写库；
  头注 :9 INVARIANTS"只读 CH（禁写任何生产表，一期 CH insert 归总统筹批）"、:38-40 同义重申。
- DDL 真源已两处就位：`schemas/categories/cohort_daily_ledger.py:51-68`（ReplacingMergeTree
  同键幂等）、INSERT_COLUMNS :83；且已注册 `scripts/ch/apply_market_tables_ddl.py:583`
  （裁定#392 之 D5 批代落；:576-580 注：真跑前须 c1_backtest 库已存在）。
- 四原料任务已在 daily_capital 18:00 档（`schedule.yaml:80`；deps 清单=`cohort_daily_ledger.py:5`
  [money_flow/margin_trading/dragon_tiger/block_trade]_incremental）。
- `tasks.yaml` grep cohort=**0 行**——写入器任务行不存在，每日算完即弃。

### 设计

写入器最小设计（新薄件，建议 `src/zephyr/alt_data/cohort_daily_writer.py`，
不动 cohort_daily_ledger.py 一行）：

```python
def write_day(day: str) -> int:
    rows = build_cohort_daily(day)                 # 产出行键=INSERT_COLUMNS 契约(:14)
    client = ch_writer.get_client_strict()         # strict 通道（ch_writer.py:217，fail-visible）
    return client.insert(table=QUALIFIED_NAME, columns=INSERT_COLUMNS,  # :80 派生名禁硬编码(:12)
        data=[(r["trade_date"], r["cohort_id"], r["metric_id"],
               decimal.Decimal(str(round(r["metric_value"], 4))),  # float→Decimal(18,4)
               r["state"], r["proxy_source"], r["bias_note"],
               json.dumps(r["detail"], ensure_ascii=False)) for r in rows])
```

- **业务日幂等口径**：不查重不先删——ReplacingMergeTree 同键重跑覆盖（schemas :9-11
  "重跑/回填安全，禁手工 UPDATE"），读侧 FINAL/argMax 收敛。
- **tasks.yaml 任务行草案**（Owner 门：tasks.yaml 禁碰）：

```yaml
cohort_ledger_daily:
  schedule: daily_capital        # 或新开 18:30 槽（四原料 18:00 批之后）
  source: internal
  handler: zephyr.alt_data.cohort_daily_writer.write_day
  params: { day: latest_trading_day }
  deps: [money_flow_incremental, margin_trading_incremental,   # 照抄 :5 CONSUMERS 自述
         dragon_tiger_incremental, block_trade_incremental]
```

- **二期消费方 next_day_forecaster 特征集接法**：读长表 pivot 为 cohort×metric 宽特征；
  PIT 硬口径 `trade_date <= T`；`proxy_source='missing'` 行特征位标缺不插补；表名经
  QUALIFIED_NAME 派生（:12 禁硬编码）。本二期只登记不施工。

### Owner 批点清单（A 段）

1. **tasks.yaml 写入权**（禁碰件）+ 档期选择：挂 daily_capital 尾部 vs 新开 18:30 槽。
2. **写库面解锁**："CH insert 归总统筹批"挂账由本单核销（净零替代声明：写入器落地
   =替代该挂账项，cohort_daily_ledger.py 自身 INVARIANTS 零改动不破）。
3. **Decimal 舍入口径**：四舍五入 round(x,4) vs 截断，金额万元 Decimal(18,4)（裁定 S4）。
4. **二期特征集消费**立项与否（只登记不施工为默认）。

### 不批的后果（A 段）

- 五人群账本永久停在一期纯计算件：CLI 可抽查、daily 数据永不落库，四原料 18:00
  采集成本持续支出而聚合结果每日丢弃；老蔡对账（:6）无表可比，一期验收 §4 无法闭环；
  next_day_forecaster 特征集缺原料，二期持续挂账。

## B. plan_deviation_monitor T4 对接

### 现状实证（文件:行号）

- 蓝图 `docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md:36`：
  T4 盘后挂点 `postmarket_reconcile(data_date)`——"当日决策 vs 实际的核对留痕
  （对接既有 plan_deviation_monitor 口径）……首版仅签名与占位"。
- 编排器侧同款占位：`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:765-769`
  `postmarket_reconcile` 返回 `{"action":"reserved_v1",...}`。
- 对接件 `src/zephyr/plan_engine/plan_deviation_monitor.py`：:112-117 `_require_decimal`
  Decimal-only 拒 float 隐转/非有限值（:8 INVARIANTS 同义）；:12/:15 `AI_AUTONOMY=human_gated`；
  :130 `record_sink` 注入（:157-161 sink 异常不阻断）；:5 CONSUMERS"留痕落 state_store"。
- 留痕落点现状：`schemas/categories/decision_daily.py:35`"prediction_log 双写暂不做=
  后续项留登记"——prediction_log 表**尚不存在**。

### 设计

**Decimal 适配器**（CH/kline float → Decimal 安全转换，str 中转规避二进制浮点误差；
收益率小数 0.0123、金额万元 Decimal(18,4) 与 cohort 侧同单位）：

```python
def to_decimal(value: float | str | None, *, name: str) -> Decimal:
    if value is None:
        raise PlanDeviationError(f"{name} 缺值（T4 缺实际侧=降级留痕，不编 0）")
    return _require_decimal(name, Decimal(str(value)))  # str 中转防 0.1+0.2 形误差；:112 类型+is_finite
```

**record_sink 落点二选一（建议①）**：
① **state_store**（模块 :5 自述落点）：key=`plan_deviation/{data_date}`，JSON 留痕，零新表零新
   schema，净零；短板=非 SQL 截面可查。② **prediction_log 新 CH 表**：决策 vs 实际逐日截面
   可回测，但须新建 schema+DDL+apply 注册三个新真源件——建议留二期（:35 登记位已在）。

**为何现在不能自动挂**：plan_deviation_monitor.py:12 `AI_AUTONOMY=human_gated`——宪法 §5 门位
（human_gated 件的接线消费方式=Owner 门位）+ §9.11 指令/数据边界（AI 不得代行 Owner 门位）；
蓝图 :36 自身写明"只定义接口，不展开"。AI 侧自动接线=越权，故本段只能出申请单。

### Owner 批点清单（B 段）

1. **T4 对接立项批准**（human_gated 件解冻：经正式通道授权后由施工批装配消费方）。
2. **record_sink 落点二选一**（建议① state_store 首版，② prediction_log 留二期登记）。
3. **"实际收益"口径**：kline close-to-close vs 成交回放；σ 来源与历史窗口长度。
4. **评估频率**：监控件本体=盘中实时语义（:20-27），T4 借它做日终核对是口径复用——日终一次
   即可，确认不启用盘中循环（避免常驻监控进程违反 §9.3 事件触发约束）。

### 不批的后果（B 段）

- T4 永远停在 reserved_v1 占位：决策拍完没人对答案，质量核对无闭环，蓝图 §八
  Owner 批准点清单持续挂账；逐层归因链缺盘后段，D2/D3 降级是否"该降"无事后证据。
- plan_deviation_monitor 生产件（:7 MATURITY=production）继续零消费方，建设成本沉没。
