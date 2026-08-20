# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/check_vocab_hardcode.py | §gate-vocab
# [MODULE] governance.d3_metadata.check_vocab_hardcode
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] zephyr.governance._shared.constants; _shared.walk
# [CONSUMERS] pre-commit GATE-VOCAB; manual audit
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] AST 扫描检测词表合法值硬编码（变量名匹配 + 值匹配）+ load_vocabulary_values 引用 yaml 存在性 + [STARTUP] 标记值合法性校验；warn-only 起步(exit 0)；DDL 例外白名单；_archive 排除；# noqa: gate-vocab 内联豁免 + noqa 审计输出（治本 2026-06-30，超基线 WARN 不阻断）；检测6：生成器数据库名硬编码（红攻1治本，仅 generators/ 范围，排除 docstring + _common.py）；检测7：commit_gates 测试目录名硬编码（红攻发现2治本，仅 commit_gates/ 范围，排除 docstring，真源 commit_gate_registry.is_test_exempt）；检测8：阈值变量硬编码（ARCH-036 P3-A5，仅 scripts/governance/ 范围，匹配 *THRESHOLD/*DEADLINE/*TIMEOUT/*QUARANTINE/*LIMIT 变量名赋值为数值字面量/数值集合，真源 thresholds.yaml + _get_threshold()，src/zephyr/ 不接入因依赖方向错误）；盲区1治本（2026-07-17）：dict 字面量检测（ast.Dict key 提取 + dict() 调用 + set({...}) 递归）；盲区2治本：检测9 if 语句 ast.Compare 字面量集合（in/not in，min_values=2）；盲区3治本：单字符词表值加载（H/M/L 等，len>=1，原 >=2 漏检 safety_level）；盲区4治本：检测10 return 语句字面量集合（min_values=2）；盲区5治本：_match_vocab_values 全子集阈值（hit_count==len(str_values) 且 ≥ min_values=2，检测4/9/10 共用）替代原 min(3,total)且≥2——覆盖 2 值子集（如 ("draft","active") 2/3 status），单值子集不报（误报率过高）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（无违规或 warn-only）；EXIT_FINDINGS=1（--ci 模式有违规）；EXIT_ERROR=2（脚本异常）
# [TESTS] 手动测试：全量扫描 exit 0；已知违规文件被检出
# [A_module] module_id=MOD-INF-005 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m11-perm-manual-legitimate  M11豁免: 由 pre-commit run_gate_chain 事件自动触发（--ci 模式在案），非人工 manual 运行
"""GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）

检测 src/ 与 scripts/ 下 .py 文件中硬编码的词表合法值集合。
词表合法值必须从 *_vocabulary.yaml 动态加载（yaml.safe_load），
禁止用 list/set/frozenset 字面量复制合法值——同步=复制=多真源=必漂移。

检测逻辑（AST 扫描）：
  1. 变量名匹配 VALID_*_VALUES/STATUSES/TYPES/LEVELS/LAYERS/TTL 等模式
  2. 赋值为字面量集合（list/set/frozenset/tuple）→ 疑似硬编码
  3. 赋值为函数调用（如 _load_xxx_values()）→ 动态加载 → 合规
  4. load_vocabulary_values("xxx.yaml") 调用 → 校验 xxx.yaml 是否存在
  5. 值匹配（v1.3.0）：不限变量名，字面量集合含 3+ 词表值 → 疑似硬编码
  6. _load_xxx 函数体复制 yaml 词表读取逻辑（R4 治本 2026-06-30）：
     新AI 可能写 def _load_my_values(): yaml.safe_load(...) 复制词表加载逻辑，
     赋值给变量时是函数调用（检测3 合规），但函数体本身是复制的（违规）。

模式:
  --warn-only（默认）: print 违规清单，exit 0
  --ci: print 违规清单，有违规则 exit 1（未来 hard block）

Usage::

    # 全量扫描（warn-only，默认）
    python scripts/governance/d3_metadata/check_vocab_hardcode.py

    # CI 模式（有违规则 exit 1）
    python scripts/governance/d3_metadata/check_vocab_hardcode.py --ci
"""

from __future__ import annotations

__manifest__ = """
args: []
description: 'GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）'
dimensions:
- D3
priority: P2
timeout_seconds: 60
warn_only: false
"""


import ast
import re
import sys
from pathlib import Path

import yaml

# ── 路径设置 ──
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)

from _shared.constants import EXCLUDE_DIRS, EXIT_ERROR, EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.walk import iter_files  # noqa: E402
from _shared.yaml_utils import (  # noqa: E402  # D-D-05：词表加载收敛到 SSoT（含批量 #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 2）
    load_all_vocabulary_values,
    load_vocabulary_values,
)

# ── 词表前缀 → YAML 文件名映射（用于输出建议）──
_VOCAB_FILES: dict[str, str] = {
    "TTL": "ttl_vocabulary.yaml",
    "STATUS": "status_vocabulary.yaml",
    "STATUSES": "status_vocabulary.yaml",
    "LAYER": "layer_vocabulary.yaml",
    "LAYERS": "layer_vocabulary.yaml",
    "CATEGORY": "category_vocabulary.yaml",
    "SAFETY": "safety_level_vocabulary.yaml",
    "SAFETY_LEVEL": "safety_level_vocabulary.yaml",
    "STABILITY": "stability_vocabulary.yaml",
    "AUTONOMY": "ai_autonomy_vocabulary.yaml",
    "AI_AUTONOMY": "ai_autonomy_vocabulary.yaml",
    "CLASSIFICATION": "classification_vocabulary.yaml",
    "DOC_TYPE": "doc_type_vocabulary.yaml",
    "DOC_TYPES": "doc_type_vocabulary.yaml",
    "REVIEW_STATUS": "review_status_vocabulary.yaml",
    "RULE_FORM": "rule_form_vocabulary.yaml",
    "VERIFIABILITY": "verifiability_vocabulary.yaml",
    "STARTUP": "startup_vocabulary.yaml",
}

# ── 疑似词表硬编码的变量名模式 ──
# 匹配 VALID/ALLOWED/LEGAL/PERMITTED_*_VALUES/STATUSES/TYPES/LEVELS/LAYERS/TTL/CATEGORIES/CLASSIFICATIONS/LIST/SET
# v1.1.0 增强：增加 ALLOWED/LEGAL/PERMITTED 前缀 + LIST/SET 后缀（覆盖红队绕过 A01/A10）
# v1.2.0 增强：增加 STARTUP 后缀（覆盖 [STARTUP] 标记硬编码漏网——红蓝发现3 治本）
_VALID_VAR_PATTERN = re.compile(
    r"^(VALID|ALLOWED|LEGAL|PERMITTED)_[A-Z_]*?(VALUES|STATUSES|TYPES|LEVELS|LAYERS|TTL|CATEGORIES|CLASSIFICATIONS|LIST|SET|STARTUP)$"
)

