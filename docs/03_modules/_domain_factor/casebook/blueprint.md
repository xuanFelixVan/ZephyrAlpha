---
module_id: MOD-L02-027
title: "因子研究案例库蓝图 — 成功/失败→修复案例沉淀，防 AI 重复试错"
doc_type: blueprint
status: Active
version: "0.1.0"
design_maturity: testing
ttl: permanent
responsibility_domain: 
---

# 因子研究案例库 (Factor Casebook) — D-FACTOR-CASE-01

> **优先级**: P1 | **成熟度**: testing | **建设标记**: ✅可建
> **设计真源**: 2026-08 架构审查报告 §4.2（ALG-03）；92 号清单 §5.3（D2 裁定授权新 SQLite 库）
> **depgraph**: MOD-L02-027（建议号，避让已用 MOD-L02-001~026）

## 1. 大白话简介

案例库是"因子研究的错题本+答案本"——每次 LLM/人工提出一个因子假设并回测后，
把假设、因子表达式、IC/ICIR/换手率统计量和结论（成功/失败/失败→修复）记进 SQLite。
下次 AI 再想挖因子，先查案例库：做过的假设不重复做，失败过的方向看诊断记录，
修复过的案例直接看修复路径。**目的声明：防 AI 重复试错、省 token，为数据期 LLM 挖因子打底。**

机制借鉴 RD-Agent CoSTEER 实证的「成功案例库 + 失败→修复库」——**只借鉴机制，
不引入 RD-Agent/Qlib 框架本体**（审查报告 §7 拒绝清单：WSL2 依赖违反 A-005、与现有回测栈重复）。

## 2. 职责与边界

| 职责 | 说明 | 状态 |
|------|------|------|
| 案例登记 | record_case：假设+表达式+统计量+verdict 落库，返回自增 id | ✅阶段1 |
| 标签检索 | query_similar：按因子族标签（元素级精确匹配）+verdict 过滤，id 倒序 | ✅阶段1 |
| 单条查询 | get_case：按 id 取案例，不存在返回 None | ✅阶段1 |
| 输入门禁 | 空 hypothesis/非法 verdict/NaN·inf 统计量一律 CasebookError 拒绝（fail-closed） | ✅阶段1 |
| 并发写 | WAL + busy_timeout + 进程内 threading.Lock，多线程写不崩 | ✅阶段1 |

**边界（不做）**：
- 不存持仓/金额/下单记录——**只存统计量**（宪章 B-011 合规红线）
- 不做向量检索（后置，待 D_KNOWLEDGE 向量件复用，本版不抢）
- 不做案例自动修剪/去重合并（重复假设允许各存一条，保留完整试错轨迹）
- 不接 LLM 挖因子流程（数据期事项，本模块只提供读写基座）

## 3. 存储

SQLite 单文件 `data/databases/factor_casebook.db`（运行时产物，gitignored 边界同
data/databases/ 既有裁定；92 号 D2 已授权新建）。

```sql
CREATE TABLE IF NOT EXISTS cases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hypothesis TEXT NOT NULL,   -- 研究假设（必填，空串拒绝）
    factor_expr TEXT,           -- 因子表达式文本
    factor_json TEXT,           -- 因子结构化 JSON
    ic REAL,                    -- 信息系数（非有限值拒绝）
    icir REAL,                  -- 信息比率（非有限值拒绝）
    turnover REAL,              -- 换手率（非有限值拒绝）
    verdict TEXT NOT NULL,      -- success / failure / fixed（词表外拒绝）
    failure_diag TEXT,          -- 失败诊断/修复说明
    tags TEXT,                  -- 因子族标签，逗号连接
    created_at TEXT NOT NULL    -- UTC ISO8601 秒级
)
```

连接策略：按调用短生命周期连接（防跨线程 SQLITE_MISUSE）；`PRAGMA journal_mode=WAL`
+ `timeout=30s`；进程内写锁兜底。空库查询返回空且不主动建库文件。

## 4. API 契约

```python
VERDICTS: Final[frozenset[str]] = frozenset({"success", "failure", "fixed"})

class CasebookError(ValueError):
    """案例库输入校验错误（fail-closed：非法输入一律拒绝，不落库）。"""

def record_case(
    hypothesis: str, *, verdict: str,
    factor_expr: str | None = None, factor_json: str | None = None,
    ic: float | None = None, icir: float | None = None,
    turnover: float | None = None, failure_diag: str | None = None,
    tags: str | Iterable[str] | None = None,
    db_path: str | Path | None = None,
) -> int: ...  # 新案例自增 id

def query_similar(
    family_tag: str | None = None, verdict: str | None = None,
    limit: int = 20, *, db_path: str | Path | None = None,
) -> list[dict]: ...  # id 倒序；空库/无匹配返回 []

def get_case(case_id: int, *, db_path: str | Path | None = None) -> dict | None: ...
```

检索口径：`family_tag` 对 tags 逗号串做**元素级精确匹配**（`','||tags||',' LIKE '%,tag,%'`，
转义 `%`/`_`/`\`），防 `mom` 误配 `momentum_long`；返回 dict 中 tags 还原为 `list[str]`；
limit 硬顶 500。

## 5. 不变量 (INVARIANTS)

- 只存统计量，不存持仓/金额（B-011）
- verdict ∈ {success, failure, fixed}，词表外拒绝
- hypothesis 空串/纯空白拒绝；ic/icir/turnover 非有限值（NaN/inf）拒绝
- 校验失败=不落库（fail-closed，CasebookError 为 ValueError 子类）
- WAL + 线程锁：多线程并发写不崩、id 唯一
- 空库查询返回空列表/None，不创建库文件

## 6. 测试计划

`tests/factor/test_casebook.py`（18 用例）：写入-检索闭环 / 最小字段 / fixed+诊断 /
标签检索 / 标签元素级精确（子串不误配）/ verdict 过滤 / limit / 空库（不建文件）/
重复假设各存一条 / 非法 verdict·NaN ic·inf icir·NaN turnover·空 hypothesis 拒绝 /
拒绝后零残留 / 双线程各写 20 条并发。

## 7. ID 映射与消费方

depgraph `blueprint_id=MOD-L02-027`（建议）。首个计划消费者：数据期 LLM 挖因子流程
（T3 CAND-RES 知识族；审查报告 §9.2：D_KNOWLEDGE 域在案例库落地后成为天然消费者）。

### 代码路径索引

| 文件路径 | 实现状态 |
|---------|:---:|
| `src/zephyr/factor/casebook/__init__.py` | ✅ 已实现 |
| `src/zephyr/factor/casebook/casebook.py` | ✅ 已实现 |
| `tests/factor/test_casebook.py` | ✅ 已实现 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-L02-027`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-L02-027` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-L02-027` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-L02-027 | MOD-L02-027 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | generated | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
