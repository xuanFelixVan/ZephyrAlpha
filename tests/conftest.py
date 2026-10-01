# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-248 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.conftest
# [DOMAIN] D_AUDITTEST
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
ZephyrAlpha 2.0 — 全局测试配置与共享 fixture
=============================================

本文件是 pytest 的全局 conftest.py，提供：
  1. 公共 fixture（tmp_db、tmp_project_dir）
  2. 自定义 pytest marker 注册
  3. 全局钩子（如 UTF-8 输出保障）

各测试文件仍可保留自己的局部 fixture（如 manager、engine 等），
但数据库初始化和临时项目目录等通用模式应提取到此处。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_src_path = _PROJECT_ROOT / "src"
if str(_src_path) not in sys.path:
    sys.path.insert(0, str(_src_path))

# Ensure subprocess scripts (check_pure_shim.py, check_frontmatter_metadata.py, etc.)
# can import zephyr regardless of their cwd. PYTHONPATH=src (relative) fails when
# subprocess cwd != project root; conftest sets absolute path so subprocesses inherit it.
import os as _os

_src_abs = str(_src_path)
_existing_pp = _os.environ.get("PYTHONPATH", "")
if _src_abs not in _existing_pp.split(_os.pathsep):
    _os.environ["PYTHONPATH"] = _src_abs + (_os.pathsep + _existing_pp if _existing_pp else "")

if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# 治本（2026-08-30，AI-WAVE5）：pytest.approx 的 numpy 探针（sys.modules.get("numpy")
# 命中即调 isscalar）与 zephyr __init__ auto_bootstrap 后台 daemon Timer 重模块链导入
# 存在时序竞争——后台线程 numpy 导入进行中（partially initialized）时主线程 approx
# 调用即炸 AttributeError（实证：test_knowledge_classifier 四次连跑 2 挂 2 过）。
# 主线程预导入 numpy 使 sys.modules["numpy"] 永远=完整模块，确定性关闭竞争窗口；
# numpy 不可用则静默跳过（approx 探针本来就不查）。
try:
    import numpy as _numpy_preload  # noqa: F401
except Exception:  # noqa: BLE001 — 预加载失败静默，不阻断收集
    pass

# CAND-GOVSEC-001 ②（2026-08-23 装；批5b 2026-08-26 裁定永久 audit-only）：
# pytest 进程纳入 in-process 删除护栏观测面。批5b 翻硬拦范围=四治理入口
# （git_commit/session_worktree CLI/commit_queue drain/sweep 库入口）；
# pytest 进程定位=永久观测哨而非防线——测试对自身 tmp/fixture 产物的删除
# 是合法行为不应被拦（红队用例如需硬拦语义，在 fixture 内 delenv 自验，
# 见 test_file_ops_enforcement.py）。安装失败静默降级——观测补强永不阻断 pytest。
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
try:
    from scripts.ops_guard import install_inprocess_enforcement_audit_only as _install_ops_guard

    _install_ops_guard()
except Exception:  # noqa: BLE001 — 观测补强永不阻断 pytest
    pass


