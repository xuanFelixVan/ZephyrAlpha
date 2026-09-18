---
ttl: task_bound
completes_when: 总包/Owner 裁 req_drift_01（CTR-P1-007 slippage_bps 的 NULL 语义）后，由下一腿按本件 §5/§6 配方落地 R-014 剩余项与污染行处置
---

# 漂移修复车道 st-ff-drift-20260918 · 受保护契约审批申请书（req_drift_01）

> **一句话**：`c1_market.execution_report.slippage_bps` 的"线上 `Nullable(Float64)` vs 代码 `Float64`"
> 前向漂移**已收口**（按 RULE-SSOT 取方向=代码真源对齐线上，零 ALTER、零行为变化）。
> 但 R-014 的"置 NULL 实现"与 `-10000.0` 污染行处置**同源于一处尚未获批的受保护契约改动**
> （CTR-P1-007 是 codegen SSOT）——本车道**未走审批旗、未硬闯**，按宪法 §5/R-017 申请授权。
> 本件同时是下一腿的施工包：配方、影响面、回滚、能红证据、三步验证留痕全部实测过。

## 1. 漂移现状实测（本车道亲跑，未沿用任何报告——含本总包任务书）

| 落点 | 位置 | 值 | 判读 |
|---|---|---|---|
| 线上（DB 真值） | `system.columns` → `c1_market.execution_report.slippage_bps` | `Nullable(Float64)` | 目标态 |
| 代码真源（收口**前**） | `schemas/categories/intraday/market_execution_report.py:72` | `Float64` | ← **漂移点（已修）** |
| 代码真源（收口**后**） | 同上 | `Nullable(Float64)` | 与线上一致，`verify_schema_truth.py --table execution_report` exit 0 |
| 契约（codegen SSOT） | `architecture_model/contracts/cross_layer_contracts.yaml:806` | `type: float, required: true` | **仍不一致——PROTECTED-PATHS，见 §5 待裁** |
| 生成件 | `src/zephyr/shared/contracts/execution_report.py:57` | `slippage_bps: float` | 由上行 YAML 生成，不可直改（改了下次 codegen 静默覆盖） |
| 校验口 | `src/zephyr/shared/contracts/execution_report_contract.py:164-167` | None → `ExecutionReportContractError[ZA-SH-0054] slippage_bps 必须为数值` | **NULL 今天在这条链上根本过不去** |
| 同表其余 17 列 | `system.columns` vs DDL-as-code | 逐列等值 | 无漂移 |

**注**：本表 `slippage_bps` 全库**零程序读者**（前手车道 G6 已证；本车道复核 `grep -rn "execution_report" src/zephyr/reporting` 只命中 contract 类型 import，无表读取），
故"改列类型"无任何 NOT NULL 依赖方受影响 → 路径 A 的数据风险 = 0。

### 1.1 全表类型对账（顺手做，成本=一条命令，未新建工具）

仓库**已有**该工具，无需再造：`scripts/ch/verify_schema_truth.py`
（DDL-as-Code 真源 vs `system.tables`/`system.columns`，比列集/列类型/引擎/排序键；有漂移 exit 1，可接 CI `--ci`）。
本车道全量实跑：**校验 205 张表真源（显式跳过 1 张设计态表 c1_market.factor_feature_value），发现 9 处漂移**
（报告：`.runtime/tmp/ff-drift/schema_drift_report.md`，有 TTL，故关键结论已抄进本件）：

| # | 漂移 | 归属 | 本车道处置 |
|---|---|---|---|
| 1 | `[execution_report] slippage_bps` 真源=Float64 vs DB=Nullable(Float64) | **本车道面** | **已修**（路径 A） |
| 2 | `[cohort_daily_ledger]` 真源有 DB 无 | z-land1（真源先行待建表，账本 R-032 已记） | 只登记 |
| 3 | `[cross_validation_log] threshold` Decimal(18,6) vs String | 他域既有 | 只登记 |
| 4 | `[stock_indicator] circ_mv` DB 有真源无 | 他域既有 | 只登记 |
| 5 | `[stock_indicator] total_mv` DB 有真源无 | 他域既有 | 只登记 |
| 6-8 | `[alt_sz_climate_hist]/[alt_sz_env_meteor]/[alt_sz_ground_obs]` 排序键"漂移" | alt_data 面 | **疑为工具判据缺陷**，见下 |
| 9 | `[alt_sz_reservoir_level]` 排序键 `((stcd, id))` vs `stcd, id` | alt_data 面 | 同上 |

