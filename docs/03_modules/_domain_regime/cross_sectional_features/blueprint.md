---
blueprint_id: MOD-REGIME-007
module_id: MOD-REGIME-007
module_name: cross_sectional_features
domain: D_REGIME
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: testing
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-REGIME-007 cross_sectional_features 蓝图

> 紧凑版（92 号清单波 2 ALG-01 落地配套）。设计真源：2026-08 架构审查报告 §4.3 + #ARCH-140。

## 0. 定位

regime 特征集的横截面结构补强：既有 6 特征全部由市场代理指数（沪深300）时序派生，横截面结构事件（指数未崩但小盘股踩踏、离散度/相关性结构剧变）在指数维度不可见。本模块提供 4 个横截面结构特征纯函数，补该盲区。

## 1. 特征清单（输出列序钉死）

| 列名 | 含义 | 口径 |
|---|---|---|
| cross_dispersion | 截面收益离散度 | 个股日收益截面 std（或 IQR/1.35 稳健版，默认 iqr），20 日滚动均值平滑 |
| avg_pairwise_corr | 平均成对相关 | 个股日收益两两 Pearson 相关均值，60 日窗；分层抽样 ~200 只（成交额 10 层等量，确定性种子，20 交易日再平衡） |
| vol_dispersion | 波动率离散 | 个股 20 日已实现波动率（年化×√252）的截面 std |
| momentum_breadth | 动量宽度 | 收盘价强于 MA20 的股票占比（%） |

## 2. 接口

`compute_cross_sectional_features(panel: pd.DataFrame, ...) -> pd.DataFrame`：输入 date×symbol 的 close/volume 面板，按 date 输出 4 列。纯函数无 IO。

## 3. 不变量

- PIT 严格：T 日特征只用 ≤T 数据；trailing 窗口，禁全样本归一
- 截面有效样本 <30 只 → 该日 4 列全 NaN（宁缺毋假）
- 个股缺数据该日剔除出截面，不填补（禁 ffill 造假收益）
- 抽样确定性：同面板同输出（种子 (random_state, t_reb)）
- 新特征列一律尾部追加，禁插既有 FEATURE_NAMES 6 列（detect 消费方列序契约）
- 进 HMM 主特征集必须经配置开关+A/B 对照，默认关

## 4. 接线

`RegimeFeatureBuilder(enable_cross_sectional=False)` 默认关（输出与现状逐字节一致）；开时 4 列 pd.concat 尾部追加，`active_feature_names()` 6→10 列联动 X 矩阵。个股面板支持注入（测试/离线）或经 `_load_stock_panel()` 从 kline_daily×adj_factor 惰性加载（2026-09-16 裁定#257④ 修复：池=全市场 A_share quality_flag=1 + 后复权 close_hfq；旧 top800 池截掉 2024-02 微盘踩踏目标信号、不复权收益混入 494 条假收益）。

## 5. A/B 实证结论

**旧 A/B（2026-08-22）已作废**（裁定#257④ ALG2-3：生成脚本不存在不可复现、臂配置≠生产配置、只测一致性不测检出力，且其池/复权缺陷使结论无效——schedule Pearson 0.9999 属"两臂同盲"而非无增量）。重做报告：docs/_working/alg01/2026-09-16-alg01-ab-redo.md（生成代码=scripts/backtest/alg01_ab_redo.py，双臂=生产配置 full+overlay+phase2c，指标含 2024-02 微盘踩踏/2025-04 关税冲击事件检出力对照与 NAV 诊断）。

## 6. 边界

- 不做横截面特征的交易信号化（本模块只供 regime 判定/诊断，不接策略链路）
- 抽样面板非全市场精确值（O(N²) 成本权衡，纪律见 §3）
- production 启用挂起等 Owner（宪章 B-007，testing 封顶）

## 7. 测试

tests/regime/test_cross_sectional_features.py（18 用例：PIT 截断/已知答案合成截面/样本不足 NaN/缺数据剔除/开关关逐字节回归）。

---

## 8. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 8.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/research/regime/test_cross_sectional_features.py` | ✅ 已实现 | |
| `tests/research/regime/test_index_regime_panel.py` | ✅ 已实现 | |

### 8.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §8（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下
