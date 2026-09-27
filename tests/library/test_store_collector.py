# [A_test] module_id: MOD-LIB-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-LIB-004 | docs/03_modules/_domain_library/blueprint.md | §4
# [MODULE] tests.library.test_store_collector
# [DOMAIN] D_GOVERNANCE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [A_module] module_id=MOD-LIB-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""test_store_collector.py — 冷储/备份基建采集器（第 7 路）四态单测

权威依据：src/zephyr/library/collectors/store_collector.py（collect）

测试组（交办清单四判据）：
- ① kind 恰为 {backup, infra} 且非空（馆入馆谓词由此不再恒空）+ 索书号唯一不塌缩
- ② 每条带真源指针（真源相对路径#条目号，可 grep 到 file:line）
- ③ 路径不存在不得静默丢 → 产出"在册但盘上无=幽灵登记"可判定态（含部分缺失、无盘位两项）
- ④ F/G 盘不可达（拔盘态）不得抛穿、不得判幽灵，必带显式 degraded 标记
- 附：真源三册缺档 fail-soft；第 7 路已在 collectors 注册；代码零盘符常量

测试隔离：tmp_path 造临时仓 + 假盘根 Z:（monkeypatch _drive_root），零真实 F:/G: 依赖。
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from zephyr.library.collectors import store_collector  # noqa: E402
from zephyr.library.collectors.store_collector import (  # noqa: E402
    ASSET_INVENTORY_REL,
    BACKUP_CONFIG_REL,
    INFRA_REGISTRY_REL,
)

# 假盘符：测试里唯一"可达盘"，其盘根被 monkeypatch 到 tmp_path/volume
_FAKE_DRIVE = "Z:"

_INFRA_YAML = """\
infrastructure:
  - infra_id: "INFRA-STORE-001"
    name: "planned-object-storage"
    type: object_storage
    host: null
    status: planned
    description: "规划项：在册但尚无物理盘位"
  - infra_id: "INFRA-STORE-002"
    name: "zephyr-cold-archive-parquet"
    type: object_storage
    host: "Z:/cold/here + Z:/cold/gone"
    status: connected
    description: "冷归档两盘位（一在一不在）"
  - infra_id: "INFRA-STORE-900"
    name: "future-store-entry"
    type: object_storage
    host: "Z:/backup/vault"
    status: connected
    description: "未来新增存储族条目应被同一规则自动纳入"
  - infra_id: "INFRA-CFG-001"
    name: "not-storage"
    type: config_center
    host: "Z:/cold/gone"
    status: connected
    description: "非存储族：不属本采集器纳入面"
"""

_INVENTORY_YAML = """\
offrepo_assets:
  - id: OFFREPO-HERE
    path: "Z:\\\\cold\\\\here"
    type: cold_archive
    backup: mirror
    notes: "有镜像备份的仓外资产"
  - id: OFFREPO-GONE
    path: "Z:\\\\cold\\\\gone"
    type: raw_corpus
    backup: none
    notes: "无备份覆盖的仓外资产（在册盘上无）"
  - id: OFFREPO-PLACEHOLDER
    path: "Z:\\\\cold\\\\{drive letter TBD}"
    type: app_data
    backup: mirror
    notes: "占位串不是可定位盘位"
"""

_BACKUP_YAML = """\
version: "fixture-1.0.0"
code_backup:
  source: "Z:\\\\repo"
  target: "Z:\\\\backup\\\\code"
vault:
  base: "Z:\\\\backup\\\\vault"
g_mirror:
  base: "Z:\\\\backup"
  targets:
    - id: cold
      source: "Z:\\\\cold"
      target: "Z:\\\\backup\\\\mirror\\\\cold"
trigger:
  state_file: "Z:\\\\nope\\\\state.json"
"""


def _write_repo(tmp_path: Path) -> Path:
    """造临时仓（三本真源齐备）+ 假盘 Z: 上只挂 Z:/cold/here 与 Z:/backup/vault。"""
    repo = tmp_path / "repo"
    for rel, body in (
        (INFRA_REGISTRY_REL, _INFRA_YAML),
        (ASSET_INVENTORY_REL, _INVENTORY_YAML),
        (BACKUP_CONFIG_REL, _BACKUP_YAML),
    ):
        target = repo / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
    volume = tmp_path / "volume"
    (volume / "backup" / "vault").mkdir(parents=True, exist_ok=True)
    (volume / "cold" / "here").mkdir(parents=True, exist_ok=True)
    return repo


@pytest.fixture
def fake_drive(monkeypatch: pytest.MonkeyPatch):
    """把盘根探测缝改成"只有 Z: 挂着、F:/G: 等一律不可达"。

    真实仓的 F:/G: 在册盘位因此永不被 stat——拔盘/插盘两种本机状态测试结果一致。
    """
    roots: dict[str, Path] = {}

    def _probe(drive: str) -> Path | None:
        return roots.get(drive)

    monkeypatch.setattr(store_collector, "_drive_root", _probe)
    return roots


