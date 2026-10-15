---
blueprint_id: MOD-SIG-146
module_id: MOD-SIG-146
module_name: pattern_series_transform
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-09-14
last_updated: 2026-09-14
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-SIG-146 pattern_series_transform 蓝图

> 设计真源：2026-09-14 Owner 拍板"替代图形族以变换层立项"（会话
> st-pattern-20260914）。本蓝图升级 REG-PAT-001 头部旧裁定（"Renko/P&F/Kagi
> 属数据图表类型，非形态语义"=排除）为：**归数据/序列层变换，立项施工**。
> 代码（拟）：`src/zephyr/signal_ashare/strategy_signal/pattern_series_transform/`。

## 0. 定位

治本路径不开"第 10 大类"铺形态条目，而是造一个"换记账方式"的底座：
OHLCV 时间序列 → 替代序列（Renko 砖块 / P&F 点数列 / Kagi 阈值线），让
MOD-SIG-091 现有几何腿（双顶/双底/趋势线/通道/突破）在更干净的价格表示上
重跑——一个抽象层让全库形态的有效覆盖翻倍，而非目录膨胀。

三实现共用一个 SeriesTransform 接口；施工序 Renko→P&F→Kagi（实现成本递增、
公开证据递减；Renko 对 A 股涨跌停平坦 bar 与跳空噪声适配最好）。
规则纯机械（每族仅 1-2 个参数）：对 100% AI 开发语境=可实现/可测试/过拟合
自由度最小。第一性依据：K 线族按时间记账（每天一笔，没动静也记），本族按
"价格真动了"记账（固定砖块/格值反转/阈值拐弯）——本质是去噪滤波器。

## 1. 接口（拟）

    SeriesTransform.build(ohlcv: DataFrame, params) -> TransformedSeries
    TransformedSeries: 事件流（砖/列/拐弯段），带 confirmed_ts 锚点
    实现：RenkoTransform(brick_size, close_to_close=True)
         PnFTransform(box_size, reversal_boxes=3)
         KagiTransform(reversal_threshold)

## 2. PIT 口径（防前视铁律）

- 全部 close-to-close 构造：已完成 bar 收盘定砖/定列/定拐弯；
  禁盘中触格判定——盘中触格=回测偷看未来（业界著名陷阱）。
- 变换序列上的形态事件：confirmed_ts=确认 bar 收盘时刻，事件落库/统计
  统一走 MOD-SIG-145（本模块不建独立统计通道）。

## 3. 目录侧联动（净零预算）

- REG-PAT-001 不开第 10 大类；仅补 P&F 原生形态 10-15 条（catapult /
  双重三重顶底 / 牛熊陷阱类），逐条带 regime 标注。
- 既有几何形态条目加 applicable_series 标注（time_bars/renko/pnf/kagi）。
- REG-PAT-001 头部 10849 行裁定注释同步升级为"已立项变换层（MOD-SIG-146）"。

## 4. 边界

- 不做：替代图形的前端渲染；tick 级盘中 Renko（日线 close-to-close 先行，
  盘中版留 tick_depth5 数据成熟后评估）。
- 消费端就绪前不启用：引擎腿经 TransformedSeries 适配器注入，无消费端=不上线。

---

## 5. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 5.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/signal_ashare/limit_up/event_axis.py` | ✅ 已实现 | |

### 5.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §5（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-146`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-146` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-146` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-146 | MOD-SIG-146 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
