# [BLUEPRINT] MOD-INF-005 | scripts/governance/architecture_health_dashboard.py | §architecture-health-dashboard
# [MODULE] scripts.governance.architecture_health_dashboard
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS] post-commit hook; AI session 冷启动; 治理基线追踪
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 30 项架构健康度指标自动化检测基线（ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四 第0期）；每项指标独立函数；复用现有检测脚本（subprocess 解析输出）；warn-only 起步（exit 0，仅记录基线）；YAML SSoT 原则；不破坏现有 151 个治理组件；M15 depgraph新鲜度与 GATE-DEPGRAPH-FRESHNESS 同阈值（#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3.3）；M16 治本进度新鲜度与 GATE-REMEDIATION-PROGRESS 同阈值（#ARCH-GOV-CONVERGENCE-META Phase 3.1）；M17 规则感知缺口追踪 Phase 3.5 paired_gate_id 补齐进度（#ARCH-GOV-CONVERGENCE-META Phase 3.2a）；M20 trae_060 §5 快照漂移数追踪 Phase 3.4b 病根1 治本（baseline vs live snapshot drift）；M21 5病根×3要素覆盖缺口数追踪 Phase 3.6 病根治本闭环（persistence+discoverability+enforceability，target=0 全 15 cell 覆盖）
# [MODIFY-GUARD] 指标清单变更 MUST 同步 ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四 + 本文件 METRICS 列表
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT_PASS=0（始终，warn-only 基线模式）；单检测器异常降级为 error 字段不中断其余
# [TESTS] 手动测试：独立运行输出 30 项指标；与手动调研基线 3193 可对账
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""architecture_health_dashboard.py — 架构健康度仪表盘（自动化检测基线）

对标 ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四 第0期：
  建立自动化检测基线，每次 commit 自动生成架构健康度指标，替代手动调研。

病根（前文 3193 个违规点的 5 个病根）：
  - SSoT 真源唯一性（211）：159 对文件复制 + 41 处词表硬编码
  - 永久系统触发（32）：15 处时间触发 + 6 处空 handler
  - 新 AI 可发现性（55）：40 个 GATE 无反查 + 10 个关键能力未注册
  - DB 全景图深度（17）：949 真孤儿未监控 + 死代码
  - 文档引用断裂（26）：136 处引用断裂 + 三方对齐 9 个

30 项指标（目标值均为 0，当前总值 3193 手动调研基线）：
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
  - SSoT 对账：每项指标可追溯到 ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §二 病根
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
description: 架构健康度仪表盘（30 项指标自动化检测基线，ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四 第0期）
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
import sqlite3
import subprocess
import sys
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yaml

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
NOQA_EXEMPT_REGISTRY = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "noqa_exempt_registry.yaml"
)
# M13 扫描面 SSoT（#ARCH-SEC-001）：仅扫描信任边界 surface（对外协议响应面），
# 同信任域（commit gates/CLI/内部服务/本地 dashboard）返异常详情属 debuggability 特性非泄露
TRUST_BOUNDARY_REGISTRY = (
    REPO_ROOT
    / "docs"
    / "01_policies_and_standards"
    / "_registry"
    / "catalogs"
    / "trust_boundary_surface_registry.yaml"
)
OUTPUT_DIR = REPO_ROOT / "data" / "architecture_health"

# 手动调研基线（architecture_debt_registry_v2.md L5667（已归档）：当前总值 3193）
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


_NOQA_MARKERS_CACHE: frozenset[str] | None = None
_NOQA_MARKERS_LOCK = __import__("threading").Lock()


def _load_noqa_exempt_markers() -> frozenset[str]:
    """从 noqa_exempt_registry.yaml 加载合法 noqa 豁免标记集合（SSoT）。

    ARCH-NOQA-GOV-001 Phase 3 统一抽象：替代4处 inline
    ``if "# noqa: <marker>" in source: continue`` 重复模式。
    fail-open：registry 加载失败返回空集合（不阻断检测器运行）。
    线程安全：double-checked locking 避免 check-then-set 竞态（红蓝对抗维度5修复）。
    """
    global _NOQA_MARKERS_CACHE
    if _NOQA_MARKERS_CACHE is not None:
        return _NOQA_MARKERS_CACHE
    with _NOQA_MARKERS_LOCK:
        if _NOQA_MARKERS_CACHE is not None:
            return _NOQA_MARKERS_CACHE
        try:
            data = load_yaml_safe(NOQA_EXEMPT_REGISTRY)
            markers = frozenset(
                m["marker"] for m in (data.get("markers") or []) if m.get("marker")
            )
            _NOQA_MARKERS_CACHE = markers
            return markers
        except Exception:  # noqa: BLE001 — fail-open 不阻断检测器
            return frozenset()


def _has_noqa_exempt(source: str, marker: str) -> bool:
    """检查源码是否含指定 noqa 豁免标记（统一抽象，ARCH-NOQA-GOV-001 Phase 3）。

    替代4处 inline ``if "# noqa: <marker>" in source: continue`` 重复模式。
    marker 合法性由 noqa_validation_gate（priority=71）在 commit 阶段强制校验，
    本函数只负责运行时检测——检查源码是否含标记字符串。

    Args:
        source: 源码字符串。
        marker: noqa 标记名（如 ``m02-manual``）。

    Returns:
        True 如果源码含 ``# noqa: <marker>`` 标记。
    """
    return f"# noqa: {marker}" in source


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

# 治本（M02，2026-07-17）：常驻服务特征模式——用于识别"真正的永久系统"。
# 原检测把所有 [STARTUP]=manual [TTL]=permanent 视为违规，但：
#   - [TTL]=permanent 表示"代码永久保留"（非一次性工具），不是"进程永久运行"
#   - [STARTUP]=manual 对 CLI 工具是正确的（人/AI/CI 手动调用）
#   - 真正的违规：含常驻服务特征的文件标记为 manual（如 while True/signal.signal/daemon）
# 检测目标：含常驻服务特征 + [STARTUP]=manual [TTL]=permanent + 未豁免
_DAEMON_FEATURE_PATTERNS = [
    r"\bwhile\s+True\s*:",                  # 主循环（常驻服务标志）
    r"\bsignal\.signal\s*\(",               # 信号处理（守护进程优雅退出）
    r"\bdaemon\s*=\s*True",                 # 守护线程
    r"\bAPScheduler",                       # APScheduler
    r"\bschedule\.every",                   # schedule 库
    r"\bthreading\.Thread\s*\([^)]*daemon", # 守护线程
    r"\bBackgroundScheduler",               # APScheduler Background
    r"\bBlockingScheduler",                 # APScheduler Blocking
    r"\bloop\.run_forever",                 # asyncio 事件循环
    r"\bsubprocess\.Popen\s*\([^)]*daemon", # 守护子进程
]
_DAEMON_FEATURE_RE = re.compile("|".join(_DAEMON_FEATURE_PATTERNS))


def metric_02_manual_only_permanent() -> dict:
    """manual-only 永久脚本数——常驻服务特征 + [STARTUP] manual + [TTL] permanent 组合违规。

    病根：永久系统全自动触发（铁律）——永久系统必须自动触发/运行/维护/关闭。
    治本（M02，2026-07-17）：
      1. 原检测把 [TTL]=permanent 误判为"进程永久运行"——实际 [TTL]=permanent 表示
         "代码永久保留"（非一次性工具），CLI 工具运行后退出，不是永久系统。
      2. 真正的违规：含常驻服务特征（while True/signal.signal/daemon=True/APScheduler 等）
         + [STARTUP]=manual + [TTL]=permanent 的文件。
      3. 扫描范围扩大到 src/zephyr/ + scripts/governance/（原仅扫描 scripts/governance/）。
      4. 支持 # noqa: m02-manual per-file 豁免（合理的 CLI 启动常驻服务，如交易主入口）。
    """
    exclude = EXCLUDE_DIRS | {"_archive", "tests", "__pycache__"}
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
            sm = _STARTUP_RE.search(source)
            tm = _TTL_RE.search(source)
            if not sm or not tm:
                continue
            startup = sm.group(1).strip()
            ttl = tm.group(1).strip()
            if startup.lower() != "manual" or ttl.lower() != "permanent":
                continue
            # 治本（M02）：per-file 豁免（合理的 CLI 启动常驻服务）
            if _has_noqa_exempt(source, "m02-manual"):
                continue
            # 治本（M02）：只检测含常驻服务特征的文件（排除纯 CLI 工具）
            if not _DAEMON_FEATURE_RE.search(source):
                continue
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


# 治本（M03，2026-07-17）：标准 dunder 方法是 Python 协议实现，
# 跨类天然重复（每个类都需要 __init__/__exit__ 等），不计为"复制粘贴"。
# 仅检测非 dunder 方法（业务逻辑）的重复簇。
_DUNDER_METHODS = frozenset({
    "__init__", "__getattr__", "__setattr__", "__delattr__",
    "__str__", "__repr__", "__format__", "__sizeof__",
    "__enter__", "__exit__", "__aenter__", "__aexit__",
    "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__",
    "__hash__", "__len__", "__length_hint__", "__contains__",
    "__iter__", "__next__", "__bool__", "__call__", "__await__",
    "__getitem__", "__setitem__", "__delitem__", "__missing__",
    "__add__", "__sub__", "__mul__", "__truediv__", "__floordiv__",
    "__mod__", "__pow__", "__and__", "__or__", "__xor__",
    "__radd__", "__rsub__", "__rmul__", "__rtruediv__",
    "__iadd__", "__isub__", "__imul__", "__itruediv__",
    "__neg__", "__pos__", "__abs__", "__invert__",
    "__post_init__", "__getstate__", "__setstate__", "__reduce__",
    "__copy__", "__deepcopy__", "__getnewargs__",
})


