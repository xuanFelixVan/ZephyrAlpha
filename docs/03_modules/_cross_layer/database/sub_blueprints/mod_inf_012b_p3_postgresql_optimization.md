---
module_id: MOD-DB_DEPGRAPH_OPT
submodule_path: src/zephyr/infrastructure/db
title: "P3 PostgreSQL优化详细施工方案 — pgvector+LISTEN/NOTIFY+分区表+监控告警"
doc_type: blueprint
status: Draft
version: "1.0.0"
layer: cross_layer
blueprint_level: sub_module
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260625-P3
date: "2026-06-25"
valid_from: "2026-06-25"
ttl: permanent
rule_form: structural
belongs_to: "SH-DB-001"
parent_module: "SH-DB-001"
scope: global
stability: evolving
verifiability: automated
construction_progress: planned
actual_disk_path: ''
codification_level: L2
generation: 3
functional_domain: data
summary: "P3长期方案——PostgreSQL优化：pgvector代码embedding语义检索、LISTEN/NOTIFY AI间事件通知、按domain_id分区表大表优化、pg_stat_activity监控告警。覆盖4大优化方向的详细施工步骤。"
tags: [postgresql, pgvector, listen-notify, partitioning, monitoring, optimization, p3, database-upgrade]
priority: P2
runtime_plane: hot
depends_on:
  - {target: "MOD-DB_DEPGRAPH_PG", at: "全篇", why: "P2迁移完成是P3优化的前置条件"}
  - {target: "SH-DB-001", at: "全篇", why: "父蓝图——Database集成蓝图"}
references:
  - {id: "MOD-DB_DEPGRAPH_PG", at: "全篇", why: "P2迁移方案——P3基于P2完成的PostgreSQL"}
  - {id: "ARCH-CAP-002", at: "v1.0.8", why: "容量治理——分区后仍适用"}
---

# P3 PostgreSQL优化详细施工方案 — pgvector+LISTEN/NOTIFY+分区表+监控告警

> module_id: MOD-DB_DEPGRAPH_OPT | version: 1.0.0 | status: Draft | belongs_to: SH-DB-001
> 施工阶段: P3（长期：优化） | 前置条件: P2迁移完成

## 文档使用说明

本文档是P3 PostgreSQL优化的**唯一施工真源**。所有任务卡必须以本文档为准。

**前置条件**：P2 PostgreSQL迁移已完成，depgraph数据已在PostgreSQL中运行，红蓝测试通过。

**文档自审规则**：本文档完成后必须经过循环审查，检查前后冲突，直到问题数=0。审查清单见§九。

---

## 一、优化目标与背景

### 1.1 P2迁移后的状态

P2完成后，depgraph已运行在PostgreSQL上：
- Windows原生安装PostgreSQL 16
- 数据已从SQLite迁移（14K nodes + 22K edges）
- SQL方言已调整（100+连接点）
- 文件锁已删除（PG MVCC管理并发）
- PostgreSQL已安装并运行（Windows原生服务）
- 红蓝测试通过（40并发写入验证）

### 1.2 P3优化目标

| 优化项 | 目标 | 量化指标 | 价值 |
|--------|------|---------|------|
| pgvector | 代码embedding语义检索 | 语义相似度查询 < 50ms | AI可按语义查找模块，不依赖精确名称匹配 |
| LISTEN/NOTIFY | AI间事件通知 | 事件传播延迟 < 100ms | AI感知其他AI的变更，避免冲突 |
| 分区表 | 按domain_id分区大表 | 查询性能提升 5-10x | 大表（nodes/edges）查询聚焦单分区 |
| 监控告警 | pg_stat_activity监控 | 告警延迟 < 30s | 及时发现慢查询和连接耗尽 |

### 1.3 设计原则

| 原则 | 说明 |
|------|------|
| 渐进式优化 | 4个优化项独立施工，互不依赖 |
| 向后兼容 | 优化不改变现有API接口 |
| 可回滚 | 每个优化项可独立回滚 |
| 监控先行 | 优化前先建立基线，优化后对比 |

---

## 二、优化影响范围总览

| 类别 | 数量 | 详情 |
|------|:---:|------|
| 新建文件 | 8 | pgvector工具、LISTEN/NOTIFY工具、分区脚本、监控脚本 |
| 修改文件 | 6 | depgraph_schema.py、apply_depgraph.py、db_utils.py等 |
| 新建扩展 | 2 | pgvector、pg_stat_statements（P2已安装） |
| 数据库变更 | 3 | 新增embedding列、分区改造、事件队列表 |

---

## 三、施工阶段总览

| 阶段 | 名称 | 依赖 | 风险 | 预计任务卡数 |
|:---:|------|------|:---:|:---:|
| 1 | pgvector扩展（代码embedding语义检索） | P2完成 | 中 | 1 |
| 2 | LISTEN/NOTIFY（AI间事件通知） | P2完成 | 中 | 1 |
| 3 | 按domain_id分区表（大表优化） | P2完成 | 高 | 1 |
| 4 | 监控告警（pg_stat_activity） | P2完成 | 低 | 1 |
| - | **合计** | - | - | **4个任务卡** |

每个任务卡后面跟一个元任务卡（循环审查修复），共**4个任务卡 + 4个元任务卡 = 8个卡**。

### 3.1 推荐执行顺序

4个优化项之间无硬依赖，但有推荐顺序：

```
阶段4（监控告警）→ 阶段1（pgvector）→ 阶段2（LISTEN/NOTIFY）→ 阶段3（分区表）
```

**理由**：
1. **监控告警先行**：建立监控基线，后续优化可对比效果
2. **pgvector次之**：在nodes表添加embedding列，需在分区表迁移之前完成（分区表DDL中包含embedding列）
3. **LISTEN/NOTIFY第三**：在nodes表上创建触发器，需在分区表迁移之前完成（分区后触发器需重建）
4. **分区表最后**：数据量最大的结构变更，需在embedding列和触发器就绪后执行

**关键约束**：
- 如果阶段3（分区表）先于阶段1（pgvector）执行，分区表DDL中不应包含embedding列，后续通过`ALTER TABLE ... ADD COLUMN`添加
- 如果阶段3先于阶段2（LISTEN/NOTIFY）执行，触发器需在分区表上重建

---

## 四、阶段1：pgvector扩展（代码embedding语义检索）

### 4.1 前置条件

- [ ] P2迁移完成（PostgreSQL运行中）
- [ ] PostgreSQL服务正常运行
- [ ] Python环境已安装`sentence-transformers`包（用于生成embedding）

### 4.2 架构设计

```
代码文件 → sentence-transformers → embedding向量(384维) → pgvector存储
                                                              ↓
                                            语义检索: ORDER BY embedding <=> query_embedding
```

**设计决策**：
- Embedding模型：`sentence-transformers/all-MiniLM-L6-v2`（384维，速度快，适合代码检索）
- 向量维度：384（平衡精度和存储）
- 索引类型：HNSW（Hierarchical Navigable Small World，适合近似最近邻搜索）
- 距离度量：余弦距离（`<=>` 操作符）

### 4.3 详细施工步骤

#### [动作1] 安装pgvector扩展

**操作**：在PowerShell中执行

