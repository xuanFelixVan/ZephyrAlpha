---
ttl: task_bound
completes_when: z-land 落地 execution_report 生产端四件套并复核本清单 G1-G6 全部关闭
---

# BRK-020 核验结论与缺口清单（对账与反馈闭环车道 st-ff-wirerecon-20260918）

> **一句话**：lane-E 留下的 execution_report 生产端接线**是真的、且已被真实模拟单打通**
> （台账从 0 行 → 1 行，见 §1 实测）。但有 **1 个会让整条 ex_core 断链的落地地雷** 和
> **1 个已经把脏数据写进生产表的数据质量缺陷**，必须由 z-land 在本批一并处理。
> 本车道**未改动** `src/zephyr/ex_core/**`、`src/zephyr/pf_alloc/**`（z-land 唯一写者）。

## 0. 验收判据（任务书 §BRK-020 硬判据）

> "段二脚本重跑后 `execution_report` 出现本单聚合行（`order_id`/`actual_quantity=0`）"

**结果：达标**（用等价驱动器跑，段二脚本本身因 G2/G3 两处检测法缺陷不可直接运行）。

## 1. 实测证据（全部本车道亲跑，非引用他人结论）

| 步 | 命令 | 实测输出 |
|---|---|---|
| E1 接线是真的 | `PYTHONPATH="D:/ZephyrAlpha;D:/ZephyrAlpha/src" python scripts/construction/qmt_bridge_regression_smoke.py`（无 PYTHONPATH 时 = ModuleNotFoundError，见 G2） | 日志：`execution_report 生产端已接线 env=sim producer=ExecutionReportProducer` → `execution_report 生产端接线 broker=qmt_sim` |
| E2 台账基线 | `SELECT count() FROM c1_market.execution_report FINAL`（`zephyr.data.ch_writer.query`） | 接线前 `0`；引擎 `ReplacingMergeTree` |
| E3 **真单终态落行** | `.runtime/tmp/st-ff-wirerecon-20260918/wire_e4_check.py`（本车道驱动器：装配→等首轮 sync→发 510300.SH BUY 100 @4.07→撤单收敛 CANCELLED→查表） | **P5 PASS**：`rows=1`；行内容 `f216058c-6df6-4752-8eb3-bb0854bf5430 / 510300.SH / BUY / intended=100 / actual=0 / commission=0 / broker_id=qmt_sim / algo_type=NONE / idempotency_key=a28ec1c6…`；producer_stats `observed=95 terminal_seen=1 emitted=1 skipped_non_terminal=91 skipped_duplicate=3 build_failed=0 validation_failed=0` |
| E4 幂等/无重复行 | `SELECT count() FROM …FINAL` vs 非 FINAL | 均为 `1`（order_id 幂等 + ReplacingMergeTree 同键替换均生效） |
| E5 单元面 | `pytest tests/ex_core/test_execution_report_producer.py -q -p no:cacheprovider -W ignore::pytest.PytestConfigWarning` | **23 passed** |
| E6 全链汇总 | `pytest tests/rollback/test_rollback_position_reconciler.py tests/trading/test_reconciliation_loop.py tests/ex_core/test_execution_report_producer.py tests/e/test_e_position_reconciler.py` | **88 passed**（含本车道新增 15 个 fail-closed 钉，见 §4） |

安全边界：全程 `env=sim`、账户双重断言 8886156677、跌停价 4.07（必不成交）、实盘 8887871993 零接触。

**残余未证的一腿**：FILLED（真实成交）终态未覆盖——A 股 15:00 收盘，柜台 18:2x 已不再回执
（E3 的 P3 步 FAIL：`status=SUBMITTED`，靠撤单才收敛）。须在下一交易窗口（09-19 09:30 后）
带 G2/G3 修复重跑，补 FILLED 行的 `actual_quantity>0` + `commission>0` 证据。

## 2. 缺口清单（按严重度；除 G6 外全部落在 z-land 独占文件）

### G1 【阻塞级·落地地雷】staged 与 untracked/unstaged 三张皮，照现暂存面落地即崩全链

