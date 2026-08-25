---
blueprint_id: MOD-BT-027
module_name: layered_validation_pipeline
domain: D_BACKTEST
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
priority: P1
blueprint_level: module
domain_id: D_BACKTEST
path: src/zephyr/backtest/services/layered_validation_pipeline.py
granularity: file
---

# MOD-BT-027 layered_validation_pipeline 蓝图（C-003 自动回测与仿真）

> **module_id**: MOD-BT-027 | **域**: D_BACKTEST | **优先级**: P1
> **来源**: B1-00258（AUD-DRAFT-001-DIGEST P1 波 W-P1-18，CAND-WFO-002，跨域元文档 §功能域模块·D-OPS）
> 代码：`src/zephyr/backtest/services/layered_validation_pipeline.py`

## 0. 定位

C-003 自动回测与仿真——策略/因子/信号**提交触发** V1 单元→V5 全链路分层验证，
自动跑回测+过拟合门禁+报告归档。TSV 现状：回测引擎存在但提交即验证的 V1~V5
分层自动化管道缺失。

查重裁定（W-P1-18 细读 TSV + 52 号 memo，**补缺不重建**）：

| 既有件 | module_id | 职责 | 与本模块边界 |
|---|---|---|---|
| strategy_validation_pipeline | MOD-BT-001(core) | 过拟合检测+IS→WFA→OOS 三阶段门控编排 | **输入注入式**（各阶段产物由调用方供给，不跑回测）；本模块=提交触发的**分层自动执行编排**，门控语义对齐不重建 |
| overfitting_detector / decision_gate | MOD-BT-001(core) | 过拟合三维检测/三阶段门控阈值 | 阈值与判定唯一真源；本模块经注入 callable 委托，**不建第二套门控**（52号§7 BM-BT-07-I 显式裁定：再建 V1-V6 门控=同一防线两套阈值，禁） |
| scheduler | MOD-BT-017 | 参数网格 FIFO 批跑回测 | 网格寻优批跑，无提交分层语义；本模块层执行器注入式，可委托其跑层回测 |
| result_repository / backtest_result_sink | MOD-BT-001(io) | 结果持久化/可视化转换 | 报告归档经注入 sink 委托，不重造持久化 |
| V1~V5 层定义 | 交易决策架构 §20.7.1 | V1因子Purged K-Fold/V2信号WF/V3策略WF+Permutation/V4管线端到端/V5日内Tick | 层执行器（runner）由运行时装配批按 §20.7.1 接线；本模块只管**提交→分层计划→递进执行→门禁→归档**编排骨架 |

不做什么：不定义任何验证阈值/门控（52号裁定禁第二套）、不直接跑回测引擎
（runner 注入式）、不持久化（sink 注入式）、V6 风控验证按需（P1 不入层计划封闭集）。

## 1. 编排规则（确定性）

- **提交** `ValidationSubmission`（frozen）：subject_kind 封闭集
  {factor, signal, strategy, pipeline} + subject_id + params + artifacts；
  未知 kind/空 id Fail-Closed。
- **层计划** `SUBJECT_LAYER_PLAN`：factor→(V1)，signal→(V2,V5)，strategy→(V3)，
  pipeline→(V4)（§20.7.1 分层映射；V1/V2 为工厂内部质量门禁，不通过不进 V3）。
- **递进执行**：层计划顺序执行，**层层递进不可跳级**——某层 failed 即中止，
  剩余层记 not_run；runner 缺失 Fail-Closed（计划层无执行器=配置错误）。
- **过拟合门禁**：注入 `overfitting_gate(submission, layer_results) -> Mapping
  {is_overfitting, reasons}`（Owner 接线 OverfittingDetector）；None=未配置记
  gate_status=not_configured。
- **裁决**：passed = 全部层 passed ∧ ¬is_overfitting（门禁配置时）。
- **归档**：注入 `report_sink(report)`；sink 异常**不吞裁决**——记
  archive_status=archive_failed+原因（fail-open 留痕，审计可见）。

## 2. 接口

```python
class LayeredValidationError(ValueError)
@dataclass(frozen=True)
class ValidationSubmission: subject_kind / subject_id / params / artifacts
@dataclass(frozen=True)
class LayerResult: layer / passed / metrics / detail / status
@dataclass(frozen=True)
class LayeredValidationReport: subject_id / subject_kind / layers_planned / layer_results / gate_status / is_overfitting / passed / archive_status / reasons
SUBJECT_LAYER_PLAN: Mapping[str, tuple[str, ...]]
run_layered_validation(submission, *, layer_runners, overfitting_gate=None, report_sink=None) -> LayeredValidationReport
```

## 3. 依赖前置

- MOD-BT-001 strategy_validation_pipeline / overfitting_detector（门控语义对齐，注入委托）。
- MOD-BT-017 scheduler / 引擎族（层 runner 接线，运行时装配批）。
- 报告归档 sink（result_repository 或等效，注入式）。

## 4. 验收标准

- 单测全绿（层计划映射、递进中止不可跳级、runner 缺失 Fail-Closed、过拟合门禁
  否决/未配置、归档失败留痕不吞裁决、端到端 提交→分层→门禁→归档）；相关域集成零回归。
