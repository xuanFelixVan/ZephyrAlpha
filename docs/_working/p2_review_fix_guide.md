---
doc_type: knowledge_entry
status: active
title: "P2迁移审查——修复指南（防漂移真源+向内收审核）"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "2.0.0"
created: "2026-06-28"
ttl: task_bound
completes_when: "P2审查全部完成，本指南归档"
---

# P2迁移审查——修复指南

> **所有AI修复前MUST先读本文件**。本文件是修复行为的唯一真源，防止漂移和幻觉。

---

## 一、修复真源文件清单（修复前MUST先读对应文件）

修复任何问题前，必须先读取以下对应真源文件，对照实现，不得臆测：

### 1. PG连接权威实现（连接/查询相关修复）
| 真源文件 | 作用 |
|---------|------|
| `src/zephyr/governance/depgraph_schema.py` | `get_db_connection()` 函数签名和实现——PG连接唯一入口 |
| `src/zephyr/governance/database_service.py` | `DatabaseService` 类——三库统一管理正确实现 |
| `scripts/governance/_shared/constants.py` | `PgConnExecuteWrapper` + `get_depgraph_pg_connection()`——兼容sqlite3接口的wrapper（AI-06 审查纠正：原指南引用的 `src/zephyr/governance/pg_conn_wrapper.py` 从未存在，git log 无历史记录；实际类定义在 `_shared/constants.py` L51-107） |

### 2. depgraph访问协议（流程/规范相关修复）
| 真源文件 | 作用 |
|---------|------|
| `docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml` | v1.4.0，depgraph访问协议（备份/锁/事务） |

### 3. P2迁移方案文档（迁移范围/标准相关修复）
| 真源文件 | 作用 |
|---------|------|
| `docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md` | P2迁移完整方案，含§12.3文档同步+§12.4测试适配清单 |

### 4. module_id三轨制（命名相关修复）
| 真源文件 | 作用 |
|---------|------|
| `scripts/governance/validate_module_id_naming.py` | module_id正则真源（三轨制） |
| 对照表 | `MOD-INF-012B-P2` → `MOD-DB_DEPGRAPH_PG`；`MOD-INF-012B-P3` → `MOD-DB_DEPGRAPH_OPT` |

### 5. 项目宪法（全局约束相关修复）
| 真源文件 | 作用 |
|---------|------|
| `AGENTS.md` | REPO_ROOT真源、文件命名规范、TTL要求、GitCommitGateway |

---

## 二、SQL方言对照表（修复depgraph相关代码的唯一标准）

| SQLite（违规） | PostgreSQL（正确） | 场景 |
|---------------|-------------------|------|
| `sqlite3.connect(path)` | `get_db_connection()` | 连接depgraph |
| `import sqlite3`（depgraph上下文） | `import psycopg2` + `from zephyr.governance.depgraph_schema import get_db_connection` | 导入 |
| `?` | `%s` | 参数占位符 |
| `INSERT OR REPLACE INTO` | `INSERT INTO ... ON CONFLICT (pk) DO UPDATE SET` | upsert |
| `sqlite_master` | `information_schema.tables` | 查表结构 |
| `GROUP_CONCAT(x)` | `STRING_AGG(x::text, ',')` | 聚合 |
| `AUTOINCREMENT` | `GENERATED ALWAYS AS IDENTITY` | 自增主键 |
| `conn.execute(sql).fetchone()` | `with conn.cursor() as cur: cur.execute(sql); cur.fetchone()` | 查询 |
| `conn.execute(sql).fetchall()` | `with conn.cursor() as cur: cur.execute(sql); cur.fetchall()` | 查询 |
| `row[0]` / `row[1]` | `row["col_name"]` | 结果访问 |
| `sqlite3.Error` | `psycopg2.Error` | 错误处理 |
| `sqlite3.IntegrityError` | `psycopg2.IntegrityError` | 错误处理 |
| `sqlite3.OperationalError` | `psycopg2.OperationalError` | 错误处理 |
| `sqlite3.Row` | `RealDictCursor`（`psycopg2.extras.RealDictCursor`） | 行工厂 |
| `PRAGMA journal_mode=WAL` | （移除，PG默认MVCC） | WAL |
| `PRAGMA busy_timeout=N` | `statement_timeout` | 超时 |
| `last_insert_rowid()` | `RETURNING id` | 获取自增ID |
| `sqlite_sequence` | `pg_sequences` | 序列表 |

