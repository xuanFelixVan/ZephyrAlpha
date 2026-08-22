---
blueprint_id: MOD-RPT-028
module_name: prediction_log_writer
domain: D_REPORTING
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
---

# MOD-RPT-028 prediction_log_writer 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘 §12.1 M4-②（"每天预测了什么"可回查可验证）+ 92号清单 §7.13（governance.db 新表 prediction_log，D2 授权 DB 写；对齐 reconciliation_differences 落治理库先例）。机构对标：TradingAgents decision log / 对冲基金 research journal。
> 代码：`src/zephyr/reporting/prediction_log_writer.py`

## 0. 定位

每日预测类输出统一落库写入器——governance.db `prediction_log` 表的 schema 唯一真源与唯一写入口。消费方=波5 各生产模块（M1 情绪分/M2 边界修正事件/M3 三情景/LLM 盘前分析——44号 §12.1 M4-② 四族）与 92号 §8.7 M4-④ 命中率统计器（规划）。

## 1. 接口

```python
def ensure_prediction_log_table(db_path: str | Path | None = None) -> Path
    # 幂等建表（CREATE TABLE IF NOT EXISTS + trade_date/module 两索引）；None=DB_PATH SSoT

def log_prediction(
    trade_date: str, module: str, prediction_type: str, payload: object,
    asof_ts: str | None = None, model_version: str | None = None,
    prompt_version: str | None = None, input_hash: str | None = None,
    db_path: str | Path | None = None,
) -> int                                      # 新行 id / 已存在行 id（同键幂等跳过）

def query_predictions(
    trade_date: str | None = None, module: str | None = None,
    prediction_type: str | None = None, limit: int = 1000,
    db_path: str | Path | None = None,
) -> list[dict]                               # 过滤器可组合，trade_date/id 倒序
```

## 2. 输出契约（表结构）

```sql
CREATE TABLE IF NOT EXISTS prediction_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trade_date TEXT NOT NULL,        module TEXT NOT NULL,
    prediction_type TEXT NOT NULL,   -- sentiment_score/boundary_revision/scenario_plan/llm_analysis/...
    payload_json TEXT NOT NULL,      -- canonical JSON（sort_keys 稳定序）
    asof_ts TEXT NOT NULL,           -- 预测生效时点（ISO8601；PIT——该时点可见信息集）
    model_version TEXT, prompt_version TEXT, input_hash TEXT,
    created_at TEXT NOT NULL,        -- 落库时点 UTC ISO8601
    UNIQUE(trade_date, module, prediction_type, input_hash)
)
```

**幂等语义**：同键重复写=跳过（INSERT OR IGNORE）**保留首条**，返回已存在行 id——预测日志是审计载体，"当天预测了什么"以首写为准；修正性重跑因输入变化自然产生新键新行（append-only 文化）。input_hash 缺省=canonical payload SHA-256（内容寻址，幂等键恒有效）；显式传入优先。SQLite UNIQUE 中 NULL 互不冲突，故 input_hash 入库前 None 归一为 ''。

## 3. 不变量（头注 INVARIANTS 原文）

- append-only 仅 INSERT（同键重复=跳过保首条不覆写）
- SQL 参数化+常量（NO-BARE-SQL）
- db_path 默认 None 走 DB_PATH SSoT（测试注入临时库，trend_analyzer db_path 同款隔离先例）
- 输入校验 fail-closed
- input_hash 缺省=canonical payload SHA-256（内容寻址，幂等键恒有效）

## 4. 降级行为

- ERROR_CONTRACT：ValueError（输入非法 fail-closed）；sqlite3.Error 透传
- DDL 常量即本模块真源，禁止测试侧复刻副本；新环境/测试库走 ensure_prediction_log_table 幂等建表

## 5. 边界（不做）

- 不做查询侧业务判定（统计/校准属 MOD-RPT-029）；不建第二账本（outcome 族回写复用本表，见 MOD-RPT-029 裁定一）

## 6. 测试

tests/reporting/test_prediction_log_writer.py
