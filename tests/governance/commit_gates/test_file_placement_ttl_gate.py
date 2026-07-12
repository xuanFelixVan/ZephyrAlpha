# [TTL] task_bound
"""test_file_placement_ttl_gate.py — 文件放置与 TTL 一致性门禁单元测试（ARCH-049）。

测试组：
- TestGateSpecAttributes: GateSpec 属性（gate_id / priority）
- TestEmptyAndDeletion: 空文件列表 + deletion commit 跳过
- TestRule1PromotionBlocked: 规则1 永久区新文件准入（PROMOTION_BLOCKED）
- TestRule1ExemptSubdirs: 规则1 exempt_subdirs 生成器豁免
- TestRule1TrackedFile: 规则1 已 tracked 文件不触发
- TestRule2TtlZoneConsistency: 规则2 TTL↔zone 一致性
- TestRule3RootSubdir: 规则3 根目录子目录准入
- TestFailClosed: fail-closed YAML 真源缺失阻断
- TestTtlLegalValuesFailClosed: TTL 合法值缺失阻断
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

# 确保能 import zephyr.*
_SRC = Path(__file__).parent.parent.parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from zephyr.gov_enforcement.commit_gates.file_placement_ttl_gate import (  # noqa: E402
    make_file_placement_ttl_gate,
)


# ============================================================
# 测试夹具：构建临时 repo + 真源 YAML stub
# ============================================================

_DC_YAML = """\
# directory_contract.yaml stub（测试用）
schema_version: "1.0.0"
directory_zones:
  permanent:
    description: "永久区"
    paths:
      - "docs/01_policies_and_standards/"
      - "docs/02_enterprise_architecture/"
    default_ttl: permanent
    gate: allow_promote_required
    exempt_subdirs:
      - "docs/02_enterprise_architecture/00_overview_entry/"
  temporary:
    description: "临时区"
    paths:
      - "docs/_working/"
    default_ttl: task_bound
    gate: auto_archive
  neutral:
    description: "中性区"
    paths:
      - "src/"
      - "tests/"
      - "tmp/"
    default_ttl: null
    gate: none
"""

_TTL_VOCAB_YAML = """\
# ttl_vocabulary.yaml stub（测试用）
values:
  - value: permanent
    definition: "永久"
  - value: task_bound
    definition: "任务绑定"
decision_tree:
  nodes:
    Q1:
      criteria:
        - signal: path
          operator: contains
          value: "/changes/"
"""


def _setup_repo(tmp_path: Path) -> Path:
    """在 tmp_path 下构建临时 repo 结构（含真源 YAML stub）。"""
    # 创建真源 YAML
    dc = tmp_path / "docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml"
    dc.parent.mkdir(parents=True, exist_ok=True)
    dc.write_text(_DC_YAML, encoding="utf-8")

    tv = tmp_path / "docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml"
    tv.parent.mkdir(parents=True, exist_ok=True)
    tv.write_text(_TTL_VOCAB_YAML, encoding="utf-8")

    return tmp_path


def _make_gateway(project_root: Path, tracked_files: set[str] | None = None) -> MagicMock:
    """构建 mock gateway（project_root + _is_git_tracked）。

    Args:
        project_root: 仓库根路径。
        tracked_files: 已 git tracked 的相对路径集合（用 "/" 分隔）。
    """
    gw = MagicMock()
    gw.project_root = project_root
    tracked = tracked_files or set()

    def _is_git_tracked(rel_path: str) -> bool:
        return rel_path.replace("\\", "/") in tracked

    gw._is_git_tracked = _is_git_tracked
    return gw


def _make_file(repo_dir: Path, rel: str, content: str = "# stub\n") -> Path:
    """在 repo_dir 下创建目标文件，返回绝对路径。"""
    f = repo_dir / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(content, encoding="utf-8")
    return f


# ============================================================
# 测试组
# ============================================================

class TestGateSpecAttributes:
    """GateSpec 属性。"""

    def test_gate_id(self) -> None:
        spec = make_file_placement_ttl_gate()
        assert spec.gate_id == "FILE-PLACEMENT-TTL"

    def test_priority(self) -> None:
        spec = make_file_placement_ttl_gate()
        assert spec.priority == 33


class TestEmptyAndDeletion:
    """空文件列表 + deletion commit。"""

    def test_empty_files_pass(self, tmp_path: Path) -> None:
        repo = _setup_repo(tmp_path)
        gw = _make_gateway(repo)
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [])
        assert passed is True

    def test_deletion_commit_skipped(self, tmp_path: Path) -> None:
        """文件不存在（deletion commit）跳过。"""
        repo = _setup_repo(tmp_path)
        gw = _make_gateway(repo)
        spec = make_file_placement_ttl_gate()
        # 不存在的文件路径
        nonexistent = str(repo / "docs/01_policies_and_standards/deleted.yaml")
        passed, detail = spec.check(gw, [nonexistent])
        assert passed is True


class TestRule1PromotionBlocked:
    """规则1：永久区新文件准入（PROMOTION_BLOCKED）。"""

    def test_new_file_in_permanent_blocked(self, tmp_path: Path) -> None:
        """永久区新文件（未 tracked）无 allow_promote → 阻断。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(repo, "docs/01_policies_and_standards/new_rule.yaml")
        gw = _make_gateway(repo, tracked_files=set())  # 空集合=全部未 tracked
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is False
        assert "PROMOTION_BLOCKED" in detail

    def test_new_file_in_permanent_allow_promote(self, tmp_path: Path) -> None:
        """永久区新文件 + allow_promote=True → 通过规则1。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(repo, "docs/01_policies_and_standards/new_rule.yaml")
        gw = _make_gateway(repo, tracked_files=set())
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)], allow_promote=True)
        # 规则1 通过（规则2/3 不触发：无 ttl 字段 + 已在登记子目录）
        assert passed is True, f"expected pass, got: {detail}"


class TestRule1ExemptSubdirs:
    """规则1：exempt_subdirs 生成器豁免。"""

    def test_exempt_subdir_pass(self, tmp_path: Path) -> None:
        """exempt_subdirs 路径下新文件无需 allow_promote。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(repo, "docs/02_enterprise_architecture/00_overview_entry/generated.md")
        gw = _make_gateway(repo, tracked_files=set())
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is True, f"expected pass, got: {detail}"


