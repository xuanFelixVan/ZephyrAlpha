---
ttl: task_bound
completes_when: 总包/Owner 裁 req_land2_01（契约 SSOT 受保护路径）后由下一腿按本件配方落地 R-014
---

# 落地接力腿 st-ff-land2-20260918 · 接力清单与待裁项（逐 T）

> 本件同时充当 `adjudications/req_land2_01.md`（同内容两份，便于 ledger 待裁表引用）。

## T1 · G1 execution_report 四件套原子落地 —— **已落（本批）**

`src/zephyr/ex_core/execution_report_producer.py`（新）+ `tests/ex_core/test_execution_report_producer.py`（新）
+ `src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py`（四接线方法，原仅 unstaged）
+ `src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py`（原 staged import）同批入面。

三件套已齐（主仓跑，非 worktree-only）：
- `batch_creation_tokens.py --prefix src/zephyr/ex_core/execution_report_producer.py`
  → 载体 `capability_canonical_file_registry.yaml` **同批进 --files**（R-017②）
- `apply_depgraph.py --add-design-node … MOD-L06-001-ERP D_EX_CORE --granularity file`（架构库直写，node_id=14830697）
- `add_module_translation.py`（→ `module_translation_registry.yaml` 同批）

落地后核验（处方 §G1 两条，本腿实测均非空）：

```bash
git show <sha>:src/zephyr/ex_core/adapters/qmt_file_bridge_integration.py | grep -c execution_report_producer
git ls-tree <sha> src/zephyr/ex_core/execution_report_producer.py src/zephyr/ex_core/adapters/qmt_file_bridge_broker.py
```

## T2 · R-014 滑点伪测量 —— **未落，卡在 Owner 受保护路径（req_land2_01）**

### 待裁 req_land2_01：`architecture_model/contracts/cross_layer_contracts.yaml` 是 PROTECTED-PATHS

- 现象（原文）：`[PROTECTED-PATHS] staged files contain protected paths (1 hit(s)):
  D:\ZephyrAlpha\architecture_model\contracts\cross_layer_contracts.yaml (重大修改须 Owner 审批).
  逃生通道: 受保护路径须 Owner 审批（无 CLI 逃生旗）`
- 冲突：R-014 裁定 `slippage_bps` 置 NULL，而该字段由 CTR-P1-007 **codegen SSOT** 定义
  （`architecture_model/contracts/cross_layer_contracts.yaml:806` = `type: float, required: true`）。
  只改生成件 = 违反 RULE-SSOT 且下次 codegen 静默覆盖；故 NULL 方案**必须**动受保护 YAML。
- 选项：①Owner 批 YAML 一行改 `type: "Optional[float]", required: false`（本腿已全套验通，见下"配方"）；
  ②改判为不改契约、生产者侧对零成交终态**不落行**（丢撤单证据，与本仓"台账可审计"取向相悖）；
  ③改判为 `slippage_bps` 保留数值但新增"有效性"旁证列（= 扩契约字段，改动更大，同样触 SSOT）。
- 建议：**①**（配方已实测：85 passed + 变异 4 红 + 生产表 ALTER 双向验证）。
- 影响面：CTR-P1-007 消费方 = TCA/归因（FF-02/FF-06 回流入口）、`execution_report_contract` 校验口、
  `c1_market.execution_report` 列类型。

### 已实测的完整配方（下一腿逐字重放即可，勿重写）

改 5 件 + 3 处测试钉：

1. `architecture_model/contracts/cross_layer_contracts.yaml:806`
   `- {name: slippage_bps, type: float, required: true, description: "滑点（基点）"}`
   → `type: "Optional[float]", required: false`，描述补"null=无有效执行样本"
2. `python scripts/governance/d5_architecture/generators/generate_contracts.py --contract CTR-P1-007`
   → 生成件字段变 `slippage_bps: float | None = None`（字段序按必填/可空分组重排，全部调用点走关键字，零位置构造）
   注：生成器会额外插 `from typing import Optional` 而 HEAD 版无此行 → 按字节删该行使净 diff 只剩字段行
3. `src/zephyr/ex_core/execution_report.py::_signed_slippage_bps` 增第 4 参 `actual_quantity: int`，
   体首 `if actual_quantity <= 0: return None`（在 `intended_price<=0` 守卫之前）；调用点传 `actual_qty`；
   `[INVARIANTS]` 头补 NULL 语义
4. `src/zephyr/shared/contracts/execution_report_contract.py`：入站校验**加严**——
   `slippage_bps is None` 仅当 `actual_quantity==0` 合法，有成交量缺滑点 `_fail("有成交量时 slippage_bps 不得为 None")`；
   `execution_report_from_payload` 的 `_FLOAT_FIELDS` 分支补 `value is None → 原样透传`（禁顶成 0.0）
5. `schemas/categories/intraday/market_execution_report.py`：`slippage_bps Float64` → `Nullable(Float64)`；
   生产表 `ALTER TABLE c1_market.execution_report MODIFY COLUMN slippage_bps Nullable(Float64)`
