# [BLUEPRINT] MOD-GOV-046 | tests/governance/test_ruff_preclean_enqueue.py | st-finaldel-crx-20260929 Rx-1
# [MODULE] tests.governance.test_ruff_preclean_enqueue
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; scripts.governance.enqueue_preflight; scripts.git_commit
# [STARTUP] python -m pytest tests/governance/test_ruff_preclean_enqueue.py
# [MATURITY] testing
# [INVARIANTS] 红例=带 ruff 违规的 .py 批被拒且处方含哪行哪规；蓝例=干净批/非 .py 批/缺失件放行；env=0 回退；大批限流 skip；设施故障 fail-open；_ruff_preclean_gate exit 8 与 --skip-preflight 逃生；全部临时文件走 tmp_path（测试隔离红线）
# [TTL] task_bound
"""test_ruff_preclean_enqueue.py — Rx-1 入队侧 ruff/format 预清验收（st-finaldel-crx-20260929）。

判据真源=仓内 pyproject.toml [tool.ruff]（与 .pre-commit-config.yaml 落地通道同一
配置）。注意：F401 已被仓配置全局 ignore（__init__.py 重导出场景），红例用仓配置
真拦的 F821 undefined-name。
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts.governance import enqueue_preflight as ep

_BAD_PY = "print(undefined_name_xyz)\n"  # F821 undefined-name（仓配置真拦；F401 已被全局 ignore）
_FMT_BAD_PY = "x=1\n"  # ruff format 会改写为 "x = 1"（check 缺省 select 不红，format 红）
_OK_PY = "x = 1\n"


def _write(tmp_path: Path, name: str, content: str) -> str:
    f = tmp_path / name
    f.write_text(content, encoding="utf-8")
    return str(f)


class TestRuffPreclean:
    @pytest.fixture(autouse=True)
    def _env_default_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(ep.RUFF_PRECLEAN_ENV, raising=False)  # 缺省 ON 口径隔离

    def test_clean_file_passes(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "ok.py", _OK_PY)
        assert ep.ruff_preclean(tmp_path, [f]) is None

    def test_non_py_batch_zero_cost(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "a.txt", "whatever\n")
        assert ep.ruff_preclean(tmp_path, [f]) is None

    def test_missing_and_deleted_files_skipped(self, tmp_path: Path) -> None:
        # 缺失件（staged delete 场景）不触发子进程，整批无 .py 即零开销放行
        assert ep.ruff_preclean(tmp_path, [str(tmp_path / "ghost.py")]) is None

    def test_relative_path_resolved_against_root(self, tmp_path: Path) -> None:
        _write(tmp_path, "ok.py", _OK_PY)
        assert ep.ruff_preclean(tmp_path, ["ok.py"]) is None

    def test_ruff_violation_rejected_with_file_line_rule(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "bad.py", _BAD_PY)
        rx = ep.ruff_preclean(tmp_path, [f])
        assert rx is not None
        assert "F821" in rx  # 哪规
        assert "bad.py" in rx  # 哪文件
        assert ":1:" in rx  # 哪行（concise 输出 file:line:col）
        assert "ruff check" in rx
        assert "--fix" in rx  # 处方给到一键可执行

    def test_format_violation_rejected(self, tmp_path: Path) -> None:
        f = _write(tmp_path, "fmt.py", _FMT_BAD_PY)
        rx = ep.ruff_preclean(tmp_path, [f])
        assert rx is not None
        assert "ruff format" in rx

    def test_env_off_rolls_back(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(ep.RUFF_PRECLEAN_ENV, "0")
        f = _write(tmp_path, "bad.py", _BAD_PY)
        assert ep.ruff_preclean_enabled() is False
        assert ep.ruff_preclean(tmp_path, [f]) is None  # 回退现行为=放行

    def test_large_batch_skipped_fail_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(ep, "_RUFF_PRECLEAN_MAX_FILES", 1)
        f1 = _write(tmp_path, "a.py", _OK_PY)
        f2 = _write(tmp_path, "b.py", "y = 2\n")
        assert ep.ruff_preclean(tmp_path, [f1, f2]) is None  # 超限 skip=放行并记原因

    def test_infra_failure_fail_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        f = _write(tmp_path, "ok.py", _OK_PY)

        def _boom(*a, **k):
            raise OSError("ruff unavailable")

        monkeypatch.setattr(subprocess, "run", _boom)
        assert ep.ruff_preclean(tmp_path, [f]) is None

    def test_timeout_fail_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        f = _write(tmp_path, "ok.py", _OK_PY)

        def _hang(*a, **k):
            raise subprocess.TimeoutExpired(cmd="ruff", timeout=60)

        monkeypatch.setattr(subprocess, "run", _hang)
        assert ep.ruff_preclean(tmp_path, [f]) is None


class TestGitCommitRuffGate:
    """git_commit._ruff_preclean_gate 挂点语义（exit 8 / --skip-preflight 逃生）。"""

    @pytest.fixture(autouse=True)
    def _env_default_on(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(ep.RUFF_PRECLEAN_ENV, raising=False)

    @staticmethod
    def _args(**kw):
        base = {"skip_preflight": False}
        base.update(kw)
        return SimpleNamespace(**base)

    def test_gate_blocks_with_exit_8(self, tmp_path: Path) -> None:
        from scripts.git_commit import _ruff_preclean_gate

        f = _write(tmp_path, "bad.py", _BAD_PY)
        assert _ruff_preclean_gate(self._args(), [f], str(tmp_path)) == 8

    def test_gate_passes_clean_file(self, tmp_path: Path) -> None:
        from scripts.git_commit import _ruff_preclean_gate

        f = _write(tmp_path, "ok.py", _OK_PY)
        assert _ruff_preclean_gate(self._args(), [f], str(tmp_path)) is None

    def test_gate_skip_preflight_escape(self, tmp_path: Path) -> None:
        from scripts.git_commit import _ruff_preclean_gate

        f = _write(tmp_path, "bad.py", _BAD_PY)
        assert _ruff_preclean_gate(self._args(skip_preflight=True), [f], str(tmp_path)) is None

    def test_gate_infra_failure_fail_open(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from scripts.git_commit import _ruff_preclean_gate

        def _boom(*a, **k):
            raise RuntimeError("enqueue_preflight import exploded")

        monkeypatch.setattr(ep, "ruff_preclean", _boom)
        f = _write(tmp_path, "ok.py", _OK_PY)
        assert _ruff_preclean_gate(self._args(), [f], str(tmp_path)) is None
