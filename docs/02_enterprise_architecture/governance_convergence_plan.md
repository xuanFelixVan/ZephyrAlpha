---
module_id: GOV-037-CONVERGENCE
doc_type: governance_convergence_plan
status: Active
version: 1.0.0
created: '2026-06-18'
last_updated: '2026-06-18'
owner: human
purpose: 治理收敛期详细工作内容，配合 architecture_upgrade_discussion.md §二十四
anti_hallucination: 本文件消除所有二元模糊地带，每个工作项有唯一编号、唯一验收标准、唯一前置条件
---

# 治理收敛期详细工作内容

> **关联文档**：`architecture_upgrade_discussion.md` §二十四（方案概要）
> **前置条件**：阶段4（搬家对齐+全量清洁）+ 阶段7（全量功能测试+规则文件格式升级）完成
> **例外**：P0 工作项不依赖阶段4/7，可立即执行
> **生命周期**：施工完成后，保留方法论和决策，删除施工细节

***

## 一、P0：修复治理基础设施自身故障（立即执行）

> **性质**：治理基础设施自身不能坏。当前 TaskRepository 导入失败，AI 被迫绕过治理（直接 SQL），形成"治理越重→绕过越多"恶性循环。
> **前置条件**：无（立即执行）
> **已建任务卡**：OPS-2026061802（核心断裂点）、OPS-2026061803（系统性批量修复）

### P0-1 修复 severity_types.py 导入链

| 项 | 内容 |
|---|------|
| 文件 | `src/zephyr/integration/shared/schema/severity_types.py` 第18行 |
| 当前 | `import_module("zephyr.data.persistence.circuit_breaker_types")` |
| 裁定 | 改为 `import_module("zephyr.governance.circuit_breaker_types")` |
| 依据 | 运行时验证可导入 + `[CONSUMERS]` 声明 + `[INVARIANTS]` 双向对齐 |
| 约束 | `[AI_AUTONOMY]=immutable_core`，需 Owner 批准 |
| 验收 | `python -c "from zephyr.governance.task_repo import TaskRepository" exit 0` |
| 任务卡 | OPS-2026061802 |

### P0-2 修复 event_store.py 导入路径

| 项 | 内容 |
|---|------|
| 文件 | `src/zephyr/governance/event_store.py` 第35行 |
| 当前 | `from zephyr.governance.persistence.sqlite_schema import ...` |
| 裁定 | 改为 `from zephyr.governance.sqlite_schema import ...` |
| 依据 | sqlite_schema.py 物理在 governance/ 根下，persistence 子包不存在 |
| 约束 | `[AI_AUTONOMY]=ai_modifiable`，但属连锁修复，建议同批 |
| 验收 | 同 P0-1 |
| 任务卡 | OPS-2026061802 |

### P0-3 批量修复 persistence 子包引用

| 项 | 内容 |
|---|------|
| 范围 | 100+ 处 `zephyr.governance.persistence.*` 引用 |
| 裁定 | 批量替换为 `zephyr.governance.*` |
| 排除 | 历史快照目录（session_logs/data/scans/data/classified/docs/08_knowledge 等） |
| 方法 | ThreadPoolExecutor(max_workers=8) + 原子写入（RULE-ONE + RULE-SEVEN） |
| 验收 | Grep `zephyr\.governance\.persistence` 全项目返回 0 匹配（排除历史快照） |
| 任务卡 | OPS-2026061803 |

### P0-4 裁定 severity_types.py AI_AUTONOMY 矛盾

| 项 | 内容 |
|---|------|
| 矛盾 | 第1行 `ai_autonomy=ai_modifiable` vs 第9行 `[AI_AUTONOMY] immutable_core` |
| 裁定原则 | 根据 onboarding_detail.md §13.1，`[AI_AUTONOMY]` 字段是权威的 |
| 处置 | 需 Owner 裁定：若 `immutable_core` 为真 → AI 不能改 P0-1；若 `ai_modifiable` 为真 → AI 可直接改 |
| 建议 | 统一为 `immutable_core`（安全敏感文件），P0-1 需 Owner 批准后执行 |

***

## 二、P1：治理瘦身（依赖阶段4搬家完成）

