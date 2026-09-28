---
ttl: task_bound
volume: wiring_A_fill_writer
session: st-ailayer-final-20260924
creation_token: bf5-fill-single-writer-w3a-20260926
---

# W3-A 施工记录：BF-5 单一写者 ＋ BF-1③/BF-9 ＋ BF-2/BF-10 零样本披露 ＋ BF-4 脱敏

> 裁法真源=`94_chief_rulings_wave2.md` §二（M7 实盘执行链 10 案）；作业规范=`92_chief_command_wave2.md` §一。
> 本车道零提交、零入队、零 release claim，全部产物由总筹单点落地。

## 一、BF-5 单一写者（已完工，F57 恒空的总根）

**落点**=`scripts/start_paper_session.py::_wire_position_book_feed`（AsyncFillDispatcher 的
**消费线程**内，非券商回调线程——守 40_execution_broker §决策①工程约束1"回调零耗时"）：

```
consumer: tracker.apply_fill(fill, order.side)              # 既有本地持仓账腿，未动
          fill_writer.process_fill(fill, 订单快照副本)        # 新增：Fill 事实 JSONL 唯一写者
```

三个非常规处置（都有测试钉，不是随手写法）：

1. **写者只吃订单快照副本**（`copy.copy(order)` ＋置 `filled_quantity=0`/`avg_fill_price=None`）。
   原因：`OrderManager._on_fill` 在触发回调链**之前**就已就地累加 `filled_quantity/avg_fill_price/status`
   （`src/zephyr/ex_core/order_manager.py:557-578`），而 `FillHandler.process_fill`
   同样就地累加——把活订单直接交给写者＝同一笔成交在订单账上计两次（数量翻倍、提前 FILLED）。
   钉=`test_live_order_is_never_second_counted_by_the_writer`。
2. **快照的 `order_id` 改按 fill 侧键**。原因：`_lookup_order` 有第二条路（券商推送
   broker 订单号 ≠ 本地 UUID），`process_fill` 的一致性校验会抛 `OrderNotFoundError`，
   被派发线程计入 `errors` 吞掉＝又一条静默丢失的 Fill 事实。
   钉=`test_broker_order_id_keyed_fill_is_not_silently_dropped`。
3. **写者去重集必须持久且必须与 tracker 分文件**。共用同一条 `AppendOnlyDedupSet`
   会让先跑的 `tracker.apply_fill` 抢登记，写者永远判"已处理"→**一行都不落**；
   纯内存 set 又会让 `--service` 退避重启重放当日成交造重复行（系统侧笔数虚高＝反向假绿）。
   故新文件 `data/runtime/state/paper_fill_jsonl_written`（与 tracker 的每装配唯一 token 反向＝稳定名）。
   钉=`test_writer_dedup_survives_process_restart` / `test_replayed_fill_id_writes_exactly_one_line`。

**单一写者判据**（不得两处写同一路径）用两台尺钉：
- 动态尺：tmp 目录跑通装配链 → 每笔成交恰好一行 JSONL，且 `FillHandler.query_fills_by_date`
  （F57 的读取口径）原样读回（写读闭环）。
- 静态尺：AST 扫 `src/`＋`scripts/`，同时"构造 `FillHandler(fills_dir=…)`"＋"调用 `process_fill`"
  的文件集合必须 `== {scripts/start_paper_session.py}`；`aggregate_root_manager.py` 门面
  不得出现 `fills_dir`（它一旦自带目录，注入即成第二写者）。
  `run_post_settlement.py` 构造 `FillHandler(fills_dir=…)` 但**只读不写**（不调 process_fill），
  故不判为写者——读写同目录、写只一处。

**验收状态**：tmp 目录侧全部实测通过；生产 `data/fills/` 出现真文件由总筹在窗口内验
（本车道按纪律**未写生产目录**，实测跑完 `data/fills` 仍不存在）。

## 二、BF-1③ 消假 auto —— 未达标，如实报红（词表闸在前面）

裁法要求把 `config/trading_decision_map.yaml` 节点 `TDM-E-L4-13` 的 `auto` 改 `manual`。
实测：**`manual` 不是合法档位，改了就硬阻断**——

| 步骤 | 实测结果 |
|---|---|
| 基线（现网 YAML）跑 `validate_decision_map` | `ok=True errors=0 R15=0 nodes=182` |
| 把该节点改成 `ai_autonomy: manual` 的临时副本再跑 | `ok=False errors=1 R15=1`：`R15: TDM-E-L4-13 ai_autonomy 非法: manual` |

