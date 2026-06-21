---
module_id: GOV-077
title: ZephyrAlpha 审计脚本质量标准
doc_type: standard
status: active
version: "1.3.0"
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-02"
valid_from: "2026-05-02"
summary: "ZephyrAlpha 审计脚本（scripts/governance/ 下所有 .py 文件）的质量标准唯一真源。定义 8 个质量维度及 MUST/SHOULD/MAY 条款。AI 创建或修复任意审计脚本时，必须以本标准为强制参考。对标 Google Python Style Guide + PEP 484/257/540 + OWASP + Clean Code + ISO 25010 + ISTQB。"
ttl: permanent
tags: [script-quality, coding-standard, ssot, ai-governance, audit]
rule_form: declarative
scope: global
stability: stable
verifiability: automated
depends_on:
  - {target: "D:/ZephyrAlpha/AGENTS.md", at: "§6.7", why: "UTF-8 输出强制声明——审计脚本编码安全铁律"}
  - {target: "PS-STD-001", at: "§2", why: "frontmatter 字段 SSoT——元数据结构标准"}
  - {target: "PS-STD-003", at: "§3~§5", why: "行为边界 ABS/COND/REC——禁止行为定义权威"}
ai_autonomy: immutable_core
---

# ZephyrAlpha 审计脚本质量标准

> **module_id**: SCRIPT-QUALITY-001 | **version**: 1.2.0 | **status**: active
>
> 本标准是 ZephyrAlpha 审计脚本（`scripts/governance/` 下所有 `.py` 文件）的**质量唯一真源（SSoT）**。
> AI 创建新审计脚本或修复已有审计脚本时，必须逐项对照本标准检查——任何违反 MUST 条款的交付视为不合格。
>
> **对标**：Google Python Style Guide（代码规范）、PEP 484（类型注解）、PEP 257（文档字符串）、PEP 540（UTF-8 模式）、OWASP（安全编码）、Clean Code（架构设计）、ISO 25010（可靠性）。

---

## 1. 目的与范围

### 1.1 目的

确保 `scripts/governance/` 下每一份审计脚本具备：

- **编码安全**：Windows GBK 环境不崩溃、不安全命令不执行
- **类型安全**：AI 和人类均能无歧义理解函数接口
- **文档自足**：新 AI session 仅读脚本即可理解其意图和用法
- **架构一致**：与 `run_all.py` + `script_manifest.yaml` 的契约对齐
- **错误健壮**：脚本不会因意外输入静默失败或输出误导信息
- **输出规范**：POSIX exit codes + 结构化输出 → 可被 CI/调度系统消费
- **可维护**：无魔法数字、无隐式依赖、配置外置
- **可测试**：每个脚本可独立验证正确性，修改后不会意外破坏其他脚本

### 1.2 适用范围

- **范围**：`scripts/governance/` 及其子目录（`d1_*` ~ `d12_*`）下所有 `.py` 文件
- **消费者**：AI session（创建/修复时）、`run_all.py`（调度执行时）、CI pipeline（门禁校验时）

### 1.3 术语

| 术语 | 含义 |
|------|------|
| **MUST** | 强制条款——违反视为不合格交付。对标 IETF BCP 14 §2（absolute requirement） |
| **SHOULD** | 推荐条款——有正当理由可以例外，但须在 Session Log 中记录原因。对标 IETF BCP 14 §3 |
| **MAY** | 可选条款——功能可以这样做，但不是必须。对标 IETF BCP 14 §5 |
| **审计脚本** | `scripts/governance/` 下所有以 `validate_` / `detect_` / `audit_` 命名前缀的 `.py` 文件 |
| **run_all.py 契约** | 脚本必须可独立运行（`--warn-only` exit 0）+ 注册在 `script_manifest.yaml` |

---

## 2. SSoT 声明

### 2.1 本标准是什么的真源

本标准是 **审计脚本质量要求** 的唯一真源。当 `AGENTS.md`、`scripts/governance/index.md` 或其他文件对脚本质量的要求与本标准不一致时，以本标准为准。

### 2.2 本标准取代什么

- 取代 `scripts/governance/index.md` 中分散的质量约定（统一为本标准）
- 取代 AGENTS.md §6.7 之外的隐式质量预期（显式化为 8 维度 MUST 条款）

### 2.3 本标准与什么互补（不取代）

| 文件 | 关系 | 说明 |
|------|:---:|------|
| AGENTS.md §6.5 | 互补 | AGENTS.md 定义**入库流程**（A0→A→B→C→D），本标准定义**代码质量**——两不冲突 |
| `script_manifest.yaml` | 互补 | manifest 定义**注册格式**（dimensions/priority/timeout），本标准定义**代码格式** |
| PS-STD-003（行为边界） | 引用 | 本标准中的禁止条款引用 PS-STD-003 的 ABS/COND 编号，不重复定义 |
| `scripts/governance/index.md` | 互补 | index.md 是脚本体系**导航入口**，本条是**质量约束**——索引引用标准 |

---

## 3. 质量维度定义

### 维度总览

