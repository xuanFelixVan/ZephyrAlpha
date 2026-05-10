# 前置准备摘要 — GOV-RSTR-001

> 生成日期: 2026-05-10 | 基于蓝图版本: 3.5.0

---

## 1. 安全搬家铁律9条（§4.1b）

| # | 铁律 | 说明 | 验证方式 |
|---|------|------|---------|
| 1 | 执行前必须重新扫描目标文件的所有 import 引用 | 蓝图记录可能过时，必须现场确认 | `grep -rn "from zephyr.目标模块" src/` |
| 2 | 重复文件合并必须逐条做价值分析 | 禁止"看起来一样就直接删"——必须用 diff 确认 | 每个副本的独有 class/function 已列出 |
| 3 | 合并后必须验证内容完整性 | 对比合并前后的 class/function 列表，确认无遗漏 | `diff <(合并前grep class) <(合并后grep class)` 返回零差异 |
| 4 | import 更新必须全量验证 | 每次合并/迁移后，全项目搜索旧 import 路径，确认零残留 | `grep -r "from zephyr.旧路径" src/` 返回零结果 |
| 5 | 一次只搬一个文件 | 禁止批量合并多个重复文件；每个文件的合并/迁移是独立原子操作 | 每个任务卡仅涉及1个重复文件的合并 |
| 6 | 搬完一个验证一个 | 每完成一个文件的合并，立即运行相关测试验证 | `pytest tests/相关目录/` 返回 0 failed |
| 7 | git commit 每步必做 | 每完成一个原子操作（合并+验证），立即 git commit | `git log --oneline -1` 显示该步提交 |
| 8 | 安全优先，速度第二 | 宁可慢，不可漏；宁可多拆100个任务卡，不可一次合并10个文件 | 任务卡数量无上限 |
| 9 | 做完一个，更新一个蓝图 | 重组+蓝图更新是原子操作，不可拆分；禁止批量延迟更新蓝图 | 每个任务卡 = 一次重组 + 一次蓝图更新 + 一次验证 + 一次提交 |

---

## 2. 价值分析方法论5步（§4.1c）

对每个跨目录同名文件，必须按以下步骤做价值分析后才能决定处理方案：

| 步骤 | 名称 | 操作 |
|:----:|------|------|
| 1 | **内容对比** | 用 `diff` 对比两个同名文件，标记差异 |
| 2 | **分类判定** | 完全相同(0 diff)→保留1份，其余deprecated；re-export wrapper→保留真源；版本分叉→进入步骤3；同名不同功能→都保留，重命名消除歧义 |
| 3 | **价值提取**（仅版本分叉） | 列出副本A的独有 class/function；列出副本B的独有 class/function；列出两者共有但实现不同的 class/function |
| 4 | **归并决策** | 独有功能→迁移到真源文件；共有功能→保留更完整版本；全部独有→两个都保留，重命名 |
| 5 | **验证** | 归并后对比 class/function 列表，确认无遗漏 |

---

## 3. 强制安全协议（§11.0b）

> §4.1b 安全搬家铁律的**执行层细化**，每个任务卡必须遵守。

### Pre-flight Scan（执行前）

| # | 扫描项 | 命令 | 通过条件 |
|---|--------|------|---------|
| 1 | 扫描目标文件的所有 import 引用 | `grep -rn "from zephyr.目标模块" src/` | 输出完整引用清单，无遗漏 |
| 2 | 确认目标文件与蓝图记录一致 | `wc -l 目标文件` | 行数与蓝图记录偏差<5% |
| 3 | 确认无未提交变更 | `git status` | working tree clean |

### 执行中

| # | 约束 | 说明 |
|---|------|------|
| 1 | 一次只操作1个文件 | 禁止批量操作 |
| 2 | 每步操作后立即验证 | 运行相关测试 |
| 3 | 验证通过后立即 git commit | 提交信息包含任务卡编号 |

### Post-merge Verify（合并后）

