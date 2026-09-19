# [BLUEPRINT] MOD-TEST-001 | tests/governance/rule_bridge/test_gate_auto_registrar.py | §
# [MODULE] tests.governance.rule_bridge.test_gate_auto_registrar
# [DOMAIN] D_GOV_ENFORCEMENT
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.gate_auto_registrar, zephyr.gov_enforcement.rule_bridge.commit_gate_registry
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 纯单元测试（tmp_path + monkeypatch，测试不写生产路径）；测试 fail-closed 行为（裁定#351）：装载失败/名册损坏/装载数≠名册数 → GateAutoRegistrationError；测试 enabled=false 跳过；测试幂等共存
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试永不抛未捕获异常
# [TESTS] self
# [A_module] module_id=MOD-TEST-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_gate_auto_registrar.py — gate_auto_registrar 单元测试（#ARCH-GATE-REGISTRY-AUTO-001 Phase 3）

测试覆盖（裁定#351 后 fail-closed 契约，2026-09-19）：
1. load_gate_entries：YAML 解析（正常/缺失=0 门容忍）；损坏（语法错/根非 dict/gates 非 list/非 dict 条目）→ 抛 GateAutoRegistrationError
2. auto_register_gates：动态 import + register（成功 / enabled=false 跳过 / 幂等共存 / 名册缺失容忍 / 名册在而空拒绝）
3. fail-closed 行为：import 失败/getattr 失败/缺字段 → 抛 GateAutoRegistrationError（报 gate_id+错误）
4. 装载数对账硬告警：条数↔total_gates 不一致 / 重复 gate_id / 声明未注册 → 抛错
5. 全链路：单门 import 被断 → GitCommitGateway() 构造失败（提交阻断）；全健康 → 构造放行
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import CommitGateRegistry, GateSpec
from zephyr.gov_enforcement.rule_bridge.gate_auto_registrar import (
    REGISTRY_REL_PATH,
    GateAutoRegistrationError,
    auto_register_gates,
    load_gate_entries,
)

# ========== load_gate_entries 测试 ==========


class TestLoadGateEntries:
    """load_gate_entries 函数测试（fail-closed 契约）。"""

    def test_load_valid_yaml(self, tmp_path: Path) -> None:
        """正常 YAML 可加载。"""
        registry_path = tmp_path / REGISTRY_REL_PATH
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(
            "gates:\n"
            "  - gate_id: TEST-GATE\n"
            "    module_path: zephyr.test\n"
            "    factory_function: make_test_gate\n"
            "    enabled: true\n",
            encoding="utf-8",
        )
        entries = load_gate_entries(tmp_path)
        assert len(entries) == 1
        assert entries[0]["gate_id"] == "TEST-GATE"

    def test_load_missing_file_returns_empty(self, tmp_path: Path) -> None:
        """名册文件缺失 → 空列表（0 门声明容忍：测试 harness/嵌入式合法用法，warn 留痕）。"""
        entries = load_gate_entries(tmp_path)
        assert entries == []

    def test_load_invalid_yaml_raises(self, tmp_path: Path) -> None:
        """YAML 语法错误 → fail-closed 抛错。"""
        registry_path = tmp_path / REGISTRY_REL_PATH
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text("invalid: yaml: content:\n  - [unclosed", encoding="utf-8")
        with pytest.raises(GateAutoRegistrationError, match="unreadable"):
            load_gate_entries(tmp_path)

    def test_load_non_dict_root_raises(self, tmp_path: Path) -> None:
        """YAML 根非 dict → fail-closed 抛错。"""
        registry_path = tmp_path / REGISTRY_REL_PATH
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text("- just\n- a\n- list\n", encoding="utf-8")
        with pytest.raises(GateAutoRegistrationError, match="root is not dict"):
            load_gate_entries(tmp_path)

    def test_load_gates_not_list_raises(self, tmp_path: Path) -> None:
        """gates 字段非 list → fail-closed 抛错。"""
        registry_path = tmp_path / REGISTRY_REL_PATH
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text("gates: not_a_list\n", encoding="utf-8")
        with pytest.raises(GateAutoRegistrationError, match="'gates' is not list"):
            load_gate_entries(tmp_path)

    def test_load_empty_gates_returns_empty(self, tmp_path: Path) -> None:
        """gates 为空列表返回空列表（装载层放行，注册层拒绝——见 auto_register 测试）。"""
        registry_path = tmp_path / REGISTRY_REL_PATH
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text("gates: []\n", encoding="utf-8")
        entries = load_gate_entries(tmp_path)
        assert entries == []

    def test_load_non_dict_entries_raises(self, tmp_path: Path) -> None:
        """非 dict 条目 → fail-closed 抛错（曾静默过滤=名册缩水无痕，裁定#351 收口）。"""
        registry_path = tmp_path / REGISTRY_REL_PATH
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(
            "gates:\n"
            "  - gate_id: VALID\n"
            "    module_path: zephyr.test\n"
            "    factory_function: make_test\n"
            '  - "not a dict"\n'
            "  - 42\n",
            encoding="utf-8",
        )
        with pytest.raises(GateAutoRegistrationError, match="non-dict entries"):
            load_gate_entries(tmp_path)