def metric_03_duplicate_function_clusters() -> dict:
    """重复簇函数数——AST 函数体哈希聚类。

    病根：SSoT 真源唯一性 211 中的 159 对文件复制（含函数级重复）。
    检测：解析 src/zephyr/ 下 .py，对每个函数体归一化后哈希，聚类统计 >1 成员的簇。
    注：归一化剥离变量名/字面量差异，捕获"复制后改个名"的重复。

    治本（M03，2026-07-17）：
    1. 过滤标准 dunder 方法（Python 协议实现，跨类天然重复，非复制粘贴）。
    2. 支持 # noqa: m03-duplicate 豁免（per-file，适用于接口实现等合法重复）。
    3. 过滤"全簇同名"的簇——接口实现(多态)和同文件重载(overloading)，非复制粘贴。
       M05(文件复制对=0)已覆盖文件级复制检测。仅保留"异名同体"的簇。
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
        # 治本（M03）：per-file 豁免（接口实现/协议方法等合法重复）
        if _has_noqa_exempt(source, "m03-duplicate"):
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # 治本（M03）：跳过标准 dunder 方法（Python 协议，跨类天然重复）
            if node.name in _DUNDER_METHODS:
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
    # 治本（M03）：过滤"全簇同名"的簇——接口实现(多态)和同文件重载(overloading)，
    # 非复制粘贴。M05(文件复制对=0)已覆盖文件级复制检测(M05=0)。
    # 仅保留"异名同体"的簇——更可能是真重复(复制后改名)。
    real_clusters: dict[str, list[str]] = {}
    for h, funcs in clusters.items():
        names = {f.split(":")[1].split("()")[0] for f in funcs}
        if len(names) > 1:
            real_clusters[h] = funcs
    details: list[str] = []
    for funcs in sorted(real_clusters.values(), key=lambda x: -len(x))[:20]:
        details.append(f"簇({len(funcs)}): " + " | ".join(funcs[:3]))
    return _make_metric("M03", "重复簇函数数", len(real_clusters), details, "inline-AST")


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
    （ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四 第3期）。
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

    治本（M07，2026-07-17）：
    1. 支持 # noqa: m07-orphan 豁免（per-file）。
    2. 检测动态引用：收集所有字符串字面量，模块 stem 出现在字符串中视为被引用
       （importlib.import_module / __import__ / 注册表字符串引用 / 配置文件引用）。
    3. 跳过有 [STARTUP] 头的文件（有定义的加载机制，非 orphan）。
    4. 扫描 scripts/ 目录的 import 和字符串字面量（跨目录引用检测）。
    """
    exclude = EXCLUDE_DIRS | {"tests", "__pycache__"}
    py_files = iter_files(SRC_ZEPHYR, extensions=frozenset({".py"}), exclude_dirs=exclude)
    all_modules: dict[str, Path] = {}
    all_trees: list[tuple[Path, ast.AST | None, str]] = []
    all_string_literals: set[str] = set()
    for fp in py_files:
        try:
            src = fp.read_text(encoding="utf-8")
            tree = ast.parse(src, filename=str(fp))
        except (OSError, UnicodeDecodeError, SyntaxError):
            tree = None
            src = ""
        # 治本（M07 盲点）：字符串字面量从所有文件收集（含 __init__.py 的 __all__
        # 与 [STARTUP] 头文件）——包 __init__.py 的 __all__ 是对子模块的合法
        # re-export 引用，原实现先跳过 __init__.py 再收集字符串，导致被 re-export
        # 的子模块（如 decision_registry/guard_layers）被误报为 orphan。
        if tree is not None:
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    all_string_literals.add(node.value)
        if fp.name in ("__init__.py", "__main__.py", "conftest.py", "setup.py"):
            continue
        # 治本（M07）：per-file 豁免
        if _has_noqa_exempt(src, "m07-orphan"):
            continue
        # 治本（M07）：跳过有 [STARTUP] 头的文件（有加载机制）
        if re.search(r"^#\s*\[STARTUP\]", src, re.MULTILINE):
            continue
        all_modules[fp.stem] = fp
        all_trees.append((fp, tree, src))
    # 治本（M07）：也扫描 scripts/ 下的 import 和字符串（跨目录引用）
    scripts_dir = REPO_ROOT / "scripts"
    if scripts_dir.exists():
        script_files = iter_files(
            scripts_dir, extensions=frozenset({".py"}),
            exclude_dirs=exclude,
        )
        for sfp in script_files:
            try:
                ssrc = sfp.read_text(encoding="utf-8")
                stree = ast.parse(ssrc, filename=str(sfp))
            except (OSError, UnicodeDecodeError, SyntaxError):
                continue
            if stree is None:
                continue
            for snode in ast.walk(stree):
                if isinstance(snode, ast.Import):
                    for alias in snode.names:
                        if alias.name:
                            all_string_literals.add(alias.name.split(".")[-1])
                elif isinstance(snode, ast.ImportFrom):
                    if snode.module:
                        all_string_literals.add(snode.module.split(".")[-1])
                    for alias in snode.names:
                        if alias.name and alias.name != "*":
                            all_string_literals.add(alias.name)
                elif isinstance(snode, ast.Constant) and isinstance(snode.value, str):
                    all_string_literals.add(snode.value)
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
        # 治本（M07）：模块 stem 出现在字符串字面量中 → 动态引用，非 orphan
        if stem in all_string_literals:
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
            # 治本（M10，2026-07-17）：支持 m10-time-trigger 标记豁免
            # 适用于：schema 中 "cron" 枚举值/注释提及 "cron"/锁等待 while True+sleep/
            # perm_trigger_gate 自身（检测器含模式字符串）/ threading.Timer 超时（非周期触发）
            if _has_noqa_exempt(source, "m10-time-trigger"):
                continue
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


# ── 指标 12/13/14 共享：生产 .py 文件 AST 扫描 ─────────────────────────────


def iter_prod_py_files() -> list[Path]:
    """生产 .py 文件清单（src/zephyr + scripts/governance，排除 tests/_archive）。"""
    exclude = EXCLUDE_DIRS | {"_archive", "tests", "__pycache__"}
    files: list[Path] = []
    for scan_dir in (SRC_ZEPHYR, SCRIPTS_GOVERNANCE):
        if scan_dir.exists():
            files.extend(iter_files(scan_dir, extensions=frozenset({".py"}), exclude_dirs=exclude))
    return files


# 向后兼容别名（R5 私有断言消除：公共 API 为主实现，_xxx 保留为别名）
_iter_prod_py_files = iter_prod_py_files


def _scan_py_file_ast(fp: Path) -> tuple[ast.Module | None, list[str]]:
    """读取并 AST 解析 .py 文件，返回 (tree, lines)；失败返回 (None, [])。"""
    try:
        source = fp.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None, []
    try:
        return ast.parse(source, filename=str(fp)), source.splitlines()
    except SyntaxError:
        return None, []


def _walk_no_nested_scope(node: ast.AST):
    """walk（含节点自身）但不下钻嵌套作用域（FunctionDef/AsyncFunctionDef/Lambda/ClassDef）。"""
    stack = [node]
    while stack:
        n = stack.pop()
        yield n
        if n is not node and isinstance(
            n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)
        ):
            continue
        stack.extend(ast.iter_child_nodes(n))


# ── 指标 12：异常粒度过粗（5.135）─────────────────────────────────────────

_BROAD_EXCEPT_NAMES = frozenset({"Exception", "BaseException"})


def _is_broad_except(handler: ast.ExceptHandler) -> bool:
    """宽泛判定：bare except 或 except Exception/BaseException。"""
    if handler.type is None:
        return True
    return isinstance(handler.type, ast.Name) and handler.type.id in _BROAD_EXCEPT_NAMES


def _is_logger_call_stmt(stmt: ast.stmt) -> bool:
    """判定语句是否为 logger.* 调用（logger.warning(...) 等）。"""
    if not isinstance(stmt, ast.Expr) or not isinstance(stmt.value, ast.Call):
        return False
    func = stmt.value.func
    return (
        isinstance(func, ast.Attribute)
        and isinstance(func.value, ast.Name)
        and func.value.id in ("logger", "_logger", "log", "LOGGER")
    )


def _classify_swallow(handler: ast.ExceptHandler) -> str | None:
    """分类宽泛 except 的吞没模式。返回 None=非吞没（有 raise/return 或正常降级）。"""
    body = handler.body
    if all(isinstance(s, ast.Pass) for s in body):
        return "except-pass"
    if all(isinstance(s, ast.Continue) for s in body):
        return "except-continue"
    has_reraise_or_return = any(
        isinstance(n, (ast.Raise, ast.Return)) for s in body for n in _walk_no_nested_scope(s)
    )
    if has_reraise_or_return:
        return None
    # logged-but-swallowed：body 仅由 logger.* 调用组成（记了日志但吞没异常）
    if body and all(_is_logger_call_stmt(s) for s in body):
        return "logged-swallowed"
    return None


