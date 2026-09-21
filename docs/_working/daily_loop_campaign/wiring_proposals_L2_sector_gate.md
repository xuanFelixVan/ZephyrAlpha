---
ttl: task_bound
session: st-dloop-20260921
issue: DLOOP-V2-WIRING-L2-SECTOR-GATE
completes_when: Owner 逐项批点后按批定档位施工（本稿只出申请单不代批）
---

# wiring_proposals L2 板块门日态产出方设计（C 类申请单）

## 一、现状实证（文件:行号）

- `src/zephyr/strategy_pipeline/daily_gate_snapshot.py:156-162`：`_collect_l2()` 是硬编码 stub，
  恒返回 `{"status":"absent","layer":"L2","error":"no_persisted_gate_state_v1"}`——模块头 :15
  自证"L2 板块门无持久化日度状态=v1 如实标 absent，不伪造门态"。
- `src/zephyr/strategy_pipeline/daily_decision_orchestrator.py:565`：编排器消费该 absent，
  `ctx.degrade.append("D2_gate_absent:"+...)`——今晨拍板行 degraded=1(D2_gate_absent:L2) 的根因即此 stub。
- `src/zephyr/signal_ashare/sector/sector_gate.py`（纯函数件，零副作用）：
  `admission_gate` :117-150 需调用方喂 `top_sectors/retained_sectors/score` 三原料；
  `water_temp_response` :91-114 是水温五档响应面（查表 `_WATER_TEMP_TABLE` :82-88）；
  头注 :23-26"水温归 regime 10 号/情绪周期 28 号，本模块不判水温"；:29"阈值 v2.1 初拟待 G05 回测验证"。
- 水温上游已在仓：`src/zephyr/signal_ashare/core/daily_condition_sensor.py:45` `WaterTempTier`
  S0-S4 五档（:198-208 `_tier_of` 净分单调映射），:32 自述"本模块输出可映射为 sector_gate.WaterTemp 入参"。
- regime 侧：蓝图为 `docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md:27`，
  `c1_backtest.regime_snapshot_history` 含 `dominant`（六段），采集器 :59-63 已复用
  `SQL_LATEST_REGIME_SNAPSHOT`（L1 步已读，桥接零新读）。

## 二、设计（两档方案）

### 方案甲（最小档）：water_temp 桥接 stub 替换，零新表零写入

`_collect_l2()` 不再恒 absent：复用 L1 已取的 regime 快照 `dominant` → 查映射表 →
调 `water_temp_response()` → 返回响应面载荷。**不激活** `admission_gate`（三原料无着落，
如实标 `gate_level:"not_evaluated"`）。仍是只读采集面，门模块 sector_gate 零改动。

映射表草案（regime 六段 dominant → WaterTemp，待批）：

| dominant | WaterTemp | 依据 |
|---|---|---|
| capitulation | CRASH | 全拦截保守侧 |
| accumulation | RISK_OFF | 仅领先象限+阈值收紧 |
| ignition | PANIC_REPAIR | 仅改善象限+阈值放宽（修复段） |
| expansion | NEUTRAL | 全权重 |
| euphoria | RISK_ON | ×0.5，叠加情绪 S4=CONSENSUS_CLIMAX 时双重抑制 |
| distribution | RISK_OFF | 派发段保守侧 |

备选桥：daily_condition_sensor 五档直映 S0→CRASH / S1→RISK_OFF / S2→NEUTRAL / S3→RISK_ON /
S4→RISK_ON(+climax)。**缺口如实报**：PANIC_REPAIR 在 S 档无直接对应格，两桥只能择一，须裁。

代码草案（daily_gate_snapshot.py :156-162 替换体）：