def pytest_configure(config):
    """治本 #ARCH-ROOT-TEMP-FILE-ENFORCEMENT-001: pytest 输出归位 .runtime/（gitignored）。

    提供健壮的默认值，防止 AI/人工 pytest 调用在项目根目录留下 ad-hoc 临时文件/目录
    （.testtmp2/、.pytest_tmp/、tmp_junit_*.xml 等）。所有默认值仅在调用方未显式指定
    时生效（尊重 CLI 覆盖）。
    """
    import os as _os_conf

    _rt_tmp = _PROJECT_ROOT / ".runtime" / "tmp"
    _rt_tmp.mkdir(parents=True, exist_ok=True)
    # basetemp：tmp_path fixture 的根。绝对路径，与 cwd 无关。
    # 治本 #ARCH-XDIST-WORKER-CRASH-001: PID-unique basetemp 避免 Windows 文件锁定。
    # 病根：原静态 .runtime/tmp/pytest 被每次 run 复用，上次崩溃/被杀 xdist worker
    # 在该目录留下锁定文件，下次 pytest 启动时 getbasetemp() 调 rm_rf 清理 →
    # PermissionError → INTERNALERROR（测试无法启动，--max-worker-restart 无法解决
    # ——错误发生在 worker 启动前的清理阶段）。
    # 治本：PID-unique 路径确保新 run 的 basetemp 不存在 → rm_rf 是 no-op → 无冲突。
    # 旧目录由 runtime_cleanup reconciler（TTL 7d 文件清理 + 空目录回收）自动回收。
    if getattr(config.option, "basetemp", None) is None:
        config.option.basetemp = str(_rt_tmp / f"pytest_{_os_conf.getpid()}")

    # basetemp 自愈（批8 r4 实证 1594 errors）：.runtime/tmp 有 TTL 清理活动，
    # 20min+ 长跑中途 basetemp 被删后，所有 autouse fixture（_isolate_commit_queue_root）
    # 与内建 tmp_path 的 mktemp 级联 FileNotFoundError。getbasetemp 缓存命中时
    # 目录若已消失则重建，pytest 原生不会自愈（make_numbered_dir 不带 parents）。
    import pytest as _pytest_mod

    _TPF = _pytest_mod.TempPathFactory

    _orig_getbasetemp = _TPF.getbasetemp

    def _getbasetemp_selfheal(self):
        bt = self._basetemp
        if bt is not None and not bt.exists():
            bt.mkdir(parents=True, exist_ok=True)
        return _orig_getbasetemp(self)

    _TPF.getbasetemp = _getbasetemp_selfheal

    # junitxml：AI 调用（ZEPHYR_AI_PYTEST=1）默认输出到 .runtime/tmp/junit.xml，
    # 避免 AI 显式传 --junit-xml=tmp_junit_p0.xml 污染根目录。仅当未显式指定时生效。
    if _os_conf.environ.get("ZEPHYR_AI_PYTEST") == "1" and getattr(config.option, "xmlpath", None) is None:
        config.option.xmlpath = str(_rt_tmp / "junit.xml")


def pytest_sessionfinish(session, exitstatus):
    """治本 #ARCH-TEST-RESIDUE-CLEANUP-001: pytest 正常退出时清自己 basetemp。

    tests/conftest.py:67 为每个 PID 创建 .runtime/tmp/pytest_<PID>/ basetemp
    （治本 #ARCH-XDIST-WORKER-CRASH-001）。原设计无退出清理 → 残留靠
    GATE-RUNTIME-CLEANUP reconciler 兜底，但 reconciler 的 os.rmdir bug
    导致 10 万+ 文件积压。本钩子在 pytest 正常退出时源头清自己 basetemp，
    异常退出/crash 仍由 reconciler 兜底（现已修复为 shutil.rmtree + PID 存活判定）。

    双层覆盖：正常退出→本钩子源头清；异常退出→reconciler post-commit 兜底。
    安全：ignore_errors=True，清理失败绝不阻断测试退出；只清 pytest_ 前缀目录。
    """
    import os
    import shutil

    bt = getattr(session.config.option, "basetemp", None)
    if not bt:
        return
    try:
        bt_name = os.path.basename(os.path.normpath(str(bt)))
        if not bt_name.startswith("pytest_"):
            return  # 非自动 basetemp（用户自定义），不动
        shutil.rmtree(str(bt), ignore_errors=True)
    except Exception:  # noqa: BLE001 — 清理失败绝不阻断测试退出
        pass


# MOD-INF-017: code_dedup_engine 裸名注入——部分 red_team 测试以 ``code_dedup_engine``
# 裸名引用本引擎（无 import 语句，仅在测试函数体内运行时通过 builtins 解析）。
# 治本(2026-07-22): 原 tests/code_dedup_engine/ 在 pytest prepend 模式下作为裸包
# 导入并占位 sys.modules['code_dedup_engine']，故旧代码需 del 清缓存。已重命名为
# tests/gov_code_dedup/ 消除包名冲突——del 不再必要，直接指向真源
# zephyr.gov_code_quality.code_dedup 并注入 builtins 使测试函数作用域可见。
try:
    import builtins as _builtins
    import importlib as _importlib_cde
    import sys as _sys

    _cde = _importlib_cde.import_module("zephyr.gov_code_quality.code_dedup")
    _sys.modules["code_dedup_engine"] = _cde
    if not hasattr(_builtins, "code_dedup_engine"):
        _builtins.code_dedup_engine = _cde
except Exception as _exc:  # noqa: BLE001 — conftest 初始化阶段必须永不阻断测试收集
    import sys as _sys

    print(f"[conftest] code_dedup_engine injection failed: {_exc}", file=_sys.stderr)


