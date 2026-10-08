---
ttl: task_bound
title: wq_alpha_87_wiring_v1 —— WQ87 核接线基准册（FactorRegistry+考试链挂载）
session: st-mx07-W6
---

# wq_alpha_87_wiring_v1 —— WQ87 核接线基准册（完成）

- 车道: st-mx07-W6（matrix 战役 2026-10-07 夜战第二波）
- 任务卡: master_backlog_v2.md P2-6「wq_alpha_87 接线（核已就绪，接线日即插）| 前置=装配批」
- 状态: **接线完成，全量验证绿**

## 1. 核出处与就绪证据

- 核本体: `src/zephyr/factor/wq_alpha_87.py`（MOD-L02-001，CAND-FAC-010 / B1-00847，GATE-92-01）
  - WorldQuant 101 精选 87 公式（剔除 14 个 IndNeutralize/cap 依赖；5 个降级公式显式标注 DEGRADED_FORMULAS）
  - 双委托注入点: `register_all(register_hook)`（入因子注册）+ `validate_ic(alpha_id, data, ic_hook)`（IC/IR 验证）
  - 就绪证据: `tests/research/factor/test_wq_alpha_87.py` 228 行全绿（87 公式 panel 可算、PIT 前缀不变性、hook 委托契约）
  - 历史 commit: 6ea93ecb19f「wq_alpha_87(WQ101 族剔除 14 IndNeutralize 依赖留档)；169 单测+两域零回归」
- 未接线证据（本次施工前）:
  - gpu_survey_v1.md:25「factor/wq_alpha_87.py（87 公式，MATURITY=design 未接线）…接线待装配批；接线后=因子批考批量面」
  - 核头部 [CONSUMERS]「因子注册表/feature_store（register_all/validate_ic 委托注入点）…接线留装配批」
  - ic_ir_calc.py 头部 [CONSUMERS]「接线待排期」
- 防重做核查: `git log --all --grep` 仅两条历史（核适配 6ea93ecb19f、I 道 GPU 探针 e607d6b1ddf），无他班接线记录。

## 2. 接线语境裁定（仓内权威记载）

「接线」在本仓语境 = 核头部声明的两处委托注入点的真实装配：
1. **注册册登记**: register_hook → `FactorRegistry`（factor_base.py 单例）——考试链入口：
   `compute_ic_ir_table(factor_ids,...)` → `evaluate_factor`（backtest.py）→ `FactorRegistry.get(factor_id)`（backtest.py:408）。
2. **调用链挂载**: `evaluate_factor` → `_compute_factor_panel` 原为逐标的调 `compute(single_df)`（backtest.py:326）——
   而 WQ87 公式是**截面型**（rank/scale 按日截面），单标的输入使截面 rank 恒 1 退化，直接注册=错值。

### 形态裁定（自裁留痕）
- 不做 87 个单标的退化注册（截面公式单标的算=静默错值，质量红线）。
- 采用 **panel 感知 duck-type 协议**：因子实例声明 `compute_panel(history)`（MultiIndex(symbol,trade_date) 长表 →
  (date×symbol) 面板）时 `_compute_factor_panel` 优先整面板一次计算；无该方法因子走原逐标的路径，行为零变化
  （OCP，5 行分支，backtest.py `[MODIFY-GUARD] none`）。
- 新接线件 `src/zephyr/factor/wq_alpha_87_wiring.py`（creation_token=wq-alpha-87-wiring-20261008，
  depgraph 设计节点 node_id=16495462，翻译条目已登 8080 条册）：
  - 87 个 FactorBase 适配类（factor_id=`wq_alpha_001`..`wq_alpha_101`，domain=`wq_alpha`，
    降级公式 tag=`ind-neutralize-degraded`）
  - `wire_wq_alpha_87()`：幂等登记（重入=0，factor_id 撞他类抛 Alpha87WiringError 不顶替）
  - `make_ic_ir_hook(return_panel, horizon)`：validate_ic 的真实 ic_hook，委托
    `metrics.compute_ic_series/compute_ir`（ic_ir_calc 同语义，纯函数无 IO）
  - `compute()` 单标的语义显式抛 Alpha87Error（诚实失败，防静默错值）
- 显式不做：import 期自动注册（全局注册表副作用污染测试隔离）；接线动作=装配批/考试入口显式调一次
  `wire_wq_alpha_87()` 即插（文档+模块 docstring 双留痕）。

## 3. 变更清单（全部落地）

| 文件 | 变更 |
|---|---|
| `src/zephyr/factor/wq_alpha_87_wiring.py` | 新建接线件（TTL permanent，四段治理齐） |
| `src/zephyr/factor/core/evaluation/backtest.py` | `_compute_factor_panel` 5 行 panel 分支（含注释） |
| `tests/research/factor/test_wq_alpha_87_wiring.py` | 新建 14 例（tests/ 豁免 token） |
| `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` | creation_tokens 末尾 di_seam_exemptions 锚前插 1 条（safe_write_text CAS，before/after sha256 留审计） |
| `src/zephyr/governance/.../module_translation_registry.yaml`（经 add_module_translation.py） | 大白话条目 upsert |
| 架构库 nodes 表（经 apply_depgraph.py） | 设计节点 node_id=16495462（file 粒度，planned） |

## 4. 验证读数（2026-10-08 本机实测）

- 新接线测试: `tests/research/factor/test_wq_alpha_87_wiring.py` **14/14 passed（4.93s / ruff 修复后复跑 5.06s）**
  - 覆盖：注册 87/幂等重入=0/撞位抛错/降级标注、panel 分支与核直算**逐位对拍**（assert_frame_equal check_exact）/
    evaluate_factor 端到端出 IC（load_history 合成注入，不触 CH）/compute_ic_ir_table 批量两因子
    /ic_hook 与 metrics.compute_ic_series 同语义（sample_size+ic_mean 精确相等）/空交集容错全 0
- 既有测试零回退: test_wq_alpha_87.py(28) + test_evaluation_backtest.py(21) + test_ic_ir_calc.py(5) = **54 passed（32.77s）**
- ruff 双清: `ruff check`（3 文件 0 违规）+ `ruff format --check` 全过（2 处自动修复后复检 All checks passed）
- 端到端语义链: wire_wq_alpha_87() → evaluate_factor("wq_alpha_101") → FactorRegistry.get → compute_panel
  分支 → WQ87 核 → IC/IR/OOS（EvaluationResult.sample_size>0, ic_mean finite，测试锚定）

## 5. 遗留与风险

- backtest.py 头部注释「因子计算调度（逐标的调用 FactorBase.compute）」未同步改为「逐标的或 panel 协议」——
  文档级小漂移，不动 [INVARIANTS]（本车道最小 diff 原则，留给后续对齐批）。
- `tests/factor/` 仅有 test_tech_factor_pipeline.py，wq87 系测试真源在 `tests/research/factor/`——核头部
  `[TESTS] tests/factor/test_wq_alpha_87.py` 指针漂移（历史遗留，非本车道引入，未修）。
- 87 因子真实 CH 数据 IC 考试（真值面）属「因子批考批量面」后续批——本车道交付=接线与机制验证（合成面）。
- depgraph regen 后台进程（PID 44712，登记时自动触发）与本车道无耦合，产物由其自身审计。