def _has_ble001_noqa(lines: list[str], node: ast.ExceptHandler) -> bool:
    """检查 handler 行范围是否含 `# noqa: BLE001`（ruff 标准码豁免——项目既有
    "已审视宽泛捕获"约定，noqa_validation_gate 对标准码跳过不校验登记）。"""
    end = node.end_lineno or node.lineno
    for ln in range(node.lineno, end + 1):
        if 1 <= ln <= len(lines) and "noqa: BLE001" in lines[ln - 1]:
            return True
    return False


def metric_12_broad_except_swallow() -> dict:
    """异常粒度过粗违规数（5.135）——宽泛 except 吞没模式 AST 检测。

    病根：5.135 异常粒度过粗（手动快照 697 项）——except Exception:pass /
    except:continue / logged-but-swallowed 吞没异常，故障被静默掩盖。
    检测：AST 扫描 except Exception/BaseException/bare 且 body 为
    pass-only / continue-only / 仅 logger 调用（无 raise/return）的 handler。
    豁免：`# noqa: BLE001`（ruff 标准码，项目既有"已审视宽泛捕获"约定）。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        tree, lines = _scan_py_file_ast(fp)
        if tree is None:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for node in ast.walk(tree):
            if not isinstance(node, ast.ExceptHandler) or not _is_broad_except(node):
                continue
            kind = _classify_swallow(node)
            if kind is None or _has_ble001_noqa(lines, node):
                continue
            violations.append(f"{rel}:{node.lineno} {kind}")
    return _make_metric("M12", "异常粒度过粗(吞没型)", len(violations), violations, "inline")


# ── 指标 13：异常信息泄露（5.168）─────────────────────────────────────────


def _return_leaks_exc(ret_value: ast.AST, exc_names: frozenset) -> str | None:
    """检测 return 值是否泄露异常内容：str(e)/repr(e)/f-string插值e/traceback.format_exc()。"""
    for n in _walk_no_nested_scope(ret_value):
        if isinstance(n, ast.Call):
            if isinstance(n.func, ast.Attribute) and n.func.attr == "format_exc":
                return "traceback.format_exc"
            if isinstance(n.func, ast.Name) and n.func.id in ("str", "repr") and n.args:
                a0 = n.args[0]
                if isinstance(a0, ast.Name) and a0.id in exc_names:
                    return f"{n.func.id}({a0.id})"
        if isinstance(n, ast.JoinedStr):
            for v in n.values:
                if (
                    isinstance(v, ast.FormattedValue)
                    and isinstance(v.value, ast.Name)
                    and v.value.id in exc_names
                ):
                    return f"f-string{{{v.value.id}}}"
    return None


# M13 HTTP 外发汇点（#ARCH-SEC-001）：except handler 内调用此类方法把异常详情
# 写进 HTTP 响应体（BaseHTTPRequestHandler 系/本项目 _MonitorHandler 封装），
# 与 return 泄露等价——return 检测覆盖不了 handler 直接 _send_json(...) 的场景
_HTTP_EMIT_SINKS = frozenset({"_send_json", "_send", "send_json", "send_error"})


def _load_trust_boundary_files() -> list[Path] | None:
    """从 trust_boundary_surface_registry.yaml 加载信任边界 surface 文件清单（SSoT）。

    #ARCH-SEC-001：M13 扫描面限定为对外协议响应面（MCP stdio / 监控 HTTP 等跨
    进程·跨机器零信任边界）。fail-closed：registry 缺失/损坏/条目异常返回 None，
    调用方转为 error 状态（指标报 error 而非假绿）。
    """
    try:
        data = load_yaml_safe(TRUST_BOUNDARY_REGISTRY)
        surfaces = data.get("surfaces") or []
        if not surfaces:
            return None
        files: list[Path] = []
        for s in surfaces:
            rel = s.get("path")
            if not rel:
                return None
            base = REPO_ROOT / rel
            if s.get("kind") == "directory":
                files.extend(sorted(base.glob(s.get("glob") or "*.py")))
            else:
                files.append(base)
        result = [f for f in files if f.exists() and f.suffix == ".py"]
        return result or None
    except Exception:  # noqa: BLE001 — fail-closed：任何加载异常都转为 error 状态
        return None


def _check_emit_sink_call(rel: Path, call: ast.Call, exc_names: frozenset) -> str | None:
    """检测 HTTP 外发汇点调用（_send_json/send_error 等）参数含异常引用，命中返回违规串。"""
    if not (isinstance(call.func, ast.Attribute) and call.func.attr in _HTTP_EMIT_SINKS):
        return None
    for arg in call.args:
        leak = _return_leaks_exc(arg, exc_names)
        if leak:
            return f"{rel}:{call.lineno} {call.func.attr}() 外发泄露 {leak}"
    return None


def _collect_m13_handler_violations(rel: Path, tree: ast.Module) -> list[str]:
    """收集单文件全部 except handler 的 M13 泄露违规（return 泄露 + HTTP 外发泄露）。"""
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ExceptHandler):
            continue
        exc_names = frozenset({node.name}) if node.name else frozenset()
        for stmt in node.body:
            for sub in _walk_no_nested_scope(stmt):
                if isinstance(sub, ast.Return) and sub.value is not None:
                    leak = _return_leaks_exc(sub.value, exc_names)
                    if leak:
                        found.append(f"{rel}:{sub.lineno} return 泄露 {leak}")
                elif isinstance(sub, ast.Call):
                    hit = _check_emit_sink_call(rel, sub, exc_names)
                    if hit:
                        found.append(hit)
    return found


def metric_13_exception_info_leak() -> dict:
    """异常信息泄露违规数（5.168）——except 块内 return/HTTP外发 泄露异常内容跨信任边界。

    病根：5.168 异常信息泄露（手动快照 142 项）——MCP/handler 的通用异常
    处理器把 str(exc)/f-string 插值异常/traceback 直返客户端，泄露内部实现
    （路径/凭据片段/SQL）。检测：AST 扫描 except handler 内 (a) return 语句、
    (b) HTTP 外发汇点调用（_send_json/send_error 等，见 _HTTP_EMIT_SINKS）含
    str(exc_var) / repr(exc_var) / f-string 插值 exc_var / traceback.format_exc()。
    不下钻嵌套函数作用域（嵌套函数的 return 非 handler 直返）。

    #ARCH-SEC-001 校准（2026-07-18）：扫描面由 trust_boundary_surface_registry.yaml
    限定为对外协议响应面——异常详情跨信任边界到达不可信消费方才是 5.168 定义的
    "泄露"；同信任域（commit gates/CLI/内部服务/本地 dashboard）返异常详情属
    debuggability 特性非泄露。registry 加载失败 fail-closed 报 error。
    """
    boundary_files = _load_trust_boundary_files()
    if boundary_files is None:
        return _make_metric(
            "M13", "异常信息泄露(返客户端)", 0,
            error="trust_boundary_surface_registry.yaml 加载失败（fail-closed）",
            source="inline",
        )
    violations: list[str] = []
    for fp in boundary_files:
        tree, _lines = _scan_py_file_ast(fp)
        if tree is None:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        violations.extend(_collect_m13_handler_violations(rel, tree))
    return _make_metric("M13", "异常信息泄露(返客户端)", len(violations), violations, "inline")


# ── 指标 14：ABC 抽象方法完整性（5.104）────────────────────────────────────

_ABSTRACT_DECO_NAMES = frozenset(
    {"abstractmethod", "abstractproperty", "abstractclassmethod", "abstractstaticmethod"}
)


def _is_abc_class(cls: ast.ClassDef) -> bool:
    """判定 ClassDef 是否 ABC（继承 ABC 或 metaclass=ABCMeta）。"""
    for base in cls.bases:
        name = base.id if isinstance(base, ast.Name) else (
            base.attr if isinstance(base, ast.Attribute) else None
        )
        if name in ("ABC", "ABCMeta"):
            return True
    return any(
        kw.arg == "metaclass"
        and isinstance(kw.value, ast.Name)
        and kw.value.id == "ABCMeta"
        for kw in cls.keywords
    )


def _abstract_methods(cls: ast.ClassDef) -> dict[str, ast.FunctionDef]:
    """提取类内 @abstractmethod 系装饰器方法 {name: node}。"""
    result: dict[str, ast.FunctionDef] = {}
    for stmt in cls.body:
        if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for deco in stmt.decorator_list:
            name = deco.id if isinstance(deco, ast.Name) else (
                deco.attr if isinstance(deco, ast.Attribute) else None
            )
            if name in _ABSTRACT_DECO_NAMES:
                result[stmt.name] = stmt
                break
    return result


def _class_methods(cls: ast.ClassDef) -> dict[str, ast.FunctionDef]:
    """提取类内全部方法 {name: node}。"""
    return {
        s.name: s for s in cls.body if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _positional_params(fn: ast.FunctionDef) -> list[str]:
    """提取位置参数名（排除 self/cls，含 kwonly，排除 *args/**kwargs）。"""
    args = fn.args
    names = [a.arg for a in list(args.posonlyargs) + list(args.args)]
    if names and names[0] in ("self", "cls"):
        names = names[1:]
    return names + [a.arg for a in args.kwonlyargs]


def _check_subclass_against_abc(rel: Path, sub: ast.ClassDef, abc: ast.ClassDef) -> list[str]:
    """比对单个子类与 ABC：缺失覆写 + 签名漂移（中间抽象类缺失覆写属合法，由人工甄别）。"""
    found: list[str] = []
    sub_methods = _class_methods(sub)
    for name, abs_fn in _abstract_methods(abc).items():
        impl = sub_methods.get(name)
        if impl is None:
            found.append(f"{rel}:{sub.lineno} {sub.name} 未覆写 {abc.name}.{name}")
            continue
        impl_params = _positional_params(impl)
        abc_params = _positional_params(abs_fn)
        if impl_params != abc_params:
            found.append(
                f"{rel}:{impl.lineno} {sub.name}.{name} 签名漂移 impl={impl_params} vs abc={abc_params}"
            )
    return found


def metric_14_abc_completeness() -> dict:
    """ABC 抽象方法完整性违规数（5.104）——同文件 ABC/子类 AST 签名比对。

    病根：5.104 ABC抽象方法完整性（手动快照 33 项）——ABC 签名与实现不匹配
    （LSP 违规）/ ABC 定义但实现类未覆写。同文件内可 AST 精确检测。
    检测：同文件 ABC（含 @abstractmethod 系方法）+ 同文件子类（bases 引用
    ABC 名），比对每个抽象方法是否覆写、覆写签名位置参数是否漂移。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        tree, _lines = _scan_py_file_ast(fp)
        if tree is None:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        abcs = {c.name: c for c in classes if _is_abc_class(c) and _abstract_methods(c)}
        if not abcs:
            continue
        for cls in classes:
            if cls.name in abcs:
                continue
            base_names = {b.id for b in cls.bases if isinstance(b, ast.Name)}
            for abc_name in base_names & set(abcs):
                violations.extend(_check_subclass_against_abc(rel, cls, abcs[abc_name]))
    return _make_metric("M14", "ABC抽象方法完整性", len(violations), violations, "inline")


# ── 指标 15：depgraph 新鲜度 ─────────────────────────────────────────────────
# 治本（#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3.3）：depgraph 新鲜度仪表盘
# 与 depgraph_freshness_gate.py (P3.1) 共享数据源 .runtime/depgraph_scan_cache.json
# _meta.saved_at，但独立解析（避免 scripts/ → src/zephyr/gov_enforcement/ 跨层耦合）
_DEPGRAPH_CACHE_REL = ".runtime/depgraph_scan_cache.json"
_DEPGRAPH_WARN_SECONDS = 30 * 60        # 30 分钟 → WARNING（与 gate 同阈值）
_DEPGRAPH_BLOCK_SECONDS = 24 * 60 * 60  # 24 小时 → 阻断级（与 gate 同阈值）
_REMEDIATION_BLOCK_SECONDS = 90 * 24 * 60 * 60  # 90 天 → 阻断级（与 GATE-REMEDIATION-PROGRESS 同阈值，#ARCH-GOV-CONVERGENCE-META Phase 3.1）
# M16 SQL（NO-BARE-SQL compliance）
_SQL_CHECK_REMEDIATION_TABLE = "SELECT name FROM sqlite_master WHERE type='table' AND name='remediation_progress'"
_SQL_SELECT_STALE_REMEDIATION = (
    'SELECT dimension_id, title, last_updated FROM remediation_progress '
    "WHERE last_updated < ? AND status NOT IN ('completed', 'deferred') "
    'ORDER BY last_updated ASC'
)


def _parse_depgraph_saved_at(saved_at_raw: str) -> datetime | None:
    """解析 depgraph scan cache 的 saved_at ISO 时间戳（兼容带/不带时区）。

    与 depgraph_freshness_gate._parse_saved_at 同逻辑——独立实现避免
    scripts/ → src/zephyr/gov_enforcement/ 跨层耦合（dashboard 自包含原则）。
    generate_project_depgraph.py 用 datetime.now().isoformat() 写入（无时区），
    按本地时间解析后转 UTC 比较。
    """
    if not saved_at_raw:
        return None
    try:
        dt = datetime.fromisoformat(saved_at_raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        # 无时区 → 按本地时间解释，转 UTC（astimezone 对 naive datetime 假定系统时区）
        dt = dt.astimezone(UTC)
    return dt.astimezone(UTC)


def metric_15_depgraph_freshness() -> dict:
    """depgraph 新鲜度——>24h 阻断级违规数（#ARCH-DEPGRAPH-RECONCILER-FAILSILENT Phase 3.3）。

    病根：depgraph 是依赖关系唯一真源（L2 铁律），但 sync 是 reconciler 异步触发。
    若触发链断裂，depgraph 长期不刷新，AI 在过期快照上设计 = 幻觉温床。
    P3.1 已在 commit 时 dual-threshold 阻断（>24h block, >30min warn）。
    本指标把新鲜度状态暴露到仪表盘，供 post-commit 基线追踪与 AI 冷启动查询。

    检测：读取 .runtime/depgraph_scan_cache.json 的 _meta.saved_at，计算 age。
    count 语义（与 GATE-DEPGRAPH-FRESHNESS 阻断行为对齐）：
      - 0 = fresh (<30min) 或 warn (>30min, <24h)——非阻断级违规
      - 1 = block (>24h)——阻断级违规，commit 会被 GATE-DEPGRAPH-FRESHNESS 拒绝
    fail-open：cache 缺失/解析失败 → count=0 + error 字段（不视为违规，
    因首启/新环境无 cache 正常；与 gate fail-open 行为一致）。
    """
    cache_path = REPO_ROOT / _DEPGRAPH_CACHE_REL
    if not cache_path.is_file():
        return _make_metric(
            "M15", "depgraph新鲜度(>24h阻断数)", 0,
            details=[f"cache missing: {_DEPGRAPH_CACHE_REL} (first-run or new env)"],
            source="inline",
            error=f"cache not found: {_DEPGRAPH_CACHE_REL}",
        )
    try:
        data = json.loads(cache_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return _make_metric(
            "M15", "depgraph新鲜度(>24h阻断数)", 0,
            details=[f"cache parse failed: {e}"],
            source="inline",
            error=f"cache parse failed: {e}",
        )

    saved_at_raw = (data.get("_meta") or {}).get("saved_at")
    if not saved_at_raw:
        return _make_metric(
            "M15", "depgraph新鲜度(>24h阻断数)", 0,
            details=["cache missing _meta.saved_at"],
            source="inline",
            error="cache missing _meta.saved_at",
        )

    saved_at = _parse_depgraph_saved_at(saved_at_raw)
    if saved_at is None:
        return _make_metric(
            "M15", "depgraph新鲜度(>24h阻断数)", 0,
            details=[f"saved_at unparseable: {saved_at_raw!r}"],
            source="inline",
            error=f"saved_at unparseable: {saved_at_raw!r}",
        )

    now_utc = datetime.now(UTC)
    age_seconds = (now_utc - saved_at).total_seconds()

    # 时钟漂移（saved_at 在未来）→ 视为 fresh（与 gate 一致）
    if age_seconds < 0:
        return _make_metric(
            "M15", "depgraph新鲜度(>24h阻断数)", 0,
            details=[f"fresh (saved_at in future: {saved_at_raw})"],
            source="inline",
        )

    # dual-threshold 判定（与 GATE-DEPGRAPH-FRESHNESS 同阈值）
    if age_seconds >= _DEPGRAPH_BLOCK_SECONDS:
        hours = int(age_seconds // 3600)
        return _make_metric(
            "M15", "depgraph新鲜度(>24h阻断数)", 1,
            details=[
                f"BLOCK: {hours}h since last sync (saved_at={saved_at_raw})",
                "超过 24h 阈值——GATE-DEPGRAPH-FRESHNESS 会阻断 commit",
                "修复: python scripts/governance/generate_project_depgraph.py",
            ],
            source="inline",
        )

    if age_seconds >= _DEPGRAPH_WARN_SECONDS:
        minutes = int(age_seconds // 60)
        return _make_metric(
            "M15", "depgraph新鲜度(>24h阻断数)", 0,
            details=[
                f"WARN: {minutes}min since last sync (saved_at={saved_at_raw})",
                "超过 30min 告警阈值——建议运行 generate_project_depgraph.py 刷新",
            ],
            source="inline",
        )

    return _make_metric(
        "M15", "depgraph新鲜度(>24h阻断数)", 0,
        details=[f"fresh (age={int(age_seconds)}s, saved_at={saved_at_raw})"],
        source="inline",
    )



# ── 指标 16：治本进度新鲜度 ────────────────────────────────────────────────

def metric_16_remediation_progress_freshness() -> dict:
    """治本进度新鲜度——>90天超期未更新维度数（#ARCH-GOV-CONVERGENCE-META Phase 3.1）。

    病根：治本进度是 6 阶段治本计划跟踪数据，若长期不更新，
    AI 在过期进度上决策 = 幻觉温床。Phase 3.1 reconciler（priority=900）
    已在 commit 时阻断（>90天 block_next）。本指标暴露超期维度数到仪表盘。

    fail-open：表不存在/DB缺失 → count=0 + error（首启正常）。
    """
    db_path = REPO_ROOT / 'data' / 'databases' / 'governance.db'
    if not db_path.is_file():
        return _make_metric('M16', '治本进度新鲜度(>90天超期数)', 0,
            details=['governance.db missing (first-run or new env)'],
            source='inline', error=f'db not found: {db_path.relative_to(REPO_ROOT)}')
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            cur = conn.execute(_SQL_CHECK_REMEDIATION_TABLE)
            if not cur.fetchone():
                return _make_metric('M16', '治本进度新鲜度(>90天超期数)', 0,
                    details=['table not yet created (Phase 3.1 not bootstrapped)'],
                    source='inline', error='table remediation_progress missing')
            cutoff_iso = (datetime.now(UTC) - timedelta(seconds=_REMEDIATION_BLOCK_SECONDS)).isoformat()
            cur = conn.execute(_SQL_SELECT_STALE_REMEDIATION, (cutoff_iso,))
            stale = cur.fetchall()
        finally:
            conn.close()
    except sqlite3.Error as e:
        return _make_metric('M16', '治本进度新鲜度(>90天超期数)', 0,
            details=[f'db query failed: {e}'], source='inline', error=f'db query failed: {e}')
    if not stale:
        return _make_metric('M16', '治本进度新鲜度(>90天超期数)', 0,
            details=['all remediation dimensions fresh (<90 days)'], source='inline')
    details = [f'STALE: {row[0]} ({row[1]}) last_updated={row[2]}' for row in stale[:20]]
    return _make_metric('M16', '治本进度新鲜度(>90天超期数)', len(stale), details=details, source='inline')


# ── 指标 17：规则感知缺口（无门禁配对数） ──────────────────────────────────

# M17 SQL/路径常量（NO-BARE-SQL compliance 不适用——读 YAML 非 SQL）
_PERCEPTION_INDEX_REL = 'docs/01_policies_and_standards/_registry/catalogs/rule_ai_perception_index.yaml'


def metric_17_rule_perception_gap() -> dict:
    """规则感知缺口——无 paired_gate_id 的规则数（#ARCH-GOV-CONVERGENCE-META Phase 3.2a）。

    病根2（规则可发现性）治本指标：perception index 已建立（Phase 3.2a），
    但规则尚未与门禁配对（Phase 3.5 RULE-EXECUTION-PAIRING 将补齐 paired_gate_id）。
    本指标统计 paired_gate_id 为 null/空的规则数，追踪 Phase 3.5 进度。

    fail-open：YAML 不存在/解析失败 → count=0 + error（首启正常）。
    """
    idx_path = REPO_ROOT / _PERCEPTION_INDEX_REL
    if not idx_path.is_file():
        return _make_metric('M17', '规则感知缺口(无门禁配对数)', 0,
            details=['perception index not yet generated (Phase 3.2a not bootstrapped)'],
            source='inline', error=f'yaml not found: {idx_path.relative_to(REPO_ROOT)}')
    try:
        data = yaml.safe_load(idx_path.read_text(encoding='utf-8'))
    except yaml.YAMLError as e:
        return _make_metric('M17', '规则感知缺口(无门禁配对数)', 0,
            details=[f'yaml parse failed: {e}'], source='inline', error=f'yaml parse failed: {e}')
    if not isinstance(data, dict):
        return _make_metric('M17', '规则感知缺口(无门禁配对数)', 0,
            details=['yaml structure invalid (not dict)'], source='inline', error='yaml not dict')
    rules = data.get('rules', [])
    if not isinstance(rules, list) or not rules:
        return _make_metric('M17', '规则感知缺口(无门禁配对数)', 0,
            details=['no rules in perception index'], source='inline', error='no rules in index')
    unpaired = [r for r in rules if not r.get('paired_gate_id')]
    if not unpaired:
        return _make_metric('M17', '规则感知缺口(无门禁配对数)', 0,
            details=[f'all {len(rules)} rules have paired_gate_id (Phase 3.5 complete)'], source='inline')
    details = [f'UNPAIRED: {r.get("rule_id", "?")} ({r.get("title", "")[:40]})' for r in unpaired[:20]]
    return _make_metric('M17', '规则感知缺口(无门禁配对数)', len(unpaired), details=details, source='inline')


# ── 指标 20：trae_060 §5 静态声明 vs 运行时快照漂移数 ──────────────────────

# M20 路径常量（#ARCH-GOV-CONVERGENCE-META Phase 3.4b，病根1 治本）
_RUNTIME_SNAPSHOT_REL = 'data/runtime_violation_snapshot/latest.json'


def metric_20_runtime_snapshot_drift() -> dict:
    """trae_060 §5 静态声明 vs 运行时快照漂移数（#ARCH-GOV-CONVERGENCE-META Phase 3.4b）。

    病根1 治本指标：trae_060 §5 prohibitions 的历史计数（baseline_2026_06_26.yaml）
    与运行时快照（latest.json）的漂移类别数。

    - drift_count=0：live 检测结果与历史基线完全一致（无新增/无修复）
    - drift_count>0：存在漂移（可能是修复了违规=负 drift，或新增了违规=正 drift）
    - snapshot 不存在或 stale（>24h）：count=1 + error（reconciler 未运行或失败）

    fail-open：snapshot 不存在/解析失败 → count=0 + error（首启正常）。
    """
    try:
        from zephyr.governance.audit.runtime_violation_snapshot import (
            compare_baseline_with_live,
        )
    except ImportError as e:
        return _make_metric('M20', 'trae_060 §5 快照漂移数', 0,
            details=[f'import failed: {e}'], source='inline',
            error=f'import failed: {e}')

    try:
        comparison = compare_baseline_with_live(REPO_ROOT)
    except Exception as e:  # noqa: BLE001 — fail-open
        return _make_metric('M20', 'trae_060 §5 快照漂移数', 0,
            details=[f'compare failed: {e}'], source='inline',
            error=f'compare failed: {e}')

    drift_count = comparison.get('drift_count', 0)
    fresh = comparison.get('fresh', False)
    error = comparison.get('error', '')

    if not fresh and drift_count == 0:
        # snapshot stale 且无 drift 信息——报告 1（stale 本身是问题）
        details = ['snapshot stale or missing (reconciler not run recently)']
        if error:
            details.append(f'reason: {error}')
        return _make_metric('M20', 'trae_060 §5 快照漂移数', 1,
            details=details, source=_RUNTIME_SNAPSHOT_REL,
            error=f'snapshot stale: {error}' if error else 'snapshot stale')

    # 构造详细 drift 信息
    details = []
    for v in comparison.get('violations', [])[:20]:
        cat = v.get('category', '?')
        claimed = v.get('claimed', 0)
        detected = v.get('detected', 0)
        drift = v.get('drift', 0)
        marker = ''
        if drift < 0:
            marker = ' (FIXED)'
        elif drift > 0:
            marker = ' (NEW VIOLATIONS)'
        details.append(f'{cat}: claimed={claimed}, detected={detected}, drift={drift}{marker}')

    return _make_metric('M20', 'trae_060 §5 快照漂移数', drift_count,
        details=details, source=_RUNTIME_SNAPSHOT_REL,
        error=error if not fresh else '')


# ── 指标 19：治理层 151→6 收敛缺口数 ──────────────────────────────────────

_CONVERGENCE_MAP_REL = 'docs/01_policies_and_standards/_registry/catalogs/governance_convergence_map.yaml'


def metric_19_governance_convergence_gap() -> dict:
    """治理层 151→6 收敛缺口数（#ARCH-GOV-CONVERGENCE-META Phase 3.3）。

    病根4 治本指标：治理体系自身 151+ 个组件（gate/reconciler/vocab/registry）
    应收敛为 6 个核心功能入口。M19 = 未收敛组件数（total - consolidated）。

    - M19=0：所有组件已收敛到 6 个核心功能入口（理想态）
    - M19>0：仍有组件未收敛，治理体系自身仍是漂移源
    - convergence_map 不存在/解析失败 → fail-open，count=0 + error

    数据真源：docs/01_policies_and_standards/_registry/catalogs/governance_convergence_map.yaml
    """
    import yaml as _yaml

    map_path = REPO_ROOT / _CONVERGENCE_MAP_REL
    if not map_path.exists():
        return _make_metric('M19', '治理层收敛缺口数', 0,
            details=[f'convergence map not found: {_CONVERGENCE_MAP_REL}'],
            source='inline', error='convergence map not found')

    try:
        data = _yaml.safe_load(map_path.read_text(encoding='utf-8'))
    except Exception as e:  # noqa: BLE001 — fail-open
        return _make_metric('M19', '治理层收敛缺口数', 0,
            details=[f'YAML parse failed: {e}'], source='inline',
            error=f'YAML parse failed: {e}')

    if not isinstance(data, dict):
        return _make_metric('M19', '治理层收敛缺口数', 0,
            details=['convergence map top-level not dict'],
            source='inline', error='invalid structure')

    summary = data.get('convergence_summary', {})
    if not isinstance(summary, dict):
        return _make_metric('M19', '治理层收敛缺口数', 0,
            details=['convergence_summary missing'],
            source='inline', error='convergence_summary missing')

    total = summary.get('total_components', 0)
    consolidated = summary.get('consolidated_components', 0)
    gap = total - consolidated

    # 构造详细信息
    details = []
    core_functions = data.get('core_functions', []) or []
    for cf in core_functions:
        if not isinstance(cf, dict):
            continue
        cf_id = cf.get('id', '?')
        cf_name = cf.get('name', '?')
        for c in cf.get('consolidates', []) or []:
            if not isinstance(c, dict):
                continue
            ctype = c.get('component_type', '?')
            count = c.get('current_count', 0)
            status = c.get('status', '?')
            details.append(f'{cf_id}/{ctype}: {count} components, status={status}')

    details.append(f'total={total}, consolidated={consolidated}, gap={gap}')
    details.append('target: 6 core function entry points (M19 ≤ 6)')

    return _make_metric('M19', '治理层收敛缺口数', gap,
        details=details, source=_CONVERGENCE_MAP_REL)


# ── 指标 21：5 病根 × 3 要素覆盖缺口数 ────────────────────────────────────

_RC_ELEMENTS = ('persistence', 'discoverability', 'enforceability')


def _scan_root_cause_cells(
    root_causes: list,
) -> tuple[int, int, list[str]]:
    """扫描 root_causes 列表，返回 (total_cells, covered_cells, uncovered_list)。

    辅助 metric_21_root_cause_coverage 降低循环复杂度（Extract Method）。
    """
    total = 0
    covered = 0
    uncovered: list[str] = []
    for rc in root_causes:
        if not isinstance(rc, dict):
            continue
        rc_id = rc.get('id', '?')
        elements = rc.get('elements', {}) or {}
        for ek in _RC_ELEMENTS:
            total += 1
            elem = elements.get(ek, {}) or {}
            if not isinstance(elem, dict):
                continue
            if elem.get('covered', False):
                covered += 1
            else:
                gap = elem.get('gap', 'no gap description')
                uncovered.append(f'{rc_id}/{ek}: {gap}')
    return total, covered, uncovered


def _format_coverage_details(
    total: int, covered: int, uncovered: list[str],
    declared_uncovered: int | None,
) -> list[str]:
    """格式化 M21 指标详情列表（辅助函数，降低 metric_21 循环复杂度）。"""
    details = [f'total_cells={total}, covered={covered}, uncovered={len(uncovered)}']
    if declared_uncovered is not None:
        details.append(f'declared_uncovered={declared_uncovered} (SSoT)')
        if declared_uncovered != len(uncovered):
            details.append(
                f'WARNING: declared ({declared_uncovered}) != scanned ({len(uncovered)})'
            )
    details.append('target: 0 (all 15 cells covered, M21=0)')
    details.extend(f'  - {u}' for u in uncovered)
    return details


def metric_21_root_cause_coverage() -> dict:
    """5 病根 × 3 要素覆盖缺口数（#ARCH-GOV-CONVERGENCE-META Phase 3.6）。

    病根治本闭环指标：ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §二 定义的 5 个病根，
    每个病根需 3 要素治本闭环（持久化 + 可发现 + 可阻断）。
    M21 = 未覆盖 cell 数（15 - covered）。

    - M21=0：全部 15 cell 覆盖（5 病根全部完成 3 要素治本闭环）
    - M21>0：仍有病根的治本未闭环（通常 enforceability gap——warn-only 未转 gate）
    - convergence_map 不存在/解析失败 → fail-open，count=0 + error

    3 要素定义（对标 capability_canonical_file_registry 治本闭环模式）：
      - persistence（持久化）：治本方案持久化到 YAML/DB
      - discoverability（可发现）：新 AI 可通过 registry/MCP/metric 发现
      - enforceability（可阻断）：commit gate 硬阻断违规

    数据真源：docs/01_policies_and_standards/_registry/catalogs/governance_convergence_map.yaml
              → root_cause_coverage section
    """
    import yaml as _yaml

    map_path = REPO_ROOT / _CONVERGENCE_MAP_REL
    if not map_path.exists():
        return _make_metric('M21', '5病根×3要素覆盖缺口数', 0,
            details=[f'convergence map not found: {_CONVERGENCE_MAP_REL}'],
            source='inline', error='convergence map not found')

    try:
        data = _yaml.safe_load(map_path.read_text(encoding='utf-8'))
    except Exception as e:  # noqa: BLE001 — fail-open
        return _make_metric('M21', '5病根×3要素覆盖缺口数', 0,
            details=[f'YAML parse failed: {e}'], source='inline',
            error=f'YAML parse failed: {e}')

    if not isinstance(data, dict):
        return _make_metric('M21', '5病根×3要素覆盖缺口数', 0,
            details=['convergence map top-level not dict'],
            source='inline', error='invalid structure')

    rc_data = data.get('root_cause_coverage', {})
    if not isinstance(rc_data, dict):
        return _make_metric('M21', '5病根×3要素覆盖缺口数', 0,
            details=['root_cause_coverage section missing'],
            source='inline', error='root_cause_coverage missing')

    root_causes = rc_data.get('root_causes', []) or []
    if not root_causes:
        return _make_metric('M21', '5病根×3要素覆盖缺口数', 0,
            details=['root_causes list empty'],
            source='inline', error='root_causes empty')

    total, covered, uncovered = _scan_root_cause_cells(root_causes)

    summary = rc_data.get('coverage_summary', {}) or {}
    declared_uncovered = (
        summary.get('uncovered_cells') if isinstance(summary, dict) else None
    )

    details = _format_coverage_details(total, covered, uncovered, declared_uncovered)

    # M21 = 实际扫描的未覆盖数（非声明值——扫描是真源）
    return _make_metric('M21', '5病根×3要素覆盖缺口数', len(uncovered),
        details=details, source=_CONVERGENCE_MAP_REL)


# ── 指标 22：docstring 覆盖率倒数（5.42 代码注释与 API 文档）────────────────


def _has_docstring(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """判定函数节点是否有 docstring（body[0] 是 ast.Constant(str)）。"""
    if not node.body:
        return False
    first = node.body[0]
    return (
        isinstance(first, ast.Expr)
        and isinstance(first.value, ast.Constant)
        and isinstance(first.value.value, str)
    )


def metric_22_docstring_coverage() -> dict:
    """docstring 覆盖率倒数（5.42 代码注释与 API 文档，P1 防复发）。

    病根：5.42 HIGH 严重度 + PERMANENT-1，AI 可发现性依赖 docstring。
    检测：AST 扫描 src/zephyr/ 公共函数（非 _ 开头）无 docstring 计数。
    范围：src/zephyr/**/*.py，排除 tests/_archive/__pycache__。
    豁免：无（warn-only 趋势监控）。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        tree, _ = _scan_py_file_ast(fp)
        if tree is None:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            # 仅公共函数（非 _ 开头）
            if node.name.startswith("_"):
                continue
            if _has_docstring(node):
                continue
            violations.append(f"{rel}:{node.lineno} {node.name}")
    return _make_metric("M22", "docstring 覆盖率倒数(公共函数无 docstring)", len(violations), violations, "inline")