| # | 验证项 | 命令 | 通过条件 |
|---|--------|------|---------|
| 1 | 旧 import 路径零残留 | `grep -r "from zephyr.旧路径" src/` | 返回零结果 |
| 2 | class/function 列表完整性 | `diff <(旧grep class) <(新grep class)` | 仅新增项，无删除项 |
| 3 | 相关测试全部通过 | `pytest tests/相关目录/` | 0 failed |

---

## 4. CapabilitiesManifest Schema（§3.1）

### Pydantic 模型定义

```python
class ActivationMode(str, Enum):
    ON = "on"
    OFF = "off"
    WARN_ONLY = "warn_only"
    AUTO = "auto"

class CapabilityEntry(BaseModel):
    capability_id: str           # 子系统唯一标识，如 a2a_protocol
    default_mode: ActivationMode # 默认激活模式
    auto_activation_condition: Optional[str] = None  # 自动激活条件表达式
    description: str             # 子系统功能说明
    file_count: int              # 涉及文件数（供容量估算）

class CapabilitiesManifest(BaseModel):
    version: str = "1.0.0"
    capabilities: dict[str, CapabilityEntry]  # 子系统名→配置

    def is_active(self, capability_id: str, context: dict) -> bool: ...
```

### 按需激活规则表（7个子系统）

| 子系统 | capability_id | 默认模式 | 自动激活条件 |
|--------|-------------|:---:|------|
| A2A Protocol | `a2a_protocol` | OFF | `agent_count > 3` |
| Code Dedup Engine | `code_dedup_engine` | OFF | `ai_code_duplication_rate > 0.15` |
| Chaos Engine | `chaos_engine` | OFF | `module_count > 500 OR cascade_failure_count > 2` |
| Canary Manager | `canary_manager` | OFF | `module_count > 500` |
| Feature Flag | `feature_flag` | OFF | `experiment_count > 10` |
| LSG L4-L8 | `lsg_advanced` | OFF | `agent_count > 5` |
| Budget Enforcer | `budget_enforcer_strict` | WARN_ONLY | `daily_cost_usd > 10` |

---

## 5. 附录A：同名文件清单摘要

> 扫描范围：`D:\ZephyrAlpha\src\zephyr\` 下所有 `.py` 文件（不含 `__init__.py`）。定义：同名文件出现在 2+ 个不同顶层模块目录中。

### 高副本数（≥3副本）

| 文件名 | 副本数 | 处理状态 |
|--------|:------:|:--------:|
| kill_switch | 5 | ✅ SRC-0041 已完成——shared/kill_switch.py 为统一枢纽 |
| circuit_breaker | 4 | 待处理 |
| models | 4 | 待处理 |
| cli | 3 | 待处理 |
| config | 3 | 待处理 |
| failure_matcher | 3 | 待处理 |
| health | 3 | 待处理 |
| phase_executor | 3 | 待处理 |
| secrets | 3 | 待处理 |
| task_queue | 3 | 待处理 |
| trigger_router | 3 | 待处理 |

### 2副本（50+个）

包括：alert_router, anomaly_detector, blind_spot_tracker, budget_tracker, canary_manager, cold_start, config_validator, context_package, contract_bus, cost_tracker, cross_module_integration, dashboard, data_lifecycle, drift_detector(✅已声明), event_bus(✅已声明), event_bus_upgrade(✅已声明), escalation_engine, finding, fitness_functions, handoff_manager, health_monitor, identity_verifier, integration_test_runner, knowledge_freshness, llm_impact_analyzer, pipeline_orchestrator(✅已声明), risk_limits, runbook_generator, schema_evolution, semantic_cache, token_budget, vector_bridge 等。

### 涉及目录数

跨目录同名文件涉及 `D:\ZephyrAlpha\src\zephyr\` 下的多个顶层模块目录，包括但不限于：agent_rbac, context_engine, core, governance, rollback, gates, orchestrator, shared, pipeline, db, feedback_loop, llm_security, vector_memory, mcp, infrastructure, kb, telemetry, l01_infrastructure, l12_system_telemetry 等。

---

## 6. 蓝图变更记录格式

蓝图变更记录采用 Markdown 表格格式，位于蓝图末尾 `## 变更记录` 章节。

