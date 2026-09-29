# [A_test] module_id: MOD-GOV_backfill_roor_reg_annotation_tests | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-005 | scripts/governance/d3_metadata/backfill_roor_reg_annotation.py | §
# [MODULE] tests.governance.d3_metadata.test_backfill_roor_reg_annotation
# [DOMAIN] D_GOV_SCRIPTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] permanent
"""test_backfill_roor_reg_annotation.py — ROOR 册页 REG 名批注扫描/回填机制单测

覆盖契约（F92 处方）：
- TestScanClassify     扫描对账四态：ok/missing/unreachable/nofile + summary 漂移
- TestMissingMapping   缺册识别：同册多 REG 归并、auto 车道分桶（机生文件禁直改）
- TestInjectionForms   批注注入位四形态 + CRLF 保真 + 多 REG 一行点全名
- TestDiffAndPatch     建议 diff 形态（unified/可 git apply）+ generator 车道默认隔离
- TestApplyGate        apply 门位：--only 白名单、auto 拒写、CAS 基线哈希透传
- TestCheckCli         --check 门出口 0/1、--apply 缺 --only 拒绝（EXIT_ERROR）

测试隔离：全部 tmp_path 造迷你仓库，不读不写真实仓库业务路径（宪法测试隔离铁律）。
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_SCRIPTS_DIR = _PROJECT_ROOT / "scripts" / "governance" / "d3_metadata"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import backfill_roor_reg_annotation as brr  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers：迷你仓库构造
# ---------------------------------------------------------------------------

CATS = "docs/01_policies_and_standards/_registry/catalogs"


def _roor_yaml(entries: list[dict], summary_total: int | None = 99) -> str:
    lines = ["tiers:", "  - tier: 0", "    registries:"]
    for e in entries:
        lines += [
            f"      - registry_id: {e['registry_id']}",
            f"        physical_path: {e['physical_path']}",
            f"        maintenance: {e.get('maintenance', 'manual')}",
            f"        format: {e.get('format', 'yaml')}",
        ]
    if summary_total is not None:
        lines += ["summary:", f"  total_registries: {summary_total}"]
    return "\n".join(lines) + "\n"


def _mk_repo(tmp_path: Path, entries: list[dict], files: dict[str, str], summary_total: int | None = 99):
    (tmp_path / CATS).mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        f = tmp_path / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content, encoding="utf-8", newline="")
    roor_rel = "docs/registry_of_registries.yaml"
    (tmp_path / roor_rel).write_text(_roor_yaml(entries, summary_total), encoding="utf-8")
    return load_roor(tmp_path)


def load_roor(tmp_path: Path) -> dict:
    return brr.load_yaml(tmp_path / "docs/registry_of_registries.yaml")


def _fake_writer(records: list):
    def writer(path: Path, new_content: str, expected_sha: str) -> None:
        records.append((path, new_content, expected_sha))
        path.write_text(new_content, encoding="utf-8", newline="")

    return writer


# ---------------------------------------------------------------------------
# TestScanClassify
# ---------------------------------------------------------------------------


class TestScanClassify:
    def test_four_states_and_summary_drift(self, tmp_path: Path) -> None:
        entries = [
            {"registry_id": "REG-OK-001", "physical_path": f"{CATS}/ok_reg.yaml"},
            {"registry_id": "REG-MISS-001", "physical_path": f"{CATS}/miss_reg.yaml"},
            {"registry_id": "REG-AUTO-001", "physical_path": f"{CATS}/auto_reg.yaml", "maintenance": "auto （gen.py）"},
            {"registry_id": "REG-DB-001", "physical_path": "postgresql://localhost:5432/depgraph"},
            {"registry_id": "REG-GONE-001", "physical_path": f"{CATS}/vanished.yaml"},
        ]
        files = {
            f"{CATS}/ok_reg.yaml": "# [ROOR] registry_id=REG-OK-001\nkey: v\n",
            f"{CATS}/miss_reg.yaml": "key: v\n",
            f"{CATS}/auto_reg.yaml": "key: v\n",
        }
        result = brr.classify_entries(_mk_repo(tmp_path, entries, files), tmp_path)
        by_rid = {r["registry_id"]: r for r in result["rows"]}
        assert by_rid["REG-OK-001"]["status"] == "ok"
        assert by_rid["REG-MISS-001"]["status"] == "missing"
        assert by_rid["REG-MISS-001"]["lane"] == "manual"
        assert by_rid["REG-AUTO-001"]["status"] == "missing"
        assert by_rid["REG-AUTO-001"]["lane"] == "generator"
        assert by_rid["REG-DB-001"]["status"] == "unreachable"
        assert by_rid["REG-GONE-001"]["status"] == "nofile"
        assert result["total_entries"] == 5
        assert result["summary_total_registries"] == 99
        assert result["summary_drift"] is True

    def test_summary_consistent_no_drift(self, tmp_path: Path) -> None:
        entries = [{"registry_id": "REG-OK-001", "physical_path": f"{CATS}/ok_reg.yaml"}]
        files = {f"{CATS}/ok_reg.yaml": "# [ROOR] registry_id=REG-OK-001\nkey: v\n"}
        result = brr.classify_entries(_mk_repo(tmp_path, entries, files, summary_total=1), tmp_path)
        assert result["summary_drift"] is False

    def test_dir_path_is_unreachable(self, tmp_path: Path) -> None:
        (tmp_path / "data" / "cards").mkdir(parents=True)
        entries = [{"registry_id": "REG-DIR-001", "physical_path": "data/cards/"}]
        result = brr.classify_entries(_mk_repo(tmp_path, entries, {}), tmp_path)
        assert result["rows"][0]["status"] == "unreachable"


# ---------------------------------------------------------------------------
# TestMissingMapping
# ---------------------------------------------------------------------------


class TestMissingMapping:
    def test_same_path_multi_rid_grouped(self, tmp_path: Path) -> None:
        entries = [
            {"registry_id": "REG-BBB-001", "physical_path": f"{CATS}/shared.yaml"},
            {"registry_id": "REG-AAA-002", "physical_path": f"{CATS}/shared.yaml"},
            {"registry_id": "REG-CCC-001", "physical_path": f"{CATS}/solo.yaml"},
        ]
        files = {f"{CATS}/shared.yaml": "k: v\n", f"{CATS}/solo.yaml": "k: v\n"}
        result = brr.classify_entries(_mk_repo(tmp_path, entries, files), tmp_path)
        grouped = result["grouped_missing"]
        assert grouped[f"{CATS}/shared.yaml"] == ["REG-AAA-002", "REG-BBB-001"]  # 排序归并
        assert grouped[f"{CATS}/solo.yaml"] == ["REG-CCC-001"]

    def test_lane_buckets(self, tmp_path: Path) -> None:
        entries = [
            {"registry_id": "REG-M-001", "physical_path": f"{CATS}/m.yaml", "maintenance": "manual"},
            {"registry_id": "REG-A-001", "physical_path": f"{CATS}/a.yaml", "maintenance": "auto （x.py 机生）"},
        ]
        files = {f"{CATS}/m.yaml": "k: v\n", f"{CATS}/a.yaml": "k: v\n"}
        result = brr.classify_entries(_mk_repo(tmp_path, entries, files), tmp_path)
        lanes = {r["registry_id"]: r["lane"] for r in result["missing"]}
        assert lanes == {"REG-M-001": "manual", "REG-A-001": "generator"}


# ---------------------------------------------------------------------------
# TestInjectionForms
# ---------------------------------------------------------------------------


class TestInjectionForms:
    def test_frontmatter_md_inserts_inside_block(self) -> None:
        content = "---\ntitle: t\nstatus: Active\n---\nbody\n"
        out = brr.propose_content(content, ["REG-BP-001"], ".md")
        lines = out.splitlines()
        assert lines[0] == "---"
        assert lines[1] == "# [ROOR] registry_id=REG-BP-001"
        assert lines[2] == "title: t"

    def test_py_header_keeps_first_line_invariant(self) -> None:
        content = "# [BLUEPRINT] MOD-X | p.py | §\n# [MODULE] x\nCODE = 1\n"
        out = brr.propose_content(content, ["REG-X-001"], ".py")
        lines = out.splitlines()
        assert lines[0].startswith("# [BLUEPRINT]")
        assert lines[1] == "# [ROOR] registry_id=REG-X-001"

    def test_plain_yaml_inserts_top(self) -> None:
        out = brr.propose_content("module_id: M\nkey: v\n", ["REG-Y-001"], ".yaml")
        assert out.splitlines()[0] == "# [ROOR] registry_id=REG-Y-001"
        assert out.splitlines()[1] == "module_id: M"

    def test_bare_md_gets_html_comment(self) -> None:
        out = brr.propose_content("# Title\ntext\n", ["REG-MD-001"], ".md")
        assert out.splitlines()[0] == "<!-- [ROOR] registry_id=REG-MD-001 -->"

    def test_crlf_preserved_and_multi_rid_one_line(self) -> None:
        content = "k: v\r\nj: w\r\n"
        out = brr.propose_content(content, ["REG-B-002", "REG-A-001"], ".yaml")
        assert "\r\n" in out
        assert out.splitlines()[0] == "# [ROOR] registry_id=REG-A-001 REG-B-002"

    def test_parse_annotation_ids_roundtrip(self) -> None:
        content = "# [ROOR] registry_id=REG-A-001 REG-B-002\nk: v\n"
        assert brr.parse_annotation_ids(content) == ["REG-A-001", "REG-B-002"]

    def test_propose_is_idempotent_after_reparse(self, tmp_path: Path) -> None:
        content = "k: v\n"
        once = brr.propose_content(content, ["REG-Z-001"], ".yaml")
        ids = brr.parse_annotation_ids(once)
        assert ids == ["REG-Z-001"]
        twice = brr.propose_content(once, ["REG-Z-001"], ".yaml")
        assert brr.parse_annotation_ids(twice).count("REG-Z-001") == 2  # 机制不隐去重复——由 scan 判 ok 不再注入


# ---------------------------------------------------------------------------
# TestDiffAndPatch
# ---------------------------------------------------------------------------


class TestDiffAndPatch:
    def _repo_with_debt(self, tmp_path: Path):
        entries = [
            {"registry_id": "REG-M-001", "physical_path": f"{CATS}/m.yaml", "maintenance": "manual"},
            {"registry_id": "REG-A-001", "physical_path": f"{CATS}/a.yaml", "maintenance": "auto （x.py）"},
        ]
        files = {f"{CATS}/m.yaml": "k: v\n", f"{CATS}/a.yaml": "k: v\n"}
        return brr.classify_entries(_mk_repo(tmp_path, entries, files), tmp_path)

    def test_diff_shape(self, tmp_path: Path) -> None:
        result = self._repo_with_debt(tmp_path)
        diffs = brr.build_all_diffs(result, tmp_path)
        assert len(diffs) == 1  # auto 车道默认隔离
        d = diffs[0]
        assert d.startswith(f"--- a/{CATS}/m.yaml")
        assert f"+++ b/{CATS}/m.yaml" in d
        assert "@@" in d
        assert "+# [ROOR] registry_id=REG-M-001" in d

    def test_include_auto_diff_flag(self, tmp_path: Path) -> None:
        result = self._repo_with_debt(tmp_path)
        diffs = brr.build_all_diffs(result, tmp_path, include_auto=True)
        assert len(diffs) == 2

    def test_patch_file_written(self, tmp_path: Path) -> None:
        result = self._repo_with_debt(tmp_path)
        diffs = brr.build_all_diffs(result, tmp_path)
        pf = tmp_path / "out" / "f92.patch"
        pf.parent.mkdir(parents=True, exist_ok=True)
        pf.write_text("".join(diffs), encoding="utf-8")
        assert "+# [ROOR]" in pf.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# TestApplyGate
# ---------------------------------------------------------------------------


class TestApplyGate:
    def _repo(self, tmp_path: Path):
        entries = [
            {"registry_id": "REG-M-001", "physical_path": f"{CATS}/m.yaml", "maintenance": "manual"},
            {"registry_id": "REG-A-001", "physical_path": f"{CATS}/a.yaml", "maintenance": "auto （x.py）"},
        ]
        files = {f"{CATS}/m.yaml": "k: v\n", f"{CATS}/a.yaml": "k: v\n"}
        return brr.classify_entries(_mk_repo(tmp_path, entries, files), tmp_path)

    def test_apply_only_listed_and_cas_hash(self, tmp_path: Path) -> None:
        result = self._repo(tmp_path)
        records: list = []
        written, skipped = brr.apply_backfill(result, tmp_path, [f"{CATS}/m.yaml"], writer=_fake_writer(records))
        assert written == [f"{CATS}/m.yaml"]
        assert skipped == []
        path, new_content, expected = records[0]
        old = "k: v\n"
        assert expected == hashlib.sha256(old.encode("utf-8")).hexdigest()
        assert new_content.startswith("# [ROOR] registry_id=REG-M-001\n")
        assert (tmp_path / f"{CATS}/m.yaml").read_text(encoding="utf-8") == new_content

    def test_apply_refuses_auto_lane_and_unknown(self, tmp_path: Path) -> None:
        result = self._repo(tmp_path)
        records: list = []
        written, skipped = brr.apply_backfill(
            result,
            tmp_path,
            [f"{CATS}/a.yaml", f"{CATS}/ghost.yaml"],
            writer=_fake_writer(records),
        )
        assert written == []
        assert len(skipped) == 2
        assert records == []

    def test_apply_normalizes_path(self, tmp_path: Path) -> None:
        result = self._repo(tmp_path)
        records: list = []
        written, _ = brr.apply_backfill(result, tmp_path, [f"./{CATS}/m.yaml"], writer=_fake_writer(records))
        assert written == [f"{CATS}/m.yaml"]


# ---------------------------------------------------------------------------
# TestCheckCli
# ---------------------------------------------------------------------------


class TestCheckCli:
    def _run_main(self, tmp_path: Path, *extra: str) -> int:
        import contextlib
        import io

        argv = [
            "prog",
            "--repo-root",
            str(tmp_path),
            *extra,
        ]
        monkey = pytest.MonkeyPatch()
        monkey.setattr(sys, "argv", argv)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                return brr.main()
        finally:
            monkey.undo()

    def test_check_pass_and_fail(self, tmp_path: Path) -> None:
        entries = [
            {"registry_id": "REG-OK-001", "physical_path": f"{CATS}/ok.yaml"},
            {"registry_id": "REG-MISS-001", "physical_path": f"{CATS}/miss.yaml"},
        ]
        files = {f"{CATS}/ok.yaml": "# [ROOR] registry_id=REG-OK-001\nk: v\n", f"{CATS}/miss.yaml": "k: v\n"}
        _mk_repo(tmp_path, entries, files)
        assert self._run_main(tmp_path, "--check") == brr.EXIT_FINDINGS

        (tmp_path / CATS / "miss.yaml").write_text("# [ROOR] registry_id=REG-MISS-001\nk: v\n", encoding="utf-8")
        assert self._run_main(tmp_path, "--check") == brr.EXIT_PASS

    def test_apply_without_only_rejected(self, tmp_path: Path) -> None:
        entries = [{"registry_id": "REG-MISS-001", "physical_path": f"{CATS}/miss.yaml"}]
        _mk_repo(tmp_path, entries, {f"{CATS}/miss.yaml": "k: v\n"})
        assert self._run_main(tmp_path, "--apply") == brr.EXIT_ERROR