# ── 指标 23：asyncio.run/get_event_loop 调用数（5.100 异步资源生命周期）────


_ASYNCIO_CALL_RE = re.compile(r"\b(asyncio\.run|get_event_loop)\s*\(")


def metric_23_asyncio_calls() -> dict:
    """asyncio.run/get_event_loop 调用数（5.100 异步资源生命周期，P1 防复发）。

    病根：5.100 PERMANENT-2 + 12+ 文件 asyncio.run/get_event_loop，wontfix 但需趋势监控防增量。
    检测：正则扫描 src/zephyr/ + scripts/governance/ 中 asyncio.run( / get_event_loop( 调用。
    范围：生产代码，排除 tests/_archive。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        try:
            source = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for line_no, line in enumerate(source.splitlines(), 1):
            if _ASYNCIO_CALL_RE.search(line):
                violations.append(f"{rel}:{line_no} {line.strip()[:80]}")
    return _make_metric("M23", "asyncio.run/get_event_loop 调用数", len(violations), violations, "inline")


# ── 指标 26：TODO/FIXME 技术债务标记（5.139）──────────────────────────────


_TODO_FIXME_RE = re.compile(r"#\s*(TODO|FIXME)\b", re.IGNORECASE)


def metric_26_todo_fixme() -> dict:
    """TODO/FIXME 计数（5.139 技术债务标记，P1 防复发）。

    病根：5.139 FIXED + 零检出，metric 监控防新增 TODO/FIXME 污染。
    检测：正则扫描 # TODO / # FIXME（大小写不敏感）。
    范围：生产代码，排除 tests/_archive。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        try:
            source = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for line_no, line in enumerate(source.splitlines(), 1):
            if _TODO_FIXME_RE.search(line):
                violations.append(f"{rel}:{line_no} {line.strip()[:80]}")
    return _make_metric("M26", "TODO/FIXME 计数", len(violations), violations, "inline")