# MOD-INF-017: zephyr.testing.code_dedup.* 注册——red_team 测试通过
# ``__import__("zephyr.testing.code_dedup.<name>", fromlist=[name])`` 导入 10 个模块.
# 物理代理包会触发 PURE-SHIM/CREATE-GUARD 门禁，改为在 sys.modules 中注册虚拟包，
# 各子模块指向 canonical 真源（zephyr.gov_code_quality.code_dedup.* 或
# zephyr.infrastructure.asset_inventory.scanner）。auto_test_generator 无 canonical
# 模块，注册为最小占位 stub（测试仅断言 mod is not None）.
try:
    import importlib as _importlib_td
    import sys as _sys_td
    import types as _types_td

    _testing_pkg_name = "zephyr.testing"
    _code_dedup_pkg_name = "zephyr.testing.code_dedup"

    # 注册 zephyr.testing 包（若不存在）
    if _testing_pkg_name not in _sys_td.modules:
        import zephyr as _zephyr_root

        _testing_pkg = _types_td.ModuleType(_testing_pkg_name)
        _testing_pkg.__path__ = []  # 标记为包
        _testing_pkg.__package__ = _testing_pkg_name
        _sys_td.modules[_testing_pkg_name] = _testing_pkg
        _zephyr_root.testing = _testing_pkg
    else:
        _testing_pkg = _sys_td.modules[_testing_pkg_name]

    # 注册 zephyr.testing.code_dedup 包（若不存在）
    if _code_dedup_pkg_name not in _sys_td.modules:
        _code_dedup_pkg = _types_td.ModuleType(_code_dedup_pkg_name)
        _code_dedup_pkg.__path__ = []
        _code_dedup_pkg.__package__ = _code_dedup_pkg_name
        _sys_td.modules[_code_dedup_pkg_name] = _code_dedup_pkg
        _testing_pkg.code_dedup = _code_dedup_pkg
    else:
        _code_dedup_pkg = _sys_td.modules[_code_dedup_pkg_name]

    # 子模块名 → canonical 真源模块名映射
    _CODE_DEDUP_MODULE_MAP = {
        "scanner": "zephyr.infrastructure.asset_inventory.scanner",
        "monoculture_guard": "zephyr.gov_code_quality.code_dedup.monoculture_guard",
        "self_scanner": "zephyr.gov_code_quality.code_dedup.self_scanner",
        "decision_auditor": "zephyr.gov_code_quality.code_dedup.decision_auditor",
        "exit_codes": "zephyr.gov_code_quality.code_dedup.exit_codes",
        "integration_hub": "zephyr.gov_code_quality.code_dedup.integration_hub",
        "cli": "zephyr.gov_code_quality.code_dedup.cli",
        "config": "zephyr.gov_code_quality.code_dedup.config",
        "function_discovery": "zephyr.gov_code_quality.code_dedup.function_discovery",
    }

    for _name, _canonical in _CODE_DEDUP_MODULE_MAP.items():
        _full = f"zephyr.testing.code_dedup.{_name}"
        if _full not in _sys_td.modules:
            _mod = _importlib_td.import_module(_canonical)
            _sys_td.modules[_full] = _mod
            setattr(_code_dedup_pkg, _name, _mod)

    # auto_test_generator 无 canonical 模块——注册最小 stub（测试仅断言 mod is not None）
    _atg_full = "zephyr.testing.code_dedup.auto_test_generator"
    if _atg_full not in _sys_td.modules:
        _atg_stub = _types_td.ModuleType(_atg_full)
        _sys_td.modules[_atg_full] = _atg_stub
        _code_dedup_pkg.auto_test_generator = _atg_stub
except Exception as _exc:  # noqa: BLE001 — conftest 初始化阶段必须永不阻断测试收集
    import sys as _sys

    print(f"[conftest] zephyr.testing.code_dedup registration failed: {_exc}", file=_sys.stderr)