# ── [STARTUP] 标记值校验（v1.2.0 新增——红蓝发现3 治本）──
# 扫描 .py 文件头部 [STARTUP] 标记，校验值是否在 startup_vocabulary.yaml 合法值中
_STARTUP_MARKER_PATTERN = re.compile(r"^#\s*\[STARTUP\]\s*(\w+)")

# ── 检测5：_load_xxx 函数体复制 yaml 词表读取逻辑（R4 治本 2026-06-30）──
# 匹配 _load_ 前缀 + 词表相关关键词的函数名（如 _load_ttl_values, _load_legal_values）
# 命中后检查函数体是否包含 yaml.safe_load 调用 → 疑似复制词表加载逻辑
# 合理不收敛的函数（SSoT 不支持的批量/分组模式）加 noqa: gate-vocab 豁免
_VOCAB_LOAD_FUNC_PATTERN = re.compile(
    r"^_load_[a-z_]*?(value|values|vocab|legal|valid|status|ttl|type|layer|safety|stability|autonomy|classification)$"
)

# ── 检测8：阈值变量硬编码（ARCH-036 P3-A5: 阈值数值应从 SSoT 读取）──
# 匹配含 THRESHOLD/DEADLINE/TIMEOUT/QUARANTINE/LIMIT 的变量名，
# 若赋值为数值字面量/数值集合（非 _get_threshold() 调用）→ 疑似硬编码。
# 阈值变量理应从 thresholds.yaml 通过 _get_threshold() 读取，硬编码=第二真源=必漂移。
# 豁免：合理不接入 SSoT 的阈值（如实验性/脚本专用）加 noqa: gate-vocab。
_THRESHOLD_VAR_PATTERN = re.compile(r"^[A-Z_]*?(THRESHOLD|DEADLINE|TIMEOUT|QUARANTINE|LIMIT)[A-Z_]*$")

# ── DDL 例外白名单（SQL CHECK 无法 yaml.safe_load，走 DDL-as-Code 协议）──
_DDL_EXEMPT_FILES: frozenset[str] = frozenset(
    {
        "sqlite_schema.py",
        "depgraph_schema.py",
        "audit_post_sync_commands.py",
    }
)

# ── SSoT 真源文件白名单（治本 2026-06-30 检测5 行为检测）──
# 这些文件是 load_vocabulary_values/load_vocabulary_entries 的真源实现，
# 自身必须用 yaml.safe_load 读取词表——豁免检测5（行为检测）。
# 约束：仅豁免 SSoT 真源文件，禁止豁免消费者。
# #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 1：纳入 check_vocab_hardcode.py 自身——
# 它是批量词表加载（_load_all_vocab_values）的真源实现（SSoT 不支持批量，
# 合理不收敛），守门人是最大违规者（19 次自豁免）属规则盲区。
_SSOT_EXEMPT_FILES: frozenset[str] = frozenset(
    {
        "yaml_utils.py",  # src/zephyr/shared/io/ + scripts/governance/_shared/ 两处真源/re-exporter
        "check_vocab_hardcode.py",  # #ARCH-VOCAB-NOQA-CONVERGENCE-001: 自身批量加载真源
    }
)

# ── noqa 豁免登记表路径（#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 1）──
# 真源：config/governance/noqa_exempt_registry.yaml（YAML）。
# 每个 gate-vocab 豁免标记（行尾 noqa 形式）必须在此登记，否则 GATE-VOCAB 校验失败。
# 基线值 = len(exemptions)，自动从登记表计算（消除硬编码魔数 _NOQA_BASELINE=33）。
_NOQA_REGISTRY_PATH = REPO_ROOT / "config" / "governance" / "noqa_exempt_registry.yaml"

# ── noqa 审计基线 fallback（治本 2026-06-30）──
# #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 1 后基线从 registry 自动计算
# （len(exemptions)），此常量仅作 registry 缺失时的 fallback。
# 防止 ``# noqa: gate-vocab`` 豁免被滥用无限增长——每次 GATE-VOCAB 运行时
# 输出当前 noqa 分布与趋势，新增 noqa 必须在 commit message 说明理由。
# 收敛期约束（AD-GOV-001）：此为审计输出，非新增门禁/reconciler/规则 YAML。
_NOQA_BASELINE_FALLBACK: int = 33


def _load_startup_values(vocab_dir: Path) -> set[str]:
    """从 startup_vocabulary.yaml 动态加载 [STARTUP] 合法值（SSoT 唯一真源）。

    红蓝发现3 治本：startup_vocabulary.yaml 声明"校验器从本文件动态加载"但无脚本实际加载。
    本函数兑现该声明，消除 [STARTUP] 标记零门禁缺口。

    D-D-05 治本（2026-06-30）：收敛到 SSoT ``load_vocabulary_values``（strict=False，
    文件不存在时返回空 set，warn-only 不崩溃）。

    Returns:
        合法值 set[str]；文件不存在时返回空 set（warn-only，不崩溃）。
    """
    return load_vocabulary_values("startup_vocabulary.yaml", vocab_dir=vocab_dir, strict=False)


def _check_startup_marker(source: str, valid_values: set[str]) -> list[tuple[int, str]]:
    """校验 .py 文件头部的 [STARTUP] 标记值是否合法（红蓝发现3 治本）。

    扫描文件头部注释（前 30 行）中的 [STARTUP] 标记，
    校验值是否在 startup_vocabulary.yaml 的合法值中。

    Args:
        source: 文件源码
        valid_values: startup_vocabulary.yaml 的合法值集合

    Returns:
        (行号, 违规描述) 列表（空列表 = 通过或无 [STARTUP] 标记）
    """
    if not valid_values:
        return []
    issues: list[tuple[int, str]] = []
    # 只扫描文件头部注释（前 30 行足够覆盖脚本头锚定区）
    for i, line in enumerate(source.splitlines()[:30], 1):
        m = _STARTUP_MARKER_PATTERN.match(line)
        if m:
            value = m.group(1)
            if value not in valid_values:
                issues.append(
                    (
                        i,
                        f"[STARTUP] 标记值 '{value}' 不在 startup_vocabulary.yaml 合法值中"
                        f"(合法值: {sorted(valid_values)})",
                    )
                )
            break  # 只检查第一个 [STARTUP] 标记
    return issues