# ========== auto_register_gates 测试 ==========


class TestAutoRegisterGates:
    """auto_register_gates 函数测试。"""

    def _make_registry_yaml(self, tmp_path: Path, gates: list[dict], total_gates: int | None = None) -> Path:
        """创建测试用 YAML 文件。"""
        registry_path = tmp_path / REGISTRY_REL_PATH
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        lines = []
        if total_gates is not None:
            lines.append(f"total_gates: {total_gates}")
        lines.append("gates:")
        for g in gates:
            lines.append(f"  - gate_id: {g['gate_id']}")
            lines.append(f"    module_path: {g['module_path']}")
            lines.append(f"    factory_function: {g['factory_function']}")
            lines.append(f"    enabled: {g.get('enabled', True)}")
        registry_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return registry_path

    _HELD = {
        "module_path": "zephyr.gov_enforcement.commit_gates.held_overlap_gate",
        "factory_function": "make_held_overlap_gate",
    }

    def test_register_success(self, tmp_path: Path) -> None:
        """成功注册一个 gate（返回空列表=兼容旧签名；声明 gate_id 须与 factory 产出一致）。"""
        self._make_registry_yaml(tmp_path, [{"gate_id": "HELD-OVERLAP", **self._HELD, "enabled": True}])
        registry = CommitGateRegistry()
        failures = auto_register_gates(registry, tmp_path)
        assert failures == []
        assert registry.get("HELD-OVERLAP") is not None  # held_overlap_gate 的实际 gate_id

    def test_register_disabled_skipped(self, tmp_path: Path) -> None:
        """enabled=false 的 gate 被跳过（对账基数=enabled 集合，跳过不算缺失）。"""
        self._make_registry_yaml(tmp_path, [{"gate_id": "TEST-DISABLED", **self._HELD, "enabled": False}])
        registry = CommitGateRegistry()
        failures = auto_register_gates(registry, tmp_path)
        assert failures == []
        assert registry.get("HELD-OVERLAP") is None

    def test_register_import_failure_raises(self, tmp_path: Path) -> None:
        """import 失败 → fail-closed 抛 GateAutoRegistrationError（报 gate_id+错误，裁定#351）。"""
        self._make_registry_yaml(
            tmp_path,
            [
                {
                    "gate_id": "TEST-IMPORT-FAIL",
                    "module_path": "zephyr.nonexistent.module",
                    "factory_function": "make_nonexistent",
                    "enabled": True,
                }
            ],
        )
        registry = CommitGateRegistry()
        with pytest.raises(GateAutoRegistrationError) as ei:
            auto_register_gates(registry, tmp_path)
        msg = str(ei.value)
        assert "TEST-IMPORT-FAIL" in msg
        assert "import failed" in msg
        assert "1/1" in msg  # 失败数/名册数

    def test_register_factory_not_found_raises(self, tmp_path: Path) -> None:
        """工厂函数不存在 → fail-closed 抛错。"""
        self._make_registry_yaml(
            tmp_path,
            [
                {
                    "gate_id": "TEST-NO-FACTORY",
                    **self._HELD,
                    "factory_function": "make_nonexistent_function",
                    "enabled": True,
                }
            ],
        )
        registry = CommitGateRegistry()
        with pytest.raises(GateAutoRegistrationError) as ei:
            auto_register_gates(registry, tmp_path)
        msg = str(ei.value)
        assert "TEST-NO-FACTORY" in msg
        assert "factory function not found" in msg

    def test_register_missing_fields_raises(self, tmp_path: Path) -> None:
        """缺失必填字段 → fail-closed 抛错。"""
        self._make_registry_yaml(
            tmp_path,
            [
                {
                    "gate_id": "",
                    "module_path": "zephyr.test",
                    "factory_function": "make_test",
                    "enabled": True,
                }
            ],
        )
        registry = CommitGateRegistry()
        with pytest.raises(GateAutoRegistrationError, match="missing required field"):
            auto_register_gates(registry, tmp_path)

    def test_register_empty_yaml_raises(self, tmp_path: Path) -> None:
        """名册存在但空（0 条）→ fail-closed 抛错（名册在而空=疑似蒸发，最大危害面）。"""
        registry_path = tmp_path / REGISTRY_REL_PATH
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text("gates: []\n", encoding="utf-8")
        registry = CommitGateRegistry()
        with pytest.raises(GateAutoRegistrationError, match="present but empty"):
            auto_register_gates(registry, tmp_path)

    def test_register_missing_roster_returns_empty(self, tmp_path: Path) -> None:
        """名册文件缺失 → 0 门装载返回空列表（harness 容忍层；防蒸发归 REGISTRY-MASS-DELETION gate）。"""
        registry = CommitGateRegistry()
        assert auto_register_gates(registry, tmp_path) == []
        assert registry.list_gate_ids() == []

    def test_register_idempotent_coexistence(self, tmp_path: Path) -> None:
        """幂等共存：同 gate_id 二次装载走 register 幂等覆盖（同 gate_id 覆盖旧 spec），对账仍通过。"""
        self._make_registry_yaml(
            tmp_path,
            [{"gate_id": "HELD-OVERLAP", **self._HELD, "enabled": True}],
        )
        registry = CommitGateRegistry()
        assert auto_register_gates(registry, tmp_path) == []
        assert auto_register_gates(registry, tmp_path) == []  # 二次装载（幂等覆盖）
        assert registry.get("HELD-OVERLAP") is not None

    def test_register_partial_failure_raises_with_all_gate_ids(self, tmp_path: Path) -> None:
        """部分失败：3 门 1 成功 2 坏 → 抛错且逐台报 gate_id；成功门仍已注册（可定位）。"""
        self._make_registry_yaml(
            tmp_path,
            [
                {"gate_id": "TEST-OK", **self._HELD, "enabled": True},
                {
                    "gate_id": "TEST-IMPORT-FAIL",
                    "module_path": "zephyr.nonexistent",
                    "factory_function": "make_nonexistent",
                    "enabled": True,
                },
                {"gate_id": "TEST-NO-FACTORY", **self._HELD, "factory_function": "make_wrong_name", "enabled": True},
            ],
        )
        registry = CommitGateRegistry()
        with pytest.raises(GateAutoRegistrationError) as ei:
            auto_register_gates(registry, tmp_path)
        msg = str(ei.value)
        assert "TEST-IMPORT-FAIL" in msg and "TEST-NO-FACTORY" in msg
        assert "TEST-OK" not in msg.split("failed to load:")[1]  # 成功门不入失败清单
        # 成功的仍注册（抛错前已装载，便于排障定位）
        assert registry.get("HELD-OVERLAP") is not None

    # ── 装载数对账硬告警（裁定#351：装载数≠名册数）──

    def test_roster_count_mismatch_declared_raises(self, tmp_path: Path) -> None:
        """条数≠头部 total_gates 声明（模拟删条目未同步）→ 硬告警抛错。"""
        self._make_registry_yaml(
            tmp_path,
            [{"gate_id": "TEST-A", **self._HELD, "enabled": True}],
            total_gates=2,  # 声明 2 实际 1 条（= 名册被删一条未同步头部）
        )
        registry = CommitGateRegistry()
        with pytest.raises(GateAutoRegistrationError, match="装载数≠名册数"):
            auto_register_gates(registry, tmp_path)

    def test_duplicate_enabled_gate_id_raises(self, tmp_path: Path) -> None:
        """重复 enabled gate_id（register 幂等覆盖=静默缩装）→ 硬告警抛错。"""
        self._make_registry_yaml(
            tmp_path,
            [
                {"gate_id": "HELD-OVERLAP", **self._HELD, "enabled": True},
                {"gate_id": "HELD-OVERLAP", **self._HELD, "enabled": True},
            ],
        )
        registry = CommitGateRegistry()
        with pytest.raises(GateAutoRegistrationError, match="duplicate enabled gate_id"):
            auto_register_gates(registry, tmp_path)

    def test_declared_but_not_registered_raises(self, tmp_path: Path) -> None:
        """名册声明 gate_id 与 factory 实际返回不一致 → 声明未注册 → 硬告警抛错。"""
        self._make_registry_yaml(
            tmp_path,
            [{"gate_id": "TEST-ID-MISMATCH", **self._HELD, "enabled": True}],
        )
        registry = CommitGateRegistry()
        with pytest.raises(GateAutoRegistrationError, match="declared but not registered"):
            auto_register_gates(registry, tmp_path)