| # | 维度 | 对标机构 | 核心约束 |
|:--:|------|---------|---------|
| D-A | **编码安全** | PEP 540 + OWASP + Google Style Guide §Exceptions | UTF-8 声明、精确异常捕获、无 `shell=True` |
| D-B | **类型安全** | PEP 484 + mypy strict | 完整函数签名注解、返回值类型、`NoReturn` 声明 |
| D-C | **文档规范** | PEP 257 + Google Docstring | 模块级 docstring + 函数 docstring（Args/Returns/Raises） |
| D-D | **架构设计** | Clean Code §3/§6/§17 | 单一职责、惰性加载、常量集中、无魔法数字 |
| D-E | **错误处理** | ISO 25010 §4.2 + Netflix Chaos Engineering | 异常分级、优雅降级、不吞异常 |
| D-F | **输出规范** | POSIX 标准 + `run_all.py` 契约 | 结构化输出、`--warn-only`、POSIX exit codes |
| D-G | **可维护性** | Clean Code §17 + Kubernetes Declarative Config | 配置外置、显式优于隐式、无隐式依赖 |
| D-H | **可测试性** | ISTQB Foundation Level + Google Testing Blog TWIMC | smoke test、核心逻辑覆盖、测试隔离 |

---

### D-A — 编码安全（Encoding Safety）

> **对标**：PEP 540（UTF-8 Mode）| Google Python Style Guide §2.4（Exceptions）| OWASP（Command Injection）

| # | 条款 | 级别 |
|:--:|------|:--:|
| D-A-01 | 脚本 MUST 在文件开头包含 UTF-8 stdout 强制重声明（AGENTS.md §6.7 强制约定） | MUST |
| D-A-02 | 脚本 MUST 精确捕获具体异常类型（`FileNotFoundError`、`ValueError` 等），禁止裸 `except` 或裸 `except Exception` | MUST |
| D-A-03 | 脚本 MUST NOT 使用 `subprocess.run(..., shell=True)`，对标 OWASP Command Injection 防护 | MUST |
| D-A-04 | 脚本 SHOULD 在 I/O 操作时显式指定 `encoding='utf-8'` | SHOULD |
| D-A-05 | 脚本 MUST NOT 重复 import 同一模块（同一 `import X` 或 `from X import Y` 在文件中出现多次） | MUST |

**D-A-01 标准写法**：
```python
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
```

> **大白话**：Windows 终端默认编码是 GBK，遇到 emoji/中文直接崩溃。加这 2 行代码强制输出 UTF-8——活不大但不修就漏水。

---

### D-B — 类型安全（Type Safety）

> **对标**：PEP 484 + mypy strict 模式

| # | 条款 | 级别 |
|:--:|------|:--:|
| D-B-01 | 所有公共函数 MUST 包含完整类型注解（参数类型 + 返回值类型） | MUST |
| D-B-02 | `main()` 函数 MUST 声明返回类型 `-> None` | MUST |
| D-B-03 | 永不返回的函数（如 `sys.exit()` 调用者）SHOULD 声明 `-> NoReturn` | SHOULD |
| D-B-04 | 脚本 SHOULD 通过基础类型检查——`mypy {script}.py` 无 import-not-found 之外的错误；mypy strict 模式（`--strict`）为远期目标，当前不强制 | SHOULD |

**标准写法示例**：
```python
from typing import NoReturn

def main() -> None:
    """入口——解析参数并执行对应维度扫描。"""
    args = _parse_args()
    findings = _scan_dimensions(args.dimension)
    _write_report(findings)
```

---

### D-C — 文档规范（Documentation Standards）

> **对标**：PEP 257（Docstring Conventions）+ Google Python Style Guide §3.8（Comments and Docstrings）

| # | 条款 | 级别 |
|:--:|------|:--:|
| D-C-01 | 每个 `.py` 文件 MUST 包含模块级 docstring——说明脚本目的、对标规则、输出格式 | MUST |
| D-C-02 | 所有公共函数 MUST 包含 docstring，格式为 Google Style（Args/Returns/Raises） | MUST |
| D-C-03 | 简单函数（≤3 行、逻辑自明）SHOULD 至少包含一行 docstring | SHOULD |
| D-C-04 | imports SHOULD 按 PEP 8 分组排序——stdlib → third-party → local，每组间空一行 | SHOULD |

**D-C-04 标准格式**：
```python
# stdlib
import os
import sys
from pathlib import Path

# third-party
import yaml

# local
from _shared.config import PROJECT_ROOT
```

**Google Docstring 标准格式**：
```python
def detect(pattern: str, directory: Path) -> list[str]:
    """扫描目录下匹配模式的文件。

    Args:
        pattern: 正则表达式模式。
        directory: 扫描目标目录路径。

    Returns:
        list[str]: 匹配文件路径列表。

    Raises:
        FileNotFoundError: 目录不存在时抛出。
        re.error: 正则表达式非法时抛出。
    """
```

---

### D-D — 架构设计（Architecture Design）

> **对标**：Clean Code §3（Functions）| §6（Objects and Data Structures）| §17（Smells and Heuristics）