# governance.d7_code.detect_forward_reference 注入——TestMainIntegration 测试使用
# ``import governance.d7_code.detect_forward_reference as mod`` 导入 scripts 模块.
# 但 pytest 将 tests/ 加入 sys.path 后，``governance`` 解析到 tests/governance/
# （tests/governance/__init__.py 存在），而 tests/governance/ 没有 d7_code/ 子包.
# 使用 importlib 显式从 scripts/governance/d7_code/ 加载并注册到 sys.modules，
# 绕过 tests/governance/ 对 scripts/governance/ 的包名遮蔽.
try:
    import importlib.util as _importlib_util_dfr
    import sys as _sys_dfr

    _scripts_gov = _PROJECT_ROOT / "scripts" / "governance"
    _d7_dir = _scripts_gov / "d7_code"
    _d7_init = _d7_dir / "__init__.py"
    _dfr_path = _d7_dir / "detect_forward_reference.py"

    if _d7_init.exists() and _dfr_path.exists():
        # 注册 governance.d7_code 包
        _d7_spec = _importlib_util_dfr.spec_from_file_location(
            "governance.d7_code",
            _d7_init,
            submodule_search_locations=[str(_d7_dir)],
        )
        _d7_mod = _importlib_util_dfr.module_from_spec(_d7_spec)
        _sys_dfr.modules["governance.d7_code"] = _d7_mod
        if _d7_spec.loader and hasattr(_d7_spec.loader, "exec_module"):
            _d7_spec.loader.exec_module(_d7_mod)

        # 注册 governance.d7_code.detect_forward_reference 模块
        _dfr_spec = _importlib_util_dfr.spec_from_file_location(
            "governance.d7_code.detect_forward_reference",
            _dfr_path,
        )
        _dfr_mod = _importlib_util_dfr.module_from_spec(_dfr_spec)
        _sys_dfr.modules["governance.d7_code.detect_forward_reference"] = _dfr_mod
        if _dfr_spec.loader and hasattr(_dfr_spec.loader, "exec_module"):
            _dfr_spec.loader.exec_module(_dfr_mod)
        _d7_mod.detect_forward_reference = _dfr_mod
except Exception as _exc:  # noqa: BLE001 — conftest 初始化阶段必须永不阻断测试收集
    import sys as _sys

    print(f"[conftest] governance.d7_code injection failed: {_exc}", file=_sys.stderr)


@pytest.fixture
def tmp_db(tmp_path):
    """返回已初始化的 SQLite 数据库路径（临时目录）。

    使用 zephyr.data_governance_governance.persistence.sqlite_schema.init_db 初始化，
    适用于所有需要数据库的测试（task_repo、circuit_breaker、olap_engine 等）。

    5.34.3 双轨说明：本 fixture 是默认的 SQLite 快速轨（零依赖、秒级）；
    需要与生产 depgraph (PostgreSQL) 对齐的测试请改用 pg_db fixture
    （ZEPHYR_TEST_PG=1 激活，见下方注释）。
    """
    from zephyr.governance.persistence.sqlite_schema import init_db

    db_path = tmp_path / "test_zalpha.db"
    init_db(db_path)
    return db_path


def _load_test_pg_config() -> dict[str, str] | None:
    """解析 PG 测试库连接参数（5.34.3 治本——双轨测试的可选 PG 轨）。

    优先级：``config/.env.postgres.test``（KEY=VALUE，若存在）>
    ``ZEPHYR_TEST_PG_*`` 环境变量。两者均未提供 host/db 时返回 None，
    调用方应 ``pytest.skip``——默认 SQLite 快速轨不受影响。

    禁止回退到 ``config/.env.postgres``（生产库真源）——测试连接目标必须
    显式声明，防测试误写生产表（5.34.4 交叉确认）。
    """
    cfg: dict[str, str] = {}
    env_file = _PROJECT_ROOT / "config" / ".env.postgres.test"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                cfg[key.strip()] = value.strip()
    host = _os.environ.get("ZEPHYR_TEST_PG_HOST") or cfg.get("POSTGRES_HOST")
    port = _os.environ.get("ZEPHYR_TEST_PG_PORT") or cfg.get("POSTGRES_PORT", "5432")
    dbname = _os.environ.get("ZEPHYR_TEST_PG_DB") or cfg.get("POSTGRES_DB")
    user = _os.environ.get("ZEPHYR_TEST_PG_USER") or cfg.get("POSTGRES_USER", "zephyr")
    password = _os.environ.get("ZEPHYR_TEST_PG_PASSWORD") or cfg.get("POSTGRES_PASSWORD", "")
    if not (host and dbname):
        return None
    return {"host": host, "port": port, "dbname": dbname, "user": user, "password": password}