> **性质**：从"加规则"转向"减规则"。审计治理基础设施自身，删除零消费者且无功能价值的组件。
> **前置条件**：阶段4（搬家对齐）完成——路径稳定后才能准确审计消费者
> **原则**：应用项目自己的 RULE-THREE（删除审判三步）+ 价值判定原则（§15.4）

### P1-1 审计 384 治理脚本消费者

| 项 | 内容 |
|---|------|
| 范围 | `scripts/governance/` 下 384 个 .py 文件 |
| 方法 | 对每个脚本：Grep 全项目引用 → 统计消费者数 → 分类 |
| 分类 | A.有消费者且被门禁引用（保留）/ B.有消费者但无门禁引用（保留+接通）/ C.零消费者但有功能价值（保留+接通）/ D.零消费者且无功能价值（退役） |
| 退役标准 | RULE-THREE 三步审判全通过 + §15.4 价值判定 ALL NO |
| 目标 | 治理脚本占 scripts/ 比从 81.6% 降至 <40% |
| 验收 | 退役清单经 Owner 审批 + 退役后 `audit_registration.py` exit 0 |

### P1-2 审计 44 门禁拦截率

| 项 | 内容 |
|---|------|
| 范围 | `src/zephyr/governance/rule_enforcement/_registry.yaml` 44 个门禁 |
| 方法 | 查 gate_decisions 表统计每个 gate 的拦截次数 |
| 分类 | A.拦截>0（保留）/ B.拦截=0但有安全价值（保留）/ C.拦截=0且无安全价值（退役） |
| 退役标准 | 零拦截 + 无安全价值 + 有替代门禁覆盖 |
| 目标 | 门禁数从 44 降至 25-35（业界 CI/CD 基准 5-15 的合理扩展） |
| 验收 | 退役清单经 Owner 审批 + 退役后 Phase Manager 检查通过 |

### P1-3 合并重复规则

| 项 | 内容 |
|---|------|
| 范围 | rule-registry.md 142 条登记规则 |
| 方法 | 语义去重——检测描述相似度 >80% 的规则对 |
| 处置 | 合并重复规则，保留更严格的版本，更新 rule-registry.md |
| 目标 | 规则数从 142 降至 100-120（消除冗余，不削弱约束） |
| 验收 | `sync_rule_registry.py` exit 0 + 合并后规则覆盖原语义 |

### P1-4 冷启动步骤精简

| 项 | 内容 |
|---|------|
| 范围 | onboarding_detail.md §五 强制 Session 冷启动序列（STEP 0-6 共 ~20 步） |
| 方法 | 评估每步必要性：A.安全必需（保留）/ B.效率提升（保留）/ C.可延迟加载（改为按需）/ D.冗余（删除） |
| 目标 | 冷启动步骤从 ~20 步降至 ~10 步 |
| 验收 | 精简后冷启动时间测量 + 关键导入链验证通过 |

***

## 三、P2：建立治理 ROI 量化（依赖阶段7全量功能测试）

> **性质**：用数据驱动治理决策。没有 ROI 数据，就无法判断哪些治理有效、哪些是空转。
> **前置条件**：阶段7（全量功能测试）完成——有测试基线才能量化拦截率
> **原则**：可测量才能可管理（NIST AI RMF Measure 函数）

### P2-1 建立规则拦截日志

| 项 | 内容 |
|---|------|
| 范围 | 142 条登记规则 |
| 方法 | 在 gate_decisions 表 + rule_enforcement_log 表记录每条规则的触发和拦截 |
| 采集 | 每次门禁执行记录：rule_id / gate_id / 触发时间 / 拦截结果（pass/block） |
| 目标 | 每条规则有可查询的拦截次数 |
| 验收 | 查询任意 rule_id 能返回其历史拦截记录 |

### P2-2 建立脚本执行频率日志

| 项 | 内容 |
|---|------|
| 范围 | 384 个治理脚本 |
| 方法 | 在 governance.db 新增 script_execution_log 表 |
| 采集 | 每次脚本执行记录：script_path / 调用者 / 执行时间 / exit code |
| 目标 | 识别零调用脚本（P1-1 退役的依据） |
| 验收 | 查询任意 script_path 能返回其执行频率 |

