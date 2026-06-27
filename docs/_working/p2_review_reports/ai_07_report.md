---
doc_type: audit_report
status: active
title: "AI-07 审查报告——P2迁移自修复"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "1.0.0"
created: "2026-06-28"
ttl: task_bound
completes_when: "报告归档"
---

# AI-07 审查报告

## 元信息
- 审查轮次：共4轮（Round1审查→Round1修复→Round2复审→Round2修复→Round3复审→Round4复审）
- 审查时间：2026-06-28
- 负责分区：scripts/governance/d7_code/ 目录下所有 .py 文件（共29个）
- 审查文件数：29
- 最终状态：✅ 通过（连续两次=0）

## 审查结果汇总
- 初始问题数：7（P2主关键词A/B/C=0；REPO_ROOT违规=7）
- 修复问题数：7
- 残留问题数：0
- 连续零问题轮次：第3轮、第4轮

### P2主关键词审查（A/B/C）
| 类别 | 关键词 | 命中数 | 判定 |
|------|--------|--------|------|
| A. SQLite残留 | sqlite3.connect(连depgraph) | 0 | ✅ 通过 |
| A. SQLite残留 | sqlite_master | 0 | ✅ 通过 |
| A. SQLite残留 | import sqlite3 | 0 | ✅ 通过 |
| A. SQLite残留 | ?占位符(depgraph) | 0 | ✅ 通过 |
| A. SQLite残留 | depgraph.db路径硬编码 | 0 | ✅ 通过 |
| B. PG正确性 | get_db_connection | 0（本目录无depgraph连接代码） | ✅ N/A |
| B. PG正确性 | %s | 0（本目录无depgraph查询代码） | ✅ N/A |
| C. module_id | MOD-INF-012B-P2 | 0 | ✅ 通过 |
| C. module_id | MOD-INF-012B-P3 | 0 | ✅ 通过 |

> 说明：scripts/governance/d7_code/ 目录是代码治理脚本（命名检查/导入检查/编码检查等），不直接访问depgraph数据库，因此A/B/C主关键词全部通过。`.sqlite3` 字符串仅出现在SKIP_EXTENSIONS文件扩展名过滤集合中（3处），属豁免项。

### 修复指南约束#8审查（REPO_ROOT）
| 违规模式 | 命中数 | 修复数 |
|----------|--------|--------|
| `REPO_ROOT = Path(__file__).resolve().parents[N]` | 4 | 4 |
| `REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent` | 2 | 2 |
| `_PROJECT_ROOT = Path(__file__).resolve().parents[3]`（用作REPO_ROOT） | 1 | 1 |
| **合计** | **7** | **7** |

> 豁免项：`detect_absolute_path_hardcoding.py:44` 的 `_SCRIPT_DIR = Path(__file__).resolve().parents[1]` 是**合法的一次性sys.path bootstrap**（project_memory允许），该文件随后 `from _shared.constants import EXIT_PASS, SCRIPTS_DIR` 获取路径常量，不违规。

## 修复记录

### 修复1
- **文件**：scripts/governance/d7_code/fix_n12_ke_naming.py
- **行号**：L34
- **类别**：约束#8 (REPO_ROOT用Path(__file__).parents[N]推算)
- **原代码**：
  ```python
  REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
  ```
- **新代码**：
  ```python
  _SCRIPT_DIR = Path(__file__).resolve()
  _GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
  if _GOV_DIR not in sys.path:
      sys.path.insert(0, _GOV_DIR)

  from _shared.constants import REPO_ROOT
  ```
- **依据文件**：scripts/governance/_shared/constants.py（L42: `from zephyr.shared.io.paths import REPO_ROOT`——真源re-export）+ 修复指南约束#8

### 修复2
- **文件**：scripts/governance/d7_code/fix_n06_scope.py
- **行号**：L56
- **类别**：约束#8 (REPO_ROOT用Path(__file__).parents[N]推算)
- **原代码**：
  ```python
  REPO_ROOT = Path(__file__).resolve().parents[3]
  ```
- **新代码**：
  ```python
  _SCRIPT_DIR = Path(__file__).resolve()
  _GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
  if _GOV_DIR not in sys.path:
      sys.path.insert(0, _GOV_DIR)

  from _shared.constants import REPO_ROOT
  ```
- **依据文件**：scripts/governance/_shared/constants.py L42 + 修复指南约束#8

### 修复3
- **文件**：scripts/governance/d7_code/detect_forward_reference.py
- **行号**：L39
- **类别**：约束#8 (REPO_ROOT用Path(__file__).parents[N]推算)
- **原代码**：
  ```python
  REPO_ROOT = Path(__file__).resolve().parents[3]
  ```
