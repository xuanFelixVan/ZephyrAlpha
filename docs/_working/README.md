---
title: 临时工作区（_working/）
doc_type: index
ttl: permanent
---

# _working/ 临时工作区

> **本目录是所有过程性文档的默认落点。**
> AI 创建的过程性文档（施工方案/评估报告/提案/调研报告/临时笔记）**必须**放在本目录下，禁止直接放入永久区。

## 一、什么文件放这里

| 文件类型 | 示例 | ttl |
|---------|------|-----|
| 施工方案 | `domain_split_plan_xxx.md` | task_bound |
| 评估报告 | `xxx_assessment.md` | task_bound |
| 规则提案 | `xxx_proposal.md` | task_bound |
| 调研报告 | `xxx_root_cause_report.md` | task_bound |
| 临时笔记/探针产出 | `_tmp_xxx.md` | task_bound |

## 二、什么文件不放这里

以下路径是**永久区**，只存放"结果型"文档（经用户批准才能进入）：

- `docs/01_policies_and_standards/` — 规则、标准、协议
- `docs/02_enterprise_architecture/` — 架构定义、目标架构、决策记录
- `docs/03_modules/` — 模块蓝图、清单
- `docs/08_knowledge/` — 知识库沉淀

**永久区准入规则**：要晋升文件到永久区，必须经用户同意（GitCommitGateway 门禁，后续实现）。

## 三、文件生命周期

```
AI 创建过程文件 → 默认落 docs/_working/（ttl=task_bound）
    │
    ├─ 任务完成 → 文档失效，可清理
    │
    └─ 文件有长期价值，经用户批准 → 晋升到永久区（ttl=permanent）
```

## 四、判定规则

文档 ttl 二元判定（详见 [ttl_vocabulary.yaml](../01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml) 的 decision_tree）：

- **在永久区路径** → `permanent`
- **不在永久区路径**（含 `_working/`）→ `task_bound`

AI 创建文档时，**默认放 `_working/`**，除非用户明确要求创建永久文件。

## 五、新文档必须声明完成条件（completes_when）

`_working/` 新增 `.md` 文件的 frontmatter **必须**包含 `completes_when` 字段，声明一个**可验证的完成条件**。GitCommitGateway 会在 commit 时拦截缺少该字段的新文档。

**目的**：治 AI 工作文档堆积为漂移源——强制 AI 在创建文档时就想清楚"这份文档什么时候算完成可归档"，使 GATE-WORKING-DOCS reconciler 能基于此条件自动判定失效并归档，而非无限堆积。

**示例**：

```yaml
---
ttl: task_bound
doc_type: design
completes_when: "scripts/governance/check_xxx.py 退出码 0 且 docs/_working/ 无幽灵引用"
---
```

**规则**：
- `completes_when` 值为字符串，描述一个可机械验证的条件（脚本退出码、文件存在性、数据库状态等）
- 仅检查**新增**文件（未 git 跟踪）；已跟踪文件修改不触发此校验
- README.md 已跟踪，不受影响

## 六、AI 读取本目录文档前必须自查（防幽灵引用）

本目录是 task_bound 过程性文档堆积区，文档里引用的脚本路径、规则 YAML、blueprint_id 会随项目演进过时，变成"幽灵引用"。AI 读取本目录任何 .md 前，**必须**先验证文档提到的真源是否还在：

1. **提取引用**：把文档里提到的 `scripts/xxx.py`、`docs/.../*.yaml`、`MODULE-ID` 这类真源标识挑出来
2. **验证存在**：用 `git ls-files <path>` 或文件系统检查这些路径是否仍存在
3. **幽灵引用处置**（目标已删除/改名/移动）：
   - **不要照文档执行**——过时信息当真 = 幻觉和漂移的源头
   - 在回复里告诉用户"这文档引用的 xxx 已不存在，内容可能过时"
   - 去查当前真源：`python -m zephyr.governance.capability_lookup --find <关键词>` 反查能力的 canonical 文件
4. **版本漂移处置**（目标还在但字段名/值域变了，如 ttl 词表从 6 值改 2 值）：
   - **以当前真源为准**，不以上述文档为准
   - 必要时提示用户文档内容与新真源不一致

## 七、已知设计权衡（红蓝测试 R5-R8，非 bug）

以下"限制"是 GATE-WORKING-DOCS 体系的**有意设计取舍**，红蓝对抗测试已记录。未来 AI 勿误判为 bug 去扩展，改前先读真源代码注释的权衡理由。

### R5. 幽灵引用只扫 markdown 链接 + 反引号，裸文本路径不扫

- **真源**：[`reconciliation_registry.py` `_extract_refs`](file:///d:/ZephyrAlpha/src/zephyr/governance/reconciliation_registry.py)（L725-742 两个正则 + `_looks_like_path` 过滤）
- **设计**：只提取 markdown 链接 `](path)` 与反引号 `` `path` `` 中扩展名为 `.py/.yaml/.yml/.md` 的路径，且必须含路径分隔符（裸文件名如 `project_memory.md` 跳过）
- **权衡理由**：裸文本路径误报率极高（叙述里提到"foo.py"都会匹配），会归档大量正常文档；含空格的多是命令行示例
- **误判风险**：未来 AI 若认为"裸文本路径引用失效也该归档"是遗漏，去扩展正则扫裸文本 → 误归档风暴

### R6. completes_when 只校验新增文件，已跟踪文件修改不阻断

- **真源**：[`git_commit_gateway.py` `_check_working_docs_completes_when`](file:///d:/ZephyrAlpha/src/zephyr/governance/git_commit_gateway.py)（L748-750 `if self._is_git_tracked(rel): continue`）
- **设计**：只拦截未 git 跟踪的新增 _working/ .md，已跟踪文件修改不校验 completes_when
- **权衡理由**：存量文档创建时无此规则，强制补全会破坏存量 + 阻断正常修改
- **误判风险**：未来 AI 若认为"已跟踪文件也该校验 completes_when"是 bug，去掉 `_is_git_tracked` 跳过 → 存量文档修改被阻断

### R7. N-16 命名唯一性只覆盖 tests/+docs/，src/ 不覆盖

- **真源**：[`trae_028.yaml` `n16_config`](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml) + [`check_naming_convention.py`](file:///d:/ZephyrAlpha/scripts/governance/check_naming_convention.py)
- **设计**：N-16 硬阻断只扫 tests/ + docs/，src/ 同名文件不检测
- **权衡理由**：src/ 有模块化目录结构（包隔离）+ `__all__` 注册 + RULE-TWO 孤儿检测兜底，同名冲突少；tests/docs/ 扁平堆积易撞名
- **误判风险**：未来 AI 若认为"src/ 同名文件也该 N-16 检查"是遗漏，扩展扫描范围 → 误报 src/ 跨包同名（如多个 `__init__.py`/`utils.py`）

### R8. capability_lookup --find 短词误命中

- **真源**：[`capability_lookup.py` `find()`](file:///d:/ZephyrAlpha/src/zephyr/governance/capability_lookup.py) token 包含匹配
- **设计**：find() 用 token 包含匹配（CJK ≥3 字符公共子串），短词如 `ttl` 会命中 `ttl_reconciler`/`vocabulary_values_loader` 等多个能力
- **权衡理由**：token 包含匹配治本（替代中文同义词字典反模式），短词误命中是合理代价
- **误判风险**：用 `--find ttl` 想找"ttl 校验"能力，返回一堆 ttl_* 能力难定位 → 应改用更长关键词（如 `--find ttl_validation`）或 `--get <capability_id>` 精确查