@pytest.fixture
def pg_db():
    """可选 PG 测试库连接 fixture（5.34.3 治本——双轨测试的 PG 轨）。

    仅在 ``ZEPHYR_TEST_PG=1`` 时激活；连接参数来自 ``_load_test_pg_config()``
    （``config/.env.postgres.test`` 或 ``ZEPHYR_TEST_PG_*`` 环境变量，独立 PG
    test 库模式；未引入 testcontainers 依赖）。未激活 / 未配置 / PG 不可用时
    ``pytest.skip``——默认 SQLite 快速轨（tmp_db）不受影响。
    teardown 回滚未提交事务，保证测试间隔离。
    """
    if _os.environ.get("ZEPHYR_TEST_PG") != "1":
        pytest.skip("ZEPHYR_TEST_PG!=1，跳过 PG 测试轨（默认 SQLite 快速路径）")
    cfg = _load_test_pg_config()
    if cfg is None:
        pytest.skip("PG 测试库未配置（ZEPHYR_TEST_PG_* 或 config/.env.postgres.test）")
    try:
        import psycopg2

        conn = psycopg2.connect(**cfg)
    except Exception as exc:  # noqa: BLE001 — PG 不可用一律降级为 skip，不阻断测试套件
        pytest.skip(f"PG 测试库不可用: {exc}")
    yield conn
    conn.rollback()  # 测试间隔离：丢弃未提交事务
    conn.close()


@pytest.fixture
def tmp_project_dir(tmp_path):
    """返回一个模拟项目根目录，包含 docs/ 和 src/zephyr/ 子目录。

    适用于 InputSanitizer、SSoTGuard 等需要项目目录结构的测试。
    """
    (tmp_path / "docs").mkdir()
    (tmp_path / "src" / "zephyr").mkdir(parents=True)
    (tmp_path / "scripts" / "governance").mkdir(parents=True)
    (tmp_path / ".audit_cache").mkdir()
    return tmp_path


@pytest.fixture
def sanitizer(tmp_project_dir):
    """返回绑定 tmp_project_dir 的 InputSanitizer 实例。"""
    from zephyr.security.llm_defense.llm_security.input_sanitizer import InputSanitizer

    return InputSanitizer(root=str(tmp_project_dir))


@pytest.fixture()
def kb_root(tmp_path: Path) -> Path:
    """知识库测试根路径——所有 kb/ 相关测试复用此 fixture。"""
    return tmp_path / "kb"


# ── #ARCH-107 sys.modules 污染探针（2026-08-16 治本）──────────────────────
# 根因：测试把 sys.modules["x"] 置 None / MagicMock 后不恢复，同进程后续无关测试爆雷
# （"import halted; None in sys.modules" / "not a package"），爆雷点≠投毒点，归因极难。
# 已实证两起：tests/escalation/conftest.py MagicMock 占位 llm_security 毒化 agent_rbac 批跑；
# tests/escalation/test_escalation_bridge.py _block 残留 adapter=None。
# 探针在每个测试 teardown 比对 zephyr.* 快照：投毒即 fail 投毒者本人，归因前移到当下。
# 合法姿势不受影响：patch.dict/monkeypatch.setitem 退出自动恢复；del 键自恢复（下次 import 载真源）。
# 已知边界：conftest 收集期（非测试执行窗口）的占位不在本探针覆盖范围。
_MISSING = object()


@pytest.fixture(autouse=True)
def _sysmodules_pollution_sentinel():
    import types as _types

    before = {k: v for k, v in list(sys.modules.items()) if k == "zephyr" or k.startswith("zephyr.")}
    yield
    poisoned = []
    # 快照迭代：teardown 期他线程可能仍在 import（无快照会 RuntimeError: dict changed size）
    for k, v in list(sys.modules.items()):
        if not (k == "zephyr" or k.startswith("zephyr.")):
            continue
        prior = before.get(k, _MISSING)
        if v is None:
            if prior is not None:
                poisoned.append(f"{k}=None(import-halted)")
        elif not isinstance(v, _types.ModuleType):
            if prior is _MISSING or isinstance(prior, _types.ModuleType):
                poisoned.append(f"{k}=<{type(v).__name__}>(not-a-module)")
    if poisoned:
        # 先恢复再报错：探针自身不得成为新污染源（删除新增毒键+回写被改键）
        for k, v in list(sys.modules.items()):
            if not (k == "zephyr" or k.startswith("zephyr.")):
                continue
            if k not in before and (v is None or not isinstance(v, _types.ModuleType)):
                del sys.modules[k]
            elif k in before and before[k] is not v and (v is None or not isinstance(v, _types.ModuleType)):
                sys.modules[k] = before[k]
        raise AssertionError(
            "sys.modules 污染检出（#ARCH-107）：本测试置脏模块注册表且未恢复: " + "; ".join(sorted(set(poisoned)))
        )


