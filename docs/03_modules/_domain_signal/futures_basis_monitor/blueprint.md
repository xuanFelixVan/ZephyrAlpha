---
blueprint_id: MOD-SIG-058
module_id: MOD-SIG-058
module_name: futures_basis_monitor
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: evolving
safety_level: L
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-SIG-058 futures_basis_monitor 蓝图

> 紧凑版（SOP Step 4 补建）。设计真源：44号备忘录 §9.8 通道2，M1-⑧/M3-⑥。
> 代码：`src/zephyr/signal_ashare/futures_basis_monitor.py`

## 0. 定位

期指基差情绪监测器——第一性原理：期货=机构带杠杆的实时投票机，价格发现领先现货（恐慌时贴水急扩先行）。消费国内股指期货（IF/IC/IM/IH 主力）与现货指数两腿，输出逐品种基差率/贴水变化率/贴水急扩告警/持仓确认标志，供 M2 降档触发与情绪注解消费。品种分工：IM 对中小盘/题材情绪最敏感（打板策略主看 IM）；IF 主看大盘蓝筹。

## 1. 接口

```python
def compute_futures_basis(
    ts: datetime | date | str | None = None,  # None=当前 Asia/Shanghai；PIT 上界，仅消费 ≤ts 数据
    ch_client: Any | None = None,             # None=延迟取 ch_writer.get_client，不可得→degraded
    config: FuturesBasisConfig | None = None, # None=44号 §9.8 默认口径
) -> FuturesBasisSnapshot
```

品种-现货映射（config 化）：IF→沪深300(000300) / IC→中证500(000905) / IM→中证1000(000852) / IH→上证50(000016)。只读六表：futures_kline_qmt / index_quote / kline_futures / kline_index / futures_position / calendar_event。

## 2. 输出契约

`FuturesBasisSnapshot`（frozen dataclass，asdict JSON 可序列化，prediction_log 预留）：ts/trade_date + `per_symbol: dict[str, FuturesBasisSymbol]` + delivery_week/applied_weight（交割周降权 0.5）+ degraded/notes。

`FuturesBasisSymbol` 逐品种：basis_rate=（F_主力−S_现货）/S_现货；basis_vel_30m（当前 d1_proxy 日频代理口径，分钟采集落地后切真 30m 参照）；discount_alert（vel < −1.5×σ_20d 贴水急扩告警，M2 降档触发输出之一）；confirm_flag（告警且持仓激增>10%→真对冲确认；持仓平稳→signal_weight×0.5 打折；持仓不可用→None 不打折 fail-open）；futures_leg/spot_leg 数据源留痕。

## 3. 不变量（头注 INVARIANTS 原文）

- 只读消费六表不写库
- fail-open：任一腿/事件/持仓查询失败不阻塞其余腿，仅 degraded 标注+留痕
- 两腿皆无→degraded=True 空结果不炸
- degraded=True 时结果不可用于 M2 降档决策
- 输出 dataclass asdict JSON 可序列化（prediction_log 预留）
- PIT——所有查询以 ts 为上界

## 4. 降级行为

- ERROR_CONTRACT：查询异常/表空/客户端不可用→fail-open 降级（degraded/notes）不抛；ts 格式非法→ValueError（fail-closed）
- 降级链：分钟腿缺→日频腿+degraded 标注；单腿缺→该品种跳过留痕；两腿皆无→snapshot degraded=True 空结果
- 交割周判定：calendar_event 表空/查询失败 fail-open 不降权+留痕
- σ_20d 样本<5 不定性（噪声护栏）

## 5. 边界（不做）

- MVP 阶段无消费方（候选：M2 降档触发、market_sentiment_analyzer 情绪注解、prediction_log 落库）
- 期货分钟采集配置另一代理并行施工中（本模块按表结构消费）

## 6. 测试

tests/signal_ashare/test_futures_basis_monitor.py

---

## 7. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 7.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 7.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §7（本节）→ 知道「哪些已实现、在哪里」
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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-058`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-058` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-058` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-058 | MOD-SIG-058 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
