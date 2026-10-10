---
blueprint_id: MOD-PLAN-006
module_id: MOD-PLAN-006
module_name: boundary_revision_engine
domain: D_PLAN
doc_type: blueprint
ttl: permanent
design_maturity: production
stability: testing
safety_level: H
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-22
last_updated: 2026-08-22
owner: ZephyrAlpha-Owner
responsibility_domain: 
---

# MOD-PLAN-006 boundary_revision_engine 蓝图

> 紧凑版（92 号清单 §8.3 落地配套，SOP Step 4 补建）。设计真源：44号备忘 §3 M2 + §9.5；30号 §2.2 firm 硬约束。
> 代码：`src/zephyr/plan_engine/boundary_revision_engine.py`

## 0. 定位

盘中次日预案边界修正引擎——44号 §3 M2 落码：盘中实时输入→当晚边界档位的修正通道（T+1 场景）。决策语义=不输出"明天涨/跌"，输出"今晚的边界该收多紧"（41号 §3.10"边界比聪明更重要"；90号 §7 不预测裁定严格绕行）。

## 1. 接口

```python
def evaluate_boundary_revision(
    trade_date: str | datetime.date,
    eval_slot: str,                              # 14:00/14:45（与 MOD-PLAN-003 尾盘窗口对齐）
    sentiment/distortion/futures_basis/sector_divergence/volume_forecast: ... | None,  # 触发源全 Optional 注入
    rs_ratio: float | None = None,
    bs005_triggered: bool = False,
    state_store: JsonStateStore | InMemoryJsonStateStore | None = None,  # 防抖/冷却持久化
    config: BoundaryRevisionConfig | None = None,
    *, eval_time: str | None = None, baseline_tier: str = "NORMAL",
    log_db_path: str | Path | None = None,
) -> BoundaryRevision
```

类形态：`BoundaryRevisionEngine(state_store, config, log_db_path).evaluate(...)`。触发源运行时鸭子类型读字段，本模块不读库取数（纯计算）。

## 2. 输出契约

`BoundaryRevision`（frozen dataclass，JSON 可序列化，**仅当日有效**）：trade_date/eval_slot/eval_time、original_tier→revised_tier（CONSERVATIVE/NORMAL/AGGRESSIVE）、revision_applied/direction（DOWNGRADE/UPGRADE/NONE）、triggers/pending_triggers/debounce_proof（防抖留痕）、cooldown（升/降当日各最多 1 次）、position_cap_scale（保守 0.5/正常 1.0/进攻 1.2）、no_add_price_shift（ATR(14) 倍数，保守 -0.5=下移，2026-08-22 统筹裁定）、expired/logged 标记。`is_effective_on(trade_date)` 供消费方校验；`with_expired()` 返过期副本。

修正规则（§9.5）：降档七触发源（情绪分<35 且 lu_net_rate<0 / 护盘失真 spread>2σ / 大幅回撤≥7 / IM 贴水 30min 急扩>1.5σ / 板块见顶派发态 / 虹吸 z>1.5σ×速度计>75 分位共振 / BS-005）；升档三条件全满足（情绪分>65 且 ŷ_full≥1.1×20 日均量 且 rs_ratio>0）。防抖≥15min 才生效（state_store 跨调用计时，信号中断清零）；升降档同窗同时确认→降档优先（安全方向）。实际改档写 prediction_log（prediction_type="plan_revision"）。

## 3. 不变量（头注 INVARIANTS 原文）

- 修正仅当日有效（次日盘前 MOD-PLAN-001 基线覆盖，不跨日累积；非当日消费拒发/标 expired）
- 升档×1.2 封顶 firm 单票 8%/组合硬约束（30号 §2.2，firm 层执行，本模块只出缩放系数不越层比较口径）
- 防抖≥15min + 升/降档当日各最多 1 次冷却
- 触发源缺数据=该源跳过不炸整体
- 升降档同窗同时确认→降档优先（安全方向）
- 输出纯 dataclass JSON 可序列化

## 4. 降级行为

- ERROR_CONTRACT：trade_date/eval_slot/eval_time/baseline_tier 非法→BoundaryRevisionError（ZA-PLAN-0006，ValueError 子类）fail-closed
- 触发源缺数据/未注入/degraded→该源跳过+skipped 留痕（不抛）
- prediction_log 写入失败 fail-open（logged=False+reasons 留痕，不阻塞盘中评估）
- state_store=None→当次性内存态（防抖/冷却仅当次有效）；生产必须注入 JsonStateStore
- M1 30m 字段未落地前 lu_net_rate 以 5m 口径代理+detail 标注 rate_proxy_5m

## 5. 边界（不做）

- 不做方向点预测（90号 §7）
- 不直接改 TomorrowBoundary（消费方经 apply_revision 应用）
- 不执行下单 / 不读库取数（触发源全部入参注入）

## 6. 测试

tests/plan_engine/test_boundary_revision_engine.py

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