```powershell
# 安装pgvector扩展
psql -U zephyr -d depgraph -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 验证安装
psql -U zephyr -d depgraph -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

**预期输出**：显示 `vector` 扩展，版本 `0.7.0+`。

#### [动作2] 更新PostgreSQL初始化脚本

**文件路径**：`d:\ZephyrAlpha\scripts\governance\migrate_sqlite_to_pg\01_create_extensions.sql`

**注意**：此文件在P2阶段1[动作3]中创建，此处为修改（取消pgvector的注释）。

**操作**：修改文件，取消pgvector的注释：

```sql
-- 创建扩展
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS vector;  -- P3: pgvector for embedding
```

#### [动作3] 在nodes表添加embedding列

**操作**：在PowerShell中执行

```powershell
psql -U zephyr -d depgraph -c "
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS embedding vector(384);
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS embedding_model TEXT DEFAULT '';
ALTER TABLE nodes ADD COLUMN IF NOT EXISTS embedding_updated_at TIMESTAMP;
"
```

#### [动作4] 创建HNSW索引

**操作**：在PowerShell中执行

```powershell
psql -U zephyr -d depgraph -c "
CREATE INDEX IF NOT EXISTS idx_nodes_embedding
ON nodes USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
"
```

**参数说明**：
- `m = 16`：每个节点的最大连接数（平衡索引大小和搜索精度）
- `ef_construction = 64`：构建索引时的搜索宽度（越大越精确，构建越慢）

#### [动作5] 创建Python embedding工具

**文件路径**：`d:\ZephyrAlpha\src\zephyr\shared\utils\code_embedding.py`

**操作**：创建新文件，内容如下：

```python
"""
代码Embedding工具
================
使用sentence-transformers生成代码embedding，存入pgvector。

使用方式：
    from zephyr.shared.utils.code_embedding import generate_embedding, semantic_search

    # 生成embedding
    embedding = generate_embedding("def hello(): print('hello')")

    # 语义搜索
    results = semantic_search("用户认证模块", top_k=5)
"""

import hashlib
import logging
from pathlib import Path

import psycopg2
import numpy as np

# 复用P2中定义的PG连接配置（src/zephyr/shared/utils/pg_connection.py）
from zephyr.shared.utils.pg_connection import PG_CONFIG

logger = logging.getLogger(__name__)

# Embedding模型
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384

# 模型单例（避免重复加载）
_model = None


def _get_model():
    """获取embedding模型单例。"""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. "
                "Run: pip install sentence-transformers"
            )
    return _model


def generate_embedding(text: str) -> list[float]:
    """生成文本的embedding向量。

    Args:
        text: 输入文本（代码片段或模块描述）

    Returns:
        384维embedding向量
    """
    model = _get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()


def update_node_embedding(node_id: str, text: str) -> None:
    """更新节点的embedding。

    Args:
        node_id: 节点ID
        text: 用于生成embedding的文本（模块名+描述+文件路径）
    """
    embedding = generate_embedding(text)
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE nodes
        SET embedding = %s,
            embedding_model = %s,
            embedding_updated_at = now()
        WHERE node_id = %s
        """,
        (embedding, EMBEDDING_MODEL_NAME, node_id)
    )
    conn.commit()
    cur.close()
    conn.close()


def semantic_search(query: str, top_k: int = 10, domain_id: str = None) -> list[dict]:
    """语义搜索节点。

    Args:
        query: 搜索查询文本
        top_k: 返回前K个结果
        domain_id: 可选，限定域

    Returns:
        匹配节点列表 [{node_id, name, domain_id, similarity}]
    """
    query_embedding = generate_embedding(query)
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    if domain_id:
        cur.execute(
            """
            SELECT node_id, name, domain_id, file_path,
                   1 - (embedding <=> %s::vector) as similarity
            FROM nodes
            WHERE embedding IS NOT NULL
              AND domain_id = %s
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, domain_id, query_embedding, top_k)
        )
    else:
        cur.execute(
            """
            SELECT node_id, name, domain_id, file_path,
                   1 - (embedding <=> %s::vector) as similarity
            FROM nodes
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> %s::vector
            LIMIT %s
            """,
            (query_embedding, query_embedding, top_k)
        )

    results = []
    for row in cur.fetchall():
        results.append({
            "node_id": row[0],
            "name": row[1],
            "domain_id": row[2],
            "file_path": row[3],
            "similarity": float(row[4]),
        })

    cur.close()
    conn.close()
    return results


def batch_update_embeddings(domain_id: str = None, batch_size: int = 100) -> int:
    """批量更新节点的embedding。

    Args:
        domain_id: 可选，限定域。None=所有域
        batch_size: 批量大小

    Returns:
        更新的节点数
    """
    conn = psycopg2.connect(**PG_CONFIG)
    cur = conn.cursor()

    # 查询需要更新embedding的节点
    if domain_id:
        cur.execute(
            """
            SELECT node_id, name, description, file_path
            FROM nodes
            WHERE (embedding IS NULL OR embedding_updated_at IS NULL)
              AND domain_id = %s
            ORDER BY node_id
            """,
            (domain_id,)
        )
    else:
        cur.execute(
            """
            SELECT node_id, name, description, file_path
            FROM nodes
            WHERE embedding IS NULL OR embedding_updated_at IS NULL
            ORDER BY node_id
            """
        )

    nodes = cur.fetchall()
    total_updated = 0

    for i in range(0, len(nodes), batch_size):
        batch = nodes[i:i + batch_size]
        for node_id, name, description, file_path in batch:
            # 组合文本用于embedding
            text = f"{name} {description or ''} {file_path or ''}"
            try:
                update_node_embedding(node_id, text)
                total_updated += 1
            except Exception as e:
                logger.error(f"Failed to update embedding for {node_id}: {e}")

        logger.info(f"Updated {total_updated}/{len(nodes)} embeddings...")

    cur.close()
    conn.close()
    return total_updated
```

#### [动作6] 安装Python依赖

**操作**：在PowerShell中执行

```powershell
pip install sentence-transformers
```

#### [动作7] 更新requirements.txt

**文件路径**：`d:\ZephyrAlpha\requirements.txt`

**操作**：追加以下行：

```txt
sentence-transformers>=2.7.0
```

#### [动作8] 创建embedding批量更新脚本

**文件路径**：`d:\ZephyrAlpha\scripts\governance\update_embeddings.py`

**操作**：创建新文件，内容如下：

```python
#!/usr/bin/env python3
"""
批量更新节点embedding脚本
========================
为depgraph中的所有节点生成embedding向量。

使用方式：
    # 更新所有节点
    python scripts/governance/update_embeddings.py

    # 更新指定域
    python scripts/governance/update_embeddings.py --domain D-GOVERNANCE
"""

import argparse
import sys
from pathlib import Path

# 添加src到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from zephyr.shared.utils.code_embedding import batch_update_embeddings


def main():
    parser = argparse.ArgumentParser(description="批量更新节点embedding")
    parser.add_argument("--domain", type=str, default=None, help="限定域ID")
    parser.add_argument("--batch-size", type=int, default=100, help="批量大小")
    args = parser.parse_args()

    print("=" * 60)
    print("批量更新节点embedding")
    print("=" * 60)

    if args.domain:
        print(f"域: {args.domain}")
    else:
        print("域: 全部")

    count = batch_update_embeddings(domain_id=args.domain, batch_size=args.batch_size)

    print(f"\n完成! 更新了 {count} 个节点的embedding")


