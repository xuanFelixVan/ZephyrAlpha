# [A_test] module_id=MOD-GOV_ssot_gate_test | suite=ssot_gate | scope=unit | safety=L | ai_autonomy=ai_modifiable

"""
test_ssot_gate — SSoT 创建门禁红蓝变异测试。

测试方案 E（零新真源，复用 [MODULE] 头）的核心链路：
  1. capability_lookup.find_files_by_module_path 反查正确性
  2. scaffold._check_duplicate_functionality 维度3 阻断正确性
  3. force_override 不跳过维度3（强不变量——同 module_path = 同文件身份）
  4. GitCommitGateway._check_ssot_canonical L2 兜底门禁
  5. 变异测试（falsifiability）：注入失效后阻断应消失，还原后阻断应恢复

红蓝对抗三层验证：
  - 功能层：门禁能正确阻断/放行
  - 不变量层：force_override 不跳过维度3
  - 可证伪层：变异注入后门禁失效，还原后恢复
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 确保项目根在 sys.path
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.scaffold import ScaffoldError, _check_duplicate_functionality
from zephyr.governance.capability_lookup import CapabilityLookup, HeaderInfo
from zephyr.governance.git_commit_gateway import CommitStatus, GitCommitGateway


# ---------------------------------------------------------------------------
# 辅助 fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def skip_dim1_dim2(monkeypatch):
    """跳过维度1/2（功能域注册表 + 蓝图关键词匹配），隔离维度3测试。

    通过让依赖模块 import 失败来跳过维度1/2，不影响维度3的 capability_lookup。
    """
    monkeypatch.setitem(sys.modules, "zephyr.infrastructure.registry_governance", None)
    monkeypatch.setitem(sys.modules, "zephyr.integration.mcp", None)


# ---------------------------------------------------------------------------
# 测试组 1：find_files_by_module_path 反查正确性
# ---------------------------------------------------------------------------

class TestFindFilesByModulePath:
    """测试 capability_lookup.find_files_by_module_path 反查正确性。"""

    def test_existing_module_path_returns_non_empty(self):
        """已有 module_path 应返回非空列表（用已知存活的 SSoT 验证）。"""
        lookup = CapabilityLookup()
        results = lookup.find_files_by_module_path("zephyr.governance.capability_lookup")
        assert len(results) > 0, "已知存活的 module_path 应返回非空列表"
        assert any("capability_lookup" in r for r in results)

    def test_nonexistent_module_path_returns_empty(self):
        """不存在的 module_path 应返回空列表。"""
        lookup = CapabilityLookup()
        results = lookup.find_files_by_module_path("zephyr.nonexistent.module_xyz_12345")
        assert results == [], "不存在的 module_path 应返回空列表"

    def test_empty_string_returns_empty(self):
        """空字符串应返回空列表。"""
        lookup = CapabilityLookup()
        assert lookup.find_files_by_module_path("") == []

    def test_whitespace_only_returns_empty(self):
        """纯空白字符串应返回空列表。"""
        lookup = CapabilityLookup()
        assert lookup.find_files_by_module_path("   ") == []

    def test_strips_whitespace(self):
        """前后空白应被 strip。"""
        lookup = CapabilityLookup()
        results = lookup.find_files_by_module_path("  zephyr.governance.capability_lookup  ")
        assert len(results) > 0, "strip 后的 module_path 应能匹配"


# ---------------------------------------------------------------------------
# 测试组 2：scaffold 维度3 阻断
# ---------------------------------------------------------------------------

class TestScaffoldSSoTGate:
    """测试 scaffold._check_duplicate_functionality 维度3 阻断。"""

    def test_block_on_conflicting_module_path(self, skip_dim1_dim2):
        """维度3：已有 module_path 应被阻断。"""
        with pytest.raises(ScaffoldError, match="module_path 冲突"):
            _check_duplicate_functionality(
                name="capability_lookup",
                description="测试探针",
                expected_module_path="zephyr.governance.capability_lookup",
            )

    def test_allow_on_new_module_path(self, skip_dim1_dim2):
        """维度3：新 module_path 应放行（不抛异常）。"""
        _check_duplicate_functionality(
            name="test_ssot_probe_xyz_999",
            description="测试探针",
            expected_module_path="zephyr.governance.test_ssot_probe_xyz_999",
        )

    def test_no_expected_module_path_skips_dim3(self, skip_dim1_dim2):
        """未传 expected_module_path 时维度3不执行（向后兼容）。"""
        # 不传 expected_module_path，不应因维度3抛异常
        _check_duplicate_functionality(
            name="test_ssot_probe_xyz_999",
            description="测试探针",
        )


# ---------------------------------------------------------------------------
# 测试组 3：强不变量——force_override 不跳过维度3
# ---------------------------------------------------------------------------

class TestForceOverrideInvariant:
    """强不变量：force_override 不跳过维度3。

    设计理由：同 module_path = 同文件身份 = 确凿重复信号。
    force_override 只跳过维度2（蓝图关键词匹配的软判断），
    不跳过维度3（module_path 精确匹配的硬判断）。
    """

    def test_force_override_does_not_skip_dim3(self, skip_dim1_dim2):
        """force_override=True 时维度3仍应阻断。"""
        with pytest.raises(ScaffoldError, match="module_path 冲突"):
            _check_duplicate_functionality(
                name="capability_lookup",
                description="测试探针",
                force_override=True,
                expected_module_path="zephyr.governance.capability_lookup",
            )


# ---------------------------------------------------------------------------
# 测试组 4：红蓝变异测试（falsifiability）
# ---------------------------------------------------------------------------

class TestMutationFalsifiability:
    """红蓝变异测试：验证门禁确实在起作用（falsifiability）。

    原理：如果门禁是有效的，注入失效后阻断应消失；还原后阻断应恢复。
    这证明门禁逻辑确实依赖 find_files_by_module_path 的返回值，
    而不是碰巧在别处阻断了。
    """

    def test_mutation_inject_empty_disables_gate(self, skip_dim1_dim2):
        """变异1：注入 find_files_by_module_path 返回空列表 → 阻断应消失。

        证明维度3确实依赖 find_files_by_module_path 的返回值。
        如果阻断仍在，说明门禁逻辑有误（可能在别处阻断）。
        """
        with patch.object(
            CapabilityLookup,
            "find_files_by_module_path",
            return_value=[],
        ):
            # 注入失效后，维度3应放行（不抛 ScaffoldError）
            _check_duplicate_functionality(
                name="capability_lookup",
                description="测试探针",
                expected_module_path="zephyr.governance.capability_lookup",
            )
            # 到这里没抛异常 = 变异生效，门禁被绕过 ✓

    def test_mutation_restore_re_enables_gate(self, skip_dim1_dim2):
        """变异2：还原后阻断应恢复。

        证明门禁逻辑是可恢复的，不是永久失效。
        """
        with pytest.raises(ScaffoldError, match="module_path 冲突"):
            _check_duplicate_functionality(
                name="capability_lookup",
                description="测试探针",
                expected_module_path="zephyr.governance.capability_lookup",
            )

    def test_mutation_inject_fake_conflict_triggers_gate(self, skip_dim1_dim2):
        """变异3：注入假冲突 → 阻断应触发。

        证明维度3确实在检查返回值是否非空，且会列出冲突文件。
        """
        fake_conflicts = ["src/zephyr/fake/conflict.py"]
        with patch.object(
            CapabilityLookup,
            "find_files_by_module_path",
            return_value=fake_conflicts,
        ):
            with pytest.raises(ScaffoldError, match="module_path 冲突") as exc_info:
                _check_duplicate_functionality(
                    name="anything",
                    description="测试探针",
                    expected_module_path="zephyr.totally.new.module",
                )
            # 验证错误消息包含了假冲突文件路径
            assert "src/zephyr/fake/conflict.py" in str(exc_info.value)


# ---------------------------------------------------------------------------
# 测试组 5：GitCommitGateway L2 兜底门禁
# ---------------------------------------------------------------------------

class TestGitCommitGatewaySSoT:
    """测试 GitCommitGateway._check_ssot_canonical L2 兜底门禁。

    L2 是 L1（scaffold）的兜底——防止 AI 绕过 scaffold 直接 Write 新文件后 commit。
    通过 mock _is_git_tracked / _parse_header / find_files_by_module_path 隔离测试，
    避免真实创建文件污染仓库。

    GitCommitGateway 实例化需要 git 仓库 + SessionRegistry。
    用真实 _PROJECT_ROOT（git 仓库）+ MagicMock registry 避免副作用。
    """

    @pytest.fixture
    def gateway(self):
        """构造 GitCommitGateway 实例（真实项目根 + mock registry）。"""
        # registry 被 mock 掉——_check_ssot_canonical 不使用 registry
        return GitCommitGateway(project_root=_PROJECT_ROOT, registry=MagicMock())

    def _fake_new_py_abs(self, rel: str) -> str:
        """构造 src/zephyr/ 下的虚假新文件绝对路径。"""
        return str(_PROJECT_ROOT / rel).replace("\\", "/")

    def test_block_on_new_py_with_existing_module_path(self, gateway, monkeypatch):
        """L2-1：新增 .py 声明已有 module_path → 阻断。

        场景：AI 绕过 scaffold 直接 Write 一个新文件，
        文件头声明了 zephyr.governance.git_commit_gateway（已有 module_path）。
        """
        fake_new_rel = "src/zephyr/governance/fake_new_ssot_xyz.py"
        fake_new_abs = self._fake_new_py_abs(fake_new_rel)

        # mock _is_git_tracked 让 fake_new 被判为"未跟踪"（即新增）
        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        # mock _parse_header 返回声明已有 module_path 的 header
        existing_mp = "zephyr.governance.git_commit_gateway"
        fake_header = HeaderInfo(path=fake_new_rel, module_path=existing_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        # mock find_files_by_module_path 返回已有文件冲突
        # （_disk_headers 被 mock 的 _parse_header 污染，故需控制 find 返回值；
        #  find 的正确性在 L1 测试组 TestFindFilesByModulePath 已覆盖）
        existing_conflict = "src/zephyr/governance/git_commit_gateway.py"
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: [existing_conflict] if mp == existing_mp else [],
        )

        passed, detail = gateway._check_ssot_canonical([fake_new_abs])
        assert not passed, "声明已有 module_path 的新文件应被阻断"
        assert "SSoT" in detail
        assert existing_mp in detail
        # 验证冲突文件路径出现在 detail 中
        assert "git_commit_gateway.py" in detail

    def test_allow_on_new_py_with_new_module_path(self, gateway, monkeypatch):
        """L2-2：新增 .py 声明全新 module_path → 放行。"""
        fake_new_rel = "src/zephyr/governance/fake_new_module_xyz_999.py"
        fake_new_abs = self._fake_new_py_abs(fake_new_rel)

        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        new_mp = "zephyr.governance.fake_new_module_xyz_999"
        fake_header = HeaderInfo(path=fake_new_rel, module_path=new_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        # mock find_files_by_module_path 返回空（新 module_path 无冲突）
        # （_disk_headers 被 mock 的 _parse_header 污染，故需控制 find 返回值）
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: [],
        )

        passed, detail = gateway._check_ssot_canonical([fake_new_abs])
        assert passed, "声明全新 module_path 的新文件应放行"
        assert "passed" in detail

    def test_allow_on_tracked_py_modification(self, gateway, monkeypatch):
        """L2-3：已跟踪文件修改 → 放行（不视为新增）。

        场景：AI 修改已有文件（非新增），门禁不应阻断。
        不 mock _is_git_tracked——让真实 git 判断该文件已跟踪。
        """
        tracked_rel = "src/zephyr/governance/capability_lookup.py"
        tracked_abs = self._fake_new_py_abs(tracked_rel)

        # 不 mock _is_git_tracked——真实 git ls-files 会返回 True（已跟踪）
        # 该文件不会进入 new_py_files → 放行
        passed, detail = gateway._check_ssot_canonical([tracked_abs])
        assert passed, "已跟踪文件修改应放行"
        assert "no new" in detail.lower()

    def test_allow_on_py_without_module_header(self, gateway, monkeypatch):
        """L2-4：无 [MODULE] 头的新文件 → 放行（无法判断）。"""
        fake_new_rel = "src/zephyr/governance/fake_no_header_xyz.py"
        fake_new_abs = self._fake_new_py_abs(fake_new_rel)

        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        # mock _parse_header 返回空 module_path（无 [MODULE] 头）
        fake_header = HeaderInfo(path=fake_new_rel, module_path="")
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )

        passed, detail = gateway._check_ssot_canonical([fake_new_abs])
        assert passed, "无 [MODULE] 头的新文件应放行（无法判断）"
        assert "passed" in detail

    def test_fail_open_when_capability_lookup_unavailable(self, gateway, monkeypatch):
        """L2-5：capability_lookup 不可用 → fail-open 放行。

        fail-open 策略：L1 scaffold 是主防线，L2 是兜底。
        capability_lookup 不可用时不阻断（避免破坏 commit 流程）。
        """
        fake_new_rel = "src/zephyr/governance/fake_import_fail_xyz.py"
        fake_new_abs = self._fake_new_py_abs(fake_new_rel)

        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        # 让 from zephyr.governance.capability_lookup import CapabilityLookup 失败
        # 通过 sys.modules 注入 None，import 会抛 ImportError
        original = sys.modules.get("zephyr.governance.capability_lookup")
        monkeypatch.setitem(sys.modules, "zephyr.governance.capability_lookup", None)

        try:
            passed, detail = gateway._check_ssot_canonical([fake_new_abs])
            assert passed, "capability_lookup 不可用时应 fail-open 放行"
            assert "不可用" in detail or "capability_lookup" in detail.lower()
        finally:
            # 恢复 sys.modules（patch fixture 自动恢复，但显式确保）
            if original is not None:
                sys.modules["zephyr.governance.capability_lookup"] = original

    def test_non_src_zephyr_py_skipped(self, gateway, monkeypatch):
        """L2-6：非 src/zephyr/ 下的 .py → 跳过（不在检查范围）。"""
        # scripts/ 下的 .py 不在检查范围
        non_src_abs = str(_PROJECT_ROOT / "scripts/fake_outside_xyz.py").replace("\\", "/")

        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        passed, detail = gateway._check_ssot_canonical([non_src_abs])
        assert passed, "非 src/zephyr/ 下的 .py 应跳过"
        assert "no new" in detail.lower()

    def test_non_py_files_skipped(self, gateway, monkeypatch):
        """L2-7：非 .py 文件 → 跳过（只检查 .py）。"""
        md_abs = str(_PROJECT_ROOT / "src/zephyr/fake_doc.md").replace("\\", "/")

        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        passed, detail = gateway._check_ssot_canonical([md_abs])
        assert passed, "非 .py 文件应跳过"
        assert "no new" in detail.lower()

    def test_empty_file_list_passes(self, gateway):
        """L2-8：空文件列表 → 放行。"""
        passed, detail = gateway._check_ssot_canonical([])
        assert passed
        assert "no new" in detail.lower()


# ---------------------------------------------------------------------------
# 测试组 6：L2 红蓝变异测试
# ---------------------------------------------------------------------------

class TestL2MutationFalsifiability:
    """L2 红蓝变异测试：验证 _check_ssot_canonical 确实在起作用。"""

    @pytest.fixture
    def gateway(self):
        return GitCommitGateway(project_root=_PROJECT_ROOT, registry=MagicMock())

    def test_l2_mutation_inject_empty_disables_gate(self, gateway, monkeypatch):
        """L2 变异1：注入 find_files_by_module_path 返回空 → 阻断消失。

        证明 L2 门禁确实依赖 find_files_by_module_path 的返回值。
        """
        fake_new_rel = "src/zephyr/governance/fake_mutation_xyz.py"
        fake_new_abs = str(_PROJECT_ROOT / fake_new_rel).replace("\\", "/")

        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        existing_mp = "zephyr.governance.git_commit_gateway"
        fake_header = HeaderInfo(path=fake_new_rel, module_path=existing_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        # 注入 find_files_by_module_path 返回空（变异：门禁失效）
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: [],
        )

        passed, detail = gateway._check_ssot_canonical([fake_new_abs])
        assert passed, "变异注入空列表后，门禁应失效（放行）——证明门禁依赖返回值"

    def test_l2_mutation_restore_re_enables_gate(self, gateway, monkeypatch):
        """L2 变异2：还原后阻断应恢复。

        不注入变异，让 find_files_by_module_path 真实运行。
        """
        fake_new_rel = "src/zephyr/governance/fake_restore_xyz.py"
        fake_new_abs = str(_PROJECT_ROOT / fake_new_rel).replace("\\", "/")

        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        existing_mp = "zephyr.governance.git_commit_gateway"
        fake_header = HeaderInfo(path=fake_new_rel, module_path=existing_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        # 不注入 find_files_by_module_path——真实运行，返回已有文件

        passed, detail = gateway._check_ssot_canonical([fake_new_abs])
        assert not passed, "还原后门禁应恢复阻断"
        assert "SSoT" in detail

    def test_l2_mutation_inject_fake_conflict_triggers_gate(self, gateway, monkeypatch):
        """L2 变异3：注入假冲突 → 阻断应触发。

        证明 L2 门禁确实在检查返回值是否非空，且会列出冲突文件。
        """
        fake_new_rel = "src/zephyr/governance/fake_inject_xyz.py"
        fake_new_abs = str(_PROJECT_ROOT / fake_new_rel).replace("\\", "/")

        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        new_mp = "zephyr.totally.new.module_xyz_999"
        fake_header = HeaderInfo(path=fake_new_rel, module_path=new_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        # 注入假冲突
        fake_conflicts = ["src/zephyr/fake/injected_conflict.py"]
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: fake_conflicts,
        )

        passed, detail = gateway._check_ssot_canonical([fake_new_abs])
        assert not passed, "注入假冲突后应阻断"
        assert "injected_conflict.py" in detail