- **新代码**：
  ```python
  _SCRIPT_DIR = Path(__file__).resolve()
  _GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
  if _GOV_DIR not in sys.path:
      sys.path.insert(0, _GOV_DIR)

  from _shared.constants import REPO_ROOT
  ```
- **依据文件**：scripts/governance/_shared/constants.py L42 + 修复指南约束#8

### 修复4
- **文件**：scripts/governance/d7_code/fix_n15_blueprint_path.py
- **行号**：L32
- **类别**：约束#8 (REPO_ROOT用Path(__file__).parent.parent链推算)
- **原代码**：
  ```python
  REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
  ```
- **新代码**：
  ```python
  _SCRIPT_DIR = Path(__file__).resolve()
  _GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
  if _GOV_DIR not in sys.path:
      sys.path.insert(0, _GOV_DIR)

  from _shared.constants import REPO_ROOT
  ```
- **依据文件**：scripts/governance/_shared/constants.py L42 + 修复指南约束#8

### 修复5
- **文件**：scripts/governance/d7_code/fix_n14_init_all.py
- **行号**：L34
- **类别**：约束#8 (REPO_ROOT用Path(__file__).parents[N]推算)
- **原代码**：
  ```python
  REPO_ROOT = Path(__file__).resolve().parents[3]
  ```
- **新代码**：
  ```python
  _SCRIPT_DIR = Path(__file__).resolve()
  _GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
  if _GOV_DIR not in sys.path:
      sys.path.insert(0, _GOV_DIR)

  from _shared.constants import REPO_ROOT
  ```
- **依据文件**：scripts/governance/_shared/constants.py L42 + 修复指南约束#8

### 修复6
- **文件**：scripts/governance/d7_code/fix_n13_snake_case.py
- **行号**：L35
- **类别**：约束#8 (REPO_ROOT用Path(__file__).parent.parent链推算)
- **原代码**：
  ```python
  REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
  ```
- **新代码**：
  ```python
  _SCRIPT_DIR = Path(__file__).resolve()
  _GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
  if _GOV_DIR not in sys.path:
      sys.path.insert(0, _GOV_DIR)

  from _shared.constants import REPO_ROOT
  ```
- **依据文件**：scripts/governance/_shared/constants.py L42 + 修复指南约束#8

### 修复7
- **文件**：scripts/governance/d7_code/fix_naming_manual.py
- **行号**：L37（及L38/L91/L128/L179/L185/L192/L212/L238/L433 共10处引用）
- **类别**：约束#8 (REPO_ROOT用Path(__file__).parents[N]推算，变量名_PROJECT_ROOT)
- **原代码**：
  ```python
  _PROJECT_ROOT = Path(__file__).resolve().parents[3]
  _CHECK_SCRIPT = _PROJECT_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"
  # ...另有8处使用 _PROJECT_ROOT（cwd=os.walk参数等）
  ```
- **新代码**：
  ```python
  _SCRIPT_DIR = Path(__file__).resolve()
  _GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
  if _GOV_DIR not in sys.path:
      sys.path.insert(0, _GOV_DIR)

  from _shared.constants import REPO_ROOT
  _CHECK_SCRIPT = REPO_ROOT / "scripts" / "governance" / "d3_metadata" / "check_naming_convention.py"
  # ...10处 _PROJECT_ROOT 全部重命名为 REPO_ROOT（对齐项目标准变量名）
  ```
- **依据文件**：scripts/governance/_shared/constants.py L42 + 修复指南约束#8 + project_memory（REPO_ROOT标准变量名）

## 未修复问题（需主AI协调）
无。本分区所有问题均已修复，无跨分区问题。

## 确认无问题项
- A. SQLite残留（sqlite3.connect/sqlite_master/import sqlite3/?占位符/depgraph.db硬编码）：✅ 通过（0命中）
- B. PG正确性：✅ 通过（本目录无depgraph连接代码，N/A）
- C. module_id（MOD-INF-012B-P2/P3）：✅ 通过（0命中）
- REPO_ROOT约束#8：✅ 通过（7处违规全部修复，剩余1处为合法bootstrap）
- TTL字段（# [TTL] task_bound）：✅ 通过（29个文件全部含TTL标记）
- module_id命名（MOD-INF-005）：✅ 通过（本目录module_id为MOD-INF-005，非违规的P2/P3）
- .sqlite3扩展名过滤（3处）：✅ 豁免（SKIP_EXTENSIONS集合，非SQLite连接）
- 语法验证：✅ 通过（7个修复文件ast.parse全部通过）
- 导入验证：✅ 通过（3个抽样文件REPO_ROOT值一致=D:\ZephyrAlpha）