# ========== 全链路 fail-closed / 放行测试（GitCommitGateway 构造链）==========


class TestFailClosedCommitChain:
    """提交链路级红证：断一门 → 构造阻断；全健康 → 放行。"""

    def test_gateway_init_blocked_by_broken_gate(self) -> None:
        """任一 enabled gate import 被断 → GitCommitGateway.__init__ 抛错（提交阻断）且报 gate_id。

        注：置脏 sys.modules 用测试体内 try/finally 自恢复（先于一切 fixture teardown，
        兼容 #ARCH-107 探针的 teardown 时序），不用 monkeypatch。"""
        from zephyr.gov_enforcement.commit_gates import held_overlap_gate as victim
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway

        saved = sys.modules.get(victim.__name__, ...)
        sys.modules[victim.__name__] = None  # import 即 ImportError（import-halted 语义）
        try:
            with pytest.raises(GateAutoRegistrationError) as ei:
                GitCommitGateway()
        finally:
            if saved is ...:
                sys.modules.pop(victim.__name__, None)
            else:
                sys.modules[victim.__name__] = saved
        msg = str(ei.value)
        assert "HELD-OVERLAP" in msg
        assert "import failed" in msg

    def test_gateway_init_succeeds_when_all_healthy(self) -> None:
        """全部健康 → GitCommitGateway() 构造放行，装载 113 台与名册一致。"""
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
        from zephyr.shared.io.paths import REPO_ROOT

        gw = GitCommitGateway()
        raw = yaml.safe_load((Path(REPO_ROOT) / REGISTRY_REL_PATH).read_text(encoding="utf-8"))
        declared = raw["total_gates"]
        assert len(gw.gate_registry.specs) == declared