### 格式规范

```markdown
## 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| YYYY-MM-DD | X.Y.Z | **[SRC-xxxx 完成！] 组件名 操作类型**：详细描述变更内容，包含关键数据（行数变化、文件数、测试结果等）。 |
```

### 近期变更示例

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-05-10 | 3.5.0 | **SRC-0066 完成！task_repo.py 拆分 1743→3模块**：原单体 1744 行拆分为 `base_repo.py`（314行）、`transition.py`（258行）、`query.py`（208行）。`task_repo.py` 缩减为 1106 行（-37%）。**零 breaking change**。311 个测试全部通过。 |
| 2026-05-10 | 3.4.1 | **SRC-0036 完成！event_bus 副本→shared 真源合并**：`shared/event_bus.py` 从 181 行扩展为 261 行（v0.3.0），合并 `core/events/event_bus.py` 的内容。`core/events/event_bus.py` 改为 17 行向后兼容 shim。3 个下游模块通过 shim 透明导入。 |
| 2026-05-10 | 3.4.0 | **SRC-0041 完成！kill_switch×4副本→shared真源**：`shared/kill_switch.py` 从10行re-export扩展为统一SSoT导出枢纽（39行）。121个测试全部通过。 |
| 2026-05-10 | 3.3.0 | **Phase 2c 完成！SRC-0068 10个大文件拆分评估**：新增 §3.4 评估报告——10个目标文件拆分优先级排序、策略建议、预估产出。 |
| 2026-05-10 | 3.2.0 | **Phase 2b 完成！SRC-0030~0034 drift拆分5组件全部完成**：28个 drift 相关测试全部通过。 |
| 2026-05-10 | 3.1.0 | **Phase 2 全部完成！SRC-0029: 精简 PO 为 dispatch-only**。Phase 2 总成果：7 组件全部提取完成。 |
| 2026-05-10 | 3.0.0 | **v1.5→v3.0全面重建**（major）：整合v2.0/v2.1所有内容+脱节修复后数据更新。 |

### 关键格式要点

1. **日期格式**: `YYYY-MM-DD`
2. **版本号**: 遵循 SemVer（major.minor.patch），与 blueprint frontmatter `version` 对齐
3. **变更内容**: 以粗体任务卡编号/Phase标识开头，后跟操作类型和详细数据
4. **数据引用**: 行数、文件名、测试通过数等关键指标必须定量
5. **状态标记**: 使用 `✅` 标记已完成项
6. **任务卡编号格式**: `SRC-xxxx`（4位数字）

---

## 7. 关键文件路径确认

| 文件 | 行数 | 完整绝对路径 | 关键信息 |
|------|:----:|------------|---------|
| blueprint.md (GOV-RSTR-001) | 1123 行 | `D:\ZephyrAlpha\docs\03_modules\_restructuring\blueprint.md` | v3.5.0, active, construction_progress=in_progress |
| config.py | 138 行 | `D:\ZephyrAlpha\src\zephyr\l01_infrastructure\config.py` | `load_config(config_path, env_override) -> AppConfig`, `reload_config(current, env_override) -> AppConfig`, dataclass `AppConfig` (frozen) |
| MOD-MASTER-001 | 3648 行 | `D:\ZephyrAlpha\docs\03_modules\_master-blueprint\blueprint.md` | v0.9.2, Active, 63条CT-*契约 (3 SAFE + 16 CAUTION_STUB + 2 IMPL_REQUIRED + 42 DO_NOT_CALL) |
| GOV-AI-001 | 326 行 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai-autonomy-authority-registry.md` | v1.3.0, 三层权限模型 (Immutable Core / Human-Gated / AI-Modifiable) |

### config.py 关键函数签名

```python
@dataclass(frozen=True)
class AppConfig:
    env: str = "dev"
    log_level: str = "INFO"
    data_source_priority: tuple[str, ...] = ("akshare", "tushare")

def load_config(config_path: str | None = None, env_override: bool = True) -> AppConfig:
    """解析顺序: 1.显式config_path → 2.环境变量ZEPHYR_APP_CONFIG_PATH → 3.CWD下config/zephyr_app.yaml或config/app.yaml"""
    ...