if __name__ == "__main__":
    main()
```

#### [动作9] 执行embedding批量更新

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha

# 先更新一个小域测试
python scripts\governance\update_embeddings.py --domain D-GOVERNANCE

# 验证embedding已生成
psql -U zephyr -d depgraph -c "
SELECT COUNT(*) as total,
       COUNT(embedding) as has_embedding
FROM nodes
WHERE domain_id = 'D-GOVERNANCE';
"

# 测试语义搜索
python -c "
import sys; sys.path.insert(0, 'src')
from zephyr.shared.utils.code_embedding import semantic_search
results = semantic_search('任务管理', top_k=5)
for r in results:
    print(f'{r[\"similarity\"]:.3f} | {r[\"node_id\"]} | {r[\"name\"]} | {r[\"domain_id\"]}')
"
```

**预期输出**：
- D-GOVERNANCE域的节点大部分有embedding
- 语义搜索返回相关模块（如task_repo、task_types等）

### 4.4 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | pgvector扩展安装 | `SELECT extname FROM pg_extension WHERE extname='vector'` | vector |
| 2 | embedding列存在 | `\d nodes` | 显示embedding列 |
| 3 | HNSW索引存在 | `SELECT indexname FROM pg_indexes WHERE indexname='idx_nodes_embedding'` | idx_nodes_embedding |
| 4 | embedding已生成 | `SELECT COUNT(embedding) FROM nodes WHERE domain_id='D-GOVERNANCE'` | >0 |
| 5 | 语义搜索可用 | `semantic_search('任务管理')` | 返回相关模块 |
| 6 | 搜索延迟 | 语义搜索计时 | < 50ms |

### 4.5 受影响文件

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `scripts/governance/migrate_sqlite_to_pg/01_create_extensions.sql` | 修改 | 启用vector扩展 |
| 2 | `src/zephyr/shared/utils/code_embedding.py` | 新建 | Embedding工具 |
| 3 | `scripts/governance/update_embeddings.py` | 新建 | 批量更新脚本 |
| 4 | `requirements.txt` | 修改 | 添加sentence-transformers |

---

## 五、阶段2：LISTEN/NOTIFY（AI间事件通知）

### 5.1 前置条件

- [ ] P2迁移完成（PostgreSQL运行中）
- [ ] PostgreSQL直连配置正常

**注意**：Windows原生安装的PostgreSQL使用直连（端口5432），LISTEN/NOTIFY的持久订阅可直接使用，无需额外配置。

### 5.2 架构设计

```
AI-1 (写入节点)                    AI-2 (监听变更)
    |                                    |
    | NOTIFY depgraph_changed           | LISTEN depgraph_changed
    |                                    |
    v                                    v
┌─────────────────────────────────────────────┐
│           PostgreSQL                        │
│  ┌─────────────────────────────────────┐    │
│  │  pg_notify (事件队列)               │    │
│  │  - channel: depgraph_changed       │    │
│  │  - payload: {"node_id":"...",      │    │
│  │             "action":"add",        │    │
│  │             "domain_id":"..."}     │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

**设计决策**：
- 通知通道：`depgraph_changed`（节点/边变更）、`domain_capacity`（容量变更）
- 载荷格式：JSON（包含node_id、action、domain_id）
- 订阅方式：独立线程LISTEN，事件入队后异步处理
- 连接方式：直连PostgreSQL（5432）

### 5.3 详细施工步骤

#### [动作1] 创建触发器函数（自动发送NOTIFY）

**操作**：在PowerShell中执行

```powershell
psql -U zephyr -d depgraph -c "
-- 创建触发器函数：节点变更时发送NOTIFY
CREATE OR REPLACE FUNCTION notify_node_change() RETURNS TRIGGER AS \$\$
DECLARE
    payload JSON;
BEGIN
    IF TG_OP = 'INSERT' THEN
        payload := json_build_object(
            'action', 'add',
            'node_id', NEW.node_id,
            'node_type', NEW.node_type,
            'domain_id', NEW.domain_id,
            'name', NEW.name
        );
    ELSIF TG_OP = 'UPDATE' THEN
        payload := json_build_object(
            'action', 'update',
            'node_id', NEW.node_id,
            'node_type', NEW.node_type,
            'domain_id', NEW.domain_id,
            'name', NEW.name
        );
    ELSIF TG_OP = 'DELETE' THEN
        payload := json_build_object(
            'action', 'delete',
            'node_id', OLD.node_id,
            'domain_id', OLD.domain_id
        );
    END IF;

    PERFORM pg_notify('depgraph_changed', payload::text);
    RETURN COALESCE(NEW, OLD);
END;
\$\$ LANGUAGE plpgsql;

-- 绑定触发器
DROP TRIGGER IF EXISTS tr_notify_node_insert ON nodes;
CREATE TRIGGER tr_notify_node_insert AFTER INSERT ON nodes
    FOR EACH ROW EXECUTE FUNCTION notify_node_change();

DROP TRIGGER IF EXISTS tr_notify_node_update ON nodes;
CREATE TRIGGER tr_notify_node_update AFTER UPDATE ON nodes
    FOR EACH ROW EXECUTE FUNCTION notify_node_change();

DROP TRIGGER IF EXISTS tr_notify_node_delete ON nodes;
CREATE TRIGGER tr_notify_node_delete AFTER DELETE ON nodes
    FOR EACH ROW EXECUTE FUNCTION notify_node_change();
"
```

#### [动作2] 创建Python LISTEN/NOTIFY工具

**文件路径**：`d:\ZephyrAlpha\src\zephyr\shared\utils\pg_notify.py`

**操作**：创建新文件，内容如下：

```python
"""
PostgreSQL LISTEN/NOTIFY 工具
=============================
AI间事件通知：一个AI修改depgraph后，其他AI自动收到通知。

使用方式：
    from zephyr.shared.utils.pg_notify import EventListener, notify_change

    # 发送通知
    notify_change('depgraph_changed', {'node_id': 'MOD-ALPHA_SIGNAL_DOMAIN', 'action': 'add'})

    # 监听通知
    listener = EventListener('depgraph_changed')
    listener.start()
    for event in listener.events():
        print(f"收到事件: {event}")
"""

import json
import logging
import queue
import threading
import psycopg2

# 复用P2中定义的PG连接配置（src/zephyr/shared/utils/pg_connection.py）
from zephyr.shared.utils.pg_connection import PG_CONFIG

logger = logging.getLogger(__name__)

# LISTEN/NOTIFY使用直连PostgreSQL
PG_DIRECT_CONFIG = {
    "host": "localhost",
    "port": 5432,  # 直连PostgreSQL
    "database": "depgraph",
    "user": "zephyr",
    "password": PG_CONFIG["password"],  # 复用P2中的密码
}


def notify_change(channel: str, payload: dict) -> None:
    """发送NOTIFY通知。

    Args:
        channel: 通知通道名
        payload: 通知载荷（dict，会转为JSON）
    """
    conn = psycopg2.connect(**PG_DIRECT_CONFIG)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(
        "SELECT pg_notify(%s, %s)",
        (channel, json.dumps(payload))
    )
    cur.close()
    conn.close()