| # | 条款 | 级别 |
|:--:|------|:--:|
| D-D-01 | 每个函数 MUST 只做一件事——一个函数只负责一个明确的职责 | MUST |
| D-D-01a | 单函数逻辑行数 SHOULD ≤ 50 行——超过时 SHOULD 拆分为多个函数 | SHOULD |
| D-D-02 | 模块级初始化 MUST 使用惰性加载——禁止在 `import` 时执行有副作用的代码（对标 Google Style Guide §2.10） | MUST |
| D-D-03 | 所有魔法数字 MUST 提取为模块级命名常量（如 `MAX_RETRIES = 3`） | MUST |
| D-D-04 | 同一概念 MUST 只在一处定义——禁止两个脚本各自硬编码同一条规则阈值 | MUST |
| D-D-05 | 脚本 MUST NOT 跨文件复制粘贴逻辑——公共功能 MUST 提取到 `scripts/governance/_shared/` | MUST |
| D-D-06 | 脚本 MUST 使用 `if __name__ == "__main__"` 守卫——无守卫的脚本无法被 import 测试，直接违反 D-H 可测试性 | MUST |
| D-D-07 | 脚本 MUST NOT 本地重定义 `_shared/` 已导出的函数/常量（如 `parse_frontmatter`、`REPO_ROOT`、`SRC_DIR`、`EXCLUDE_DIRS`）——必须通过 `from _shared.xxx import` 引用。对标 AGENTS.md §8.2.1 `_shared/` API 速查目录 | MUST |
| D-D-08 | 脚本 MUST NOT 使用 `os.walk()` + 手动 `EXCLUDE_DIRS` 过滤模式——必须使用 `_shared.walk.iter_files()`。对标 D-D-05（公共功能提取到 `_shared/`） | MUST |

**D-D-02 反例（禁止）**：
```python
# ❌ 模块导入时即执行副作用
SCRIPT_REGISTRY = _load_script_registry()
```

**D-D-02 正例（允许）**：
```python
_registry: dict[str, ScriptInfo] | None = None

def _get_registry() -> dict[str, ScriptInfo]:
    """惰性加载——首次调用时从 manifest 构建。"""
    global _registry
    if _registry is None:
        _registry = _load_registry()
    return _registry
```

**D-D-05 反例（禁止）**：
```python
# ❌ detect_shell_true.py 和 detect_git_dangerous.py 各自复制了同一个 YAML 解析函数
def _load_yaml(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)
```

**D-D-05 正例（允许）**：
```python
# ✅ 提取到 _shared/yaml_utils.py，两个脚本均 import
from _shared.yaml_utils import load_yaml
```

---

### D-E — 错误处理（Error Handling）

> **对标**：ISO 25010 §4.2（Reliability）| Netflix Chaos Engineering（优雅降级）

| # | 条款 | 级别 |
|:--:|------|:--:|
| D-E-01 | 异常 MUST 分级处理——CRITICAL 抛给调用者 / HIGH 记录后继续 / LOW 静默跳过 | MUST |
| D-E-02 | 脚本 MUST NOT 吞异常——捕获异常后至少记录一条 WARNING 级别日志或输出到 stderr | MUST |
| D-E-03 | 外部输入（命令行参数、文件内容）MUST 在使用前校验合法性 | MUST |
| D-E-04 | 脚本 SHOULD 实现优雅降级——子任务失败不应整体崩溃，应输出 PARTIAL 级别 report | SHOULD |

**D-E-03 标准模式**：
```python
def _parse_dimension(raw: str) -> Dimension:
    """将命令行维度参数转为 Dimension 枚举。

    Raises:
        ValueError: 收到不合法维度值时立即抛出——不在下游产生歧义。
    """
    try:
        return Dimension(raw.upper())
    except KeyError:
        raise ValueError(f"非法维度值: '{raw}'。合法值: {[d.value for d in Dimension]}")
```

---

### D-F — 输出规范（Output Standards）

> **对标**：POSIX Exit Code 标准（0=成功 / 1=通用错误 / 2=误用）+ `run_all.py` 消费者契约

| # | 条款 | 级别 |
|:--:|------|:--:|
| D-F-01 | 脚本 MUST 支持 `--warn-only` 参数——warn 模式下诊断发现问题但 exit 0（不阻断 CI） | MUST |
| D-F-02 | 脚本 MUST 使用 POSIX exit codes：0（成功/无发现）、1（发现违规）、2（脚本使用错误） | MUST |
| D-F-03 | 输出 MUST 结构化——至少是可被 `grep` 解析的行式格式（`FILE:LINE:SEVERITY:MESSAGE`） | MUST |
| D-F-04 | 脚本 MUST 注册在 `script_manifest.yaml` 中——`run_all.py` 通过 manifest 发现脚本 | MUST |
| D-F-05 | 脚本 MUST 区分 stdout（数据输出）和 stderr（诊断信息）——12-Factor App §XI：日志/警告写 stderr，结构化结果写 stdout | MUST |

