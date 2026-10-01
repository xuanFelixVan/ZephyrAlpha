---
ttl: task_bound
title: "WO-1 MAC传感器下游接线执行报告"
owner: st-datasop-20260930
language: zh
status: active
version: "1.0.0"
date: 2026-10-01
---

# WO-1 执行报告：MacroRegimeSensor.score() 接第一个消费者（E3）

工单真源：`docs/_working/fullflow_mine/lanes/L08_macro_commodity.md` §④ 工单 WO-1（P0）。
commit：`080fdfec`（080fdfeca39822886872fac6a83e653906b6f060，3 文件，git log -1 --name-only 已核实归属无连坐）。

## 1. 改动点（函数级 old→new）

### 1.1 src/zephyr/plan_engine/llm_premarket_analysis.py（消费侧本体）

| 位置 | old→new |
|---|---|
| `PremarketInjections`（注入契约区） | 新增字段 `macro_regime_reading: Any = None`（MacroRegimeSensor.score() 输出 dict；None=缺省走 live 读数）——同 BS-005 注入先例 |
| 新增模块函数 `_default_macro_reading()` | 惰性导入传感器→`MacroRegimeSensor().score()`（as_of=None 现值面=传感器不变量②钦定的盘前判定面）；异常透传（传感器 ERROR_CONTRACT：调用方自行降级）；测试经 monkeypatch 本函数注入桩 |
| 新增常量 `_MACRO_TIERS` / `_MACRO_FAMILY_NOTE` | 档位合法枚举 frozenset{supportive,neutral,cautious}（对齐 CAUTION_TIERS tier 值；no_data 按降级）+ 注入提示词语义注记（档位说明随 families JSON 进盘前提示词） |
| 新增 `PremarketPackager._build_macro_regime_family(ledger, trace)` | 宏观敏感度族打包：注入优先→缺省 live 读数（仅 ch_client=None 生产面发起，ch_client 注入=离线/测试态跳过 `skipped:not_injected`，零 CH 依赖）；PIT：generated_at>cutoff 拒入（degraded:pit_rejected+rejected 留痕）；tier 非法/caution 非有限数→degraded:no_data；任何异常→degraded:sensor_error 跳过不抛错（复杂度 ≤15、参数 3 个） |
| `PremarketPackager.build()` builders 元组 | 追加 `("macro_regime", ...)` 第 8 族（复用既有单族 fail-open 包装） |
| 文档面 | [DEPENDENCIES]/[ERROR_CONTRACT]/模块 docstring/ALGO_FLOW/build() docstring/PremarketPackage 注释同步"七族+宏观敏感度族"；PROMPT_VERSION 不动（提示词模板文本零改动，families JSON=数据非模板） |
| 门禁被动修复（gate 硬阻断驱动） | ①RUFF-PRECLEAN I001×3：三文件 import 排序机械修复；②hook gate-any-abuse ANY-1×5：`_safe_float/_safe_int/_parse_date/_parse_ts/_coerce_str_list` 参数裸 `Any`→`object`（仅注解，零运行时变更）；③IMPORT-INTEGRITY：传感器模块=他会话 st-menu-w3h-20260930 沙盘在途件（盘上已存在未 merge），import 行加 `# noqa: import-integrity  他会话沙盘在途件未merge`（门内既有行级逃生，先例=fcntl/tqcenter），**其 merge 后标记可摘**；留痕 `.runtime/audit/debt_ratchet_lever_20261001.jsonl` |

### 1.2 测试（两处既有断言随新族键机械适配 + 新增 5 用例）

- `tests/plan_engine/test_llm_premarket_analysis.py`：families 集断言 +`macro_regime` 键；新增 `_macro_reading()` 桩构造器与 5 用例（见 §2）。
- `tests/integration/test_phase2_premarket_intraday_e2e.py`：`test_chain_b_premarket_full_chain` families 集断言同步（+键+`skipped:not_injected` 断言），其余零改动。

## 2. 测试读数

| 用例 | 读数 |
|---|---|
| WO-1a 注入读数（`test_wo1_macro_injected_reading_appears_in_package_and_prompt`） | caution_factor=0.9/tier=neutral/weather_score=55.0 入包+入提示词（`"caution_factor": 0.9` 字面命中）；input_hash 同注入稳定、变档位敏感 |
| live 面（`test_wo1_macro_live_sensor_called_in_live_mode`） | ch_client=None（生产 daily_loop 形态）→传感器被调用 status=ok source=live tier=cautious；ch_client 注入=离线态 `skipped:not_injected` 不连真库 |
| WO-1b 传感器异常（`test_wo1_macro_sensor_error_degrades_run_still_succeeds`） | sensor 抛 RuntimeError→族 degraded:sensor_error（fields 全 None）不抛错；`run_llm_analysis` 端到端照常 STATUS_SUCCESS 产出分析 |
| PIT 拒入（`test_wo1_macro_injected_after_cutoff_pit_rejected`） | generated_at=T 日 09:00>cutoff→degraded:pit_rejected+rejected 留痕（family=macro_regime, field=sensor_reading） |
| no_data 降级（`test_wo1_macro_no_data_tier_degrades`） | tier=no_data/caution=NaN→degraded:no_data 不注入档位 |

总计：单测 37 passed（原 32+新增 5）+ e2e 6 passed = 43 passed；传感器侧回归 `tests/regime/features/test_macro_regime_sensor.py` 18 passed（本体零改动交叉验证）。

## 3. 门自检

- ruff format --check：3 文件全过；ruff check own-diff：0 新增违规（I001 已修；残余 F401×5/F841×1 均为 HEAD 既有件，preclean 通道不纳）。
- 复杂度 ≤15 / 参数 ≤7：`_build_macro_regime_family` 3 参，分支数达标（COMPLEXITY-GUARD 门实际通过）。
- 新增 import：仅惰性 `zephyr.regime.features.macro_regime_sensor`——无裸 LLM、无裸 duckdb、无裸 SQL；传感器读数走其自有 ch_reader 通道。
- 禁改本体核实：`src/zephyr/regime/features/macro_regime_sensor.py` 零改动（git 状态+传感器 18 测全绿）；flag/部署零触碰；PROMPT_VERSION 冻结不动。

## 4. commit 与留痕

- commit：`080fdfec`，message 含门禁留痕三段（RUFF-PRECLEAN/gate-any-abuse/COMMIT-SCOPE --allow-multi-domain/IMPORT-INTEGRITY noqa）。
- 审计：`.runtime/audit/debt_ratchet_lever_20261001.jsonl` 追加 1 行（IMPORT-INTEGRITY 适配案，expiry=本笔一次性）。
- claim：3 文件 acquire→落地后 `--release-only` 全量释放。

## 5. 遗留

1. **noqa:import-integrity 待摘**：st-menu-w3h-20260930 merge 传感器模块后，`llm_premarket_analysis.py` L584 行级豁免标记即可删除（建议该 lane 收尾时顺手摘除并复跑门）。
2. 第二消费者（可选加分项）`src/zephyr/regime/style_regime_model.py` 状态合成入口未动工——本单只做 WO-1 主交付（盘前注入点），加分项留给后续工单（避开他会话 regime 聚合件并行施工面）。
3. 本报告文件为 docs/_working task_bound 暂存件（未入 commit）；生产 live 面（daily_loop ch_client=None）尚未真跑验证，待传感器 lane merge 后随盘前链路首跑读数核验。
4. 未消费 warning：`build_premarket_package` 的 macro 族在 ch_client 注入形态恒为 skipped:not_injected——运行态要拿到宏观档位必须走 live 面（现网 daily_loop 即此形态，无需改造）。