真源=`src/zephyr/trading/decision_map.py:82` `_AI_AUTONOMY = {shadow, paper, pilot, daily_review, auto}`，
它是**宪章 B-007（2026-09-06 Owner 终裁）五档实盘治理阶梯**的镜像，
文档侧同锚=`sop/trading_decision_map_sop/trading_decision_map_layering_policy.md §2.2.1`。
"补一档 manual"要同时动 代码常量＋SOP 阶梯表＋宪章 B-007 文本 三处，属词表/判据变更
（车道纪律：禁改判据、禁自赋裁定、禁写 Owner 署名）⇒ **今夜不落，YAML 一字未改**。

已落的"没有争议的半边"：`tests/trading/test_tdm_false_auto_census.py`
- 普查器（机器可复算，不靠记忆）：`ai_autonomy=auto` 且 `module_ref` 在 `src/+scripts/`
  零非自身引用 的节点＝假 auto 候选。**2026-09-26 实测＝5 个**：
  `TDM-E-L2-10 / TDM-E-L3-05 / TDM-E-L3-10 / TDM-E-L4-13 / TDM-X-S2-06`。
- 词表防扩档尺：`_AI_AUTONOMY == 五档阶梯`，谁悄悄加档而不同批改 SOP/宪章即红。

### 待裁（一案一行，供总筹并入 pending 账）

- **W3-A-P-1｜ai_autonomy 缺"未接线"档**：五档全是"授权跑多狠"，没有一档表达"根本没跑"，
  于是"零调用方的引擎标 auto"在词表层面**无法被改真**。已试路径＝直接改 `manual`（R15 硬错误）。
  选项 ①补第 6 档 `manual`（代码＋SOP §2.2.1＋宪章 B-007 同批，另配"改 YAML 能改变行为"的红测）；
  选项 ②新增独立字段 `wiring_status: wired|unwired`（不碰授权阶梯，普查器改读该字段）；
  选项 ③节点级 `autonomy_log` 追一条降级说明（最轻，但 md 表不派生该字段＝标注面仍在说谎）。
  建议＝②（授权档位与接线状态是两个正交事实，塞进同一阶梯以后必然再撞一次）。门位＝high（词表/判据变更）。
- **W3-A-P-2｜BF-2 三态与拆码**（裁法已留 Owner，此处只报施工边界）：今夜只落披露，
  `reconcile_status/audit_status` 与 exit 0/1/3 矩阵**逐字节未动**。
- **W3-A-P-3｜BF-9 两套 PositionReconciler**：今夜只互写头注边界（未改名/未并判据）。
  改名与口径上移留 Owner（含注册表条目净删）。
- **W3-A-P-4｜BF-4 残留明文面**：`src/zephyr/ex_core/adapters/miniqmt_broker.py:420`
  （`MiniQMT 券商连接成功 … account=%s`）与 `:938`（`StockAccount 构造成功 account_id=%s`）
  仍打明文券商账号——该文件属 W3-B 车道（本车道禁触）。脱敏件已备好可直接复用（见 §四）。

## 三、BF-2 / BF-10 零样本披露（已完工，纯披露）

落点=`scripts/run_post_settlement.py`（盘后链唯一编排面）：

| 步 | 零样本判据（新增） | 披露动作 |
|---|---|---|
| 对账·系统侧 | `query_fills_by_date` 返回空 | WARNING＋台账 `step=reconcile_system_side` |
| 对账·券商侧 | `fetch_broker_settlement_records` 返回空 | WARNING＋台账 `step=reconcile_broker_side` |
| 日终审计 | `fills/positions/nav` 三腿皆零（空快照最小输入） | WARNING＋台账 `step=daily_audit` |
| VaR 定级 | 状态根无盘前基线，或 `report is None`，或 `n_obs` 为零 | WARNING＋台账 `step=var_backtest` |
| 降级路径 | 券商离线且系统侧零笔 | WARNING＋台账 `step=system_fills_degraded` |

- 台账真源=`data/runtime/post_settlement_zero_sample_ledger.jsonl`（gitignore 在册；
  机器读物落机器目录，文档面引用不誊抄）。测试注入 tmp_path，实测跑完生产根零新文件。
- 幂等口径守本件既有 [INVARIANTS]"同 trade_date 重跑无副作用"：整档读→剔同
  `(trade_date, step)`→追加→`os.replace` 原子换名，重跑不堆同键行。
