---
module_id: MOD-INF-015
title: "health_probes database 探针 stub 处置方案 — 降级标记，不修不删"
doc_type: construction_plan
status: Draft
version: "1.0.0"
layer: cross_layer
blueprint_level: sub_module
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260628-P3T4
date: "2026-06-28"
valid_from: "2026-06-28"
ttl: task_bound
completes_when: "health_probes.py Maturity 降级为 prototype + 行内 stub 注释添加 + AGENTS.md 登记"
belongs_to: "MOD-INF-015"
parent_module: "MOD-INF-015"
scope: global
stability: evolving
verifiability: manual
construction_progress: planned
priority: P3
runtime_plane: hot
depends_on:
  - {target: "MOD-DB_DEPGRAPH_OPT", at: "§P3-T4", why: "P3-T4 裁定——verify_schema_health 校验4 已是 PG 健康检查真源"}
references:
  - {id: "trae_053_automation_dual_track", at: "全篇", why: "自动化双轨约束——HealthAggregator 15s 定时轨是灰色地带"}
  - {id: "MOD-INF-015", at: "全篇", why: "system_telemetry 蓝图——health_probes 真源"}
---

# health_probes database 探针 stub 处置方案

> 真源：[health_probes.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/health_probes.py)
> P3-T4 裁定背景：[P3方案 §裁定记录](../03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p3_postgresql_optimization.md)

---

## 一、stub 真相（调研结论）

### 1.1 不是 bug，是协议层化石

`health_probes.py` 的 `healthz()` 方法（第99-123行）**逻辑完整**：实现了 database 的 `wal_checkpoint_lag > 5s` degraded 判定。但：

| 环节 | 状态 | 证据 |
|------|------|------|
| 协议层（health_probes.py） | ✅ 完整 | L111-113 有 wal_checkpoint_lag 判定逻辑 |
| 调用层（HealthAggregator.poll_all） | ❌ 断链 | [health_aggregator.py:61](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/health_aggregator.py) `healthz(system)` 不传 metrics → `if metrics:` 短路 → degraded 永不触发 |
| 采集层（wal_checkpoint_lag） | ❌ 零采集器 | 全项目 grep `wal_checkpoint_lag` 仅 health_probes + 测试，零采集代码 |
| 消费层（API/告警/日志） | ❌ 零消费者 | `_snapshots` 仅存内存 list，无 API endpoint，无告警联动，无日志输出 |

**三重孤立**：协议完整 / 数据断链 / 消费者断链。所谓"stub"指这个三重孤立状态，不是函数体是 `pass`。

### 1.2 为什么不该修

**修复方案A（仅让 stub 生效）**：改 `poll_all` 传 metrics → 无数据源（wal_checkpoint_lag 零采集器）+ 无消费者 → 修了等于没修。

