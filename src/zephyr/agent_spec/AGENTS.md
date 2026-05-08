# ZephyrAlpha Agent Skills System

> **模块**: MOD-INF-019 (Agent Spec)
> **版本**: 0.18.0
> **总 Token 预算**: ~9600 tokens (L0:800 + L1:500/skill + L2:300/skill + L3:8000)

---

## ⚡ 新 AI 入群必读：Skill 自动发现与加载

**本系统已集成到 Pipeline**：每次 `PipelineOrchestrator.dispatch()` 执行时，
会根据 TaskCard 的 `description`/`tags`/`stage` 自动通过 `PipelineSkillBridge`
匹配并注入对应的 Domain Skill + Role Skill 到模块执行上下文。

### AI 自主使用方法
```bash
python -m zephyr.agent_spec list      # 列出所有已注册的 Domain/Role Skills
python -m zephyr.agent_spec status    # 检查模块健康状态
```

### Python API 自主调用
```python
from zephyr.agent_spec.integration.pipeline_bridge import PipelineSkillBridge
bridge = PipelineSkillBridge()
result = bridge.inject_for_task(
    task_description="你的任务描述",
    stage="construction"  # idea|blueprint|construction|verification|audit
)
if result.loaded:
    print(result.injection_context)  # 直接注入到你的工作上下文
```

### 何时应该使用 agent-spec
- 当你不确定某个模块的特定约束/陷阱时 → 加载对应的 Domain Skill
- 当你不确定当前阶段应该执行什么流程时 → 查看触发表匹配 Role Skill
- 当你需要了解"这段代码写完要做什么检查"时 → 加载对应 Role Skill
- 任何涉及 `database|migration|sql|mcp|context|feedback|gate|rbac|blueprint|audit|rollback|vector|a2a` 的任务

---

## L0: Constitution (~800 tokens, always loaded)

### 项目拓扑与首关路径索引

```
ZephyrAlpha/
├── src/zephyr/          # 核心源码（19+ 模块）
│   ├── core/            # 会话连续性 + 蓝图分解
│   ├── context_engine/  # 上下文组装/注入/裁剪
│   ├── db/              # SQLite 数据库 + ATM
│   ├── gates/           # Gate G0-G9 门控引擎
│   ├── orchestrator/    # Agent 编排器
│   ├── pipeline/        # 管道编排器
│   ├── feedback_loop/   # 反馈闭环
│   ├── kb/              # 知识库管道
│   ├── vector_memory/   # VMS 向量记忆服务 (MOD-INF-011)
│   ├── mcp/             # MCP 服务器
│   ├── llm_security/    # LLM 安全
│   ├── shared/          # 共享基础库
│   └── ...
├── docs/                # 文档与蓝图
├── tests/               # 全量测试
├── scripts/             # 治理脚本
├── config/              # 运行时配置
└── AGENTS.md            # 本文件
```

### 标准命令

```bash
# 构建/测试/Lint
python scripts/governance/run_all.py      # 完整治理扫描
python scripts/arch_guard/run_all.py      # 架构守卫
pytest tests/ -x --tb=short               # 单元测试
pytest tests/integration/ -x --tb=short    # 集成测试
python scripts/governance/env_check.py     # 环境检查
```

### 会话恢复协议

1. 读 `session-logs/` 找最新 session
2. 读 `_journals/checkpoint_*.json` 找中断层
3. 加载对应蓝图和任务卡
4. 重建 SessionContinuity 上下文

### 触发表（浓缩版）

| 阶段 | Role Skill | Domain Default |
|------|-----------|---------------|
| 想法/草稿 | architect | master-blueprint |
| 审计(施工前) | governor | gate-engine |
| 蓝图/设计 | architect | topic-match |
| 施工/实现 | implementer | module-match |
| 验收/验证 | governor | module-match |
| 审计(施工后) | governor | drift-detector |

---

## L1: Domain Skills (loaded on trigger match, ~500 tokens each)

| Skill ID | 名称 | 触发关键词 | 模块 |
|----------|------|-----------|------|
| SKILL-DOM-DBS-001 | database-specialist | database,migration,sql,ATM | shared/db |
| SKILL-DOM-MCP-001 | mcp-specialist | mcp,server,tool,protocol | mcp |
| SKILL-DOM-CTX-001 | context-specialist | context,pipeline | context_engine |
| SKILL-DOM-FBL-001 | feedback-specialist | feedback,loop | feedback_loop |
| SKILL-DOM-GAT-001 | gate-specialist | gate,rule,policy | gates |
| SKILL-DOM-AGT-001 | agent-specialist | permission,rbac | agent_rbac |
| SKILL-DOM-BLU-001 | master-blueprint | blueprint | master-blueprint |
| SKILL-DOM-DRF-001 | drift-detector | audit,compliance,governance | drift_detector |
| SKILL-DOM-KNW-001 | knowledge-specialist | knowledge,KE | kb |
| SKILL-DOM-RBK-001 | rollback-specialist | rollback,undo,revert,checkpoint | rollback |
| SKILL-DOM-VMS-001 | vector-memory | vector,memory,vms,chroma,chromadb,embedding | vector_memory |
| SKILL-DOM-A2A-001 | a2a-protocol | a2a,agent-to-agent,agent_coordination,多agent,多智能体,协调,冲突,conflict | a2a_protocol |
| SKILL-DOM-BEH-001 | behavioral-auditor | behavioral,越权,behavior audit,行为边界,AI安全审计,操作越界,未经授权 | behavioral_auditor |

---

## L2: Role Skills (loaded in combination with Domain, ~300 tokens each)

### architect
- **职责**: 蓝图解读、接口设计、架构决策
- **约束**: 只读蓝图、不写代码、产出 KB 决策记录
- **工具**: blueprint_search, kb_query, read_file

### implementer
- **职责**: 代码实现、测试编写、Lint 修复
- **约束**: 必须通过 Gate 校验后才可写入
- **工具**: read_file, write_file, search_replace, run_command

### governor
- **职责**: 审计扫描、漂移修复、合规检查
- **约束**: 不可修改业务代码
- **工具**: governance_scan, drift_fix, audit_report

---

## L3: Cold Memory (MCP on-demand retrieval, ~8000 tokens)

- **蓝图全文**: 通过 MCP Blueprint Search Server 检索
- **历史 Session**: session-logs/ 中的 YAML 归档
- **审计报告**: docs/09_audit/reports/ 中的 Markdown 报告
- **知识图谱**: ChromaDB 向量存储（KB-legacy） + VMS (MOD-INF-011) 8 Collection 主向量后端 + GraphValidator
- **向量记忆**: InProcessVectorMemory 统一入口 — vector_memory/ 11 子模块（Vector+BM25+RRF 混合检索）
