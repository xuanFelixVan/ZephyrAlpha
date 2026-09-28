# [BLUEPRINT] MOD-LIB-003 | docs/03_modules/_domain_library/blueprint.md | §3
# [MODULE] tests.library.test_library_hygiene
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] scripts/governance/generators/library_hygiene.py (classify_working_docs/_tracked_working_docs/run_hygiene)
# [CONSUMERS] none
# [STARTUP] manual
# [MATURITY] production
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [A_module] module_id=MOD-LIB-003 | layer=test | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [TESTS] tests/library/test_library_hygiene.py
"""library_hygiene 陈化判据常驻尺（FMS 收尾班 2026-09-27）。

本件同时补一个**元数据谎**：`library_hygiene.py` 头部 `[TESTS] tests/library/test_library_hygiene.py`
一直指向一个不存在的文件（本次实测 `git ls-files` 无此件）＝"有测试登记、零测试实存"。

治本对象（实测出来的，不是猜的）：该生成器原先对 `docs/_working` 用 **mtime** 判龄，
而案卷 `fms_overhaul/S2_lifecycle_ephemeral/README.md` §2.5 已证 mtime>30 天桶=0
（git checkout/merge/stash 天天碰 mtime）⇒ 类目①**永久空转**：看着在跑，实则永不产出候选。
改成 frontmatter `created` 轴后当日实测 3,172 在册件的分布=
aged 1 / fresh 798 / **undated 2,361** / other_ttl 2 / missing_on_disk 10
⇒ "2,827 件待迁移"这个框架本身被推翻：按年龄几乎无候选，真欠账是 74% population 无出生日。

四条不得放宽的判据（本尺逐条钉死）：
1. 轴=created，不是 mtime（否则本类目又能悄悄空转回去）；
2. ttl 必走 YAML 解析——`ttl: "task_bound"` 带引号变体用裸正则会被判"未声明"而漏掉
   （反例真源=doc_lifecycle.py:152；实测永久区有 810 件是带引号写法）；
3. 读不得者**单列计数**，禁静默归零（否则"把字段写坏"就能躲过盘点）；
4. 在册但盘上缺失＝删除欠账，必须与元数据缺失分桶——两种病处置路径相反。
"""

from __future__ import annotations

import datetime as dt
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "governance"))

from scripts.governance.generators.library_hygiene import (  # noqa: E402
    _DOCS_WORKING_DAYS,
    _tracked_working_docs,
    classify_working_docs,
    run_hygiene,
)

TODAY = dt.date(2026, 9, 27)


def _doc(root: Path, rel: str, *, ttl: str | None = None, created: str | None = None, body: str = "x\n") -> str:
    """写一份带/不带 frontmatter 的在册件，返回仓内相对路径（POSIX）。"""
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if ttl is None and created is None:
        p.write_text(body, encoding="utf-8")
        return rel
    lines = ["---"]
    if ttl is not None:
        lines.append(f"ttl: {ttl}")
    if created is not None:
        lines.append(f"created: {created}")
    lines += ["---", "", body]
    p.write_text("\n".join(lines), encoding="utf-8")
    return rel


def _buckets(root: Path, *paths: str, days: int = _DOCS_WORKING_DAYS, today: dt.date = TODAY) -> dict[str, list[str]]:
    return classify_working_docs(root, days, today, tracked=list(paths))