实测（`git status --short -- src/zephyr/ex_core/ tests/ex_core/`）：

| 件 | 现状 | 后果（若按现 staged 面落地） |
|---|---|---|
| `src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py` | `MM`（staged +45 行含 `:40` `from zephyr.ex_core.execution_report_producer import ExecutionReportProducer`，且 unstaged 还改了头注释 DEPENDENCIES/INVARIANTS） | — |
| `src/zephyr/ex_core/execution_report_producer.py` | **`??` untracked** | 落地后 `import …qmt_file_bridge_integration` → **ModuleNotFoundError**，ex_core 装配层整条 import 断（交易会话、`frontend/dashboard/app_panel.py:525` 健康监控、`scripts/construction/*` 全灭） |
| `tests/ex_core/test_execution_report_producer.py` | **`??` untracked** | 生产件与其唯一测试面分离，TRANSLATION/TESTS 头指向不存在的测试 |
| `src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py` | **` M` unstaged**（`attach_execution_report_producer`/`order_cache_snapshot`/`execution_report_stats`/`_observe_terminal_orders` +40/-1，以及同步线程 `:804` 的调用点） | 即使 producer 在，`broker.attach_execution_report_producer(...)` → **AttributeError at assemble()**；且 `_observe_terminal_orders()` 无人调用 = 台账恒 0 行（断点原地复活） |

**改法（z-land）**：上述 4 件 + 新件登记三件套 **必须同一 commit 原子落地**：
`batch_creation_tokens.py`（token 载体 `capability_canonical_file_registry.yaml` 同批）、
`apply_depgraph.py --add-design-node`、`add_module_translation.py`（须主仓跑）。
**落地后核验命令**（两条都必须非空，缺一即判 G1 未闭）：
```bash
git show <sha>:src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py | grep -c execution_report_producer
git ls-tree <sha> src/zephyr/ex_core/execution_report_producer.py src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py
```

### G2 【高】验收仪根本跑不起来：`scripts/construction/qmt_bridge_regression_smoke.py:59-64` 缺 repo-root sys.path bootstrap

实测：`python scripts/construction/qmt_bridge_regression_smoke.py` →
`ModuleNotFoundError: No module named 'schemas.categories'`（traceback 经
`execution_report_producer.py:60`，即 `schemas/` 在 repo root 而非 site-packages，
脚本按路径执行时 `sys.path[0]=scripts/construction`）。
**改法**（本仓既有惯例，见 `scripts/ch/apply_consensus_daily_ddl.py:33-34`）：在 `:59` 的 import 块之前插

```python
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
```

并把 `:59-64` 的 6 个 import 补 `# noqa: E402`。临时绕过：带 `PYTHONPATH=<repo>;<repo>/src`（本车道 E1/E3 即用此法）。

### G3 【高】验收仪竞态误中止：`qmt_bridge_regression_smoke.py:193-194`（`_assert_sim_counter`）

实测：`前置中止: 柜台 Account.csv 不可读（QMT 模拟端未导出？）` → exit 2，**但文件在且新鲜**
（`E:\qmt_bridge_sim\Stock\Account.csv` mtime 17:57，account=8886156677 可正常解析）。
成因：`QmtFileBridgeBroker.connect()`（`qmt_file_bridge_broker.py:461-491`）只**启 daemon 同步线程即刻返回**，
`CounterStateMirror._account` 由首轮 `sync_all()`（`:170` `_sync_account()`）填充；
`get_counter_account()`（`:737`）在首轮完成前恒返回 `{}` → falsy → 误判"不可读"。
**改法**：`_assert_sim_counter` 改为限时轮询（≤25s，0.5s 步进）等首轮落账，超时才 fail-fast；
参照实现见 `.runtime/tmp/st-ff-wirerecon-20260918/wire_e4_check.py::wait_first_sync`（E3 实测 PASS：
`{'total': 9999867.66, 'available': 9990768.46, 'frozen': 335150.51, 'market_value': 9099.20}`）。
**与 seg2 已登记两条检测法缺陷同族**（"盘后/时序"型误判），建议一并写进检测法清单。