def reload_config(current: AppConfig | None = None, env_override: bool = True) -> AppConfig:
    """热重载：按上次成功加载的路径重新构建AppConfig"""
    ...
```

---

## 8. 补充发现

### 8.1 MOD-MASTER-001 关键架构信息

- **真源优先级宪章 (§零之零)**: Tier 0 (MOD-MASTER-001) > Tier 1 (architecture-model/layers/*.yaml) > Tier 2 (module blueprints) > Tier 3 (policies) > Tier 4 (code)
- **冲突裁决链**: PS-STD-005 > SYS-MASTER-001 > MOD-MASTER-001 > 模块蓝图
- **63条CT-*契约**: 其中仅3条完全落地(SAFE)，16条部分实现(CAUTION_STUB)，42条规划阶段(DO_NOT_CALL)
- **蓝图级别**: domain (Level 1)，归属 SYS-MASTER-001 (Level 0)
- **施工状态**: construction_progress = completed

### 8.2 GOV-AI-001 关键架构信息

- **三层权限模型**: Immutable Core (禁止AI修改) / Human-Gated (需Owner审批) / AI-Modifiable (AI可自主修改)
- **C轨14层**: L00(Human-Gated), L01(Human-Gated), L02(AI-Modifiable), L03(AI-Modifiable), L04(Immutable Core), L05(Human-Gated), L06(Human-Gated), L07(Human-Gated), L08(AI-Modifiable), L09(AI-Modifiable), L10(Immutable Core), L11(AI-Modifiable), L12(AI-Modifiable), L13(AI-Modifiable)
- **B轨横切**: llm_security(Immutable Core), gates(Immutable Core), db/shared/context_engine/orchestrator/feedback_loop/vector_memory/mcp(Human-Gated)
- **自动派生**: GOV-AI-001 → rbac_roles.yaml (通过 `scripts/governance/d3_metadata/derive_rbac_roles.py`)
- 旧路径 `governance/ai/ai-autonomy-authority-registry.md` 已迁移为 DEPRECATED-GOV-AI-001

### 8.3 config.py 与重组蓝图的集成点

- 蓝图 §7 集成目标中明确：`config.py` 需新增 `load_capabilities()` 函数来读取 `capabilities.yaml`
- 蓝图 §3.6 明确：capabilities.yaml 由 config.py 直接读取，不通过 MCP 协议
- 当前 config.py 仅支持单一 YAML 加载 (`config/zephyr_app.yaml` 或 `config/app.yaml`)，需要扩展支持 `src/zephyr/capabilities.yaml`

### 8.4 施工状态摘要

- **construction_status**: in_progress
- **verification_status**: unverified
- **Phase 1**: 2卡 (SRC-0021修复测试失败 ✅, SRC-0022接入LLM API)
- **Phase 2**: 12卡 (PO拆分7组件 + drift拆分5组件) — **全部完成 ✅**
- **Phase 2b**: 1卡 (SRC-0068大文件拆分评估) — **完成 ✅**
- **Phase 2c**: SRC-0066 (task_repo.py拆分) — **完成 ✅**
- **Phase 3a**: 9卡 (跨目录合并) — 部分完成 (SRC-0036 event_bus ✅, SRC-0041 kill_switch ✅)
- **Phase 3b**: 目录内部版本分叉审计 — 待执行
- **Phase 4-7**: GateEngine注册表化 / SafetyGate参数化 / capabilities.yaml / phase:future标记 — 待执行

### 8.5 容量关键指标

| 维度 | 当前规模 | 重组后目标 |
|------|:------:|:------:|
| Python文件总数 | 1,791 | ~1,570 |
| 总代码行数 | ~218,000 | ~148,000 |
| 最大单文件行数 | ~2,541 (PO) → 2,303 | ≤400 |
| >400行文件数 | 82 | ≤20 |
| >1000行文件数 | 6 | 0 |
| 跨目录重复概念数 | 75个 | 0 (每类1真源) |
