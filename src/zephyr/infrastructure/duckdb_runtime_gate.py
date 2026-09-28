# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md
# [MODULE] zephyr.infrastructure.duckdb_runtime_gate
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] zephyr.infrastructure.database_service（白名单豁免对象，惰性不导入）
# [CONSUMERS] zephyr.infrastructure.__init__（discoverability re-export）；sitecustomize/usercustomize 引导链（B1 接线另批）；tests/infrastructure/test_duckdb_runtime_gate.py
# [STARTUP] manual
# [MATURITY] evolving
# [INVARIANTS] 裸 duckdb.connect 运行时拦截（宪法 §9.1 运行时侧补齐，M3-C1/T1）——对齐 runtime_interceptor 模式：
#   eager patch + sys.meta_path finder 双覆盖；白名单（DatabaseService 自身 + 既有直连点 zephyr.factor.offline_store）
#   按调用栈任意帧命中即豁免（防包装间接层审计噪音）；动作出厂 warn+审计 jsonl，block 翻转属 Owner 门位
#   （config/flags.yaml flags.duckdb_runtime_gate.mode）；ZEPHYR_RUNTIME_GATE=0 kill-switch 双重尊重；
#   门逻辑自身异常一律 fail-open 放行（宁可漏拦不破坏建连链），审计写失败仅告警；
#   install 幂等 / uninstall 还原原函数；审计字段 schema_version="1.0" 固定。
# [MODIFY-GUARD] RULE-SSOT：mode/enabled 出厂值真源=config/flags.yaml，本模块 default 仅兜底
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] install 返回 bool 永不抛；uninstall 永不抛；被拦 connect 仅在 block 模式抛
#   BareDuckDBConnectError，其余异常 fail-open 放行原函数
# [TESTS] tests/infrastructure/test_duckdb_runtime_gate.py
# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
duckdb_runtime_gate.py — 裸 duckdb.connect 运行时拦截器（bare_sql_gate 的运行时后备防线）

对标：宪法 §9.1 运维红线 "数据库访问：禁裸 duckdb.connect / 裸 SQL 散落——一律 DatabaseService"。

背景（挖矿册 docs/_working/fullflow_mining/m3_governance/04_coverage_gaps.md T1）：
bare_sql_gate 是 pre-commit 静态门，运行时侧此前零拦截零审计——"只有门没有运行时"
的单侧覆盖真空。本模块对齐 runtime_interceptor（GATE-20 后备防线）的成熟模式，
把同构防线平移到 duckdb.connect 面。

机制：
1. install() 对已导入的 duckdb 立即 monkey-patch ``duckdb.connect``（eager patch）；
   未导入时经 ``sys.meta_path`` finder 在"安装后首次导入"完成后补 patch——与
   runtime_interceptor._LLMGuardFinder 同构。
2. 被 patch 的 connect 在调用时做调用栈豁免判定：栈上任一非门/非 duckdb 帧所属模块
   命中白名单（默认=DatabaseService 自身 + 既有直连点 offline_store.py:329）→ 静默放行
   （零审计噪音）；否则按 mode 处置——
   - warn（出厂）：放行 + 审计 jsonl 落账；
   - block：审计落账后抛 BareDuckDBConnectError。
3. kill-switch：ZEPHYR_RUNTIME_GATE=0 时不安装（sitecustomize 引导与 install 内部双重尊重，
   对标 runtime_interceptor）。
4. 配置真源=config/flags.yaml 的 ``flags.duckdb_runtime_gate``（enabled/mode/audit_path）；
   config_path 缺省时回读仓库 flags.yaml，读不到/解析失败回退出厂默认（enabled=warn-only）。