# ── 指标 27：open() 未在 with 语句（5.144 资源清理顺序）─────────────────────


def _is_open_call(node: ast.AST) -> bool:
    """判定节点是否为 open() 调用。"""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    return isinstance(func, ast.Name) and func.id == "open"


def metric_27_open_not_in_with() -> dict:
    """open() 未在 with 语句计数（5.144 资源清理顺序，P1 防复发）。

    病根：5.144 FIXED + finally 模式已批量落地，metric 监控防回归。
    检测：AST 扫描 open() 调用不在 with 上下文管理器内。
    范围：生产代码，排除 tests/_archive。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        tree, _ = _scan_py_file_ast(fp)
        if tree is None:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        # 收集所有 with 语句内的 open() 调用行号集合
        with_open_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                for item in node.items:
                    if _is_open_call(item.context_expr):
                        with_open_lines.add(item.context_expr.lineno)
        # 找出不在 with 内的 open() 调用
        for node in ast.walk(tree):
            if not _is_open_call(node):
                continue
            if node.lineno in with_open_lines:
                continue
            violations.append(f"{rel}:{node.lineno} open() not in with")
    return _make_metric("M27", "open() 未在 with 语句计数", len(violations), violations, "inline")


# ── 指标 29：资源未在 try/finally（5.169 文件句柄/资源泄漏）──────────────────


def _is_resource_acquire(node: ast.AST) -> bool:
    """判定节点是否为资源获取调用（acquire/__enter__/Lock()/open()）。"""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    # 直接名调用：open() / Lock() / Semaphore() 等
    if isinstance(func, ast.Name) and func.id in ("open", "Lock", "Semaphore", "RLock"):
        return True
    # 方法调用：xxx.acquire() / xxx.__enter__()
    if isinstance(func, ast.Attribute) and func.attr in ("acquire", "__enter__"):
        return True
    return False


def metric_29_resource_not_in_try_finally() -> dict:
    """资源未在 try/finally 计数（5.169 文件句柄/资源泄漏，P1 防复发）。

    病根：5.169 FIXED + try/finally 已批量包装，与 5.144 同族防回归。
    检测：AST 扫描 acquire/release 模式不在 try/finally 内。
    范围：生产代码，排除 tests/_archive。
    简化策略：只统计 acquire 调用（open()/Lock()/acquire()）不在 try 块内。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        tree, _ = _scan_py_file_ast(fp)
        if tree is None:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        # 收集所有 Try 节点（含 finally）覆盖的行号范围
        try_lines: set[int] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                start = node.lineno
                end = getattr(node, "end_lineno", start)
                for i in range(start, end + 1):
                    try_lines.add(i)
        # 收集所有 with 语句覆盖的行号范围（with 等价于 try/finally）
        for node in ast.walk(tree):
            if isinstance(node, ast.With):
                start = node.lineno
                end = getattr(node, "end_lineno", start)
                for i in range(start, end + 1):
                    try_lines.add(i)
        # 找出不在 try/finally/with 内的资源获取
        for node in ast.walk(tree):
            if not _is_resource_acquire(node):
                continue
            if node.lineno in try_lines:
                continue
            violations.append(f"{rel}:{node.lineno} resource acquire not in try/finally")
    return _make_metric("M29", "资源未在 try/finally 计数", len(violations), violations, "inline")


