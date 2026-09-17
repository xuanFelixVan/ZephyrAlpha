# [A_test] test_id=G1-R04-20260918 | module=scripts/git_commit.py+scripts/lock_files.py+git_commit_gateway.py | gate=pytest
# [BLUEPRINT] MOD-INF-005 | scripts/git_commit.py | §R-04 claim 生命周期 + 派生写入归属
# [TESTS] self
# [TTL] task_bound
"""R-04 claim 生命周期治本验收钉（lane G1，2026-09-18；真源 S18 根因表 R-04 行）。

覆盖验收矩阵：
1. 提交失败（gate 阻断/异常）→ claim 保留 + .ailocks TTL 收窄兜底（默认 300s，参数化）；
   提交成功（OK/NOTHING_TO_COMMIT）→ 释放。决策表全覆盖。
2. 收窄后的 claim TTL 过期 → 走既有 stale 回收通道可被他人认领（锁尸兜底）。
3. TTL 参数化优先级：CLI --failed-claim-ttl > env ZEPHYR_FAILED_CLAIM_TTL_S > 300。
4. 派生写入归属台账：reconciler/integrity 派生产物钉回触发会话名下，
   最新记录胜出，台账缺失返回空（语义不放大）。

隔离纪律：锁库/台账全部落 tmp_path，禁碰真仓。
模块路径默认指向本体；落地前验证用 ZEPHYR_G1_SURGERY_LOCK_FILES /
ZEPHYR_G1_SURGERY_GIT_COMMIT / ZEPHYR_G1_SURGERY_GATEWAY 指向镜像。
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
_SRC = _REPO / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
# 镜像 bootstrap 的 _PROJECT_ROOT 指向 surgery 目录（找不到真仓 d3_metadata）——
# 预置真仓 scripts/governance/d3_metadata 到 sys.path，使镜像模块级 import 可解析
_D3_METADATA = _REPO / "scripts" / "governance" / "d3_metadata"
if str(_D3_METADATA) not in sys.path:
    sys.path.insert(0, str(_D3_METADATA))

_LOCK_FILES_PATH = Path(
    os.environ.get("ZEPHYR_G1_SURGERY_LOCK_FILES", str(_REPO / "scripts" / "lock_files.py"))
)
_GIT_COMMIT_PATH = Path(
    os.environ.get("ZEPHYR_G1_SURGERY_GIT_COMMIT", str(_REPO / "scripts" / "git_commit.py"))
)
_GATEWAY_PATH = Path(
    os.environ.get(
        "ZEPHYR_G1_SURGERY_GATEWAY",
        str(_REPO / "src" / "zephyr" / "gov_enforcement" / "rule_bridge" / "git_commit_gateway.py"),
    )
)


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclass 处理等按 __module__ 反查 sys.modules
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture()
def lf(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """被测 lock_files（镜像/本体由 env 决定），锁库隔离到 tmp。"""
    mod = _load(_LOCK_FILES_PATH, "lock_files_g1_r04")
    monkeypatch.setattr(mod, "LOCK_ROOT", tmp_path / ".ailocks")
    monkeypatch.setattr(mod, "REGISTRY_PATH", tmp_path / ".ailocks" / "registry.json")
    monkeypatch.setattr(mod, "_is_git_tracked", lambda _p: True)
    return mod


@pytest.fixture()
def gc(lf, monkeypatch: pytest.MonkeyPatch):
    """被测 git_commit 模块；其内部 `import lock_files` 绑定到被测镜像。"""
    monkeypatch.setitem(sys.modules, "lock_files", lf)
    return _load(_GIT_COMMIT_PATH, "git_commit_g1_r04")


def _claim(lf, rel: str, owner: str) -> None:
    rc = lf.cmd_acquire(rel, owner, lf.AcquireOptions(skip_naming_check=True))
    assert rc == 0


def _owner(lf, rel: str) -> dict:
    return json.loads(lf._owner_file(lf._lock_dir(rel)).read_text(encoding="utf-8"))


def _registry(lf) -> dict:
    return json.loads(lf.REGISTRY_PATH.read_text(encoding="utf-8"))


class _FakeGateway:
    """claim/commit/release 全可编程的假网关（R-04 决策表驱动）。"""

    def __init__(self, commit_result=None, commit_exc: Exception | None = None) -> None:
        self.commit_result = commit_result
        self.commit_exc = commit_exc
        self.released: list[tuple[str, list[str]]] = []

    def commit(self, **_kwargs):
        if self.commit_exc is not None:
            raise self.commit_exc
        return self.commit_result

    def release_files(self, session_id: str, files: list[str]) -> None:
        self.released.append((session_id, list(files)))


# ── 1. 决策表：成功释放 / 失败保留 / 异常保留并上抛 ──
def test_success_releases_claims(gc) -> None:
    gw = _FakeGateway(commit_result=SimpleNamespace(status=gc.CommitStatus.OK))
    gc._commit_with_claim_lifecycle(
        gw, "s1", ["a.py"], {"anything": 1}, ttl_s=300.0, project_root="."
    )
    assert gw.released == [("s1", ["a.py"])]


def test_nothing_to_commit_releases_claims(gc) -> None:
    gw = _FakeGateway(commit_result=SimpleNamespace(status=gc.CommitStatus.NOTHING_TO_COMMIT))
    gc._commit_with_claim_lifecycle(
        gw, "s1", ["a.py"], {}, ttl_s=300.0, project_root="."
    )
    assert gw.released == [("s1", ["a.py"])]


def test_blocked_commit_retains_claims(gc, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict] = []
    monkeypatch.setattr(
        gc, "_retain_claims_after_failure", lambda *a, **k: calls.append({"a": a, "k": k})
    )
    gw = _FakeGateway(commit_result=SimpleNamespace(status=gc.CommitStatus.CLAIM_REQUIRED_VIOLATION))
    gc._commit_with_claim_lifecycle(
        gw, "s1", ["a.py"], {}, ttl_s=300.0, project_root="."
    )
    assert gw.released == []  # 失败不释放（R-04 核心）
    assert len(calls) == 1
    assert calls[0]["a"][0] == "s1"
    assert calls[0]["k"]["ttl_s"] == 300.0


def test_commit_exception_retains_and_reraises(gc, monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[dict] = []
    monkeypatch.setattr(
        gc, "_retain_claims_after_failure", lambda *a, **k: calls.append({"k": k})
    )
    gw = _FakeGateway(commit_exc=RuntimeError("boom"))
    with pytest.raises(RuntimeError):
        gc._commit_with_claim_lifecycle(gw, "s1", ["a.py"], {}, ttl_s=300.0, project_root=".")
    assert gw.released == []
    assert calls and calls[0]["k"]["reason"] == "commit-exception"


# ── 2. 保留 + TTL 收窄端到端：失败后 claim 保留可重试，过期后被他人认领 ──
def test_retained_claim_ttl_shortened_and_reclaimable(gc, lf, tmp_path: Path) -> None:
    _claim(lf, "docs/a.md", "s1")
    before = time.time()

    gc._retain_claims_after_failure(
        "s1", ["docs/a.md"], reason="CLAIM_REQUIRED_VIOLATION", ttl_s=0.3, project_root=str(tmp_path)
    )

    # 保留未释放 + owner.json/registry 过期点收窄到 ~0.3s + 审计标记
    owner = _owner(lf, "docs/a.md")
    assert owner["owner_id"] == "s1"
    assert owner["expires_at"] <= before + 0.3 + 0.5
    assert owner["retention"] == "commit-failed-retained"
    reg_entry = _registry(lf)["locks"]["docs/a.md"]
    assert abs(reg_entry["expires_at"] - owner["expires_at"]) < 1.0
    # 审计落盘
    audit = tmp_path / ".runtime" / "claim_snapshots" / "claim_retention.jsonl"
    assert audit.is_file()
    row = json.loads(audit.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert row["session_id"] == "s1" and row["reason"] == "CLAIM_REQUIRED_VIOLATION"

    # TTL 过期 → 既有 stale 回收通道接管，他人可认领（锁尸兜底）
    time.sleep(0.5)
    rc = lf.cmd_acquire("docs/a.md", "s2", lf.AcquireOptions(skip_naming_check=True))
    assert rc == 0
    assert _owner(lf, "docs/a.md")["owner_id"] == "s2"


def test_shorten_claim_ttl_only_touches_owner(lf) -> None:
    _claim(lf, "docs/a.md", "s1")
    _claim(lf, "docs/b.md", "s2")
    s2_expires_before = _owner(lf, "docs/b.md")["expires_at"]

    rewritten = lf.shorten_claim_ttl("s1", ["docs/a.md", "docs/b.md"], 300.0)

    assert rewritten == ["docs/a.md"]  # 他人 claim 不动
    assert abs(_owner(lf, "docs/b.md")["expires_at"] - s2_expires_before) < 1.0


# ── 3. TTL 参数化优先级 ──
def test_failed_claim_ttl_default(gc, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ZEPHYR_FAILED_CLAIM_TTL_S", raising=False)
    assert gc._failed_claim_ttl(SimpleNamespace(failed_claim_ttl=None)) == 300.0


def test_failed_claim_ttl_env_override(gc, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZEPHYR_FAILED_CLAIM_TTL_S", "120")
    assert gc._failed_claim_ttl(SimpleNamespace(failed_claim_ttl=None)) == 120.0


def test_failed_claim_ttl_cli_beats_env(gc, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ZEPHYR_FAILED_CLAIM_TTL_S", "120")
    assert gc._failed_claim_ttl(SimpleNamespace(failed_claim_ttl=45.0)) == 45.0


# ── 4. 派生写入归属台账（gateway 镜像/本体模块级真源）──
@pytest.fixture()
def gw_mod():
    return _load(_GATEWAY_PATH, "gw_g1_r04")


def test_derived_write_attribution_roundtrip(gw_mod, tmp_path: Path) -> None:
    f = tmp_path / "scripts" / "governance" / "meta" / "rules_integrity_db.json"
    f.parent.mkdir(parents=True)
    f.write_text("{}", encoding="utf-8")

    gw_mod.record_derived_write(tmp_path, "sessA", [str(f)], source="rules_integrity_re_register", committed=False)
    owners = gw_mod.lookup_derived_write_owners(tmp_path, [str(f)])
    rel = "scripts/governance/meta/rules_integrity_db.json"
    assert owners[rel]["session_id"] == "sessA"
    assert owners[rel]["source"] == "rules_integrity_re_register"
    assert owners[rel]["committed"] is False

    # 最新记录胜出（auto-commit 成功后 committed=True 覆盖）
    gw_mod.record_derived_write(tmp_path, "sessA", [str(f)], source="auto_commit", committed=True)
    owners = gw_mod.lookup_derived_write_owners(tmp_path, [str(f)])
    assert owners[rel]["committed"] is True
    assert owners[rel]["source"] == "auto_commit"


def test_derived_write_lookup_missing_ledger_returns_empty(gw_mod, tmp_path: Path) -> None:
    assert gw_mod.lookup_derived_write_owners(tmp_path, ["x.py"]) == {}


def test_derived_write_attribution_unrelated_file_not_mapped(gw_mod, tmp_path: Path) -> None:
    f = tmp_path / "a.txt"
    f.write_text("1", encoding="utf-8")
    gw_mod.record_derived_write(tmp_path, "sessA", [str(f)], source="auto_commit", committed=True)
    owners = gw_mod.lookup_derived_write_owners(tmp_path, ["b.txt"])
    assert owners == {}