# ========== 真实项目集成测试（smoke test） ==========


class TestRealProjectIntegration:
    """真实项目集成测试——使用真实 in_process_gate_registry.yaml。"""

    def test_load_real_yaml_entries(self) -> None:
        """真实 YAML 可加载且条目数与头部 total_gates 声明一致（去硬编码治本）。

        演进史：2026-08-15：83→92；2026-08-16：92→93；2026-08-17：93→97；2026-08-21：97→98
        +GATE-ERRCODE-CONSISTENCY；2026-08-23：98→99 +HOT-FILE-BASE-FRESHNESS；2026-09-04：
        99→100 +FRONTEND-TRUTH-SOURCE；2026-09-04：100→101 +FRONTEND-MAP；2026-09-05：
        101→104 +DECISION-MAP+BUSINESS-REGISTRY+GATE-BATTLE-MAP-ALIGNMENT；2026-09-09：
        104→105 +REGISTRY-MASS-DELETION；2026-09-09：105→106 +ALGO-NOTE-SYNC（47ab163cbf）。

        治本（2026-09-10）：assert == <数字> 的硬编码在每次 registry 演进时必然滞后
        （105 断言 vs 106 实际，测试期望三批滞后补记的根因）——改为「实际条数 == 头部
        total_gates 声明」单锚双端校验：演进者加条目时必须同步 total_gates 字段，
        同步义务由本断言显式化。裁定#351（2026-09-19）：该对账义务下沉为装载器内建
        fail-closed 硬告警（auto_register_gates 装载数对账），本测试保留为静态锚。"""
        from zephyr.shared.io.paths import REPO_ROOT

        reg_path = Path(REPO_ROOT) / REGISTRY_REL_PATH
        raw = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
        declared = (raw or {}).get("total_gates")
        assert isinstance(declared, int), f"total_gates 字段缺失或非整数: {declared!r}"
        entries = load_gate_entries(Path(REPO_ROOT))
        assert len(entries) == declared, (
            f"registry 实际条数 {len(entries)} 与头部 total_gates 声明 {declared} 不一致——"
            "加条目时必须同步 total_gates 字段（同步义务）"
        )

    def test_real_yaml_all_enabled(self) -> None:
        """真实 YAML 所有 gate enabled=true。"""
        from zephyr.shared.io.paths import REPO_ROOT

        entries = load_gate_entries(Path(REPO_ROOT))
        for entry in entries:
            assert entry.get("enabled") is True, f"gate {entry.get('gate_id')} not enabled"

    def test_real_yaml_all_have_required_fields(self) -> None:
        """真实 YAML 所有条目有必填字段。"""
        from zephyr.shared.io.paths import REPO_ROOT

        entries = load_gate_entries(Path(REPO_ROOT))
        for entry in entries:
            assert entry.get("gate_id"), f"missing gate_id: {entry}"
            assert entry.get("module_path"), f"missing module_path: {entry}"
            assert entry.get("factory_function"), f"missing factory_function: {entry}"

    def test_auto_register_full_roster_fail_closed(self) -> None:
        """全量装载：任一台坏即抛 GateAutoRegistrationError（fail-closed），全好则装满名册。"""
        from zephyr.shared.io.paths import REPO_ROOT

        registry = CommitGateRegistry()
        failures = auto_register_gates(registry, Path(REPO_ROOT))  # 坏门在此抛错
        assert failures == []
        reg_path = Path(REPO_ROOT) / REGISTRY_REL_PATH
        declared = yaml.safe_load(reg_path.read_text(encoding="utf-8"))["total_gates"]
        assert len(registry.list_gate_ids()) == declared

    def test_auto_register_matches_explicit_register(self) -> None:
        """auto_register 注册的 gate 集合与显式注册一致。"""
        from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import GitCommitGateway
        from zephyr.shared.io.paths import REPO_ROOT

        # 显式注册（通过 GitCommitGateway 实例化——裁定#351 后构造即全量 fail-closed 装载）
        gw = GitCommitGateway()
        explicit_ids = set(gw.gate_registry.specs.keys())

        # auto_register
        auto_registry = CommitGateRegistry()
        failures = auto_register_gates(auto_registry, Path(REPO_ROOT))
        assert failures == []
        auto_ids = set(auto_registry.specs.keys())

        # auto_register 应是 explicit 的子集（explicit 可能含 reconciler 等非 gate）
        missing = auto_ids - explicit_ids
        assert not missing, f"auto_register has gates not in explicit: {missing}"
