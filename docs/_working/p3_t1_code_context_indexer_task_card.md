---
module_id: MOD-DB_DEPGRAPH_OPT
title: "P3-T1 改造任务卡 — VMS code_context indexer（AST-aware 分块 + reconciler 事件驱动）"
doc_type: construction_plan
status: Suspended
version: "1.1.0"
layer: cross_layer
blueprint_level: sub_module
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260628-P3T1
date: "2026-06-28"
valid_from: "2026-06-28"
ttl: task_bound
completes_when: "code_context indexer 实现完成 + 注册为 GATE-CODE-CONTEXT reconciler + 测试通过 + AGENTS.md 登记"
belongs_to: "MOD-DB_DEPGRAPH_OPT"
parent_module: "SH-DB-001"
scope: global
stability: evolving
verifiability: automated
construction_progress: planned
priority: P2
runtime_plane: hot
depends_on:
  - {target: "MOD-DB_DEPGRAPH_OPT", at: "§裁定记录", why: "P3 裁定 T1 改造方向——扩展 VMS 不建 pgvector"}
  - {target: "MOD-INF-011", at: "全篇", why: "VMS 蓝图——code_context collection 真源"}
references:
  - {id: "MOD-DB_DEPGRAPH_OPT", at: "§P3-T1", why: "P3 方案裁定——本任务卡的来源"}
  - {id: "trae_053_automation_dual_track", at: "全篇", why: "自动化双轨约束——reconciler 事件驱动"}
---

# P3-T1 改造任务卡 — VMS code_context indexer

> 真源裁定：[P3方案 §裁定记录](../03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p3_postgresql_optimization.md)
> 自动化约束：[trae_053](../01_policies_and_standards/rules/trae_053_automation_dual_track.yaml) — 事件驱动，非常驻

---

## §0 第二轮第一性原理审查裁定（2026-06-28，暂缓施工）

> **本任务卡当前状态：Suspended（暂缓施工）**。消费方就绪前禁止施工。
> 下方原始设计文档保留作为审查过程证据，**不代表当前可施工方案**。

### 0.1 审查发现的 5 个根本性问题

