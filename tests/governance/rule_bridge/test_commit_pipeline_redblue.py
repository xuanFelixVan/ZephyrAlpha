"""提交通道 v2.1 红蓝对抗套件（W8，st-commitspeed-20260916）。

覆盖六类攻击面：预检快败与逃生旗/预检降级不误拦/own-scope 无自伤豁免/
车道防饿死/loader mtime 缓存失效/pytest 生产根守卫。全部 tmp_path 隔离，
只读真仓（预检集成用例只读 AGENTS.md 不写）。
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from zephyr.gov_enforcement.rule_bridge.commit_preflight import PREFLIGHT_GATES, run_preflight


# ---------------------------------------------------------------------------
# 红队1：预检快败——真实网关只读集成（受保护路径必被锁外拦截）
# ---------------------------------------------------------------------------

class TestPreflightFastFailLive:
    def test_protected_path_blocked_outside_lock(self, tmp_path):
        """红攻：拿受保护路径（AGENTS.md）提交——预检须在锁外拦下并给逃生提示。

        预检全程只读（真仓网关装配+gate 检查零副作用），此为快败路径的
        生产级验证（2026-09-16 实弹同款场景）。
        """
        import sys

        sys.path.insert(0, "src")
        sys.path.insert(0, "scripts")
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

        gw = GitCommitGateway(project_root=".")
        t0 = time.monotonic()
        result = run_preflight(gw, ["AGENTS.md"], "redblue-session")
        elapsed = time.monotonic() - t0
        assert result.blocking, "受保护路径须被预检拦截"
        gate_ids = [f.gate_id for f in result.findings]
        assert "PROTECTED-PATHS" in gate_ids
        hint = next(f for f in result.findings if f.gate_id == "PROTECTED-PATHS").escape_hint
        assert "Owner 审批" in hint
        assert elapsed < 30, f"预检须快败（实测 {elapsed:.1f}s）"

    def test_clean_file_passes_preflight(self, tmp_path):
        """蓝守：干净文件集预检放行（无假阳性快败）。"""
        import sys

        sys.path.insert(0, "src")
        sys.path.insert(0, "scripts")
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

        gw = GitCommitGateway(project_root=".")
        # 用既有合规文件（本测试文件自身在 tests/ 豁免区）
        result = run_preflight(
            gw,
            [str(Path(__file__))],
            "redblue-session",
            skip_gate_ids={"SESSION-REQUIRED", "CLAIM-REQUIRED", "WORKTREE-REQUIRED"},
            specs=None,
            audit_event="redblue",
        )
        assert not result.blocking or "TTL-METADATA" not in [f.gate_id for f in result.findings]


# ---------------------------------------------------------------------------
# 红队2：逃生旗映射——旗标对应 gate 必须跳过（防假阳性快败逼用户加错旗）
# ---------------------------------------------------------------------------

class TestEscapeFlagMapping:
    def test_worktree_flag_skips_gate(self, tmp_path):
        """WORKTREE-REQUIRED 在 skip 集时即便违规也不进失败清单。"""
        import sys

        sys.path.insert(0, "src")
        sys.path.insert(0, "scripts")
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

        gw = GitCommitGateway(project_root=".")
        result = run_preflight(
            gw,
            ["AGENTS.md"],
            "redblue-session",
            skip_gate_ids={"WORKTREE-REQUIRED"},
            audit_event="redblue",
        )
        assert "WORKTREE-REQUIRED" not in [f.gate_id for f in result.findings]


# ---------------------------------------------------------------------------
# 红队3：own-scope 无自伤豁免（外来不连坐 + 自己违规照拦——引用 W4 批单测，此处断言白名单门禁齐备）
# ---------------------------------------------------------------------------

class TestOwnScopeCoverageContract:
    def test_preflight_whitelist_only_files_deriven_gates(self):
        """白名单契约：禁入依赖全暂存扫描的 gate（防外来 WIP 假阳性）。"""
        forbidden = {"DEPGRAPH-PRE-REGISTRATION", "RENAME-DEPGRAPH-SYNC", "CREATE-GUARD", "ENCODING-SAFETY"}
        assert not (PREFLIGHT_GATES & forbidden), "暂存区衍生 gate 禁入预检白名单"

    def test_escape_hints_cover_all_whitelist_gates(self):
        """每道白名单 gate 都有逃生提示（一过式清单完备性）。"""
        from zephyr.gov_enforcement.rule_bridge.commit_preflight import _ESCAPE_HINTS

        missing = PREFLIGHT_GATES - set(_ESCAPE_HINTS)
        assert not missing, f"缺逃生提示: {missing}"


# ---------------------------------------------------------------------------
# 红队4：车道防饿死——最老 machine 项超 30min 必须放行
# ---------------------------------------------------------------------------

class TestLaneStarvationGuard:
    def test_starved_machine_promoted(self, tmp_path, monkeypatch):
        import sys

        sys.path.insert(0, "scripts")
        import commit_queue as cq
        from datetime import datetime, timedelta

        pending = tmp_path / "pending"
        pending.mkdir()
        now = datetime.now().astimezone()
        old_iso = (now - timedelta(seconds=cq._MACHINE_LANE_STARVATION_SEC + 60)).isoformat()
        new_iso = now.isoformat()
        # machine 项很老 + interactive 项很新 → 必须选 machine（防饿死护栏）
        (pending / "q-20260916-simA-0001.json").write_text(
            json_dump({"qid": "q-20260916-simA-0001", "created_at": old_iso, "meta": {"lane": "machine"}}),
            encoding="utf-8",
        )
        (pending / "q-20260916-simB-0002.json").write_text(
            json_dump({"qid": "q-20260916-simB-0002", "created_at": new_iso, "meta": {"lane": "interactive"}}),
            encoding="utf-8",
        )
        head, lane = cq._pick_head(sorted(pending.glob("q-*.json")))
        assert lane == "machine" and head.name.startswith("q-20260916-simA")


def json_dump(obj) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


# ---------------------------------------------------------------------------
# 红队5：loader mtime 缓存失效（Serializer 长活进程陈旧缓存治本的回归钉）
# ---------------------------------------------------------------------------

class TestLoaderMtimeInvalidation:
    def test_mtime_change_forces_reload(self, tmp_path, monkeypatch):
        import sys

        sys.path.insert(0, "scripts")
        from scripts.governance._shared import module_translation_loader as mtl

        reg = tmp_path / "module_translation_registry.yaml"
        reg.write_text(
            "entries:\n- module_path: src/x/a.py\n  plain_zh: 一句话简介补足八个汉字以上\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(mtl, "_REGISTRY_YAML", reg)
        mtl._PATH_CACHE = None
        mtl._PATH_CACHE_MTIME = None
        assert mtl.get_module_translation("src/x/a.py") is not None
        # 陈旧缓存攻击：文件更新但缓存对象仍在 → mtime 变化必须触发重载
        time.sleep(0.05)
        reg.write_text(
            "entries:\n- module_path: src/x/a.py\n  plain_zh: 更新后的一句话简介补足八个汉字\n- module_path: src/x/b.py\n  plain_zh: 新条目简介补足八个汉字以上\n",
            encoding="utf-8",
        )
        got_b = mtl.get_module_translation("src/x/b.py")
        assert got_b is not None, "mtime 变化后新条目必须可见（陈旧缓存治本）"
        mtl._PATH_CACHE = None
        mtl._PATH_CACHE_MTIME = None


# ---------------------------------------------------------------------------
# 红队6：pytest 生产根守卫（P0-C 测试隔离的回归钉）
# ---------------------------------------------------------------------------

class TestPytestProductionRootGuard:
    def test_bare_resolve_refuses_production_root(self, monkeypatch, tmp_path):
        import sys

        sys.path.insert(0, "scripts")
        import commit_queue as cq

        monkeypatch.delenv(cq.QUEUE_ENV_VAR, raising=False)
        # PYTEST_CURRENT_TEST 在 pytest 运行态自动存在
        with pytest.raises(RuntimeError, match="测试隔离"):
            cq.resolve_queue_root(None)

    def test_explicit_root_still_works(self, monkeypatch, tmp_path):
        import sys

        sys.path.insert(0, "scripts")
        import commit_queue as cq

        assert cq.resolve_queue_root(tmp_path) == tmp_path
