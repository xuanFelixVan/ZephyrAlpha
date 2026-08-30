---
ttl: task_bound
---

> **文档元信息**（_working 临时区豁免规范，EXEMPT-ZONE-FM）：doc_type=audit_report · owner=ZephyrAlpha-Owner · language=zh · status=active · version=1.0.0 · date=2026-08-30 · topic=aiarch_residual_closure · scope=09_ai_architecture（清单 2.2/2.8/3.9 残余三件） · completes_when=Owner 审阅三件结论并裁定遗留项（P2-1 两周观测排期、2.8 SLA 连跑、3.9 长期生成器）。

# aiarch 清单残余三件收口批次报告（2026-08-30）

任务包：`docs/_working/2026-08-24-aiarch-construction-list.md` 2.2（Learn 回写残余）/ 2.8（boot watchdog 存量缺陷复核）/ 3.9（derived_graphs 6 篇）。

---

## 任务 1：fix_pattern_miner 落码（16 号文 §4.4 P2-1，MOD-INF-055 一部分）——✅ 完成

**设计声明**（16 号文 §4.4 P2-1 原文）：「`fix_pattern_miner` 周期性挖掘修复记录 → 修复策略库更新 → Diagnose 匹配命中率可观测」，验收「连续 2 周挖掘任务运行；命中率在仪表板可观测（指标只观测不设目标值）」。

**落码**（TDD：先 RED 实测 ModuleNotFoundError，后 GREEN）：
- `src/zephyr/security/ops/fix_pattern_miner.py`（新建）：纯函数 `mine_records()` 按 (fault_class, action_type) 聚簇挖掘 `data/fix_patterns/pattern_index.yaml` 修复记录 → 三类策略库更新建议（PROMOTE_PATTERN 高频高成功 / REVIEW_PATTERN 高频低成功 / ENRICH_DIAGNOSIS 诊断未覆盖簇）+ Diagnose 匹配命中率统计（总体 + 按 fault_class 分解）；`FixPatternMiner.run_once()` 单次挖掘入口，报告 append-only 落盘 `.runtime/security_ops/pattern_mining_reports.jsonl`（命中率可观测载体）。
- **不变量按 P2-1/P2-2 口径钉死**：只产建议不落策略库（A-L2 封顶，采纳 human_gated）；命中率只观测不设目标值；与既有 `auto_fix_engine/fix_pattern_miner.py`（MOD-INF-031，SQLite 数据源）互补不替代——本件挖 16 号文知识库 YAML。
- **铁律执行**：depgraph 先登记 planned（node_id=11102322，施工前）→ 验收后 planned→generated→testing（E2 裁定 testing 封顶，production 留 Owner）；文件头 [MATURITY] testing + 全标签族；错误码 ZA-SC-0038 已登记 `error_code_registry.yaml`；翻译真源条目已登记（add_module_translation，6716 条）；`security/ops/__init__.py` 导出同步。

**测试**：`tests/security/ops/test_fix_pattern_miner.py` 新建 9 用例（8 纯内存夹具 + 1 tmp_path 持久化）全绿；`tests/security/ops/` 全目录 56 件全绿（零回归）；ruff check/format 双净。
- 注：测试落点按仓内实证惯例为 `tests/security/ops/`（任务包写 `tests/zephyr/security/ops/`，该目录不存在；sibling 件 incident_pipeline/ops_maturity 测试均在前者）。

**遗留（归 Owner/后续排期）**：P2-1 验收口径「连续 2 周挖掘任务运行」需外部周期调度挂接（Windows 任务计划调 `run_once()`），本批只交付挖掘件本体；仪表板消费 jsonl 归 L6 观测面既有件演进。

## 任务 2：boot watchdog 存量缺陷复核（清单 2.8 / tracker #255①）——✅ 核销登记