### P2-3 建立治理开销时间统计

| 项 | 内容 |
|---|------|
| 范围 | Session 冷启动 + 单次写操作 + 任务卡建卡/完成 + Session 关门 |
| 方法 | 在 session_logs 中记录每阶段的耗时 |
| 目标 | 治理开销时间占比控制在 25-35%（业界生产系统区间） |
| 验收 | 月度报告显示治理开销占比在目标区间 |

### P2-4 建立治理绕过检测

| 项 | 内容 |
|---|------|
| 范围 | 直接 SQL INSERT/UPDATE（绕过 TaskRepository）/ 直接文件写入（绕过锁协议） |
| 方法 | DB 触发器检测非 TaskRepository 的 tasks 表写入 + 文件系统监控检测非锁协议的写入 |
| 目标 | 治理绕过次数 = 0 |
| 验收 | 月度报告显示零绕过 |

***

## 四、P3：防幻觉机制补强（依赖 P0-P1 完成）

> **性质**：从"静态规则"走向"运行时检测"。142 条静态规则未能阻止 100+ 处引用错误，需补强运行时验证。
> **前置条件**：P0（基础设施修复）+ P1（治理瘦身）完成
> **原则**：分层防御（Defense in Depth）—— Input + LLM + Output + Grounding + Monitoring

### P3-1 运行时导入健康检查

| 项 | 内容 |
|---|------|
| 范围 | Session 冷启动时自动验证关键导入链 |
| 方法 | 新增 `scripts/governance/check_import_health.py` |
| 检查项 | `from zephyr.governance.task_repo import TaskRepository` / `from zephyr.governance.event_store import EventStore` 等关键链 |
| 失败处置 | 阻止 Session 继续 + 报告断裂点 + 建议修复 |
| 目标 | 治理基础设施自身故障在 Session 启动时即被发现 |
| 验收 | 故意制造导入断裂 → 冷启动检查能捕获并报告 |

### P3-2 实时幻觉检测

| 项 | 内容 |
|---|------|
| 范围 | AI 输出中的路径/ID/命令引用 |
| 方法 | AI 输出后自动 Grep 验证引用的路径/ID/命令是否存在 |
| 检测 | 引用不存在的路径/ID/命令 → 即时阻断 + 要求修正 |
| 目标 | 幻觉率 <1%（业界 AI 代码安全漏洞基线 45%，项目目标远低于此） |
| 验收 | 注入测试：AI 引用不存在路径 → 被检测阻断 |

### P3-3 关键链形式验证

| 项 | 内容 |
|---|------|
| 范围 | 任务卡 post_sync_standard 验收命令 |
| 方法 | 扩展 post_sync_standard 从"连续 2 轮 exit 0"到"导入链形式验证" |
| 验证 | `python -c "import zephyr.governance.task_repo; import zephyr.governance.event_store; ..."` |
| 目标 | 任务完成时自动验证关键导入链完整性 |
| 验收 | 制造导入断裂 → 任务卡 transition(COMPLETED) 被拒绝 |

### P3-4 置信度评分机制

| 项 | 内容 |
|---|------|
| 范围 | AI 的每个假设/推断 |
| 方法 | `[ASSUMPTION]` 标记扩展为置信度分级（高/中/低） |
| 处置 | 低置信度 → 强制要求 Grep/Read 验证；高置信度 → 可继续但标记 |
| 目标 | 假设显式化（防幻觉 #10）的工程化升级 |
| 验收 | AI 输出中所有假设都有置信度标记 |

***

## 五、执行顺序与依赖关系