class EventListener:
    """事件监听器。

    在独立线程中LISTEN指定通道，收到通知后放入队列。

    使用方式：
        listener = EventListener('depgraph_changed')
        listener.start()
        for event in listener.events():
            print(f"收到事件: {event}")
    """

    def __init__(self, channel: str, config: dict = None):
        self.channel = channel
        self.config = config or PG_DIRECT_CONFIG
        self._conn = None
        self._thread = None
        self._running = False
        self._event_queue = queue.Queue()

    def start(self):
        """启动监听线程。"""
        self._running = True
        self._thread = threading.Thread(target=self._listen_loop, daemon=True)
        self._thread.start()
        logger.info(f"EventListener started for channel: {self.channel}")

    def stop(self):
        """停止监听。"""
        self._running = False
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
        if self._thread:
            self._thread.join(timeout=5)
        logger.info(f"EventListener stopped for channel: {self.channel}")

    def _listen_loop(self):
        """监听循环（在独立线程中运行）。"""
        while self._running:
            try:
                self._conn = psycopg2.connect(**self.config)
                self._conn.autocommit = True
                cur = self._conn.cursor()
                cur.execute(f"LISTEN {self.channel};")

                while self._running:
                    # select有超时，允许检查_running标志
                    if self._conn.poll() == 0:
                        # 无就绪通知，短暂等待
                        import time
                        time.sleep(0.1)
                        continue

                    for notify in self._conn.notifies:
                        payload = json.loads(notify.payload) if notify.payload else {}
                        self._event_queue.put({
                            "channel": notify.channel,
                            "payload": payload,
                            "pid": notify.pid,
                        })

                cur.close()
            except Exception as e:
                logger.error(f"LISTEN error: {e}, reconnecting in 5s...")
                import time
                time.sleep(5)

    def events(self):
        """事件生成器（阻塞迭代）。"""
        while self._running:
            try:
                event = self._event_queue.get(timeout=1)
                yield event
            except queue.Empty:
                continue
```

#### [动作3] 创建事件通知集成工具

**文件路径**：`d:\ZephyrAlpha\src\zephyr\shared\utils\depgraph_events.py`

**操作**：创建新文件，内容如下：

```python
"""
depgraph事件通知集成
===================
将LISTEN/NOTIFY集成到depgraph操作中。

使用方式：
    from zephyr.shared.utils.depgraph_events import get_event_listener

    listener = get_event_listener()
    listener.start()
    for event in listener.events():
        if event['payload'].get('domain_id') == 'D-GOVERNANCE':
            print(f"GOVERNANCE域变更: {event['payload']}")
"""

import logging
from zephyr.shared.utils.pg_notify import EventListener

logger = logging.getLogger(__name__)

# 全局事件监听器单例
_listener = None


def get_event_listener() -> EventListener:
    """获取全局事件监听器单例。"""
    global _listener
    if _listener is None:
        _listener = EventListener("depgraph_changed")
    return _listener
```

#### [动作4] 验证LISTEN/NOTIFY功能

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha
python -c "
import sys; sys.path.insert(0, 'src')
import time
from zephyr.shared.utils.pg_notify import EventListener, notify_change

# 启动监听
listener = EventListener('depgraph_changed')
listener.start()

# 等待监听就绪
time.sleep(1)

# 发送通知
notify_change('depgraph_changed', {'node_id': 'TEST-001', 'action': 'add', 'domain_id': 'D-TEST'})

# 等待接收
time.sleep(1)

# 检查事件
events = []
try:
    while True:
        event = listener._event_queue.get_nowait()
        events.append(event)
except:
    pass

print(f'收到 {len(events)} 个事件:')
for e in events:
    print(f'  {e}')

listener.stop()
"
```

**预期输出**：收到1个事件，payload包含node_id、action、domain_id。

#### [动作5] 验证触发器自动通知

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha
python -c "
import sys; sys.path.insert(0, 'src')
import time
import psycopg2
from zephyr.shared.utils.pg_notify import EventListener

PG_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'depgraph',
    'user': 'zephyr',
    'password': 'zephyr_dev_2026',
}

# 启动监听
listener = EventListener('depgraph_changed')
listener.start()
time.sleep(1)

# 插入节点（触发器应自动发送NOTIFY）
conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()
cur.execute(
    \"\"\"INSERT INTO nodes (node_id, node_type, domain_id, name, design_maturity)
    VALUES (%s, %s, %s, %s, %s)\"\"\",
    ('test_notify_node', 'module', 'D-TEST', 'Test Notify', 'draft')
)
conn.commit()
cur.close()
conn.close()

# 等待接收
time.sleep(1)

# 检查事件
events = []
try:
    while True:
        event = listener._event_queue.get_nowait()
        events.append(event)
except:
    pass

print(f'收到 {len(events)} 个事件:')
for e in events:
    print(f'  {e}')

