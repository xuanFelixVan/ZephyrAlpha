---
blueprint_id: MOD-INF-019
---

# ZephyrAlpha Agent Skills System

> **模块**: MOD-INF-019 (Agent Spec)
> **蓝图**: [blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/l01_infrastructure/agent-spec/blueprint.md)
> **版本**: 0.19.0

---

## AI 自主使用方法

```bash
python -m zephyr.agent_spec list      # 列出所有已注册的 Domain/Role Skills
python -m zephyr.agent_spec status    # 检查模块健康状态
```

```python
from zephyr.agent_spec.integration.pipeline_bridge import PipelineSkillBridge
bridge = PipelineSkillBridge()
result = bridge.inject_for_task(
    task_description="你的任务描述",
    stage="construction"
)
if result.loaded:
    print(result.injection_context)
```

---

## 触发表

| 阶段 | Role Skill | Domain Default |
|------|-----------|---------------|
| 想法/草稿 | architect | master-blueprint |
| 审计(施工前) | governor | gate-engine |
| 蓝图/设计 | architect | topic-match |
| 施工/实现 | implementer | module-match |
| 验收/验证 | governor | module-match |
| 审计(施工后) | governor | drift-detector |

---

## L1: Domain Skills

| Skill ID | 名称 | 触发关键词 | 模块 |
|----------|------|-----------|------|
| SKILL-DOM-DBS-001 | database-specialist | database,数据库,迁移,migration,sql,表结构 | shared/db |
| SKILL-DOM-MCP-001 | mcp-specialist | mcp,MCP,工具注册,server,protocol | mcp |
| SKILL-DOM-CTX-001 | context-specialist | context,上下文,pipeline,管线 | context_engine |
| SKILL-DOM-FBL-001 | feedback-specialist | feedback,反馈,根因,5whys,治根,诊断反转 | feedback_loop |
| SKILL-DOM-GAT-001 | gate-specialist | gate,门禁,规则,policy,验收 | gates |
| SKILL-DOM-AGT-001 | agent-specialist | permission,权限,rbac,RBAC | agent_rbac |
| SKILL-DOM-BLU-001 | master-blueprint | blueprint,蓝图,架构,设计,拆分 | master-blueprint |
| SKILL-DOM-DRF-001 | drift-detector | audit,审计,漂移,合规,治理 | drift_detector |
| SKILL-DOM-KNW-001 | knowledge-specialist | knowledge,知识库,知识,KE | kb |
| SKILL-DOM-RBK-001 | rollback-specialist | rollback,回滚,撤销,undo,revert,checkpoint,检查点 | rollback |
| SKILL-DOM-LSG-001 | lsg-security | security,安全,lsg,注入,injection,脱敏,越狱 | llm_security |
| SKILL-DOM-VMS-001 | vector-memory | vector,向量,memory,chroma,embedding,语义搜索 | vector_memory |
| SKILL-DOM-TSK-001 | task-system | task,任务,任务卡,taskcard | task_repo |
| SKILL-DOM-TEL-001 | system-telemetry | telemetry,遥测,可观测,指标,metrics,日志,健康检查 | telemetry |
| SKILL-DOM-DED-001 | code-dedup-engine | dedup,去重,重复,duplicate,monoculture | dedup |
| SKILL-DOM-BGT-001 | budget-enforcer | budget,预算,cost limit,token limit | budget |
| SKILL-DOM-AFX-001 | auto-fix-engine | fix,repair,self-heal,修复,故障 | auto_fix |
| SKILL-DOM-A2A-001 | a2a-protocol | a2a,agent-to-agent,agent_coordination,多agent,多智能体,协调,冲突,conflict | a2a_protocol |
| SKILL-DOM-BEH-001 | behavioral-auditor | behavioral,越权,behavior audit,行为边界,AI安全审计,操作越界,未经授权 | behavioral_auditor |

---

## L2: Role Skills

| Role | 职责 | 约束 | 工具 |
|------|------|------|------|
| architect | 蓝图解读、接口设计、架构决策 | 只读蓝图、不写代码、产出 KB 决策记录 | blueprint_search, kb_query, read_file |
| implementer | 代码实现、测试编写、Lint 修复 | 必须通过 Gate 校验后才可写入 | read_file, write_file, search_replace, run_command |
| governor | 审计扫描、漂移修复、合规检查 | 不可修改业务代码 | governance_scan, drift_fix, audit_report |

---

## L3: Cold Memory

- **蓝图全文**: MCP Blueprint Search Server
- **历史 Session**: session-logs/ YAML 归档
- **审计报告**: docs/09_audit/reports/
- **向量记忆**: InProcessVectorMemory — vector_memory/ 11 子模块（Vector+BM25+RRF 混合检索）

> 完整架构、四层渐进披露、SpecEngine 流程、依赖关系 → 见 [blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/l01_infrastructure/agent-spec/blueprint.md)