→ 6-9 的形态（`((x))` vs `(x)`）指向 `_norm_key()` 只剥**一层**外层括号（`verify_schema_truth.py:132-137`），
多包一层即误报漂移 = **尺子自身的假阳**，不是数据问题。属他人文件（`scripts/ch/`），按宪法 §3.4 owner 责任制**不代修**，
移交建议：由 alt_data/registry 簇车道复核并把 `_norm_key` 改为循环剥括号 + 配能红钉。
（同型先例＝R-024 系列"机械事实 vs 语义判断"，此处是"机械比对自身的口径缺陷"。）

## 2. "HTTP 500" 根因：两条错误叠加，真实原因曾被传输层吞掉

先复现（临时库 `zephyr_drift_probe` 建同构 ReplacingMergeTree 表测，**测毕已 DROP，全程未碰生产列**），
再读服务器自己的 `system.query_log`——两问都在 2026-09-18 11:16:04 同秒留痕：

**真因（ClickHouse 拒绝该 ALTER 的裸形态）Code 36**
```
Code: 36. DB::Exception: Cannot convert column 'slippage_bps' from nullable type Nullable(Float64)
to non-nullable type Float64. Please specify `DEFAULT` expression in ALTER MODIFY COLUMN statement.
```
复现矩阵（scratch 表，逐条亲跑）：

| 场景 | 结果 |
|---|---|
| `Nullable→Float64`（表内**无** NULL 值） | **FAIL Code 36** → 不是数据阻塞，是类型收窄被禁 |
| `Nullable→Float64`（表内**有** NULL 值） | **FAIL Code 36**（同一错误） |
| `Nullable→Float64 DEFAULT 0` | **SUCCEEDED**，但 NULL 行被静默改写成 `0.0`（实测 `[(1,-10000.0),(2,0.0)]`） |
| `Float64→Nullable`（正向） | 可行——生产留痕 `system.mutations` `mutation_9 = (MODIFY COLUMN \`slippage_bps\` Nullable(Float64))` `is_done=1 @2026-09-18 11:11:38` |

→ **结论：漂移在物理上是单向门。** 回退方向被数据库否决，而唯一可执行的回退形态**主动制造错数**
（NULL→0.0 正是 R-014/N-1 要消灭的"0 伪装合法数值进闭环"）。这从数据库层独立印证路径 A 是唯一不撒病的收口方向。

**伪报（车道看到的 500）Code 164 + 错误体被丢弃**
```
Code: 164. DB::Exception: zephyr_writer: Cannot execute query in readonly mode.
For queries over HTTP, method GET implies readonly. You should use method POST for modifying queries.
```
成因链（`src/zephyr/data/ch_writer.py`，**本车道未改，属他人面**）：
`:427 query()` TCP 抛错 → 仅 `log.warning` 后降级 HTTP（`:465`）→ HTTP 分支用 **GET**（`:471 conn.request("GET", path, ...)`）
⇒ 任何 DDL/DML 走这条路必被 readonly 拒（Code 164）→ 非 200 分支**只记 status 不读响应体**（`:477`）
⇒ 真实错误码/文本永久丢失 ⇒ 调用方只能看到"HTTP 500"。
同族自认先例：`ensure_database()` 注释写明"避免权限错误走 query() 降级链：TCP 失效 churn + **HTTP 伪报**"。

→ **登记断点候选（提请总包派工）**：`ch_writer.query()` 的 HTTP 降级面对写操作**结构性不可用**且吞错误体，
属 R-021 家族"看起来在工作、实际报不了真错"。修法方向：写语句禁走 GET 降级（或改 POST）+ 非 200 必读 body 入日志。
复验命令：
```bash
python -c "import sys;sys.path.insert(0,'src');from zephyr.infrastructure.database_service import get_db_service as g; \
print(g().get_clickhouse_conn(role='reader').execute(\
\"SELECT event_time,type,exception_code,left(exception,200) FROM system.query_log \
WHERE query ILIKE '%ALTER TABLE c1_market.execution_report%' AND event_date>=today()-2 ORDER BY event_time DESC LIMIT 6\"))"
```

## 3. 收口方向判定（RULE-SSOT）= 路径 A

- 判定依据（本仓 SSOT 规则 6：表 schema 属**架构数据** → 真源=DDL-as-Code，`apply_*.py` 直写 DB）：
  本例两条真源冲突，必须选一个当"该成的样子"。
- 选 A（代码对齐线上 Nullable）的三个独立理由：
  1. **R-014 裁定依赖 NULL**："无有效执行样本"只有 Nullable 列存得下；非 Nullable 列会把 NULL 又变成 0（=N-1 病）。
  2. **数据库否决 B**：Code 36 证明 `Nullable→Float64` 只能配 DEFAULT 才执行，而任何 DEFAULT 都是伪造数值（§2 实测）。
  3. **A 零风险**：不改数据、不改行为（该列零程序读者），只让代码写真话。