## 结论
- [x] 无问题，本分区审查通过（连续两次=0）
- [ ] 有残留问题，需主AI协调

---

## 红蓝极限对抗审核（第七节 7.3）

### 7.3.1 模拟新AI可发现性测试

| 测试项 | 判定 | 说明 |
|--------|------|------|
| 可被发现性 | ✅ 通过 | 新AI扫描d7_code目录，25/25文件均用 `from _shared.constants import REPO_ROOT`，模式高度一致 |
| 可被绕过性 | ✅ 通过 | `_shared/constants.py` 是治理脚本统一入口，新AI若绕过将无法获得EXIT_*等必需常量 |
| 可被使用性 | ✅ 通过 | 接口清晰：`from _shared.constants import REPO_ROOT`，无需理解bootstrap细节 |
| 可被重复造轮子性 | ✅ 通过 | 25个文件统一模式，`_shared/constants.py` docstring明确声明"不再各自硬编码parents[N]" |

### 7.3.2 红蓝极限对抗测试

**红方攻击1**：如果 `_shared/` 目录不存在怎么办？
- 蓝方防御：bootstrap代码 `next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists())` 会抛StopIteration，与目录中其他18个文件行为一致（同模式同风险，非本次修复引入）。

**红方攻击2**：如果有人把 `REPO_ROOT` 改回 `Path(__file__).parents[N]` 怎么办？
- 蓝方防御：修复后的代码已统一从 `_shared.constants` 导入，且该模块docstring明确禁止。如被改回，治理脚本 `detect_absolute_path_hardcoding.py` 会检测到硬编码路径。

**红方攻击3**：bootstrap是否会产生重复sys.path条目？
- 蓝方防御：代码含 `if _GOV_DIR not in sys.path` 守卫，幂等。

**红方攻击4**：fix_naming_manual.py 中 `_PROJECT_ROOT` → `REPO_ROOT` 重命名是否遗漏？
- 蓝方防御：Grep确认10处全部替换完成（`_PROJECT_ROOT` 0命中）。

**红方攻击5**：修复是否引入循环导入？
- 蓝方防御：导入链 `d7_code → _shared.constants → zephyr.shared.io.paths`，无回环。

**对抗结论**：5项攻击全部被蓝方防御住，无对抗漏洞。

---

## 大白话汇报（向内收审核结论）

### 我做了什么
把 scripts/governance/d7_code/ 目录下7个Python文件里"自己用 Path(__file__).parents[N] 算仓库根"的写法，统一改成"从 _shared.constants 导入 REPO_ROOT"。

### 这个功能的作用
让这7个治理脚本和目录里其他18个脚本一样，通过唯一入口 `_shared.constants` 获取仓库根路径常量。

### 达成了什么目标
消除了7处 REPO_ROOT 真源分裂——之前每个文件各自算 `parents[3]` 或 `parent.parent.parent.parent`，现在全部统一到 `zephyr.shared.io.paths.REPO_ROOT`（经 `_shared.constants` re-export）。

### 解决了什么痛点
解决了"同一概念多处定义"的漂移风险：如果仓库根算法变化（如改用marker文件搜索），之前要改7个文件，现在只需改 `zephyr.shared.io.paths` 一处。

### 功能通过什么触发自动启动
不适用——这些是手动触发的一次性治理脚本（STARTUP: manual），不是永久性系统。修复只改了REPO_ROOT获取方式，未改触发机制。

### 如何自动运行
不适用（手动脚本）。触发后：bootstrap找到_shared → 导入REPO_ROOT → 执行原有治理逻辑。

### 如何自动关闭
不适用（手动脚本）。脚本执行完即退出，无需人工干预关闭。

### 向内收审核结果
- [x] 责任唯一真源唯一：通过（7处分裂已合并到 zephyr.shared.io.paths 唯一真源）
- [x] 能用现成不创造：通过（未创建新文件，复用已有 _shared.constants 模块，与18个现有文件同模式）
- [x] 永久系统全自动：通过（N/A——本目录是手动治理脚本，非永久系统；修复未改触发机制）
- [x] 第一性原理治本：通过（治本：消除parents[N]散点算法，改为统一真源导入；非打补丁）
- [x] AI可发现性：通过（25/25文件同模式，_shared/constants.py docstring声明约定，新AI扫描即可发现）
- [x] 红蓝对抗：通过（5项攻击全部防御，无对抗漏洞）