def _is_literal_collection(value: ast.expr) -> bool:
    """判断 AST 节点是否为字面量集合（list/set/tuple 字面量，或对字面量参数的 set/frozenset 调用）。

    Returns:
        True 如果是字面量集合（硬编码嫌疑），False 如果是函数调用/动态加载（合规）。
        关键区分：set({...字面量...}) = 硬编码；set(动态调用) = 合规动态加载。

    v1.1.0 增强（覆盖红队绕过 A04/A05）:
        - dict()/list()/tuple() 字面量参数调用 → 硬编码
        - "a,b,c".split(",") 字符串方法产生列表 → 硬编码
        - dict(a=1, b=2) 关键字参数 → 硬编码
    """
    if isinstance(value, (ast.List, ast.Set, ast.Tuple)):
        return True
    # 仅当 set()/frozenset()/dict()/list()/tuple() 的参数本身是字面量集合时才判为字面量硬编码
    # set({"a","b"}) → True（字面量参数）
    # set(_bp_meta.get(...)) → False（动态调用参数，合规）
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
        if value.func.id in ("frozenset", "set", "list", "tuple"):
            if value.args and isinstance(value.args[0], (ast.List, ast.Set, ast.Tuple)):
                return True
            # 无参数或参数非字面量集合 → 动态加载，合规
            return False
        # dict(a=1, b=2) 关键字参数 → 字面量硬编码
        if value.func.id == "dict":
            if value.args and isinstance(value.args[0], (ast.Dict, ast.List, ast.Set, ast.Tuple)):
                return True
            if value.keywords:
                return True
            return False
    # "a,b,c".split(",") → 字符串方法产生列表，硬编码
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute):
        if value.func.attr in ("split", "rsplit", "splitlines"):
            if isinstance(value.func.value, ast.Constant):
                return True
            return False
    return False


def _is_number_literal_or_collection(value: ast.expr) -> bool:
    """判断 AST 节点是否为数值字面量或数值集合（阈值硬编码嫌疑）。

    检测8（ARCH-036 P3-A5）专用：匹配阈值变量名后，判断赋值是否为数值字面量/
    数值集合。函数调用（如 _get_threshold()）= 动态加载 = 合规 → False。

    覆盖：
    - 数值字面量：24, 0.05, 900
    - 数值 dict：{"CRITICAL": 24, "HIGH": 168}（值全为数值）
    - 数值 list/set/tuple：[24, 168, 720]
    - set/frozenset/list/tuple([数值集合]) 调用

    注意：bool 是 int 子类，需排除（True/False 不是阈值）。
    """
    # 数值字面量（排除 bool，因为 bool 是 int 子类）
    if isinstance(value, ast.Constant) and isinstance(value.value, (int, float)) and not isinstance(value.value, bool):
        return True
    # 数值 dict：所有 values 为数值（排除 None 和 bool）
    if isinstance(value, ast.Dict) and value.values:
        numeric_vals = [v for v in value.values if v is not None]
        if numeric_vals and all(
            isinstance(v, ast.Constant) and isinstance(v.value, (int, float)) and not isinstance(v.value, bool)
            for v in numeric_vals
        ):
            return True
        return False
    # 数值 list/set/tuple
    if isinstance(value, (ast.List, ast.Set, ast.Tuple)) and value.elts:
        return all(
            isinstance(e, ast.Constant) and isinstance(e.value, (int, float)) and not isinstance(e.value, bool)
            for e in value.elts
        )
    # set/frozenset/list/tuple([数值集合]) 调用
    if isinstance(value, ast.Call) and isinstance(value.func, ast.Name):
        if value.func.id in ("set", "frozenset", "list", "tuple"):
            if value.args and isinstance(value.args[0], (ast.List, ast.Set, ast.Tuple)):
                return (
                    all(
                        isinstance(e, ast.Constant)
                        and isinstance(e.value, (int, float))
                        and not isinstance(e.value, bool)
                        for e in value.args[0].elts
                    )
                    and len(value.args[0].elts) > 0
                )
    return False


def _load_all_vocab_values(vocab_dir: Path) -> dict[str, set[str]]:
    """加载所有 *_vocabulary.yaml 的合法值，构建 vocab_name → set[value] 映射。

    治本（#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 2）：改为调用 SSoT
    ``load_all_vocabulary_values()``，消除 noqa 豁免——SSoT 现支持批量加载，
    不再需要消费者自己 ``yaml.safe_load + glob``（D-D-05 收敛）。

    用于值匹配检测（检测4）：不限变量名，扫描字面量集合的字符串值，
    若命中数 ≥ 1，标记为疑似硬编码（盲区5 治本：阈值从 ≥2 降到 ≥1）。
    覆盖检测1（变量名匹配）漏检的 DOC_TYPES/CODE_TYPES/TYPE_PRIORITY 等命名。

    Returns:
        {vocab_name: {value, ...}}；vocab_name 不含 _vocabulary.yaml 后缀。
        过滤纯数字值（避免误报）和空串，保留单字符值（盲区3 治本：H/M/L 等需检测）。
        SSoT 返回原始值（含数字/空串），此处后处理过滤（业务策略，不属 SSoT 加载层）。
    """
    raw = load_all_vocabulary_values(vocab_dir=vocab_dir)
    # 后处理：过滤纯数字值（避免误报）和空串，保留单字符值（H/M/L 等需检测）
    result: dict[str, set[str]] = {}
    for vocab_name, values in raw.items():
        filtered = {v for v in values if v and not v.isdigit()}
        if filtered:
            result[vocab_name] = filtered
    return result


def _extract_str_literals(node: ast.expr) -> set[str]:
    """从字面量集合 AST 节点提取所有字符串常量值。

    覆盖 _is_literal_collection 判定为 True 的所有形态：
      - list/set/tuple 字面量：[a, b], {a, b}, (a, b)
      - set/frozenset/list/tuple([...]) 调用
      - "a,b,c".split(",") 字符串方法
    """
    values: set[str] = set()
    if isinstance(node, (ast.List, ast.Set, ast.Tuple)):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                values.add(elt.value)
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        if node.func.id in ("set", "frozenset", "list", "tuple") and node.args:
            inner = node.args[0]
            if isinstance(inner, (ast.List, ast.Set, ast.Tuple)):
                for elt in inner.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        values.add(elt.value)
    elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
        if (
            node.func.attr in ("split", "rsplit")
            and isinstance(node.func.value, ast.Constant)
            and isinstance(node.func.value.value, str)
        ):
            sep = ","
            if node.args and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str):
                sep = node.args[0].value
            values.update(s for s in node.func.value.value.split(sep) if s)
    return values