```python
_DOMINANT_TO_TEMP = {"capitulation": "CRASH", "accumulation": "RISK_OFF",
                     "ignition": "PANIC_REPAIR", "expansion": "NEUTRAL",
                     "euphoria": "RISK_ON", "distribution": "RISK_OFF"}

def _collect_l2(dominant: str | None, consensus_climax: bool = False) -> dict[str, Any]:
    if not dominant or dominant not in _DOMINANT_TO_TEMP:
        return {"status": "absent", "layer": "L2", "error": "no_persisted_gate_state_v1"}
    from zephyr.signal_ashare.sector.sector_gate import water_temp_response
    resp = water_temp_response(_DOMINANT_TO_TEMP[dominant], consensus_climax=consensus_climax)
    return {"status": "ok", "layer": "L2", "mode": "response_face_v1",
            "water_temp": _DOMINANT_TO_TEMP[dominant],
            "signal_weight": resp.signal_weight, "rrg_filter": resp.rrg_filter,
            "gate_thresholds": [resp.gate_thresholds.level2, resp.gate_thresholds.level3],
            "gate_level": "not_evaluated"}  # admission_gate 三原料缺，未评
```

### 方案乙（完整档）：盘后 L2 日态产出者 + 新表 + 采集器改读表

新盘后任务产出 top_sectors/retained_sectors/score 原料与当日生效阈值，落新表；采集器
`_collect_l2` 改为读表（有当日行→status=ok+gate_level 明细；无→沿用 absent 降级）。DDL 草案：

```sql
CREATE TABLE IF NOT EXISTS c1_backtest.sector_gate_state_daily
(
    trade_date        Date                    COMMENT '业务交易日',
    water_temp        LowCardinality(String)  COMMENT 'NEUTRAL|RISK_ON|PANIC_REPAIR|RISK_OFF|CRASH',
    top_sectors       Array(String)           COMMENT '当日 Top 热门板块集（级别1直通）',
    retained_sectors  Array(String)           COMMENT '保留板块集（次优归属判定）',
    threshold_level2  Float64                 COMMENT '水温联动后二级阈值（v2.1 基 0.60）',
    threshold_level3  Float64                 COMMENT '水温联动后三级阈值（v2.1 基 0.80）',
    signal_weight     Float64                 COMMENT '水温响应权重',
    rrg_filter        LowCardinality(String)  COMMENT 'ALL|IMPROVING_ONLY|LEADING_ONLY|NONE',
    consensus_climax  UInt8 DEFAULT 0         COMMENT 'RISK_ON 叠加 CONSENSUS_CLIMAX 双重抑制',
    source_run_id     String                  COMMENT '产出者 run 溯源',
    ingest_ts         DateTime64(3,'UTC') DEFAULT now64(3) COMMENT 'RULE-SCHEMA-TZ'
) ENGINE = ReplacingMergeTree ORDER BY (trade_date)
```

## 三、Owner 批点清单（逐项）

1. **甲档映射表 6 格拍板**：尤其 ignition→PANIC_REPAIR、distribution→RISK_OFF 两个争议格；
   两桥（regime 六段桥 vs 情绪 S 档桥）择一。
2. **"查表=采集"边界认可**：daily_gate_snapshot 头注 :12 承诺"只读零判定"，
   water_temp_response 是查表非判定——此边界解释须 Owner 追认。
3. **乙档立项**：新表 DDL + 盘后产出者施工 + top_sectors/retained_sectors 口径真源
   （哪张板块热度表/涨停梯队表产出，现为空白）——乙档前置依赖，须先裁原料源。
4. **阈值 v2.1 带标上线**：0.60/0.80 未经 G05 回测校准（sector_gate.py:29/40），
   甲乙两档均建议载荷标 `"threshold_provenance": "v2.1_proposed_pending_G05"`，是否接受。
5. **decision_daily 解降条件追认**：l2.status=="ok" 即不再追加 D2_gate_absent:L2
   （orchestrator :565 判定面零改动，降级随采集自动消失）。

## 四、不批的后果

- decision_daily 每日继续 degraded=1(D2_gate_absent:L2)，依赖 L2 门参与的包持续禁用
  （蓝图 §四.2 原文口径），降级矩阵 L2 格永缺——编排器通而不全。
- 五层门快照 l2 恒 absent，当日归因链 L2 段空白，复盘无板块维度可查。
- 乙档不立项则 G05 选股引擎漏斗准入层无日态可读（sector_gate.py:5 CONSUMERS 挂账继续），
  v2.1 阈值永远停在"初拟"，回测校准无落地面。