# 清理
conn = psycopg2.connect(**PG_CONFIG)
cur = conn.cursor()
cur.execute(\"DELETE FROM nodes WHERE node_id = 'test_notify_node'\")
conn.commit()
cur.close()
conn.close()

listener.stop()
"
```

**预期输出**：收到1个事件，action=add，node_id=test_notify_node。

### 5.4 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 触发器函数存在 | `SELECT proname FROM pg_proc WHERE proname='notify_node_change'` | notify_node_change |
| 2 | 触发器已绑定 | `SELECT tgname FROM pg_trigger WHERE tgname LIKE 'tr_notify_%'` | 3个触发器 |
| 3 | 手动NOTIFY可用 | `SELECT pg_notify('test', '{}')` | 成功 |
| 4 | EventListener可用 | Python测试脚本 | 收到事件 |
| 5 | 触发器自动通知 | 插入节点测试 | 自动收到事件 |
| 6 | 事件延迟 | 计时 | < 100ms |

### 5.5 受影响文件

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `src/zephyr/shared/utils/pg_notify.py` | 新建 | LISTEN/NOTIFY工具 |
| 2 | `src/zephyr/shared/utils/depgraph_events.py` | 新建 | 事件通知集成 |

---

## 六、阶段3：按domain_id分区表（大表优化）

### 6.1 前置条件

- [ ] P2迁移完成（PostgreSQL运行中）
- [ ] 数据已迁移（14K nodes + 22K edges）
- [ ] 当前查询性能基线已记录

### 6.2 架构设计

**分区策略**：按domain_id的哈希分区

```
nodes表（14K行）
├── nodes_d_governance    (hash=0, ~2000行)
├── nodes_d_data         (hash=1, ~1500行)
├── nodes_d_signal       (hash=2, ~1800行)
├── ...
└── nodes_default        (其他域)
```

**设计决策**：
- 分区方式：HASH分区（按domain_id哈希，均匀分布）
- 分区数：8（2的幂，便于哈希分布）
- 分区表命名：`nodes_p0` ~ `nodes_p7`
- 默认分区：`nodes_default`（未匹配的domain_id）

**为什么选择HASH分区而非LIST分区**：
- 55个域，LIST分区需要55个分区（过多）
- HASH分区8个，每个约7个域，均匀分布
- 查询时PG自动分区裁剪（partition pruning）

### 6.3 风险评估

| 风险 | 严重度 | 缓解措施 |
|------|:---:|---------|
| 分区迁移期间数据不可用 | 高 | 在维护窗口执行，先创建分区表再迁移 |
| 外键约束失效 | 中 | 分区表的外键支持有限，需调整约束 |
| 索引需重建 | 中 | 分区后索引自动创建在子分区上 |
| 回滚困难 | 高 | 保留原表备份，可回滚 |
| **主键变更影响** | **高** | 分区表主键必须包含分区键(domain_id)，原主键仅node_id需改为(node_id, domain_id)，影响所有按node_id查询的代码 |
| **edges外键引用** | **高** | edges表通过source_id/target_id引用nodes.node_id，分区后外键需改为引用(node_id, domain_id)复合键，或删除外键改用应用层校验 |

**主键变更处理方案**：
- 原主键：`PRIMARY KEY (node_id)`
- 新主键：`PRIMARY KEY (node_id, domain_id)`（分区表要求分区键在主键中）
- 影响范围：所有`WHERE node_id = ?`的查询仍可用（PG自动优化），但`JOIN ... ON e.source_id = n.node_id`需确保同时关联domain_id
- 代码调整：apply_depgraph.py中按node_id查询的SQL需验证是否依赖domain_id

**edges外键处理方案**：
- 方案A（推荐）：删除edges到nodes的外键约束，改用应用层校验（apply_depgraph.py已有孤儿边检测）
- 方案B：在edges表添加domain_id列，外键改为`FOREIGN KEY (source_id, domain_id) REFERENCES nodes(node_id, domain_id)`
- 方案C：不分区edges表，仅分区nodes表（降低风险但edges查询无分区裁剪）

**apply_depgraph.py 影响核查结论**（按方案A执行时）：
- 经核查，apply_depgraph.py 中按 `node_id` 查询的 SQL 均为单表 `WHERE node_id = ?` 形式，PG 分区表对此自动优化，无需修改
- apply_depgraph.py 已含孤儿边检测逻辑，删除外键约束后该逻辑依然有效
- 结论：**按方案A执行时，apply_depgraph.py 无需修改**；若改用方案B，则需在 JOIN 中补充 domain_id 关联

### 6.4 详细施工步骤

#### [动作1] 记录性能基线

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha

# 记录查询性能基线
psql -U zephyr -d depgraph -c "
-- 查询1: 按domain_id查询nodes
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM nodes WHERE domain_id = 'D-GOVERNANCE';

-- 查询2: 按domain_id查询edges
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM edges WHERE source_id IN (
    SELECT node_id FROM nodes WHERE domain_id = 'D-GOVERNANCE'
);

-- 查询3: 全表扫描
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM nodes;
" > scripts\governance\migrate_sqlite_to_pg\performance_baseline.txt
```

#### [动作2] 创建分区表迁移脚本

**文件路径**：`d:\ZephyrAlpha\scripts\governance\migrate_sqlite_to_pg\02_partition_tables.sql`

**操作**：创建新文件，内容如下：

```sql
-- ============================================================
-- 分区表迁移脚本
-- 将nodes和edges表改为按domain_id的HASH分区
-- ============================================================

-- 注意：此脚本需要在维护窗口执行
-- 执行前请确保已备份depgraph数据库
-- 完整列定义获取命令：
--   psql -U zephyr -d depgraph -c "\d nodes"
--   psql -U zephyr -d depgraph -c "\d edges"
-- 将输出中的列定义填入下方DDL（替换 -- ... 注释部分）

BEGIN;

-- 1. 重命名原表
ALTER TABLE nodes RENAME TO nodes_old;
ALTER TABLE edges RENAME TO edges_old;

-- 2. 创建分区表
CREATE TABLE nodes (
    node_id TEXT NOT NULL,
    node_type TEXT NOT NULL,
    domain_id TEXT NOT NULL,
    name TEXT,
    description TEXT,
    file_path TEXT,
    -- ... 其他列（从nodes_old复制）
    design_maturity TEXT DEFAULT 'draft',
    embedding vector(384),
    embedding_model TEXT DEFAULT '',
    embedding_updated_at TIMESTAMP,
    PRIMARY KEY (node_id, domain_id)
) PARTITION BY HASH (domain_id);

CREATE TABLE edges (
    edge_id BIGINT GENERATED ALWAYS AS IDENTITY,
    source_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    edge_type TEXT NOT NULL,
    domain_id TEXT NOT NULL,
    -- ... 其他列（从edges_old复制）
    PRIMARY KEY (edge_id, domain_id)
) PARTITION BY HASH (domain_id);

-- 3. 创建8个分区
CREATE TABLE nodes_p0 PARTITION OF nodes FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE nodes_p1 PARTITION OF nodes FOR VALUES WITH (MODULUS 8, REMAINDER 1);
CREATE TABLE nodes_p2 PARTITION OF nodes FOR VALUES WITH (MODULUS 8, REMAINDER 2);
CREATE TABLE nodes_p3 PARTITION OF nodes FOR VALUES WITH (MODULUS 8, REMAINDER 3);
CREATE TABLE nodes_p4 PARTITION OF nodes FOR VALUES WITH (MODULUS 8, REMAINDER 4);
CREATE TABLE nodes_p5 PARTITION OF nodes FOR VALUES WITH (MODULUS 8, REMAINDER 5);
CREATE TABLE nodes_p6 PARTITION OF nodes FOR VALUES WITH (MODULUS 8, REMAINDER 6);
CREATE TABLE nodes_p7 PARTITION OF nodes FOR VALUES WITH (MODULUS 8, REMAINDER 7);
CREATE TABLE nodes_default PARTITION OF nodes DEFAULT;

CREATE TABLE edges_p0 PARTITION OF edges FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE edges_p1 PARTITION OF edges FOR VALUES WITH (MODULUS 8, REMAINDER 1);
CREATE TABLE edges_p2 PARTITION OF edges FOR VALUES WITH (MODULUS 8, REMAINDER 2);
CREATE TABLE edges_p3 PARTITION OF edges FOR VALUES WITH (MODULUS 8, REMAINDER 3);
CREATE TABLE edges_p4 PARTITION OF edges FOR VALUES WITH (MODULUS 8, REMAINDER 4);
CREATE TABLE edges_p5 PARTITION OF edges FOR VALUES WITH (MODULUS 8, REMAINDER 5);
CREATE TABLE edges_p6 PARTITION OF edges FOR VALUES WITH (MODULUS 8, REMAINDER 6);
CREATE TABLE edges_p7 PARTITION OF edges FOR VALUES WITH (MODULUS 8, REMAINDER 7);
CREATE TABLE edges_default PARTITION OF edges DEFAULT;

-- 4. 迁移数据
INSERT INTO nodes SELECT * FROM nodes_old;
INSERT INTO edges SELECT * FROM edges_old;

-- 5. 创建索引（分区表索引自动传播到子分区）
CREATE INDEX idx_nodes_domain ON nodes (domain_id);
CREATE INDEX idx_nodes_type ON nodes (node_type);
CREATE INDEX idx_nodes_embedding ON nodes USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_edges_source ON edges (source_id);
CREATE INDEX idx_edges_target ON edges (target_id);
CREATE INDEX idx_edges_domain ON edges (domain_id);

-- 6. 验证数据
SELECT 'nodes_old' as tbl, COUNT(*) FROM nodes_old
UNION ALL
SELECT 'nodes_new', COUNT(*) FROM nodes
UNION ALL
SELECT 'edges_old', COUNT(*) FROM edges_old
UNION ALL
SELECT 'edges_new', COUNT(*) FROM edges;

-- 7. 如果数据一致，删除旧表（取消注释执行）
-- DROP TABLE nodes_old;
-- DROP TABLE edges_old;

COMMIT;
```

#### [动作3] 执行分区迁移

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha

# 1. 先备份PostgreSQL数据库
pg_dump -U zephyr -d depgraph > data\databases\backups\depgraph_pre_partition.sql

# 2. 执行分区迁移
psql -U zephyr -d depgraph -f scripts\governance\migrate_sqlite_to_pg\02_partition_tables.sql

# 3. 验证数据一致性
psql -U zephyr -d depgraph -c "
SELECT 'nodes_old' as tbl, COUNT(*) FROM nodes_old
UNION ALL
SELECT 'nodes_new', COUNT(*) FROM nodes
UNION ALL
SELECT 'edges_old', COUNT(*) FROM edges_old
UNION ALL
SELECT 'edges_new', COUNT(*) FROM edges;
"
```

**预期输出**：nodes_old和nodes_new行数一致，edges_old和edges_new行数一致。

#### [动作4] 验证分区裁剪

**操作**：在PowerShell中执行

```powershell
psql -U zephyr -d depgraph -c "
-- 验证分区裁剪：只扫描1个分区
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM nodes WHERE domain_id = 'D-GOVERNANCE';
"
```

**预期输出**：EXPLAIN显示只扫描1个分区（如`Seq Scan on nodes_p3`），而非全表扫描。

#### [动作5] 对比性能

**操作**：在PowerShell中执行

```powershell
psql -U zephyr -d depgraph -c "
-- 查询1: 按domain_id查询nodes
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM nodes WHERE domain_id = 'D-GOVERNANCE';

-- 查询2: 按domain_id查询edges
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM edges WHERE domain_id = 'D-GOVERNANCE';

-- 查询3: 全表扫描
EXPLAIN (ANALYZE, BUFFERS)
SELECT COUNT(*) FROM nodes;
" > scripts\governance\migrate_sqlite_to_pg\performance_after_partition.txt
```

对比 `performance_baseline.txt` 和 `performance_after_partition.txt`，验证：
- 按domain_id查询：性能提升5-10x
- 全表扫描：性能基本不变（略有下降，因分区开销）

#### [动作6] 删除旧表

**操作**：确认数据一致后，在PowerShell中执行

```powershell
psql -U zephyr -d depgraph -c "
DROP TABLE nodes_old;
DROP TABLE edges_old;
"
```

#### [动作7] 更新depgraph_schema.py

**文件路径**：`d:\ZephyrAlpha\src\zephyr\governance\depgraph_schema.py`

**操作**：修改Schema DDL，将nodes和edges表定义改为分区表定义。具体修改内容参照 `02_partition_tables.sql` 中的DDL。

#### [动作8] 重建 LISTEN/NOTIFY 触发器

**操作**：分区表迁移后，原绑定在 nodes 表上的 LISTEN/NOTIFY 触发器（P3-T2 §五.5.3[动作1] 创建）会随旧表 DROP 而失效，需在新分区表上重新创建。

**步骤**：重新执行 §五.5.3[动作1] 中的触发器函数与触发器创建 SQL（`notify_node_change` 函数 + `tr_notify_node_insert`/`tr_notify_node_update`/`tr_notify_node_delete` 三个触发器）。

**验证**：
```powershell
psql -U zephyr -d depgraph -c "
SELECT tgname FROM pg_trigger WHERE tgname LIKE 'tr_notify_%';
"
```
预期返回 3 行。

### 6.5 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | nodes已分区 | `SELECT count(*) FROM pg_partitions WHERE tablename='nodes'` | 9（8分区+默认） |
| 2 | edges已分区 | `SELECT count(*) FROM pg_partitions WHERE tablename='edges'` | 9 |
| 3 | 数据一致 | nodes_old vs nodes_new行数 | 一致 |
| 4 | 分区裁剪生效 | EXPLAIN显示单分区扫描 | 只扫描1个分区 |
| 5 | 按域查询性能提升 | 对比基线 | 5-10x提升 |
| 6 | 索引已创建 | `\di` | 显示所有索引 |
| 7 | 旧表已删除 | `\dt` | 无nodes_old/edges_old |
| 8 | LISTEN/NOTIFY触发器已重建 | `SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'tr_notify_%'` | 3 |
| 9 | embedding列在分区表中存在 | `SELECT column_name FROM information_schema.columns WHERE table_name='nodes' AND column_name='embedding'` | embedding |
| 10 | apply_depgraph.py diagnose可运行 | `python scripts\governance\apply_depgraph.py diagnose` | 无报错 |

### 6.6 受影响文件

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `scripts/governance/migrate_sqlite_to_pg/02_partition_tables.sql` | 新建 | 分区迁移脚本 |
| 2 | `scripts/governance/migrate_sqlite_to_pg/performance_baseline.txt` | 新建 | 性能基线 |
| 3 | `scripts/governance/migrate_sqlite_to_pg/performance_after_partition.txt` | 新建 | 分区后性能 |
| 4 | `src/zephyr/governance/depgraph_schema.py` | 修改 | Schema DDL改为分区表 |

---

## 七、阶段4：监控告警（pg_stat_activity）

### 7.1 前置条件

- [ ] P2迁移完成（PostgreSQL运行中）
- [ ] pg_stat_statements扩展已安装（P2阶段1已安装）

### 7.2 架构设计

```
PostgreSQL
├── pg_stat_activity    (活动连接/查询)
├── pg_stat_statements  (查询统计)
└── pg_stat_database    (数据库级统计)
        ↓
监控脚本（每30s采集）
        ↓
┌───────────────────────────────┐
│  告警规则                     │
│  - 慢查询 > 5s               │
│  - 连接数 > 150              │
│  - 死锁发生                   │
│  - 事务空闲 > 60s            │
└───────────────────────────────┘
        ↓
告警输出（日志 + 控制台）
```

### 7.3 详细施工步骤

#### [动作1] 创建监控脚本

**文件路径**：`d:\ZephyrAlpha\scripts\governance\monitor_pg.py`

**操作**：创建新文件，内容如下：

```python
#!/usr/bin/env python3
"""
PostgreSQL监控告警脚本
=====================
监控pg_stat_activity，发现异常时告警。

使用方式：
    # 单次检查
    python scripts/governance/monitor_pg.py

    # 持续监控（每30s检查）
    python scripts/governance/monitor_pg.py --watch --interval 30
"""

import argparse
import datetime
import json
import logging
import sys
import time
from pathlib import Path

import psycopg2

# 复用P2中定义的PG连接配置（src/zephyr/shared/utils/pg_connection.py）
from zephyr.shared.utils.pg_connection import PG_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# 告警阈值
ALERT_THRESHOLDS = {
    "slow_query_seconds": 5,       # 慢查询阈值
    "max_connections": 150,        # 最大连接数
    "idle_transaction_seconds": 60, # 空闲事务阈值
    "deadlock_count": 1,           # 死锁次数
}

# 告警日志路径
ALERT_LOG_PATH = Path("data/databases/postgres/alerts.log")


def check_slow_queries(conn):
    """检查慢查询。"""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
        FROM pg_stat_activity
        WHERE state != 'idle'
          AND now() - pg_stat_activity.query_start > INTERVAL '%s seconds'
        ORDER BY duration DESC
        """,
        (ALERT_THRESHOLDS["slow_query_seconds"],)
    )
    slow_queries = cur.fetchall()
    cur.close()

    alerts = []
    for pid, duration, query, state in slow_queries:
        alerts.append({
            "type": "slow_query",
            "severity": "warning",
            "pid": pid,
            "duration_seconds": duration.total_seconds(),
            "query": query[:200],  # 截断长查询
            "state": state,
            "timestamp": datetime.datetime.now().isoformat(),
        })
    return alerts


def check_connection_count(conn):
    """检查连接数。"""
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM pg_stat_activity;")
    count = cur.fetchone()[0]
    cur.close()

    alerts = []
    if count > ALERT_THRESHOLDS["max_connections"]:
        alerts.append({
            "type": "high_connections",
            "severity": "critical",
            "current": count,
            "threshold": ALERT_THRESHOLDS["max_connections"],
            "timestamp": datetime.datetime.now().isoformat(),
        })
    return alerts


def check_idle_transactions(conn):
    """检查空闲事务。"""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT pid, now() - xact_start AS duration, query, state
        FROM pg_stat_activity
        WHERE state = 'idle in transaction'
          AND now() - xact_start > INTERVAL '%s seconds'
        ORDER BY duration DESC
        """,
        (ALERT_THRESHOLDS["idle_transaction_seconds"],)
    )
    idle_txns = cur.fetchall()
    cur.close()

    alerts = []
    for pid, duration, query, state in idle_txns:
        alerts.append({
            "type": "idle_transaction",
            "severity": "warning",
            "pid": pid,
            "duration_seconds": duration.total_seconds(),
            "query": query[:200],
            "timestamp": datetime.datetime.now().isoformat(),
        })
    return alerts