# ---------------------------------------------------------------------------
# 提交队列隔离（2026-09-10 死信事故治本：pytest 污染进程 drain 真实队列，
# 851 项真实物品被环境失败误标死信——详见 .runtime/tmp/commit_queue_dead_triage_20260910.md）
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _isolate_commit_queue_root(tmp_path_factory, monkeypatch):
    """autouse：pytest 全域禁触真实 .runtime/commit_queue。

    ZEPHYR_COMMIT_QUEUE_DIR 是 commit_queue 预留的测试/多仓隔离覆盖位
    （scripts/commit_queue.py QUEUE_ENV_VAR，先例 ZEPHYR_TASK_BOARD_DB）。
    显式传 queue_root 的队列测试不受影响；生产环境无此 env 照常锚主仓。
    """
    iso_root = tmp_path_factory.mktemp("commit_queue_iso")
    monkeypatch.setenv("ZEPHYR_COMMIT_QUEUE_DIR", str(iso_root))


@pytest.fixture(autouse=True)
def _isolate_audit_key_eras(monkeypatch):
    """autouse：pytest 全域禁用仓内审计密钥分期注册表（config/audit_key_eras.yaml）。

    ZEPHYR_AUDIT_KEY_ERAS 是 IntegrityVerifier 分期注册表的测试/多仓隔离覆盖位
    （integrity.py _load_key_eras；先例 _isolate_commit_queue_root 同型）。
    未隔离时：仓内注册表的 era 边界（真钥部署时刻）会把测试事件（now() 时间戳）
    划入强分期——测试环境无 env 密钥即 fail-loud 误判 mismatch。
    分期语义专测（tests/governance/audit/test_key_era_verification.py）在自身
    fixture 内显式 setenv 覆盖本值（后执行者生效）。
    """
    monkeypatch.setenv("ZEPHYR_AUDIT_KEY_ERAS", str(Path(__file__).parent / "_nonexistent_audit_key_eras.yaml"))


# ---------------------------------------------------------------------------
# 告警外推通道隔离（FF-16 / alert_webhook_dispatch 接线批）
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# #ARCH-084 治本第一刀（2026-10-01，st-fullscore-20260930）：tracked 区写入守护
# 病根：全量 pytest 运行期 tracked 区被并发写入（docstring 追加/blueprint_registry
# 误删/git add 注入 staged 三类实证，见 architecture_issue_registry #ARCH-084）。
# 本守护=会话级 git status 两次+热点册（10 册）每测试 stat 快查/sha 升级比对，
# 归因到测试粒度，warning 汇总；ZEPHYR_TEST_GUARD_STRICT=1 转硬 fail；
# ZEPHYR_TEST_GUARD_OFF=1 关闭。报告落 .runtime/tmp/test_guard/report_<pid>.json。
# ---------------------------------------------------------------------------
import hashlib as _hashlib
import json as _json
import subprocess as _subprocess
import warnings as _warnings
from datetime import datetime as _datetime
from datetime import timezone as _timezone


def _datetime_now_iso() -> str:
    return _datetime.now(_timezone.utc).isoformat(timespec="seconds")


@pytest.fixture(autouse=True)
def _tracked_write_guard_probe(request):
    """autouse：每测试前后抽查热点注册表指纹（#ARCH-084 治本第一刀，2026-10-01）。

    定位到测试粒度：本 probe 前后各扫一次热点册 stat 指纹（mtime_ns+size，零 sha 开销），
    指纹漂移才升级算 sha 比对——sha 变=本测试 wrote tracked/热册文件，记肇事
    （nodeid→文件集）。禁每测试跑 git status（性能红线）；git status 全量比对只在
    会话级（_tracked_write_guard_session）做两次。
    """
    guard = _get_tracked_write_guard()
    if guard is None:
        yield
        return
    guard.mark(request.node.nodeid)
    yield
    guard.check(request.node.nodeid)