6. 生产端 `_to_tsv_row`：`slippage_bps` 单元 `"\N" if value is None else f"{float(value):.6f}"`
   （Python 源里必须写 `"\\N"`，单反斜杠 `\N` 是 named-unicode 转义 → SyntaxError，本腿踩过）；
   `ProducerStats` 增 `emitted_filled/emitted_unfilled`（撤单与 FILLED 分开计数，此件**本批已落**，不依赖 NULL）

测试钉：`test_zero_fill_has_no_slippage_sample`（断言 `is None`）、`test_one_lot_fill_still_measures_slippage`（反向钉）、
契约层 `TestSlippageNullSemantics`（零成交过校验 / 有量缺滑点拒 / payload None 往返恒等）、
producer 层 `row["slippage_bps"] == r"\N"`。

**能红证据（本腿亲跑）**：把守卫改成 `actual_quantity < 0`（等价旧算法）→
`4 failed, 81 passed`（`test_zero_fill_has_no_slippage_sample` / `TestSlippageNullSemantics` 两钉 /
`test_cancelled_zero_fill_lands_one_row`）；按字节还原 sha256 一致后 85 passed。

**生产表副作用（重要）**：本腿对 `c1_market.execution_report.slippage_bps` 执行过
`MODIFY COLUMN → Nullable(Float64)`（元数据变更、原值保留、可逆），确认漂移不存在后**已改回 `Float64`**，
现列类型与 DDL-as-code 一致。备份：`.runtime/tmp/ff-land2/execution_report_backup_before_alter.txt`
（唯一行 `f216058c-…  510300.SH  actual=0  slippage_bps=-10000.0`）。
该行 -10000.0 污染值的清理属 DELETE 变更 → **本腿未自行删**，交总包/Owner 择一：
①按上配方落地后由 ReplacingMergeTree 同键替换自愈（需该 order_id 再被观测一次），
②或授权 `ALTER TABLE … DELETE WHERE order_id='f216058c-6df6-4752-8eb3-bb0854bf5430'`（已备份可逆）。

## T3 · pf_alloc 8 红 —— **未落**（腿时预算耗尽，staged 原样未动）

已复核实测基线（本腿未重跑 tests/pf_alloc，沿用 z-land 实测）：382 passed / 8 failed。
归因未完成 → **禁带红落地**，故危机闸三批整组留 staged。
`scripts/backtest/crisis_drill_monthly.py`（770 行自身债）本腿未触碰，NO-HIGH-COMPLEXITY 预裁 R-K1 仍待执行。

## T4 · 幂等键三件套 —— **未落**，且**发现新阻塞**（须下一腿先归因）

- 三件套文件仍 staged 未提交：`src/zephyr/shared/infra/idempotency.py`、
  `src/zephyr/ex_core/adapters/miniqmt_broker.py`、`src/zephyr/ex_core/order_manager.py` + 三测试。
- 本腿跑 `tests/ex_core` 全目录检出 **1304 passed / 4 failed**，4 红全在
  `tests/ex_core/test_miniqmt_broker.py`：`test_account_passed_to_xttrader`（order_stock 调用 0 次）、
  `test_order_side_mapping`（`buy_call.args` NoneType）、`test_price_cage_clamp_in_submit`
  （夹到 10.80 而非 10.71）、`test_query_order_int_order_id_match`（`decimal.ConversionSyntax`）。
  四症同指 **staged 的 miniqmt_broker.py 提交路径改写后未与既有测试对齐**（属 R-016 三分法①候选，
  也可能被 ③环境性 xtquant 缺失放大）→ 下一腿 MUST 先独立归因这 4 红再落 T4，禁与 T4 同批带红提交。
- TDM：`config/trading_decision_map.yaml:2399 node_id: TDM-E-L4-10 → module_ref: src/zephyr/ex_core/order_manager.py`
  → 落 T4 时须同批给该节点补 `note_confirmed: 2026-09-18`（R-012 已下放，本腿未消耗该额度）。

## T5 · 战役真源 docs（33 件新 .md） —— **未落**

`docs/_working/fullflow_campaign/**` 与 `docs/_working/n5_closure/` 新 .md 全部缺 creation_token，
须逐件 `batch_creation_tokens.py --prefix <完整路径>`（单值 argparse）。
`sim-memo-202609.json` 已按 DIRECTORY-CONTRACT 永久剔除（勿加回）。

## T6 · 其余 260 件 —— **未落**（清单 `.runtime/tmp/ff-land/rest.txt` 原样）

## 本腿提交实况

计划 ≤5 笔，实际 **1 笔**（第 2 笔起撞上受保护路径与 4 红归因需求，未强行入队以免制造死信）。
未落清单与原因如上；`.runtime/tmp/ff-land2/patch_g4.py`+`patch_g4_tests.py`+`patch_g4_revert.py`
是本腿用过的字节级补丁器（有 TTL，配方本文已自足）。