- B 若坚持（"Nullable 不该存在"）= 推翻 R-014 的可存储前提，本车道无权限也无证据支持，故**未采用、未改裁定**。

## 4. R-014 剩余实现为何**未落**（实测，非转报）

`actual_quantity=0 → slippage_bps=NULL` 的落地要过三道，其中一道是受保护文件，绕不过：
1. 生产者 `src/zephyr/ex_core/execution_report.py:54 _signed_slippage_bps(side, intended_price, avg_fill_price)`
   **实测现状=3 参、无零成交守卫**（本车道 grep 亲验，前手配方未进 HEAD）→ 返回 -10000.0 的路径仍在。
2. 契约 `CTR-P1-007` 仍 `float/required` → 生成件字段 `slippage_bps: float`（非 Optional）。
3. **入站校验实测拒 NULL**（本车道亲跑）：
   - `validate_execution_report(ExecutionReport(..., slippage_bps=None))` → `[ZA-SH-0054] slippage_bps 必须为数值`
   - `execution_report_from_payload({..., "slippage_bps": None})` → `[ZA-SH-0054] slippage_bps 反序列化只接受数值`
   - 同一 payload 用 `-10000.0` → **校验通过**
   → **契约今天拦得住 NULL，却放行 -10000.0 这个错数**：门禁方向与语义诉求正好相反，这是本申请的核心论据。
4. 因此"只改 `schemas/**` 不碰契约"做不掉 NULL：只改生产者 → 写出的行读不回（第 3 条红）；
   只改生成件 → 下次 codegen 静默覆盖（违 RULE-SSOT）。**故停手申请，未硬闯 PROTECTED-PATHS。**

⚠️ **对总包任务书两处事实更正**（属 §6.6 型自纠，请总包别再沿用）：
- 任务书称"z-land2 已给出能红证据…你复用这套钉，别另写"——**那些钉不在仓库里**：
  `grep -rn "zero_fill_has_no_slippage|SlippageNullSemantics|one_lot_fill_still" tests/` → **0 命中**。
  前手是把改动**整体回退**后交工的（`req_land2_01.md` T2 配方态），故 85 passed / 变异 4 红这组数**无法复用、也无从复跑**。
  本车道改以"`verify_schema_truth.py` 变异 + 契约 None 探针"作本批能红证据（§7），未冒用前手数字。
- 任务书给的 SOP 路径 `docs/01_policies_and_standards/sop/data_ops_sop/schema_change_sop/` **不存在**
  （`data_ops_sop/` 实测只有 `data_ops_policy.md` + `data_source_onboarding_sop.md`）。
  本仓**无** `schema_changes` 登记表/注册表（CH `system.tables` 里 name 含 schema/chang/migrat 只有 `system.*` 内建表）。
  等价机制实测只有两处：① `apply_market_tables_ddl.py _MIGRATIONS`（该文件按账本 §2 归 residG 独占 → **未改**）；
  ② 真源文件自带的 `变更记录` 段（本车道采用，见 `market_execution_report.py` docstring）。
  → 提请总包裁：schema 变更登记机制是否要正式立一个（若立，建议挂 `_MIGRATIONS` + `verify_schema_truth.py --ci` 双钉）。

## 5. 待裁（Owner/Max，A 类）：批准 CTR-P1-007 把 slippage_bps 改为可空

**要改什么**（一处一行，`architecture_model/contracts/cross_layer_contracts.yaml:806`）：
```diff
-      - {name: slippage_bps, type: float, required: true, description: "滑点（基点）"}
+      - {name: slippage_bps, type: "Optional[float]", required: false, description: "滑点（基点，正=不利成本；null=无有效执行样本）"}
```
**为什么**：R-014 的判据（宁可缺一个数，不可有一个错数）要求"零成交终态不落数值"。
契约不放开可空，NULL 就无处安放 → 撤单/拒单每笔继续向 TCA/FF-02/FF-06 投一张"满分执行"的乐观票。

**批准后的落地配方**（前手已逐字节验通、本车道复核其结论未进 HEAD，故**需重放并重新配钉**）：
1. 改上 YAML 行 → `python scripts/governance/d5_architecture/generators/generate_contracts.py --contract CTR-P1-007`
   （注意：生成器会额外插 `from typing import Optional`，若 HEAD 版无此行需按字节删该行使净 diff 只剩字段行——前手实测坑）
