---
ttl: permanent
doc_type: architecture_view
title: TDM 节点验证 runner（validation）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.1.4"
date: 2026-09-10
topic: tdm_validation_runner
scope: module
module_id: MOD-TDMVAL-001
design_maturity: design
build_status: generated
responsibility_domain: 
---

# TDM 节点验证 runner（MOD-TDMVAL-001）

> 节点级可回测治理 P1-2（真源：`docs/_working/2026-09-09-node-backtest-governance.md` §8.2）。
> 职责一句话：读回测成交流水 → 按 validation_method_registry 推导方法算指标 → 过显著性土规 → 写 `c1_backtest.node_verdict` 台账。

## 1. 职责与边界

| 项 | 内容 |
|---|---|
| 做 | 验证批入口 `run_validation(batch=...)`：L4 执行类首批 14 节点（exec_quality 滑点/成交指标，排除币圈镜像 TDM-C-*）+ X 流第二批 18 节点（`batch="XFLOW"`，flow==exit_flow，exit_counterfactual 避损口径，Owner 2026-09-10 X 流验证批指令 T3）；holdout 窗口排除（最近 12 个月）；两套土规（触发<30 不下结论 / 样本外衰减≥50% 判存疑）；lag=1 滞后重算开关；台账写入 |
| 不做 | 消融回放实弹运行（对照数据=T2 信号消融对照器，受协议备忘录 §12「参数定稿前不跑回测」约束，放行前对照缺失按 pending 降级）；衰减巡检调度（P2-1 独立落盘=验证批尾随事件）；结论反哺地图 YAML（验证态只进台账，地图保持设计真源纯净） |

## 2. 数据流

```
config/trading_decision_map.yaml（L4 节点清单 / flow==exit_flow X 流 18 节点）
data/backtest_artifacts/bt-*.json（成交流水 trade_log；T1 起含 decision_price/order_type）
src/zephyr/trading/validation/ablation.py（T2 信号消融对照器，exit_counterfactual 对照数据源——回放受 §12 约束）
docs/01_policies_and_standards/_registry/catalogs/validation_method_registry.yaml（方法推导+土规参数）
  → runner.run() → c1_backtest.node_verdict（schemas/categories/backtest/backtest_node_verdict.py DDL 真源）
  → /api/tdm/validation（只读端点）→ tdm 抽屉「验证档案」区
```

## 3. 关键设计裁定（施工中自裁）

1. **holdout 优先**：现有流水全部落在 holdout 窗口内（2026-02~08 > 2025-09 截止线）→ 首批 verdict 全部为 `pending` + `significance=insufficient_samples`，notes 如实披露原因。宁可 pending 不作弊（PB-08 铁律："定稿前不许跑回测"）。
2. **归因粒度限制**：trade_log 无 order_type/节点归因字段，v1 以执行流水全量为统计对象写每节点行；notes 披露该限制。子环节级归因待执行报告数据源扩展。
3. **滑点基准**：决策价不存在于流水 → 用同日 kline_daily 成交额/成交量 VWAP 代理；lag_recheck=True 时基准右移 1 个交易日（前视诊断，PB-16）。
4. **事件驱动**：runner 为手动/上游事件触发的无状态批函数（B 类），不做常驻调度；P2-1 衰减巡检=验证批写台账成功后的尾随事件（decay_check=True，2026-09-10 裁定落地），不挂 cron 不动 Human-Gated 路由表。
5. **第二批=X 流风控批**（2026-09-10 Owner 指令 T3）：`load_xflow_nodes` 按 flow==exit_flow 选 18 节点；`compute_exit_counterfactual_metrics`/`apply_exit_soil_rules` 按方法学 exit_counterfactual 口径（触发/不触发损失差；对照=T2 消融器差额序列，缺失时 avoided_amount=None → pending 如实降级）；触发计数 v1 以卖出流水代理（全量口径+notes 披露，同裁定 2 先例）；R1-03（护盘加仓白名单）动作方向为买入，消融放行时需单独核对方向。本批流水全落 holdout 保密窗口（>2025-09-09），verdict 全部 pending+insufficient_samples 如实披露（纪律不是欠账，同裁定 1）。

## 4. 接口

```python
from zephyr.trading.validation.runner import run_validation
report = run_validation(dry_run=True)   # 先看不出库
report = run_validation()               # 写台账
```

## 5. 验收

- tests/trading/test_validation_runner.py：方法推导 / holdout 切分 / 两套土规 / lag 开关 / dry-run 零写入 / X 流 18 节点与 exit_counterfactual（2026-09-10 第二批 +7 用例，全绿）
- tests/trading/test_validation_ablation.py：消融对照器 9 用例（空剥越恒等/回滚式剥算子保 Σw=1/非法动作拒绝/幂等基线 rescued≡0/清仓差额非零/NaT 过滤），2026-09-10 T2 落地
- 实弹：`run_validation()` 后 `SELECT count() FROM c1_backtest.node_verdict` 出现 14 行 L4 verdict；`/api/tdm/validation?node_id=TDM-E-L4-03` 返回记录；`run_validation(batch="XFLOW")` 追加 18 行 X 流 verdict（holdout 锁窗下全 pending）

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-TDMVAL-001`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-TDMVAL-001` 的 9 个 file 节点 | design | `extract_depgraph.py --modules MOD-TDMVAL-001` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-TDMVAL-001 | MOD-TDMVAL-001 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | generated | ✅ |
| file_count | 9 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 6. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 6.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `schemas/categories/backtest/backtest_node_verdict.py` | ✅ 已实现 | |
| `schemas/categories/backtest/backtest_strategy_screen.py` | ✅ 已实现 | |
| `src/zephyr/trading/validation/__init__.py` | ⚠️ 骨架 | |
| `src/zephyr/trading/validation/ablation.py` | ✅ 已实现 | |
| `src/zephyr/trading/validation/decay_watch.py` | ✅ 已实现 | |
| `src/zephyr/trading/validation/runner.py` | ✅ 已实现 | |

### 6.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/trading/test_validation_ablation.py` | ✅ 已实现 | |

### 6.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §6（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