def _match_vocab_values(
    node_value: ast.expr,
    vocab_values: dict[str, set[str]] | None,
    min_values: int = 2,
) -> tuple[str, int, int] | None:
    """检查字面量集合是否为词表合法值的子集（盲区5 治本）。

    检测4/9/10 共用辅助：检测字面量集合（list/set/tuple/dict）中的词表值硬编码。

    原检测4 阈值 ``≥ min(3, total) 且 ≥ 2`` 漏检 2 值子集（如 ``("draft","active")``
    仅 2/3 status，原阈值要求 ≥ min(3,3)=3）。新阈值要求整个集合为词表子集
    （``hit_count == len(str_values) 且 ≥ min_values``），覆盖 2 值子集的同时
    避免部分匹配误报（如 ``("accepted", "active")`` 仅 1/2 命中不报，
    因 "accepted" 不在 status_vocabulary values 中）。

    Args:
        node_value: AST 节点（赋值值 / comparator / return value）。
        vocab_values: ``{vocab_name: set[value]}`` 映射；None 跳过。
        min_values: 集合最少字符串值数量（默认 2——单值匹配误报率过高，
            任何单字符串都可能巧合命中某词表；2+ 值全子集匹配才是硬编码强信号）。

    Returns:
        ``(vocab_name, hit_count, total)`` 如果匹配；``None`` 如果不匹配。
    """
    if not vocab_values or not _is_literal_collection(node_value):
        return None
    str_values = _extract_str_literals(node_value)
    if not str_values or len(str_values) < min_values:
        return None
    for vocab_name, vocab_set in vocab_values.items():
        hit_count = len(str_values & vocab_set)
        # 盲区5 治本：全子集阈值（hit_count == len(str_values) 且 ≥ min_values）
        if hit_count >= min_values and hit_count == len(str_values):
            return (vocab_name, hit_count, len(vocab_set))
    return None