---

## 三、修复约束（防漂移防幻觉——铁律）

1. **真源优先**：修复前MUST先读取第一节对应的真源文件，对照实现
2. **最小改动**：只改不合规的部分，不重构不优化不加无关注释
3. **不引入新依赖**：修复不得引入新的sqlite3依赖（governance.db上下文除外）
4. **不越界**：只修改自己分区的文件，不得修改其他AI分区的文件
5. **记录留痕**：报告中记录 `原代码 → 新代码 → 依据文件`
6. **豁免确认**：
   - `governance.db` 用 `sqlite3` 是**正确的**，不得修改
   - `market.duckdb` 用 `duckdb` 是**正确的**，不得修改
   - 只有 `depgraph` 相关的 sqlite3 残留才是违规
7. **跨区问题**：如果问题跨文件/跨分区，只记录不修复，在报告中标注 `需主AI协调`
8. **REPO_ROOT**：使用 `from zephyr.shared.io.paths import REPO_ROOT`，禁止 `Path(__file__).parents[N]`
9. **TTL字段**：.md文件frontmatter含 `ttl`，.py文件头部含 `# [TTL]`（task_bound或permanent）
10. **GitCommitGateway**：修复后如需commit，必须通过 `python scripts/git_commit.py`，禁止裸git commit
11. **不臆测**：如果不确定某代码是否违规，先Read确认上下文，仍不确定则记录为"提示项"不修复
12. **不创建新文件**：修复只修改已有文件，不得创建新文件（除非修复指南明确要求）

---

## 四、自修复循环流程

```
┌─────────────────────────────────────────┐
│  第N轮审查                                │
│  1. Grep搜索关键词                        │
│  2. Read确认上下文（区分depgraph vs 其他）  │
│  3. 发现问题清单                           │
└──────────────┬──────────────────────────┘
               │
               ▼ 有问题
┌─────────────────────────────────────────┐
│  修复阶段                                 │
│  1. 读取修复指南（本文件）                  │
│  2. 读取对应真源文件                       │
│  3. Edit修复（最小改动）                   │
│  4. 记录：原代码 → 新代码 → 依据           │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  第N+1轮审查（复审）                       │
│  1. 重新Grep搜索关键词                     │
│  2. 确认修复生效                           │
│  3. 发现新问题？                           │
│     → 是：继续修复，进入第N+2轮            │
│     → 否：本轮问题数=0                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  连续两次问题数=0？                        │
│  → 是：审查通过 ✅，写最终报告             │
│  → 否：继续循环                           │
└─────────────────────────────────────────┘
```

**最大循环次数**：5轮。若5轮后仍有问题，停止修复，在报告中标注 `需主AI介入`。

---

## 五、汇报机制

### 5.1 每个AI写独立报告

写入路径：`D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-XX_report.md`

### 5.2 报告格式（升级版——含修复记录）

```markdown
---
doc_type: audit_report
status: active
title: "AI-XX 审查报告——P2迁移自修复"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "1.0.0"
created: "2026-06-28"
ttl: task_bound
completes_when: "报告归档"
---

# AI-XX 审查报告

## 元信息
- 审查轮次：共N轮
- 审查时间：2026-06-28
- 负责分区：xxx
- 审查文件数：XX
- 最终状态：✅ 通过 / ⚠️ 需主AI协调

## 审查结果汇总
- 初始问题数：X
- 修复问题数：X
- 残留问题数：X
- 连续零问题轮次：第N轮、第N+1轮

## 修复记录

### 修复1
- **文件**：path/to/file.py
- **行号**：L123
- **类别**：A1 (sqlite3.connect连depgraph)
- **原代码**：
  ```python
  conn = sqlite3.connect("data/databases/depgraph.db")
  ```
- **新代码**：
  ```python
  from zephyr.governance.depgraph_schema import get_db_connection
  conn = get_db_connection(autocommit=True)
  ```
- **依据文件**：src/zephyr/governance/depgraph_schema.py

### 修复2
...

## 未修复问题（需主AI协调）
### 问题1
- **文件**：path/to/file.py
- **行号**：L456
- **类别**：跨分区依赖
- **描述**：xxx
- **原因**：涉及其他AI分区，未修复

## 确认无问题项
- 检查项X：✅ 通过
- 检查项Y：✅ 通过

## 结论
- [x] 无问题，本分区审查通过（连续两次=0）
- [ ] 有残留问题，需主AI协调
```