2. `src/zephyr/ex_core/execution_report.py`：`_signed_slippage_bps` 增第 4 参 `actual_quantity: int`，
   体首 `if actual_quantity <= 0: return None`（在 `intended_price<=0` 守卫之前），调用点 `:119` 传 `actual_qty`，`[INVARIANTS]` 头补 NULL 语义
   （注意 `NO-LONG-PARAM-LIST` 阈值 7 → 4 参安全）
3. `execution_report_contract.py`：入站校验**加严**——`slippage_bps is None` 仅当 `actual_quantity==0` 合法，
   有成交量缺滑点 `_fail`；`_FLOAT_FIELDS` 分支补 `value is None → 原样透传`（禁顶成 0.0）
4. 生产端 `_to_tsv_row`：`"\N" if value is None else f"{float(value):.6f}"`（Python 源里须写 `"\\N"`，单反斜杠是 named-unicode 转义→SyntaxError）
5. **DB 侧本车道已就位**：`schemas/**` 与线上均已是 `Nullable(Float64)`，此批**不需要任何 ALTER**
6. 必补测试钉（当前 HEAD **没有**）：`test_zero_fill_has_no_slippage_sample`（断言 `is None`）/
   `test_one_lot_fill_still_measures_slippage`（反向钉）/ 契约层 `TestSlippageNullSemantics` 三钉 /
   producer 层 `row["slippage_bps"] == r"\N"`
   ⚠️ 既有钉 `tests/ex_core/test_execution_report.py:105 test_zero_intended_price_slippage_degrades_zero`
   仍断言"无基准→0.0"——**它是"缺数伪装成 0"的现存标本**，落地腿须一并改判（否则该测试会锁死旧语义）

**影响面**：CTR-P1-007 消费方 = TCA/归因回流入口（FF-02/FF-06）、`execution_report_contract` 校验口、
本表列类型（已就位）。字段数不变、无新增列 → 不触"注册表净删"门位；但**契约语义变更属 Owner 授权面**。

**回滚方案**：YAML 单行 revert + 重跑生成器即回 `float/required`；生成件与 `schemas/**` 的 diff 均可按字节 revert；
DB 侧本批零 ALTER ⇒ 回滚不涉及数据。

## 6. 污染行（`-10000.0`）处置：三条路代价 + 选择

**RULE-DATA-OPS 三步验证留痕**
- 必要性：错数会进闭环被当证据复用（R-014）；但**当前零程序读者 ⇒ 危害尚未兑现**，非紧急。
- 真实性（看内容不只看聚合）：`SELECT count() FROM c1_market.execution_report` = 1；FINAL 亦 1；
  全字段 `GROUP BY ALL HAVING count()>1` → **0 组重复**（未用 `count()-uniqExact(排序键)` 判据）。
- 可逆性：**前手那份 5 字段备份不足以回滚**（缺 direction/价格/时间/idempotency_key/schema_version/ingest_ts）。
  本车道已补**全 18 列**备份，并内嵌于此（不依赖 TTL 目录，R-030 教训）：
  ```
  order_id  symbol  direction  intended_quantity  actual_quantity  intended_price  vwap_price  slippage_bps  commission  execution_start  execution_end  broker_id  algo_type  idempotency_key  schema_version  ingest_ts  exchange  symbol_canonical
  f216058c-6df6-4752-8eb3-bb0854bf5430  510300.SH  BUY  100  0  4.07  0  -10000.0  0  2026-09-18 10:26:15.033000+00:00  2026-09-18 10:27:49.064000+00:00  qmt_sim  NONE  a28ec1c62f3d939459f97c7fac611cb3993fe633c2978ea5b3cef340404bd792  1.0  2026-09-18 10:27:50+00:00  SH  510300.SH
  ```
  （机器件：`.runtime/tmp/ff-drift/backup/execution_report_full_row_20260918.txt`）

| 路 | 做法 | 实测代价 | 判定 |
|---|---|---|---|
| ① mutation | `ALTER TABLE … UPDATE slippage_bps=NULL WHERE order_id=…` | 不可逆改写历史 part（`system.mutations` 留痕，但**回滚只能再发一条反向 mutation**，而反向 `Float64→` 赋值又受 Code 36 之外的另一类限制）；且 mutation 是"最终一致"，未 merge 前 FINAL 与非 FINAL 视图不一致；**写入 NULL 立刻撞 §5 未批的契约** | 否 |
| ② data_quality 标记 | 加旁证列 + 下游过滤 | 需 `ADD COLUMN` → 违本表 `[INVARIANTS]` "15 字段与 CTR-P1-007 一一对应，不按想象加字段" → **同样触受保护契约且改动更大** | 否 |
| ③ 追加新版本行（ReplacingMergeTree 正道） | 同 `ORDER BY` 键 `INSERT … SELECT` 一条 `slippage_bps=NULL` 的行，旧行由 merge 收敛 | 最可逆（旧行物理仍在，可用同法再追加旧值覆盖）；**但**：merge 前非 FINAL 读会短暂见 2 行（本仓房规"查 ReplacingMergeTree 必带 FINAL"已覆盖）；且 NULL 同样需 §5 先批 | **采用（延后至 §5 批准）** |
| ⓪ 不动 | 等 §5 批准后与 §6 配方同批 | 错数继续留在表内（当前零读者 ⇒ 未兑现危害） | 本批实况 |