def _check_file(
    filepath: Path,
    vocab_dir: Path,
    startup_values: set[str] | None = None,
    vocab_values: dict[str, set[str]] | None = None,
) -> list[tuple[int, str]]:
    """检查单个 Python 文件的词表硬编码与 yaml 引用存在性 + [STARTUP] 标记值校验。

    Args:
        filepath: Python 文件绝对路径。
        vocab_dir: 词表 YAML 所在目录（用于校验 load_vocabulary_values 引用存在性）。
        startup_values: startup_vocabulary.yaml 的合法值集合（None 表示跳过 [STARTUP] 校验）。
        vocab_values: 所有词表的 {vocab_name: set[value]} 映射（None 表示跳过值匹配检测）。

    Returns:
        (行号, 违规描述) 列表（空列表 = 通过）。

    内联豁免：行尾 ``# noqa: gate-vocab`` 可豁免该行检测（标准 lint 做法）。
    豁免行仍会记录到 issues 但标记为 [EXEMPTED]，warn-only 模式不阻断。
    """
    issues: list[tuple[int, str]] = []

    # _archive 排除
    if "_archive" in filepath.parts:
        return issues

    # DDL 例外
    if filepath.name in _DDL_EXEMPT_FILES:
        return issues

    try:
        source = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return [(0, "cannot read file")]

    # 检测3：[STARTUP] 标记值合法性校验（v1.2.0 新增——红蓝发现3 治本）
    if startup_values:
        startup_issues = _check_startup_marker(source, startup_values)
        issues.extend(startup_issues)

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return []  # 语法错误的文件跳过（非词表问题）

    for node in ast.walk(tree):
        # 检测1：词表硬编码（VALID_* 赋值为字面量集合）
        # v1.1.0 增强：同时检测 ast.NamedExpr（walrus 操作符，覆盖红队绕过 A11）
        # v1.3.1 增强：同时检测 ast.AnnAssign（带类型注解赋值 VAR: list[str] = [...]，覆盖红队绕过 A12）
        if isinstance(node, (ast.Assign, ast.NamedExpr, ast.AnnAssign)):
            # Assign.targets 是列表；NamedExpr/AnnAssign.target 是单个 Name
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            # AnnAssign 可能无赋值（如 x: int），跳过
            if node.value is None:
                continue
            name_match_reported = False
            for target in targets:
                if not isinstance(target, ast.Name):
                    continue
                var_name = target.id
                match = _VALID_VAR_PATTERN.match(var_name)
                if not match:
                    continue

                # 字面量赋值 = 硬编码嫌疑；函数调用 = 动态加载 = 合规
                if not _is_literal_collection(node.value):
                    continue

                # gate-vocab 内联豁免检查（避免以 # noqa: 开头被审计误识别为指令）
                if _has_noqa_exempt(source, node.lineno):
                    continue  # 豁免，不报

                # 提取词表前缀，推断对应 YAML 文件名
                suffix = match.group(2)  # VALUES / STATUSES / TYPES / LEVELS / LAYERS / TTL / LIST / SET
                # 从变量名提取前缀：VALID_TTL_VALUES → TTL，VALID_LAYERS → LAYERS
                # v1.1.0: 前缀可能是 VALID/ALLOWED/LEGAL/PERMITTED
                prefix_part = var_name.split("_", 1)[1]  # 去掉前缀（VALID/ALLOWED/...）
                prefix_part = prefix_part[: -(len(suffix) + 1)]  # 去掉 _SUFFIX 后缀
                if not prefix_part:
                    prefix_part = suffix  # VALID_VALUES → VALUES
                vocab_file = _VOCAB_FILES.get(prefix_part) or _VOCAB_FILES.get(suffix)
                if not vocab_file:
                    vocab_file = f"{prefix_part.lower()}_vocabulary.yaml"

                issues.append(
                    (
                        node.lineno,
                        f"{var_name} 硬编码词表合法值(应从 {vocab_file} 动态加载)",
                    )
                )
                name_match_reported = True

            # 检测4：值匹配（v1.3.0 新增——不限变量名，覆盖 DOC_TYPES/CODE_TYPES/TYPE_PRIORITY 等漏检命名）
            # 仅当检测1未报时进行，避免与检测1重复。
            # 盲区5 治本：全子集阈值（hit_count == len(str_values) 且 ≥ min_values=2），
            # 原 min(3,total) 且 ≥2 漏检 2 值子集（如 ("draft","active") 2/3 status）。
            # min_values=2：单值子集（如 ("draft",)）不报——任何单字符串都可能巧合命中某词表，
            # 单值匹配误报率过高（实测 140+ 误报）；2+ 值全子集匹配才是硬编码强信号。
            if not name_match_reported and vocab_values and not _has_noqa_exempt(source, node.lineno):
                match = _match_vocab_values(node.value, vocab_values, min_values=2)
                if match:
                    vocab_name, hit_count, total = match
                    issues.append(
                        (
                            node.lineno,
                            f"字面量集合含 {hit_count}/{total} 个 {vocab_name} 词表值"
                            f"(疑似硬编码，应从 {vocab_name}_vocabulary.yaml 动态加载)",
                        )
                    )

            # 检测8：阈值变量硬编码（ARCH-036 P3-A5: 阈值数值应从 SSoT 读取）
            # 仅对 scripts/governance/ 范围生效——thresholds.yaml 是脚本治理系统的 SSoT，
            # src/zephyr/ 的阈值属于不同系统（依赖方向错误，不应接入 scripts SSoT）。
            # 匹配 *THRESHOLD/*DEADLINE/*TIMEOUT/*QUARANTINE/*LIMIT 变量名，
            # 若赋值为数值字面量/数值集合（非 _get_threshold() 调用）→ 疑似硬编码。
            if (
                "scripts" in filepath.parts
                and "governance" in filepath.parts
                and not name_match_reported
                and not _has_noqa_exempt(source, node.lineno)
            ):
                for target in targets:
                    if not isinstance(target, ast.Name):
                        continue
                    var_name = target.id
                    if not _THRESHOLD_VAR_PATTERN.match(var_name):
                        continue
                    if not _is_number_literal_or_collection(node.value):
                        continue
                    issues.append(
                        (
                            node.lineno,
                            f"{var_name} 硬编码阈值数值(应从 thresholds.yaml 通过 _get_threshold() 读取)",
                        )
                    )
                    break  # 一个变量名命中即可，避免重复报
        # 检测2：load_vocabulary_values("xxx.yaml") 引用的词表文件存在性
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id != "load_vocabulary_values":
                continue
            if not node.args:
                continue
            first = node.args[0]
            # 仅校验字面量字符串参数（变量参数无法静态分析）
            if not (isinstance(first, ast.Constant) and isinstance(first.value, str)):
                continue
            # noqa 豁免
            if _has_noqa_exempt(source, node.lineno):
                continue
            vocab_file = first.value
            p = Path(vocab_file)
            if not p.is_absolute():
                p = vocab_dir / vocab_file
            if not p.exists():
                issues.append(
                    (
                        node.lineno,
                        f"load_vocabulary_values 引用的词表文件不存在: {vocab_file}",
                    )
                )
        # 检测5：函数体复制 yaml 词表读取逻辑（R4 治本 2026-06-30，行为检测 v2）
        # 治本（2026-06-30 红蓝对抗）：废弃函数名正则门控（漏检 _get_valid_layers/
        # _load_doc_type_suffixes 等非标准命名），改为行为检测——任何函数体内含
        # yaml.safe_load 且引用 vocabulary 相关路径/字符串 → 疑似复制词表加载。
        # SSoT 真源文件（yaml_utils.py）白名单豁免。
        # 合理不收敛的函数（SSoT 不支持的批量/分组模式）加 noqa: gate-vocab 豁免。
        elif isinstance(node, ast.FunctionDef):
            # SSoT 真源文件豁免（自身必须用 yaml.safe_load 读词表）
            if filepath.name in _SSOT_EXEMPT_FILES:
                continue
            func_name = node.name
            # 识别 docstring 节点（函数体第一个 Expr 的 Constant），遍历时跳过——
            # 避免 docstring 中提到 "vocabulary" 字样触发误报（如 load_contract 的 docstring）
            docstring_const = None
            if (
                node.body
                and isinstance(node.body[0], ast.Expr)
                and isinstance(node.body[0].value, ast.Constant)
                and isinstance(node.body[0].value.value, str)
            ):
                docstring_const = node.body[0].value
            # 行为检测：函数体内是否含 yaml.safe_load 调用
            has_yaml_load = False
            has_vocab_ref = False
            for child in ast.walk(node):
                if child is docstring_const:
                    continue  # 跳过 docstring
                if (
                    isinstance(child, ast.Call)
                    and isinstance(child.func, ast.Attribute)
                    and child.func.attr == "safe_load"
                    and isinstance(child.func.value, ast.Name)
                    and child.func.value.id == "yaml"
                ):
                    has_yaml_load = True
                # 检测 vocabulary 相关字符串字面量（路径/文件名含 vocab/vocabulary）
                # 注意：不检测变量名——避免误报引用 vocab_values 参数的同步函数
                if isinstance(child, ast.Constant) and isinstance(child.value, str):
                    low = child.value.lower()
                    if "vocab" in low or "vocabulary" in low:
                        has_vocab_ref = True
            if not has_yaml_load or not has_vocab_ref:
                continue  # 非词表 yaml 加载，跳过
            # noqa 豁免
            if _has_noqa_exempt(source, node.lineno):
                continue
            issues.append(
                (
                    node.lineno,
                    f"def {func_name}() 函数体含 yaml.safe_load 读取词表逻辑"
                    f"(疑似复制词表加载，应使用 load_vocabulary_values SSoT 函数)",
                )
            )
        # 检测9：if 语句中字面量集合（盲区2 治本）
        # 检测 ast.Compare（如 if x not in {"draft", "active"}）中的字面量集合。
        # 原检测仅查 Assign，漏检 if 语句中的 in/not in 字面量集合硬编码。
        # min_values=2：if x in ("draft",): 等价 if x == "draft": 属业务逻辑，不报；
        # 同检测4 rationale，单值匹配误报率过高。
        elif isinstance(node, ast.Compare):
            if vocab_values and not _has_noqa_exempt(source, node.lineno):
                for comparator in node.comparators:
                    match = _match_vocab_values(comparator, vocab_values, min_values=2)
                    if match:
                        vocab_name, hit_count, total = match
                        issues.append(
                            (
                                node.lineno,
                                f"if 语句字面量集合含 {hit_count}/{total} 个 {vocab_name} 词表值"
                                f"(疑似硬编码，应从 {vocab_name}_vocabulary.yaml 动态加载)",
                            )
                        )
                        break  # 一个 comparator 命中即可，避免重复报
        # 检测10：return 语句中字面量集合（盲区4 治本）
        # 检测 ast.Return 中的字面量集合（如 return ("draft", "active")）。
        # 原检测仅查赋值语句，漏检 return 语句中的字面量集合硬编码。
        # min_values=2：return ("draft",) 等价 return "draft" 属业务逻辑，不报。
        elif isinstance(node, ast.Return) and node.value is not None:
            if vocab_values and not _has_noqa_exempt(source, node.lineno):
                match = _match_vocab_values(node.value, vocab_values, min_values=2)
                if match:
                    vocab_name, hit_count, total = match
                    issues.append(
                        (
                            node.lineno,
                            f"return 语句字面量集合含 {hit_count}/{total} 个 {vocab_name} 词表值"
                            f"(疑似硬编码，应从 {vocab_name}_vocabulary.yaml 动态加载)",
                        )
                    )

    # 检测6：生成器数据库名硬编码（治本 2026-06-30，红攻1治本）
    # 生成器产物里的数据库名必须从 _common.DB_DISPLAY_NAME 引用，禁止硬编码字面量。
    # 范围：仅 scripts/governance/d5_architecture/generators/*.py（排除 _common.py 真源定义）
    # 排除：docstring（模块/函数/类 body[0]）+ noqa: gate-vocab 豁免
    # 收敛期约束（AD-GOV-001）：扩展现有 _check_file 检测，非新增门禁。
    generators_dir = REPO_ROOT / "scripts" / "governance" / "d5_architecture" / "generators"
    try:
        is_generator = filepath.is_relative_to(generators_dir)
    except (ValueError, AttributeError):
        is_generator = str(filepath).startswith(str(generators_dir))
    if is_generator and filepath.name != "_common.py":
        # 收集 docstring 节点 id（排除检测，避免误报模块/函数/类说明文本）
        docstring_ids: set[int] = set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if n.body and isinstance(n.body[0], ast.Expr):
                    v = n.body[0].value
                    if isinstance(v, ast.Constant) and isinstance(v.value, str):
                        docstring_ids.add(id(v))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if "depgraph (PostgreSQL)" not in node.value:
                continue
            if id(node) in docstring_ids:
                continue  # docstring 豁免
            if _has_noqa_exempt(source, node.lineno):
                continue
            issues.append(
                (
                    node.lineno,
                    "硬编码数据库名 'depgraph (PostgreSQL)'（应 from _common import DB_DISPLAY_NAME 引用常量）",
                )
            )

    # 检测7：commit_gates 测试目录名硬编码（治本 2026-06-30，红攻发现2治本）
    # commit_gates 中 tests/ 豁免必须从 commit_gate_registry.is_test_exempt 引用，
    # 禁止硬编码 "tests/" 字面量——真源漂移风险（新AI可能直接硬编码绕过 SSoT，
    # 导致 Windows 路径归一化等治本逻辑被绕过）。
    # 范围：仅 src/zephyr/gov_enforcement/commit_gates/*.py
    # 排除：docstring（模块/函数/类 body[0]）+ noqa: gate-vocab 豁免
    # 收敛期约束（AD-GOV-001）：扩展现有 _check_file 检测，非新增门禁。
    # 真源：src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py 的 TEST_EXEMPT_PREFIXES/is_test_exempt。
    commit_gates_dir = REPO_ROOT / "src" / "zephyr" / "gov_enforcement" / "commit_gates"
    try:
        is_commit_gate = filepath.is_relative_to(commit_gates_dir)
    except (ValueError, AttributeError):
        is_commit_gate = str(filepath).startswith(str(commit_gates_dir))
    if is_commit_gate:
        gate_docstring_ids: set[int] = set()
        for n in ast.walk(tree):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if n.body and isinstance(n.body[0], ast.Expr):
                    v = n.body[0].value
                    if isinstance(v, ast.Constant) and isinstance(v.value, str):
                        gate_docstring_ids.add(id(v))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
                continue
            if "tests/" not in node.value:
                continue
            if id(node) in gate_docstring_ids:
                continue  # docstring 豁免
            if _has_noqa_exempt(source, node.lineno):
                continue
            issues.append(
                (
                    node.lineno,
                    "硬编码测试目录名 'tests/'"
                    "（应 from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import is_test_exempt 引用 SSoT）",
                )
            )

    return issues


