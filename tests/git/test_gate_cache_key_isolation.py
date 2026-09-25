# [TTL] permanent
"""T7/B2 缓存键隔离判别测试（st-commitspeed-tbl-20260924）。

钉住四件不可回退的事：
- **键隔离（红绿差分）**：own 文件不变时，他人向共享 index 暂存/推进 HEAD
  不得作废我的缓存。红证＝旧键公式（gate_id×own_scope×write-tree 树指纹×
  head_sha×flags mtime）在「他人提交推进 HEAD」场景下同键位漂移必 miss——
  这就是 24h 仅 87 命中的结构性病根；绿证＝现键（内容哈希，禁含 HEAD/共享
  树状态）同场景命中。
- **内容敏感**：own 文件 staged 内容变化必须立即 miss（缓存投毒的逆命题）。
- **门源码判失**：被缓存门读取的门实现文件一字节篡改 ⇒ 下次必 miss
  （spec_sha 内容哈希的语义自证）。
- **注册表判失**：GATE_INPUT_MANIFEST 声明的注册表文件一字节篡改 ⇒ 下次必
  miss（manifest 内容哈希的语义自证）——未来注册表读取类门准入的机械前置。
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from zephyr.gov_enforcement.rule_bridge import gate_cache_preflight as gcp

_REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def git_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    def git(*a: str) -> str:
        r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, errors="replace")
        assert r.returncode == 0, r.stderr
        return r.stdout.strip()

    git("init", "-q", "--initial-branch=main")
    git("config", "core.autocrlf", "false")
    git("config", "user.email", "t@t")
    git("config", "user.name", "t")
    (repo / "own.py").write_text("X = 1\n", encoding="utf-8")
    (repo / "config").mkdir()
    (repo / "config" / "flags.yaml").write_text("flags: {}\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-qm", "init")
    return repo


def _gateway(repo: Path) -> SimpleNamespace:
    def run_git(argv: list[str], cwd: str | None = None):
        return subprocess.run(argv, cwd=str(repo), capture_output=True, text=True)

    return SimpleNamespace(run_git=run_git, project_root=str(repo))


def _stage(repo: Path, name: str, text: str) -> None:
    (repo / name).write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "add", name], check=True)


def _git(repo: Path, *a: str) -> str:
    r = subprocess.run(["git", "-C", str(repo), *a], capture_output=True, text=True, errors="replace")
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def _real_fingerprint(repo: Path) -> gcp.Fingerprint:
    """旧键公式所需的现场指纹（逐字段复刻旧 compute_fingerprint，供红证重建）。"""
    return gcp.Fingerprint(
        staged_tree_sha=_git(repo, "write-tree"),
        head_sha=_git(repo, "rev-parse", "HEAD"),
        flags_mtime=(repo / "config" / "flags.yaml").stat().st_mtime,
    )


def _old_key_path(cache: gcp.GateResultCache, gate_id: str, own_scope: str, fp: gcp.Fingerprint) -> Path:
    """旧键公式逐字重建（T7/B2 改键前的 _path：write-tree 树指纹×HEAD_sha）。

    红证用途：证明旧公式在「他人推进 HEAD」场景下键位漂移=全失效。
    原式：sha256(f"{gate_id}\\x1e{own_scope}\\x1e{staged_tree_sha}\\x1e{head_sha}\\x1e{flags_mtime}")
    """
    raw = f"{gate_id}\x1e{own_scope}\x1e{fp.staged_tree_sha}\x1e{fp.head_sha}\x1e{fp.flags_mtime}"
    assert cache._dir is not None
    return cache._dir / f"{hashlib.sha256(raw.encode()).hexdigest()}.json"


def _old_lookup(cache: gcp.GateResultCache, gate_id: str, own_scope: str, fp: gcp.Fingerprint) -> str | None:
    p = _old_key_path(cache, gate_id, own_scope, fp)
    try:
        return str(json.loads(p.read_text(encoding="utf-8"))["detail"])
    except (OSError, ValueError, KeyError, TypeError):
        return None


def test_old_key_misses_on_head_advance_new_key_hits(git_repo: Path) -> None:
    """红证先行：他人提交推进 HEAD ⇒ 旧键必 miss（87/24h 病根）；改键后同场景命中。"""
    gw = _gateway(git_repo)
    fp_before = _real_fingerprint(git_repo)

    # 旧公式下写入一条 passed=True 缓存（复刻旧 _path 的落键位）
    cache_old = gcp.GateResultCache(gw, ["own.py"])
    old_path = _old_key_path(cache_old, "ENCODING-SAFETY", "scope-x", fp_before)
    old_path.parent.mkdir(parents=True, exist_ok=True)
    old_path.write_text(
        json.dumps({"gate_id": "ENCODING-SAFETY", "detail": "old-v1", "ts": time.time()}), encoding="utf-8"
    )
    assert _old_lookup(cache_old, "ENCODING-SAFETY", "scope-x", fp_before) == "old-v1", (
        "同指纹下旧键应命中（红证前置自检）"
    )

    # 新键同场景先存一条（own 内容不变）
    cache_new = gcp.GateResultCache(gw, ["own.py"])
    cache_new.store("ENCODING-SAFETY", "scope-x", "new-v1")

    # 他人提交推进 HEAD（与我无关的文件；write-tree/HEAD 双双前移）
    _stage(git_repo, "foreign_other.py", "Y = 2\n")
    _git(git_repo, "commit", "-qm", "foreign advances HEAD")
    fp_after = _real_fingerprint(git_repo)
    assert fp_after.head_sha != fp_before.head_sha, "场景前置：HEAD 已被他人推进"

    # 红证：旧键公式同场景 miss（head_sha 进键 ⇒ 键位漂移=缓存全失效）
    assert _old_lookup(cache_old, "ENCODING-SAFETY", "scope-x", fp_after) is None, (
        "旧键公式在他人推进 HEAD 后必须 miss（这就是 87/24h 的病根）"
    )
    # 绿证：新键（内容哈希，禁含 HEAD/共享树状态）同场景命中
    cache_new2 = gcp.GateResultCache(gw, ["own.py"])
    assert cache_new2.lookup("ENCODING-SAFETY", "scope-x") == "new-v1", "改键后他人推进 HEAD 不得作废 own 缓存"


def test_cache_survives_foreign_staging(git_repo: Path) -> None:
    """他人暂存活动（index 全树 sha 变化）不得作废 own 文件的缓存。"""
    gw = _gateway(git_repo)
    cache = gcp.GateResultCache(gw, ["own.py"])
    cache.store("ENCODING-SAFETY", "scope-x", "detail-v1")
    assert cache.lookup("ENCODING-SAFETY", "scope-x") == "detail-v1"

    # 他人暂存一个与我无关的文件（write-tree 全树 sha 必变）
    _stage(git_repo, "foreign_other.py", "Y = 2\n")

    cache2 = gcp.GateResultCache(gw, ["own.py"])
    assert cache2.lookup("ENCODING-SAFETY", "scope-x") == "detail-v1", "own 内容未变 ⇒ 缓存必须命中（键隔离）"


def test_cache_misses_on_own_content_change(git_repo: Path) -> None:
    """own staged 内容变化必须立即 miss（投毒逆命题）。"""
    gw = _gateway(git_repo)
    cache = gcp.GateResultCache(gw, ["own.py"])
    cache.store("NO-BARE-SQL", "scope-y", "detail-a")
    assert cache.lookup("NO-BARE-SQL", "scope-y") == "detail-a"

    _stage(git_repo, "own.py", "X = 999\n")

    cache2 = gcp.GateResultCache(gw, ["own.py"])
    assert cache2.lookup("NO-BARE-SQL", "scope-y") is None, "own 内容变化 ⇒ 必须 miss"


def test_gate_source_byte_tamper_forces_miss(git_repo: Path) -> None:
    """门实现面一字节篡改 ⇒ 下次必 miss（spec_sha 内容哈希语义自证）。"""
    spec_dir = git_repo / "src" / "zephyr" / "gov_enforcement" / "commit_gates"
    spec_dir.mkdir(parents=True)
    gate_file = spec_dir / "some_gate_impl.py"
    gate_file.write_text("def check():\n    return True\n", encoding="utf-8")

    gw = _gateway(git_repo)
    cache = gcp.GateResultCache(gw, ["own.py"])
    cache.store("RELATIVE-PATH-LITERAL", "scope-z", "clean-v1")
    assert cache.lookup("RELATIVE-PATH-LITERAL", "scope-z") == "clean-v1"

    # 篡改门源码一个字节（内容哈希必变）
    gate_file.write_text("def check():\n    return False\n", encoding="utf-8")

    cache2 = gcp.GateResultCache(gw, ["own.py"])
    assert cache2.lookup("RELATIVE-PATH-LITERAL", "scope-z") is None, "门源码一字节篡改 ⇒ spec_sha 变 ⇒ 必须 miss"


def test_manifest_registry_byte_tamper_forces_miss(git_repo: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """manifest 声明的注册表文件一字节篡改 ⇒ 下次必 miss（注册表判失分量）。"""
    reg_dir = git_repo / "docs" / "01_policies_and_standards" / "_registry" / "catalogs"
    reg_dir.mkdir(parents=True)
    reg_file = reg_dir / "some_gate_registry.yaml"
    reg_file.write_text("entries: []\n", encoding="utf-8")
    monkeypatch.setitem(
        gcp.GATE_INPUT_MANIFEST,
        "X-REGISTRY-READING-GATE",
        ("docs/01_policies_and_standards/_registry/catalogs/some_gate_registry.yaml",),
    )

    gw = _gateway(git_repo)
    cache = gcp.GateResultCache(gw, ["own.py"])
    cache.store("X-REGISTRY-READING-GATE", "scope-w", "clean-v1")
    assert cache.lookup("X-REGISTRY-READING-GATE", "scope-w") == "clean-v1"

    # 篡改被缓存门读取的注册表一个字节
    reg_file.write_text("entries: [x]\n", encoding="utf-8")

    cache2 = gcp.GateResultCache(gw, ["own.py"])
    assert cache2.lookup("X-REGISTRY-READING-GATE", "scope-w") is None, (
        "注册表字节篡改 ⇒ manifest 输入哈希变 ⇒ 必须 miss"
    )


def test_whitelist_members_are_registered() -> None:
    """白名单台账钉：每台必须在 in_process_gate_registry 名册（防死条目复发）。

    T7/B2 实测退役先例：NO-LONG-PARAM-LIST/NO-GOD-CLASS/NO-HIGH-COMPLEXITY
    24h 零触发零消费且不在名册 ⇒ 退役。
    """
    registry_text = (
        _REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "in_process_gate_registry.yaml"
    ).read_text(encoding="utf-8")
    registered = {
        line.split(":", 1)[1].strip() for line in registry_text.splitlines() if line.lstrip().startswith("- gate_id:")
    }
    missing = sorted(gcp.CONTENT_SCAN_CACHE_WHITELIST - registered)
    assert not missing, f"白名单含未注册死条目（应退役）: {missing}"