**D-F-05 标准模式**：
```python
import sys

def _diagnose(msg: str) -> None:
    """诊断信息——写入 stderr，不污染 stdout 数据流。"""
    print(f"[WARN] {msg}", file=sys.stderr)

def main() -> None:
    findings = _scan()
    # 数据 → stdout
    for finding in findings:
        print(f"{finding.file}:{finding.line}:{finding.severity}:{finding.message}")
    # 诊断 → stderr
    if not findings:
        _diagnose("未发现违规——目标目录可能为空或扫描模式未命中")
```

**D-F-01 标准模式**：
```python
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--warn-only", action="store_true",
                        help="诊断发现问题但 exit 0（用于 CI 非阻断检查）")
    args = parser.parse_args()

    findings = _scan()
    _print_findings(findings)

    if args.warn_only or not findings:
        sys.exit(0)
    sys.exit(1)
```

---

### D-G — 可维护性（Maintainability）

> **对标**：Clean Code §17（Smells and Heuristics）| Kubernetes Declarative Config（配置外置）

| # | 条款 | 级别 |
|:--:|------|:--:|
| D-G-01 | 路径/阈值等运行参数 SHOULD 外置为命令行参数或配置常量——禁止硬编码在函数体内 | SHOULD |
| D-G-01a | 脚本 SHOULD 从项目根推导路径（如 `Path(__file__).resolve().parents[2]`），而非硬编码绝对路径（如 `d:/ZephyrAlpha/`）——对标 12-Factor App §X（Dev/Prod Parity：开发/生产环境路径结构应一致） | SHOULD |
| D-G-02 | 公共功能（如 YAML 解析、路径标准化）SHOULD 提取到 `scripts/governance/_shared/` 作为共享模块 | SHOULD |
| D-G-03 | 显式优于隐式——函数的依赖应通过参数注入，不应隐式依赖全局状态或环境变量（如 `PROJECT_ROOT` 应通过参数传入而非直接引用模块级常量） | SHOULD |
| D-G-04 | 脚本 SHOULD NOT 包含冗余计算——循环内重复查找应使用缓存 | SHOULD |
| D-G-05 | 脚本 SHOULD 有清晰的命令行参数定义——使用 `argparse.ArgumentParser` 而非手动解析 `sys.argv` | SHOULD |
| D-G-06 | 代码变换 MUST 使用无损工具——禁止 `ast.unparse()` 重写文件（丢失行内注释/格式），必须使用 LibCST（`libcst.parse_module()` → `CSTTransformer` → `tree.code`）或等效无损方案。对标 Instagram/Meta LibCST + ruff safe/unsafe 修复分类 | MUST |

---

### D-H — 可测试性（Testability）

> **对标**：ISTQB Foundation Level（测试基础理论）| Google Testing Blog TWIMC（测试有意义的行为）| Google SRE Book Ch.16（可运维 = 可测试）

| # | 条款 | 级别 |
|:--:|------|:--:|
| D-H-01 | 脚本 MUST 至少包含一个 smoke test——能 `python {script}.py --warn-only` 无异常退出（此测试验证脚本基本可运行性，是 script_manifest.yaml 注册的隐含前置条件） | MUST |
| D-H-02 | 核心检测逻辑 SHOULD 有单元测试——至少用 `assert` 验证典型输入产生预期输出 | SHOULD |
| D-H-03 | 测试 SHOULD 验证具体行为而非仅验证"不抛异常"——例：`assert detect("secret_key", code) == ["line 5"]`，而非仅 `assert detect(...) is not None` | SHOULD |
| D-H-04 | 测试 SHOULD 彼此隔离——不依赖运行顺序、不共享可变全局状态 | SHOULD |

**D-H-02 标准模式（最小可行测试）**：
```python
# test_detect_secrets.py
from d6_security.detect_secrets import detect_pattern

def test_detect_api_key() -> None:
    """验证典型 API Key 模式被正确检测。"""
    code = 'API_KEY = "sk-abc123def456"'
    findings = detect_pattern(r'sk-[A-Za-z0-9]+', code)
    assert len(findings) == 1
    assert "sk-abc123def456" in findings[0]

def test_clean_code_no_false_positive() -> None:
    """验证正常代码不产生误报。"""
    code = 'version = "1.0.0"'
    findings = detect_pattern(r'sk-[A-Za-z0-9]+', code)
    assert len(findings) == 0
```

> **大白话**：D-H-01 就像"出厂自检"——每件产品出厂前至少通一次电看能不能开机。D-H-02~D-H-04 是"质检标准"——不仅测能不能开机，还测开机后功能对不对。审计脚本尤其重要——如果检测器有 bug 说"没问题"，比直接崩溃更危险（false negative > crash）。

---

## 4. 好的脚本系统的可操作验收标准

> **对标**：Google Testing Blog TWIMC（Test What Is Meaningful to Customers）——测试应该验证用户关心的行为。
>
> 以下 6 条是可被 AI 直接自检的**行为判据**。任何一个新 AI session 读完这 6 条，即可判断审计脚本系统是否处于健康状态——无需通读全部 8 个质量维度。

