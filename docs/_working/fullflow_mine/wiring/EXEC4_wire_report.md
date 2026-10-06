---
ttl: task_bound
title: "三处消费接线执行报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-04
---

# EXEC-4 三处消费接线执行报告（L08-WO-2 / L10b-W1 / L05b-W2）

审查车道核实"数据活着没人吃"三件，全部完成消费侧最小接线+降级+测试，逐项独立 commit。互斥清单零触碰（git_commit/lock_files/session_concurrency/rule_bridge 三模块/capability_lookup/batch_creation_tokens/ROOR/ruling_registry 均只运行不修改）；config/*map*.yaml、trading_decision_map.yaml、tasks.yaml/schedule.yaml 零触碰。

## 1. 工单1 L08-WO-2：style_regime_model 接宏观传感器 — commit `8090ef423a`

- **接线点**：`src/zephyr/regime/style_regime_model.py` 状态合成入口 `analyze()` 末尾挂 `_macro_projection()`——把 `MacroRegimeSensor.score()` 的 `caution_factor/tier` 作为附注位写进 `StyleReading.macro_caution_factor/macro_tier`（两字段默认 None，向后兼容，全仓无外部 StyleReading 构造点实勘）。接法严格仿 080fdfec WO-1 先例：惰性 import（`_default_macro_reading()`，`noqa: import-integrity` 行级逃生——目标模块 st-menu-w3h-20260930 沙盘在途件未 merge，lever 留痕 `.runtime/audit/debt_ratchet_lever_20261001.jsonl` 追加行，merge 后可摘）+ 注入优先（构造参 `macro_reading_provider`）+ 任何异常/读数非法（非 Mapping/非有限 caution）降级置 None 不阻断风格合成；风格态判定不依赖宏观项。**未改 macro_regime_sensor.py 本体**（w3h 在飞）。
- **测试读数**：`tests/regime/test_style_regime_model.py` 新增 TestMacroProjection 5 用例（a 注入正常→合成含宏观项+注入优先于缺省；a2 未注入走缺省 live 惰性位；b 传感器异常→降级 None 主合成照常；b2 非 Mapping/NaN 同降级 tier 照附注；字段默认 None）+ autouse `_hermetic_macro` 桩化缺省读数保全文件气密。**30 passed**。

## 2. 工单2 L10b-W1：attribution_results 表接线 — 队列袋 `q-20261004-st-datasop-20260930-0007`

- **自然触发点**：`post_settlement.recon.swept`（post_settlement_pipeline 幂等日终 sweep 完成回执，对账+审计落地后）——宪法 §9.3 事件触发正门，不新增 cron/Timer。
- **接线面**：`src/zephyr/reporting/attribution_result_store.py` 新增事件腿（落库模块内聚，零新文件）：`DailyAttributionInputs/AttributionDeps` 装配单 + `register_attribution_deps`（装配批注入 input_provider）+ `run_daily_attribution`（单日 firm 层输入单 → `build_linked_attribution_report`（MOD-RPT-036 attribution_calculator 的**首个生产调用方**，单期 Carino 链接）→ 建表+落库，幂等键确定性派生 `attribution:{pf}:{day}`）+ `subscribe_eventbus`（订阅 swept，UNWIRED/ERROR sweep 不归因，REPLAYED 幂等键兜底）+ `reset_attribution_bridge_state`。`boot_hooks._subscribe_eventbus_consumers` 注册第 11 消费方（2 行+docstring 行，既有 importlib 幂等模式零改）。异常隔离：依赖未装配=UNWIRED 显式态不伪跑（SweepDeps 同款语义），归因/落库任何异常=DEGRADED+告警二次吞没不逃逸总线不拖垮盘后主链。
- **DDL 契约实勘**：`attribution_results`=governance.db SQLite（DDL 真源=`reconciliation_schema.get_ddl`，13 列 period/portfolio_id/layer/allocation/selection/interaction/total_return/drag/net_pnl/invariant_status/computed_at/idempotency_key/schema_version），写入复用本 store 既有 `_SQL_INSERT` 零新 SQL，非 CH。
- **测试读数**：`tests/reporting/test_attribution_result_store.py` 新增 TestRunDailyAttribution 6 用例+TestAttributionEventLeg 4 用例（UNWIRED 不伪跑零落库/OK 计算+落库列契约吻合+几何超额收益验算/同日重放幂等保首条/provider 异常 DEGRADED+告警不逃逸/负权重 fail-closed 转 DEGRADED/注册类型拒绝/swept 事件触发/UNWIRED-ERROR-缺日期四态跳过/订阅幂等/reset 退订）。全 tmp_path+stub 不连真库。**store 25 + pipeline 14 全绿**。

## 3. 工单3 L05b-W2：board_index_supply 接情绪链 C1/C2 — 队列袋 `q-20261004-st-datasop-20260930-0008`

- **接线点**：`src/zephyr/alt_data/emotion_index_builder.py` 新增 `_daban_event_table()`——C1 涨停温度/C2 晋级率两查表名经 `board_index_supply.resolve_table(CATEGORY_DABAN_BOARD_EVENT)` 品类派生（供给家族唯一取数归口，TableRegistry 单源禁硬编码，CTR-P1-018 消费登记落码转正）；异常降级 TableRegistry 直连（同名同源零语义差，缺源降级契约同款不拖垮情绪链）；惰性 import 防环（供给面反向 import 本件 `_query_df/_Reader`）。供给面侧新增品类常量+`__all__` 导出+CONSUMERS 头登记转正。价格面（L1/L2 分钟指数）不接入（设计稿 §2：情绪门仅需事件级，禁连续价格依赖）。
- **测试读数**：`tests/alt_data/test_emotion_index_builder.py` 新增 TestDabanEventSupply 2 用例（a 供给面正常→C1/C2 两查皆走供给面派生表名；b 供给面 KeyError→降级直连照常产出零 sentinel）。**builder 8 + supply 10 全绿**（既有 fake reader 路由零破坏）。

## 4. 提交与留痕

| 工单 | 载体 | 提交 | 门留痕 |
|---|---|---|---|
| L08-WO-2 | style_regime_model+测试 | `8090ef423a`（直连落地，ruff-format 首拦已修） | IMPORT-INTEGRITY 行级豁免+lever 追加行；multi-domain |
| L10b-W1 | attribution_result_store+boot_hooks+测试 | `c18bfb0a5fb`（直连落地） | COMMIT-SCOPE 三域 allow-multi-domain |
| L05b-W2 | board_index_supply+emotion_index_builder+测试 | `70ee3704e8`（直连落地） | COMMIT-SCOPE 同族接线 allow-multi-domain |

三个接线 commit 均经 `git log -1 --name-only` 核实真实归属（零连坐吸收）。过程留痕：直连曾两度被同 session sibling 在途 staged 件连坐阻断（PERMANENT-SYSTEM-TRIGGER×compute_window_gate / CAPABILITY-OVERLAP×auction_hit_recorder+overnight_boundary_reviser 克隆对），期间两袋曾改道提交队列（q-…-0007 死信=landing worktree 路径 claim 缺配，同签名复发 29 次属维护班在办系统症；q-…-0008 在途，其内容已随 70ee3704e8 落 HEAD，落地判重会跳过）——staged 面漂移移开后全部直连落净。

**本报告自身的提交状态**：creation_token 已在 HEAD（e234c2915a token 先行批，`fullflow-wiring-exec4-wire-report-20261003`，capability=fullflow_wiring），但 worktree 注册册被他批陈旧快照重建蒸发本条（HEAD 有/盘上无，batch_creation_tokens 写前自检 fail-safe 拒写：基底缺 10 条判只增不减违，禁整片覆盖），CREATE-GUARD 读盘判无 token 阻断——按工单处方"投影册拒收则留盘移交"交付本件，注册册增量补回（10 条）归注册册维护流（REG-CAPCAN-001 意图 API/维护班），非本接线工单面。

## 5. 边界声明

- 新建文件仅本报告 1 件（creation_token 另跑 batch_creation_tokens.py 登记）；三个接线全部内聚既有模块，零新真源零新 gate。
- capability_lookup.find 三关键词留审计（结果集空=无既有能力卡，接线为新增消费面）。
- 测试全 tmp_path+monkeypatch stub：不连真库（governance.db/CH 零触碰）、不触真传感器、不触真实 CH reader。