```
P0（立即，不依赖阶段4/7）
  ├─ P0-1: severity_types.py（需 Owner 批准 immutable_core）
  ├─ P0-2: event_store.py（连锁修复）
  ├─ P0-3: persistence 批量替换（脚本化）
  └─ P0-4: AI_AUTONOMY 矛盾裁定（Owner 决策）
       ↓
阶段4（搬家对齐+清洁）→ 路径稳定
       ↓
P1（依赖阶段4）
  ├─ P1-1: 审计 384 脚本消费者
  ├─ P1-2: 审计 44 门禁拦截率
  ├─ P1-3: 合并重复规则
  └─ P1-4: 冷启动精简
       ↓
阶段7（全量功能测试）→ 测试基线建立
       ↓
P2（依赖阶段7）
  ├─ P2-1: 规则拦截日志
  ├─ P2-2: 脚本执行频率日志
  ├─ P2-3: 治理开销时间统计
  └─ P2-4: 治理绕过检测
       ↓
P3（依赖 P0+P1）
  ├─ P3-1: 运行时导入健康检查
  ├─ P3-2: 实时幻觉检测
  ├─ P3-3: 关键链形式验证
  └─ P3-4: 置信度评分机制
       ↓
阶段8（业务层建设）→ 治理收敛后进入业务冲刺
```

***

## 六、验收标准汇总

| 阶段 | 验收项 | 验收命令/标准 |
|------|--------|-------------|
| P0 | TaskRepository 可导入 | `python -c "from zephyr.governance.task_repo import TaskRepository" exit 0` |
| P0 | persistence 引用清零 | Grep `zephyr\.governance\.persistence` = 0 匹配（排除历史快照） |
| P1 | 治理脚本占比下降 | scripts/ 下治理脚本占比 <40% |
| P1 | 门禁数合理 | 门禁数 25-35 个 |
| P1 | 冷启动精简 | 冷启动步骤 ~10 步 |
| P2 | 规则拦截可查 | 查询任意 rule_id 返回拦截记录 |
| P2 | 治理开销可控 | 月度治理开销占比 25-35% |
| P2 | 零绕过 | 月度治理绕过次数 = 0 |
| P3 | 导入健康检查 | 故意制造断裂 → 冷启动捕获 |
| P3 | 幻觉检测 | 注入测试 → 引用不存在路径被阻断 |

***

## 七、回滚方案

| 阶段 | 回滚方法 |
|------|---------|
| P0 | `git checkout` 恢复 severity_types.py + event_store.py + 批量替换的文件 |
| P1 | 退役清单分批执行，每批可独立回滚（`git revert`） |
| P2 | 日志表新增不删除原有数据，回滚 = 停止采集 |
| P3 | 检测脚本可独立启停，回滚 = 禁用检测 |

***

## 八、风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|:---:|:---:|------|
| P0 修改 immutable_core 文件引入新 bug | 中 | 高 | Owner 批准 + 充分测试 + 回滚方案 |
| P1 退役有用脚本导致治理失效 | 中 | 高 | RULE-THREE 三步审判 + Owner 审批 + 灰度退役 |
| P2 日志采集影响性能 | 低 | 中 | 异步采集 + 采样率可调 |
| P3 误报阻断正常开发 | 中 | 中 | 先 warn-only 模式运行 2 周，再启用阻断 |

***

## 九、业界对标参考

| 维度 | 业界标准 | 项目对标 | 来源 |
|------|---------|---------|------|
| AI 管理体系 | ISO 42001 PDCA | 五层防线 + P0-P3 收敛 | ISO/IEC 42001:2023 |
| AI 风险管理 | NIST AI RMF 4 函数 | Govern(注册表) + Map(depgraph) + Measure(P2) + Manage(P3) | NIST AI 100-1 |
| 防幻觉 | 5 大公认做法 | 18 条四层 + P3 运行时补强 | swiftflutter/AWS/Wildflare |
| 自治度分级 | L1-L5 | `[AI_AUTONOMY]` 三级（L1-L3） | arXiv 2506.22276 |
| 治理开销 | 14.5% 运行时基线 | 目标 25-35%（含冷启动） | Transactional Sandboxing |
| 规范纪律 | Spec-Driven Development | 蓝图 + 施工图模板 v4.0 | GitHub Spec Kit |
| 多 Agent 治理 | AGENTSAFE 三层控制 | A2A + RBAC + Escalation | arXiv 2512.03180 |

> **核心结论**：业界共识"Specification discipline, not model capability, is the binding constraint"——规范纪律而非模型能力是可靠性的约束瓶颈。项目治理方向正确，收敛期目标是让规范纪律从"纸面"走向"运行时"。