class TestRule1TrackedFile:
    """规则1：已 tracked 文件不触发（修改文件）。"""

    def test_tracked_file_in_permanent_ok(self, tmp_path: Path) -> None:
        """永久区已 tracked 文件修改不触发规则1。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(repo, "docs/01_policies_and_standards/existing.yaml")
        gw = _make_gateway(repo, tracked_files={"docs/01_policies_and_standards/existing.yaml"})
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is True, f"expected pass, got: {detail}"


class TestRule2TtlZoneConsistency:
    """规则2：TTL↔zone 一致性。"""

    def test_permanent_ttl_in_temporary_blocked(self, tmp_path: Path) -> None:
        """ttl=permanent 但在临时区 → 阻断。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(repo, "docs/_working/note.md", content="---\nttl: permanent\n---\n")
        gw = _make_gateway(repo, tracked_files={"docs/_working/note.md"})
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is False
        assert "permanent" in detail and "临时区" in detail

    def test_task_bound_ttl_in_permanent_blocked(self, tmp_path: Path) -> None:
        """ttl=task_bound 但在永久区 → 阻断。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(
            repo, "docs/01_policies_and_standards/rule.yaml",
            content="---\nttl: task_bound\n---\n",
        )
        gw = _make_gateway(repo, tracked_files={"docs/01_policies_and_standards/rule.yaml"})
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is False
        assert "task_bound" in detail and "永久区" in detail

    def test_no_ttl_field_pass(self, tmp_path: Path) -> None:
        """无 ttl 字段 → 规则2 不触发。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(repo, "docs/01_policies_and_standards/no_ttl.yaml", content="# no ttl\n")
        gw = _make_gateway(repo, tracked_files={"docs/01_policies_and_standards/no_ttl.yaml"})
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is True, f"expected pass, got: {detail}"


class TestRule3RootSubdir:
    """规则3：根目录子目录准入。"""

    def test_unregistered_root_subdir_blocked(self, tmp_path: Path) -> None:
        """未登记的根子目录新文件 → 阻断。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(repo, "audit_assignment/plan.md")
        gw = _make_gateway(repo, tracked_files=set())
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is False
        assert "audit_assignment/" in detail

    def test_registered_root_subdir_pass(self, tmp_path: Path) -> None:
        """已登记的根子目录新文件 → 通过规则3。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(repo, "src/new_module.py")
        gw = _make_gateway(repo, tracked_files=set())
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)], allow_promote=False)
        # src/ 在 neutral zone，不触发规则1；无 ttl 不触发规则2；src/ 已登记不触发规则3
        assert passed is True, f"expected pass, got: {detail}"

    def test_hidden_dir_exempt(self, tmp_path: Path) -> None:
        """隐藏目录（. 开头）豁免规则3。"""
        repo = _setup_repo(tmp_path)
        f = _make_file(repo, ".aidrafts/session/file.py")
        gw = _make_gateway(repo, tracked_files=set())
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is True, f"expected pass, got: {detail}"


class TestFailClosed:
    """fail-closed：YAML 真源缺失阻断。"""

    def test_dc_missing_fail_closed(self, tmp_path: Path) -> None:
        """directory_contract.yaml 缺失 → 阻断。"""
        # 不创建真源 YAML
        gw = _make_gateway(tmp_path)
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(tmp_path / "any.py")])
        assert passed is False
        assert "fail-closed" in detail or "not found" in detail


class TestTtlLegalValuesFailClosed:
    """TTL 合法值缺失阻断（ARCH-049 审查问题6 修复）。"""

    def test_ttl_values_missing_fail_closed(self, tmp_path: Path) -> None:
        """ttl_vocabulary.yaml 缺少 permanent/task_bound → 阻断。"""
        repo = tmp_path
        # 创建 directory_contract.yaml（正常）
        dc = repo / "docs/01_policies_and_standards/_registry/contracts/directory_contract.yaml"
        dc.parent.mkdir(parents=True, exist_ok=True)
        dc.write_text(_DC_YAML, encoding="utf-8")

        # 创建 ttl_vocabulary.yaml（缺少 values）
        tv = repo / "docs/01_policies_and_standards/_registry/vocabularies/ttl_vocabulary.yaml"
        tv.parent.mkdir(parents=True, exist_ok=True)
        tv.write_text("values: []\ndecision_tree:\n  nodes:\n    Q1:\n      criteria: []\n", encoding="utf-8")

        f = _make_file(repo, "src/test.py")
        gw = _make_gateway(repo, tracked_files=set())
        spec = make_file_placement_ttl_gate()
        passed, detail = spec.check(gw, [str(f)])
        assert passed is False
        assert "permanent/task_bound" in detail or "缺少必需值" in detail
