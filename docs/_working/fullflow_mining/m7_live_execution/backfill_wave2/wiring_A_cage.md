---
ttl: task_bound
volume: wiring_A_cage
session: st-ailayer-final-20260924
creation_token: bf6-cage-wiring-w3b-20260926
---

# W3-B 施工记录：案 BF-6 价格笼子（供数＋UNKNOWN 告警＋opt-in 执法力度）

> 照裁法＝94 册 §二 BF-6 那一行：做供数（prev_close/盘口透传）＋UNKNOWN 分支打告警；
> 执法力度走 opt-in 旗标、出厂默认不翻。本车道未改判据数值、未自赋裁定号。

## 〇、病因自验（本车道实测，不沿用前棒账面）

| 主张 | 实测证据 | 结论 |
|---|---|---|
| 两条腿都在调 `check_price_cage` | `src/zephyr/ex_core/adapters/miniqmt_broker.py:814` `_apply_price_cage_locked`（改前 L836 调用点）；`src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py:536`（改前 submit_order 内） | 成立（不是"未接线"） |
| 唯一下单调用方不喂基准价 | `src/zephyr/ex_core/order_manager.py:345` `broker.submit_order(order)` 单参；miniqmt 腿形参 `order_book/prev_close` 默认 None；文件桥腿**根本没有**基准价形参（文件头注自陈"无实时盘口，预校验降级为无盘口模式"） | 成立 |
| 恒 UNKNOWN＝恒放行 | `src/zephyr/ex_core/price_cage.py:186-195` 无基准价 ⇒ `CageStatus.UNKNOWN` + `clamped_price=limit_price`；两腿对 UNKNOWN 的一致处置＝原价继续 | 成立＝假硬约束 |
| 正确用法已有先例 | `src/zephyr/signal_ashare/tradability_preflight.py:191` `_cage_suggestion` 用 `snap.prev_close` 喂 `check_price_cage` | 成立（本案照此供数口径，不另起方向） |
| 文件桥腿 UNKNOWN 连告警都没有 | 改前该分支只在 CLAMPED 时 `warning`，UNKNOWN 静默通过 | 成立 |
| 红测复现 | 新增 `tests/ex_core/test_price_cage_bf6_wiring.py::TestSupplyMakesCageDecide::test_cage_port_without_supply_is_always_unknown`：委托价 99.00（荒谬越界）在无基准价下仍 `UNKNOWN`+原价放行 | 病因钉死（此断言在改动前也成立，故非"我造的稻草人"） |

## 一、改了什么（执法力度未翻出厂默认）

1. **判据中枢单点化**（防 BF-7 式"加一条只对一腿"）——`src/zephyr/ex_core/price_cage.py` 新增：
   - `CageBaseQuote`（四基准价束）＋ `coerce_cage_quote`（认既有真源字段名：`ask1|ask_price|ask_prices`、`bid1|bid_price|bid_prices`、`last_price`、`prev_close|last_close`，**不新建取数通道**）；
   - `fetch_cage_quote`（source＝callable 或既有 provider 的 `get_quote`/`get_order_book`；取数失败/形态不认识一律 warn＋回落现状判定，绝不放大成下单异常）；
   - `decide_cage_for_limit_order(...)`＝供数→判定→执法力度三段合一，**两腿共用同一实现**；
   - 两枚 opt-in 旗标常量 `CAGE_BASE_SUPPLY_FLAG="ex_core_price_cage_base_supply"`／`CAGE_UNKNOWN_REJECT_FLAG="ex_core_price_cage_unknown_reject"`，读方 `_flag_on()` 走 `zephyr.shared.foundation.flags`（未注册＝缺省 False＝现状；旗标层故障亦回落 False）；
   - `UNKNOWN_WARNING_TEMPLATE`＝两腿同一告警文案（防"一腿有告警一腿静默"再分叉）。
