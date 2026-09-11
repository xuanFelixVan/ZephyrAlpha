# [A_test] module_id: zephyr.gov_enforcement.rule_bridge.gate_cache_preflight | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | tests/git/test_gate_cache_preflight.py | §gate-cache-preflight-tests
# [MODULE] tests.git.test_gate_cache_preflight
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] pytest；zephyr.gov_enforcement.rule_bridge.{gate_cache_preflight,commit_gate_registry,git_commit_gateway}
# [CONSUMERS] pytest 自动发现
# [STARTUP] imported -m pytest tests/git/test_gate_cache_preflight.py
# [MATURITY] testing
# [INVARIANTS] 指纹四元组任一变化→不匹配；缓存只存 passed=True；key 含 own_scope/tree/head/flags mtime；白名单默认保守；flag OFF=行为不变
# [MODIFY-GUARD] 2026-09-10 提交通道性能优化方案 §2.2-A3/§2.3/§2.6 验收
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] 本文件
# [TTL] permanent
"""test_gate_cache_preflight.py — P2⑦ 预跑指纹采信 + P2⑧ 结果持久缓存验收。"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

import zephyr.gov_enforcement.rule_bridge.gate_cache_preflight as gcp
from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway


def _init_git_repo(repo_dir: Path) -> None:
    """最小 git 仓（与 test_git_commit_gateway 同款——本文件独立不跨文件 import）。"""
    repo_dir.mkdir(parents=True, exist_ok=True)
    def git(*a: str) -> None:
        subprocess.run(["git", "-C", str(repo_dir), *a], check=True, capture_output=True)
    git("init")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    git("checkout", "-b", "dev")
    (repo_dir / "seed.txt").write_text("seed\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-m", "init")


def _gateway(tmp_path: Path) -> GitCommitGateway:
    _init_git_repo(tmp_path)
    return GitCommitGateway(project_root=tmp_path)


class TestFingerprint:
    def test_compute_and_match(self, tmp_path: Path) -> None:
        gw = _gateway(tmp_path)
        fp1 = gcp.compute_fingerprint(gw)
        fp2 = gcp.compute_fingerprint(gw)
        assert fp1 is not None and fp2 is not None and fp1.matches(fp2), "稳态两次指纹应一致"

    def test_staged_change_breaks_match(self, tmp_path: Path) -> None:
        gw = _gateway(tmp_path)
        fp1 = gcp.compute_fingerprint(gw)
        (tmp_path / "new.txt").write_text("x\n", encoding="utf-8")
        gw.run_git(["git", "add", "-A"])
        fp2 = gcp.compute_fingerprint(gw)
        assert fp1 is not None and fp2 is not None and not fp1.matches(fp2), "staged 变化须全失效"


class TestGateResultCache:
    def test_store_lookup_roundtrip(self, tmp_path: Path) -> None:
        gw = _gateway(tmp_path)
        cache = gcp.GateResultCache(gw, ["a.py"])
        assert cache.usable
        assert cache.lookup("ENCODING-SAFETY", "own1") is None
        cache.store("ENCODING-SAFETY", "own1", "clean")
        assert cache.lookup("ENCODING-SAFETY", "own1") == "clean"

    def test_own_scope_change_misses(self, tmp_path: Path) -> None:
        gw = _gateway(tmp_path)
        cache = gcp.GateResultCache(gw, ["a.py"])
        cache.store("ENCODING-SAFETY", "own1", "clean")
        assert cache.lookup("ENCODING-SAFETY", "own2") is None, "own_scope 变化不得命中"

    def test_expired_entry_misses(self, tmp_path: Path) -> None:
        gw = _gateway(tmp_path)
        cache = gcp.GateResultCache(gw, ["a.py"])
        cache.store("ENCODING-SAFETY", "own1", "clean")
        p = list((tmp_path / ".runtime/gate_cache").glob("*.json"))[0]
        data = json.loads(p.read_text(encoding="utf-8"))
        data["ts"] = time.time() - 601  # TTL 10min + 1s
        p.write_text(json.dumps(data), encoding="utf-8")
        assert cache.lookup("ENCODING-SAFETY", "own1") is None, "TTL 过期不得命中"

    def test_whitelist_conservative(self) -> None:
        """白名单红线：信号型/引擎依赖/注册表读取类不得入池。"""
        assert "DECISION-MAP" not in gcp.CONTENT_SCAN_CACHE_WHITELIST
        assert "CAPABILITY-OVERLAP" not in gcp.CONTENT_SCAN_CACHE_WHITELIST  # CloneGuard 引擎依赖（degraded 语义）
        assert "ENCODING-SAFETY" in gcp.CONTENT_SCAN_CACHE_WHITELIST


class TestCheckAllCacheIntegration:
    def _registry(self) -> CommitGateRegistry:
        reg = CommitGateRegistry()
        calls = {"n": 0}

        def check(gateway, files, **kw):  # noqa: ANN001, ANN003
            calls["n"] += 1
            return True, f"ran-{calls['n']}"

        from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

        reg.register(GateSpec(gate_id="ENCODING-SAFETY", check=check, priority=42))
        reg._calls = calls  # type: ignore[attr-defined] — 测试计数器
        return reg

    def test_flag_off_executes_every_time(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gcp, "result_cache_enabled", lambda: False)
        gw = _gateway(tmp_path)
        reg = self._registry()
        reg.check_all(gw, ["a.py"])
        reg.check_all(gw, ["a.py"])
        assert reg._calls["n"] == 2, "flag OFF（出厂默认）→ 每次现算，行为不变"

    def test_flag_on_second_run_hits_cache(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gcp, "result_cache_enabled", lambda: True)
        gw = _gateway(tmp_path)
        reg = self._registry()
        r1 = reg.check_all(gw, ["a.py"])
        assert reg._calls["n"] == 1
        r2 = reg.check_all(gw, ["a.py"])
        assert reg._calls["n"] == 1, "第二次应命中缓存不再现算"
        assert r1[0].passed and r2[0].passed
        assert r2[0].detail.startswith("cache-hit:"), "命中结果带 cache-hit 前缀供审计"

    def test_failure_not_cached(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(gcp, "result_cache_enabled", lambda: True)
        gw = _gateway(tmp_path)
        reg = CommitGateRegistry()
        calls = {"n": 0}

        def fail_check(gateway, files, **kw):  # noqa: ANN001, ANN003
            calls["n"] += 1
            return False, "violation"

        from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

        reg.register(GateSpec(gate_id="ENCODING-SAFETY", check=fail_check, priority=42))
        reg.check_all(gw, ["a.py"])
        reg.check_all(gw, ["a.py"])
        assert calls["n"] == 2, "失败结果绝不缓存（每次真实执行）"


class TestCheckAllPreflightResults:
    def test_preflight_hit_skips_rerun(self, tmp_path: Path) -> None:
        gw = _gateway(tmp_path)
        reg = CommitGateRegistry()
        calls = {"n": 0}

        def check(gateway, files, **kw):  # noqa: ANN001, ANN003
            calls["n"] += 1
            return True, "should-not-run"

        from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

        reg.register(GateSpec(gate_id="ENCODING-SAFETY", check=check, priority=42))
        results = reg.check_all(
            gw,
            ["a.py"],
            preflight_results={"ENCODING-SAFETY": (True, "pre-ok")},
        )
        assert calls["n"] == 0, "指纹已由调用方校验匹配时，白名单 gate 复用预跑结果"
        assert results[0].passed and results[0].detail.startswith("preflight:")

    def test_no_preflight_runs_normally(self, tmp_path: Path) -> None:
        gw = _gateway(tmp_path)
        reg = CommitGateRegistry()
        calls = {"n": 0}

        def check(gateway, files, **kw):  # noqa: ANN001, ANN003
            calls["n"] += 1
            return True, "ran"

        from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

        reg.register(GateSpec(gate_id="ENCODING-SAFETY", check=check, priority=42))
        reg.check_all(gw, ["a.py"], preflight_results=None)
        assert calls["n"] == 1, "preflight_results=None → 现行全量路径"


class TestEnqueueGuard:
    def test_enqueue_flag_off_rejected(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """P2⑨：flag commit_queue_interactive 出厂 OFF → --enqueue 拒绝 exit 2。"""
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "flags.yaml").write_text("x: 1\n", encoding="utf-8")
        monkeypatch.setattr(gcp, "flag_enabled", lambda name: False)
        monkeypatch.setattr(sys, "argv", [
            "git_commit.py",
            "--session", "test-enqueue-s",
            "--files", "config/flags.yaml",
            "--message", "test enqueue",
            "--enqueue",
            "--project-root", str(tmp_path),
        ])
        import scripts.git_commit as gcm

        rc = gcm.main()
        assert rc == 2, "flag OFF → --enqueue fail-closed 拒绝 exit 2"

    def test_enqueue_conflict_params_rejected(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """--enqueue 与 --reconciler-verify 互斥（exit 2，先于 flag 判定）。"""
        (tmp_path / "config").mkdir()
        (tmp_path / "config" / "flags.yaml").write_text("x: 1\n", encoding="utf-8")
        monkeypatch.setattr(gcp, "flag_enabled", lambda name: True)
        monkeypatch.setattr(sys, "argv", [
            "git_commit.py",
            "--session", "test-enqueue-s",
            "--files", "config/flags.yaml",
            "--message", "m",
            "--enqueue",
            "--reconciler-verify",
            "--project-root", str(tmp_path),
        ])
        import scripts.git_commit as gcm

        rc = gcm.main()
        assert rc == 2
