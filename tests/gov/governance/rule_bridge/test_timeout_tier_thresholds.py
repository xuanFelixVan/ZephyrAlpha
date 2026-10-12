# [MODULE] tests.gov.governance.test_timeout_tier_thresholds
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] scripts/governance/_shared/thresholds.py; git_commit_gateway; scripts/session_worktree
# [CONSUMERS] pytest
# [STARTUP] pytest
# [MATURITY] production
# [INVARIANTS] 本文件只验"读得到＋读不到退原值＋事件字段齐"三件事，禁在此断言任何超时数值语义
# [MODIFY-GUARD] 超时档键名变更须与 thresholds.yaml git_operations 段同批
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即口径断裂
# [TESTS] tests/gov/governance/test_timeout_tier_thresholds.py
# [TTL] permanent
"""超时乙＋C13 的口径钉（统筹裁定 2026-10-13，维护三班）。

钉三件事，防止三类真实回归形态：
1. **装饰性键**：thresholds 里加了键而代码从不读（在册教训
   `config-consumed-by-only-one-code-path`）——本组直接断言 gateway 常量来自册。
2. **读失败变成 0/负数**：那会让每个 git 调用瞬间超时（比不调更糟），
   故 `_resolve_git_timeout` 必须对缺键/坏值/设施异常一律退原常量。
3. **擦除事件缺存证坐标**：lane-archive 历史上只写 worktree_abort.jsonl，
   统一遥测流 worktree_ops_log.jsonl 里六条被归档车道零命中——
   本组断言 begin/done 两拍都落流，且 done 带 patch 路径。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


def _load_gateway_timeouts():
    import zephyr.gov_enforcement.rule_bridge.git_commit_gateway as g

    return g


class TestYiTimeoutTierIsActuallyConsumed:
    def test_keys_exist_with_unchanged_values(self) -> None:
        """乙＝搬值不改值：15/60/30 必须与裁定前的代码常量逐字相同。"""
        import yaml

        data = yaml.safe_load((REPO / "scripts/governance/_shared/thresholds.yaml").read_text(encoding="utf-8"))
        gop = data["git_operations"]
        assert gop["gateway_git_read_timeout_seconds"] == 15
        assert gop["gateway_git_write_timeout_seconds"] == 60
        assert gop["gateway_git_default_timeout_seconds"] == 30

    def test_gateway_reads_from_registry_not_hardcode(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """键不是装饰：把桩打进 thresholds.get，gateway 必须跟着变（再撤桩验真值）。"""
        from scripts.governance._shared import thresholds

        g = _load_gateway_timeouts()
        mapping = {
            "git_operations.gateway_git_read_timeout_seconds": 1501,
            "git_operations.gateway_git_write_timeout_seconds": 1502,
            "git_operations.gateway_git_default_timeout_seconds": 1503,
        }
        monkeypatch.setattr(thresholds, "get", lambda key, default=None: mapping.get(key, default))
        for key, want in mapping.items():
            assert g._resolve_git_timeout(key, 7) == want, f"{key} 未经 thresholds.get 真读"
        monkeypatch.undo()
        # 撤桩回绿：在册真值经同一条路取到
        assert g._resolve_git_timeout("git_operations.gateway_git_write_timeout_seconds", 7) == 60

    def test_bad_or_missing_value_falls_back_not_zero(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """读失败/缺键/坏值/0 或负数一律退原常量——绝不把 git 调参面变成瞬间超时。"""
        from scripts.governance._shared import thresholds

        g = _load_gateway_timeouts()
        for bad in (None, 0, -5, "abc", ""):
            monkeypatch.setattr(thresholds, "get", lambda k, d=None, _v=bad: _v)
            assert g._resolve_git_timeout("git_operations.gateway_git_write_timeout_seconds", 60) == 60

        def _boom(k, d=None):
            raise FileNotFoundError("thresholds.yaml missing")

        monkeypatch.setattr(thresholds, "get", _boom)
        assert g._resolve_git_timeout("git_operations.gateway_git_read_timeout_seconds", 15) == 15


class TestC13ArchiveEraseTelemetry:
    def test_begin_and_done_land_in_ops_log_with_patch_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        import scripts.session_worktree as swt
        import zephyr.shared.io.paths as paths

        # 遥测助手在函数内 import anchor_main_root 并写 <锚定根>/.runtime/，
        # 测试里把锚钉到 tmp_path，绝不擦生产日志现场（正对照由断言本身承担：
        # 若不落盘，rows 为空即红）
        monkeypatch.setattr(paths, "anchor_main_root", lambda p: tmp_path)
        (tmp_path / ".runtime").mkdir(parents=True, exist_ok=True)
        log = tmp_path / ".runtime" / "worktree_ops_log.jsonl"
        monkeypatch.setattr(swt, "REPO_ROOT", tmp_path)
        wt = tmp_path / ".aidrafts" / "st-c13-fakelane"
        swt._log_archive_delete_event(wt, "begin")
        swt._log_archive_delete_event(wt, "done", extra={"patch_path": "p.patch", "verdict": "ARCHIVED", "ahead": 0})
        rows = [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]
        assert [r["phase"] for r in rows] == ["begin", "done"]
        assert all(r["op"] == "worktree_delete" for r in rows)
        assert all(r["source"] == "lane-archive" for r in rows)
        assert all(r["session_id"] == "st-c13-fakelane" for r in rows), "目录名即 sid，删事件必须归到人"
        assert rows[0].get("stack"), "begin 拍要带调用现场（谁发起删除）"
        assert rows[1]["patch_path"] == "p.patch", "done 拍必须带存证坐标（东西在哪）"

    def test_telemetry_failure_never_breaks_archive(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """降级面：遥测写不进一律静默，不得改变归档结果（在册 fail-soft 契约）。"""
        import scripts.session_worktree as swt
        import zephyr.gov_enforcement.rule_bridge.session_worktree as rb

        def _boom(*a, **k):
            raise OSError("disk gone")

        monkeypatch.setattr(rb, "_log_worktree_delete", _boom)
        swt._log_archive_delete_event(Path("D:/nowhere/.aidrafts/st-x"), "begin")  # 不抛即绿