### 5.3 汇总机制

- 所有19个AI完成后，主对话（当前对话）读取所有 `AI-XX_report.md`
- 按13项清单分类汇总
- 更新 `p2_migration_review_checklist.md` 的审查记录表格
- 若所有项连续两次=0，逐项打✅

---

## 六、常见问题判定

| 场景 | 判定 | 处理 |
|------|------|------|
| `sqlite3.connect("governance.db")` | ✅ 豁免 | 不修复 |
| `sqlite3.connect("depgraph.db")` | ❌ 违规 | 改为 `get_db_connection()` |
| `duckdb.connect("market.duckdb")` | ✅ 豁免 | 不修复 |
| `conn.execute("SELECT 1").fetchone()` 用于governance | ✅ 豁免 | 不修复 |
| `conn.execute("SELECT 1").fetchone()` 用于depgraph(psycopg2) | ❌ 违规 | 改为cursor模式 |
| 文档中历史记录提到"depgraph.db曾是SQLite" | ✅ 合理 | 不修复 |
| 文档中当前状态仍说"depgraph.db是SQLite" | ❌ 违规 | 更新为PG |
| `MOD-INF-012B-P2` 在frontmatter | ❌ 违规 | 改为 `MOD-DB_DEPGRAPH_PG` |
| `MOD-INF-012B-P2` 在历史commit记录 | ✅ 豁免 | 不修复 |
| `?` 占位符用于governance.db查询 | ✅ 豁免 | 不修复 |
| `?` 占位符用于depgraph查询 | ❌ 违规 | 改为 `%s` |
| `Path(__file__).parents[3]` 推算REPO_ROOT | ❌ 违规 | 改为 `from zephyr.shared.io.paths import REPO_ROOT` |

---

## 七、向内收工作逻辑审核标准（元思考层——所有AI MUST遵循）

> **本节是所有AI工作行为的元准则**。审查和修复时，不仅要检查技术合规性（SQL方言/连接方式），还要用以下逻辑审核你所有对话里所有的工作。违反本节准则的"修复"本身也是漂移。

### 7.1 责任唯一，真源唯一

项目文件做到：**责任唯一，真源唯一**。

- 就算是一个真源，多个地方同步，也增加了同步的成本，而且AI不可能去同步
- 能用一个的绝对不用多个
- 减少幻觉和漂移

**审查判定**：如果发现同一信息在多处定义（如正则在两个文件各写一份、配置在代码和YAML各存一份），记录为"一般问题"，建议合并到唯一真源。

---

### 7.2 向内收——AI工作的核心逻辑

整个项目，AI的工作一定是**"向内收的"**。具体工作逻辑：

#### 7.2.1 能用现成的不创造

能用现成有的绝对不创造，创造是没办法才创建。

- 工作之前先查找有没有能用的
- 能增加功能扩展功能优先，不要同步之类的
- 扩展已有 > 创建新建

**审查判定**：如果发现修复中创建了新文件（而非扩展现有文件），检查是否真的无法扩展。能扩展却新建的，记录为"一般问题"。

#### 7.2.2 永久性系统必须全自动

创造的永久性系统或功能脚本，必须：
- ✅ 自动事件触发
- ✅ 自动运行
- ✅ 自动维护
- ✅ 自动关闭
- ✅ 全自动，不能有需要手工触发的（除非特殊情况功能）
- ❌ 不能有时间触发的（时间触发等于需要人工指令触发，没达成自动触发目的）

**审查判定**：如果发现永久性脚本需手工运行或用定时器触发，记录为"一般问题"，建议改为事件驱动。

