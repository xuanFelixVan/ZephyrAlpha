# [BLUEPRINT] MOD-INF-005 | scripts/governance/architecture_health_dashboard.py | §architecture-health-dashboard
# [MODULE] scripts.governance.architecture_health_dashboard
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] post-commit hook; AI session 冷启动; 治理基线追踪
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 11 项架构健康度指标自动化检测基线（architecture_debt_registry.md §六 第0期）；每项指标独立函数；复用现有检测脚本（subprocess 解析输出）；warn-only 起步（exit 0，仅记录基线）；YAML SSoT 原则；不破坏现有 151 个治理组件
# [MODIFY-GUARD] 指标清单变更 MUST 同步 architecture_debt_registry.md §六 + 本文件 METRICS 列表
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（始终，warn-only 基线模式）；单检测器异常降级为 error 字段不中断其余
# [TESTS] 手动测试：独立运行输出 11 项指标；与手动调研基线 3193 可对账
# [A_module] module_id=MOD-GOV-architecture_health_dashboard | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""architecture_health_dashboard.py — 架构健康度仪表盘（自动化检测基线）

对标 architecture_debt_registry.md §六 第0期（L5660-5667）：
  建立自动化检测基线，每次 commit 自动生成架构健康度指标，替代手动调研。

病根（前文 3193 个违规点的 5 个病根）：
  - SSoT 真源唯一性（211）：159 对文件复制 + 41 处词表硬编码
  - 永久系统触发（32）：15 处时间触发 + 6 处空 handler
  - 新 AI 可发现性（55）：40 个 GATE 无反查 + 10 个关键能力未注册
  - DB 全景图深度（17）：949 真孤儿未监控 + 死代码
  - 文档引用断裂（26）：136 处引用断裂 + 三方对齐 9 个

11 项指标（目标值均为 0，当前总值 3193 手动调研基线）：
  1. 词表硬编码违规数      — 复用 check_vocab_hardcode.py
  2. manual-only 永久脚本数 — [STARTUP] manual + [TTL] permanent 组合违规
  3. 重复簇函数数          — AST 函数体哈希聚类（>1 成员的簇）
  4. GATE 未登记 capability 数 — commit_gates/ 文件 vs capability 注册表
  5. 文件复制对数          — 复用 check_code_duplication.py
  6. reconciler 健康度     — post-commit reconciler 数（目标收敛 3-5）
  7. 死代码数              — orphan 模块（src/ 未被任何 import 引用）
  8. 路径漂移数            — 复用 check_contract_physical_path.py
  9. 三方对齐违规数        — 复用 validate_three_way_consistency.py
  10. 时间触发残留数       — 永久脚本扫描 time-trigger 模式
  11. PG域引用一致性违规数 — 连 PG 查幽灵域/空字符串脏数据/FK违规

设计原则：
  - 复用优先：现有检测脚本通过 subprocess 调用，解析 stdout 计数
  - 独立降级：单检测器异常不中断其余，记录到 error 字段
  - SSoT 对账：每项指标可追溯到 architecture_debt_registry.md 病根
  - warn-only 起步：第0期仅记录基线，第1期才转 hard block

集成点：
  - 独立运行：python scripts/governance/architecture_health_dashboard.py
  - post-commit reconciler 自动触发：GitCommitGateway commit 完成后由
    make_architecture_health_reconciler（reconciliation_registry.py）自动调用
    --snapshot 保存基线快照到 data/architecture_health/
  - 非阻断：第0期不阻断 commit（第1期 AST 门禁才阻断）

Usage::

    # 独立运行（控制台摘要 + JSON 快照）
    python scripts/governance/architecture_health_dashboard.py

    # 仅 JSON 输出（供下游消费）
    python scripts/governance/architecture_health_dashboard.py --json

    # 保存历史快照
    python scripts/governance/architecture_health_dashboard.py --snapshot
"""

from __future__ import annotations

__manifest__ = """
args:
  - --json
  - --snapshot
  - --metric
