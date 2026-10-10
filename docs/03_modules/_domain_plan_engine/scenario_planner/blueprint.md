---
blueprint_id: MOD-PLAN-005
module_id: MOD-PLAN-005
module_name: scenario_planner
domain: D_PLAN
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

# MOD-PLAN-005 scenario_planner 蓝图

> 紧凑版（92 号清单波次落地配套，SOP Step 4 补建）。设计真源：44号备忘 §4 M3-③ 多情景方案 + §9.11 竞价三细节 + §9.6 末段；40号 §2.9 决策⑧。
> 代码：`src/zephyr/plan_engine/scenario_planner.py`

## 0. 定位

盘前"多情景方案整机"——MOD-PLAN-002 只"加载昨夜边界+9:25 竞价匹配 9 情景"，缺"今日三情景操作预案"输出与 auction_book（1.46M 行已采集）消费接入，本模块两段式补该缺口：9:00 三情景预案 + 9:25 竞价验证二次匹配。

## 1. 接口

```python
def compute_scenario_plan(
    trade_date: str | datetime.date,
    ch_client: Callable[[str], str] | None = None,
    config: ScenarioPlannerConfig | None = None,
    revision: OvernightRevision | None = None,   # MOD-PLAN-004 产出；None=同一 ch_client 现算
    boundary: TomorrowBoundary | None = None,     # MOD-PLAN-001 产出注入；None=价位字段缺省
) -> ScenarioPlan
```

类形态：`ScenarioPlanner(ch_client, config).compute(trade_date, revision, boundary)`。

## 2. 输出契约

`ScenarioPlan`（frozen dataclass，`to_dict()` JSON 可序列化）：

- `three_scenarios: list[ScenarioActionPlan]`——9:00 高开/平开/低开三套参数化预案（HIGH/FLAT/LOW 顺序固定）：档位 stance（final_shift 经 SHIFT_STANCE 映射：-1 保守×0.5 / -0.5 偏守×0.8 / 0 正常×1.0 / +0.5 偏多×1.2 / +1 进攻×1.2）、修正后加仓上限、禁加仓价位/减仓触发价/必出止盈价（boundary 注入时给绝对价位）+ 中文动作清单
- `auction_verification: AuctionVerification | None`——9:25 竞价三细节（§9.11）：D1 虚拟开盘价偏离（成交额加权）、D2 匹配量放大（竞价量/5 日均量，≥1.2× 确认 /<1.0× 降信半档）、D3 撤单识别（9:20 分界，fake_ratio>0.6 方向信号作废）、昨日涨停竞价溢价注记
- `final_scenario`——9 情景之一（SCENARIO_LIST 语义对齐 MOD-PLAN-002；竞价缺数据降级 FLAT_OPEN_WASH）
- `confidence_scale`——1.0 确认 / 0.5 降信半档 / 0.25 双降信；`degraded` / `reasons` / `trace` 留痕

## 3. 不变量（头注 INVARIANTS 原文）

- 竞价仅作验证信号不作下单通道（40号决策⑧ MVP 不碰集合竞价，本模块零下单路径）
- fail-open 不阻塞主流程
- auction_book 缺数据=竞价验证段 degraded 不影响 9:00 三情景段
- 9 情景语义与 MOD-PLAN-002 SCENARIO_LIST 对齐
- 输出纯 dataclass JSON 可序列化

## 4. 降级行为

- ERROR_CONTRACT：单通道异常→该段降级（None/缺省值）+trace 留痕；整体不抛异常（仅 trade_date 非法抛 ValueError）
- auction_book 无今日数据→竞价验证段全字段 None + status=degraded:no_data，final_scenario 缺省 FLAT_OPEN_WASH（与 MOD-PLAN-002 无竞价数据降级口径一致）
- revision 未注入→经 OvernightBoundaryReviser 现算（trace 标 computed_inline）
- boundary 未注入→价位字段 None 仅相对参数（degraded=True 留痕）
- final_shift 非预期值→就近吸附五档集合 {-1,-0.5,0,+0.5,+1}

## 5. 边界（不做）

- 不直接改 TomorrowBoundary/ConstraintState（消费方负责应用）
- 不做方向点预测（90号 §7 只画栏杆不算命）
- 不参与集合竞价下单（40号决策⑧）

## 6. 测试

tests/plan_engine/test_scenario_planner.py

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