**本车道选择 = ③，但时序绑定 §5 批准，本批不执行任何写。** 理由（实测）：NULL 今天读不回来（§4 第 3 条），
先落 NULL 行等于把一个"合约方读不了"的行种进即将接通的 TCA 入口——比留着已知错数更坏（错数是可计量的乐观偏差，
unreadable 行会让消费链 fail-closed 全断）。已备好可执行 SQL + 回滚，批准后一条命令做完：

```sql
-- 修正（§5 批准后执行；键由 SELECT 自取，杜绝手抄 ms 级时间戳打偏导致永不合流）
INSERT INTO c1_market.execution_report
  (order_id, symbol, direction, intended_quantity, actual_quantity, intended_price,
   vwap_price, slippage_bps, commission, execution_start, execution_end, broker_id,
   algo_type, idempotency_key, schema_version)
SELECT order_id, symbol, direction, intended_quantity, actual_quantity, intended_price,
   vwap_price, NULL, commission, execution_start, execution_end, broker_id,
   algo_type, idempotency_key, schema_version
FROM c1_market.execution_report FINAL
WHERE order_id = 'f216058c-6df6-4752-8eb3-bb0854bf5430' AND actual_quantity = 0;

-- 验证（做完这两条必须成立）
SELECT slippage_bps FROM c1_market.execution_report FINAL WHERE order_id='f216058c-6df6-4752-8eb3-bb0854bf5430';  -- 期望 \N
SELECT count() FROM c1_market.execution_report;  -- 期望 2（merge 前），OPTIMIZE 后回 1

-- 回滚（同法追加旧值行， newest 胜出；旧值见本件 §6 全字段备份）
```
执行前置：`OPTIMIZE TABLE c1_market.execution_report FINAL` 前先确认无并发写者；
本表 `ENGINE = ReplacingMergeTree` **无版本列**（实测 `system.tables.engine_full`，收敛按插入序取最新）
→ 故"追加覆盖"可用，但若要求严格单调须把版本列一并申请（另裁）。

## 7. 本批能红证据（不冒用前手数字）

1. **漂移判据变异红/绿**（按字节 mutate + sha256 校验还原）：
   - 把 `schemas/**` 该行改回 `Float64` → `verify_schema_truth.py --table execution_report` **exit 1**，
     明细 `- [execution_report] 列 'slippage_bps' 类型漂移: 真源=Float64 vs DB=Nullable(Float64)`
   - 还原（sha256 一致）→ **exit 0，0 处漂移**
2. **契约 NULL 不可用探针**（本车道亲跑，即 §4 第 3 条三条输出）：证明"不批契约则 NULL 落不了地"。
3. **回归**：`tests/ex_core/test_execution_report.py` + `test_execution_report_producer.py` = **33 passed**；
   `tests/ex_core/test_execution_report_contract.py` = **47 passed**（合计 80，本批改 schemas 后零红）。
   按 #325 口径：这只说明"这三套本轮 80 条通过且漂移判据被证明能红"，**不等于全链路无缺陷**——
   已知零读者（G6）与 §5 未落地项仍在。
4. 诚实未做项：未跑 `tests/ex_core` 全目录（该目录另有前手在途 4 红，`req_land2_01.md` T4 已记，非本车道面）。

## 8. 需总包/Max 做的三件事

| # | 事项 | 类别 |
|---|---|---|
| 1 | 批 §5 契约单行（或明写不批+给替代方案），本车道无 CLI 逃生旗可用 | A 类裁定（PROTECTED-PATHS 本质是 Owner 授权面） |
| 2 | 裁 §4 末"schema 变更登记机制要不要正式立"（路径写错+无 schema_changes 的实测更正请回写账本） | A 类裁定 |
| 3 | 派工 §2 的 `ch_writer.query()` HTTP 降级伪报（吞错误体 + GET 不可执行写），与 §1.1 的 `_norm_key` 假阳 | B 类执行 |