| # | 问题 | 严重度 | 证据 |
|---|------|--------|------|
| Q1 | **元问题不成立**：trae IDE 内置 `SearchCodebase` 工具已是语义搜索（基于 embedding model 套件 + 实时代码库索引），覆盖 src/zephyr/，零成本零维护。任务卡 §1.1 立论"项目没有按语义找代码的能力"被证伪 | 致命 | [.trae/rules/project_rules.md](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) RULE-EIGHT 强制 AI 使用 SearchCodebase |
| Q2 | **code_context collection 零真实消费方**：全项目 `grep .search("code_context")` No matches。CE（context_engine.py）是 stub 不调 VMS，`readers=["CE"]`（collection_manager.py:181）是画饼。建 indexer = 往黑洞灌数据 | 致命 | [context_engine.py](file:///d:/ZephyrAlpha/src/zephyr/shared/context_engine.py) 是 stub |
| Q3 | **writer 路径错误会制造 90 天重复垃圾**：任务卡原设计用 `write_with_provenance`，其实现是 `col.add + uuid` doc_id（[collection_manager.py:446-468](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/collection_manager.py#L446)），同一函数 commit N 次堆 N 份重复 doc，90 天才清理。正确范式是 [kb_repo._upsert_vector](file:///d:/ZephyrAlpha/src/zephyr/intelligence/model_evaluation/kb_repo.py#L399) 的 `col.upsert + 确定性业务 id` | 致命 | collection_manager.py 第 446-468 行 vs kb_repo.py 第 399-432 行 |
| Q4 | **AST 分块过度工程**：[symbol_index.py](file:///d:/ZephyrAlpha/src/zephyr/governance/symbol_index.py) 已有 AST 解析能力，[chunk_strategy_router.py:74-85](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/chunk_strategy_router.py#L74) ast_aware 分支未实现。在消费方为零时实现 AST 切分是空转 | 中 | symbol_index.py 已覆盖符号查询场景 |
| Q5 | **向内收违反**：已有 trae SearchCodebase（L1 IDE 场景）+ symbol_index（符号查询场景），任务卡忽略两者新建 indexer | 中 | 四大逻辑审核结论 |

### 0.2 裁定结论

**P3-T1 code_context indexer：暂缓施工**

理由（基于第一性原理）：
1. **消费方为零**——建 indexer 是往黑洞灌数据，违反 RULE-THREE 功能价值审判
2. **已有现成能力**——trae SearchCodebase 已覆盖 L1 IDE 场景语义搜索，零成本零维护
3. **writer 路径错误未修复**——若现在施工会制造 90 天重复垃圾

### 0.3 解除暂缓的前置条件

满足以下任一条件后方可重新评估施工：

1. **CE 接入 VMS**：[context_engine.py](file:///d:/ZephyrAlpha/src/zephyr/shared/context_engine.py) 从 stub 升级为真实接入 VMS/hybrid_retriever，code_context 成为 CE 的真实数据源
2. **Agent 增加 code_search 工具**：autonomy_core 的 Agent 工具集新增 `code_search` 工具，显式消费 code_context collection

### 0.4 若施工的硬约束

解除暂缓后若施工，必须遵守：

1. **writer 路径**：必须用 `col.upsert + 确定性业务 id`（如 `f"{file_path}::{symbol_name}::{start_line}"`），**禁用** `write_with_provenance` 的 `col.add + uuid` 路径
2. **AST 分块**：扩展 [chunk_strategy_router.py](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/chunk_strategy_router.py) 的 `_ast_aware_chunk` 方法（当前 stub），**禁用**新建独立分块函数
3. **复用 symbol_index**：AST 解析逻辑复用 [symbol_index.py](file:///d:/ZephyrAlpha/src/zephyr/governance/symbol_index.py) 的 `ast.parse + ast.walk` 模式
4. **reconciler 注册**：GATE-CODE-CONTEXT reconciler 仅在消费方就绪后注册，避免死代码

### 0.5 关联遗留项

- **write_with_provenance 治本**（独立任务，非本任务卡范围）：[collection_manager.py:446-468](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/collection_manager.py#L446) 的 `col.add + uuid` 路径是 VMS 全局设计缺陷，影响所有 HOT collection（decisions/lessons/knowledge/rules/code_context）。需单独立任务卡评估对已有数据的影响
- **AGENTS.md §11.2 遗留项登记**：本裁定已登记到 [AGENTS.md](file:///d:/ZephyrAlpha/AGENTS.md) §11.2 P3 遗留项章节

---

## §1 原始设计文档（保留作为审查过程证据，非当前可施工方案）

> ⚠️ 以下内容是第二轮审查前的原始设计，存在上述 5 个根本性问题。
> 仅作为审查过程证据保留，**不代表当前可施工方案**。
> 解除暂缓条件见 §0.3，施工硬约束见 §0.4。

---

## 一、任务背景与第一性原理

### 1.1 元问题

**AI 在 100% 自动开发项目里，如何"按语义查找代码"？**

当前现状：
- 项目有 6429 个 depgraph 节点，`src/zephyr/` 下数百个 .py 文件
- AI 想找"实现向量检索的代码在哪"、"谁调用了 embedding_router"——只能靠 grep（精确字符串）或读 AGENTS.md
- **没有"按语义找代码"的能力**：AI 想找"处理死锁的代码"时，grep "deadlock" 会漏掉 `check_pg_runtime_health`（用 `pg_stat_database.deadlocks` 但函数名不含 deadlock）

### 1.2 真正的空白

VMS 已有 8 大 collection，其中 `code_context` collection：
- **schema 已定义**（[collection_schemas.py:68-78](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/collection_schemas.py)）：1024d BGE-M3、ast_aware 分块、ttl 90 天
- **检索已就绪**：[hybrid_retriever.py](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/hybrid_retriever.py) 已支持 code_context 的 dense+BM25+时间衰减检索
- **但 indexer 零写入者**——collection 是空的，检索不到任何东西

**治本**：补 code_context indexer，让 collection 有数据。**不建 pgvector**（VMS 已是更强体系，pgvector 是降级重复造轮子）。

### 1.3 裁定依据（来自 P3 第一性原理审查）

| 维度 | pgvector 方案（原 P3-T1） | VMS code_context indexer（本任务卡） |
|------|--------------------------|--------------------------------------|
| 向量模型 | all-MiniLM-L6-v2 384d | BGE-M3 1024d（更强） |
| 检索能力 | 纯余弦 | Hybrid = Vector HNSW + BM25 + RRF + 时间衰减 + reranker |
| 存储 | PostgreSQL 扩展 | ChromaDB（已部署，已有 8 collection） |
| 真源唯一 | 第二套向量库（违反） | 复用 VMS 唯一真源 |
| 自动维护 | 手动跑 update_embeddings.py | reconciler 事件驱动（commit 触发） |
| AI 可发现 | 未注册 AGENTS.md | 注册 AGENTS.md + reconciler 清单 |

---

## 二、调研结论（已完成）

### 2.1 code_context collection 现状

- **schema 真源**：[collection_schemas.py:171-181](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/collection_manager.py) + [collection_schemas.py:68-78](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/collection_schemas.py)
- 字段：`dimension=1024`、`chunk_strategy=ast_aware`、`ttl_days=90`、`embedding_model=BAAI/bge-m3`、`writers=["ScriptSystem","Orchestrator"]`、`readers=["CE"]`
- **indexer 缺口**：全仓搜索确认零写入者，collection 实际为空

### 2.2 复用模式：sync_engine.py（KB→VMS）

现有两个 indexer（[memory_writer.py](file:///d:/ZephyrAlpha/src/zephyr/trading/orchestrator/memory_writer.py)、[sync_engine.py](file:///d:/ZephyrAlpha/src/zephyr/intelligence/model_evaluation/sync_engine.py)）模式高度一致。code_context indexer 复用 sync_engine 模式（"从持久化源读记录→逐条写 VMS"）。

**现有 indexer 的两个缺陷，本 indexer 必须改进**：
1. 现有 indexer 用 `InMemoryFakeVMS()`（数据不落 ChromaDB）→ 本 indexer 用 `ServiceRegistry.get("vector-memory")` 取真实 VMS
2. 现有 indexer metadata 无 provenance → 本 indexer metadata 必须带 `provenance`（否则过不了 `validate_provenance`）

### 2.3 AST 分块缺口

- [chunk_strategy_router.py:74-85](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/chunk_strategy_router.py) 的 `ast_aware` 分支**未实现**，落到 `_default_chunk` 500字符定长切分
- [symbol_index.py:32-55](file:///d:/ZephyrAlpha/src/zephyr/governance/symbol_index.py) 有 AST 解析能力（`ast.parse` + `ast.walk`），但只建符号表，不提取源码片段
- **结论**：indexer 需自己实现 AST 分块（参考 symbol_index 的 ast.parse 模式，扩展为提取函数/类源码片段）

### 2.4 ReconciliationRegistry 注册模式

- 真源：[reconciliation_registry.py](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py)
- 注册：`_register_default_reconcilers()` 工厂闭包模式，10 个已注册
- trigger：Python 谓词 `(committed_files: list[str]) -> bool`
- 触发：post-commit，非阻断，锁外运行
- **code_context 应做 reconciler**（非 pre-commit hook）：派生产物对账语义匹配，且 gateway 用 `--no-verify` 会绕过 pre-commit hook
- **不 auto-commit**：code_context 索引落 `data/vector_db/`（已被 .gitignore），无需 git commit

### 2.5 关键 API

- **写入入口**：`InProcessVectorMemory.write(collection_name, content, metadata)` ([in_process_vector_memory.py:253-269](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/in_process_vector_memory.py))
  - 内部调 `write_with_provenance`，强制 metadata 含 `provenance`/`origin`
  - 自动加 `written_at`（时间衰减用）
  - 自动调 `embedding_router.embed(content, collection_name)` 生成 1024d 向量
- **获取 VMS 实例**：`ServiceRegistry.get("vector-memory")`

---

## 三、施工方案

### 3.1 架构设计

```
开发者 commit src/zephyr/xxx.py
        │
        ▼
GitCommitGateway.commit()
        │ (post-commit, 锁外)
        ▼
ReconciliationRegistry.reconcile_for(committed_files)
        │ trigger: committed_files 含 src/zephyr/**/*.py
        ▼
GATE-CODE-CONTEXT reconciler
        │
        ├─ 1. 筛出 .py 文件（src/zephyr/ + scripts/governance/）
        ├─ 2. AST 解析 → 切出函数/类源码片段
        ├─ 3. 构造 metadata（provenance/file_path/symbol_name/symbol_type）
        ├─ 4. ServiceRegistry.get("vector-memory").write("code_context", content, metadata)
        └─ 5. 报告落盘 .runtime/reconcile_reports/code_context_<ts>.json
```

### 3.2 白名单文件（向内收，只改现有文件 + 最小新增）

| 文件 | 操作 | 说明 |
|------|------|------|
| [chunk_strategy_router.py](file:///d:/ZephyrAlpha/src/zephyr/governance/vector_memory/chunk_strategy_router.py) | **修改** | 实现 `ast_aware` 分支（当前是 stub，落到 _default_chunk） |
| [reconciliation_registry.py](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py) | **修改** | 新增 `make_code_context_reconciler()` 工厂函数 |
| [git_commit_gateway.py](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) | **修改** | `_register_default_reconcilers()` 加一行注册 |
| `src/zephyr/governance/vector_memory/code_context_indexer.py` | **新建** | indexer 核心：AST 分块 + 写 VMS（参考 sync_engine 模式） |
| [AGENTS.md](file:///d:/ZephyrAlpha/AGENTS.md) | **修改** | §11.2 登记 GATE-CODE-CONTEXT reconciler |

**禁止新建**：pgvector 扩展、code_embedding.py（P3 原计划名）、nodes.embedding 列、第二套向量库

### 3.3 AST-aware 分块设计（chunk_strategy_router.py 改造）

**当前问题**：`route()` 第74-85行，`ast_aware` 落到 `_default_chunk` 500字符定长切分，与 schema 声明的"func/class AST 分块"不符。

**改造方案**：在 `ChunkStrategyRouter` 新增 `_ast_aware_chunk` 方法：

```python
def _ast_aware_chunk(self, source: str, file_path: str = "") -> list[Chunk]:
    """AST-aware 分块：按函数/类切分，每块含签名+docstring+体。
    
    设计原则（第一性原理）：
    - 一个函数/类 = 一个 chunk（语义完整，embedding 质量高）
    - chunk 含签名+docstring+体（检索时能理解"这个函数做什么"）
    - 超长函数（>2000字符）不切分（保持语义完整，靠 BGE-M3 长上下文）
    - 模块级代码（import/常量/赋值）合并为一个"module_header" chunk
    """
    import ast
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return self._default_chunk(source, "ast_aware")  # 降级
    
    chunks = []
    # 模块级代码（import + module 常量 + module docstring）
    module_lines = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign, ast.Expr)):
            start = node.lineno - 1
            end = getattr(node, 'end_lineno', start + 1)
            module_lines.extend(source.splitlines()[start:end])
    if module_lines:
        chunks.append(Chunk(
            text="\n".join(module_lines)[:2000],
            strategy="ast_aware",
            index=0,
            metadata={"symbol_type": "module_header", "file_path": file_path}
        ))
    
    # 函数和类
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1
            end = getattr(node, 'end_lineno', start + 1)
            lines = source.splitlines()[start:end]
            chunk_text = "\n".join(lines)[:2000]  # 截断保护
            symbol_type = "class" if isinstance(node, ast.ClassDef) else "function"
            chunks.append(Chunk(
                text=chunk_text,
                strategy="ast_aware",
                index=len(chunks),
                metadata={
                    "symbol_type": symbol_type,
                    "symbol_name": node.name,
                    "file_path": file_path,
                    "start_line": node.lineno,
                    "end_line": end,
                }
            ))
    return chunks if chunks else [Chunk(text=source[:2000], strategy="ast_aware", index=0)]
```

**关键设计决策**：
- **不切分超长函数**：BGE-M3 支持 8192 token，2000字符在能力范围内，切分会破坏语义
- **模块级代码合并**：import + 常量 + module docstring 合为一个 chunk，避免碎片化
- **降级机制**：SyntaxError 时降级为 _default_chunk（保证不阻断 commit）

### 3.4 code_context_indexer.py 设计

参考 [sync_engine.py](file:///d:/ZephyrAlpha/src/zephyr/intelligence/model_evaluation/sync_engine.py) 模式：

```python
# [BLUEPRINT] MOD-INF-011 | docs/03_modules/_domain-knowledge/vector-memory/blueprint.md
# [MODULE] zephyr.governance.vector_memory.code_context_indexer
# [DOMAIN] D-KNOWLEDGE
# [CONSUMERS] GitCommitGateway GATE-CODE-CONTEXT reconciler
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] code_context collection 是代码语义检索唯一真源; 复用 VMS 不建第二套向量库
# [MODIFY-GUARD] reconciliation_registry.py (reconciler 工厂)
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] VMS不可用→degraded不阻断commit; AST解析失败→降级定长切分
# [TTL] task_bound
"""
code_context_indexer — 源码 AST 分块 → VMS code_context collection

事件驱动：GitCommitGateway post-commit reconciler 触发（非常驻）
复用真源：VMS (ChromaDB + BGE-M3 + Hybrid Retriever)，不建 pgvector
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from pathlib import Path

from zephyr.shared.registry import ServiceRegistry
from zephyr.governance.vector_memory.chunk_strategy_router import ChunkStrategyRouter

_logger = logging.getLogger(__name__)
_router = ChunkStrategyRouter()

# 白名单：只索引 src/zephyr/ 和 scripts/governance/ 下的 .py
_INDEX_SCOPES = ("src/zephyr/", "scripts/governance/")
# 排除：测试文件、__pycache__、生成器产物
_EXCLUDE_PATTERNS = ("test_", "_test.py", "__pycache__", "/generators/")


@dataclass
class IndexResult:
    indexed: int = 0
    skipped: int = 0
    status: str = "ok"  # ok / degraded / skipped
    error: str = ""


def _should_index(rel_path: str) -> bool:
    """判断文件是否在索引范围内。"""
    if not rel_path.endswith(".py"):
        return False
    if not any(rel_path.startswith(s) for s in _INDEX_SCOPES):
        return False
    if any(p in rel_path for p in _EXCLUDE_PATTERNS):
        return False
    return True


def index_files_to_vms(file_paths: list[str], repo_root: str) -> IndexResult:
    """将给定文件 AST 分块后写入 VMS code_context collection。
    
    入口：reconciler 调用，传入本次 commit 涉及的 .py 文件绝对路径列表。
    幂等性：同文件重复索引会产生新 doc_id（code_context ttl 90 天，过期自动清理）。
    降级：VMS 不可用 → status=degraded，不阻断 commit。
    """
    try:
        vms = ServiceRegistry.get("vector-memory")
    except Exception as e:
        _logger.warning("code_context_indexer: VMS 不可用，跳过: %s", e)
        return IndexResult(status="degraded", error=str(e))
    
    result = IndexResult()
    router = ChunkStrategyRouter()
    
    for abs_path in file_paths:
        rel = str(Path(abs_path).relative_to(repo_root)).replace("\\", "/")
        if not _should_index(rel):
            result.skipped += 1
            continue
        try:
            source = Path(abs_path).read_text(encoding="utf-8")
            chunks = router.route(source, "ast_aware")
            for chunk in chunks:
                meta = {
                    "provenance": f"code_indexer:{rel}:{chunk.metadata.get('symbol_name', 'module')}",
                    "file_path": rel,
                    "symbol_name": chunk.metadata.get("symbol_name", ""),
                    "symbol_type": chunk.metadata.get("symbol_type", ""),
                    "start_line": chunk.metadata.get("start_line", 0),
                    "indexer_version": "1.0",
                }
                vms.write("code_context", chunk.text, metadata=meta)
                result.indexed += 1
        except Exception as e:
            _logger.warning("code_context_indexer: 索引 %s 失败: %s", rel, e)
            result.skipped += 1
    
    _logger.info("code_context_indexer: indexed=%d skipped=%d status=%s",
                 result.indexed, result.skipped, result.status)
    return result
```

**关键设计**：
- **幂等性**：重复索引产生新 doc_id，靠 ttl 90 天自动清理旧版本（不搞复杂 upsert）
- **降级**：VMS 不可用 → status=degraded，不阻断 commit（reconciler 非阻断语义）
- **provenance**：`code_indexer:<file_path>:<symbol>` 满足 `validate_provenance`
- **白名单**：只索引 `src/zephyr/` 和 `scripts/governance/`，排除测试/生成器

### 3.5 reconciler 注册（reconciliation_registry.py 改造）

新增工厂函数 `make_code_context_reconciler`：

```python
def make_code_context_reconciler(gateway) -> ReconcilerSpec:
    """GATE-CODE-CONTEXT: commit 涉及 src/zephyr/ 或 scripts/governance/ 下 .py 时，
    AST 分块后写入 VMS code_context collection（事件驱动，非 auto-commit）。
    
    裁定背景：P3-T1 改造，替代原计划 pgvector（重复造轮子）。
    自动化：trae_053 事件驱动（post-commit），非常驻。
    """
    project_root = gateway.project_root
    
    def trigger(committed_files: list[str]) -> bool:
        for rel in committed_files:
            if rel.endswith(".py") and (rel.startswith("src/zephyr/") or rel.startswith("scripts/governance/")):
                return True
        return False
    
    def reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        from zephyr.governance.vector_memory.code_context_indexer import index_files_to_vms
        abs_files = [str(Path(project_root) / rel) for rel in committed_files if rel.endswith(".py")]
        result = index_files_to_vms(abs_files, str(project_root))
        detail = f"indexed={result.indexed} skipped={result.skipped} status={result.status}"
        # 报告落盘（复用 gateway._write_reconcile_report）
        gateway._write_reconcile_report("code_context", {"detail": detail, "result": result.__dict__}, session_id)
        if result.status == "degraded":
            return ReconcileResult(action="warn", detail=detail)
        return ReconcileResult(action="clean", detail=detail)
    
    return ReconcilerSpec(
        gate_id="GATE-CODE-CONTEXT",
        trigger=trigger,
        reconcile=reconcile,
        priority=220,  # 在 path_tree(150)/manifest(100) 之后，baseline_aware(200) 附近
    )
```

在 [git_commit_gateway.py](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py) `_register_default_reconcilers()` 加一行：
```python
self._reconciliation_registry.register(make_code_context_reconciler(self))
```

### 3.6 不 auto-commit 的理由

- code_context 索引落 `data/vector_db/`（ChromaDB PersistentClient）
- `data/vector_db/` 已被 [.gitignore:197](file:///d:/ZephyrAlpha/.gitignore) 排除
- 索引是 runtime 派生物，无需入 git 历史
- 与 GATE-GHOST/GATE-REG-BL 同属"非阻断报告类"

---

## 四、验收标准

### 4.1 功能验收

```powershell
# 1. 单元测试：AST 分块
python -m pytest tests/test_chunk_strategy_router.py -k ast_aware -v

# 2. 单元测试：indexer
python -m pytest tests/test_code_context_indexer.py -v

# 3. 集成测试：reconciler 注册
python -c "from zephyr.governance.git_commit_gateway import GitCommitGateway; gw = GitCommitGateway(); print('CODE-CONTEXT' in str(gw._reconciliation_registry.list_gate_ids()))"

# 4. 端到端：commit 一个 .py 文件，验证 code_context 有数据
python -c "
from zephyr.shared.registry import ServiceRegistry
vms = ServiceRegistry.get('vector-memory')
col = vms._collection_manager.get_collection('code_context')
print('code_context count:', col.count())
"
```

### 4.2 治理验收

- [ ] chunk_strategy_router.py 的 ast_aware 分支不再落到 _default_chunk
- [ ] code_context_indexer.py 头部 manifest 完整（[BLUEPRINT]/[MODULE]/[INVARIANTS]/...）
- [ ] reconciliation_registry.py 导出 make_code_context_reconciler
- [ ] git_commit_gateway.py `_register_default_reconcilers` 含注册行
- [ ] AGENTS.md §11.2 登记 GATE-CODE-CONTEXT
- [ ] 无新建 pgvector / code_embedding.py / nodes.embedding 列

### 4.3 自动化约束验收

- [ ] indexer 事件驱动（post-commit reconciler），非常驻进程
- [ ] 无定时触发（无 --watch / --interval / sleep loop）
- [ ] VMS 不可用时降级不阻断 commit
- [ ] 新 AI 可通过 AGENTS.md §11.2 发现此能力

---

## 五、回滚方案

1. 从 `_register_default_reconcilers()` 删除 `make_code_context_reconciler` 注册行
2. 删除 `code_context_indexer.py`
3. 还原 `chunk_strategy_router.py` 的 ast_aware 分支（回到 _default_chunk）
4. code_context collection 数据靠 ttl 90 天自动清理，无需手动清

---

## 六、与 P3 裁定的对齐

| P3 裁定条款 | 本任务卡落实 |
|------------|-------------|
| 不建 pgvector | ✓ 复用 VMS code_context |
| 不建 code_embedding.py | ✓ 新建 code_context_indexer.py（命名对齐 VMS 子系统） |
| 扩展 VMS code_context indexer | ✓ 本任务卡核心 |
| 注册为 GitCommitGateway reconciler | ✓ GATE-CODE-CONTEXT priority=220 |
| 事件驱动 | ✓ post-commit，非常驻 |
| 新 AI 可发现 | ✓ AGENTS.md §11.2 登记 |

---

## 七、遗留风险

1. **首次全量索引**：reconciler 只索引本次 commit 的文件，历史代码需手动跑一次全量索引（`index_files_to_vms` 传入全量 .py 列表）。建议作为元任务卡 P3-MT1。
2. **embedding 耗时**：BGE-M3 嵌入大文件可能慢（首次加载模型 ~10s，之后每函数 ~50ms）。commit 大量文件时可能增加 post-commit 耗时。缓解：reconciler 非阻断，不卡 commit 本身。
3. **ChromaDB 并发**：多 AI 并发 commit 可能并发写 ChromaDB。ChromaDB 有内置锁，但高并发可能退化。缓解：reconciler 在 gateway 锁外运行，但 VMS 写入本身有 CollectionManager 内部锁。
