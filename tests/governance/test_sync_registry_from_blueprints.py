# [BLUEPRINT] MOD-INF-005 | docs/03_modules/_domain_governance/governance_automation/blueprint.md | §
# [TTL] permanent
# [MODULE] tests.governance.test_sync_registry_from_blueprints
# [DOMAIN] D_AUDITTEST
# [DEPENDENCIES] scripts.governance.d5_architecture.syncers.sync_registry_from_blueprints
# [CONSUMERS] pytest
# [STARTUP] manual
# [MATURITY] volatile
# [INVARIANTS] 测试目录隔离：monkeypatch BLUEPRINTS_DIR/BLUEPRINT_REGISTRY_PATH 到 tmp_path，禁写真实 docs/03_modules
# [MODIFY-GUARD]
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""tests for sync_registry_from_blueprints.py — registry 派生件自举（bootstrap）回归锚。

钉住 2026-09-16 治本：registry 被裁定转 gitignore 派生件后，"文件不存在"是干净 worktree
的常态；旧实现此时 exit(ERROR) 造成自举死锁（唯一能重生的工具拒绝无文件运行），
连带 check_blueprint_code_alignment 的 registry 维度静默空转。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_GOVERNANCE_DIR = _REPO_ROOT / "scripts" / "governance"
_SYNCER_DIR = _GOVERNANCE_DIR / "d5_architecture" / "syncers"
for _p in (str(_GOVERNANCE_DIR), str(_SYNCER_DIR), str(_REPO_ROOT)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import sync_registry_from_blueprints as srb  # noqa: E402


def _write_blueprint(root: Path, module_id: str, *, title: str = "t") -> Path:
    """造一份最小合法蓝图（frontmatter 含 module_id 才会入册）。"""
    bp = root / f"_domain_demo/{module_id.lower()}/blueprint.md"
    bp.parent.mkdir(parents=True, exist_ok=True)
    bp.write_text(
        "---\n"
        f"module_id: {module_id}\n"
        f"title: {title}\n"
        "version: '1.0'\n"
        "status: active\n"
        "date: '2026-09-16'\n"
        "layer: L2_domain\n"
        "---\n\n# body\n",
        encoding="utf-8",
    )
    return bp


@pytest.fixture
def isolated(tmp_path, monkeypatch):
    """把扫描根与产物路径全钉到 tmp_path（宪法 §9.6 测试禁写生产路径）。"""
    blueprints_dir = tmp_path / "docs" / "03_modules"
    blueprints_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(srb, "BLUEPRINTS_DIR", blueprints_dir)
    monkeypatch.setattr(srb, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(srb, "BLUEPRINT_REGISTRY_PATH", blueprints_dir / "blueprint_registry.yaml")
    return tmp_path


class TestRegistryBootstrap:
    def test_missing_registry_returns_empty_dict_not_none(self, isolated, capsys):
        """缺失 → {} 且出声 BOOTSTRAP（返回 None 会让 main() 硬退出=死锁回归）。"""
        assert srb.load_registry() == {}
        assert "BOOTSTRAP" in capsys.readouterr().out

    def test_non_mapping_payload_degrades_to_empty(self, isolated):
        """旧文件内容是列表/标量时不炸（派生件可全量重建，坏内容等同缺席）。"""
        srb.BLUEPRINT_REGISTRY_PATH.write_text("- not: a mapping\n", encoding="utf-8")
        assert srb.load_registry() == {}

    def test_main_writes_registry_from_zero(self, isolated, monkeypatch):
        """端到端：无 registry 文件 + --write → 从磁盘 frontmatter 全量重建落盘。"""
        _write_blueprint(isolated / "docs" / "03_modules", "MOD-DEMO-001")
        _write_blueprint(isolated / "docs" / "03_modules", "MOD-DEMO-002", title="second")
        assert not srb.BLUEPRINT_REGISTRY_PATH.exists()
        monkeypatch.setattr(sys, "argv", ["sync_registry_from_blueprints.py", "--write", "--no-changelog"])
        with pytest.raises(SystemExit) as exc:
            srb.main()
        assert exc.value.code == 0
        text = srb.BLUEPRINT_REGISTRY_PATH.read_text(encoding="utf-8")
        assert "MOD-DEMO-001" in text and "MOD-DEMO-002" in text
        assert "total_blueprints: 2" in text

    def test_dry_run_tolerates_missing_registry(self, isolated, monkeypatch):
        """dry-run 同样不得因缺文件走 ERROR 路径（缺文件=全新增，退出码是 FINDINGS 不是 ERROR）。"""
        _write_blueprint(isolated / "docs" / "03_modules", "MOD-DEMO-003")
        monkeypatch.setattr(sys, "argv", ["sync_registry_from_blueprints.py"])
        with pytest.raises(SystemExit) as exc:
            srb.main()
        assert exc.value.code == srb.EXIT_FINDINGS  # 有 diff 待写=正常告警，非旧 ERROR 硬失败