# ── 指标 24：字段遮蔽计数（5.101 变量遮蔽与命名冲突）─────────────────────────


# 内置名遮蔽检测集（5.101: 42 处数据类字段遮蔽内置名）
_BUILTIN_NAME_SHADOWS: frozenset[str] = frozenset({
    "id", "file", "type", "format", "hash", "open", "input", "round",
    "list", "dict", "set", "tuple", "str", "int", "float", "bool", "bytes",
    "map", "filter", "range", "len", "print", "sum", "min", "max", "sorted",
})


def _is_dataclass_or_basemodel(node: ast.ClassDef) -> bool:
    """判定类是否为 dataclass 或 Pydantic BaseModel 子类（字段遮蔽检测范围）。"""
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "dataclass":
            return True
        if isinstance(dec, ast.Attribute) and dec.attr == "dataclass":
            return True
    for base in node.bases:
        if isinstance(base, ast.Name) and base.id in {"BaseModel", "BaseSettings"}:
            return True
        if isinstance(base, ast.Attribute) and base.attr in {"BaseModel", "BaseSettings"}:
            return True
    return False


def metric_24_field_shadowing() -> dict:
    """字段遮蔽计数（5.101 变量遮蔽与命名冲突，P2 防复发）。

    病根：5.101 PERMANENT-12 + 42 处数据类字段遮蔽内置名。wontfix（R80 裁定
    实例属性不参与作用域链），但需 metric 监控趋势防增量。
    检测：AST 扫描 dataclass/BaseModel 类的字段名（AnnAssign target）是否
    遮蔽内置名（id/file/type/format/hash/open/input/round 等）。
    范围：src/zephyr/**/*.py，排除 tests/_archive。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        tree, _ = _scan_py_file_ast(fp)
        if tree is None:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if not _is_dataclass_or_basemodel(node):
                continue
            for stmt in node.body:
                if not isinstance(stmt, ast.AnnAssign):
                    continue
                if not isinstance(stmt.target, ast.Name):
                    continue
                field_name = stmt.target.id
                if field_name in _BUILTIN_NAME_SHADOWS:
                    violations.append(f"{rel}:{stmt.lineno} {node.name}.{field_name}")
    return _make_metric("M24", "字段遮蔽计数(dataclass/BaseModel 字段遮蔽内置名)", len(violations), violations, "inline")


# ── 指标 25：模块级常量未标 Final 计数（5.114 Final/@final 强制）────────────


def _is_literal_constant(node: ast.AST) -> bool:
    """判定节点是否为字面量常量（模块级常量候选）。"""
    if isinstance(node, ast.Constant):
        return True
    if isinstance(node, (ast.List, ast.Tuple, ast.Set, ast.Dict)):
        return True
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        return isinstance(node.operand, ast.Constant)
    return False


def _is_final_annotation(annotation: ast.AST) -> bool:
    """判定注解是否为 Final[...] 形式。"""
    if isinstance(annotation, ast.Name) and annotation.id == "Final":
        return True
    if isinstance(annotation, ast.Subscript):
        if isinstance(annotation.value, ast.Name) and annotation.value.id == "Final":
            return True
        if isinstance(annotation.value, ast.Attribute) and annotation.value.attr == "Final":
            return True
    return False


def _check_module_const_assign(stmt: ast.Assign, rel) -> str | None:
    """检查模块级 Assign（CONST_NAME = value）是否为未标 Final 的字面量常量。

    返回违规描述字符串，或 None 表示无违规。
    """
    if len(stmt.targets) != 1:
        return None
    target = stmt.targets[0]
    if not isinstance(target, ast.Name):
        return None
    if not target.id.isupper():
        return None
    if _is_literal_constant(stmt.value):
        return f"{rel}:{stmt.lineno} {target.id} (无 Final 标注)"
    return None


def _check_module_const_annassign(stmt: ast.AnnAssign, rel) -> str | None:
    """检查模块级 AnnAssign（CONST_NAME: T = value）是否为未标 Final 的字面量常量。

    返回违规描述字符串，或 None 表示无违规。
    """
    if not isinstance(stmt.target, ast.Name):
        return None
    if not stmt.target.id.isupper():
        return None
    if stmt.value is None:
        return None
    if _is_final_annotation(stmt.annotation):
        return None
    if _is_literal_constant(stmt.value):
        return f"{rel}:{stmt.lineno} {stmt.target.id} (注解非 Final)"
    return None


def metric_25_module_const_missing_final() -> dict:
    """模块级常量未标 Final 计数（5.114 Final/@final 强制，P2 防复发）。

    病根：5.114 FIXED + 375 处模块级常量已标注。metric 监控回归防新增未标 Final 常量。
    检测：AST 扫描模块级赋值（Assign/AnnAssign）值为字面量常量且无 Final[...] 标注。
    范围：src/zephyr/**/*.py，排除 tests/_archive。
    仅检测大写常量命名风格（CONST_NAME）。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        tree, _ = _scan_py_file_ast(fp)
        if tree is None:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for stmt in tree.body:  # 仅模块级（不递归）
            if isinstance(stmt, ast.Assign):
                v = _check_module_const_assign(stmt, rel)
                if v:
                    violations.append(v)
            elif isinstance(stmt, ast.AnnAssign):
                v = _check_module_const_annassign(stmt, rel)
                if v:
                    violations.append(v)
    return _make_metric("M25", "模块级常量未标 Final 计数", len(violations), violations, "inline")