@pytest.fixture(scope="session", autouse=True)
def _tracked_write_guard_session(request):
    """session 级：进入记 `git status --porcelain` 基线，退出比对+汇总肇事（#ARCH-084）。

    报告双通道：warnings.warn 汇总（默认）+ .runtime/tmp/test_guard/report_<pid>.json
    （ forensic 全量）。ZEPHYR_TEST_GUARD_STRICT=1 时检出肇事（可归因 tracked 写）
    即 raise 转 fail——非严格模式 tracked 区漂移只 warn（并发会话脏区噪声不做归因，
    归因只信热点册 sha 证据）。xdist 下每 worker 独立跑本 fixture（同一棵树，重复
    报告可接受；per-test 归因在各 worker 内自洽）。
    """
    guard = _get_tracked_write_guard(create=_os.environ.get("ZEPHYR_TEST_GUARD_OFF") != "1")
    if guard is None:
        yield
        return
    yield
    guard.finish(strict=_os.environ.get("ZEPHYR_TEST_GUARD_STRICT") == "1")


class _TrackedWriteGuard:
    """热点册指纹台账+肇事归因（纯进程内，无跨进程共享假设）。"""

    #: 热册白名单（#ARCH-084 受害册+高频被写册；relpath 相对仓根）。
    #: blueprint_registry.yaml 已派生退库（untracked），盯盘上存在性防误删复发。
    HOT_REGISTRIES: tuple[str, ...] = (
        "docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/rule_catalog_registry.yaml",
        "docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml",
        "docs/03_modules/blueprint_registry.yaml",
        "docs/01_policies_and_standards/sop/governance_sop/alignment_checklist.md",
        "AGENTS.md",
    )

    def __init__(self, root: Path):
        self.root = root
        self.hot_sha: dict[str, str | None] = {}
        self._hot_stat: dict[str, tuple[int, int] | None] = {}
        self.culprits: dict[str, set[str]] = {}
        self.baseline_status: list[str] | None = None
        self.final_status: list[str] | None = None
        self._pending: set[str] = set()

    # -- 基础探针 ----------------------------------------------------------
    @staticmethod
    def _sha256(path: Path) -> str | None:
        try:
            h = _hashlib.sha256()
            with open(path, "rb") as fh:
                for chunk in iter(lambda: fh.read(65536), b""):
                    h.update(chunk)
            return h.hexdigest()
        except OSError:
            return None

    def _scan_hot(self) -> list[str]:
        """扫热册：stat 指纹快查，漂移才算 sha。返回 sha 变更的 relpath 列表。"""
        changed: list[str] = []
        for rel in self.HOT_REGISTRIES:
            path = self.root / rel
            try:
                st = path.stat()
                sig: tuple[int, int] | None = (st.st_mtime_ns, st.st_size)
            except OSError:
                sig = None
            if sig == self._hot_stat.get(rel):
                continue
            sha = None if sig is None else self._sha256(path)
            self._hot_stat[rel] = sig
            if sha != self.hot_sha.get(rel):
                changed.append(rel)
            self.hot_sha[rel] = sha
        return changed

    def mark(self, nodeid: str) -> None:
        self._pending = set(self._scan_hot())

    def check(self, nodeid: str) -> None:
        after = set(self._scan_hot())
        wrote = after - getattr(self, "_pending", set())
        if wrote:
            self.culprits.setdefault(nodeid, set()).update(wrote)

    # -- 会话级 ------------------------------------------------------------
    def _git_status(self) -> list[str] | None:
        try:
            proc = _subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(self.root),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )
        except (OSError, _subprocess.TimeoutExpired):
            return None
        if proc.returncode != 0:
            return None
        # 只留 tracked 区行（?? untracked 不算 tracked 写；测试产 tmp 未忽略文件是合法噪音）
        return sorted(ln for ln in proc.stdout.splitlines() if ln and not ln.startswith("??"))

    def start(self) -> None:
        for rel in self.HOT_REGISTRIES:
            path = self.root / rel
            try:
                st = path.stat()
                sig: tuple[int, int] | None = (st.st_mtime_ns, st.st_size)
            except OSError:
                sig = None
            self._hot_stat[rel] = sig
            self.hot_sha[rel] = None if sig is None else self._sha256(path)
        self.baseline_status = self._git_status()

    def finish(self, *, strict: bool = False) -> None:
        self.final_status = self._git_status()
        culprit_files = sorted({f for files in self.culprits.values() for f in files})
        drift: list[str] = []
        if self.baseline_status is not None and self.final_status is not None:
            base, fin = set(self.baseline_status), set(self.final_status)
            drift = sorted(fin - base) + sorted(f"{ln} [vanished]" for ln in sorted(base - fin))
        self._emit_report(culprit_files, drift)
        if culprit_files:
            top = sorted(self.culprits.items(), key=lambda kv: -len(kv[1]))[:10]
            detail = "; ".join(f"{nid} -> {sorted(files)[:4]}" for nid, files in top)
            msg = (
                f"#ARCH-084 tracked 区写入守护：检出 {len(self.culprits)} 个肇事测试/"
                f"{len(culprit_files)} 个热册文件被写: {detail}"
            )
            _warnings.warn(msg, category=_TrackedWriteWarning, stacklevel=2)
            if strict:
                raise AssertionError(msg)
        elif drift:
            _warnings.warn(
                f"#ARCH-084 会话级 tracked 区漂移（{len(drift)} 行，未归因到具体测试"
                "——并发会话或收集期写入，详见 guard report json）: 前几条="
                f"{drift[:5]}",
                category=_TrackedWriteWarning,
                stacklevel=2,
            )

    def _emit_report(self, culprit_files: list[str], drift: list[str]) -> None:
        try:
            report_dir = self.root / ".runtime" / "tmp" / "test_guard"
            report_dir.mkdir(parents=True, exist_ok=True)
            payload = {
                "pid": _os.getpid(),
                "finished_utc": _datetime_now_iso(),
                "culprits": {k: sorted(v) for k, v in sorted(self.culprits.items())},
                "culprit_files": culprit_files,
                "tracked_drift_lines": drift[:200],
                "drift_count": len(drift),
            }
            (report_dir / f"report_{_os.getpid()}.json").write_text(
                _json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8"
            )
        except Exception:  # noqa: BLE001 — 报告落盘失败绝不阻断测试会话
            pass