2. **miniqmt 腿**——`src/zephyr/ex_core/adapters/miniqmt_broker.py`：`__init__` 加 `self._cage_quote_source=None`；新增 `attach_cage_quote_source()`；`_apply_price_cage_locked` 改走 `decide_cage_for_limit_order`（调用点自带盘口/昨收**优先**，供数端口只在旗标 ON 且调用点无数据时补供）；UNKNOWN 告警文案与 CLAMPED 日志文案**逐字节未改**；enforce 态抛既有错误契约 `MiniQmtBrokerError`（在 `_lock` 内、xttrader 调用之前 ⇒ 拒单不可能触达券商）。
3. **文件桥腿**——`src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py`：`__init__` 加供数端口位；新增 `attach_cage_quote_source()`；`submit_order` 内笼子段改走同一判据中枢，**补上改前完全缺失的 UNKNOWN 告警**；enforce 态抛 `QmtFileBridgeError`，抛点在 `_append_instruction`（含 HTTP 快路径）与本地缓存之前 ⇒ 指令不进桥、订单不置 SUBMITTED。
4. **红测册**——新建 `tests/ex_core/test_price_cage_bf6_wiring.py`（16 例，三枚判据分组）。

未改：`order_manager.py`（保持 `BrokerInterface` 单参签名，避免波及 okx 等其余 broker 腿）、`check_price_cage` 本体、任何判据阈值、任何既有测试断言。

## 二、三枚红测各自结论

| 判据 | 用例 | 结论 |
|---|---|---|
| ①供数后笼子真能判出 PASS/FAIL（不再恒 UNKNOWN） | `TestSupplyMakesCageDecide::test_supply_on_produces_in_cage_and_clamped`（同价格族判出 IN_CAGE/CLAMPED，买基准=卖一 10.00、卖基准=买一 9.90）、`::test_file_bridge_leg_writes_clamped_price_after_supply`（真实调用链写出行价＝夹边价 10.2）、`::test_coercion_accepts_existing_file_bridge_snapshot`（消费既有 `QuoteSnapshot` 字段名，含 `last_close`＝昨收） | **达标** |
| ②enforce 态打开会拒单（测试内开关，不改出厂默认） | `TestUnknownRejectEnforce::test_file_bridge_rejects_and_writes_nothing`（抛 `QmtFileBridgeError`＋指令文件零行＋状态非 SUBMITTED）、`::test_miniqmt_leg_rejects_on_unknown`、`::test_file_bridge_rejects_even_when_supply_on_but_no_data`（两旗标正交）、`::test_enforce_only_bites_unknown_not_in_cage`（不扩大打击面：合规放行/越界仍夹边不废单）、`::test_market_orders_never_rejected`（市价单豁免） | **达标（只实现不启用）** |
| ③旗标关闭＝与改动前逐字节一致 | `TestFlagsOffIsByteIdentical::test_factory_flags_are_off`、`::test_file_bridge_price_and_line_unchanged`（指令行逐字节比对 `"…,100,limit,4.5"`）、`::test_file_bridge_no_supply_when_flag_off`（spy 供数源**零调用**＝真 opt-in）、`::test_miniqmt_call_site_path_unchanged`（夹边结果＋原日志文案全等）、`::test_miniqmt_no_supply_when_flag_off`、`::test_cage_pure_function_semantics_untouched` | **达标**，唯一允许增量＝两腿 UNKNOWN 各多一行 WARNING（本案第 2 条要求的纯披露，不改判定/不改价/不改状态机）。下单链之外另有一条装配期 INFO（`attach_cage_quote_source` 挂载时打印），不在下单路径上，故不构成行为差异 |

红测全绿：新册 `16 tests collected` 全通过。同批复跑既有相关面（**未修改任何一处既有断言**）：
`tests/ex_core/test_price_cage.py`＋`test_miniqmt_broker.py`＋`adapters/test_qmt_file_bridge_broker.py`＋`test_pricing_policy.py`＝75 例（1 xfail 原样保留）；
`tests/ex_core` 全域＝1333 例 rc=0；`tests/ex_sor`（`rl_exec_boundary` 是 price_cage 声明消费方）＝609 例 rc=0；
`tests/signal_ashare/test_tradability_preflight.py`（先例用法的供数口径件）rc=0。
判据自检：`git diff HEAD -- src/zephyr/ex_core/price_cage.py | grep -E "^[+-].*(0\.02|0\.05|0\.10)"` → **零命中**（阈值一字未动）。

## 三、待登项（交总筹单点落地，本车道零提交零入队）

1. **旗标出厂值**（禁本车道自改 `config/flags.yaml`：他在途热件）——请随袋新增两键，**默认必须 false**：
   ```yaml
   ex_core_price_cage_base_supply:
     enabled: false
     description: "案 BF-6 供数：喂 prev_close/盘口基准价给价格笼子（ON 会让沉睡的夹边分支在真实路径咬合）"
   ex_core_price_cage_unknown_reject:
     enabled: false
     description: "案 BF-6 enforce：连续竞价限价单 UNKNOWN=拒单（出厂翻转=Owner 门位）"
   ```