@pytest.fixture
def collected(tmp_path: Path, fake_drive):  # noqa: ANN001, ANN201
    repo = _write_repo(tmp_path)
    fake_drive[_FAKE_DRIVE] = tmp_path / "volume"
    return store_collector.collect(str(repo))


def _by_id(assets: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {a["asset_id"]: a for a in assets}


def _aux(asset: dict[str, Any]) -> dict[str, Any]:
    return asset["fingerprint_aux"]


class TestKindSet:
    """判据①：kind 恰为 {backup, infra} 且非空。"""

    def test_fixture_kinds_exactly_backup_and_infra(self, collected):
        assert not [a for a in collected if "error" in a]
        kinds = {a["kind"] for a in collected}
        assert kinds == {"backup", "infra"}
        for kind in ("backup", "infra"):
            assert [a for a in collected if a["kind"] == kind], kind

    def test_asset_id_prefix_matches_kind_and_is_unique(self, collected):
        ids = [a["asset_id"] for a in collected]
        assert len(ids) == len(set(ids)), "同一 home 塌缩=条目锚定失效"
        for asset in collected:
            prefix = "BAK" if asset["kind"] == "backup" else "INF"
            assert asset["asset_id"].startswith(f"{prefix}:")

    def test_only_storage_family_and_declared_positions_included(self, collected):
        ids = set(_by_id(collected))
        assert f"INF:{INFRA_REGISTRY_REL}#INFRA-STORE-900" in ids
        assert f"INF:{INFRA_REGISTRY_REL}#INFRA-CFG-001" not in ids
        assert f"BAK:{BACKUP_CONFIG_REL}#trigger.state_file" not in ids
        assert f"BAK:{BACKUP_CONFIG_REL}#code_backup.source" not in ids

    def test_real_repo_sources_produce_both_kinds(self, fake_drive):
        """真仓三真源读数（只读；所有盘被 monkeypatch 成不可达⇒零真实 F:/G: stat）。"""
        assets = store_collector.collect(str(_PROJECT_ROOT))
        assert not [a for a in assets if "error" in a]
        kinds = {a["kind"] for a in assets}
        assert kinds == {"backup", "infra"}
        assert {f"INF:{INFRA_REGISTRY_REL}#INFRA-STORE-003"} <= set(_by_id(assets))


class TestSourcePointer:
    """判据②：每条带可 grep 的真源指针。"""

    def test_home_is_register_entry_anchor(self, collected):
        for asset in collected:
            home = asset["home"]
            assert "#" in home, home
            source_rel, anchor = home.rsplit("#", 1)
            assert anchor
            assert _aux(asset)["source_anchor"] == anchor
            assert _aux(asset)["source_file"] == source_rel

    def test_source_line_resolves_to_the_declaring_line(self, tmp_path: Path, fake_drive):
        repo = _write_repo(tmp_path)
        fake_drive[_FAKE_DRIVE] = tmp_path / "volume"
        for asset in store_collector.collect(str(repo)):
            aux = _aux(asset)
            line_no = aux["source_line"]
            assert line_no, f"真源指针未定位到行：{asset['asset_id']}"
            assert aux["source_ref"] == f"{aux['source_file']}:{line_no}"
            text = (repo / aux["source_file"]).read_text(encoding="utf-8").splitlines()[line_no - 1]
            leaf = aux["source_anchor"].rsplit(".", 1)[-1]
            assert leaf in text, f"{asset['asset_id']} 指针指错行：{text}"

    def test_real_repo_pointers_are_greppable(self, fake_drive):
        assets = store_collector.collect(str(_PROJECT_ROOT))
        for asset in assets:
            aux = _aux(asset)
            path = _PROJECT_ROOT / aux["source_file"]
            assert path.exists(), asset["asset_id"]
            line = path.read_text(encoding="utf-8").splitlines()[aux["source_line"] - 1] if aux["source_line"] else ""
            assert aux["source_anchor"].rsplit(".", 1)[-1] in line, asset["asset_id"]


class TestGhostRegistration:
    """判据③：在册但盘上无=幽灵登记，不得静默丢。"""

    def test_missing_path_yields_determinable_ghost(self, collected):
        by_id = _by_id(collected)
        ghost = by_id[f"INF:{ASSET_INVENTORY_REL}#OFFREPO-GONE"]
        assert ghost["status"] == "ghost"
        assert _aux(ghost)["obs_state"] == "ghost_registered"
        assert _aux(ghost)["degraded"] is True
        assert _aux(ghost)["missing_locations"] == ["Z:/cold/gone"]
        assert "幽灵登记" in ghost["tags"]
        assert "ghost_registered" in ghost["ai_contract"]
        assert "Z:/cold/gone" in ghost["ai_contract"]

    def test_ghost_backup_position_present(self, collected):
        by_id = _by_id(collected)
        asset = by_id[f"BAK:{BACKUP_CONFIG_REL}#code_backup.target"]
        assert _aux(asset)["obs_state"] == "ghost_registered"
        assert _aux(asset)["physical_locations"] == ["Z:/backup/code"]

    def test_partial_missing_never_silently_dropped(self, collected):
        asset = _by_id(collected)[f"INF:{INFRA_REGISTRY_REL}#INFRA-STORE-002"]
        aux = _aux(asset)
        assert aux["obs_state"] == "present"
        assert aux["missing_locations"] == ["Z:/cold/gone"]
        assert aux["degraded"] is False
        assert aux["raw_locations"] == "Z:/cold/here + Z:/cold/gone"

    def test_no_physical_location_is_its_own_state(self, collected):
        by_id = _by_id(collected)
        planned = by_id[f"INF:{INFRA_REGISTRY_REL}#INFRA-STORE-001"]
        placeholder = by_id[f"BAK:{ASSET_INVENTORY_REL}#OFFREPO-PLACEHOLDER"]
        for asset in (planned, placeholder):
            assert _aux(asset)["obs_state"] == "no_physical_location"
            assert asset["status"] == "active"
            assert _aux(asset)["degraded"] is False
        assert placeholder["fingerprint_aux"]["raw_locations"].startswith("Z:\\cold\\{")

    def test_ghost_states_survive_on_real_repo(self, fake_drive):
        """本仓有盘上真源漂移前科：真册跑一遍必须能产出可判定的盘态（含幽灵/不可达）。"""
        assets = store_collector.collect(str(_PROJECT_ROOT))
        states = {_aux(a)["obs_state"] for a in assets}
        assert states <= {"present", "ghost_registered", "disk_unreachable", "no_physical_location"}
        assert "no_physical_location" in states  # INFRA-STORE-001 host: null


class TestUnpluggedDriveDegraded:
    """判据④：拔盘态不得抛穿、不得判幽灵，必带显式 degraded 标记。"""

    def test_unplugged_drive_does_not_raise_and_marks_degraded(self, tmp_path: Path, fake_drive):
        repo = _write_repo(tmp_path)  # 故意不注入 Z: 盘根=盘被拔掉
        assets = store_collector.collect(str(repo))
        assert assets and not [a for a in assets if "error" in a]
        for asset in assets:
            aux = _aux(asset)
            if asset["home"].endswith("#INFRA-STORE-001") or asset["home"].endswith("#OFFREPO-PLACEHOLDER"):
                assert aux["obs_state"] == "no_physical_location"
                continue
            assert aux["obs_state"] == "disk_unreachable", asset["asset_id"]
            assert aux["degraded"] is True
            assert asset["status"] == "blind"
            assert "盘不可达" in asset["tags"]
            assert aux["missing_locations"] == [], "拔盘≠幽灵：不可观测不得判缺失"
        assert {d for a in assets for d in _aux(a)["unreachable_drives"]} == {_FAKE_DRIVE}

    def test_real_repo_unplug_never_bubbles_up(self, fake_drive, monkeypatch: pytest.MonkeyPatch):
        """真册 + 全盘不可达：collect_all 侧不得见 error（图书馆不得因拔盘整体降级）。"""
        from zephyr.library.collectors import collect_all

        monkeypatch.setattr(store_collector, "_drive_root", lambda drive: None)
        collected = collect_all(["store"])
        assert "store" in collected
        assert not [a for a in collected["store"] if "error" in a]
        assert {a["kind"] for a in collected["store"]} == {"backup", "infra"}

    def test_missing_true_source_fails_soft(self, tmp_path: Path, fake_drive):
        assets = store_collector.collect(str(tmp_path))
        assert len(assets) == 1 and "error" in assets[0]


class TestNoHardcodedDrive:
    """盘符必须走 config 真源：模块级字符串常量里不得出现盘路径。"""

    def test_module_level_constants_carry_no_drive_letter(self):
        tree = ast.parse(Path(store_collector.__file__).read_text(encoding="utf-8"))
        strings: list[str] = []
        for node in tree.body:
            value = node.value if isinstance(node, (ast.Assign, ast.AnnAssign)) else None
            if value is None:
                continue
            strings += [
                const.value
                for const in ast.walk(value)
                if isinstance(const, ast.Constant) and isinstance(const.value, str)
            ]
        offenders = [text for text in strings if _has_drive(text)]
        assert not offenders, f"硬编码盘路径常量：{offenders}"
        assert strings, "常量面为空=探针失效"


def _has_drive(text: str) -> bool:
    """串里是否含 `<盘符>:` 形态的盘路径（真源派生的盘符不算——这里查的是代码常量）。"""
    return any(text[i].isalpha() and text[i + 1 : i + 3] == ":/" for i in range(len(text) - 3))


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))