| # | 判据 | 验证方式 | 对应维度 |
|:--:|------|---------|:--:|
| 1 | **知道有哪些脚本** | `python scripts/governance/run_all.py --list` 一次性列出全部注册脚本及维度映射 | D-F-04 |
| 2 | **知道每个脚本做什么** | 任意脚本 `{script}.py` 的模块级 docstring 自描述其目的、对标规则、输出格式 | D-C-01 |
| 3 | **一键运行全部** | `python scripts/governance/run_all.py` 无参数执行，全部 12 维度完成，0 脚本异常（此判据验证的是调度系统健康度，与 D-H-01 的单个脚本 smoke test 互补——前者是"orchestra 能演奏"，后者是"每件乐器能发声"） | D-F-04 |
| 4 | **知道哪里坏了** | 每个脚本 exit code 精确（0/1/2），stderr 输出可操作的诊断信息（而非仅 "Error"） | D-F-02, D-F-05 |
| 5 | **能改一个而不会意外弄坏另一个** | 每个脚本有至少一个 smoke test（D-H-01），核心逻辑有对应单元测试（D-H-02） | D-H |
| 6 | **能找到复用的东西** | 共享常量/工具函数在 `scripts/governance/_shared/` 集中定义，脚本通过 import 引用 | D-D-05, D-G-02 |

> **大白话**：这 6 条就是"体检总评"——不用看几十项指标，看这 6 条就知道整个脚本系统是否健康。每一条都对应到具体的命令或行为，AI 可以逐条执行验证，不需要"理解意图"。

---

## 5. 消费者注册表

| 消费者 | Tier | 消费方式 | 变更影响 |
|--------|:----:|---------|---------|
| `run_all.py` | Tier 1 | 脚本执行结果依赖本标准的 D-F（exit codes）和 D-A（UTF-8） | exit code 定义变更 → 调度逻辑可能需调整 |
| `status.py` | Tier 1 | 依赖 D-F（结构化输出）解析脚本状态 | 输出格式变更 → status.py 需同步更新 |
| `scripts/governance/index.md` | Tier 2 | 索引文件引用本标准为"质量宪章" | 版号变更 → 索引的交叉引用需更新 |
| AGENTS.md §8.2 | Tier 2 | 任务路由表引用本标准 | 文件名/路径变更 → AGENTS.md 路由条目需同步（本标准 `immutable_core`，变更需 Owner 审批） |
| 所有 `d*_*/validate_*` 脚本 | Tier 1 | 脚本必须遵守本标准的 MUST 条款才能通过 code review | MUST 条款变更 → 存量脚本需逐份修复 |
| `script_manifest.yaml` | Tier 2 | manifest 注册的脚本应满足本标准质量标准 | 新增 quality 类字段 → manifest schema 需扩展 |

---

## 6. 禁止行为

以下行为直接违反本标准，对标 PS-STD-003 行为边界体系：

| # | 禁止行为 | 对标 PS-STD-003 | 后果 |
|:--:|---------|:--------------:|------|
| D-FORBID-01 | 交付违反任意 D-A/D-B/D-C/D-D/D-E/D-F MUST 条款，或无正当理由跳过 D-G/D-H SHOULD 条款的脚本 | COND-43 | 视为不合格交付——AI 必须修复或记录例外原因后方可标记任务完成 |
| D-FORBID-02 | 跳过本标准检查，凭"之前做过类似脚本"的记忆直接写新脚本 | ABS-13（幻觉自检） | 禁止——没有两个 script context 完全一样，省略检查必出问题 |
| D-FORBID-03 | 在脚本中硬编码路径（如 `d:/ZephyrAlpha/`），而非通过参数或项目根推导 | D-G-01a | 脚本不可移植——CI 环境和本地环境路径结构可能不同 |
| D-FORBID-04 | 跨脚本复制粘贴逻辑——同一个函数在两个文件中各自定义 | D-D-05 | 违反 DRY——一处修 bug 另一处仍然有 bug，是最恶劣的技术债务之一 |
| D-FORBID-05 | 创建 `.py` 文件在 `scripts/governance/`、`src/zephyr/`、`tests/` 之外的落位，且未在 Session Log 中充分论证 | AGENTS.md §6.5 v2.0 | 违规——对标 K8s Admission Controller：所有 .py 文件只有三个合法落位，不在其中必须论证 |

---

## 7. 标准间引用规范

### 7.1 Normative 引用（必须遵守）

| 引用目标 | 说明 |
|---------|------|
| AGENTS.md §6.7 | UTF-8 stdout 重声明——所有审计脚本的编码安全铁律 |
| AGENTS.md §6.5 v2.0 | 脚本自创入库强制约定——任何 .py 文件只有三个合法落位（scripts/governance/、src/zephyr/、tests/），不在其中必须 Session Log 论证 |
| PEP 540 | Python UTF-8 Mode 标准——Windows 下编码问题的权威解决方案 |
| PEP 484 | Type Hints——函数签名的类型注解标准 |
| PEP 257 | Docstring Conventions——文档字符串格式标准 |
| PEP 8 §Imports | 导入语句组织规范——分组排序的权威定义 |
| POSIX Exit Codes | 0=成功 / 1=错误 / 2=误用——脚本退出码的权威定义 |
| 12-Factor App §XI | Logs——stdout（数据）vs stderr（诊断）分离的权威实践 |