2. **待接线一行**（装配面非本车道所有；两腿端口已就绪，不接＝端口恒空＝现状）：
   - 文件桥：`QmtFileBridgeAssembly` 装配后 `broker.attach_cage_quote_source(QmtFileBridgeQuoteProvider(env=env))`（`src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py:141` 循环体内，`QmtFileBridgeQuoteProvider` 读同一份 quote CSV，既有通道）；
   - miniqmt：构造 `MiniQmtBroker` 处（`src/zephyr/frontend/dashboard/components/position_monitor.py:365` 之外的实盘/模拟装配点）`broker.attach_cage_quote_source(<MiniQmtQuoteProvider 实例>)`——该 provider 的 `get_order_book` 已含五档与 `last_price`。
3. **depgraph/翻译册/算法流册**：新建测试模块 `tests.ex_core.test_price_cage_bf6_wiring`（tests 免 creation_token，但请按需补翻译覆盖登记）；`price_cage`/两腿的 `[CONSUMERS]`/`[INVARIANTS]`/`[TESTS]` 头注已就地更新；`price_cage` 新增 10 个公开符号 ⇒ 若 `docs/03_modules/_domain_execution_core/algo_flow/price_cage.yaml` 是生成物，请随袋 `--force` 重建（本车道未改它，避免踩在途热件）；请 `generate_project_depgraph.py --force` 复核（本车道未改名、未新建 .py 生产模块）。另：本案未动 `40_execution_broker.md §决策⑭` 的判据（该 MODIFY-GUARD 只约束幅度/回退链/夹边语义，全部原样）。
4. **enforce 启用前置（新发现，非裁已决项）**：本仓**没有**"连续竞价/集合竞价/临时停牌"相位判据真源（`src/zephyr/data/implementations/miniqmt_provider.py:3434` 的集合竞价快照是 error 占位，`qmt_bridge_provider.py:345` 是含集合竞价的粗判），故 enforce 现仅按 `OrderType.LIMIT` 判——9:15-9:25、14:57-15:00、临停窗口的合法委托会被误拒。旗标恒 OFF 无现实风险；**翻转前必须先补相位豁免判别器**（已写进代码注释与 pending_rulings.md 一行）。

## 四、门位与红线自查

- 零真实交易动作：测试不 connect 券商、文件桥 `http_port=None` 显式禁 HTTP 快路径、miniqmt 腿只直调私有判定件；xtquant/xttrader 活体路径未被触及。
- "真实路径行为变化"全部停在 opt-in 态：供数（会激活沉睡的夹边分支）与 enforce（拒单）两旗标默认 OFF，且红测③钉了 spy 零调用。
- 未碰禁触清单：`order_manager.py`/`config/flags.yaml`/`catalogs/**`/`src/zephyr/data/**`/`pf_alloc`/`comparator`/`shared/vocab`/`settlement_reconciliation.py`/两个 `position_reconciler.py`/`trading_decision_map.yaml`/`run_post_settlement*.py`/`start_paper_session.py` 全零改动。
- 未自赋裁定号、未写 Owner 署名、未改任何判据阈值。

## 五、复核命令

```bash
cd /d/ZephyrAlpha/.worktrees/st-ailayer-final-20260924
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:$PATH"
PYTHONPATH=src python -m pytest tests/ex_core/test_price_cage_bf6_wiring.py \
  tests/ex_core/test_price_cage.py tests/ex_core/test_miniqmt_broker.py \
  tests/ex_core/adapters/test_qmt_file_bridge_broker.py \
  -p no:cacheprovider -c py.ini -q --timeout=300
# 病因面自检（应只见 UNKNOWN 相关新增行，判据数值零变更）
git diff --stat -- src/zephyr/ex_core tests/ex_core
git diff HEAD -- src/zephyr/ex_core/price_cage.py | grep -E "^[+-].*(0\.02|0\.05|0\.10)"
```
期望：**第二条 grep 零命中**（新增块里不出现任何笼子幅度/兜底阈值字面量；`Decimal(str(...))` 类解析语句不计入）。

## 六、三态结论

**完工**（今夜最小面全部达标）。残余＝三件待登项（旗标出厂值／两腿装配一行／enforce 前置的相位判别器），其中第三件是 enforce 的启用前置而非本案交付缺口，**不影响本案 BF-6 今夜判据达标**。
