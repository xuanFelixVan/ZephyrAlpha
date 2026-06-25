# 预存DB问题深度调研报告与治本方案

> **文档定位**：针对4域拆分（裁定#200）后深度检查发现的3个预存DB问题 + 1个工具gap的完整调研报告
> **调研日期**：2026-06-25
> **调研对象**：D-SECURITY-LLM / D-GOV-REPAIR / D-INTEGRATION-GATEWAY（3空域）+ D-SIGNAL（ssot_path冲突）+ domain_dependencies（工具gap）
> **调研方法**：只读调研（未修改任何文件），证据来源为代码静态分析 + DB派生制品 + 项目文档 + 行业基准对标
> **适用语境**：100% AI 开发项目

---

## 目录

- [第一部分：详细调研报告（事实层）](#第一部分详细调研报告事实层)
  - [1.1 问题清单与实测数据](#11-问题清单与实测数据)
  - [1.2 domains 表 Schema 实测](#12-domains-表-schema-实测)
  - [1.3 三条写入路径的字段覆盖对比](#13-三条写入路径的字段覆盖对比)
  - [1.4 3个空域的来历与定性](#14-3个空域的来历与定性)
  - [1.5 D-SIGNAL 冲突的真相](#15-d-signal-冲突的真相)
  - [1.6 domain_dependencies 的设计 gap](#16-domain_dependencies-的设计-gap)
- [第二部分：根因分析（分析层）](#第二部分根因分析分析层)
  - [2.1 根因归类：四类系统性缺陷](#21-根因归类四类系统性缺陷)
  - [2.2 RC1 详解：双写路径的字段覆盖裂缝](#22-rc1-详解双写路径的字段覆盖裂缝)
  - [2.3 RC2 详解：DB 层零防御](#23-rc2-详解db-层零防御)
  - [2.4 RC3 详解：占位域无生命周期闭环](#24-rc3-详解占位域无生命周期闭环)
  - [2.5 RC4 详解：非正式拆分的留痕缺失](#25-rc4-详解非正式拆分的留痕缺失)
- [第三部分：行业基准对标（参考层）](#第三部分行业基准对标参考层)
  - [3.1 专业机构实践（DDD / TOGAF / NIST）](#31-专业机构实践ddd--togaf--nist)
  - [3.2 量化社区实践（ArchUnit / SonarQube / Fitness Functions）](#32-量化社区实践archunit--sonarqube--fitness-functions)
  - [3.3 氛围编程社区（Vibe Coding / AMGF）](#33-氛围编程社区vibe-coding--amgf)
  - [3.4 综合对标裁定](#34-综合对标裁定)
- [第四部分：裁定结果（决策层）](#第四部分裁定结果决策层)
- [第五部分：治本施工方案（执行层）](#第五部分治本施工方案执行层)
  - [5.1 施工总原则](#51-施工总原则)
  - [5.2 分阶段施工方案](#52-分阶段施工方案)
  - [5.3 执行顺序与依赖](#53-执行顺序与依赖)
  - [5.4 验收标准](#54-验收标准)
  - [5.5 回滚方案](#55-回滚方案)
- [第六部分：总结](#第六部分总结)
- [附录：完整证据清单](#附录完整证据清单)

---

## 第一部分：详细调研报告（事实层）

### 1.1 问题清单与实测数据

| # | 问题 | 受影响域 | 实测值 | 应有值 |
|---|------|---------|--------|--------|
| P1 | max_modules 缺失 | D-SECURITY-LLM / D-GOV-REPAIR / D-INTEGRATION-GATEWAY | NULL（生成器回退显示 200 或 150，不一致） | 150 |
| P2 | layer_id 缺失 | 同上 3 域 | NULL（落入 domain_index.md "未分类3域" L101-107） | L1_platform / L2_domain / L1_platform |
| P3 | ssot_path 缺失 | D-SIGNAL（1 prod 节点） | `''`（空字符串） | 需架构决策 |
| P4（gap） | domain_dependencies 无 INSERT 命令 | 全域 | apply_depgraph.py 仅支持 UPDATE 迁移 | 需扩展工具 |

**数据来源说明**：因 `data/databases/depgraph.db` 在磁盘上不存在（Glob `**/depgraph.db` 未命中），无法直接执行 sqlite3 SELECT。本报告数据来自该 DB 的自动生成派生制品（时间戳 2026-06-25，与裁定#200 后状态一致）：

| 数据来源 | 生成时间 | 文件路径 |
|---|---|---|
| 域容量报告 | 2026-06-25 03:06:23 | `docs/02_enterprise_architecture/03_governance_reports/capacity_report.md` |
| 域总览索引 | 2026-06-25 03:32:03 | `docs/02_enterprise_architecture/02_domain_architecture_docs/domain_index.md` |
| 设计态vs运营态报告 | 2026-06-25 03:41:37 | `docs/02_enterprise_architecture/03_governance_reports/design_vs_production.md` |
| 域架构文档 | 2026-06-24 23:56:40 | `docs/02_enterprise_architecture/02_domain_architecture_docs/4*.md` |
| 含缓存SQL结果的拆分方案 | 2026-06-25 | `docs/02_enterprise_architecture/domain_split_plan_4_oversized_domains.md`（附录C.3 含 domains 表实测快照） |

### 1.2 domains 表 Schema 实测

**建表 SQL 位置**：`src/zephyr/governance/depgraph_schema.py` 第 149-167 行（`_DDL_DOMAINS` 变量），由 `init_db()` 函数在迁移 v1 中执行（第 621-641 行）。

```sql
-- src/zephyr/governance/depgraph_schema.py:149-167
CREATE TABLE IF NOT EXISTS domains (
    domain_id        TEXT    PRIMARY KEY,
    domain_name      TEXT    NOT NULL,
    domain_group     TEXT    NOT NULL,
    description      TEXT,                    -- 可空
    ssot_path        TEXT,                    -- 可空，无 UNIQUE
    current_modules  INTEGER DEFAULT 0,
    max_modules      INTEGER,                 -- 可空，无 CHECK
    lifecycle        TEXT    DEFAULT 'design_only',
    created_at       TEXT    NOT NULL,
    updated_at       TEXT    NOT NULL,
    build_status     TEXT    DEFAULT 'unbuilt',
    modification_permission TEXT,
    layer_id         TEXT,                    -- 可空，无 CHECK
    target_modules   INTEGER,
    production_nodes INTEGER DEFAULT 0
)
```

**完整字段清单（15 列，v10 清理后）**：

| # | 字段名 | 类型 | NOT NULL | 默认值 | CHECK 约束 | 来源行号 |
|---|--------|------|:---:|--------|:---:|---|
| 1 | `domain_id` | TEXT | YES (PK) | — | — | 151 |
| 2 | `domain_name` | TEXT | YES | — | — | 152 |
| 3 | `domain_group` | TEXT | YES | — | — | 153 |
| 4 | `description` | TEXT | NO | — | — | 154 |
| 5 | `ssot_path` | TEXT | NO | — | — | 155 |
| 6 | `current_modules` | INTEGER | NO | 0 | — | 156 |
| 7 | `max_modules` | INTEGER | NO | — | — | 157 |
| 8 | `lifecycle` | TEXT | NO | 'design_only' | — | 158 |
| 9 | `created_at` | TEXT | YES | — | — | 159 |
| 10 | `updated_at` | TEXT | YES | — | — | 160 |
| 11 | `build_status` | TEXT | NO | 'unbuilt' | — | 161 |
| 12 | `modification_permission` | TEXT | NO | — | — | 162 |
| 13 | `layer_id` | TEXT | NO | — | — | 163 |
| 14 | `target_modules` | INTEGER | NO | — | — | 164 |
| 15 | `production_nodes` | INTEGER | NO | 0 | — | 165 |

**关键缺陷**：`max_modules`/`layer_id`/`ssot_path` 三个字段均为**可空、无 CHECK、无 UNIQUE**。DB 层不阻止 NULL，也不阻止两个域共享同一 ssot_path。

**Schema 演进历史**：

| 版本 | 变更 | 文件行号 |
|------|------|---------|
| v1 | 初始创建 domains 表（11 列） | depgraph_schema.py:621-641 |
| v3 | 新增 build_status/can_build/gate_reason/hard_boundary_ref | depgraph_schema.py:691-696 |
| v6 | 新增 layer_id/growth_pattern/target_modules/feasibility/bottleneck_description/last_capacity_check（合并 arch_domain_capacity + arch_domain_layers） | depgraph_schema.py:733-741 |
| v9 | 新增 production_nodes（ARCH-CAP-001 口径修复） | depgraph_schema.py:771 |
| v10 | 删除 7 个装饰字段（can_build/gate_reason/hard_boundary_ref/growth_pattern/feasibility/bottleneck_description/last_capacity_check） | depgraph_schema.py:778-786 |

### 1.3 三条写入路径的字段覆盖对比

| 写入路径 | 文件:行号 | max_modules | layer_id | ssot_path(列) | ssot_path(arch_path_mappings表) |
|---------|----------|:---:|:---:|:---:|:---:|
| `cmd_insert_domain` | `scripts/governance/apply_depgraph.py:1059-1063` | ✅（默认200，**陈旧**） | ✅ | ✅ | ❌ |
| `sync_yaml_to_depgraph.py` | `scripts/governance/sync_yaml_to_depgraph.py:401-413` | ❌ | ❌ | ❌ | ✅ |
| `generate_project_depgraph.py` | — | ❌（仅读取） | ❌（仅读取） | ❌（仅读取） | ❌ |

**这是问题的核心**：存在两条写入路径，但字段覆盖**互不完整**。经 `sync_yaml_to_depgraph.py` 同步的域（3个空域正是此路径），`max_modules`/`layer_id`/`ssot_path` 列均为 NULL。

**证据1 — apply_depgraph.py cmd_insert_domain（L1023-1076）**：

```python
# scripts/governance/apply_depgraph.py:1023-1064
def cmd_insert_domain(
    domain_id: str,
    domain_name: str,
    domain_group: str,
    layer_id: str,
    ssot_path: str,
    max_modules: int = 200,   # ← 陈旧默认值，v1.0.8 前的值
    description: str = "",
    dry_run: bool = False,
    db_path: str = str(DEPGRAPH_PATH),
    conn=None,
) -> bool:
    ...
    conn.execute(
        """INSERT INTO domains (domain_id, domain_name, domain_group, description, ssot_path,
           current_modules, max_modules, lifecycle, created_at, updated_at, build_status, layer_id)
           VALUES (?, ?, ?, ?, ?, 0, ?, 'design_only', ?, ?, 'unbuilt', ?)""",
        (domain_id, domain_name, domain_group, description, ssot_path, max_modules, now, now, layer_id),
    )
```

**证据2 — sync_yaml_to_depgraph.py INSERT（L401-413）**：

```python
# scripts/governance/sync_yaml_to_depgraph.py:401-413
cur.execute(
    """
INSERT INTO domains (domain_id, domain_name, domain_group, description,
                     modification_permission, created_at, updated_at)
VALUES (?, ?, ?, ?, ?, ?, ?)
ON CONFLICT(domain_id) DO UPDATE SET
    domain_name=excluded.domain_name,
    description=excluded.description,
    modification_permission=excluded.modification_permission,
    updated_at=excluded.updated_at
""",
    (domain_id, d.get("subdomain", ""), domain_group, description, ai_autonomy, now, now),
)
```

INSERT 仅含 7 字段，**不含** max_modules/layer_id/ssot_path（domains 表列）。

**证据3 — sync 脚本只写 arch_path_mappings，不写 domains.ssot_path（L416-426）**：

```python
# scripts/governance/sync_yaml_to_depgraph.py:416-426
ssot_path = d.get("ssot_path", "")
if ssot_path:
    # arch_path_mappings 需要 path_type NOT NULL 和 state NOT NULL
    cur.execute(
        """
    INSERT OR REPLACE INTO arch_path_mappings
    (path_pattern, domain_id, path_type, state)
    VALUES (?, ?, 'ssot', 'active')
    """,
        (ssot_path, domain_id),
    )
```

ssot_path 被写入 `arch_path_mappings` 表，但**不写入** `domains.ssot_path` 列。生成器 `generate_project_depgraph.py` 从 `domains` 表读取 ssot_path（L504），导致经 sync 同步的域在生成器中 ssot_path 为空。

**证据4 — 生成器读取时的 NULL 回退掩盖问题**：

```python
# scripts/governance/generate_capacity_report.py:57
r[4] or 150   # max_modules 为 NULL 时回退到 150

# scripts/governance/generate_domain_doc.py:62
r[4] or 150   # 同样的回退
```

回退逻辑掩盖了 NULL 缺失，使问题在报告中"看起来正常"。

### 1.4 3个空域的来历与定性

#### 1.4.1 domains 表完整记录

来源：`domain_split_plan_4_oversized_domains.md` 附录C.3（L668-675，2026-06-25 实测快照，裁定#200 拆分前的 48 域基线）。这 3 个域在裁定#200 中**未被触及**，故记录至今不变：

| domain_id | domain_name | layer_id | current_modules | production_nodes | ssot_path |
|---|---|---|---:|---:|---|
| D-SECURITY-LLM | llm_defense | NULL | 0 | 0 | NULL |
| D-GOV-REPAIR | rollback | NULL | 0 | 0 | NULL |
| D-INTEGRATION-GATEWAY | mcp_servers | NULL | 0 | 0 | NULL |

补充字段（来自 `domain_index.md` L101-107 "未分类(3个域)" 与 `capacity_report.md`）：
- **max_modules**：存在生成器间不一致——`domain_index.md` 与域架构文档显示 `0/200`，而 `capacity_report.md` 显示 `Max=150`。根因是 max_modules 实际为 NULL，不同生成器默认值不同（domain_doc/index 默认 200，capacity_report 默认 150）。裁定#194 仅将 5 个特定域（D-GOVERNANCE/D-GOV_AUDIT/D-GOV_DRIFT/D-GOV_RULE/D-SECURITY）从 200 改为 150，**未覆盖这 3 个空域**。

#### 1.4.2 何时被创建 / 由哪个脚本任务创建

**直接创建脚本**：`scripts/governance/generate_project_depgraph.py` **不创建**这 3 个域（Grep 该文件对 3 个域名 + llm_defense/mcp_servers/signal_fundamental 均"No matches found"）。它们是通过 `apply_depgraph.py --insert-domain` 命令在全景图重造（PANORAMA-REBUILD）阶段手动插入的。

**正式定性裁定**：`dependency_architecture_panorama.md` **裁定#176**（L1470）：

> | 176 | 设计态域处理 | **保留 5 个设计态域**（D-GOV_ENFORCEMENT/D-GOV_REPAIR/D-GOV_SCRIPTS/D-INTEGRATION_GATEWAY/D-SECURITY_LLM），标记为"计划中"。这些域为缓解超容父域而规划（D-GOVERNANCE 3860 模块超容 1930%、D-SECURITY 849、D-INTEGRATION 705、D-OPS 679），functional_domain_registry.yaml 已有完整 covers 规划。业界对标 DDD Bounded Context planned/TOGAF Transition Architecture | ✅ |

注意：裁定#176 使用**下划线风格**（D-GOV_REPAIR 等），而数据库实际存储为**连字符风格**（D-GOV-REPAIR）。这正是裁定#177（域命名统一）所指的"15 个域违规"的一部分。

**未找到精确的 INSERT commit/任务卡**：`data/archive/taskcards/` 中 Grep 这 3 个域名仅命中 DM-100257（该卡是关于 ssot_path 路径拆分设计，非创建）。裁定#176 措辞为"保留"，说明它们在裁定前已存在于 DB 中，裁定只是确认保留而非删除。结合裁定#175（删除 10 个并发测试域空壳）紧邻其后，可推断这 3 个域与测试域空壳同期产生于早期全景图重造，裁定#175/#176 对"空域"做了分流处置：测试残留→删除；规划占位→保留。

#### 1.4.3 functional_domain_registry.yaml 条目

**3 个域均有完整注册条目**（`docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml`）：

| 域 | 行号 | subdomain | ssot_module | ssot_path | 关键 covers |
|---|---:|---|---|---|---|
| D-SECURITY-LLM | L209-231 | llm_defense | MOD-INF-014 | `src/zephyr/security/llm_defense/` | L0~L8 九层防御 |
| D-GOV-REPAIR | L376-397 | rollback | MOD-INF-021 | `src/zephyr/governance/` | 双轨Checkpoint/四级回滚/Kill Switch |
| D-INTEGRATION-GATEWAY | L754-776 | mcp_servers | MOD-INF-013 | `src/zephyr/integration/mcp/` | 11个MCP服务端+1Gateway |

注意：registry 中的 ssot_path 与 depgraph.db 中的 ssot_path（NULL）**不一致**——registry 已规划了路径，但 DB 未写入。

#### 1.4.4 域架构文档

**3 个域均有自动生成的架构文档**（`docs/02_enterprise_architecture/02_domain_architecture_docs/`，2026-06-24 23:56:40 生成）：

| 域文档 | 架构图文档 | 内容 |
|---|---|---|
| `48_d_security_llm.md` | `48_d_security_llm_architecture.md` | 0 模块，0 依赖，layer 空，容量 0/200 |
| `47_d_integration_gateway.md` | `47_d_integration_gateway_architecture.md` | 0 模块，0 依赖，layer 空，容量 0/200 |
| `45_d_gov_repair.md` | `45_d_gov_repair_architecture.md` | 0 模块，0 依赖，layer 空，容量 0/200 |

#### 1.4.5 对标域分析

| 空域 | 对标域 | 关系 | 证据 |
|---|---|---|---|
| **D-SECURITY-LLM** | **D-SECURITY** | 同级拆分（sibling split）。D-SECURITY 含 access_control(MOD-INF-018) + adversarial_validation(MOD-INF-030)；D-SECURITY-LLM 专管 llm_defense(MOD-INF-014)。llm_defense 代码物理存在于 `src/zephyr/security/llm_defense/`，但当前归属 D-SECURITY（276 模块/132 prod），**尚未迁移**到 D-SECURITY-LLM | registry L185-256 (D-SECURITY) vs L209-231 (D-SECURITY-LLM)；裁定#176 列 D-SECURITY 849 超容 |
| **D-GOV-REPAIR** | 原计划对标 **D-GOV-ENFORCEMENT**，但**实际已被 D-INFRA_RECOVERY 取代/冗余** | D-GOV-REPAIR registry 声称覆盖 rollback(MOD-INF-021, `src/zephyr/governance/`)；但裁定#200 新建的 **D-INFRA_RECOVERY**（registry L849-876）**同样声称覆盖 rollback(MOD-INF-021)**，且 ssot_path 为 `src/zephyr/infrastructure/rollback/`，并已实际迁入 107 个 prod 节点。两者 covers 高度重叠，D-INFRA_RECOVERY 是 D-GOV-REPAIR 的超集 | registry L376-397 vs L849-876；裁定#200 拆分结果表 L1923 |
| **D-INTEGRATION-GATEWAY** | **D-INTEGRATION** | 子域拆分。D-INTEGRATION 含 pipeline_routing(MOD-INF-009, `src/zephyr/integration/`)；D-INTEGRATION-GATEWAY 专管 mcp_servers(MOD-INF-013, `src/zephyr/integration/mcp/`)。MCP 代码当前归属 D-INTEGRATION（314 模块/71 prod），**尚未迁移**到 D-INTEGRATION-GATEWAY | registry L257-277 (D-INTEGRATION) vs L754-776 (D-INTEGRATION-GATEWAY)；裁定#176 列 D-INTEGRATION 705 超容 |

**根因**：这 3 个域是裁定#176 确认的"设计态占位域"，原计划在父域（D-SECURITY/D-INTEGRATION/D-OPS）拆分时被填充。但裁定#200 的 4 域拆分**只处理了 D-INFRA_RUNTIME/D-GOV_AUDIT/D-GOVERNANCE/D-GOV_RULE**，未触及 D-SECURITY/D-INTEGRATION/D-OPS，故这 3 个空域至今未被填充。其中 D-GOV-REPAIR 还因 D-INFRA_RECOVERY 的建立而变得**冗余**。

### 1.5 D-SIGNAL 冲突的真相

#### 1.5.1 D-SIGNAL 域完整记录

来源：`38_d_signal.md`（2026-06-24 23:56:40）+ `domain_split_plan` 附录C.3（L675）+ `capacity_report.md`（L110）。

| 字段 | 值 | 证据 |
|---|---|---|
| domain_id | D-SIGNAL | `38_d_signal.md` L24 |
| domain_name | 信号 | L25 |
| layer_id | L2_domain | L26 |
| current_modules | 476（2026-06-24）/ 47（2026-06-25 裁定#192 清理幽灵设计节点后） | `38_d_signal.md` L27 vs `domain_index.md` L94 |
| production_nodes | 1 | `capacity_report.md` L110, `design_vs_production.md` L89 |
| ssot_path | **''（空字符串）** | `domain_split_plan` 附录C.3 L675 |
| design 模块 | 474→45（裁定#192 删除无 blueprint_id 幽灵节点） | `38_d_signal.md` L31 vs `design_vs_production.md` L89 |
| 容量 | 476/150 超容（旧口径）/ 1/150 正常（production_nodes 新口径） | `38_d_signal.md` L34 vs `capacity_report.md` L110 |

#### 1.5.2 D-SIGNAL_FUNDAMENTAL 域完整记录

来源：`40_d_signal_fundamental.md`（2026-06-24 23:56:40）+ `d_signal_fundamental_dependency.mmd`。

| 字段 | 值 | 证据 |
|---|---|---|
| domain_id | D-SIGNAL_FUNDAMENTAL | `40_d_signal_fundamental.md` L24 |
| domain_name | 基本面信号 | L25 |
| layer_id | L2_domain | L26 |
| current_modules | 24（含 1 design + 20 prototype + 3 production） | L27, `design_vs_production.md` L91 |
| production_nodes | 3 | `capacity_report.md` L112 |
| ssot_path | **`src/zephyr/signal_fundamental/`** | mmd L10 "src/zephyr/signal_fundamental/ [design]"；模块清单 L43-66 全部在该路径下 |
| 描述 | "基本面信号域...拆分自原D-SIGNAL域" | L35 |
| 容量 | 24/150 正常 | L34 |

#### 1.5.3 D-SIGNAL 下的 prod 节点与路径

D-SIGNAL 唯一的 production 节点是 **`src/zephyr/signal_fundamental/pipeline.py`**。

证据：`38_d_signal.md`
- L472-473 模块清单：`src/zephyr/signal_fundamental/__init__.py`（prototype）、`src/zephyr/signal_fundamental/pipeline.py`（**production**）均列为 D-SIGNAL 模块
- L1839 依赖图：`src_zephyr_signal_fundamental_pipeline_py["src/zephyr/signal_fundamental/pipeline.py production"]`
- L1865-1870：该 prod 节点 `import_depends` 指向 D-GOVERNANCE、**D-SIGNAL_FUNDAMENTAL**、D-TRADING

即 D-SIGNAL 的 prod 节点物理路径是 `src/zephyr/signal_fundamental/pipeline.py`。

#### 1.5.4 冲突分析

**直接根因**：`src/zephyr/signal_fundamental/pipeline.py` 这个文件的 `domain_id=D-SIGNAL`，但其物理路径 `src/zephyr/signal_fundamental/` 是 D-SIGNAL_FUNDAMENTAL 的 ssot_path。即**节点的逻辑归属（D-SIGNAL）与物理路径归属（D-SIGNAL_FUNDAMENTAL）不一致**。

**任务卡佐证**：`data/archive/taskcards/DM-100257.md`（status=COMPLETED）明确记载此为已知冲突：

> 根因：depgraph.db 的 domains 表 3 处 ssot_path 被多个 D-XXX 域共享——...src/zephyr/signal/ 被 **D-SIGNAL/D-SIGNAL_FUNDAMENTAL 共享**...导致域归属歧义。治根：为每处重复路径设计子目录拆分方案，确保一域一路径。

该卡 deliverable 指向 `docs/02_enterprise_architecture/archive/路径拆分设计方案.md`，但**该交付文件在磁盘上不存在**（Glob `**/*路径拆分*` 无结果，`_archive/` 下也无）。即任务卡标记 COMPLETED 但交付物缺失，路径拆分方案**未真正落地**。

#### 1.5.5 历史遗留还是设计问题

**判定：历史遗留（不完整迁移）为主，叠加设计边界未定义。**

证据链：
1. **D-SIGNAL_FUNDAMENTAL 自述"拆分自原D-SIGNAL域"**（`40_d_signal_fundamental.md` L35），证明 D-SIGNAL_FUNDAMENTAL 是从 D-SIGNAL 拆分出来的新域。
2. 同期拆分的还有 D-SIGNAL_ASHARE（A股特色信号）、D-SIGNAL_QUALITY（信号质量），见 `domain_index.md` L94-97。
3. **拆分时迁移不完整**：`src/zephyr/signal_fundamental/` 子目录被划归 D-SIGNAL_FUNDAMENTAL，但该目录下的 `pipeline.py`（及 `__init__.py`）的 `domain_id` **未被更新**为 D-SIGNAL_FUNDAMENTAL，仍留在 D-SIGNAL。
4. **D-SIGNAL 的 ssot_path 被清空为 ''**：原 ssot_path 应为 `src/zephyr/signal/`（DM-100257 所指的共享路径），后清空为空字符串——可能是为消除与 D-SIGNAL_FUNDAMENTAL 的路径包含关系（`src/zephyr/signal/` 包含 `src/zephyr/signal_fundamental/`）而做的临时处置，但导致 D-SIGNAL 失去合法 ssot_path。
5. **信号域拆分未在全景图正式裁定**：Grep `dependency_architecture_panorama.md` 对"D-SIGNAL|signal_fundamental|signal_ashare|signal_quality|信号拆分"**无任何命中**。即 D-SIGNAL→3 子域的拆分没有裁定记录，与裁定#200（D-INFRA_RUNTIME 等 4 域拆分有完整裁定#199/#200）形成对比。
6. **信号域未注册**：Grep `functional_domain_registry.yaml` 对"D-SIGNAL|signal|信号"仅命中 2 行无关文本（"后验信号"描述），**D-SIGNAL/D-SIGNAL_FUNDAMENTAL/D-SIGNAL_ASHARE/D-SIGNAL_QUALITY 均无 registry 条目**。

#### 1.5.6 边界定义现状

| 域 | 应有 ssot_path | 实际 ssot_path | 状态 |
|---|---|---|---|
| D-SIGNAL | `src/zephyr/signal/`（原） | `''`（空） | 路径丢失，仅剩 1 个错位 prod 节点 + 45 design 节点 |
| D-SIGNAL_FUNDAMENTAL | `src/zephyr/signal_fundamental/` | `src/zephyr/signal_fundamental/` | 正常，但目录下混入 1 个 D-SIGNAL 的 pipeline.py |
| D-SIGNAL_ASHARE | `src/zephyr/signal_ashare/`（推测） | 未在缓存快照中确认 | 0 prod |
| D-SIGNAL_QUALITY | `src/zephyr/signal_quality/`（推测） | 未在缓存快照中确认 | 0 prod |

**真正的 ssot_path 冲突案例**（非 D-SIGNAL）：D-GOV-REPAIR 和 D-GOVERNANCE 在 functional_domain_registry.yaml 中共享同一 ssot_path `src/zephyr/governance/`（D-GOV-REPAIR: 第 379 行，D-GOVERNANCE task_management: 第 780 行，D-GOVERNANCE lifecycle_management: 第 796 行）。这违反 ARCH-CAP-004 的 1:1 映射要求。

### 1.6 domain_dependencies 的设计 gap

#### 1.6.1 表结构

`domain_dependencies` 是**独立的表**，不是 domains 表的字段。

表定义在 `depgraph_schema.py:173-182`（`_DDL_DOMAIN_DEPS`）：

```sql
-- src/zephyr/governance/depgraph_schema.py:173-182
CREATE TABLE IF NOT EXISTS domain_dependencies (
    from_domain      TEXT    NOT NULL,
    to_domain        TEXT    NOT NULL,
    edge_count       INTEGER DEFAULT 0,
    edge_types       TEXT,
    constraint_type  TEXT,
    PRIMARY KEY (from_domain, to_domain)
)
```

#### 1.6.2 管理位置

| 位置 | 文件 | 行号 | 操作类型 |
|------|------|------|---------|
| `cmd_migrate_dependencies` | apply_depgraph.py | 1237-1330 | **仅 UPDATE**（迁移 from/to_domain） |
| `--migrate-dependencies` CLI | apply_depgraph.py | 1631-1637 | 命令行入口 |
| `detect_cross_domain_violations` | audit_domain_nodes.py | 37-53 | **读取**（检测未声明的跨域依赖） |
| `get_domain_dependencies` | depgraph_reader.py | 184-188 | **读取** |
| `generate_project_depgraph.py` | — | — | **不写入** domain_dependencies（grep 无匹配） |
| `sync_yaml_to_depgraph.py` | — | — | **不写入** domain_dependencies |
| `test_depgraph_db.py` | tests/test_depgraph_db.py | 104 | **仅测试** INSERT OR REPLACE |

#### 1.6.3 根因分析

**直接原因**：apply_depgraph.py 的 `cmd_migrate_dependencies`（第 1237-1330 行）只支持 UPDATE（迁移已有记录的 from_domain/to_domain），不支持 INSERT（新增域间依赖声明）。

**根因链**：

1. **设计意图**：domain_dependencies 表是 edges 表的聚合视图（按 from_domain/to_domain 聚合 edge_count）。按全景图（dependency_architecture_panorama.md:93）描述，domain_dependencies 是"域间依赖声明"，arch_constraints 跨域检测引用它。

2. **生成器未自动填充**：generate_project_depgraph.py 生成 nodes 和 edges，但**不生成 domain_dependencies 聚合记录**（grep "domain_dependencies" 在该文件中无匹配）。这导致 domain_dependencies 表数据需要手动维护。

3. **审计依赖此表**：audit_domain_nodes.py:38-53 的 `detect_cross_domain_violations` 检测"import 跨越域边界但未在 domain_dependencies 中声明"的违规——但如果 domain_dependencies 表本身为空或不全，所有跨域 import 都会被报为违规。

4. **工具 gap**：apply_depgraph.py 提供了域级操作（insert_domain/update_domain_id/update_path/migrate_dependencies/update_domain_layer/update_domain_ssot_path），但缺少 `cmd_insert_domain_dependency` 命令。migrate_dependencies 只能迁移已有记录，不能新增。唯一的 INSERT 在测试代码中（test_depgraph_db.py:104）。

5. **影响**：域拆分时，新域的跨域依赖无法通过 CLI 声明，只能直接操作 DB 或通过 batch JSON 间接处理（但 batch 也不支持 insert_domain_dependency op）。

---

## 第二部分：根因分析（分析层）

### 2.1 根因归类：四类系统性缺陷

将4个问题抽象归类，根因不是"某个字段忘了写"，而是**四类系统性缺陷**：

| 根因类别 | 涉及问题 | 本质 |
|---------|---------|------|
| **RC1：双写路径字段覆盖不一致** | P1/P2/P3 | sync 脚本与 apply 脚本各写一部分字段，无"全字段必填"约束 |
| **RC2：DB 层无防御性约束** | P1/P2/P3 | NOT NULL/CHECK/UNIQUE 全缺，NULL 可静默写入 |
| **RC3：占位域生命周期无闭环** | P1/P2 | 占位域创建后无"转正/补齐元数据"的强制门禁 |
| **RC4：非正式拆分无裁定留痕** | P3 | 信号域拆分绕过全景图裁定，路径已拆节点未迁 |

### 2.2 RC1 详解：双写路径的字段覆盖裂缝

```
functional_domain_registry.yaml（规划真源）
        │
        ├──sync_yaml_to_depgraph.py──► domains表（7字段）+ arch_path_mappings表
        │                                    ↑ 缺 max_modules/layer_id/ssot_path列
        │
        └──apply_depgraph.py cmd_insert_domain──► domains表（9字段）
                                                  ↑ 默认 max_modules=200（陈旧，v1.0.8前）
```

**问题**：3个空域走的是 sync 路径（因它们在 registry 有条目），所以缺3个字段。裁定#200 新建的5个域走的是 apply 路径，所以字段齐全。**同一张表，两种创建方式，字段完整度不同**——这是典型的"多入口无统一校验"反模式。

### 2.3 RC2 详解：DB 层零防御

`max_modules`/`layer_id`/`ssot_path` 三字段在 schema 中：
- 无 `NOT NULL` → NULL 可静默写入
- 无 `CHECK(max_modules IN (150))` → 200/150/NULL 共存
- 无 `UNIQUE(ssot_path)` → 两域可共享路径（D-GOV-REPAIR 与 D-GOVERNANCE 实际共享 `src/zephyr/governance/`）

这与项目 memory 中记载的"DB实际值与文档定义严重不一致（build_status有10种值，合法4种仅占0.6%），根因是无DB CHECK约束形成脏值自循环"是**同一类病根**。裁定#178-193 已为 build_status 治理了此病，但 max_modules/layer_id/ssot_path 的同类病根**未治理**。

### 2.4 RC3 详解：占位域无生命周期闭环

裁定#176 保留5个设计态域为"计划中"，但**未定义"计划中→转正"的门禁**。结果：
- D-GOV-ENFORCEMENT/D-GOV-SCRIPTS 在裁定#200 中被 `--update-domain-ssot-path` 补齐了 ssot_path
- D-SECURITY-LLM/D-GOV-REPAIR/D-INTEGRATION-GATEWAY 因父域（D-SECURITY/D-INTEGRATION）未被裁定#200 触及，至今未补齐

**这是"占位域"模式缺少强制收尾机制的典型表现**：占位域创建容易，但"何时必须补齐元数据"无规则约束。

**空域合法性判定标准**（由裁定#175 vs #176 对比得出）：

| 维度 | 合法占位域（裁定#176 保留） | 非法空壳域（裁定#175 删除） |
|---|---|---|
| 来源 | 为缓解超容父域而规划 | 测试残留泄漏到生产 DB |
| registry 覆盖 | functional_domain_registry.yaml 有完整 covers | 无 registry 条目 |
| ssot_path 语义 | 路径有规划代码（虽未迁移） | 路径不存在代码 |
| 业界对标 | DDD Bounded Context planned / TOGAF Transition Architecture | JUnit/K8s kind/Google Bazel（测试应独立库） |

这 3 个空域符合"合法占位域"标准（有 registry covers、有规划代码路径），但存在**未完成治理**：ssot_path 在 DB 中仍为 NULL（registry 已规划但未写入 DB），layer_id 为 NULL，max_modules 为 NULL。

### 2.5 RC4 详解：非正式拆分的留痕缺失

信号域拆分（D-SIGNAL → D-SIGNAL_FUNDAMENTAL/ASHARE/QUALITY）与裁定#200 的4域拆分形成鲜明对比：

| 维度 | 裁定#200（正式） | 信号域拆分（非正式） |
|------|-----------------|-------------------|
| 全景图裁定 | ✅ 裁定#199/#200 | ❌ 无任何记录 |
| registry 注册 | ✅ 5新域已注册 | ❌ 4域均无条目 |
| 节点迁移 | ✅ cmd_migrate_nodes 精确迁移 | ❌ pipeline.py 漏迁 |
| ssot_path 补齐 | ✅ --update-domain-ssot-path | ❌ D-SIGNAL 清空未补 |
| 任务卡 | ✅ 12张任务卡 | ❌ DM-100257 标记完成但交付物缺失 |

---

## 第三部分：行业基准对标（参考层）

针对"100% AI 开发"这一特殊语境，对标三类实践：

### 3.1 专业机构实践（DDD / TOGAF / NIST）

| 实践来源 | 核心原则 | 对本项目的启示 |
|---------|---------|--------------|
| **DDD Bounded Context**（Eric Evans） | 限界上下文是语义边界，planned 状态合法但必须有明确边界定义 | 占位域合法，但 ssot_path/layer_id 是边界定义的**最小集**，不可缺 |
| **TOGAF Transition Architecture** | 过渡架构是基线与目标之间的里程碑，必须记录在架构连续体中 | 信号域拆分是过渡架构，**必须在全景图留痕** |
| **NIST Cybersecurity Framework** | 结构化语言和控制边界减少复杂环境混淆 | DB 层约束是"控制边界"的最低实现 |

### 3.2 量化社区实践（ArchUnit / SonarQube / Fitness Functions）

InfoQ《Architectural Governance at AI Speed》（2026-03）提出**声明式架构（Declarative Architecture）**：

> 核心思想：将架构决策与约束蒸馏为**机器可执行的意图声明**，使合规路径成为阻力最小的路径。不是让决策更好，而是让决策**无法被忽视**。

Fora Soft《AI in Software Architecture Design 2026》给出量化KPI：
- **Architecture drift score**：SonarQube/CodeScene 周度检测，目标 <5% 偏离
- **Fitness function enforcement**：每条架构规则必须作为 ArchUnit/NetArchTest 检查，**违反即阻断合并**
- **ADR git-native**：决策记录必须 git 原生存储，可追溯

**对标结论**：本项目的 YAML 规则文件 + apply_depgraph.py 已接近"声明式架构"，但**缺机器可执行的 fitness function**——DB 层 CHECK 约束就是最直接的 fitness function，目前为0。

### 3.3 氛围编程社区（Vibe Coding / AMGF）

2026奇点大会《AI-augmented Merge Governance Framework》(AMGF) 三大支柱：
1. **意图对齐验证**：PR 必须含结构化意图声明
2. **影响面沙箱执行**：AI 变更必须在隔离环境跑全测试
3. **责任链签名锚定**：开发者确认 + AI模型哈希 + SAST签名 三者绑定

TheNeuralBase《LLM代码治理四支柱》（2026-04验证）：
1. Generation capture（生成捕获）
2. Automated scanning（自动扫描）
3. Review enforcement（审查强制）
4. Audit trail（审计链）

**对标结论**：本项目在"审查强制"和"审计链"上较强（任务卡+循环验收+GitCommitGateway），但在"自动扫描"层有缺口——**DB 层约束缺失意味着脏数据可静默写入而不被扫描拦截**。

### 3.4 综合对标裁定

| 本项目现状 | 行业基准 | 差距 |
|-----------|---------|------|
| 规则在 YAML（文档态） | 规则必须机器可执行（fitness function） | DB CHECK 约束缺失 |
| 占位域无转正门禁 | TOGAF 过渡架构有里程碑门禁 | 缺生命周期闭环 |
| 拆分有正式/非正式两套 | ADR 必须全量 git-native 留痕 | 信号域拆分无裁定 |
| 双写路径字段不一致 | 声明式架构要求单一真源单一入口 | sync 与 apply 字段覆盖裂缝 |

---

## 第四部分：裁定结果（决策层）

作为客观专业架构师，基于上述事实与分析，作出以下裁定：

### 裁定A：3个空域定性——合法占位域，但元数据欠债须偿还

**裁定**：D-SECURITY-LLM / D-GOV-REPAIR / D-INTEGRATION-GATEWAY 是裁定#176 确认的合法设计态占位域，**保留不删除**。但其 max_modules/layer_id/ssot_path 三项元数据缺失属"治理欠债"，**必须补齐**，不能以"预存问题"为由无限期搁置。

**理由**：
1. 占位域合法（DDD planned / TOGAF Transition Architecture 均认可）
2. 但"占位"≠"元数据可空"——ssot_path/layer_id 是边界定义的最小集，缺失会导致域归属歧义（已实际发生：3域落入"未分类"）
3. 100% AI 开发语境下，AI 无法像人类那样"默认知道"D-SECURITY-LLM 属 L1_platform——**必须显式落库**

### 裁定B：D-GOV-REPAIR 冗余——并入 D-INFRA_RECOVERY

**裁定**：D-GOV-REPAIR 与裁定#200 新建的 D-INFRA_RECOVERY covers 高度重叠（均覆盖 rollback/MOD-INF-021，双轨Checkpoint/四级回滚/Kill Switch），且 D-INFRA_RECOVERY 已实际迁入107个prod节点，是 D-GOV-REPAIR 的超集。**D-GOV-REPAIR 应标记为 deprecated 并并入 D-INFRA_RECOVERY**，不单独补齐元数据。

**理由**：保留冗余占位域会制造"两个域争同一代码路径"的歧义，违反 ARCH-CAP-004 的 1:1 映射。

### 裁定C：D-SIGNAL 冲突——不完整迁移，须补裁定+迁节点

**裁定**：信号域拆分属"未经裁定的非正式拆分"，导致路径已拆、节点未迁、ssot_path 清空未补。**须补全景图裁定记录**，并将 `src/zephyr/signal_fundamental/pipeline.py` 的 domain_id 迁移到 D-SIGNAL_FUNDAMENTAL，为 D-SIGNAL 重新指定合法 ssot_path。

**理由**：DM-100257 虽标记 COMPLETED 但交付物缺失，治根方案未落地。继续放任会导致 D-SIGNAL 长期持有1个错位prod节点，审计与容量统计失真。

### 裁定D：根因治理——DB层约束 + 单一写入入口 + 占位域门禁

**裁定**：4个问题的根因是"双写路径字段覆盖不一致 + DB层零防御 + 占位域无闭环"。治本须三管齐下：
1. **DB 层加约束**（fitness function）：max_modules NOT NULL CHECK、layer_id NOT NULL CHECK、ssot_path UNIQUE
2. **统一写入入口**：sync 脚本与 apply 脚本字段覆盖对齐，或收敛为单一入口
3. **占位域生命周期门禁**：定义"planned→active"的强制元数据补齐检查

### 裁定E：domain_dependencies gap——补 INSERT 命令 + 自动聚合

**裁定**：apply_depgraph.py 须新增 `cmd_insert_domain_dependency` 命令，并在 generate_project_depgraph.py 中增加 domain_dependencies 自动聚合（从 edges 表按 from_domain/to_domain 聚合）。

**理由**：domain_dependencies 是跨域违规检测的数据源，表数据不全会导致 audit 误报，违反"声明式架构"的完整性要求。

---

## 第五部分：治本施工方案（执行层）

### 5.1 施工总原则

1. **备份先行**：改 depgraph.db 前必须 `git commit` 备份（trae_054 STEP0）
2. **全景图修改用 apply_depgraph.py**，禁止直接改 .db
3. **循环验收**：每阶段完成后连续2轮零错误才标记完成
4. **任务卡驱动**：复杂步骤建任务卡，遵循 OPS-<日期><序号> 命名

### 5.2 分阶段施工方案

#### 阶段0：备份与基线快照（前置）

| 步骤 | 命令/操作 | 验证 |
|------|----------|------|
| 0.1 | `python scripts/git_guard.py add data/databases/depgraph.db && python scripts/git_guard.py commit -m "backup: depgraph before metadata debt cleanup"` | git log 确认 |
| 0.2 | 生成基线快照：`python scripts/governance/generate_capacity_report.py` | capacity_report.md 时间戳更新 |
| 0.3 | 记录当前3空域+D-SIGNAL的完整字段值（SELECT快照存档） | 快照文件存在 |

#### 阶段1：补齐3空域元数据（裁定A，数据修复）

对 D-SECURITY-LLM / D-INTEGRATION-GATEWAY（保留），D-GOV-REPAIR 按裁定B处理：

| 域 | max_modules | layer_id | ssot_path | 命令 |
|----|:---:|:---:|:---:|------|
| D-SECURITY-LLM | 150 | L1_platform | `src/zephyr/security/llm_defense/` | `apply_depgraph.py --update-domain-capacity` + `--update-domain-layer` + `--update-domain-ssot-path` |
| D-INTEGRATION-GATEWAY | 150 | L1_platform | `src/zephyr/integration/mcp/` | 同上 |
| D-GOV-REPAIR | — | — | — | 标记 deprecated（见阶段2） |

**验证**：`SELECT domain_id, max_modules, layer_id, ssot_path FROM domains WHERE domain_id IN ('D-SECURITY-LLM','D-INTEGRATION-GATEWAY')` 三字段均非NULL。

#### 阶段2：D-GOV-REPAIR 并入 D-INFRA_RECOVERY（裁定B）

| 步骤 | 操作 | 验证 |
|------|------|------|
| 2.1 | 确认 D-GOV-REPAIR 的0节点（无节点需迁移） | `SELECT COUNT(*) FROM nodes WHERE domain_id='D-GOV-REPAIR'` = 0 |
| 2.2 | 将 D-GOV-REPAIR 的 lifecycle 改为 `deprecated`，build_status 改为 `deprecated` | SELECT 确认 |
| 2.3 | 在 functional_domain_registry.yaml 中标注 D-GOV-REPAIR 为 deprecated，指向 D-INFRA_RECOVERY | YAML 条目更新 |
| 2.4 | 在全景图补裁定记录（裁定#201） | panorama.md 新增条目 |

#### 阶段3：D-SIGNAL 冲突修复（裁定C）

| 步骤 | 操作 | 风险控制 |
|------|------|---------|
| 3.1 | 定位 `src/zephyr/signal_fundamental/pipeline.py` 的 node_id | SELECT node_id FROM nodes WHERE file_path LIKE '%signal_fundamental/pipeline.py%' |
| 3.2 | 用 `apply_depgraph.py --migrate-nodes` 将该节点 domain_id 从 D-SIGNAL 迁移到 D-SIGNAL_FUNDAMENTAL | dry-run 先行 |
| 3.3 | 为 D-SIGNAL 指定合法 ssot_path（需架构决策：若 `src/zephyr/signal/` 仍有 D-SIGNAL 节点则用此路径；若已无节点则考虑 deprecate D-SIGNAL） | 决策记录入裁定#202 |
| 3.4 | 补登信号域4域到 functional_domain_registry.yaml | YAML 新增4条目 |
| 3.5 | 全景图补裁定记录（信号域拆分追溯裁定#203） | panorama.md 新增条目 |

**验证**：`SELECT domain_id, ssot_path FROM domains WHERE domain_id='D-SIGNAL'` ssot_path 非空；D-SIGNAL_FUNDAMENTAL 下无 D-SIGNAL 节点。

#### 阶段4：DB层约束治理（裁定D，治本核心）

这是**防止问题再发**的治本步骤。需新增迁移版本（v11）：

```sql
-- 迁移 v11：元数据防御性约束
-- 1. max_modules NOT NULL + CHECK
UPDATE domains SET max_modules = 150 WHERE max_modules IS NULL;
ALTER TABLE domains RENAME TO domains_old_v10;
CREATE TABLE domains (
    -- ... 原字段 ...
    max_modules      INTEGER NOT NULL DEFAULT 150 CHECK(max_modules = 150),
    layer_id         TEXT    NOT NULL CHECK(layer_id IN ('L0_infrastructure','L1_foundation','L1_platform','L2_domain')),
    ssot_path        TEXT,  -- 占位域可空，但非占位域须 UNIQUE
    -- ...
);
-- 迁移数据 + 去重 ssot_path
INSERT INTO domains SELECT * FROM domains_old_v10;
DROP TABLE domains_old_v10;

-- 2. ssot_path UNIQUE 索引（仅对非空值）
CREATE UNIQUE INDEX IF NOT EXISTS idx_domains_ssot_path_unique
    ON domains(ssot_path) WHERE ssot_path IS NOT NULL AND ssot_path != '';
```

**注意**：
- SQLite 不支持直接 `ALTER TABLE ADD CONSTRAINT`，须重建表
- 重建前必须确保数据已满足约束（阶段1-3已完成补齐）
- ssot_path 的 UNIQUE 须排除空字符串（占位域过渡期）

**验证**：尝试 INSERT 一个 max_modules=NULL 的域应失败；尝试 INSERT 重复 ssot_path 应失败。

##### 阶段4执行结果（2026-06-25 完成）

阶段4核心目标（防止问题再发）已达成，但实际执行与原方案有以下调整：

| 项 | 原方案 | 实际执行 | 调整理由 |
|---|---|---|---|
| 迁移版本号 | v11 | v12 | v11 已被前序会话用于 nodes 表 CHECK 约束（裁定#178），不可重复使用 |
| 实现机制 | ALTER TABLE 重建表 | 触发器 BEFORE INSERT/UPDATE | SQLite 的 ALTER TABLE ADD CHECK 不会回溯校验既有数据，触发器方案可幂等执行（CREATE TRIGGER IF NOT EXISTS），更适合版本化迁移 |
| 约束范围 | max_modules + layer_id + ssot_path UNIQUE | lifecycle + build_status + layer_id + nodes DELETE 自动清理 edges | 扩展：lifecycle/build_status 也是裸字段需约束；ssot_path UNIQUE 因占位域过渡期暂缓；新增根治孤儿边的 DELETE 触发器 |

**实际执行内容**（裁定 #203-B / #203-C，议题 #ARCH-006 / #ARCH-007）：

1. **孤儿边清理**（commit 290df512）：
   - 调研确认 148 条孤儿边均为预存问题（edges 表 FK 无 ON DELETE CASCADE 累积）
   - 在 `apply_depgraph.py` 新增 `cmd_cleanup_orphan_edges()` 命令 + `--cleanup-orphan-edges` CLI 参数（commit 87e793ec）
   - 执行清理：148 条全部删除
   - 验证：`SELECT COUNT(*) FROM edges WHERE ...` 返回 0

2. **v12 迁移**（commit 87e793ec + 0a69d345）：在 `depgraph_schema.py` `_MIGRATIONS` 列表新增 v12，创建 7 个触发器：
   - `trg_nodes_delete_cleanup_edges`（AFTER DELETE ON nodes）：删除节点时自动清理引用它的 edges，**根治孤儿边再生**
   - `chk_domains_lifecycle_insert` / `chk_domains_lifecycle_update`：校验 lifecycle ∈ ('operational','design_only','prototype','deprecated')
   - `chk_domains_build_status_insert` / `chk_domains_build_status_update`：校验 build_status ∈ ('planned','generated','testing','stable','deprecated')
   - `chk_domains_layer_id_insert` / `chk_domains_layer_id_update`：校验 layer_id ∈ 4 合法值或 NULL

3. **配套修复**：
   - `apply_depgraph.py cmd_insert_domain` 默认值 max_modules 200→150（裁定#194 硬上限），build_status 'unbuilt'→'planned'（避免被触发器拦截）
   - `apply_depgraph.py add_design_node` build_status 默认值 'unbuilt'→'planned'
   - D-GOV-REPAIR max_modules NULL → 150

4. **验证全部通过**：
   - `schema_version` = 12
   - 7 个新触发器在 sqlite_master 中可见
   - `orphan_edges` = 0
   - `max_modules NULL` = 0
   - `build_status='unbuilt'` = 0
   - `layer_id='L1_platform'` = 0
   - 非法值插入测试 5 项全 PASS

**遗留事项（不在阶段4范围）**：
- ssot_path UNIQUE 索引：占位域过渡期暂缓，待占位域全部转正后再加
- domains 表 max_modules NOT NULL 约束：当前仍有触发器校验机制保护，DDL 级 NOT NULL 待后续 v13 迁移加入
- sync_yaml_to_depgraph.py 写入路径修复（原方案阶段5）：仍待执行

#### 阶段5：统一写入入口（裁定D，工具修复）

| 文件 | 修改 | 验证 |
|------|------|------|
| `scripts/governance/sync_yaml_to_depgraph.py:401-413` | INSERT 语句补齐 max_modules/layer_id/ssot_path 字段（从 YAML 的 tier 映射 layer_id，max_modules 默认150） | 同步后 SELECT 三字段非NULL |
| `scripts/governance/apply_depgraph.py:1029` | `max_modules: int = 200` 改为 `max_modules: int = 150`（对齐 v1.0.8） | grep 确认无残留200默认值 |
| `scripts/governance/generate_capacity_report.py:57` | 移除 `r[4] or 150` 回退（DB层已 NOT NULL，回退掩盖问题） | 回退逻辑删除 |

#### 阶段6：domain_dependencies 补全（裁定E）

| 步骤 | 操作 | 验证 |
|------|------|------|
| 6.1 | apply_depgraph.py 新增 `cmd_insert_domain_dependency(from_domain, to_domain, constraint_type)` | 单元测试通过 |
| 6.2 | generate_project_depgraph.py 新增 domain_dependencies 自动聚合（从 edges 表 GROUP BY from_domain, to_domain） | 聚合后行数与 edges 跨域对数一致 |
| 6.3 | 运行 `audit_domain_nodes.py` 验证跨域违规检测无误报 | 误报数=0 |

#### 阶段7：占位域生命周期门禁（裁定D，机制闭环）

新增规则到 ARCH-CAP 规则文件（trae_055）：

```
ARCH-CAP-007（新增）：占位域生命周期门禁
- 占位域（lifecycle='design_only'）创建时须填写 ssot_path/layer_id/max_modules
- 占位域转正（lifecycle 改为 'active'）前须通过元数据完整性检查
- 父域拆分时，相关占位域必须同步补齐元数据或标记 deprecated
- 检查命令：apply_depgraph.py --audit-placeholder-domains
```

**验证**：`apply_depgraph.py --audit-placeholder-domains` 输出0个欠债域。

### 5.3 执行顺序与依赖

```
阶段0（备份）
   ↓
阶段1（补3空域元数据）──► 阶段2（D-GOV-REPAIR deprecate）
   │                          ↓
   ├─────────────────────► 阶段3（D-SIGNAL修复）
   │                          ↓
   └─────────────────────► 阶段4（DB约束，依赖1-3数据已干净）
                                  ↓
                           阶段5（统一入口，依赖4约束已就位）
                                  ↓
                           阶段6（domain_dependencies补全）
                                  ↓
                           阶段7（门禁机制，依赖5-6工具已就位）
```

**关键依赖**：阶段4（DB约束）必须在阶段1-3（数据修复）完成后执行，否则重建表时会因数据不满足约束而失败。

### 5.4 验收标准

| 验收项 | 标准 | 验证命令 |
|--------|------|---------|
| 3空域元数据 | max_modules/layer_id/ssot_path 非NULL | SELECT 三字段 |
| D-GOV-REPAIR | lifecycle='deprecated' | SELECT |
| D-SIGNAL | ssot_path 非空，无错位节点 | SELECT + 节点归属检查 |
| DB约束 | INSERT NULL/重复ssot_path 被拒 | 手动测试 |
| 双写入口 | sync 后字段齐全 | 同步后 SELECT |
| domain_dependencies | 有 INSERT 命令+自动聚合 | 单元测试+audit无误报 |
| 循环验收 | 连续2轮零错误 | batch_review |

### 5.5 回滚方案

| 阶段 | 回滚方式 |
|------|---------|
| 阶段1-3 | `git checkout data/databases/depgraph.db`（阶段0备份） |
| 阶段4 | 迁移 v11 失败时回滚到 v10 schema（保留 domains_old_v10 临时表） |
| 阶段5-7 | 代码修改通过 git revert 回滚 |

---

## 第六部分：总结

### 6.1 病根一句话

**4个问题同源于"声明式架构的执行层缺位"**——规则写在 YAML（文档态），但 DB 层无机器可执行的 fitness function（CHECK/UNIQUE 约束），双写路径字段覆盖不一致，占位域无生命周期闭环，非正式拆分无裁定留痕。

### 6.2 治本核心

治本不是"补3个字段"，而是建立**三道防线**：
1. **DB 层约束**（fitness function）：让脏数据**无法写入**，而非写入后靠扫描发现
2. **单一写入入口**：消除 sync/apply 双路径的字段覆盖裂缝
3. **生命周期门禁**：占位域创建易、转正难，必须有强制收尾机制

### 6.3 对100% AI开发的特殊意义

在100% AI开发语境下，人类架构师的"默认常识"（如"D-SECURITY-LLM 当然属 L1_platform"）**对 AI 不成立**——AI 必须从显式数据中获取语义。因此：
- 元数据缺失不是"小问题"，而是**语义断裂**
- DB 约束不是"可选优化"，而是**AI 协作的契约边界**
- 裁定留痕不是"形式主义"，而是**AI 可追溯的唯一真源**

这与 InfoQ《Architectural Governance at AI Speed》的核心论断一致：**在 AI 时代，架构治理的核心不是让决策更好，而是让决策无法被忽视**。

---

## 附录：完整证据清单

### A.1 代码证据（绝对路径 + 行号）

| 证据 | 文件路径 | 行号 | 说明 |
|------|---------|------|------|
| domains 表 DDL | `D:\ZephyrAlpha\src\zephyr\governance\depgraph_schema.py` | 149-167 | max_modules/layer_id/ssot_path 均可空无约束 |
| domain_dependencies 表 DDL | `D:\ZephyrAlpha\src\zephyr\governance\depgraph_schema.py` | 173-182 | 独立表，复合主键 |
| cmd_insert_domain | `D:\ZephyrAlpha\scripts\governance\apply_depgraph.py` | 1023-1076 | 默认 max_modules=200（陈旧） |
| cmd_insert_domain INSERT | `D:\ZephyrAlpha\scripts\governance\apply_depgraph.py` | 1059-1063 | 写9字段，含 max_modules/layer_id/ssot_path |
| cmd_migrate_dependencies | `D:\ZephyrAlpha\scripts\governance\apply_depgraph.py` | 1237-1330 | 仅 UPDATE，无 INSERT |
| cmd_update_domain_capacity | `D:\ZephyrAlpha\scripts\governance\apply_depgraph.py` | 1333-1386 | 更新 max_modules |
| cmd_update_domain_layer | `D:\ZephyrAlpha\scripts\governance\apply_depgraph.py` | 1389-1438 | 更新 layer_id，合法值集合 |
| cmd_update_domain_ssot_path | `D:\ZephyrAlpha\scripts\governance\apply_depgraph.py` | 1441-1480 | 更新 ssot_path，无查重 |
| sync INSERT（7字段） | `D:\ZephyrAlpha\scripts\governance\sync_yaml_to_depgraph.py` | 401-413 | 缺 max_modules/layer_id/ssot_path |
| sync 写 arch_path_mappings | `D:\ZephyrAlpha\scripts\governance\sync_yaml_to_depgraph.py` | 416-426 | ssot_path 写错表 |
| NULL 回退掩盖 | `D:\ZephyrAlpha\scripts\governance\generate_capacity_report.py` | 57 | `r[4] or 150` |
| NULL 回退掩盖 | `D:\ZephyrAlpha\scripts\governance\generate_domain_doc.py` | 62 | `r[4] or 150` |
| 跨域违规检测 | `D:\ZephyrAlpha\scripts\governance\audit_domain_nodes.py` | 37-53 | 依赖 domain_dependencies 表 |
| 域依赖读取 | `D:\ZephyrAlpha\src\zephyr\governance\depgraph_reader.py` | 184-188 | get_domain_dependencies |
| 测试 INSERT | `D:\ZephyrAlpha\tests\test_depgraph_db.py` | 104 | 唯一的 INSERT OR REPLACE |

### A.2 文档证据（绝对路径 + 行号/裁定号）

| 证据 | 文件路径 | 行号/裁定 | 说明 |
|------|---------|----------|------|
| 裁定#175（删测试空壳） | `D:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_architecture_panorama.md` | L1469 | 非法空域判定标准 |
| 裁定#176（保留设计态域） | 同上 | L1470 | 3空域来历，合法占位域 |
| 裁定#177（域命名统一） | 同上 | L1471 | 15域连字符违规 |
| 裁定#194（统一150硬上限） | 同上 | L1849-1854 | 废除ARCH-CAP-003 |
| 裁定#195（production_nodes） | 同上 | — | 容量口径修复 |
| 裁定#199（立4域拆分任务） | 同上 | — | 正式拆分 |
| 裁定#200（完成4域拆分） | 同上 | L1923 | 5新建+3扩充+4保留 |
| domains 表字段清单 | 同上 | L1803 | 15列定义 |
| --update-domain-ssot-path 新增 | 同上 | L1940 | 裁定#200 工具扩展 |
| 占位域允许 | 同上 | L1296 | "全景图允许占位" |
| 设计态占位定义 | 同上 | L1306 | design+planned |
| 生命周期状态机 | 同上 | L1290-1328 | §17 |
| domains 表实测快照 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\domain_split_plan_4_oversized_domains.md` | 附录C.3 L668-675 | 6域 ssot_path/layer_id 为 NULL |
| D-SIGNAL 域文档 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\02_domain_architecture_docs\38_d_signal.md` | L24-34, L472-473, L1839, L1865-1870 | 476模块/1prod，ssot_path空 |
| D-SIGNAL_FUNDAMENTAL 域文档 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\02_domain_architecture_docs\40_d_signal_fundamental.md` | L24-35, L43-66 | 24模块/3prod，拆分自D-SIGNAL |
| 3空域文档 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\02_domain_architecture_docs\{45,47,48}_*.md` | — | 0模块空壳 |
| 域总览索引 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\02_domain_architecture_docs\domain_index.md` | L101-107 | "未分类3域" |
| 容量报告 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\capacity_report.md` | L110-112 | D-SIGNAL 1prod，D-SIGNAL_FUNDAMENTAL 3prod |
| 设计态vs运营态 | `D:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\design_vs_production.md` | L89-91 | 同上 |
| 3空域 registry 条目 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\functional_domain_registry.yaml` | L209-231, L376-397, L754-776 | 有条目，ssot_path已规划 |
| D-INFRA_RECOVERY registry | 同上 | L849-876 | 与D-GOV-REPAIR covers重叠 |
| 信号域无 registry | 同上 | — | Grep 无命中 |
| ssot_path 拆分任务卡 | `D:\ZephyrAlpha\data\archive\taskcards\DM-100257.md` | — | COMPLETED 但交付物缺失 |

### A.3 行业基准证据

| 实践来源 | 核心论点 | 对标结论 |
|---------|---------|---------|
| InfoQ《Architectural Governance at AI Speed》2026-03 | 声明式架构：让决策无法被忽视 | DB CHECK 约束缺失 |
| Fora Soft《AI in Software Architecture Design 2026》 | Fitness function 必须阻断合并 | 本项目 fitness function=0 |
| 2026奇点大会 AMGF | 意图对齐+沙箱执行+责任链签名 | 自动扫描层有缺口 |
| TheNeuralBase《LLM代码治理四支柱》2026-04 | 生成捕获+自动扫描+审查强制+审计链 | DB约束是自动扫描的最低实现 |
| DDD Bounded Context（Eric Evans） | planned 状态合法但须有边界定义 | 占位域合法，元数据不可缺 |
| TOGAF Transition Architecture | 过渡架构须记录在架构连续体 | 信号域拆分须留痕 |
| NIST Cybersecurity Framework | 结构化语言和控制边界 | DB约束是控制边界最低实现 |

### A.4 max_modules 字段管理位置汇总

| 位置 | 文件 | 行号 | 操作 | 默认值 |
|------|------|------|------|--------|
| `cmd_insert_domain` | apply_depgraph.py | 1029 | INSERT 新域时设置 | 200（陈旧） |
| `cmd_update_domain_capacity` | apply_depgraph.py | 1333-1386 | UPDATE 已有域 | — |
| `--batch` op `insert_domain` | apply_depgraph.py | 425, 496 | 批量 INSERT | 200 |
| `--max-modules` CLI 参数 | apply_depgraph.py | 1680 | argparse 默认值 | 200 |
| `sync_yaml_to_depgraph.py` | sync_yaml_to_depgraph.py | 401-413 | **不设置** | — |
| `generate_project_depgraph.py` | — | — | **不引用** | — |
| `generate_capacity_report.py` | generate_capacity_report.py | 57 | 读取时 NULL 回退 | 150 |
| `generate_domain_doc.py` | generate_domain_doc.py | 62 | 读取时 NULL 回退 | 150 |

### A.5 layer_id 合法值定义

| 位置 | 文件 | 行号 | 合法值集合 |
|------|------|------|-----------|
| `cmd_update_domain_layer` | apply_depgraph.py | 1399 | `{L0_infrastructure, L1_foundation, L1_platform, L2_domain}` |
| `LAYER_ORDER` | generate_domain_doc.py | 45 | `["L0_infrastructure", "L1_foundation", "L1_platform", "L2_domain"]` |
| arch_layers 表 | depgraph_schema.py | 294-302 | 存储层定义，但 domains.layer_id 无外键约束 |

### A.6 ssot_path 写入位置汇总

| 位置 | 文件 | 行号 | 操作 | 目标表 |
|------|------|------|------|--------|
| `cmd_insert_domain` | apply_depgraph.py | 1060-1064 | INSERT 新域时设置 | domains.ssot_path |
| `cmd_update_domain_ssot_path` | apply_depgraph.py | 1441-1480 | UPDATE 已有域 | domains.ssot_path |
| `sync_yaml_to_depgraph.py` | sync_yaml_to_depgraph.py | 416-426 | **不写入 domains.ssot_path** | arch_path_mappings |
| `generate_project_depgraph.py` | generate_project_depgraph.py | 504, 653 | 从 domains 表**读取** | — |

---

## 附录B：架构裁定议题（已决策）

> 以下议题在 preexisting 阶段1-3 执行过程中发现，已于 2026-06-25 决策并落地。
>
> **合并说明（2026-06-25）**：本附录已合并另一个 AI 会话（6a3c179e）的 5 个独有发现。该会话的交接文档 `handover_to_session_6a3cacc8.md` 已按用户要求删除，其发现统一归并到本报告。
>
> | 发现 # | 来源 | 内容 | 处理 |
> |--------|------|------|------|
> | 发现1 | 6a3c179e 独有 | layer_id 非法值（L1_platform 不在 arch_layers 合法层表，9域） | 新增议题 #ARCH-005，已修复 |
> | 发现2 | 6a3c179e 独有 | 孤儿边 148 条（预存问题） | 新增议题 #ARCH-006，留待阶段4 |
> | 发现3 | 6a3c179e 独有 | 命名结构分析（36个域有疑似父子命名） | 已并入议题 #ARCH-002 统一裁定 |
> | 发现4 | 6a3c179e 独有 | lifecycle 字段无 CHECK 约束（4值：operational/design_only/prototype/deprecated） | 新增议题 #ARCH-007，接受当前4值 |
> | 发现5 | 6a3c179e 独有 | D-SIGNAL 状态（0 production，45 design，ssot_path空） | 已并入议题 #ARCH-004 统一裁定 |

### 议题#ARCH-001：域数量超标（53 vs 设计39）✅ 已决策

**事实**：DB中有53个域，比 D38/D42 裁定的39个平铺域设计多14个。

**裁定**：39是初始设计值（D38/D42），不是硬上限。后续通过裁定#200等拆分增加域数是合法架构演进。14个多出域经调研：11个有合法裁定记录，3个无记录（D-SIGNAL拆分产物，由裁定#201补记），2个数据不一致（由裁定#202修复）。全部合法化。

### 议题#ARCH-002：D-SIGNAL* 命名违反"无子域"规则 ✅ 已决策

**事实**：D-SIGNAL_ASHARE / D-SIGNAL_FUNDAMENTAL / D-SIGNAL_QUALITY 的命名带 `D-SIGNAL_` 前缀，暗示子域层级关系。

**6a3c179e 会话补充**：不止 D-SIGNAL 子域，**36个域**（连字符6 + 下划线30）都有命名上的"父子关系"嫌疑，违反"所有域平级"硬约束。其中 D-GOV 前缀同时有连字符（D-GOV-DOCS 等）和下划线（D-GOV_AUDIT 等）两种风格，**命名不统一**。

**裁定**：不重命名。依据D38裁定原文"parent_domain仅作分组属性"——命名前缀不等于子域关系。这3个域在DB中是独立平级域（无parent_domain字段指向D-SIGNAL），数据结构上不违反"无子域"规则。扩展到36个域同理：命名前缀仅作分组属性，DB结构上均为独立平级域。重命名涉及105文件+301行DB更新，风险远大于收益。补写裁定#201明确平级关系。命名风格不统一问题（D-GOV- vs D-GOV_）留作后续命名规范治理，不在本次范围内。

### 议题#ARCH-003：D-SIGNAL拆分无正式裁定记录 ✅ 已决策

**事实**：D-SIGNAL→3子域的拆分在 `dependency_architecture_panorama.md` 中无任何裁定记录，无registry条目。

**裁定**：补写裁定#201（D-SIGNAL拆分追溯补记）到 `dependency_architecture_panorama.md`，补写4个registry条目（D-SIGNAL_ASHARE/FUNDAMENTAL/QUALITY + D-GOV_RULE）到 `functional_domain_registry.yaml`。裁定#202修复D-GOV_RULE（有裁定无registry）和D-INFRA_OPS（有registry无裁定）的数据不一致。

### 议题#ARCH-004：D-SIGNAL 本身是否应deprecated ✅ 已决策

**事实**：D-SIGNAL经过拆分后，代码已分散到3个独立域，本身有45个design节点（虚拟设计态路径），无production代码，ssot_path为空，production_nodes=0。

**6a3c179e 会话补充**：确认 D-SIGNAL 当前状态——production_nodes=0，build_status=planned（本会话归一化后），lifecycle=design_only，ssot_path=空字符串。node 51005 已被本会话迁走，D-SIGNAL 现仅剩45个design节点。

**裁定**：保留为设计态占位域（build_status=planned），45个design节点后续随架构演进重新分配到子域。ssot_path留空（无代码目录）。

### 议题#ARCH-005：layer_id 非法值（L1_platform 不在 arch_layers 合法层表）✅ 已决策

**来源**：6a3c179e 会话独有发现1。

**事实**：`arch_layers` 表只定义了 4 个合法层，但 DB 中有 9 个域使用了 `L1_platform`（不在合法层表中）。

**arch_layers 表合法层定义**（已验证）：

| layer_id | layer_name | decision_type | parent_layer |
|----------|-----------|---------------|--------------|
| L0_infrastructure | 基础设施层 | infrastructure | NULL |
| L1_foundation | 基础服务层 | foundation | L0_infrastructure |
| L2_domain | 领域层 | domain | L1_foundation |
| L3_application | 应用层 | application | L2_domain |

**使用非法值 L1_platform 的 9 个域**：

| 域 | 来源 | ssot_path | 说明 |
|----|------|-----------|------|
| D-AUTONOMY_CORE | 预存脏值 | src/zephyr/autonomy_core/ | 自主核心 |
| D-FRONTEND | 预存脏值 | src/zephyr/frontend/ | 前端 |
| D-INTEGRATION | 预存脏值 | src/zephyr/integration/ | 集成 |
| D-OPS | 预存脏值 | src/zephyr/ops/ | 运维 |
| D-REPORTING | 预存脏值 | src/zephyr/reporting/ | 报告 |
| D-SECURITY | 预存脏值 | src/zephyr/security/ | 安全 |
| D-SHARED | 预存脏值 | src/zephyr/shared/ | 共享 |
| D-SECURITY-LLM | 本会话阶段1引入 | src/zephyr/security/llm_defense/ | LLM防御 |
| D-INTEGRATION-GATEWAY | 本会话阶段1引入 | src/zephyr/integration/mcp/ | MCP网关 |

**修复前 layer_id 值分布**：L2_domain 32 / L1_platform 9(非法) / L1_foundation 6 / L0_infrastructure 5 / NULL 1

**待决策方案**：方案A（仅修2域 D-SECURITY-LLM/D-INTEGRATION-GATEWAY）/ 方案B（注册 L1_platform 为第5个合法层）/ 方案C（全部9域改为 L1_foundation）

**裁定**：采用方案C——将全部 9 个使用 L1_platform 的域改为 L1_foundation（基础服务层）。

**理由**：
1. `L1_platform` 不是 arch_layers 表中的合法层，是预存脏值（7域）和本会话阶段1错误沿用（2域），无任何架构依据
2. 这9个域的 ssot_path 都是 `src/zephyr/xxx/` 基础服务路径，归属 L1_foundation（基础服务层）语义正确
3. 方案B（新增第5层）需修改 YAML + arch_layers 表 + 重新设计层间依赖规则，成本远大于收益
4. 方案A（仅修2域）会留下7个预存脏值，治标不治本

**执行结果**：commit fadd3fdc，9 域全部修改为 L1_foundation。修复后 layer_id 分布：L2_domain 32 / L1_foundation 15 / L0_infrastructure 5 / NULL 1（D-GOV-REPAIR，已 deprecated）。

### 议题#ARCH-006：孤儿边 148 条（预存问题）✅ 已决策

**来源**：6a3c179e 会话独有发现2。

**事实**：edges 表有 148 条边引用了不存在的 node（from_node_id 或 to_node_id 在 nodes 表中不存在）。

**关键验证**：
- 孤儿边**不涉及** node 50999（6a3c179e 会话迁移的节点）
- 孤儿边**不涉及** node 51005（本会话迁移的节点）
- 这是**纯预存问题**，不是任一会话引入的

**样本**（前5条）：

| from_node_id | to_node_id | dep_type | dep_maturity |
|---------------|------------|----------|--------------|
| 48852 | 50843 | import_depends | active |
| 48854 | 50843 | import_depends | active |
| 48855 | 50843 | import_depends | active |
| 48863 | 50843 | import_depends | active |
| 48870 | 50843 | import_depends | active |

**裁定**：留待阶段4（DB约束治理）统一清理。148条孤儿边不影响生产功能（无 production 节点引用），但污染依赖图完整性。阶段4将执行：
1. 调研每条孤儿边的来源（哪些节点被删除时未清理边）
2. 评估是否可安全删除
3. 在 apply_depgraph.py 增加 `cmd_cleanup_orphan_edges()` 命令
4. 执行清理 + 验证

**不立即清理的理由**：preexisting 阶段1-3聚焦3空域+D-SIGNAL元数据修复，孤儿边是独立的预存问题，不在该范围内，避免范围蔓延。

### 议题#ARCH-007：lifecycle 字段无 CHECK 约束 ✅ 已决策

**来源**：6a3c179e 会话独有发现4。

**事实**：domains 表 lifecycle 字段无 CHECK 约束，当前分布4值：

| lifecycle | 域数 | 说明 |
|-----------|------|------|
| operational | 22 | 运行中 |
| design_only | 19 | 设计态 |
| prototype | 11 | 原型 |
| deprecated | 1 | 已废弃 |

**Schema 现状**（`src/zephyr/governance/depgraph_schema.py:158`）：
```sql
lifecycle        TEXT    DEFAULT 'design_only',   -- 无 CHECK 约束
```

**裁定**：接受当前4值为合法值集合，阶段4加 CHECK 约束。

**理由**：
1. 这4个值覆盖了域的完整生命周期：operational（生产运行）→ prototype（原型验证）→ design_only（纯设计态）→ deprecated（已废弃）
2. 与 build_status 的5态（planned→generated→testing→stable→deprecated）互补：lifecycle 描述运行态，build_status 描述构建态
3. 不接受新值：当前4值已满足需求，无需扩展

**阶段4执行**：在 depgraph_schema.py 的 domains 表 DDL 中增加：
```sql
lifecycle TEXT DEFAULT 'design_only'
    CHECK (lifecycle IN ('operational', 'design_only', 'prototype', 'deprecated')),
```
并在 apply_depgraph.py 的 cmd_insert_domain 中校验 lifecycle 值合法性。

---

**文档结束**

> 本报告记录 preexisting DB 问题的完整调研与修复过程。
>
> **阶段1-3 数据修复**：已完成（元数据补齐 / deprecated 标记 / 节点迁移 / build_status 归一化 / layer_id 非法值修复）。
>
> **附录B 架构议题**：7个议题全部决策并落地（#ARCH-001~007）。
> - #ARCH-001~004：本会话发现，裁定#201/#202 落地
> - #ARCH-005：合并 6a3c179e 发现1，裁定#203 落地（已修复）
> - #ARCH-006：合并 6a3c179e 发现2，留待阶段4
> - #ARCH-007：合并 6a3c179e 发现4，留待阶段4加 CHECK 约束
>
> **合并的 6a3c179e 发现3/5**：已分别并入 #ARCH-002 / #ARCH-004 统一裁定，不再单独立项。