#### 7.2.3 第一性原理治本

想问题、解决问题，都要从**第一性原理**出发，**治本**的原理出发先思考问题本身：

- 元问题是否合理？是否应该存在？
- 在100% AI开发的项目里，上下文有限的AI只有这么多记忆力，依靠用户在Trae里和AI对话进行触发工作
- 这个要解决的问题、功能本身**该不该存在**？
  - 是不是要**删除**？
  - 或者**合并**进其他已有功能？
- 如果要存在，该如何运行？如何最大程度确保：
  - 唯一真源
  - 唯一责任
  - 自动维护
  - 自动运行
  - 甚至无需维护
  - 未来每个刚进项目的AI，在运行此功能相关内容时，不会产生漂移幻觉，不会另行创建、建造

**审查判定**：如果发现修复只是"打补丁"未治本（如加了 workaround 而非解决根因），记录为"提示项"，建议重新思考根因。

#### 7.2.4 AI可发现性双问

创建新功能或维护已有功能/文件/规则/数据库等一切内容，思考两个问题：

1. **刚进项目没有上下文的AI，如何知道有这个内容或功能并使用？**
2. **AI在准备进行涉及这个内容的工作时，如何知道有这个内容或功能，而不会去创造？**

**审查判定**：如果发现某功能/文件/规则无法被新AI通过标准入口（AGENTS.md / capability_canonical_file_registry.yaml / __all__ 等）发现，记录为"一般问题"，建议补充可发现性注册。

---

### 7.3 红蓝极限对抗审核（最终验证层）

在技术审查和修复完成后，每个AI MUST对自己的工作执行以下审核：

#### 7.3.1 模拟新AI可发现性测试

模拟一个刚进项目、零上下文的AI，测试你所有对话完成的所有功能：

| 测试项 | 判定标准 |
|--------|---------|
| 可被发现性 | 新AI能否通过 AGENTS.md / 注册表 / 标准入口 发现这个功能？ |
| 可被绕过性 | 新AI能否绕过这个功能自行实现？（绕过=真源分裂风险） |
| 可被使用性 | 新AI发现后，能否正确使用？接口是否清晰？ |
| 可被重复造轮子性 | 新AI是否容易重复造一个同类功能？（容易=注册不足） |

#### 7.3.2 红蓝极限对抗测试

对你完成的所有功能和达成的目的做全面的红蓝极限对抗测试：

- **红方**：尝试破坏/绕过/误用你修复的功能
- **蓝方**：验证修复是否抵御住了红方攻击
- 发现的对抗漏洞记录在报告中

---

### 7.4 最终大白话汇报

审查和修复全部完成后，在报告末尾追加**大白话汇报**章节：

```markdown
## 大白话汇报（向内收审核结论）

### 我做了什么
（一句话说清楚）

### 这个功能的作用
（一句话说清楚）

### 达成了什么目标
（一句话说清楚）

### 解决了什么痛点
（一句话说清楚）

### 功能通过什么触发自动启动
（事件驱动？什么事件？）

### 如何自动运行
（触发后做什么？）

### 如何自动关闭
（什么时候结束？需要人工干预吗？）

### 向内收审核结果
- [ ] 责任唯一真源唯一：通过/发现问题X
- [ ] 能用现成不创造：通过/发现问题X
- [ ] 永久系统全自动：通过/发现问题X
- [ ] 第一性原理治本：通过/发现问题X
- [ ] AI可发现性：通过/发现问题X
- [ ] 红蓝对抗：通过/发现问题X
```

---

### 7.5 本节审查结论如何写入报告

每个AI的 `AI-XX_report.md` 末尾MUST包含第7.4节的"大白话汇报"章节。若向内收审核发现问题，记入"未修复问题（需主AI协调）"并标注类别：
- `[向内收-真源分裂]` 同一信息多处定义
- `[向内收-不必要的创造]` 能扩展却新建
- `[向内收-非全自动]` 需手工触发或定时触发
- `[向内收-未治本]` 打补丁未解决根因
- `[向内收-不可发现]` 新AI无法发现此功能
- `[向内收-可被绕过]` 新AI可绕过真源自行实现
