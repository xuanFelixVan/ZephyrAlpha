# [A_test] module_id: zephyr.gov_enforcement.rule_bridge.checker_supervisor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | tests/git/test_checker_supervisor.py | §checker-supervisor-tests
# [MODULE] tests.git.test_checker_supervisor
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] pytest; zephyr.gov_enforcement.rule_bridge.checker_supervisor
# [CONSUMERS] pytest 自动发现
# [STARTUP] imported -m pytest tests/git/test_checker_supervisor.py
# [MATURITY] testing
# [INVARIANTS] 结果≡直 spawn（rc/stdout/stderr 等价）；worker 异常→run 返回 None（回退信号）；超时=TimeoutExpired；disable env→None
# [MODIFY-GUARD] 2026-09-10 提交通道性能优化方案 §2.2-A2 验收
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_checker_supervisor.py — A2 checker 合并执行（持久 worker）验收。"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge.checker_supervisor import (
    CheckerSupervisor,
    _SUPERVISOR_DISABLE_ENV,
    get_supervisor,
)


def _write_checker(tmp_path: Path, name: str, body: str) -> Path:
    p = tmp_path / name
    p.write_text(body, encoding="utf-8")
    return p


class TestCheckerSupervisor:
    def test_text_roundtrip_and_exit_code(self, tmp_path: Path) -> None:
        """rc/stdout/stderr 与直 spawn 等价（text 模式）；SystemExit code 捕获。"""
        checker = _write_checker(
            tmp_path,
            "ok_checker.py",
            (
                "import sys\n"
                "print('OUT-line')\n"
                "sys.stderr.write('ERR-line\\n')\n"
                "sys.exit(3)\n"
            ),
        )
        sup = CheckerSupervisor()
        result = sup.run(checker, ["--flag", "v"], cwd=tmp_path, timeout=30)
        sup.close()
        assert result is not None and result.returncode == 3
        assert "OUT-line" in result.stdout and "ERR-line" in result.stderr
        assert result.args[0] == str(checker)

    def test_bytes_mode_roundtrip(self, tmp_path: Path) -> None:
        checker = _write_checker(tmp_path, "bytes_checker.py", "import sys\nsys.stdout.write('B\\n')\n")
        sup = CheckerSupervisor()
        result = sup.run(checker, [], cwd=tmp_path, timeout=30, text=False)
        sup.close()
        assert result is not None and result.returncode == 0
        assert result.stdout == b"B\n", "bytes 模式 stdout 应为 bytes（base64 往返无损）"

    def test_env_delta_and_cwd(self, tmp_path: Path) -> None:
        checker = _write_checker(
            tmp_path,
            "env_checker.py",
            "import os\nprint(os.environ.get('ZEPHYR_TEST_DELTA', 'missing'))\nprint(os.getcwd().split('\\\\')[-1].split('/')[-1])\n",
        )
        sub = tmp_path / "sub"
        sub.mkdir()
        sup = CheckerSupervisor()
        result = sup.run(checker, [], cwd=sub, timeout=30, env={"ZEPHYR_TEST_DELTA": "injected"})
        sup.close()
        assert result is not None
        assert "injected" in result.stdout and "sub" in result.stdout

    def test_timeout_raises_timeout_expired(self, tmp_path: Path) -> None:
        """per-checker 超时=父进程强制杀 worker，抛 TimeoutExpired（与直 spawn 同款）。"""
        checker = _write_checker(tmp_path, "slow_checker.py", "import time\ntime.sleep(30)\n")
        sup = CheckerSupervisor()
        try:
            with pytest.raises(subprocess.TimeoutExpired):
                sup.run(checker, [], cwd=tmp_path, timeout=2)
            # worker 被杀重建后，后续请求仍可服务（隔离恢复）
            ok = _write_checker(tmp_path, "after_checker.py", "print('alive')\n")
            result = sup.run(ok, [], cwd=tmp_path, timeout=30)
            assert result is not None and "alive" in result.stdout
        finally:
            sup.close()

    def test_worker_crash_returns_none(self, tmp_path: Path) -> None:
        """checker 硬崩（os._exit）→ worker 死亡 → run 返回 None（回退直 spawn 信号）。"""
        checker = _write_checker(tmp_path, "crash_checker.py", "import os\nos._exit(9)\n")
        sup = CheckerSupervisor()
        try:
            assert sup.run(checker, [], cwd=tmp_path, timeout=30) is None
        finally:
            sup.close()

    def test_disable_env_returns_none(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv(_SUPERVISOR_DISABLE_ENV, "0")
        checker = _write_checker(tmp_path, "any_checker.py", "print('x')\n")
        assert get_supervisor().run(checker, [], cwd=tmp_path, timeout=30) is None, "禁用 env → None（回退直 spawn）"