- **未动的东西**（三态判据/错误契约属 Owner）：`SettlementReconciler` 判据、
  `DailyAuditor` 判据、`run_post_settlement_pipeline` 状态机、`_exit_code_of()` 矩阵。
  钉=`test_disclosure_never_changes_verdict_or_exit_code`（带台账/不带台账同一次零样本跑
  exit 码必等；且状态仍 `("OK","OK")`、`_exit_code_of==0`）。

## 四、BF-4 账号脱敏（已完工，只动日志面）

- 新增可复用件=`src/zephyr/shared/security/secrets.py::mask_identifier_tail(identifier, keep=4)`：
  留末 4 位；`None`/空串/长度≤keep → 全遮 `***`（短号留尾＝几乎原样泄露）。
- 与既有 `sanitize_secret`（`***REDACTED*** (len=N)`）**故意分两口径并写明理由**：
  券商账号是运营定位键（日志要能回答"哪一路账户出的问题"），密钥没有任何"留尾"的正当性；
  混用一条口径的历史结局要么泄露账号、要么运维失明。
- 本车道改了哪些明文日志：`scripts/run_post_settlement.py::_try_connect_sim_broker`
  的盘后标注（`account=8886156677` → `account=***6677`）。真号仍原样交给 broker（功能不变）。
- **待接线一行（W3-B 文件，本车道未触）**：
  `src/zephyr/ex_core/adapters/miniqmt_broker.py:420` 与 `:938` 改为
  `account=%s ... mask_identifier_tail(self._account_id)`（import：
  `from zephyr.shared.security.secrets import mask_identifier_tail`）。
  "模拟账户号是否算敏感"的口径立法仍留 Owner（94 册 BF-4 第二列）。
- 未动 `scripts/tests/smoke_test_qmt_broker.py:148` / `smoke_test_trading_session.py:118` /
  `scripts/construction/qmt_bridge_regression_smoke.py:121` 三处冒烟打印（非盘后生产日志链，
  留同批复核，避免跨面改判据）。

## 五、待登项（总筹单点补，本车道未改任何热册/PG）

- **creation_token**（新建 .py 非 tests/ 豁免范围内者）：
  - `mask_identifier_tail` 所在件为**修改**既有模块 → 无需新 token；
  - 新建件均在 `tests/`（CREATE-GUARD 豁免）：`tests/ex_core/test_fill_jsonl_single_writer.py`、
    `tests/scripts/test_run_post_settlement_disclosure.py`、`tests/trading/test_tdm_false_auto_census.py`；
  - 本 .md 自身 token=`bf5-fill-single-writer-w3a-20260926`（头注在册）。
- **翻译册（大白话简介）**：本车道**未新建 .py 模块**，只在既有模块内加函数/改装配；
  若 TRANSLATION-COVERAGE 要求新增测试件登记，待登 3 个 tests 模块（路径见上）。
- **depgraph**：需登记的设计节点/产物声明两条——
  1. `MOD-SCRIPT-start_paper_session` 新增产物边：`data/fills/YYYYMMDD.jsonl`（写者，本件唯一）
     与 `data/runtime/state/paper_fill_jsonl_written`（写侧去重集）；
  2. `MOD-SCRIPT-run_post_settlement` 新增产物边：`data/runtime/post_settlement_zero_sample_ledger.jsonl`
     （披露台账，消费方=次日复算/盘后体检，不参与任何判定）。
  另：`zephyr.ex_core.fill_handler` 的 `[CONSUMERS]` 头注可补一句"生产唯一写者=
  scripts.start_paper_session（经 AsyncFillDispatcher 消费线程）"，本车道未代改热册。

## 六、复核命令（Windows PowerShell，先注入 3.12）

```
$env:PATH = "$env:LOCALAPPDATA\Programs\Python\Python312;" + $env:PATH
$env:PYTHONPATH = "src"
python -m pytest tests/ex_core/test_fill_jsonl_single_writer.py `
  tests/scripts/test_run_post_settlement_disclosure.py `
  tests/scripts/test_run_post_settlement.py `
  tests/scripts/test_start_paper_session.py `
  tests/ex_core/test_async_fill_dispatcher.py `
  tests/trading/test_tdm_false_auto_census.py `
  -p no:cacheprovider -c py.ini -q --timeout=300
# 生产目录必须仍不存在（车道禁写）：
Test-Path data/fills          # 期望 False
# BF-1③ 词表闸复现（改 manual 必 R15 硬错误）：
python .runtime/tmp/probe_manual_vocab.py
```