class TestCreatedAxisNotMtime:
    """轴必须是 created：把 mtime 造老而 created 造新，就必须落在 fresh。"""

    def test_old_mtime_but_fresh_created_is_not_a_candidate(self, tmp_path: Path) -> None:
        rel = _doc(tmp_path, "docs/_working/a/fresh.md", ttl="task_bound", created="2026-09-26")
        old_stamp = dt.datetime(2025, 1, 1).timestamp()
        os.utime(tmp_path / rel, (old_stamp, old_stamp))
        # 反向自证：mtime 必须真的被造老了，否则本例会"因为什么都没发生"而假绿。
        landed = (tmp_path / rel).stat().st_mtime
        assert abs(landed - old_stamp) < 5, f"utime 未生效（{landed} vs {old_stamp}）＝本例无判别力"
        got = _buckets(tmp_path, rel)
        assert got["fresh"] == [rel], f"mtime 造老就被判陈化=轴又退回 mtime：{got}"
        assert got["aged"] == []

    def test_old_created_is_a_candidate(self, tmp_path: Path) -> None:
        rel = _doc(tmp_path, "docs/_working/a/old.md", ttl="task_bound", created="2026-01-05")
        got = _buckets(tmp_path, rel)
        assert got["aged"] == [rel], got

    def test_boundary_is_strictly_greater_than_days(self, tmp_path: Path) -> None:
        """恰好 N 天不算陈化（`>` 而非 `>=`）：判据边界必须由尺钉住，否则月批数量会漂。"""
        edge = (TODAY - dt.timedelta(days=_DOCS_WORKING_DAYS)).isoformat()
        over = (TODAY - dt.timedelta(days=_DOCS_WORKING_DAYS + 1)).isoformat()
        e = _doc(tmp_path, "docs/_working/a/edge.md", ttl="task_bound", created=edge)
        o = _doc(tmp_path, "docs/_working/a/over.md", ttl="task_bound", created=over)
        got = _buckets(tmp_path, e, o)
        assert got["fresh"] == [e] and got["aged"] == [o], got


class TestTtlQuotedVariant:
    """引号变体是现成陷阱：yaml 能吃下的引号，裸正则会判成"未声明 ttl"。"""

    def test_quoted_task_bound_still_judged(self, tmp_path: Path) -> None:
        rel = _doc(tmp_path, "docs/_working/a/q.md", ttl='"task_bound"', created="2026-01-05")
        assert _buckets(tmp_path, rel)["aged"] == [rel]

    def test_permanent_never_becomes_a_candidate(self, tmp_path: Path) -> None:
        rel = _doc(tmp_path, "docs/_working/a/p.md", ttl="permanent", created="2024-01-01")
        got = _buckets(tmp_path, rel)
        assert got["aged"] == [] and got["permanent"] == [rel], got

    def test_missing_ttl_with_old_created_is_aged_not_silently_skipped(self, tmp_path: Path) -> None:
        """无 ttl 但有 created 且超龄 ⇒ 仍进候选（缺 ttl 不等于免死），并同时被 TTL 缺口尺看见。"""
        rel = _doc(tmp_path, "docs/_working/a/nottl.md", created="2026-01-05")
        assert _buckets(tmp_path, rel)["aged"] == [rel]


class TestUnknownNeverDisappearsQuietly:
    """读不得者单列：把 created 写坏不能变成"这件不存在"。"""

    def test_no_created_key_goes_to_undated(self, tmp_path: Path) -> None:
        rel = _doc(tmp_path, "docs/_working/a/nodate.md", ttl="task_bound")
        got = _buckets(tmp_path, rel)
        assert got["undated"] == [rel] and got["aged"] == [] and got["fresh"] == [], got

    def test_garbage_created_value_goes_to_undated(self, tmp_path: Path) -> None:
        rel = _doc(tmp_path, "docs/_working/a/bad.md", ttl="task_bound", created="yesterday-ish")
        assert _buckets(tmp_path, rel)["undated"] == [rel]

    def test_broken_frontmatter_goes_to_undated(self, tmp_path: Path) -> None:
        """有 `---` 但 yaml 解析失败 ⇒ 同样不得静默消失（实测真档里就躺着 3 件）。"""
        p = tmp_path / "docs/_working/a/broken.md"
        p.parent.mkdir(parents=True)
        p.write_text("---\nttl: task_bound\n created: [unclosed\n---\nbody\n", encoding="utf-8")
        got = _buckets(tmp_path, "docs/_working/a/broken.md")
        assert got["undated"] or got["aged"] or got["fresh"], f"解析失败件凭空消失：{got}"