description: 架构健康度仪表盘（11 项指标自动化检测基线，architecture_debt_registry.md §六 第0期）
dimensions:
- D5
priority: P1
timeout_seconds: 180
warn_only: true
"""

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "_shared").exists()))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
# 确保 zephyr 包可导入（_shared.constants 依赖 zephyr.shared.io.paths）——
# 使脚本自包含：手动运行与 post-commit reconciler subprocess 均无需外部 PYTHONPATH=src
# 治本 #AD-HEALTH-001：reconciler subprocess 未设 PYTHONPATH 导致 dashboard 启动即 ModuleNotFoundError
_SRC_DIR = str(next(p for p in _SCRIPT_DIR.parents if (p / "src" / "zephyr").exists()) / "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from _shared.constants import EXCLUDE_DIRS, EXIT_PASS, REPO_ROOT  # noqa: E402
from _shared.encoding import ensure_utf8_stdout  # noqa: E402
from _shared.file_utils import atomic_write_safe  # noqa: E402
from _shared.walk import iter_files  # noqa: E402
from _shared.yaml_utils import load_yaml_safe  # noqa: E402

ensure_utf8_stdout()

# ── 路径常量 ──────────────────────────────────────────────────────────────
SRC_ZEPHYR = REPO_ROOT / "src" / "zephyr"
SCRIPTS_GOVERNANCE = REPO_ROOT / "scripts" / "governance"
COMMIT_GATES_DIR = SRC_ZEPHYR / "gov_enforcement" / "commit_gates"
CAPABILITY_REGISTRY = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "capability_canonical_file_registry.yaml"
)
OUTPUT_DIR = REPO_ROOT / "data" / "architecture_health"

# 手动调研基线（architecture_debt_registry.md L5667：当前总值 3193）
# 各项基线为手动调研派生，用于对账自动化检测覆盖度
MANUAL_BASELINE_TOTAL = 3193


# ── 工具函数 ──────────────────────────────────────────────────────────────

def _run_script(script_path: Path, args: list[str] | None = None, timeout: int = 120) -> tuple[int, str, str]:
    """运行治理脚本，返回 (exit_code, stdout, stderr)。

    统一 cwd=REPO_ROOT，捕获输出供解析。超时降级为 error。

    治本 #AD-HEALTH-002：子进程 env 显式注入 PYTHONPATH=src，确保子脚本
    （check_vocab_hardcode.py 等）能 `import zephyr.*`，否则子进程静默
    ModuleNotFoundError 返回 0 计数，dashboard 误报"已治理"。
    parent sys.path 修改不会继承到 subprocess env，必须显式传 env。
    """
    cmd = [sys.executable, str(script_path)] + (args or [])
    child_env = {**os.environ, "PYTHONPATH": str(REPO_ROOT / "src")}
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(REPO_ROOT),
            env=child_env,
            timeout=timeout,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"timeout after {timeout}s"
    except Exception as e:  # noqa: BLE001 — 降级不中断
        return -2, "", f"run failed: {e}"


def _parse_count(pattern: str, text: str, default: int = 0) -> int:
    """从文本中正则提取首个整数计数。"""
    m = re.search(pattern, text)
    if m:
        try:
            return int(m.group(1))
        except (ValueError, IndexError):
            return default
    return default


def _make_metric(
    metric_id: str,
    name: str,
    count: int,
    details: list[str] | None = None,
    source: str = "",
    error: str = "",
) -> dict:
    """构造单项指标结果 dict。"""
    return {
        "metric_id": metric_id,
        "name": name,
        "count": count,
        "target": 0,
        "details": (details or [])[:20],  # 截断避免输出过大
        "source": source,
        "error": error,
    }


# ── 指标 1：词表硬编码违规数 ──────────────────────────────────────────────

def metric_01_vocab_hardcode() -> dict:
    """词表硬编码违规数——复用 check_vocab_hardcode.py。

    病根：SSoT 真源唯一性 211 中的 41 处词表硬编码。
    检测：subprocess 调用，解析 "FOUND: N vocabulary hardcode issue(s)"。
    """
    script = SCRIPTS_GOVERNANCE / "d3_metadata" / "check_vocab_hardcode.py"
    code, out, err = _run_script(script, ["--warn-only"], timeout=120)
    if code < 0:
        return _make_metric("M01", "词表硬编码违规数", 0, error=err, source=str(script.name))
    combined = out + err
    count = _parse_count(r"FOUND:\s*(\d+)\s*vocabulary hardcode", combined)
    # 采样违规（前 20 行 WARN）
    details = [
        line.strip() for line in combined.splitlines()
        if line.strip().startswith("WARN:") or line.strip().startswith("  WARN:")
    ][:20]
    return _make_metric("M01", "词表硬编码违规数", count, details, script.name)


# ── 指标 2：manual-only 永久脚本数 ────────────────────────────────────────

_STARTUP_RE = re.compile(r"^#\s*\[STARTUP\]\s*(\S+)", re.MULTILINE)
_TTL_RE = re.compile(r"^#\s*\[TTL\]\s*(\S+)", re.MULTILINE)


def metric_02_manual_only_permanent() -> dict:
    """manual-only 永久脚本数——[STARTUP] manual + [TTL] permanent 组合违规。

    病根：永久系统全自动触发（铁律）——永久系统必须自动触发/运行/维护/关闭。
    manual-only 永久脚本=永久存在但需手动触发，违反全自动铁律。
    检测：扫描 scripts/governance/ 下 .py 文件头部 [STARTUP]/[TTL] 标记。
    """
    exclude = EXCLUDE_DIRS | {"_archive", "tests", "__pycache__"}
    py_files = iter_files(SCRIPTS_GOVERNANCE, extensions=frozenset({".py"}), exclude_dirs=exclude)
    violations: list[str] = []
    for fp in py_files:
        try:
            # 只读头部 30 行（标记锚定区）
            source = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        sm = _STARTUP_RE.search(source)
        tm = _TTL_RE.search(source)
        if not sm or not tm:
            continue
        startup = sm.group(1).strip()
        ttl = tm.group(1).strip()
        if startup.lower() == "manual" and ttl.lower() == "permanent":
            try:
                rel = fp.relative_to(REPO_ROOT)
            except ValueError:
                rel = fp
            violations.append(f"{rel} [STARTUP]={startup} [TTL]={ttl}")
    return _make_metric("M02", "manual-only 永久脚本数", len(violations), violations, "inline")


# ── 指标 3：重复簇函数数 ──────────────────────────────────────────────────

def _normalize_function_body(node: ast.FunctionDef) -> str:
    """归一化函数体为可比较字符串——剥离 docstring/注释/空白/变量名。

    用于函数级重复检测：相同逻辑不同变量名视为重复簇。
    """
    # 移除 docstring（body[0] 若为 Expr(Constant str)）
    body = list(node.body)
    if body and isinstance(body[0], ast.Expr):
        if isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
            body = body[1:]
    if not body:
        return ""
    # AST dump 归一化（去掉位置信息），用类型结构签名
    try:
        return ast.dump(ast.Module(body=body, type_ignores=[]), annotate_fields=False)
    except Exception:  # noqa: BLE001
        return ""


def metric_03_duplicate_function_clusters() -> dict:
    """重复簇函数数——AST 函数体哈希聚类。

    病根：SSoT 真源唯一性 211 中的 159 对文件复制（含函数级重复）。
    检测：解析 src/zephyr/ 下 .py，对每个函数体归一化后哈希，聚类统计 >1 成员的簇。
    注：归一化剥离变量名/字面量差异，捕获"复制后改个名"的重复。
    """
    exclude = EXCLUDE_DIRS | {"tests", "__pycache__"}
    py_files = iter_files(SRC_ZEPHYR, extensions=frozenset({".py"}), exclude_dirs=exclude)
    hash_to_funcs: dict[str, list[str]] = defaultdict(list)
    for fp in py_files:
        try:
            source = fp.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(fp))
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # 跳过短函数（<5 行体），避免 getter/setter 误报
            body_len = sum(1 for _ in ast.walk(node)) - 1
            if body_len < 8:
                continue
            norm = _normalize_function_body(node)
            if len(norm) < 60:  # 太短不聚类
                continue
            h = hashlib.md5(norm.encode("utf-8")).hexdigest()  # noqa: S324 — 聚类非安全用途
            hash_to_funcs[h].append(f"{rel}:{node.name}() L{node.lineno}")
    clusters = {h: funcs for h, funcs in hash_to_funcs.items() if len(funcs) > 1}
    details: list[str] = []
    for funcs in sorted(clusters.values(), key=lambda x: -len(x))[:20]:
        details.append(f"簇({len(funcs)}): " + " | ".join(funcs[:3]))
    return _make_metric("M03", "重复簇函数数", len(clusters), details, "inline-AST")


# ── 指标 4：GATE 未登记 capability 数 ─────────────────────────────────────

def metric_04_gate_unregistered_capability() -> dict:
    """GATE 未登记 capability 数——commit_gates/ 文件 vs capability 注册表。

    病根：新 AI 可发现性 55 中的 40 个 GATE 无反查。
    检测：commit_gates/ 下真实 gate .py 文件（含 gate_id= 或 GateSpec( 标记，
    排除 gate_repo.py 等 DAO）basename(无 .py) 若不在 capability 注册表
    的 capability_id/aliases 中，则未登记反查。
    """
    # 加载 capability 注册表
    reg = load_yaml_safe(CAPABILITY_REGISTRY) or {}
    known_caps: set[str] = set()
    for entry in reg.get("capabilities", []) or []:
        if not isinstance(entry, dict):
            continue
        cid = entry.get("capability_id", "")
        if cid:
            known_caps.add(cid)
        for alias in entry.get("aliases", []) or []:
            if isinstance(alias, str):
                known_caps.add(alias)
    # 收集 commit_gates/ 文件
    if not COMMIT_GATES_DIR.exists():
        return _make_metric("M04", "GATE 未登记 capability 数", 0, error="commit_gates/ 不存在", source="inline")
    gate_files = sorted(COMMIT_GATES_DIR.glob("*.py"))
    violations: list[str] = []
    for fp in gate_files:
        if fp.name == "__init__.py":
            continue
        # 排除非 gate 文件（如 gate_repo.py 是 DAO，不是 gate）
        # 真实 gate 文件有 make_*() 工厂函数 return GateSpec(...)；DAO/工具文件无此模式
        try:
            content = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "return GateSpec(" not in content:
            continue  # 非 gate 文件，跳过
        stem = fp.stem  # basename 无 .py
        # 标准化：去 _gate 后缀
        normalized = re.sub(r"_gate$", "", stem)
        # 检查 stem / normalized 是否在已知 capability 中
        if stem in known_caps or normalized in known_caps:
            continue
        # 宽松匹配：capability_id 含 stem 子串
        if any(stem in c or normalized in c for c in known_caps):
            continue
        violations.append(f"{fp.name} (stem={stem}) 未在 capability_canonical_file_registry.yaml 登记")
    return _make_metric("M04", "GATE 未登记 capability 数", len(violations), violations, "inline")


# ── 指标 5：文件复制对数 ──────────────────────────────────────────────────

def metric_05_file_copy_pairs() -> dict:
    """文件复制对数——复用 check_code_duplication.py。

    病根：SSoT 真源唯一性 211 中的 159 对文件复制。
    检测：subprocess 调用，解析 "CODE DUPLICATIONS: N"。
    """
    script = SCRIPTS_GOVERNANCE / "d5_architecture" / "checkers" / "check_code_duplication.py"
    code, out, err = _run_script(script, ["--warn-only", "--threshold", "0.8"], timeout=120)
    if code < 0:
        return _make_metric("M05", "文件复制对数", 0, error=err, source=script.name)
    combined = out + err
    count = _parse_count(r"CODE DUPLICATIONS:\s*(\d+)", combined)
    details = [
        line.strip() for line in combined.splitlines()
        if line.strip() and not line.strip().startswith("CODE DUPLICATIONS")
        and "|" in line and not line.startswith("-")
    ][:20]
    return _make_metric("M05", "文件复制对数", count, details, script.name)


# ── 指标 6：reconciler 健康度 ─────────────────────────────────────────────

def metric_06_reconciler_health() -> dict:
    """reconciler 健康度——post-commit reconciler 数（目标收敛 3-5）。

    病根：治理层臃肿——17 个 post-commit reconciler 应收敛为 3-5 个 pre-commit 阻断
    （architecture_debt_registry.md §六 第3期 L5696）。
    检测：扫描 src/zephyr/governance/ 与 scripts/governance/ 下 .py，
    计数实际 reconciler 注册调用点（``.register`` + ``ReconcilerSpec`` 组合，排除 registry 定义文件自身）。
    健康度 = 当前 post-commit reconciler 注册数（>5 视为债务，目标 3-5）。
    """
    exclude = EXCLUDE_DIRS | {"tests", "__pycache__"}
    registry_file = "reconciliation_registry.py"  # ReconcilerSpec 类定义文件，非注册点
    violations: list[str] = []
    scan_dirs = [SRC_ZEPHYR / "governance", SCRIPTS_GOVERNANCE]
    # 实际注册调用模式：.register( 后跟 ReconcilerSpec(
    register_pattern = re.compile(r"\.register\(\s*ReconcilerSpec\s*\(", re.MULTILINE)
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        py_files = iter_files(scan_dir, extensions=frozenset({".py"}), exclude_dirs=exclude)
        for fp in py_files:
            if fp.name == registry_file:
                continue
            try:
                source = fp.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            matches = register_pattern.findall(source)
            if not matches:
                continue
            try:
                rel = fp.relative_to(REPO_ROOT)
            except ValueError:
                rel = fp
            spec_count = len(matches)
            violations.append(f"{rel} ({spec_count} spec)")
    count = sum(int(re.search(r"\((\d+)", v).group(1)) for v in violations) if violations else 0
    return _make_metric("M06", "reconciler 健康度(post-commit数)", count, violations, "inline")


# ── 指标 7：死代码数 ──────────────────────────────────────────────────────

def metric_07_dead_code() -> dict:
    """死代码数——orphan 模块（src/ 未被任何 import 引用）。

    病根：DB 全景图深度 17 中的死代码 + 5.136(11) + 5.159(9)。
    检测：AST 解析 src/zephyr/ 下 .py 的 import 语句，收集被引用的模块名/符号名，
    若某模块 basename 不被任何 import 引用且非入口，则为 orphan。
    排除 __init__.py / __main__.py / conftest.py / setup.py / _ 前缀私有模块（按相对导入）。
    """
    exclude = EXCLUDE_DIRS | {"tests", "__pycache__"}
    py_files = iter_files(SRC_ZEPHYR, extensions=frozenset({".py"}), exclude_dirs=exclude)
    all_modules: dict[str, Path] = {}
    all_trees: list[tuple[Path, ast.AST | None, str]] = []
    for fp in py_files:
        if fp.name in ("__init__.py", "__main__.py", "conftest.py", "setup.py"):
            continue
        try:
            src = fp.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=str(fp))
        except (OSError, UnicodeDecodeError, SyntaxError):
            tree = None
            src = ""
        all_modules[fp.stem] = fp
        all_trees.append((fp, tree, src))
    # AST 精确解析 import：收集模块路径末段 + import 的符号名
    imported_names: set[str] = set()
    for _, tree, _ in all_trees:
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name:
                        imported_names.add(alias.name.split(".")[-1])
            elif isinstance(node, ast.ImportFrom):
                # from X import Y, Z → X 末段 + Y/Z 均收集（Y/Z 可能是子模块）
                if node.module:
                    imported_names.add(node.module.split(".")[-1])
                for alias in node.names:
                    if alias.name and alias.name != "*":
                        imported_names.add(alias.name)
    # 入口模块（含 if __name__ == "__main__"）不算 orphan
    entry_pattern = re.compile(r'if\s+__name__\s*==\s*["\']__main__["\']')
    for fp, _, src in all_trees:
        if entry_pattern.search(src):
            imported_names.add(fp.stem)
    orphans: list[str] = []
    for stem, fp in sorted(all_modules.items()):
        if stem in imported_names:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        orphans.append(str(rel))
    return _make_metric("M07", "死代码数(orphan模块)", len(orphans), orphans, "inline")


# ── 指标 8：路径漂移数 ────────────────────────────────────────────────────

def metric_08_path_drift() -> dict:
    """路径漂移数——复用 check_contract_physical_path.py。

    病根：cross_layer_contracts.yaml physical_path 指向连字符目录（Python 无法 import）。
    检测：subprocess 调用，解析 "违规=N"。
    """
    script = SCRIPTS_GOVERNANCE / "d5_architecture" / "checkers" / "check_contract_physical_path.py"
    code, out, err = _run_script(script, ["--warn-only"], timeout=60)
    if code < 0:
        return _make_metric("M08", "路径漂移数", 0, error=err, source=script.name)
    combined = out + err
    count = _parse_count(r"违规=(\d+)", combined)
    details = [
        line.strip() for line in combined.splitlines()
        if line.strip().startswith("  ") and ":" in line and "physical_path" in line
    ][:20]
    return _make_metric("M08", "路径漂移数", count, details, script.name)


# ── 指标 9：三方对齐违规数 ────────────────────────────────────────────────

def metric_09_three_way_alignment() -> dict:
    """三方对齐违规数——复用 validate_three_way_consistency.py。

    病根：三方对齐与规则一致性 9 个（frontmatter vs blockquote vs registry）。
    检测：subprocess 调用，解析 "N 个三方不一致" 或 stderr 计数。
    """
    script = (
        SCRIPTS_GOVERNANCE / "d5_architecture" / "validators" / "validate_three_way_consistency.py"
    )
    code, out, err = _run_script(script, ["--warn-only"], timeout=60)
    if code < 0:
        return _make_metric("M09", "三方对齐违规数", 0, error=err, source=script.name)
    combined = out + err
    count = _parse_count(r"(\d+)\s*个三方不一致", combined)
    if count == 0:
        # 兜底：从分类计数求和
        nums = re.findall(r"(?:≠|不一致):?\s*(\d+)", combined)
        if nums:
            count = sum(int(n) for n in nums)
    details = [
        line.strip() for line in combined.splitlines()
        if line.strip().startswith("[") and "≠" in line
    ][:20]
    return _make_metric("M09", "三方对齐违规数", count, details, script.name)


# ── 指标 10：时间触发残留数 ───────────────────────────────────────────────

# 时间触发模式：永久脚本中出现以下模式=违反"事件触发"铁律
_TIME_TRIGGER_PATTERNS = [
    re.compile(r"\bwhile\s+True\s*:.*?time\.sleep", re.DOTALL),  # while True + sleep 轮询
    re.compile(r"schedule\.(every|\.run_pending)", re.IGNORECASE),  # schedule 库
    re.compile(r"\bcron\b", re.IGNORECASE),  # cron 引用
    re.compile(r"threading\.Timer\b"),  # Timer 定时
    re.compile(r"APScheduler|BackgroundScheduler", re.IGNORECASE),  # APScheduler
    re.compile(r"time\.sleep\s*\(\s*\d{3,}", re.IGNORECASE),  # 长睡眠（>=100s，疑似轮询间隔）
]


def metric_10_time_trigger_residuals() -> dict:
    """时间触发残留数——永久脚本扫描 time-trigger 模式。

    病根：永久系统触发 32 中的 15 处时间触发——永久系统必须事件触发（铁律）。
    检测：扫描 [TTL]=permanent 或 task_bound（但被声明为永久系统）的脚本，
    若源码含 time-trigger 模式（schedule/cron/while True+sleep/Timer/长sleep），则为残留。
    """
    exclude = EXCLUDE_DIRS | {"_archive", "tests", "__pycache__"}
    # 扫描范围：scripts/governance/（治理系统永久脚本）+ src/zephyr/（runtime 永久系统）
    scan_dirs = [SCRIPTS_GOVERNANCE, SRC_ZEPHYR]
    violations: list[str] = []
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        py_files = iter_files(scan_dir, extensions=frozenset({".py"}), exclude_dirs=exclude)
        for fp in py_files:
            try:
                source = fp.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            # 必须是永久系统（[TTL]=permanent 或 [STARTUP]=daemon/imported 的运行时系统）
            tm = _TTL_RE.search(source)
            if not tm or tm.group(1).strip().lower() != "permanent":
                continue
            sm = _STARTUP_RE.search(source)
            if sm and sm.group(1).strip().lower() == "manual":
                continue  # manual 脚本不计入时间触发（已在 M02 统计）
            # 检测 time-trigger 模式
            hit_patterns: list[str] = []
            for pat in _TIME_TRIGGER_PATTERNS:
                if pat.search(source):
                    hit_patterns.append(pat.pattern[:30])
            if hit_patterns:
                try:
                    rel = fp.relative_to(REPO_ROOT)
                except ValueError:
                    rel = fp
                violations.append(f"{rel} 命中: {','.join(hit_patterns)}")
    return _make_metric("M10", "时间触发残留数", len(violations), violations, "inline")


# ── 指标 11：PG 域引用一致性违规数 ─────────────────────────────────────────

def metric_11_pg_domain_consistency() -> dict:
    """PG depgraph 域引用一致性违规数——直接连 PG 查询。

    病根：DB 全景图深度 17 中的域引用一致性——9 张含 domain_id 列的表
    可能存在幽灵域（引用 domains 表中不存在的域）、空字符串脏数据、FK 违规。
    检测：动态发现含 domain_id/from_domain/to_domain/source_domain 列的表，
    统计幽灵域 + 空字符串脏数据 + arch_directory_tree FK 违规。
    PG 连接失败时降级为 error 不中断其余指标。
    """
    try:
        from _shared.constants import get_depgraph_pg_connection
    except ImportError as e:
        return _make_metric("M11", "PG域引用一致性违规数", 0, error=f"import failed: {e}", source="pg_depgraph")

    conn = None
    cur = None
    try:
        conn = get_depgraph_pg_connection(autocommit=True)
        cur = conn.cursor()
        violations: list[str] = []
        ghost_count = 0
        empty_str_count = 0

        # 1. 动态发现含域引用列的表
        cur.execute(
            """
            SELECT t.table_name, c.column_name
            FROM information_schema.columns c
            JOIN information_schema.tables t
              ON c.table_name = t.table_name AND t.table_schema = 'public'
            WHERE t.table_type = 'BASE TABLE'
              AND c.column_name IN ('domain_id', 'from_domain', 'to_domain', 'source_domain')
              AND t.table_name NOT LIKE '%%_backup_%%'
            ORDER BY t.table_name, c.column_name
            """
        )
        tables: dict[str, list[str]] = {}
        for r in cur.fetchall():
            tables.setdefault(r["table_name"], []).append(r["column_name"])

        # 2. 逐表逐列检查幽灵域 + 空字符串脏数据
        for tbl, cols in tables.items():
            for col in cols:
                if col == "target_domains":
                    continue
                # 幽灵域（排除 NULL 和空字符串）
                cur.execute(
                    f"""SELECT DISTINCT {col} AS d FROM {tbl}
                    WHERE {col} IS NOT NULL AND {col} != ''
                      AND {col} NOT IN (SELECT domain_id FROM domains)"""
                )
                ghosts = [row["d"] for row in cur.fetchall()]
                if ghosts:
                    ghost_count += len(ghosts)
                    violations.extend(f"{tbl}.{col} 幽灵域: {g}" for g in ghosts[:5])
                # 空字符串脏数据
                cur.execute(f"SELECT COUNT(*) AS n FROM {tbl} WHERE {col} = ''")
                n_empty = cur.fetchone()["n"]
                if n_empty > 0:
                    empty_str_count += n_empty
                    violations.append(f"{tbl}.{col} 空字符串脏数据: {n_empty}条")

        # 3. arch_directory_tree FK 违规（有 FK 约束，验证无违规）
        cur.execute(
            """SELECT COUNT(*) AS n FROM arch_directory_tree
            WHERE domain_id IS NOT NULL
              AND domain_id NOT IN (SELECT domain_id FROM domains)"""
        )
        fk_violations = cur.fetchone()["n"]
        if fk_violations > 0:
            violations.append(f"arch_directory_tree FK违规: {fk_violations}条")

        total = ghost_count + empty_str_count + fk_violations
        return _make_metric("M11", "PG域引用一致性违规数", total, violations, "pg_depgraph")
    except Exception as e:  # noqa: BLE001 — PG 连接失败降级不中断
        return _make_metric("M11", "PG域引用一致性违规数", 0, error=f"pg query failed: {e}", source="pg_depgraph")
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# ── 仪表盘主逻辑 ──────────────────────────────────────────────────────────

# 11 项指标注册表（id → 检测函数）
METRICS: list[tuple[str, str, callable]] = [
    ("M01", "词表硬编码违规数", metric_01_vocab_hardcode),
    ("M02", "manual-only 永久脚本数", metric_02_manual_only_permanent),
    ("M03", "重复簇函数数", metric_03_duplicate_function_clusters),
    ("M04", "GATE 未登记 capability 数", metric_04_gate_unregistered_capability),
    ("M05", "文件复制对数", metric_05_file_copy_pairs),
    ("M06", "reconciler 健康度(post-commit数)", metric_06_reconciler_health),
    ("M07", "死代码数(orphan模块)", metric_07_dead_code),
    ("M08", "路径漂移数", metric_08_path_drift),
    ("M09", "三方对齐违规数", metric_09_three_way_alignment),
    ("M10", "时间触发残留数", metric_10_time_trigger_residuals),
    ("M11", "PG域引用一致性违规数", metric_11_pg_domain_consistency),
]


def run_all_metrics(selected: list[str] | None = None) -> dict:
    """运行全部（或选定）指标检测，返回仪表盘结果 dict。

    Args:
        selected: 选定的 metric_id 列表（如 ["M01", "M05"]），None 表示全部。

    Returns:
        仪表盘结果 dict（含 timestamp/metrics/total/manual_baseline）。
    """
    metrics_results: list[dict] = []
    for mid, name, fn in METRICS:
        if selected and mid not in selected:
            continue
        try:
            result = fn()
        except Exception as e:  # noqa: BLE001 — 单检测器异常降级不中断
            result = _make_metric(mid, name, 0, error=f"detector raised: {e}", source="inline")
        metrics_results.append(result)
    total = sum(m["count"] for m in metrics_results)
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "dashboard": "architecture_health",
        "phase": "第0期-自动化检测基线",
        "metrics": metrics_results,
        "total_auto": total,
        "manual_baseline_total": MANUAL_BASELINE_TOTAL,
        "note": (
            "自动化检测基线（第0期）。total_auto 为自动化检出总数；"
            "manual_baseline_total=3193 为手动调研基线。"
            "二者差异源于自动化覆盖度（部分病根需 AST 门禁第1期才覆盖）。"
        ),
    }


def format_console_report(result: dict) -> str:
    """格式化控制台摘要报告。"""
    lines = [
        "=" * 78,
        "ZephyrAlpha 架构健康度仪表盘（第0期 - 自动化检测基线）",
        f"生成时间: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}",
        "真源: architecture_debt_registry.md §六 L5660-5667",
        "=" * 78,
        "",
        f"{'ID':<5} {'指标':<32} {'当前值':>8} {'目标':>6} {'来源':<18} {'状态':<8}",
        "-" * 78,
    ]
    for m in result["metrics"]:
        status = "OK" if m["count"] == 0 else ("ERR" if m["error"] else "DEBT")
        lines.append(
            f"{m['metric_id']:<5} {m['name']:<32} {m['count']:>8} {m['target']:>6} "
            f"{m['source']:<18} {status:<8}"
        )
    lines.append("-" * 78)
    lines.append(f"{'自动化检出合计':<38} {result['total_auto']:>8} {'':>6} {'':<18}")
    lines.append(f"{'手动调研基线':<38} {result['manual_baseline_total']:>8} {'':>6} {'':<18}")
    lines.append("")
    # 错误提示
    errors = [m for m in result["metrics"] if m["error"]]
    if errors:
        lines.append("[WARN] 以下检测器异常（降级为 0，需排查）:")
        for m in errors:
            lines.append(f"  {m['metric_id']} {m['name']}: {m['error']}")
        lines.append("")
    lines.append("对账说明：自动化检测覆盖度 < 手动调研（部分病根需 AST 门禁第1期才覆盖）。")
    lines.append("目标：所有指标 → 0（第1期 AST 门禁阻断 + 第2期批量修复）。")
    lines.append("=" * 78)
    return "\n".join(lines)


def main() -> int:
    """入口：解析参数，运行检测，输出报告。"""
    parser = argparse.ArgumentParser(
        description="架构健康度仪表盘（11 项指标自动化检测基线，architecture_debt_registry.md §六 第0期）"
    )
    parser.add_argument("--json", action="store_true", help="仅输出 JSON（供下游消费）")
    parser.add_argument("--snapshot", action="store_true", help="保存历史快照到 data/architecture_health/")
    parser.add_argument("--metric", nargs="*", help="仅运行指定指标（如 M01 M05）")
    args = parser.parse_args()

    selected = args.metric if args.metric else None
    result = run_all_metrics(selected)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(format_console_report(result))
        # 控制台模式下也打印采样违规
        for m in result["metrics"]:
            if m["details"]:
                print(f"\n[{m['metric_id']}] {m['name']} 采样违规:")
                for d in m["details"][:5]:
                    print(f"  - {d}")
                if len(m["details"]) > 5:
                    print(f"  ... 还有 {len(m['details']) - 5} 条")

    if args.snapshot:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        snapshot_path = OUTPUT_DIR / f"dashboard_{ts}.json"
        atomic_write_safe(snapshot_path, json.dumps(result, ensure_ascii=False, indent=2))
        if not args.json:
            print(f"\n快照已保存: {snapshot_path.relative_to(REPO_ROOT)}")
        # 同时更新 latest.json（供下游 always 读取最新）
        latest_path = OUTPUT_DIR / "latest.json"
        atomic_write_safe(latest_path, json.dumps(result, ensure_ascii=False, indent=2))

    return EXIT_PASS  # warn-only 基线模式，始终 exit 0


if __name__ == "__main__":
    sys.exit(main())
