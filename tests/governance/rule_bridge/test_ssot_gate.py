# [A_test] module_id=MOD-GOV_ssot_gate_test | suite=ssot_gate | scope=unit | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

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
from zephyr.governance.capability_lookup import CapabilityLookup, HeaderInfo, SSoTConflict
from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import CommitStatus, GitCommitGateway


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
        文件头声明了 zephyr.gov_enforcement.rule_bridge.git_commit_gateway（已有 module_path）。
        """
        fake_new_rel = "src/zephyr/governance/fake_new_ssot_xyz.py"
        fake_new_abs = self._fake_new_py_abs(fake_new_rel)

        # mock _is_git_tracked 让 fake_new 被判为"未跟踪"（即新增）
        monkeypatch.setattr(GitCommitGateway, "_is_git_tracked", lambda self, rel: False)

        # mock _parse_header 返回声明已有 module_path 的 header
        existing_mp = "zephyr.gov_enforcement.rule_bridge.git_commit_gateway"
        fake_header = HeaderInfo(path=fake_new_rel, module_path=existing_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        # mock find_files_by_module_path 返回已有文件冲突
        # （_disk_headers 被 mock 的 _parse_header 污染，故需控制 find 返回值；
        #  find 的正确性在 L1 测试组 TestFindFilesByModulePath 已覆盖）
        existing_conflict = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
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
        # 验证阻断消息含"修复指令"（消息优化后明确指令化）
        assert "修复指令" in detail

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

        existing_mp = "zephyr.gov_enforcement.rule_bridge.git_commit_gateway"
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

        existing_mp = "zephyr.gov_enforcement.rule_bridge.git_commit_gateway"
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


# ---------------------------------------------------------------------------
# 测试组 7：共享检测函数 check_ssot_conflicts（L2/L3 唯一真源）
# ---------------------------------------------------------------------------

class TestCheckSsotConflicts:
    """测试 capability_lookup.check_ssot_conflicts 共享检测函数。

    这是 L2（GitCommitGateway）和 L3（pre-commit hook）检测逻辑的唯一真源。
    测试覆盖：空列表/无头/新module_path/已有module_path/排除自己/多文件混合。
    """

    def test_empty_list_returns_empty(self):
        """空列表 → 空冲突列表。"""
        lookup = CapabilityLookup()
        assert lookup.check_ssot_conflicts([]) == []

    def test_no_module_header_skipped(self, monkeypatch):
        """无 [MODULE] 头的文件 → 跳过（不报冲突）。"""
        lookup = CapabilityLookup()
        fake_header = HeaderInfo(path="src/zephyr/fake.py", module_path="")
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        result = lookup.check_ssot_conflicts([("/abs/fake.py", "src/zephyr/fake.py")])
        assert result == [], "无 [MODULE] 头应跳过"

    def test_new_module_path_no_conflict(self, monkeypatch):
        """新 module_path → 无冲突。"""
        lookup = CapabilityLookup()
        new_mp = "zephyr.totally.new.module_xyz_999"
        fake_header = HeaderInfo(path="src/zephyr/fake.py", module_path=new_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: [],
        )
        result = lookup.check_ssot_conflicts([("/abs/fake.py", "src/zephyr/fake.py")])
        assert result == [], "新 module_path 应无冲突"

    def test_existing_module_path_returns_conflict(self, monkeypatch):
        """已有 module_path → 返回冲突。"""
        lookup = CapabilityLookup()
        existing_mp = "zephyr.gov_enforcement.rule_bridge.git_commit_gateway"
        fake_header = HeaderInfo(path="src/zephyr/fake_new.py", module_path=existing_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        existing_file = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: [existing_file] if mp == existing_mp else [],
        )
        result = lookup.check_ssot_conflicts([("/abs/fake_new.py", "src/zephyr/fake_new.py")])
        assert len(result) == 1
        assert result[0].rel_path == "src/zephyr/fake_new.py"
        assert result[0].module_path == existing_mp
        assert existing_file in result[0].conflicts

    def test_excludes_self(self, monkeypatch):
        """新文件自己声明已有 module_path → 排除自己后无冲突。

        场景：新文件路径恰好与已有文件相同（理论上不会发生，但验证排除逻辑）。
        """
        lookup = CapabilityLookup()
        existing_mp = "zephyr.gov_enforcement.rule_bridge.git_commit_gateway"
        new_rel = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
        fake_header = HeaderInfo(path=new_rel, module_path=existing_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        # find 返回包含新文件自己的列表
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: [new_rel],
        )
        result = lookup.check_ssot_conflicts([("/abs/git_commit_gateway.py", new_rel)])
        assert result == [], "排除自己后应无冲突"

    def test_multiple_files_mixed(self, monkeypatch):
        """多文件混合：有的无头、有的新mp、有的冲突 → 正确分类。"""
        lookup = CapabilityLookup()
        existing_mp = "zephyr.gov_enforcement.rule_bridge.git_commit_gateway"
        new_mp = "zephyr.totally.new.xyz"

        # 三个文件：无头 / 新mp / 冲突mp
        headers = {
            "src/zephyr/no_header.py": HeaderInfo(path="src/zephyr/no_header.py", module_path=""),
            "src/zephyr/new_module.py": HeaderInfo(path="src/zephyr/new_module.py", module_path=new_mp),
            "src/zephyr/conflict.py": HeaderInfo(path="src/zephyr/conflict.py", module_path=existing_mp),
        }
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: headers.get(rel, HeaderInfo(path=rel))),
        )
        existing_file = "src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: [existing_file] if mp == existing_mp else [],
        )

        files = [
            ("/abs/no_header.py", "src/zephyr/no_header.py"),
            ("/abs/new_module.py", "src/zephyr/new_module.py"),
            ("/abs/conflict.py", "src/zephyr/conflict.py"),
        ]
        result = lookup.check_ssot_conflicts(files)
        assert len(result) == 1, "只有 conflict.py 应报冲突"
        assert result[0].rel_path == "src/zephyr/conflict.py"
        assert result[0].module_path == existing_mp
        assert existing_file in result[0].conflicts

    def test_returns_ssoTConflict_type(self, monkeypatch):
        """返回类型应为 SSoTConflict（验证 dataclass 结构）。"""
        lookup = CapabilityLookup()
        existing_mp = "zephyr.gov_enforcement.rule_bridge.git_commit_gateway"
        fake_header = HeaderInfo(path="src/zephyr/fake.py", module_path=existing_mp)
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: fake_header),
        )
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: ["src/zephyr/existing.py"],
        )
        result = lookup.check_ssot_conflicts([("/abs/fake.py", "src/zephyr/fake.py")])
        assert len(result) == 1
        assert isinstance(result[0], SSoTConflict)
        assert hasattr(result[0], "rel_path")
        assert hasattr(result[0], "module_path")
        assert hasattr(result[0], "conflicts")


# ---------------------------------------------------------------------------
# 测试组 8：红蓝极限对抗（模拟刚进项目的 AI）
# ---------------------------------------------------------------------------

class TestRedBlueExtreme:
    """红蓝极限对抗——模拟刚进项目的 AI 尝试绕过 SSoT 门禁。

    视角：AI 没有上下文，不知道门禁存在，尝试各种创建方式。
    验证三层防线（L1/L2/L3）的极限防御能力 + 已知限制边界。
    """

    @pytest.fixture
    def gateway(self):
        return GitCommitGateway(project_root=_PROJECT_ROOT, registry=MagicMock())

    def _mock_l3_git_diff(self, monkeypatch, new_files: list[str]):
        """mock check_ssot_gate 的 git diff 返回指定新文件列表。"""
        import scripts.governance.check_ssot_gate as gate_module
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "\n".join(new_files) + "\n" if new_files else ""
        mock_result.stderr = ""
        monkeypatch.setattr(gate_module.subprocess, "run", lambda *a, **kw: mock_result)
        return gate_module

    def _mock_capability_lookup(self, monkeypatch, headers: dict, conflicts: dict):
        """mock CapabilityLookup 避免 scan 磁盘 + 控制解析/反查。"""
        monkeypatch.setattr(CapabilityLookup, "_scan_disk_headers", lambda self: {})
        monkeypatch.setattr(
            CapabilityLookup, "_parse_header",
            staticmethod(lambda py, rel: headers.get(rel, HeaderInfo(path=rel))),
        )
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: conflicts.get(mp, []),
        )

    def _mock_path_exists(self, monkeypatch, fake_names: set[str]):
        """mock Path.exists 对指定文件名返回 True，其余用真实 exists。"""
        real_exists = Path.exists
        def mock_exists(self):
            if any(name in str(self) for name in fake_names):
                return True
            return real_exists(self)
        monkeypatch.setattr(Path, "exists", mock_exists)

    # ---- L3 pre-commit hook 直接测试 ----

    def test_red_l3_blocks_direct_git_commit(self, monkeypatch, capsys):
        """红方攻击1：绕过 Gateway 直接 git commit 重复文件 → L3 应拦截。

        场景：刚进项目的 AI 不知道 GitCommitGateway 铁律，直接 git commit。
        """
        gate_module = self._mock_l3_git_diff(monkeypatch, ["src/zephyr/governance/fake_red.py"])
        self._mock_path_exists(monkeypatch, {"fake_red"})
        self._mock_capability_lookup(
            monkeypatch,
            headers={"src/zephyr/governance/fake_red.py": HeaderInfo(
                path="src/zephyr/governance/fake_red.py",
                module_path="zephyr.gov_enforcement.rule_bridge.git_commit_gateway",
            )},
            conflicts={"zephyr.gov_enforcement.rule_bridge.git_commit_gateway": ["src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"]},
        )
        exit_code = gate_module.main()
        assert exit_code == 1, "L3 应阻断直接 git commit 的重复文件"
        captured = capsys.readouterr()
        assert "修复指令" in captured.err, "L3 消息应含'修复指令'"

    def test_red_l3_passes_no_new_py(self, monkeypatch):
        """红方攻击2：commit 无新 .py 文件 → L3 放行。"""
        gate_module = self._mock_l3_git_diff(monkeypatch, [])
        assert gate_module.main() == 0

    def test_red_l3_fail_open_on_lookup_error(self, monkeypatch):
        """红方攻击3：capability_lookup 不可用 → L3 fail-open 放行。

        fail-open 策略：L3 是双保险，capability_lookup 崩溃时不阻断 commit 流程。
        """
        gate_module = self._mock_l3_git_diff(monkeypatch, ["src/zephyr/governance/fake_err.py"])
        self._mock_path_exists(monkeypatch, {"fake_err"})
        def fake_init(self, *args, **kwargs):
            raise RuntimeError("mock init fail")
        monkeypatch.setattr(CapabilityLookup, "__init__", fake_init)
        assert gate_module.main() == 0, "L3 应 fail-open 放行"

    # ---- 已知限制验证 ----

    def test_red_same_batch_conflict_missed(self, monkeypatch):
        """红方攻击4：同批次两新文件声明相同新 module_path → 漏检（已知限制）。

        根因：check_ssot_conflicts 只反查磁盘已有文件，不检查 new_py_files 列表内部。
        L1 scaffold 单文件创建不会有此问题；只有绕过 scaffold 批量 commit 才触发。
        """
        lookup = CapabilityLookup()
        new_mp = "zephyr.brand_new.duplicate_xyz_999"
        headers = {
            "src/zephyr/fake_a.py": HeaderInfo(path="src/zephyr/fake_a.py", module_path=new_mp),
            "src/zephyr/fake_b.py": HeaderInfo(path="src/zephyr/fake_b.py", module_path=new_mp),
        }
        monkeypatch.setattr(CapabilityLookup, "_parse_header", staticmethod(lambda py, rel: headers.get(rel, HeaderInfo(path=rel))))
        monkeypatch.setattr(CapabilityLookup, "find_files_by_module_path", lambda self, mp: [])
        files = [("/abs/fake_a.py", "src/zephyr/fake_a.py"), ("/abs/fake_b.py", "src/zephyr/fake_b.py")]
        result = lookup.check_ssot_conflicts(files)
        assert result == [], "同批次新文件互相冲突 → 漏检（已知限制）"

    # ---- [MODULE] 头格式变异 ----

    def test_red_lowercase_module_header_ignored(self):
        """红方攻击5：[module] 小写 → 正则不匹配 → 跳过。

        正则 _RE_MODULE 大小写敏感。AI 写错大小写会被放行——
        但这也意味着文件不会被 scaffold 识别（无 module_path = 不存在）。
        """
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("# [module] zephyr.gov_enforcement.rule_bridge.git_commit_gateway\n")
            tmp = f.name
        try:
            header = CapabilityLookup._parse_header(Path(tmp), "fake.py")
            assert header.module_path == "", "小写 [module] 应不匹配"
        finally:
            os.unlink(tmp)

    def test_red_empty_module_header_skipped(self):
        """红方攻击6：`# [MODULE]` 无内容 → module_path 为空 → 跳过。"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("# [MODULE]\n")
            tmp = f.name
        try:
            header = CapabilityLookup._parse_header(Path(tmp), "fake.py")
            assert header.module_path == "", "空 [MODULE] 应解析为空"
        finally:
            os.unlink(tmp)

    def test_red_empty_file_skipped(self):
        """红方攻击7：空文件 → 无头 → 跳过。"""
        import tempfile, os
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as f:
            f.write("")
            tmp = f.name
        try:
            header = CapabilityLookup._parse_header(Path(tmp), "fake.py")
            assert header.module_path == "", "空文件应解析为空"
        finally:
            os.unlink(tmp)

    # ---- 大小写敏感 ----

    def test_red_module_path_case_sensitive(self, monkeypatch):
        """红方攻击8：module_path 大小写变异 → 不匹配（检测能力限制）。

        AI 声明 Zephyr.Governance.Git_Commit_Gateway（大写）→ 与已有
        zephyr.gov_enforcement.rule_bridge.git_commit_gateway（小写）不匹配 → 不报冲突。
        检测依赖 AI 正确声明 module_path——这是方案 E 的固有边界。
        """
        lookup = CapabilityLookup()
        wrong_case_mp = "Zephyr.Governance.Git_Commit_Gateway"
        headers = {"src/zephyr/fake_case.py": HeaderInfo(path="src/zephyr/fake_case.py", module_path=wrong_case_mp)}
        monkeypatch.setattr(CapabilityLookup, "_parse_header", staticmethod(lambda py, rel: headers.get(rel, HeaderInfo(path=rel))))
        monkeypatch.setattr(
            CapabilityLookup, "find_files_by_module_path",
            lambda self, mp: ["src/zephyr/gov_enforcement/rule_bridge/git_commit_gateway.py"] if mp == "zephyr.gov_enforcement.rule_bridge.git_commit_gateway" else [],
        )
        result = lookup.check_ssot_conflicts([("/abs/fake_case.py", "src/zephyr/fake_case.py")])
        assert result == [], "大小写不同的 module_path 应不匹配（检测能力限制）"