### 7.2 Informative 引用（仅供参考）

| 引用目标 | 说明 |
|---------|------|
| Google Python Style Guide | 编码风格——本项目对标其 Exceptions、Docstrings、Imports 章节，非全文采纳 |
| Google SRE Book Ch.16~17 | 可运维性——Ch.16（代码正确性）+ Ch.17（Toil 管理），启发 D-E + D-H |
| ISTQB Foundation Level | 测试基础理论——启发 D-H 的测试条款级别设计 |
| Google Testing Blog TWIMC | 测试有意义的行为——启发 §4 的 6 点验收标准 |
| Clean Code（Robert C. Martin） | 架构原则——§3/§6/§17 被本标准采纳，其余章节供参考 |
| ISO 25010 §4.2 | 可靠性标准——定义"优雅降级"的理论框架，非逐条映射 |
| Netflix Chaos Engineering | 错误注入理念——启发 D-E-04（优雅降级），非实操指南 |
| Kubernetes Declarative Config | 配置外置理念——启发 D-G-01，非直接使用 Kubernetes |
| 12-Factor App §III + §X | Config（配置外置）+ Dev/Prod Parity（开发生产路径一致）——§III 启发 D-G-01a，§X 独立引用 |

---

## 8. 修改条件

- 本标准 `ai_autonomy: immutable_core` → AI **禁止自主修改**
- Owner 审批后，由 Owner 直接修改或 AI 在 Owner 明确指令下修改
- 修改后需同步更新：
  - `scripts/governance/index.md`（如版号变更）
  - AGENTS.md §8.2（如文件名/路径变更）
  - `_registry/catalogs/rule-registry.md`（规则登记条目）

---

## 9. AI 可消费性声明

### 9.1 AI 能否无歧义理解并执行本标准？

**能**。本标准满足以下 AI 可消费性条件：

- ✅ 8 个质量维度均为 **MUST/SHOULD/MAY 枚举条款**——AI 逐项检查即可，无需"理解意图"
- ✅ 每个条款有 **正例/反例代码**（D-A~D-F/D-H）或**可操作判定标准**（D-G）——AI 可以 diff 式对比
- ✅ 专业参考标注给出**具体章节号**（如 PEP 257，不是"PEP 系列"）——AI 可以精确查原文
- ✅ 附录含**自检清单**——AI 可以逐项勾选，机械化执行

### 9.2 最小必读路径（Zero-Memory Restart）

```
新 AI session 接到"创建/修复审计脚本"任务
  → 1. 自动加载 AGENTS.md（已注入）→ §8.2 任务路由
  → 2. 读 scripts/governance/index.md → 发现本标准
  → 3. 读本标准 → D-A~D-H 逐项检查
  → 4. 创建前：§10 自检清单 → 创建后：再次自检
```

### 9.3 Token 预算

本标准全文约 **540 行**（含代码示例），预估 **5000 tokens**。对标 AGENTS.md §8.2 的任务路由设计——这是一个中等规模的标准，AI session 读完后仍有充足 token 用于施工。

---

## 10. 完整性自检清单

> AI 创建新脚本或修复已有脚本时，MUST 逐项勾选。全部 ✅ 后方可交付。

### 编码安全（D-A）
- [ ] D-A-01：文件开头含 `ensure_utf8_stdout()` 或等效 UTF-8 声明
- [ ] D-A-02：所有 `except` 捕获具体异常类型，无裸 `except`
- [ ] D-A-03：无 `shell=True`
- [ ] D-A-04：I/O 操作显式指定 `encoding='utf-8'`（SHOULD，例外需记录）
- [ ] D-A-05：无重复 import

### 类型安全（D-B）
- [ ] D-B-01：所有公共函数含类型注解
- [ ] D-B-02：`main()` 声明 `-> None`
- [ ] D-B-03：`NoReturn` 函数有正确返回类型声明（SHOULD，例外需记录）
- [ ] D-B-04：通过基础 mypy 检查——无 import-not-found 之外的错误（SHOULD，例外需记录）

### 文档规范（D-C）
- [ ] D-C-01：文件开头含模块级 docstring
- [ ] D-C-02：所有公共函数含 Google Style docstring
- [ ] D-C-03：简单函数至少包含一行 docstring（SHOULD，例外需记录）
- [ ] D-C-04：imports 按 stdlib → third-party → local 分组排序

### 架构设计（D-D）
- [ ] D-D-01：每个函数只做一件事
- [ ] D-D-01a：单函数 ≤ 50 行（SHOULD，例外需记录）
- [ ] D-D-02：无模块级有副作用初始化
- [ ] D-D-03：无魔法数字——已提取为命名常量
- [ ] D-D-04：同一概念只在一处定义——无跨脚本规则阈值重复
- [ ] D-D-05：无跨文件复制粘贴逻辑——公共功能提取到 `_shared/`
- [ ] D-D-06：有 `if __name__ == "__main__"` 守卫
- [ ] D-D-07：无本地重定义 `_shared/` 已导出函数/常量
- [ ] D-D-08：无 `os.walk()` + 手动 `EXCLUDE_DIRS` 过滤

