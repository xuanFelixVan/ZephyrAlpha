# [A_test] module_id=MOD-GOV_COMMIT_QUEUE_LANDED_ID_PROBE_TEST | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.gov.governance.test_commit_queue_landed_id_probe
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] pytest; subprocess; json; hashlib; scripts.commit_queue
# [CONSUMERS] pytest 自动发现；LANDED_ID_FOREIGN 探针（2026-10-12 维护三班·通宵令队列完整性簇首件）红绿自证
# [STARTUP] python -m pytest tests/gov/governance/test_commit_queue_landed_id_probe.py
# [MATURITY] testing
# [INVARIANTS] 全 tmp 隔离（tmp git 仓 + tmp 队列根，绝不碰主仓 .runtime/commit_queue 与真实 dev）；
#              每条判据先证"能红"再证不误伤：假落地档必须真报出 qid，同内容/后继覆写档必须不点名
# [MODIFY-GUARD] 去掉 dev 现面二次核（把零命中一律判 foreign）或把 all_match 与 unverifiable 混档即红
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败即测试失败
# [TESTS] tests/gov/governance/test_commit_queue_landed_id_probe.py
# [TTL] permanent
"""test_commit_queue_landed_id_probe.py — done 项 landed_id 归属探针自证（只读探针）。

病根（在册第五形态）：landed_id 取提交后的 `git rev-parse HEAD`，并发窗口里他人提交会被记成
本袋落地号；现网实测 done/ 里两组共用 landed_id、backfix3-0011 与 gpux2-0004 的袋字节
既不在记录的 commit 也不在 dev 现面（=done 而内容从未落地）。
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "scripts"))

import commit_queue as cq  # noqa: E402


def _git(cwd: Path, *args: str) -> str:
    r = subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, timeout=60)
    assert r.returncode == 0, f"git {args} -> rc={r.returncode} {r.stderr.decode('utf-8', 'replace')[:300]}"
    return r.stdout.decode("utf-8", errors="replace").strip()


@pytest.fixture()
def probe_env(tmp_path: Path) -> tuple[Path, Path]:
    """裸 git 仓（dev 分支）+ 隔离队列根（done/ 与 blobs/ 建好）。"""
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "dev")
    _git(repo, "config", "user.email", "t@example.com")
    _git(repo, "config", "user.name", "test")
    _git(repo, "config", "core.autocrlf", "false")
    (repo / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(repo, "add", "seed.txt")
    _git(repo, "commit", "-qm", "init")
    qroot = tmp_path / "queue"
    (qroot / "done").mkdir(parents=True)
    (qroot / "blobs").mkdir(parents=True)
    return repo, qroot


def _commit_file(repo: Path, rel: str, text: str) -> str:
    """把内容提交进 dev，返回该笔 commit sha。

    newline="\\n" 是判据的一部分：write_text 缺省在 Windows 落 CRLF，而袋内 blob 字节是
    "\\n"——那样 all_match 永远测不出来（在册 write_text 默认 CRLF 假绿坑）。
    """
    (repo / rel).parent.mkdir(parents=True, exist_ok=True)
    (repo / rel).write_text(text, encoding="utf-8", newline="\n")
    _git(repo, "add", "--", rel)
    _git(repo, "commit", "-qm", f"land {rel}")
    return _git(repo, "rev-parse", "HEAD")


def _done_item(qroot: Path, qid: str, landed: str, files: list[tuple[str, str]]) -> None:
    """写一只 done 袋：files=[(路径, 袋内字节)]，blob_ref 按队列惯例落 blobs/。"""
    entries = []
    for rel, text in files:
        data = text.encode("utf-8")
        sha = hashlib.sha256(data).hexdigest()
        (qroot / "blobs" / sha).write_bytes(data)
        entries.append({"path": rel, "blob_ref": f"blobs/{sha}", "blob_sha256": sha, "action": "modify"})
    (qroot / "done" / f"{qid}.json").write_text(
        json.dumps({"qid": qid, "session_id": "st-probe", "landed_id": landed, "files": entries}, ensure_ascii=False),
        encoding="utf-8",
    )


def _audit(qroot: Path, repo: Path, **kw) -> dict:
    return cq.audit_landed_id_integrity(queue_root=qroot, repo_root=repo, **kw)


def test_matching_blob_reads_all_match(probe_env) -> None:
    """绿基座：袋字节==commit 里的 blob ⇒ all_match，且不进任何点名清单。"""
    repo, qroot = probe_env
    sha = _commit_file(repo, "docs/a.md", "one\n")
    _done_item(qroot, "q-ok", sha, [("docs/a.md", "one\n")])
    out = _audit(qroot, repo)
    assert out["verdict_counts"].get("all_match") == 1, out
    assert out["foreign_qids"] == [] and out["shared_landed_id_groups"] == []


def test_zero_match_and_absent_in_dev_is_named_as_foreign(probe_env) -> None:
    """红证臂（本探针存在的理由）：landed_id 是别人的提交、袋字节在 dev 也无面 ⇒ 点名。"""
    repo, qroot = probe_env
    other = _commit_file(repo, "docs/other.md", "someone else\n")
    _done_item(qroot, "q-foreign", other, [("docs/mine.md", "my content\n")])
    out = _audit(qroot, repo)
    assert out["verdict_counts"].get("foreign_zero_match_not_in_dev") == 1, out
    assert out["foreign_qids"] == ["q-foreign"], out


def test_zero_match_but_content_in_dev_reads_stale_superseded(probe_env) -> None:
    """不误伤臂：记录号里查无此内容、但 dev 现面有（后继袋把它落进去了）⇒ 记陈旧袋，不报假落地。"""
    repo, qroot = probe_env
    unrelated = _commit_file(repo, "docs/other.md", "other\n")  # 这一笔里没有 docs/x.md
    _commit_file(repo, "docs/x.md", "v1\n")  # 随后另一笔把袋内容送上 dev
    _done_item(qroot, "q-stale", unrelated, [("docs/x.md", "v1\n")])
    out = _audit(qroot, repo)
    assert out["verdict_counts"].get("stale_superseded") == 1, out
    assert out["foreign_qids"] == []


def test_shared_landed_id_across_two_items_is_grouped(probe_env) -> None:
    """共用落地号＝连坐/覆写嫌疑，必须成组点名（现网实测两组）。"""
    repo, qroot = probe_env
    sha = _commit_file(repo, "docs/s.md", "s\n")
    _done_item(qroot, "q-1", sha, [("docs/s.md", "s\n")])
    _done_item(qroot, "q-2", sha, [("docs/s.md", "s\n")])
    out = _audit(qroot, repo)
    groups = out["shared_landed_id_groups"]
    assert len(groups) == 1 and sorted(groups[0]["qids"]) == ["q-1", "q-2"], out


def test_value_shape_arms_are_not_counted_as_foreign(probe_env) -> None:
    """取值形态分档：空串/noop 哨兵/stub 各归各档，一律不进 foreign 名单。"""
    repo, qroot = probe_env
    _done_item(qroot, "q-empty", "", [("docs/e.md", "e\n")])
    _done_item(qroot, "q-noop", "noop@deadbeef", [("docs/n.md", "n\n")])
    _done_item(qroot, "q-stub", "stub:q-stub", [("docs/t.md", "t\n")])
    out = _audit(qroot, repo)
    assert out["verdict_counts"]["landed_id_absent"] == 1
    assert out["verdict_counts"]["landed_id_noop_sentinel"] == 1
    assert out["verdict_counts"]["landed_id_stub"] == 1
    assert out["foreign_qids"] == []


def test_ledger_backed_registry_book_is_unverifiable_not_matched(probe_env) -> None:
    """账本族册（/_registry/catalogs/）落地字节=PG 现读渲染，不代表袋字节 ⇒ 判"无从核"，
    既不冒认 all_match，也不冒判假落地（在册三口径不可互换）。"""
    repo, qroot = probe_env
    sha = _commit_file(repo, "docs/01_policies_and_standards/_registry/catalogs/any_book.yaml", "book: 1\n")
    _done_item(qroot, "q-reg", sha, [("docs/01_policies_and_standards/_registry/catalogs/any_book.yaml", "book: 2\n")])
    out = _audit(qroot, repo)
    assert out["verdict_counts"].get("unverifiable") == 1, out
    assert out["foreign_qids"] == []


def test_purged_blob_reference_is_unverifiable(probe_env) -> None:
    """袋内 blob 文件已被 purge ⇒ 无从核，不得当成"匹配"（降级态与无动作同形是在册假绿）。"""
    repo, qroot = probe_env
    sha = _commit_file(repo, "docs/p.md", "p\n")
    _done_item(qroot, "q-purged", sha, [("docs/p.md", "p\n")])
    for f in (qroot / "blobs").glob("*"):
        f.unlink()
    out = _audit(qroot, repo)
    assert out["verdict_counts"].get("unverifiable") == 1, out


def test_budget_truncation_is_declared_not_silent(probe_env) -> None:
    """预算截断必须显影：只给 1 次检查额度时 truncated=True（半集当全集是在册计数坑）。"""
    repo, qroot = probe_env
    sha = _commit_file(repo, "docs/b.md", "b\n")
    _done_item(qroot, "q-b1", sha, [("docs/b.md", "b\n")])
    _done_item(qroot, "q-b2", sha, [("docs/c.md", "c\n")])
    out = _audit(qroot, repo, max_checks=1)
    assert out["truncated"] is True, out
    assert out["scanned_items"] <= 2 and out["budget"]["max_checks"] == 1


def test_unreadable_done_item_is_counted_not_dropped(probe_env) -> None:
    """坏 JSON 也要有出口计数（每出口独立），不能静默消失。"""
    repo, qroot = probe_env
    sha = _commit_file(repo, "docs/u.md", "u\n")
    (qroot / "done" / "q-broken.json").write_text("{ not json", encoding="utf-8")
    _done_item(qroot, "q-u", sha, [("docs/u.md", "u\n")])
    out = _audit(qroot, repo)
    assert out["verdict_counts"].get("item_unreadable") == 1, out
    assert out["verdict_counts"].get("all_match") == 1, out