def _has_noqa_exempt(source: str, lineno: int) -> bool:
    """检查指定行是否有 ``noqa: gate-vocab`` 内联豁免。

    Args:
        source: 文件源码
        lineno: 1-based 行号

    Returns:
        True 如果该行有 noqa: gate-vocab 注释
    """
    lines = source.splitlines()
    if lineno < 1 or lineno > len(lines):
        return False
    return "# noqa: gate-vocab" in lines[lineno - 1]


def _collect_noqa_exemptions(source: str) -> list[tuple[int, str]]:
    """收集文件中所有 ``# noqa: gate-vocab`` 豁免指令的行号和理由注释。

    治本（2026-06-30）：noqa 审计机制——防止豁免被滥用无限增长。
    每次 GATE-VOCAB 运行时累计输出 noqa 分布，趋势可见。
    约束（向内收）：扩展现有 main() 输出，不新建 reconciler/YAML。

    精确识别（v1 治本）：用 ``tokenize`` 模块识别真正的 COMMENT token，
    自动排除 docstring/字符串字面量/文档嵌套引用中的 ``noqa: gate-vocab``
    文字——避免审计自身脚本文档时误报。

    Args:
        source: 文件源码

    Returns:
        ``[(行号, 理由注释), ...]``；理由注释为 noqa 指令后的说明（可空）。
    """
    import io
    import tokenize

    exemptions: list[tuple[int, str]] = []
    directive_prefix = "noqa: gate-vocab"
    try:
        tokens = list(tokenize.generate_tokens(io.StringIO(source).readline))
    except tokenize.TokenError:
        return []
    for tok in tokens:
        if tok.type != tokenize.COMMENT:
            continue
        # tok.string 形如 "# noqa: gate-vocab  R4 豁免：批量加载"
        after_hash = tok.string[1:].lstrip()
        if not after_hash.startswith(directive_prefix):
            continue  # 非指令形式（如文档引用 "# ... # noqa 内联豁免"）
        reason = after_hash[len(directive_prefix) :].strip()
        exemptions.append((tok.start[0], reason))
    return exemptions


# ── noqa 豁免登记表加载（#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 1）──
# 真源：config/governance/noqa_exempt_registry.yaml。基线值 = len(exemptions)。
# 未登记的 # noqa: gate-vocab = 违规（在审计输出标记 [UNREGISTERED]，
# --ci 模式 exit 1）。这消除开环系统——每个 noqa 必须有结构化登记+理由。