**核查实证**：
1. `scripts/` 全树零命中 `09a_governance_watchdog_start`（任务包背景属实）——但**真实缺陷载体不在 scripts/**：全仓 Grep 命中 `src/zephyr/trading/lifecycle_manager.py:119`（boot 序列 09a 步 `_start_governance_watchdog`）与 `construction_workflow_sop.md` 注释。
2. 该缺陷**已于 2026-08-22 修复**：tracker #255① 状态「✅ d1a89501（sys.modules 预注册治本）」；`lifecycle_manager.py` [CHANGE-NOTE] 2026-08-22 记载 Owner 授权手术式修复（exec_module 前注册 `sys.modules`，失败回滚防半注册）。病根：`@dataclass` 处理 `X | None` 注解时 `dataclasses._is_type` 需 `sys.modules[cls.__module__].__dict__`，未注册即 NoneType AttributeError。
3. **运行时双向实证**（本批，临时探针已删）：对照组（不预注册 sys.modules 旧路径）实测复现 `AttributeError: 'NoneType' object has no attribute '__dict__'`；修复路径（现行代码同机制）加载 `scripts/governance/meta/governance_watchdog.py` + 实例化 `GovernanceWatchdog` 成功零异常（其 `ServiceRecord` 恰含 `datetime | None` 注解，为原触发面）。

**裁定**：缺陷载体存在且缺陷已修复核销——不属「载体不存在」也不属「待修复」；本批不改代码（lifecycle_manager.py 为 immutable_core，[MODIFY-GUARD] 禁 AI 自主修改，且无需改）。**残余出列**：清单 2.8 后半「冷启动 SLA 20 次连跑实测（boot P99<10s）」与「tests/automation AutoEvolution 3 项存量失败」非本任务「缺陷复核」范围，维持登记待择窗。

## 任务 3：derived_graphs 6 篇生成（00 号文 §5.2，清单 3.9）——✅ 完成

**生成器核查结论**（00 号文 §6.2 待办①实证关闭）：既有派生图生成器族（`generate_integration_topology.py` 等）按**功能域**从 depgraph PG edges 生成，**不支持跨域 AI 层视图**；`nodes.tags='ai_layer'` 实测仅 1 节点（`ml_train/ai_operator/`），标签查询暂不可派生。本批按清单口径以一次性批生成落地六篇（01 跨域拓扑由 depgraph PG 7893 节点/19846 边实测派生；02~06 由源真源施工文档既定口径派生）；长期生成器 tags 支持归后续裁定。

**六篇落盘**（`docs/02_enterprise_architecture/09_ai_architecture/derived_graphs/`，均 Mermaid 图 + 源真源表，每篇头部标注源真源 + 生成时间 2026-08-29T23:47Z + 「视图不是真源」声明）：
1. `01_ai_layer_dependency_topology.md`——15 簇跨域拓扑 + 簇清单表（模块数/蓝图/production 计数全实测；ModuleFactory 前缀 0 节点不入图如实标注）；
2. `02_runtime_orchestration_layers.md`——L1 Trae（不进代码）/L2 Ollama/L3 API 三层 + AutoRuntime Core 运营中心 + 统一入口缺口（GP1）；
3. `03_model_lifecycle_flow.md`——画像→考试→护照→门控→路由→推理→退役（GP0 手动链路已通、自动闭环 GP1+）；
4. `04_context_memory_flow.md`——build→compress→validate→inject 四段管道 + 记忆检索两源（inject 空段 GP1+）；
5. `05_multi_ai_collaboration.md`——人调度多会话时序（worktree 隔离/落盘交接/提交队列/人工裁决合并）；
6. `06_llm_security_stack.md`——L0~L8 纵深栈 + 各层代码落点与剩余缺口表 + 延迟/硬件约束口径。

## 新建/变更文件清单

| 文件 | 性质 |
|---|---|
| `src/zephyr/security/ops/fix_pattern_miner.py` | 新建（MOD-INF-055，testing） |
| `tests/security/ops/test_fix_pattern_miner.py` | 新建（9 用例） |
| `src/zephyr/security/ops/__init__.py` | 变更（导出同步） |
| `architecture_model/contracts/error_code_registry.yaml` | 变更（ZA-SC-0038 登记） |
| 翻译真源（add_module_translation 落条目） | 变更（6716 条） |
| depgraph PG node_id=11102322 | 登记 planned→testing |
| `derived_graphs/01~06`（6 篇） | 新建 |
| 本报告 | 新建 |

## 测试与验证结果

- `pytest tests/security/ops/test_fix_pattern_miner.py`：**9 passed**（RED→GREEN 全程）；
- `pytest tests/security/ops/`（含 sibling 回归）：**56 passed**；
- ruff check / format --check（新建两文件）：双净；
- watchdog 修复双向实证：旧路径复现 NoneType、修复路径加载+实例化成功（探针临时文件已删）；
- depgraph 状态机：planned→generated→testing 两步合法转换 OK（planned→testing 直达被状态机正确拒绝，已按合法路径走通）。

## 自裁定事项与理由

1. **测试落点取 `tests/security/ops/` 而非任务包字面路径**——后者目录不存在，sibling 惯例与 depgraph 既有登记均指向前者。
2. **任务 2 核销而非修复**——实证缺陷已修复（tracker #255① d1a89501 + CHANGE-NOTE + 运行时双向验证），现行代码 immutable_core 禁改；SLA 连跑/AutoEvolution 项判出本任务范围。
3. **任务 3 一次性批生成而非等长期生成器**——00 号文 §6.2 待办①实测结论为「既有生成器不支持跨域 AI 层视图」，六篇以实证数据+源真源文档既定口径派生，长期机制留裁定；六篇均在头部声明「视图不是真源」防漂移误食。
4. **miner 只产建议不落库**——16 号文 P2-2 A-L2 封顶 + ops_maturity 不变量，采纳/写库 human_gated，本件不越权。

未 commit/push（纪律遵守）；dashboard/ex_core 避让面零触碰。