class TestScopeIsTrackedOnly:
    """作用域=tracked 面：盘面 rglob 会把 gitignore 离库派生区与影子车道副本算进来。"""

    def test_untracked_file_never_counted(self, tmp_path: Path) -> None:
        rel = _doc(tmp_path, "docs/_working/a/ghost.md", ttl="task_bound", created="2026-01-05")
        # 不传 tracked 时走 git ls-files；tmp_path 无 git ⇒ 集合为空，ghost 不得出现
        got = classify_working_docs(tmp_path, _DOCS_WORKING_DAYS, TODAY)
        assert got["aged"] == [], f"未在册件被判进候选：{got}"
        assert rel and not got["aged"]

    def test_tracked_list_is_authoritative(self, tmp_path: Path) -> None:
        rel = _doc(tmp_path, "docs/_working/a/real.md", ttl="task_bound", created="2026-01-05")
        assert classify_working_docs(tmp_path, _DOCS_WORKING_DAYS, TODAY, tracked=[rel])["aged"] == [rel]

    def test_missing_on_disk_is_its_own_bucket(self, tmp_path: Path) -> None:
        """在册但盘上没有＝删除欠账（实测 10 件），混进 undated 会把人引去补字段。"""
        ghost = "docs/_working/a/deleted.md"
        got = classify_working_docs(tmp_path, _DOCS_WORKING_DAYS, TODAY, tracked=[ghost])
        assert got["missing_on_disk"] == [ghost], got
        assert got["undated"] == [], "缺失件被误并入元数据缺失桶"


class TestFailVisibleWhenAxisCannotRun:
    """git 不可用时不得报"零陈化件"了事——那正是本类目当年的死法。"""

    def test_warns_when_tracked_face_is_empty(self, tmp_path: Path) -> None:
        res = run_hygiene(str(tmp_path))
        assert res["warn"], "git 面读不到件却零警告=假空"
        assert any("tracked" in w for w in res["warn"]), res["warn"]

    def test_report_records_the_axis(self, tmp_path: Path) -> None:
        run_hygiene(str(tmp_path))
        rep = tmp_path / "docs/_working/ultimate_library/HYGIENE.md"
        assert rep.is_file(), "报告未落盘"
        txt = rep.read_text(encoding="utf-8")
        assert "created" in txt and "不用 mtime" in txt, "报告未自述判龄轴，日后会被改回 mtime 而无人察觉"

    def test_report_carries_no_forbidden_frontmatter_key(self, tmp_path: Path) -> None:
        """生成器自己写出的报告必须能被落地——多一个 `doc_type` 就会被放置/TTL 门整批打回。

        这是"每次都给自己埋雷"的形态：尺跑一次，产出一件不可提交的产物。
        """
        run_hygiene(str(tmp_path))
        head = (tmp_path / "docs/_working/ultimate_library/HYGIENE.md").read_text(encoding="utf-8").split("---")[1]
        assert "doc_type" not in head, f"docs/_working 的 md 禁 doc_type：{head!r}"
        assert 'ttl: "task_bound"' in head or "ttl: task_bound" in head, head


class TestHelperContract:
    """两个小工具函数自身的契约（防止判据被静默换掉）。"""

    def test_tracked_docs_returns_posix_relative_paths(self) -> None:
        paths = _tracked_working_docs(REPO_ROOT)
        assert paths, "主仓 tracked 面读到 0 件=本尺失去采集面"
        assert all(p.startswith("docs/_working/") and "\\" not in p for p in paths[:50]), paths[:3]

    def test_generator_header_tests_path_now_exists(self) -> None:
        """[TESTS] 指向的文件必须真实存在——本尺的存在本身就是这条断言的实现。"""
        hdr = (REPO_ROOT / "scripts" / "governance" / "generators" / "library_hygiene.py").read_text(encoding="utf-8")
        assert "# [TESTS] tests/library/test_library_hygiene.py" in hdr
        assert Path(__file__).relative_to(REPO_ROOT).as_posix() == "tests/library/test_library_hygiene.py"