# ── 指标 28：模块级单例无锁 double-check 计数（5.165 全局状态管理）──────────


def _class_has_instance_none(node: ast.ClassDef) -> bool:
    """检测类是否含 `_instance = None` 或 `__instance = None` 类变量。"""
    for stmt in node.body:
        if isinstance(stmt, ast.Assign):
            for tgt in stmt.targets:
                if isinstance(tgt, ast.Name) and tgt.id in ("_instance", "__instance"):
                    if isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                        return True
        elif isinstance(stmt, ast.AnnAssign):
            if isinstance(stmt.target, ast.Name) and stmt.target.id in ("_instance", "__instance"):
                if stmt.value is not None and isinstance(stmt.value, ast.Constant) and stmt.value.value is None:
                    return True
    return False


def _class_uses_lock(node: ast.ClassDef) -> bool:
    """检测类是否使用 Lock/RLock/allocate_lock 或 `with lock:` 模式。"""
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call):
            func = sub.func
            if isinstance(func, ast.Name) and func.id in ("Lock", "RLock", "allocate_lock"):
                return True
            if isinstance(func, ast.Attribute) and func.attr in ("Lock", "RLock", "allocate_lock"):
                return True
        elif isinstance(sub, ast.With):
            for item in sub.items:
                ctx = item.context_expr
                if isinstance(ctx, ast.Name) and "lock" in ctx.id.lower():
                    return True
                if isinstance(ctx, ast.Attribute) and "lock" in ctx.attr.lower():
                    return True
    return False