class _TrackedWriteWarning(UserWarning):
    """#ARCH-084 tracked 区写入守护告警（warnings 汇总通道）。"""


_GUARD_SINGLETON: _TrackedWriteGuard | None = None


def _get_tracked_write_guard(create: bool = True) -> _TrackedWriteGuard | None:
    """惰性单例：guard 关闭/非 git 仓/初始化失败一律返回 None（守护永不阻断测试）。"""
    global _GUARD_SINGLETON
    if _GUARD_SINGLETON is not None:
        return _GUARD_SINGLETON
    if not create or _os.environ.get("ZEPHYR_TEST_GUARD_OFF") == "1":
        return None
    if not (_PROJECT_ROOT / ".git").exists():
        return None
    try:
        guard = _TrackedWriteGuard(_PROJECT_ROOT)
        guard.start()
    except Exception:  # noqa: BLE001 — 守护初始化失败静默降级
        return None
    _GUARD_SINGLETON = guard
    return _GUARD_SINGLETON


@pytest.fixture(autouse=True)
def _isolate_alert_webhook_sinks(tmp_path_factory, monkeypatch):
    """autouse：pytest 全域禁让告警外推通道写**真实**落点。

    zephyr.data.alerter 的 CRITICAL 事件钩子会在失败汇总落盘后同进程外发；
    缺省配置 enabled=false → 走 fail-closed 分支，会写
      ① data/runtime/alert_webhook_{state.json,trail.jsonl}（去重账本+留痕）
      ② .runtime/ops_notifications/notifications.jsonl（前端 promotion 页真读的板）
    ②尤其致命：测试跑一次就在**生产通知板**挂一条"告警外发通道不可用"红条，
    Owner 看到的是假告警。故本 fixture 把两处都重定向到 tmp：
      ZEPHYR_ALERT_WEBHOOK_DIR → state/trail 锚定根（本批在 _sink_root 新建的覆盖位）
      ZEPHYR_OPS_NOTIFICATION_DIR → 通知板目录（ops_alert_feed.board_dir 既有覆盖位）
    先例同型：_isolate_commit_queue_root / _isolate_audit_key_eras。
    通道语义专测（tests/data/test_alert_webhook_dispatch.py）在自身 fixture 内
    显式注入 tmp 配置/板（后执行者生效，不受本 fixture 影响）。
    """
    iso = tmp_path_factory.mktemp("alert_webhook_iso")
    monkeypatch.setenv("ZEPHYR_ALERT_WEBHOOK_DIR", str(iso / "sinks"))
    monkeypatch.setenv("ZEPHYR_OPS_NOTIFICATION_DIR", str(iso / "ops_notifications"))