**修复方案B（完整修复：采集器+消费者+API）**：
- 需新建 `pg_metrics.py` 采集器（~100行）
- 需改 HealthAggregator + facade.py 落盘（~80行）
- 需新建 API endpoint 或接入 AlertSubsystem（~50行）
- 需补测试（~50行）
- **严重违反 P3-T4 裁定**：[AGENTS.md §11.2](file:///d:/ZephyrAlpha/AGENTS.md) 明确"禁止新建 monitor_pg.py 常驻监控"，HealthAggregator 每 15s 跑 poll_all 本身就是 trae_053 定时轨灰色地带
- **与已裁定路线冲突**：`verify_schema_health.py` 校验4 已是 PG 健康检查真源（事件驱动，pre-commit）

### 1.3 为什么不该删

**RULE-THREE 三步审判**：
- STEP 1 登记：health_probes 在 `__init__.py` 导出，manifest 引用 → 有登记
- STEP 2 重复：`health_monitor/health_aggregator.py` 是另一套设计，不重复
- STEP 3 功能价值：
  - 3a 协议契约（CT-HEALTH-001）有价值——12 系统三态探针是 MOD-MASTER-002 §十四 标准化 HealthCheck 实现
  - 3b 零消费者原因是管线未接通，不是设计错误
  - 3c 重建成本高（12 系统 × 3 态 + SPECIAL_RULES）
  - **ANY → 保留，不删除**

---

## 二、处置方案：降级标记（方案C）

### 2.1 改动清单（最小化）

| 文件 | 改动 | 行数 |
|------|------|------|
| [health_probes.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/health_probes.py) | `[MATURITY] production` → `[MATURITY] prototype`；L99 healthz 方法加 stub 注释 | ~3 行 |
| [health_aggregator.py](file:///d:/ZephyrAlpha/src/zephyr/infrastructure/system_telemetry/health_aggregator.py) | L61 加行内注释标明 stub | ~1 行 |
| [AGENTS.md](file:///d:/ZephyrAlpha/AGENTS.md) | §11.2 补充说明 health_probes stub 状态 | ~3 行 |

**总工作量**：~7 行注释/标记改动，零功能改动。

### 2.2 health_probes.py 改动

```python
# 第7行：[MATURITY] production → [MATURITY] prototype
# [MATURITY] prototype  # stub: 协议完整但数据断链，见 docs/_working/health_probes_stub_disposition.md

# 第99行 healthz 方法 docstring 补充：
def healthz(self, system: str, metrics: dict[str, Any] | None = None) -> dict:
    """三态健康判定。
    
    [STUB] 当 metrics=None 时（HealthAggregator.poll_all 当前调用方式），
    degraded 判定永不触发。database 的 wal_checkpoint_lag 指标零采集器。
    PG 健康检查真源已迁移至 verify_schema_health.py 校验4（事件驱动）。
    详见 docs/_working/health_probes_stub_disposition.md
    """
```

### 2.3 health_aggregator.py 改动

```python
# 第61行
healthz = self._probes.healthz(system)  # [STUB] 未传 metrics，degraded 永不触发——CT-HEALTH-001 部分功能
```

### 2.4 AGENTS.md §11.2 补充

在现有 P3 裁定记录后追加：

```markdown
**health_probes database 探针 stub 状态**：`health_probes.py` 协议层完整但三重孤立
（HealthAggregator 不传 metrics + wal_checkpoint_lag 零采集器 + 零 API 消费者）。
裁定：降级 Maturity=prototype + 行内注释，不修不删。PG 健康检查真源已迁移至
`verify_schema_health.py` 校验4（事件驱动，pre-commit）。新 AI 勿尝试"修复"此 stub——
它是项目治理层选择事件驱动路线后留下的协议层化石，修复会违反 P3-T4 裁定。
```

---

## 三、为什么这个方案治本

### 3.1 防止未来 AI 浪费精力

调研发现，这个 stub 会让新 AI 误以为是"断链 bug"而尝试修复。降级标记 + 行内注释 + AGENTS.md 登记后，新 AI 进项目能立即看到：
- 这是已知 stub，不是 bug
- 修复会违反 P3-T4 裁定
- PG 健康检查真源在 verify_schema_health.py 校验4

### 3.2 不违反任何裁定

- ✓ 不新建 monitor_pg.py（P3-T4 裁定）
- ✓ 不建常驻采集器（trae_053）
- ✓ 不删 health_probes（RULE-THREE）
- ✓ 向内收（只改注释和 Maturity 标记，零功能改动）

### 3.3 保留协议层价值

CT-HEALTH-001 契约（12 系统三态探针）保留，未来若真需要常驻健康监控（如生产部署），协议层可直接复用，只需补采集器和消费者。

---

## 四、验收标准

- [ ] health_probes.py `[MATURITY]` 为 prototype
- [ ] health_probes.py healthz 方法有 [STUB] 注释
- [ ] health_aggregator.py L61 有 [STUB] 行内注释
- [ ] AGENTS.md §11.2 有 health_probes stub 说明
- [ ] 无功能代码改动（仅注释/标记）

---

## 五、后续触发条件

若未来满足以下任一条件，可重新评估是否激活 health_probes：
1. 项目部署到生产环境，需要常驻健康监控（此时 trae_053 可能有例外条款）
2. verify_schema_health.py 校验4 无法覆盖某些运行时场景（如 WAL 复制延迟）
3. 出现 API 消费者需求（如 dashboard 展示健康状态）

在此之前，本方案维持现状。