def check_deadlocks(conn):
    """检查死锁。"""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT deadlocks FROM pg_stat_database WHERE datname = 'depgraph';
        """
    )
    deadlocks = cur.fetchone()[0]
    cur.close()

    alerts = []
    if deadlocks > 0:
        alerts.append({
            "type": "deadlock",
            "severity": "critical",
            "count": deadlocks,
            "timestamp": datetime.datetime.now().isoformat(),
        })
    return alerts


def check_query_stats(conn):
    """检查查询统计（pg_stat_statements）。"""
    cur = conn.cursor()
    cur.execute(
        """
        SELECT query, calls, total_exec_time, mean_exec_time, rows
        FROM pg_stat_statements
        ORDER BY mean_exec_time DESC
        LIMIT 5;
        """
    )
    stats = cur.fetchall()
    cur.close()

    alerts = []
    for query, calls, total_time, mean_time, rows in stats:
        if mean_time > 1000:  # 平均执行时间 > 1s
            alerts.append({
                "type": "slow_avg_query",
                "severity": "info",
                "query": query[:200],
                "calls": calls,
                "mean_ms": mean_time,
                "timestamp": datetime.datetime.now().isoformat(),
            })
    return alerts


def run_checks():
    """执行所有检查。"""
    conn = psycopg2.connect(**PG_CONFIG)
    all_alerts = []

    all_alerts.extend(check_slow_queries(conn))
    all_alerts.extend(check_connection_count(conn))
    all_alerts.extend(check_idle_transactions(conn))
    all_alerts.extend(check_deadlocks(conn))
    all_alerts.extend(check_query_stats(conn))

    conn.close()
    return all_alerts


def log_alerts(alerts):
    """记录告警。"""
    if not alerts:
        return

    ALERT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(ALERT_LOG_PATH, "a") as f:
        for alert in alerts:
            f.write(json.dumps(alert) + "\n")

    for alert in alerts:
        logger.warning(f"[ALERT] {alert['type']}: {alert}")


def main():
    parser = argparse.ArgumentParser(description="PostgreSQL监控告警")
    parser.add_argument("--watch", action="store_true", help="持续监控")
    parser.add_argument("--interval", type=int, default=30, help="检查间隔（秒）")
    args = parser.parse_args()

    if args.watch:
        logger.info(f"开始持续监控，间隔 {args.interval}s")
        try:
            while True:
                alerts = run_checks()
                log_alerts(alerts)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("监控已停止")
    else:
        alerts = run_checks()
        log_alerts(alerts)
        if alerts:
            print(f"发现 {len(alerts)} 个告警")
            for alert in alerts:
                print(f"  [{alert['severity']}] {alert['type']}: {alert}")
        else:
            print("无告警")


if __name__ == "__main__":
    main()
```

#### [动作2] 执行单次监控检查

**操作**：在PowerShell中执行

```powershell
cd D:\ZephyrAlpha
python scripts\governance\monitor_pg.py
```

**预期输出**：`无告警`（或显示当前告警）。

#### [动作3] 验证慢查询检测

**操作**：在PowerShell中执行

```powershell
# 在一个终端启动慢查询
psql -U zephyr -d depgraph -c "SELECT pg_sleep(10);"

# 在另一个终端运行监控
python scripts\governance\monitor_pg.py
```

**预期输出**：监控检测到慢查询（duration > 5s）。

#### [动作4] 创建监控配置文件

**文件路径**：`d:\ZephyrAlpha\config\pg_monitor.yaml`

**操作**：创建新文件，内容如下：

```yaml
# PostgreSQL监控告警配置
pg_monitor:
  # 检查间隔（秒）
  interval: 30

  # 告警阈值
  thresholds:
    slow_query_seconds: 5
    max_connections: 150
    idle_transaction_seconds: 60
    deadlock_count: 1
    slow_avg_query_ms: 1000

  # 告警日志路径
  alert_log: data/databases/postgres/alerts.log

  # 告警通知方式（未来扩展）
  notifications:
    - type: log
      enabled: true
    # - type: webhook
    #   url: http://localhost:8080/alert
    #   enabled: false
```

### 7.4 验证清单

| # | 验证项 | 命令 | 预期结果 |
|---|--------|------|---------|
| 1 | 监控脚本可运行 | `python monitor_pg.py` | 无报错 |
| 2 | 慢查询检测 | pg_sleep(10) + 监控 | 检测到慢查询 |
| 3 | 连接数检测 | 并发连接 + 监控 | 显示当前连接数 |
| 4 | 告警日志写入 | 检查alerts.log | 有告警记录 |
| 5 | 持续监控 | `--watch --interval 5` | 每5s检查一次 |

### 7.5 受影响文件

| # | 文件路径 | 操作 | 说明 |
|---|---------|------|------|
| 1 | `scripts/governance/monitor_pg.py` | 新建 | 监控告警脚本 |
| 2 | `config/pg_monitor.yaml` | 新建 | 监控配置 |

---

## 八、回滚方案

### 8.1 回滚触发条件

- pgvector安装失败或embedding生成错误
- LISTEN/NOTIFY触发器导致写入性能严重退化
- 分区表迁移后查询性能退化（而非提升）
- 监控脚本占用过多资源

### 8.2 各阶段回滚步骤

#### 阶段1（pgvector）回滚

```powershell
# 1. 删除embedding列
psql -U zephyr -d depgraph -c "
ALTER TABLE nodes DROP COLUMN IF EXISTS embedding;
ALTER TABLE nodes DROP COLUMN IF EXISTS embedding_model;
ALTER TABLE nodes DROP COLUMN IF EXISTS embedding_updated_at;
"

# 2. 删除HNSW索引
psql -U zephyr -d depgraph -c "
DROP INDEX IF EXISTS idx_nodes_embedding;
"

# 3. 删除vector扩展
psql -U zephyr -d depgraph -c "DROP EXTENSION IF EXISTS vector;"
```

#### 阶段2（LISTEN/NOTIFY）回滚

```powershell
# 1. 删除触发器
psql -U zephyr -d depgraph -c "
DROP TRIGGER IF EXISTS tr_notify_node_insert ON nodes;
DROP TRIGGER IF EXISTS tr_notify_node_update ON nodes;
DROP TRIGGER IF EXISTS tr_notify_node_delete ON nodes;
DROP FUNCTION IF EXISTS notify_node_change();
"
```

#### 阶段3（分区表）回滚

```powershell
# 1. 恢复旧表（如果尚未删除）
psql -U zephyr -d depgraph -c "
DROP TABLE IF EXISTS nodes;
DROP TABLE IF EXISTS edges;
ALTER TABLE nodes_old RENAME TO nodes;
ALTER TABLE edges_old RENAME TO edges;
"

# 2. 如果旧表已删除，从备份恢复
psql -U zephyr -d depgraph -f data\databases\backups\depgraph_pre_partition.sql
```

#### 阶段4（监控）回滚

```powershell
# 直接停止监控脚本即可，无需数据库变更
```

### 8.3 回滚验证

| # | 验证项 | 预期结果 |
|---|--------|---------|
| 1 | 数据库可用 | apply_depgraph.py diagnose正常 |
| 2 | 数据完整 | 行数与迁移前一致 |
| 3 | 单元测试通过 | 全部通过 |
| 4 | 无残留优化对象 | 无embedding列、无NOTIFY触发器、无分区表 |

---

## 九、风险与缓解措施

| # | 风险 | 严重度 | 概率 | 缓解措施 |
|---|------|:---:|:---:|---------|
| 1 | pgvector安装失败 | 中 | 低 | 使用官方PostgreSQL安装包，手动安装pgvector |
| 2 | embedding生成耗时 | 中 | 中 | 批量更新，非阻塞 |
| 3 | LISTEN/NOTIFY触发器影响写入性能 | 中 | 中 | 触发器仅发送轻量JSON，测试验证 |
| 4 | LISTEN长连接稳定性 | 中 | 低 | LISTEN使用直连PG（5432） |
| 5 | 分区迁移数据丢失 | 高 | 低 | 迁移前后行数对比 + pg_dump备份 |
| 6 | 分区后外键失效 | 中 | 中 | 分区表外键支持有限，需调整约束 |
| 7 | 监控脚本资源占用 | 低 | 低 | 30s间隔，轻量查询 |
| 8 | 并发session冲突 | 中 | 中 | git分支隔离 + 并发session锁 |

---

## 十、受影响文件完整索引

### 10.1 新建文件

| # | 文件路径 | 阶段 | 说明 |
|---|---------|:---:|------|
| 1 | `src/zephyr/shared/utils/code_embedding.py` | 1 | Embedding工具 |
| 2 | `scripts/governance/update_embeddings.py` | 1 | 批量更新脚本 |
| 3 | `src/zephyr/shared/utils/pg_notify.py` | 2 | LISTEN/NOTIFY工具 |
| 4 | `src/zephyr/shared/utils/depgraph_events.py` | 2 | 事件通知集成 |
| 5 | `scripts/governance/migrate_sqlite_to_pg/02_partition_tables.sql` | 3 | 分区迁移脚本 |
| 6 | `scripts/governance/migrate_sqlite_to_pg/performance_baseline.txt` | 3 | 性能基线 |
| 7 | `scripts/governance/migrate_sqlite_to_pg/performance_after_partition.txt` | 3 | 分区后性能 |
| 8 | `scripts/governance/monitor_pg.py` | 4 | 监控告警脚本 |
| 9 | `config/pg_monitor.yaml` | 4 | 监控配置 |

### 10.2 修改文件

| # | 文件路径 | 阶段 | 修改说明 |
|---|---------|:---:|---------|
| 1 | `scripts/governance/migrate_sqlite_to_pg/01_create_extensions.sql` | 1 | 启用vector扩展 |
| 2 | `requirements.txt` | 1 | 添加sentence-transformers |
| 3 | `src/zephyr/governance/depgraph_schema.py` | 3 | Schema DDL改为分区表 |

### 10.3 需同步更新的文档

| # | 文件路径 | 更新内容 |
|---|---------|---------|
| 1 | `docs/03_modules/_cross_layer/database/blueprint.md` | MOD-DB_DEPGRAPH_PG状态更新 |
| 2 | `docs/02_enterprise_architecture/dependency_architecture_panorama.md` | 全景图优化说明 |
| 3 | `docs/03_modules/_cross_layer/database/sub_blueprints/index.md` | 子蓝图索引更新 |

---

## 十一、文档循环审查清单

本文档完成后，必须按以下清单循环审查，直到问题数=0：

| # | 审查项 | 检查方法 | 通过标准 |
|---|--------|---------|---------|
| 1 | 前后术语一致 | 全文搜索关键术语 | 同一术语全文统一 |
| 2 | 文件路径一致 | 全文搜索文件路径 | 路径前后一致 |
| 3 | 施工步骤无遗漏 | 对照4个优化项 | 4项全覆盖 |
| 4 | 依赖关系正确 | 阶段间依赖检查 | 均依赖P2完成 |
| 5 | 验证清单完整 | 每个阶段有验证 | 每阶段≥5项验证 |
| 6 | 回滚方案可行 | 回滚步骤可执行 | 4阶段各有回滚 |
| 7 | 风险识别完整 | 8项风险全覆盖 | 每项有缓解措施 |
| 8 | 受影响文件完整 | 对照各阶段 | 文件数匹配 |
| 9 | 代码示例可执行 | 代码语法检查 | 无语法错误 |
| 10 | 配置参数合理 | 对照PG最佳实践 | 参数值合理 |
| 11 | 与P2文档一致 | 对照P2文档 | 术语/路径/配置一致 |
| 12 | pgvector设计合理 | 对照pgvector文档 | 维度/索引类型正确 |
| 13 | LISTEN/NOTIFY设计合理 | 对照PG文档 | 直连PostgreSQL |
| 14 | 分区设计合理 | 对照PG分区文档 | HASH分区8个合理 |

**审查流程**：
1. 按清单逐项检查
2. 记录问题
3. 修复问题
4. 重新检查
5. 连续2次0问题 → 通过