fail-open 铁律：本门逻辑自身任何异常（栈回溯失败/审计写失败等）一律放行原 connect——
宁可漏拦也不破坏建连链（与 runtime_interceptor "patch 失败 no-op 不阻断导入链" 同源）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: duckdb.connect 调用（args/kwargs）
#   fields: database 位置参或 kwargs；白名单=flags 配置 + install(allowlist) 并集
#   code: _guarded_connect（eager patch + _DuckDBGateFinder 导入钩子双覆盖）
# 层: 算法
# - id: A1
#   name_zh: 调用栈豁免判定
#   name_en: classify caller
#   intro: 跳过门模块/duckdb 内部帧，栈上任一其余帧命中白名单即豁免（防包装间接层噪音）
#   desc: _classify_caller；判定异常 fail-open 放行
# - id: A2
#   name_zh: 处置与审计
#   name_en: enforce and audit
#   intro: warn=审计 jsonl 落账放行；block=落账后抛 BareDuckDBConnectError；审计写失败仅告警
#   desc: _enforce/_append_audit；schema_version=1.0，event_id=uuid4
# 层: 输出
# - id: O1
#   name: 原 duckdb.connect 结果或 BareDuckDBConnectError
#   fields: 连接对象 / 异常
#   code: return orig(*args, **kwargs) / raise
# [/ALGO_FLOW]
# 边: I1 --> A1 ; A1 --> A2 ; A2 --> O1
"""

from __future__ import annotations

import importlib.abc
import importlib.machinery
import json
import logging
import os
import sys
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from zephyr.shared.foundation.errors import ErrorCodeRuntimeError

logger = logging.getLogger(__name__)

__all__: Final = [
    "BareDuckDBConnectError",
    "install",
    "uninstall",
    "is_installed",
]

# ── kill-switch（与 runtime_interceptor 同键，一次关闭全部运行时门）──
_KILL_SWITCH_ENV = "ZEPHYR_RUNTIME_GATE"

_GATE_MODULE = "zephyr.infrastructure.duckdb_runtime_gate"
_TARGET_MODULE = "duckdb"
_SCHEMA_VERSION = "1.0"
_AUDIT_EVENT_GATE = "duckdb_runtime_gate"

# ── 配置真源与出厂默认（SSOT=config/flags.yaml；此处仅兜底，勿当第二真源）──
_REPO_ROOT = Path(__file__).resolve().parents[3]
_FLAGS_PATH = _REPO_ROOT / "config" / "flags.yaml"
_DEFAULT_MODE = "warn"
_DEFAULT_AUDIT_PATH = _REPO_ROOT / ".runtime" / "audit" / "duckdb_runtime_gate.jsonl"
# 白名单豁免面（调用栈任一帧命中即豁免）：
# 1) zephyr.infrastructure.database_service — 宪法指定的唯一合法 duckdb 入口（DatabaseService 自身）；
# 2) zephyr.factor.offline_store — 既有直连点（offline_store.py:329 注入式 :memory:，挖矿册 04 §三 T1 在案灰区）。
_DEFAULT_ALLOWLIST: tuple[str, ...] = (
    "zephyr.infrastructure.database_service",
    "zephyr.factor.offline_store",
)


class BareDuckDBConnectError(ErrorCodeRuntimeError):
    """裸 duckdb.connect 被运行时门阻断（block 模式）。

    对标宪法 §9.1：数据库访问一律经 DatabaseService。受控直连须在
    config/flags.yaml flags.duckdb_runtime_gate 或 install(allowlist=...) 显式登记豁免。
    """

    error_code = "ZA-INF-0901"

    # 包5 工厂化（st-nightsweep-sw8-20260929）：__init__ 同构收编 ErrorCodeRuntimeError
    # 基类（原 extract 级克隆与 git_commit_gateway.GatewayError 同构）。


# ============================================================================
# 运行态（install/uninstall 写，guard 读；GIL 下引用读写原子，配合锁防安装竞态）
# ============================================================================

_state_lock = threading.RLock()
_audit_lock = threading.Lock()
_INSTALLED = False
_ORIG_CONNECT = None  # 首次 patch 捕获的原 duckdb.connect（uninstall 还原用）
_AUDIT_PATH: Path | None = None
_MODE: str = _DEFAULT_MODE
_ALLOWLIST: tuple[str, ...] = _DEFAULT_ALLOWLIST


def _load_settings(config_path: str | Path | None) -> tuple[bool, str, Path | None]:
    """读 flags 真源 -> (enabled, mode, audit_path)。

    config_path=None 时回读仓库 config/flags.yaml（SSOT）；文件缺失/解析异常回退出厂默认
    （enabled=True + warn-only），安装侧永不抛。
    """
    enabled, mode, audit_path = True, _DEFAULT_MODE, None
    path = Path(config_path) if config_path is not None else _FLAGS_PATH
    try:
        if path.is_file():
            import yaml

            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            entry = (data.get("flags") or {}).get(_AUDIT_EVENT_GATE) or {}
            enabled = bool(entry.get("enabled", True))
            raw_mode = str(entry.get("mode", _DEFAULT_MODE)).strip().lower()
            if raw_mode in ("warn", "block"):
                mode = raw_mode
            raw_audit = entry.get("audit_path")
            if raw_audit:
                p = Path(str(raw_audit))
                audit_path = p if p.is_absolute() else _REPO_ROOT / p
    except Exception as e:  # noqa: BLE001 — 配置读取失败回退出厂默认，安装侧永不抛
        logger.warning("duckdb_runtime_gate: 配置读取失败(%s: %s)，回退出厂默认 warn-only", type(e).__name__, e)
    return enabled, mode, audit_path


# ============================================================================
# 调用栈豁免判定
# ============================================================================


def _classify_caller() -> tuple[str, bool]:
    """回溯调用栈 -> (caller_module, exempt)。

    跳过门模块自身与 duckdb.* 内部帧；首个其余帧即直接调用点（caller_module）；
    白名单按"栈上任一其余帧命中"判定——包装/间接层不产生审计噪音。
    判定异常由调用方 fail-open 兜底。
    """
    caller = "<unknown>"
    exempt = False
    frame = sys._getframe(2)  # 0=_classify_caller 1=_guarded_connect 2=真实调用侧
    while frame is not None:
        mod_name = frame.f_globals.get("__name__", "")
        if mod_name and mod_name != _GATE_MODULE and not mod_name.startswith("duckdb"):
            if caller == "<unknown>":
                caller = mod_name
            if mod_name in _ALLOWLIST:
                exempt = True
                break
        frame = frame.f_back
    return caller, exempt


def _append_audit(caller: str, database, action: str) -> None:
    """审计 jsonl 落账（追加式；失败仅告警，绝不向建连链抛异常）。"""
    if _AUDIT_PATH is None:
        return
    event = {
        "schema_version": _SCHEMA_VERSION,
        "event_id": uuid.uuid4().hex,
        "gate": _AUDIT_EVENT_GATE,
        "action": action,
        "caller_module": caller,
        "database": str(database),
        "ts": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
    }
    try:
        _AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        line = json.dumps(event, ensure_ascii=False)
        with _audit_lock, open(_AUDIT_PATH, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except Exception as e:  # noqa: BLE001 — 审计写失败不阻断建连链（fail-open）
        logger.warning("duckdb_runtime_gate: 审计落账失败(%s: %s)", type(e).__name__, e)


def _enforce(caller: str, database) -> None:
    """按 _MODE 处置：warn=落账放行；block=落账后抛 BareDuckDBConnectError。"""
    if _MODE == "block":
        _append_audit(caller, database, "block")
        raise BareDuckDBConnectError(
            f"裸 duckdb.connect({database!r}) 被运行时门阻断 (caller={caller})"
            f" -> 数据库访问一律经 zephyr.infrastructure.database_service.DatabaseService"
            f" (宪法 §9.1); 受控直连请在 config/flags.yaml flags.duckdb_runtime_gate 白名单显式登记"
        )
    _append_audit(caller, database, "warn")
    logger.warning(
        "duckdb_runtime_gate: 裸 duckdb.connect(%r) 来自 %s（warn 放行，已审计）——一律 DatabaseService（宪法 §9.1）",
        database,
        caller,
    )


def _make_guard(orig_connect):
    """包装原 duckdb.connect：白名单静默放行；否则 warn/block 处置后走原函数。"""

    def _guarded_connect(*args, **kwargs):
        orig = _ORIG_CONNECT if _ORIG_CONNECT is not None else orig_connect
        try:
            caller, exempt = _classify_caller()
        except Exception:  # noqa: BLE001 — 门逻辑异常 fail-open 放行
            return orig(*args, **kwargs)
        if not exempt:
            database = args[0] if args else kwargs.get("database", ":memory:")
            try:
                _enforce(caller, database)
            except BareDuckDBConnectError:
                raise
            except Exception:  # noqa: BLE001 — 处置链异常不阻断建连链
                logger.warning("duckdb_runtime_gate: enforce 链异常被吞（fail-open）", exc_info=True)
        return orig(*args, **kwargs)

    _guarded_connect.__zephyr_duckdb_gate__ = True  # 防重复 patch 标记
    return _guarded_connect


def _patch_module(module) -> None:
    """对已加载的 duckdb 模块 patch connect（幂等；防御式失败 no-op 不破坏导入链）。"""
    global _ORIG_CONNECT
    connect = getattr(module, "connect", None)
    if connect is None or getattr(connect, "__zephyr_duckdb_gate__", False):
        return
    if _ORIG_CONNECT is None:
        _ORIG_CONNECT = connect
    try:
        module.connect = _make_guard(connect)
    except Exception as e:  # noqa: BLE001 — patch 失败宁可漏拦也不破坏导入链
        logger.warning("duckdb_runtime_gate: duckdb.connect patch 失败(%s: %s)", type(e).__name__, e)


# ============================================================================
# sys.meta_path 导入钩子（安装后首次导入 duckdb -> 加载完成即 patch）
# ============================================================================


class _DuckDBGateLoader(importlib.abc.Loader):
    """包装真实 loader：执行原 loader 后立即 patch 目标模块。"""

    def __init__(self, orig_loader):
        self._orig = orig_loader

    def create_module(self, spec):
        if hasattr(self._orig, "create_module"):
            return self._orig.create_module(spec)
        return None

    def exec_module(self, module):
        self._orig.exec_module(module)
        try:
            _patch_module(module)
        except Exception:  # noqa: BLE001 — 宁可漏拦也不破坏导入链
            pass


class _DuckDBGateFinder(importlib.abc.MetaPathFinder):
    """meta_path finder：仅拦 duckdb 顶层模块，其余交给默认机制。"""

    def find_spec(self, fullname, path=None, target=None):
        if fullname != _TARGET_MODULE:
            return None
        with _state_lock:
            if not _INSTALLED:
                return None
        spec = importlib.machinery.PathFinder.find_spec(fullname, path)
        if spec is None or spec.loader is None:
            return None
        spec.loader = _DuckDBGateLoader(spec.loader)
        return spec


# ============================================================================
# install / uninstall / is_installed
# ============================================================================


def install(audit_path: str | Path | None = None, config_path: str | Path | None = None, allowlist=None) -> bool:
    """安装裸 duckdb.connect 运行时门。

    Args:
        audit_path: 审计 jsonl 路径；缺省取 flags 配置 audit_path，再缺省
            ``<repo>/.runtime/audit/duckdb_runtime_gate.jsonl``。
        config_path: flags YAML 路径；缺省回读仓库 ``config/flags.yaml``（SSOT），
            测试可注入 tmp_path 配置（测试隔离铁律）。
        allowlist: 追加豁免模块名（与默认白名单取并集；None=仅默认白名单）。

    Returns:
        True=已安装（含幂等重入）；False=kill-switch 或 flags.enabled=false 未安装。
    """
    global _INSTALLED, _AUDIT_PATH, _MODE, _ALLOWLIST
    if os.environ.get(_KILL_SWITCH_ENV, "1") == "0":
        return False
    enabled, mode, cfg_audit = _load_settings(config_path)
    if not enabled:
        return False
    extra = tuple(allowlist) if allowlist else ()
    with _state_lock:
        _AUDIT_PATH = Path(audit_path) if audit_path is not None else (cfg_audit or _DEFAULT_AUDIT_PATH)
        _MODE = mode
        _ALLOWLIST = tuple(dict.fromkeys(_DEFAULT_ALLOWLIST + extra))
        if not _INSTALLED:
            sys.meta_path.insert(0, _DuckDBGateFinder())
            _INSTALLED = True
        mod = sys.modules.get(_TARGET_MODULE)
        if mod is not None:
            _patch_module(mod)
    return True


def uninstall() -> None:
    """卸载门（测试隔离用）：移除 finder 并还原原 duckdb.connect。"""
    global _INSTALLED, _ORIG_CONNECT, _AUDIT_PATH, _MODE, _ALLOWLIST
    with _state_lock:
        try:
            sys.meta_path[:] = [f for f in sys.meta_path if not isinstance(f, _DuckDBGateFinder)]
        except Exception as e:  # noqa: BLE001 — 卸载侧永不抛
            logger.warning("duckdb_runtime_gate: finder 移除异常(%s: %s)", type(e).__name__, e)
        mod = sys.modules.get(_TARGET_MODULE)
        if mod is not None and _ORIG_CONNECT is not None:
            cur = getattr(mod, "connect", None)
            if getattr(cur, "__zephyr_duckdb_gate__", False):
                try:
                    mod.connect = _ORIG_CONNECT
                except Exception as e:  # noqa: BLE001
                    logger.warning("duckdb_runtime_gate: 原函数还原异常(%s: %s)", type(e).__name__, e)
        _ORIG_CONNECT = None
        _AUDIT_PATH = None
        _MODE = _DEFAULT_MODE
        _ALLOWLIST = _DEFAULT_ALLOWLIST
        _INSTALLED = False


def is_installed() -> bool:
    """门是否处于安装态。"""
    return _INSTALLED