### G4 【高·数据质量】未成交终态落行 `slippage_bps = -10000.0`（已污染生产表 1 行）

实证（E3 真实生产行）：`order_id=f216058c-6df6-4752-8eb3-bb0854bf5430 → slippage_bps=-10000.0, vwap_price=0, intended_price=4.07, intended_qty=100, actual_qty=0, commission=0`。
成因链：
1. `execution_report_producer.py:301-303`：未成交 → `avg_fill_price` 为 None/≤0 且无 fill 明细 → 保持 `Decimal("0")`；
2. `:315` 把它作为 `avg_fill_price` 送进 `ExecutionEngineRunRecord`；
3. `src/zephyr/ex_core/execution_report.py:54-62` `_signed_slippage_bps(BUY, intended=4.07, avg=0)` = `(0-4.07)/4.07*10000` = **-10000**。

危害（这是 FF-12→FF-02/FF-06 回流的入口数据）：滑点口径"正=不利成本"，**-10000bps = 满分执行**。
每一笔撤单/拒单都向 TCA 与归因投一张"执行得最好"的票，均值随撤单率线性放大且方向恒定乐观；
`execution_report` 越接通，下游越自信。**这是"接了线反而更错"的一类，必须与 G1 同批修**。
**改法（建议 A）**：`src/zephyr/ex_core/execution_report.py:54` 签名加 `actual_quantity: int`，
函数体首行加 `if actual_quantity <= 0: return 0.0`（"无成交不判滑点"，与既有
`intended_price <= 0 → 0.0` 的"无基准不判定"同哲学），调用点 `:119` 传 `actual_qty`；
**配套测试钉**：未成交终态行 `slippage_bps == 0.0`（删该行即红）。
（不建议在 producer 侧把 avg 顶成 intended——会连带污染 `vwap_price`。）

### G5 【中】FILLED 腿未测（时间窗，非缺陷）

见 §1 末。登记为"下一交易窗口 09-19 09:30 后重跑 smoke 补证"。属可自动完成项，**不属 Owner 门位**。

### G6 【高】台账有生产者但**零读者** → 闭环仍差最后一公里（本车道只能到这一步）

- `c1_market.execution_report` 现无 src 侧读者：`grep -rn "execution_report" src/zephyr/reporting` 仅命中
  `attribution_result_store.py` 的注释，无表读取；`build_execution_report` 的下游 = 0。
- 持仓对账事件入口 `PositionReconciler.handle_execution_report` 存在，但**没有扇出点**：
  producer 只写 CH，不发事件；`zephyr/shared/event_bus.py:58` 的 `EventType` 是任务生命周期枚举，无执行域事件。
- **改法（建议，落 ex_core → z-land）**：`ExecutionReportProducer.__init__` 增
  `listeners: Sequence[Callable[[ExecutionReport], None]] = ()`，`observe()` 在 `_write()` 之后
  对本轮每个成功 report 回调（try/except + Fail-Loud 计数，旁路不得打断订单主链，与 `:381-408` 同策）；
  `QmtFileBridgeAssembly` 增 `add_execution_report_listener(cb)` 透传至各 broker 的 producer。
  装配层（`zephyr.trading` 运行时装配批）再把 `PositionReconciler.handle_execution_report` 注册为 listener
  ——这样 FF-12 天然满足宪法 §9.3"事件触发，禁 cron/Timer/sleep-loop"。
- 本车道已在消费侧就绪：`position_reconciler` 现为 fail-closed 事件入口 + `escalation_sink` 注入位（§4）。

## 3. 附带发现：对账域**六件实现并存、六件全部零程序消费**（BRK-016 的真正病形）

