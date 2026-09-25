# [A_test] module_id: MOD-INF-002 | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] tests.infrastructure.test_duckdb_runtime_gate
# [INVARIANTS] 审计/配置一律 tmp_path 注入（测试隔离铁律：禁写生产路径）；每用例 teardown uninstall 防 patch 泄漏
# [CONSUMERS] pytest（tests/infrastructure）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即用例失败；子进程超时 120/180s 硬顶
# [TESTS] pytest tests/infrastructure/test_duckdb_runtime_gate.py -q
# [TTL] permanent

"""duckdb_runtime_gate 红绿测试（M3-C1：裸 duckdb.connect 运行时拦截）。

三命覆盖（挖矿册 docs/_working/fullflow_mining/m3_governance/04_coverage_gaps.md T1）：
1. 未拦截时裸 ``duckdb.connect(":memory:")`` 成功（子进程、门未安装）——证明拦截
   不是 duckdb 自带行为，红测基线。
2. 拦截后裸 connect 被捕获：warn 模式=成功放行+审计 jsonl 落账；block 模式=抛
   ``BareDuckDBConnectError`` + 审计落账；白名单调用点豁免=零审计噪音；
   meta_path finder 对"安装后首次导入"的 duckdb 同样生效。
3. DatabaseService 正常路径不受扰（门安装时 sqlite 治理连接照常、零审计）。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path

import duckdb
import pytest

from zephyr.infrastructure.duckdb_runtime_gate import (
    BareDuckDBConnectError,
    install,
    is_installed,
    uninstall,
)

_WT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _gate_cleanup():
    """每用例后卸载拦截器，防 duckdb.connect patch 泄漏到同进程其他测试。"""
    yield
    uninstall()


def _read_audit(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _tmp_config(tmp_path: Path, mode: str = "warn") -> Path:
    cfg = tmp_path / "flags_test.yaml"
    cfg.write_text(
        textwrap.dedent(
            f"""
            version: "test"
            flags:
              duckdb_runtime_gate:
                enabled: true
                mode: "{mode}"
            """
        ).lstrip(),
        encoding="utf-8",
    )
    return cfg


# ============================================================================
# 命 1：未拦截时裸 connect 成功（红测基线）
# ============================================================================


def test_unpatched_bare_connect_succeeds_subprocess() -> None:
    """门未安装的干净进程里裸 duckdb.connect 正常工作。"""
    code = "import duckdb; c = duckdb.connect(':memory:'); print('OK', c.execute('select 41+1').fetchone()[0])"
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["ZEPHYR_RUNTIME_GATE"] = "0"  # 双保险：即便解释器引导存在也不许装门
    proc = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "OK 42" in proc.stdout


# ============================================================================
# 命 2：拦截后裸 connect 被捕获审计
# ============================================================================


def test_warn_mode_bare_connect_captured_and_audited(tmp_path: Path) -> None:
    audit = tmp_path / "duckdb_runtime_gate.jsonl"
    assert install(audit_path=audit, config_path=_tmp_config(tmp_path)) is True
    assert is_installed() is True

    # 测试模块不在默认白名单——裸 connect 属被拦面
    conn = duckdb.connect(":memory:")
    assert conn.execute("select 41+1").fetchone()[0] == 42  # warn 模式放行不破坏功能
    conn.close()

    events = _read_audit(audit)
    assert len(events) == 1
    ev = events[0]
    assert ev["gate"] == "duckdb_runtime_gate"
    assert ev["action"] == "warn"
    assert ev["caller_module"] == __name__
    assert ev["database"] == ":memory:"
    assert ev["schema_version"] == "1.0"
    assert ev["event_id"]


def test_block_mode_raises_and_audits(tmp_path: Path) -> None:
    audit = tmp_path / "duckdb_runtime_gate.jsonl"
    assert install(audit_path=audit, config_path=_tmp_config(tmp_path, mode="block")) is True
    with pytest.raises(BareDuckDBConnectError):
        duckdb.connect(":memory:")
    events = _read_audit(audit)
    assert len(events) == 1
    assert events[0]["action"] == "block"
    assert events[0]["caller_module"] == __name__


def test_allowlisted_caller_exempt(tmp_path: Path) -> None:
    audit = tmp_path / "duckdb_runtime_gate.jsonl"
    assert (
        install(
            audit_path=audit,
            config_path=_tmp_config(tmp_path),
            allowlist=(__name__, "zephyr.infrastructure.database_service"),
        )
        is True
    )
    conn = duckdb.connect(":memory:")
    assert conn.execute("select 7").fetchone()[0] == 7
    conn.close()
    assert _read_audit(audit) == []  # 白名单调用点豁免：零审计噪音


def test_meta_path_finder_patches_future_import(tmp_path: Path) -> None:
    """安装后"首次导入"的 duckdb 也被 patch（meta_path finder 路径，子进程隔离）。"""
    audit = tmp_path / "audit_out" / "duckdb_runtime_gate.jsonl"
    script = tmp_path / "bootstrap_probe.py"
    script.write_text(
        textwrap.dedent(
            f"""
            import sys

            sys.path.insert(0, r"{_WT_ROOT / "src"}")
            from zephyr.infrastructure.duckdb_runtime_gate import install

            install(audit_path=r"{audit}")
            import duckdb  # 安装后首次导入 -> meta_path finder patch 生效

            conn = duckdb.connect(":memory:")
            print("REACHED", conn.execute("select 1").fetchone()[0])
            """
        ).lstrip(),
        encoding="utf-8",
    )
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    proc = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True,
        text=True,
        env=env,
        cwd=str(tmp_path),
        timeout=180,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert "REACHED 1" in proc.stdout  # warn 模式放行
    events = _read_audit(audit)
    assert len(events) == 1
    assert events[0]["action"] == "warn"
    assert events[0]["caller_module"] == "__main__"


def test_install_idempotent_and_uninstall_restores(tmp_path: Path) -> None:
    audit = tmp_path / "duckdb_runtime_gate.jsonl"
    assert install(audit_path=audit, config_path=_tmp_config(tmp_path)) is True
    assert install(audit_path=audit, config_path=_tmp_config(tmp_path)) is True  # 幂等
    assert is_installed() is True
    uninstall()
    assert is_installed() is False
    # 卸载后裸 connect 不再被拦（block 模式下原函数已还原，正常建连）
    conn = duckdb.connect(":memory:")
    assert conn.execute("select 3").fetchone()[0] == 3
    conn.close()
    assert _read_audit(audit) == []


def test_kill_switch_disables_install(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ZEPHYR_RUNTIME_GATE", "0")
    assert install(audit_path=tmp_path / "a.jsonl", config_path=_tmp_config(tmp_path)) is False
    assert is_installed() is False


def test_disabled_flag_disables_install(tmp_path: Path) -> None:
    cfg = tmp_path / "flags_off.yaml"
    cfg.write_text(
        textwrap.dedent(
            """
            version: "test"
            flags:
              duckdb_runtime_gate:
                enabled: false
                mode: "warn"
            """
        ).lstrip(),
        encoding="utf-8",
    )
    assert install(audit_path=tmp_path / "a.jsonl", config_path=cfg) is False
    assert is_installed() is False


# ============================================================================
# 命 3：DatabaseService 正常路径不受扰
# ============================================================================


def test_database_service_normal_path_unaffected(tmp_path: Path) -> None:
    audit = tmp_path / "duckdb_runtime_gate.jsonl"
    assert install(audit_path=audit, config_path=_tmp_config(tmp_path)) is True

    from zephyr.infrastructure.database_service import DatabaseService

    ds = DatabaseService()
    try:
        conn = ds.get_governance_conn(read_only=True)
        assert conn.execute("SELECT 1").fetchone()[0] == 1
    finally:
        ds.close_all()

    assert _read_audit(audit) == []  # DatabaseService 路径零 duckdb、零告警