### 错误处理（D-E）
- [ ] D-E-01：异常已分级处理
- [ ] D-E-02：异常捕获后有日志/stderr输出（不吞）
- [ ] D-E-03：命令行参数/文件内容已校验合法性
- [ ] D-E-04：子任务失败时脚本优雅降级，输出 PARTIAL report（SHOULD，例外需记录）

### 输出规范（D-F）
- [ ] D-F-01：支持 `--warn-only`
- [ ] D-F-02：使用 POSIX exit codes（0/1/2）
- [ ] D-F-03：输出为结构化格式
- [ ] D-F-04：已注册到 `script_manifest.yaml`
- [ ] D-F-05：stdout（数据）与 stderr（诊断）已分离

### 可维护性（D-G）
- [ ] D-G-01：路径/阈值未硬编码
- [ ] D-G-01a：路径从项目根推导，非绝对路径
- [ ] D-G-02：公共功能提取到 `_shared/`（SHOULD，例外需记录）
- [ ] D-G-03：函数依赖通过参数注入，非隐式引用全局状态（SHOULD，例外需记录）
- [ ] D-G-04：循环内无重复计算（已缓存）
- [ ] D-G-05：使用 argparse 定义命令行参数，非手动解析 sys.argv（SHOULD，例外需记录）
- [ ] D-G-06：代码变换使用无损工具（LibCST），禁止 ast.unparse() 重写文件

### 可测试性（D-H）
- [ ] D-H-01：至少一个 smoke test——`--warn-only` 无异常退出
- [ ] D-H-02：核心检测逻辑有单元测试（SHOULD，例外需记录）
- [ ] D-H-03：测试验证具体行为而非仅验证"不抛异常"（SHOULD，例外需记录）
- [ ] D-H-04：测试彼此隔离——不依赖运行顺序（SHOULD，例外需记录）

**判定规则**：
- 本标准共 **41 条款**：25 MUST + 16 SHOULD
- 所有 MUST 条款 = ✅ → 合格交付
- 任意 MUST 条款 = ❌ → 不合格——AI MUST 修复后方可标记完成
- SHOULD 条款 = ❌ → 需在 Session Log 中记录例外原因

> **AI 快速自检流程**（对应 §4 验收标准）：
> 1. 先执行 §4 的 6 点行为判据——逐条通过命令验证
> 2. 全部 ✅ → 系统健康，无需深入检查
> 3. 任意 ❌ → 回读 §3 对应质量维度（判据表的"对应维度"列指引），按 §10 自检清单逐项排查

---

