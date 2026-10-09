"""死信归因引擎回归（2026-10-03 deadletter-cure 战役 · Layer1+Layer2）。

钉死三件事：
  1. 八类史实归因判定正确性（尤其 pristine_lost / never_landed 两类的因果关系）；
  2. **不变量 SV**：含任一不可销账分类的袋永不判 settleable（Owner 裁定 A）；
  3. sweep 默认零写（dry-run），显式 execute 才动盘。

判定三元组（本引擎的全部判据都由此派生）：
    bag  = 袋里那版改动
    base = 袋创建时 HEAD 的内容（袋的 base_head）
    head = 今天 HEAD 的内容
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from scripts.governance.session_takeover_ledger import (
    ATTR_ABSORBED,
    ATTR_MIGRATED,
    ATTR_NEVER_LANDED,
    ATTR_NEWFILE_DIFF,
    ATTR_NO_BASE,
    ATTR_NO_FP,
    ATTR_PRISTINE_LOST,
    ATTR_SUPERSEDED,
    NO_WRITE_OFF_CLASSES,
    SETTLEABLE_CLASSES,
    GitBlobReader,
    classify_entry,
    git_blob_sha1,
    head_blob_index,
    sweep_with_attribution,
    triage_bag,
)

_BAGS = ".runtime/commit_queue"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """一个带两次提交的迷你仓（HEAD 有 base_HEAD 与后续改动两个 payment 面）。"""
    root = tmp_path
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t.t")
    _git(root, "config", "user.name", "test")
    _git(root, "config", "commit.gpgsign", "false")
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("v1\n", encoding="utf-8", newline="\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "base")
    (root / ".runtime" / "commit_queue" / "blobs").mkdir(parents=True)
    return root


def _store_blob(root: Path, content: str) -> dict:
    """把一个内容存进队列 blobs 目录，返回对应的袋 files[] 条目体。"""
    raw = content.encode()
    sha = hashlib.sha256(raw).hexdigest()
    (root / _BAGS / "blobs" / sha).write_bytes(raw)
    return {"blob_sha256": sha, "blob_ref": f"blobs/{sha}"}


def _write_file(root: Path, rel: str, content: str, *, commit_msg: str = "x") -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", commit_msg)


def _head(root: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()


class TestClassification:
    """八类归因的逐类钉死。"""

    def test_absorbed_when_content_matches_head(self, repo: Path) -> None:
        base = _head(repo)
        entry = {**_store_blob(repo, "v1\n"), "path": "src/a.py"}
        assert classify_entry(repo, entry, base) == (ATTR_ABSORBED, "src/a.py")
        assert classify_entry(repo, entry, base) == (ATTR_ABSORBED, "src/a.py")

    def test_superseded_when_someone_rewrote_afterwards(self, repo: Path) -> None:
        """袋死后有人改过这文件（HEAD≠base 且 ≠bag）→ 袋版本被取代。"""
        base = _head(repo)
        entry = {**_store_blob(repo, "bag-version\n"), "path": "src/a.py"}
        _write_file(repo, "src/a.py", "someone-else-version\n", commit_msg="later edit")
        with GitBlobReader(repo) as rd:
            assert classify_entry(repo, entry, base, reader=rd) == (ATTR_SUPERSEDED, "src/a.py")

    def test_pristine_lost_when_file_untouched_since_bag(self, repo: Path) -> None:
        """★核心：袋死后从头到尾没人碰过该文件 → 这版改动从未进入仓库。"""
        base = _head(repo)
        entry = {**_store_blob(repo, "never-landed\n"), "path": "src/a.py"}
        # 此后再无提交，HEAD == base
        assert classify_entry(repo, entry, base) == (ATTR_PRISTINE_LOST, "src/a.py")

    def test_never_landed_when_target_never_existed(self, repo: Path) -> None:
        """★目标文件在 HEAD 与 base 都不存在 —> 从来没建成。"""
        base = _head(repo)
        entry = {**_store_blob(repo, "x\n"), "path": "src/new_target.py"}
        assert classify_entry(repo, entry, base) == (ATTR_NEVER_LANDED, "src/new_target.py")

    def test_newfile_diff_when_bag_created_new_file_but_head_has_other_content(self, repo: Path) -> None:
        """袋在"新建"此文件，今天 HEAD 有同名但不同内容 → 不可确认是否被吸收。"""
        base = _head(repo)
        entry = {**_store_blob(repo, "my-new-file-v1\n"), "path": "src/brand_new.py"}
        _write_file(repo, "src/brand_new.py", "totally-different\n", commit_msg="others built it")
        with GitBlobReader(repo) as rd:
            assert classify_entry(repo, entry, base, reader=rd) == (ATTR_NEWFILE_DIFF, "src/brand_new.py")

    def test_migrated_when_content_moved_to_another_path(self, repo: Path) -> None:
        """Layer1 迁移感知：目标路径消失，但同样内容出现在别的路径。"""
        base = _head(repo)
        moved = "moved content v1\n"
        entry = {**_store_blob(repo, moved), "path": "src/old_location.py"}
        # HEAD 上没有 old_location，但同样的字节出现在 src/a.py
        _write_file(repo, "src/a.py", moved, commit_msg="rename+content carry")
        # old_location 从未在 HEAD 存在 → 走 never_landed 分支前先查迁移索引
        index = head_blob_index(repo)
        with GitBlobReader(repo) as rd:
            cls, note = classify_entry(repo, entry, base, reader=rd, blob_index=index)
        assert cls == ATTR_MIGRATED
        assert note == "src/a.py", "迁移备注应给出新路径"

    def test_no_base_when_bag_lacks_base_head(self, repo: Path) -> None:
        """无 base_head → 不能做史实归因，保守判 no_base。"""
        entry = {**_store_blob(repo, "whatever\n"), "path": "src/a.py"}
        assert classify_entry(repo, entry, None) == (ATTR_NO_BASE, "src/a.py")

    def test_no_fp_when_blob_missing_on_disk(self, repo: Path) -> None:
        """blobs 被 GC 迁走 / 老形条目无指纹 → 不可机判，不得误销。"""
        entry = {"blob_sha256": "deadbeef" * 8, "blob_ref": "blobs/nope", "path": "src/a.py"}
        assert classify_entry(repo, entry, _head(repo)) == (ATTR_NO_FP, "src/a.py")

    def test_empty_path_is_no_fp(self, repo: Path) -> None:
        assert classify_entry(repo, {"path": ""}, _head(repo)) == (ATTR_NO_FP, "")

    def test_crlf_only_difference_still_counts_as_absorbed(self, repo: Path) -> None:
        """行尾差异等价（第四夜 F4 治本的归因版继承）。"""
        base = _head(repo)
        raw = b"v1\r\n"
        sha = hashlib.sha256(raw).hexdigest()
        (repo / _BAGS / "blobs" / sha).write_bytes(raw)
        entry = {"blob_sha256": sha, "blob_ref": f"blobs/{sha}", "path": "src/a.py"}
        assert classify_entry(repo, entry, base) == (ATTR_ABSORBED, "src/a.py")


class TestTriageVerdict:
    """袋级分诊的三种裁决。"""

    def test_all_settleable_bag_is_settleable(self, repo: Path) -> None:
        base = _head(repo)
        _write_file(repo, "src/a.py", "someone-else-version\n", commit_msg="later")
        bag = {
            "qid": "q-1",
            "base_head": base,
            "files": [{**_store_blob(repo, "bag-version\n"), "path": "src/a.py"}],
        }
        assert triage_bag(repo, bag)["verdict"] == "settleable"

    def test_bag_with_pristine_lost_is_must_keep(self, repo: Path) -> None:
        """★不变量 SV：含 pristine_lost 的袋绝不判 settleable。"""
        base = _head(repo)
        bag = {
            "qid": "q-2",
            "base_head": base,
            "files": [{**_store_blob(repo, "never-landed\n"), "path": "src/a.py"}],
        }
        tri = triage_bag(repo, bag)
        assert tri["verdict"] == "must_keep"
        assert "不变量 SV" in tri["reason"]
        assert tri["lost_paths"][0]["path"] == "src/a.py"

    def test_bag_with_never_landed_is_must_keep(self, repo: Path) -> None:
        """★同上，never_landed 版。"""
        bag = {
            "qid": "q-3",
            "base_head": _head(repo),
            "files": [{**_store_blob(repo, "x\n"), "path": "src/brand_new.py"}],
        }
        tri = triage_bag(repo, bag)
        assert tri["verdict"] == "must_keep"
        assert tri["lost_paths"][0]["class"] == ATTR_NEVER_LANDED

    def test_single_protected_file_poisons_whole_bag(self, repo: Path) -> None:
        """9 个可销 + 1 个不可销 → 整袋必须保住（全袋制，保守）。"""
        base = _head(repo)
        files = []
        for i in range(9):
            files.append({**_store_blob(repo, f"gone-{i}\n"), "path": f"src/absent_{i}.py"})
        # 一个 pristine_lost：src/a.py 内容不同且此后无人改
        files.append({**_store_blob(repo, "precious\n"), "path": "src/a.py"})
        bag = {"qid": "q-4", "base_head": base, "files": files}
        assert triage_bag(repo, bag)["verdict"] == "must_keep"

    def test_classes_counts_are_reported(self, repo: Path) -> None:
        base = _head(repo)
        files = [
            {**_store_blob(repo, "never-landed\n"), "path": "src/a.py"},
            {**_store_blob(repo, "x\n"), "path": "src/absent.py"},
        ]
        tri = triage_bag(repo, bag := {"qid": "q-5", "base_head": base, "files": files})
        assert tri["classes"][ATTR_PRISTINE_LOST] == 1
        assert tri["classes"][ATTR_NEVER_LANDED] == 1
        assert tri["file_count"] == 2


class TestInvariantSV:
    """不变量 SV 的代数性质（错写法催收不到）。"""

    def test_settleable_and_no_write_off_are_disjoint(self) -> None:
        assert not (SETTLEABLE_CLASSES & NO_WRITE_OFF_CLASSES)

    def test_every_class_is_in_exactly_one_bucket(self) -> None:
        from scripts.governance.session_takeover_ledger import ATTRIBUTION_CLASSES

        union = SETTLEABLE_CLASSES | NO_WRITE_OFF_CLASSES
        assert set(ATTRIBUTION_CLASSES) == union, "存在未归类的分类，判据会漏"

    def test_no_write_off_covers_both_lost_families(self) -> None:
        assert ATTR_PRISTINE_LOST in NO_WRITE_OFF_CLASSES
        assert ATTR_NEVER_LANDED in NO_WRITE_OFF_CLASSES
        # 这两类绝不能被划进可销集合
        assert ATTR_PRISTINE_LOST not in SETTLEABLE_CLASSES
        assert ATTR_NEVER_LANDED not in SETTLEABLE_CLASSES


class TestSweepWriteDiscipline:
    """零写纪律：默认不动盘，execute 才搬。"""

    def _make_dead_bag(self, repo: Path, qid: str, content: str, *, base_head: str | None) -> Path:
        dead = repo / _BAGS / "dead"
        dead.mkdir(parents=True, exist_ok=True)
        bag = {
            "qid": qid,
            "session_id": "s1",
            "base_head": base_head,
            "files": [{**_store_blob(repo, content), "path": "src/a.py"}],
        }
        p = dead / f"{qid}.json"
        p.write_text(json.dumps(bag, ensure_ascii=False), encoding="utf-8")
        return p

    def test_dry_run_moves_nothing(self, repo: Path) -> None:
        base = _head(repo)
        _write_file(repo, "src/a.py", "later\n", commit_msg="later")
        p = self._make_dead_bag(repo, "q-dry", "bag\n", base_head=base)

        rep = sweep_with_attribution(repo, dry_run=True)

        assert p.exists(), "dry-run 不得动盘"
        assert rep["settleable_count"] == 1
        assert rep["dry_run"] is True

    def test_execute_archives_settleable_and_keeps_protected(self, repo: Path) -> None:
        base = _head(repo)
        _write_file(repo, "src/a.py", "later\n", commit_msg="later")
        settable = self._make_dead_bag(repo, "q-set", "bag-version\n", base_head=base)

        # 再造一个 pristine_lost 袋（src/b.py 存在于 base 且此后未改）
        (repo / "src" / "b.py").write_text("orig\n", encoding="utf-8", newline="\n")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "b")
        b_base = _head(repo)
        dead = repo / _BAGS / "dead"
        keep = dead / "q-keep.json"
        keep.write_text(
            json.dumps(
                {
                    "qid": "q-keep",
                    "session_id": "s1",
                    "base_head": b_base,
                    "files": [{**_store_blob(repo, "precious\n"), "path": "src/b.py"}],
                }
            ),
            encoding="utf-8",
        )

        rep = sweep_with_attribution(repo, dry_run=False)

        assert not settable.exists(), "可销账袋应被归档"
        assert (repo / _BAGS / "dead_archive" / "absorbed" / "q-set.json").exists()
        assert keep.exists(), "★不变量 SV：含 pristine_lost 的袋必须留在 dead/"
        assert rep["kept_count"] >= 1

    def test_salvage_ledger_is_written(self, repo: Path) -> None:
        base = _head(repo)
        self._make_dead_bag(repo, "q-6", "precious\n", base_head=base)
        sweep_with_attribution(repo, dry_run=False)
        ledger = repo / ".runtime" / "takeover" / "salvage_ledger.jsonl"
        assert ledger.exists()
        rows = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert rows and rows[0]["verdict"] == "must_keep"
        assert rows[0]["lost_paths"][0]["path"] == "src/a.py"


class TestHelpers:
    def test_git_blob_sha1_matches_git(self, repo: Path) -> None:
        """指纹口径必须与 git ls-tree 同真（否则迁移感知全失效）。"""
        content = b"hello world\n"
        idx = head_blob_index(repo)
        # src/a.py 内容是 "v1\n"，换一个内容验证算法本身
        (repo / "src" / "probe.py").write_bytes(content)
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "probe")
        idx = head_blob_index(repo)
        want = None
        for sha, paths in idx.items():
            if "src/probe.py" in paths:
                want = sha
                break
        assert want is not None
        assert git_blob_sha1(content) == want

    def test_head_blob_index_covers_all_paths(self, repo: Path) -> None:
        idx = head_blob_index(repo)
        flat = {p for paths in idx.values() for p in paths}
        assert "src/a.py" in flat

    def test_reader_returns_none_for_missing(self, repo: Path) -> None:
        with GitBlobReader(repo) as rd:
            assert rd.get("HEAD:src/nope.py") is None
            assert rd.get("HEAD:src/a.py") == b"v1\n"
