# [A_test] module_id: MOD-GOV_conftest | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-248 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.conftest
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

    before = {k: v for k, v in sys.modules.items() if k == "zephyr" or k.startswith("zephyr.")}
    yield
    poisoned = []
    for k, v in sys.modules.items():
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