## 11. 变更记录

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| 1.1.5 | 2026-05-02 | v1.1.5 DeepSeek V4 精准审查 + 穿透性修复。(1) C1 L30 header 版本号 1.1.3→1.1.4（v1.1.4 frontmatter 已更新但 header 遗漏——4 次审查均未发现）。(2) C2 §10 判定规则条款数严重错误——"36 条款：20 MUST + 15 SHOULD + 1 MAY"→"38 条款：22 MUST + 16 SHOULD"（实数为 22M+16S+0MAY，MAY 条款从未存在过，1 MAY 是凭空数字）。(3) C3 §10 自检清单补 D-D-04（"同一概念只在⼀处定义"）——该 MUST 条款从 v1.0.0 起就存在但清单从未勾选，统计遗漏的直接后果。(4) H1 D-B 章节标题与维度表术语不一致——章节写"PEP 484 strict 模式 + mypy 类型检查器"，维度表写"PEP 484 + mypy strict"，统一为后者。(5) H2 D-G-01a 实际应用 v1.1.4 changelog 声称的修改——正文从"§X Dev/Prod Parity"→"§X（Dev/Prod Parity：开发/生产环境路径结构应一致）"。 |
| 1.1.4 | 2026-05-02 | v1.1.4 MiniMax 视角审查 + 专业引用精确化。(1) §1.2 范围描述验证——实际目录 d1_structure~d11_compliance（11 个维度）+ _shared 共享模块，与描述完全一致，确认为正确描述。(2) SCRIPT 域 manifest 注册状态验证——script_manifest.yaml 不注册 SCRIPT 域是正确的（质量标准本身不是被调度执行的脚本），SCRIPT-001 条目在 rule-registry.md 而非 manifest，符合 SSoT 原则。(3) D-G-01a 12-Factor 章节引用修正——"§X Dev/Prod Parity"补充说明为"§X（Dev/Prod Parity：开发/生产环境路径结构应一致）"。(4) Informative 引用表修正——"12-Factor App §V + §X（Build/Release/Run 分离）"→"12-Factor App §III + §X（Config 配置外置 + Dev/Prod Parity）"——§V Build/Run 不是 D-G-01a 的来源，§III Config 才是（配置应外置不硬编码）。 |
| 1.1.3 | 2026-05-02 | v1.1.3 全维度一致性审查 + 判定规则强化。(1) A1 §4 修正前导空格 `" orchestra"`→`"orchestra"`。(2) A2 §5 消费者表 `AGENTS.md §8.2` 变更影响补充——标注 `immutable_core` + Owner 审批约束。(3) A3 §9.1 修正"正例/反例代码"声称——D-G 维度无代码示例，改为"每个条款有可操作的判定标准"。(4) B1 §6 D-FORBID-01 精确化——D-G 无 MUST 条款，枚举改为 "D-A~D-F MUST 条款 + D-G/D-H SHOULD 条款跳过"，判定逻辑同步。(5) B2 §10 自检清单补全——D-B-03/04（NoReturn + mypy）、D-E-04（优雅降级）。(6) B3 D-B 对标维度表修正——"PEP 484 strict + mypy"→"PEP 484 + mypy strict"（strict 是 mypy 标志，不是 PEP 属性）。(7) B4 D-E 对标维度表修正——"ISO 25010 §Reliability"→"ISO 25010 §4.2"（精确章节号）。(8) C1 §10 判定规则补充条款总数声明（36 条款：20 MUST + 15 SHOULD + 1 MAY）。(9) C2 §4 补充 AI 快速自检流程——先走 §4 6 点行为判据，有 ❌ 再回读 §3 + §10。 |
| 1.1.2 | 2026-05-02 | v1.1.2 可执行性审查 + 条款精确化。(1) 修复 §2.2 残留旧版引用——"7维度"→"8维度"（v1.1.0→v1.1.1 升级遗漏）。(2) D-B-04 mypy strict → 降级为基础类型检查（`mypy {script}.py`），strict 模式标为远期目标——实测 strict 在现有代码库产生 import-not-found + dict 泛型参数误报，当前环境不可行。(3) §4 验收标准第3条补充注释——澄清"一键运行全部"（调度系统健康度）与 D-H-01 smoke test（单脚本可运行性）的互补关系，消除"orchestra vs 乐器"歧义。(4) D-H-01 修正措辞——"这是注册的前置条件"→"是注册的隐含前置条件"，避免因果倒置（注册不依赖测试，测试是注册的隐含验证）。(5) D-G-03 补充示例——加"PROJECT_ROOT 应通过参数传入"的具体说明，降低 AI 理解成本。(6) 新增 D-G-05——命令行参数应使用 argparse（SHOULD），禁止手动 sys.argv 解析。(7) §10 自检清单补 D-G-03/D-G-05 勾选项。 |
| 1.1.1 | 2026-05-02 | v1.1.1 一致性修复 + 逻辑补强。(1) 修复 5 处 v1.0.0→v1.1.0 升级遗漏同步：summary/§9.1 "7维度"→"8维度"、§9.2 "D-A~D-G"→"D-A~D-H"、§9 子节编号 8.x→9.x、Token 预算 2500行/3500tok→540行/5000tok、§1.1 目的补"可测试"。(2) 拆分 D-D-01：MUST（单一职责）+ SHOULD（≤50行）分离为 D-D-01 和 D-D-01a。(3) 修复 D-F-05 代码示例：`_scan()` 调用两次→存入变量一次调用。(4) 新增 D-D-06：`if __name__ == "__main__"` 守卫强制条款——无守卫 = 无法 import 测试 = 违反 D-H。 |
| 1.1.0 | 2026-05-02 | v1.1.0 横向对标融合更新。(1) 新增 D-H — **可测试性**（ISTQB + Google Testing Blog TWIMC）：smoke test MUST + 核心逻辑单元测试 SHOULD。(2) 扩展 D-C — 新增 D-C-04 imports 分组排序（PEP 8 §Imports）。(3) 扩展 D-D — 新增 D-D-05 禁止跨脚本复制粘贴逻辑（DRY 强制条款）。(4) 扩展 D-F — 新增 D-F-05 stdout/stderr 分离（12-Factor App §XI）。(5) 扩展 D-G — 新增 D-G-01a 路径从项目根推导（12-Factor App §X）。(6) 新增 §4 **好的脚本系统的可操作验收标准**（6 点行为判据）——AI 无需通读 8 个维度即可自检系统健康度。(7) 扩展 §6 禁止行为 —— D-FORBID-04 跨脚本复制粘贴禁止。(8) 更新 §10 自检清单 —— 8 维度全覆盖。章节号重编号（§4~§10→§5~§11）。 |
| 1.0.0 | 2026-05-02 | 初始创建。(1) 定义 7 个质量维度（D-A~D-G）及 MUST/SHOULD/MAY 条款。(2) 对标 Google Python Style Guide + PEP 484/257/540 + OWASP + Clean Code + ISO 25010。(3) 含 AI 自检清单——AI 创建/修复脚本前逐项勾选。(4) 注册到 rule-registry.md + AGENTS.md §8.2 任务路由。(5) 互补 AGENTS.md §6.5（入库流程）+ §6.7（UTF-8 强制声明）。 |