| 件 | 自称 | 实测消费方 | 判定 |
|---|---|---|---|
| `src/zephyr/position/position_reconciler.py` | MATURITY=production | 仅 `tests/rollback/`、`tests/e/` | 盘中事件入口，**保留为权威事件侧**（本车道已加严） |
| `src/zephyr/ex_core/position_reconciler.py` | — | `eod_reconciliation.py`、`trading/recon_runner.py`、`risk_layer_orchestrator.py`、`reporting/attribution_result_store.py` | **真权威比较器**（有入度） |
| `src/zephyr/ex_core/eod_reconciliation.py` | CONSUMERS="运行时装配批(盘后 15:30)" | **零 import**（aspirational 承诺） | 待装配批落地，否则蓝图↔代码漂移 |
| `src/zephyr/trading/recon_runner.py`（MOD-TRADING-007） | production | CONSUMERS="57号文日循环SOP（人工）" = 零程序调用 | 三层 L1/L2/L3 + 治理库 `reconciliation_differences` 落表，**日终权威件，缺调度** |
| `src/zephyr/trading/three_way_reconciliation.py`（ThreeWayReconEngine） | production | 仅被 `eod_reconciliation.py` 引用（后者又零消费） | 与 recon_runner 职责重叠，须并表 |
| `src/zephyr/orchestrator/execution/reconciliation_loop.py` | MATURITY=production，GOMAP 归 `families.L5_selfheal` | 零 | **普查误归因**：它调和的是编排器自完整性 5 不变量（契约校验和/熔断器态/CBAC 矩阵/任务卡态机/DLQ 数），与 FF-11→FF-12 成交对账**无关**；若照 BRK-017 字面"接上成交数据"，就是假闭环 |

→ 提请总包按 R-002 同原则（merge 不 ack）裁：**盘中=position 事件入口（薄适配复用 ex_core 比较器）+ 日终=recon_runner**，
`eod_reconciliation`/`three_way_reconciliation` 归入 recon_runner 或显式标 aspirational；
GOMAP 把 `reconciliation_loop` 从 `L5_selfheal` 摘出（它不是自愈对账）。
**tasks.yaml 归 residG 单一写者**，本车道不代写，片段待 G1 落地后另批提交。

## 4. 本车道实际改动（不越权，全部在自己可写域）

| 件 | 改动 | 能红证据 |
|---|---|---|
| `src/zephyr/position/position_reconciler.py` | 事件入口改 **Fail-Closed**：缺键/值为 None/非 dict/双空无出处 → `status=input_unavailable, match=False, rule_id=POS-RECON-002, escalate=True`（旧实现 `.get(k, {})` 会把"两侧都瞎"判成 `match=True` 的假对账）；新增 `escalation_sink` 注入位 + `unavailable_count/mismatch_count`；`reconcile()` 纯比较器语义不变 | 变异测试：把入口改回 `.get(k,{})` → **4 failed / 30 passed, rc=1** |
| `src/zephyr/orchestrator/execution/reconciliation_loop.py` | 未观测不变量一律判不通过（旧 `states.get(name, True)` = **恒真门**：不传 states 时 5 项全绿）；新增 `unobserved` 列表区分"查了且坏"与"根本没查"；值非 bool 判不通过；`datetime.now(UTC)` → `now_utc()`；删无引用的 `_interval_s`；补齐 CONSUMERS/INVARIANTS/ERROR_CONTRACT/TESTS 头 | 变异测试：把 `ok=False` 改回 `ok=True` → **2 failed / 22 passed, rc=1** |
| `tests/rollback/test_rollback_position_reconciler.py` | +11 个 fail-closed/升级钉（`TestHandleExecutionReportFailClosed`） | 全绿 |
| `tests/trading/test_reconciliation_loop.py` | 2 个恒真断言按加严改写 + 2 个新钉（未观测/非 bool） | 全绿 |

两次变异均按字节还原（`read_bytes`/`write_bytes` + sha256 校验），还原后 88 passed。
`git diff --numstat` 与 `--ignore-cr-at-eol` 计数一致 → **无 CRLF 换行污染**（R-008 教训已避）。

## 5. 六向台账

见 `stages/FF-12_recon_feedback/ledger_sixway.md`（本车道交工格式）。