def _load_noqa_registry() -> dict | None:
    """加载 noqa 豁免登记表（#ARCH-VOCAB-NOQA-CONVERGENCE-001）。

    真源：``config/governance/noqa_exempt_registry.yaml``（YAML）。
    本函数是 registry→audit 的唯一加载点，禁止其他模块复制加载逻辑。

    Returns:
        ``{'meta':..., 'categories':[...], 'exemptions':[{file,line,category,reason}]}``
        ``None`` 如果文件不存在或解析失败（warn-only，不崩溃——registry 缺失时
        退化为 fallback 基线 33，审计仍运行但无法校验未登记）。
    """
    try:
        data = yaml.safe_load(_NOQA_REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def _noqa_baseline(registry: dict | None) -> int:
    """基线值 = ``len(exemptions)``，自动从登记表计算（消除硬编码魔数）。

    #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 1：原 ``_NOQA_BASELINE=33`` 是硬编码
    魔数，治本降低豁免后无人更新——趋势永远显示正值。改为从 registry 自动计算
    后，每次治本降低 noqa 必须同步删除 registry 条目，基线自动下降，趋势始终=0。

    Args:
        registry: ``_load_noqa_registry()`` 返回的 dict；None 时退化为 fallback。

    Returns:
        基线值（registry 有效时 = ``len(exemptions)``，否则 = ``_NOQA_BASELINE_FALLBACK``）。
    """
    if registry and isinstance(registry.get("exemptions"), list):
        return len(registry["exemptions"])
    return _NOQA_BASELINE_FALLBACK


def _registered_exemption_keys(registry: dict | None) -> set[tuple[str, int]]:
    """提取登记表中所有 ``(file, line)`` 键，用于精确匹配。

    file 路径用正斜杠规范化（registry 中统一用 ``/``，实际扫描可能返回 ``\\``）。

    Args:
        registry: ``_load_noqa_registry()`` 返回的 dict；None 时返回空 set。

    Returns:
        ``{(file_path_with_slash, line), ...}``；空 set 如果 registry 缺失。
    """
    if not registry or not isinstance(registry.get("exemptions"), list):
        return set()
    keys: set[tuple[str, int]] = set()
    for entry in registry["exemptions"]:
        if not isinstance(entry, dict):
            continue
        file_path = entry.get("file")
        line_no = entry.get("line")
        if not isinstance(file_path, str) or not isinstance(line_no, int):
            continue
        # 规范化为正斜杠（跨平台一致）
        keys.add((file_path.replace("\\", "/"), line_no))
    return keys


def _registered_reason_map(registry: dict | None) -> dict[str, set[str]]:
    """提取登记表中 ``{file -> {reason, ...}}`` 映射，用于行号漂移时的 fallback 匹配。

    #ARCH-VOCAB-NOQA-CONVERGENCE-001：100% AI 开发场景下代码频繁修改，行号
    漂移是常态——精确 ``(file, line)`` 匹配会误报。本函数提供 reason fallback：
    当 ``(file, line)`` 不匹配时，用 ``(file, reason)`` 匹配（reason 是业务语义，
    比行号稳定）。reason 规范化：strip + lstrip('# ')，与 registry 生成脚本一致。

    Args:
        registry: ``_load_noqa_registry()`` 返回的 dict；None 时返回空 dict。

    Returns:
        ``{file_with_slash: {normalized_reason, ...}}``；空 dict 如果 registry 缺失。
    """
    if not registry or not isinstance(registry.get("exemptions"), list):
        return {}
    result: dict[str, set[str]] = {}
    for entry in registry["exemptions"]:
        if not isinstance(entry, dict):
            continue
        file_path = entry.get("file")
        reason = entry.get("reason")
        if not isinstance(file_path, str) or not isinstance(reason, str):
            continue
        norm_file = file_path.replace("\\", "/")
        norm_reason = reason.strip().lstrip("# ").strip()
        result.setdefault(norm_file, set()).add(norm_reason)
    return result


def _is_noqa_registered(
    file_rel_slash: str,
    lineno: int,
    reason: str,
    line_keys: set[tuple[str, int]],
    reason_map: dict[str, set[str]],
) -> bool:
    """检查实际 noqa 是否在 registry 登记（混合匹配：line 精确 + reason fallback）。

    匹配优先级：
        1. ``(file, line)`` 精确匹配——最可靠，行号未漂移时命中
        2. ``(file, reason)`` 匹配——行号漂移时 fallback（reason 是业务语义更稳定）

    Args:
        file_rel_slash: 文件相对路径（正斜杠规范化）
        lineno: noqa 行号
        reason: noqa 理由注释（已 strip）
        line_keys: ``_registered_exemption_keys()`` 返回的精确键集合
        reason_map: ``_registered_reason_map()`` 返回的 file→reasons 映射

    Returns:
        True 如果任一匹配命中；False 如果均未命中（未登记 noqa = 违规）。
    """
    # 1. 精确 (file, line) 匹配
    if (file_rel_slash, lineno) in line_keys:
        return True
    # 2. Fallback (file, reason) 匹配——行号漂移时使用
    norm_reason = reason.strip().lstrip("# ").strip()
    if norm_reason and file_rel_slash in reason_map:
        if norm_reason in reason_map[file_rel_slash]:
            return True
    return False


def main() -> int:
    """Entry point: parse args, run logic, return exit code."""
    import argparse

    parser = argparse.ArgumentParser(description="GATE-VOCAB: 词表合法值硬编码检测（trae_060 §2）")
    parser.add_argument(
        "--warn-only",
        action="store_true",
        default=True,
        help="仅警告不阻断（默认，exit 0 即使有违规）",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI 模式，有违规则 exit 1（未来硬阻断用）",
    )
    parser.add_argument(
        "--files",
        nargs="+",
        default=None,
        help="只扫描指定文件（绝对路径），不扫描 scan_dirs。供 vocab_hardcode_gate subprocess 调用。",
    )
    args = parser.parse_args()

    # 词表 YAML 真源目录（用于校验 load_vocabulary_values 引用存在性）
    vocab_dir = REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies"

    # 加载 [STARTUP] 合法值（红蓝发现3 治本：兑现 startup_vocabulary.yaml "校验器动态加载"声明）
    startup_values = _load_startup_values(vocab_dir)

    # 加载所有词表合法值（v1.3.0 新增——检测4 值匹配，覆盖变量名漏检）
    vocab_values = _load_all_vocab_values(vocab_dir)

    # 排除 _archive 目录
    exclude = EXCLUDE_DIRS | {"_archive", "tests"}

    all_issues: list[tuple[Path, int, str]] = []
    # noqa 审计累计（治本 2026-06-30）：防止豁免被滥用无限增长
    all_noqa: list[tuple[Path, int, str]] = []
    checked = 0

    if args.files:
        # --files 模式：只扫描指定文件（供 gate subprocess 调用）
        py_files = [Path(f) for f in args.files if f.endswith(".py")]
    else:
        # 默认模式：扫描 src/zephyr/ 和 scripts/
        scan_dirs = [
            REPO_ROOT / "src" / "zephyr",
            REPO_ROOT / "scripts",
        ]
        py_files = []
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            py_files.extend(
                iter_files(
                    scan_dir,
                    extensions=frozenset({".py"}),
                    exclude_dirs=exclude,
                )
            )

    for filepath in py_files:
        checked += 1
        issues = _check_file(filepath, vocab_dir, startup_values, vocab_values)
        for lineno, issue in issues:
            all_issues.append((filepath, lineno, issue))
        # noqa 审计：收集本文件的豁免行
        try:
            src = filepath.read_text(encoding="utf-8")
            for lineno, reason in _collect_noqa_exemptions(src):
                all_noqa.append((filepath, lineno, reason))
        except (OSError, UnicodeDecodeError):
            pass

    # 输出违规
    if all_issues:
        for filepath, lineno, issue in all_issues:
            try:
                rel = filepath.relative_to(REPO_ROOT)
            except ValueError:
                rel = filepath
            print(f"  WARN: {rel}:{lineno} {issue}")
        print(f"\nFOUND: {len(all_issues)} vocabulary hardcode issue(s) in {checked} files checked")
    else:
        print(f"OK: No vocabulary hardcode issues found ({checked} files checked)")

    # ── noqa 审计摘要（治本 2026-06-30）──
    # #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 1：基线从 registry 自动计算
    # （len(exemptions)），未登记 noqa 标记 [UNREGISTERED]——闭环系统：
    # 每个 noqa 必须在 config/governance/noqa_exempt_registry.yaml 登记，
    # 否则 --ci 模式 exit 1。registry 缺失时退化为 fallback 基线 33。
    registry = _load_noqa_registry()
    registered_keys = _registered_exemption_keys(registry)
    reason_map = _registered_reason_map(registry)
    unregistered = _print_noqa_audit(all_noqa, checked, registry, registered_keys, reason_map)

    # --ci 模式：未登记 noqa = 违规（exit 1）——闭环强制登记
    if args.ci and (all_issues or unregistered):
        return EXIT_FINDINGS
    return EXIT_PASS  # warn-only


def _print_noqa_audit(
    all_noqa: list[tuple[Path, int, str]],
    checked: int,
    registry: dict | None = None,
    registered_keys: set[tuple[str, int]] | None = None,
    reason_map: dict[str, set[str]] | None = None,
) -> list[tuple[Path, int, str]]:
    """输出 ``# noqa: gate-vocab`` 豁免审计摘要 + 校验登记表一致性。

    治本（2026-06-30）：noqa 审计机制——防止豁免被滥用无限增长。
    #ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 1：基线从 registry 自动计算
    （``len(exemptions)``），未登记 noqa 标记 ``[UNREGISTERED]``——
    闭环系统（每个 noqa 必须结构化登记，否则违规）。

    匹配策略（行号漂移免疫）：``_is_noqa_registered()`` 用混合匹配——
    ``(file, line)`` 精确 + ``(file, reason)`` fallback。100% AI 开发
    场景下代码频繁修改，行号漂移是常态，reason fallback 确保业务语义
    稳定的豁免不会因行号变化而误报。

    Args:
        all_noqa: 所有文件的 noqa 收集结果 ``[(filepath, lineno, reason), ...]``
        checked: 本次扫描的 .py 文件总数（用于密度计算）
        registry: ``_load_noqa_registry()`` 返回的 dict；None 时退化为 fallback 基线
        registered_keys: ``_registered_exemption_keys(registry)`` 返回的
            ``(file_with_slash, line)`` 集合；None 时跳过未登记校验
        reason_map: ``_registered_reason_map(registry)`` 返回的 file→reasons 映射；
            None 时跳过 reason fallback

    Returns:
        未登记的 noqa 列表 ``[(filepath, lineno, reason), ...]``；
        空列表 = 全部登记或 registered_keys 为 None。
    """
    baseline = _noqa_baseline(registry)
    total = len(all_noqa)
    files_with_noqa = len({fp for fp, _, _ in all_noqa})
    trend = total - baseline
    trend_str = f"+{trend}" if trend > 0 else str(trend) if trend < 0 else "0"
    density = (total / checked * 100) if checked else 0.0

    registry_status = "registry" if registry else "fallback"
    print(
        f"\nNOQA AUDIT: {total} exemptions across {files_with_noqa} files "
        f"(baseline={baseline} via {registry_status}, trend={trend_str}, density={density:.2f}%)"
    )

    # 校验未登记 noqa（#ARCH-VOCAB-NOQA-CONVERGENCE-001 Phase 1 闭环核心）
    unregistered: list[tuple[Path, int, str]] = []
    if registered_keys is not None:
        for fp, lineno, reason in all_noqa:
            try:
                rel = str(fp.relative_to(REPO_ROOT)).replace("\\", "/")
            except ValueError:
                rel = str(fp).replace("\\", "/")
            if not _is_noqa_registered(rel, lineno, reason, registered_keys, reason_map or {}):
                unregistered.append((fp, lineno, reason))
        if unregistered:
            print(f"\n  [UNREGISTERED] {len(unregistered)} 个 noqa 未在 registry 登记：")
            for fp, lineno, reason in unregistered:
                try:
                    rel = fp.relative_to(REPO_ROOT)
                except ValueError:
                    rel = fp
                reason_display = reason if reason else "(无理由注释)"
                print(f"    {rel}:{lineno} {reason_display}")
            print("  必须在 config/governance/noqa_exempt_registry.yaml 登记，")
            print("  或删除该 noqa（治本：扩展 SSoT 函数消除豁免需求）。")

    # 按文件分组输出（仅当有豁免时）
    if all_noqa:
        from collections import defaultdict

        by_file: dict[Path, list[tuple[int, str]]] = defaultdict(list)
        for fp, lineno, reason in all_noqa:
            by_file[fp].append((lineno, reason))
        # 按文件内 noqa 数量降序输出（热点文件优先）
        for fp, items in sorted(by_file.items(), key=lambda kv: -len(kv[1])):
            try:
                rel = fp.relative_to(REPO_ROOT)
            except ValueError:
                rel = fp
            print(f"  {rel} ({len(items)}):")
            for lineno, reason in items:
                reason_display = reason if reason else "(无理由注释)"
                print(f"    L{lineno}: {reason_display}")

    # 趋势告警（warn-only，不阻断；闭环由 UNREGISTERED 校验承担）
    if trend > 0:
        print(f"\n  [WARN] noqa 总数 {total} > 基线 {baseline}（趋势 +{trend}）")
        print("  新增 # noqa: gate-vocab 必须先在 registry 登记 + commit message 说明豁免理由，")
        print("  或通过治本（如扩展 SSoT 函数支持批量/分组模式）消除豁免需求。")
    elif trend < 0:
        print(
            f"\n  [OK] noqa 总数 {total} < 基线 {baseline}（趋势 {trend}）"
            f"——治本见效，请同步删除 registry 中已退役的条目以降低基线。"
        )

    return unregistered


if __name__ == "__main__":
    sys.exit(main())


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def check_file(
    filepath,
    vocab_dir,
    startup_values: set[str] | None = None,
    vocab_values: dict[str, set[str]] | None = None,
) -> list[tuple[int, str]]:
    """公共接口：check_file（Stage 4 公共化）。

    #ARCH-VOCAB-NOQA-CONVERGENCE-001：startup_values/vocab_values 加默认值 None，
    与 ``_check_file`` 签名对齐——向后兼容旧调用方（仅传 filepath/vocab_dir），
    修复 test_check_vocab_hardcode.py 7 处 pre-existing 接口不匹配失败。
    """
    return _check_file(filepath, vocab_dir, startup_values, vocab_values)