def metric_28_singleton_no_lock() -> dict:
    """模块级单例无锁 double-check 计数（5.165 全局状态管理，P2 防复发）。

    病根：5.165 FIXED（残留 2 项 LOW）+ ~20 处模块级单例无锁 double-check。
    metric 监控回归防新增无锁单例。
    检测：AST 扫描类中 `_instance = None` 类变量 + 同类无 Lock() 使用。
    范围：src/zephyr/**/*.py，排除 tests/_archive。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        tree, _ = _scan_py_file_ast(fp)
        if tree is None:
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef):
                continue
            if not _class_has_instance_none(node):
                continue
            if not _class_uses_lock(node):
                violations.append(f"{rel}:{node.lineno} {node.name} (单例无 Lock)")
    return _make_metric("M28", "模块级单例无锁 double-check 计数", len(violations), violations, "inline")


# ── 指标 30：ZEPHYR_ENV 枚举一致性（5.34 环境隔离）──────────────────────────


_ZEPHYR_ENV_ACCESS_RE = re.compile(
    r"os\.environ(?:\.get\(\s*['\"]ZEPHYR_ENV['\"]\s*\)|\[['\"]ZEPHYR_ENV['\"]\])"
    r"|os\.getenv\(\s*['\"]ZEPHYR_ENV['\"]\s*\)"
)


def metric_30_zephyr_env_enum_consistency() -> dict:
    """ZEPHYR_ENV 枚举一致性（5.34 环境隔离，P2 防复发）。

    病根：5.34 FIXED + ZEPHYR_ENV 与枚举不匹配历史。metric 监控回归防
    直接 os.environ["ZEPHYR_ENV"] 访问绕过 canonical 验证器（is_prod/get_environment）。
    检测：正则扫描直接访问 os.environ["ZEPHYR_ENV"] / os.environ.get("ZEPHYR_ENV")
    / os.getenv("ZEPHYR_ENV") 的位置（应通过 is_prod() / get_environment() canonical 入口）。
    范围：src/zephyr/**/*.py，排除 tests/_archive。
    """
    violations: list[str] = []
    for fp in iter_prod_py_files():
        try:
            source = fp.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        try:
            rel = fp.relative_to(REPO_ROOT)
        except ValueError:
            rel = fp
        for line_no, line in enumerate(source.splitlines(), 1):
            if _ZEPHYR_ENV_ACCESS_RE.search(line):
                violations.append(f"{rel}:{line_no} {line.strip()[:80]}")
    return _make_metric("M30", "ZEPHYR_ENV 直接访问数(绕过 canonical 验证器)", len(violations), violations, "inline")


# ── 指标 31：MCP version 字段覆盖率（5.35 API 版本管理）─────────────────────


MCP_JSON_CANDIDATES = (
    REPO_ROOT / "src" / "zephyr" / "integration" / "mcp" / "mcp.json",
    REPO_ROOT / "config" / "mcp.json",
    REPO_ROOT / "mcp.json",
)

# 向后兼容别名（R5 私有断言消除：公共 API 为主实现，_xxx 保留为别名）
_MCP_JSON_CANDIDATES = MCP_JSON_CANDIDATES


def metric_31_mcp_version_coverage() -> dict:
    """MCP version 字段覆盖率（5.35 API 版本管理，P2 防复发）。

    病根：5.35 FIXED + MCP 工具无 version 历史。metric 监控回归防新增工具无 version。
    检测：解析 mcp.json，统计 tools 数组中无 "version" 字段的工具数。
    范围：mcp.json（候选路径：src/zephyr/integration/mcp/mcp.json, config/mcp.json, mcp.json）。
    """
    mcp_path = None
    for candidate in MCP_JSON_CANDIDATES:
        if candidate.exists():
            mcp_path = candidate
            break
    if mcp_path is None:
        return _make_metric("M31", "MCP version 字段覆盖率(无 version 工具数)", 0,
            details=["mcp.json not found in candidate paths"], source="inline", error="mcp.json not found")
    try:
        data = json.loads(mcp_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return _make_metric("M31", "MCP version 字段覆盖率(无 version 工具数)", 0,
            details=[f"parse failed: {e}"], source=mcp_path.name, error=f"parse failed: {e}")
    tools: list = []
    if isinstance(data, dict):
        tools = data.get("tools") or []
    elif isinstance(data, list):
        tools = data
    if not isinstance(tools, list):
        return _make_metric("M31", "MCP version 字段覆盖率(无 version 工具数)", 0,
            details=["tools field is not a list"], source=mcp_path.name, error="invalid tools structure")
    violations: list[str] = []
    for idx, tool in enumerate(tools):
        if not isinstance(tool, dict):
            continue
        if "version" not in tool:
            name = tool.get("name", f"<tool#{idx}>")
            violations.append(f"{mcp_path.name}: tool '{name}' missing version")
    return _make_metric("M31", "MCP version 字段覆盖率(无 version 工具数)", len(violations), violations, mcp_path.name)


# ── 仪表盘主逻辑 ──────────────────────────────────────────────────────────

# 30 项指标注册表（id → 检测函数）
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
    ("M12", "异常粒度过粗(吞没型)", metric_12_broad_except_swallow),
    ("M13", "异常信息泄露(返客户端)", metric_13_exception_info_leak),
    ("M14", "ABC抽象方法完整性", metric_14_abc_completeness),
    ("M15", "depgraph新鲜度(>24h阻断数)", metric_15_depgraph_freshness),
    ("M16", "治本进度新鲜度(>90天超期数)", metric_16_remediation_progress_freshness),
    ("M17", "规则感知缺口(无门禁配对数)", metric_17_rule_perception_gap),
    # M18 reserved: 原 M18 (治理层收敛缺口数 v1) 已合并至 M19，编号保留不回收（连续性约定）
    ("M19", "治理层收敛缺口数", metric_19_governance_convergence_gap),
    ("M20", "trae_060 §5 快照漂移数", metric_20_runtime_snapshot_drift),
    ("M21", "5病根×3要素覆盖缺口数", metric_21_root_cause_coverage),
    ("M22", "docstring 覆盖率倒数(公共函数无 docstring)", metric_22_docstring_coverage),
    ("M23", "asyncio.run/get_event_loop 调用数", metric_23_asyncio_calls),
    ("M24", "字段遮蔽计数(dataclass/BaseModel 字段遮蔽内置名)", metric_24_field_shadowing),
    ("M25", "模块级常量未标 Final 计数", metric_25_module_const_missing_final),
    ("M26", "TODO/FIXME 计数", metric_26_todo_fixme),
    ("M27", "open() 未在 with 语句计数", metric_27_open_not_in_with),
    ("M28", "模块级单例无锁 double-check 计数", metric_28_singleton_no_lock),
    ("M29", "资源未在 try/finally 计数", metric_29_resource_not_in_try_finally),
    ("M30", "ZEPHYR_ENV 直接访问数(绕过 canonical 验证器)", metric_30_zephyr_env_enum_consistency),
    ("M31", "MCP version 字段覆盖率(无 version 工具数)", metric_31_mcp_version_coverage),
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
        "真源: ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四",
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


def _cleanup_old_snapshots(output_dir, max_age_days: int = 30) -> int:
    """清理过期 dashboard 快照文件（红蓝对抗维度7修复）。

    保留最近 max_age_days 天的快照，删除更早的 dashboard_*.json。
    latest.json 不在清理范围（始终保留最新）。

    Args:
        output_dir: 快照目录 Path。
        max_age_days: 保留天数，默认 30。

    Returns:
        已删除的快照文件数。
    """
    import time as _time
    try:
        cutoff = _time.time() - max_age_days * 86400
        removed = 0
        for fp in output_dir.glob("dashboard_*.json"):
            try:
                if fp.stat().st_mtime < cutoff:
                    fp.unlink()
                    removed += 1
            except OSError:
                continue
        if removed > 0:
            print(f"快照 TTL 清理：删除 {removed} 个过期快照（>{max_age_days}天）")
        return removed
    except Exception:  # noqa: BLE001 — 清理失败不阻断主流程
        return EXIT_PASS  # noqa: any-abuse — best-effort cleanup, 0=success


def main() -> int:
    """入口：解析参数，运行检测，输出报告。"""
    parser = argparse.ArgumentParser(
        description="架构健康度仪表盘（30 项指标自动化检测基线，ai_first_governance_principles.md（文档已删 2026-07-30，git 历史可查） §四 第0期）"
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
        ts = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        snapshot_path = OUTPUT_DIR / f"dashboard_{ts}.json"
        atomic_write_safe(snapshot_path, json.dumps(result, ensure_ascii=False, indent=2))
        if not args.json:
            print(f"\n快照已保存: {snapshot_path.relative_to(REPO_ROOT)}")
        # 同时更新 latest.json（供下游 always 读取最新）
        latest_path = OUTPUT_DIR / "latest.json"
        atomic_write_safe(latest_path, json.dumps(result, ensure_ascii=False, indent=2))
        # 快照 TTL 清理：保留最近 30 天，删除过期快照（红蓝对抗维度7修复）
        _cleanup_old_snapshots(OUTPUT_DIR, max_age_days=30)

    return EXIT_PASS  # warn-only 基线模式，始终 exit 0


if __name__ == "__main__":
    sys.exit(main())
