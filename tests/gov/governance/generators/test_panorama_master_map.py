# [MODULE] tests.governance.generators.test_panorama_master_map
# [DOMAIN] D_GOV_SCRIPTS
# [TTL] permanent
# tests/ 豁免 CREATE-GUARD token（测试非能力真源）
"""全景总图（图之图）对抗测试——tmp 副本宇宙三红+绿基线。

三攻击（总包令 st-mastermap-20261004 任务3）：
  红1 新增图不入总图（§3 加行而 nodes 不加=E1 少节点）+ 反向（§3 删行=E1 多节点）
  红2 边指向不存在图（E3）
  红3 node 文件被删（E2）
绿基线：真源副本原样=五条全绿；附幂等（双跑逐字节等）与 fail-closed（master 缺失 exit 2）。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
import yaml

_REPO = (
    Path(__file__).resolve().parents[4]
)  # tests/gov/governance/generators/ 四层深（tests-reorg 2026-10-04 迁址适配）
_GENERATORS_DIR = _REPO / "scripts" / "governance" / "d5_architecture" / "generators"
if str(_GENERATORS_DIR) not in sys.path:
    sys.path.insert(0, str(_GENERATORS_DIR))

gen = importlib.import_module("generate_panorama_master_map")

_CHECKLIST_REL = Path(gen.CHECKLIST_REL)
_MASTER_REL = Path(gen.MASTER_REL)

_ANCHOR_ROWS = {
    # 攻击1 的插桩锚：§3 表内一行（在其后插幽灵新图行）
    "frontend": "| **frontend_map**（",
}


def _build_universe(tmp_path: Path) -> Path:
    """tmp 副本宇宙：master yaml+checklist+15 个节点锚文件，路径结构与真仓同构。"""
    (tmp_path / _CHECKLIST_REL.parent).mkdir(parents=True, exist_ok=True)
    (tmp_path / _CHECKLIST_REL).write_text(
        (_REPO / _CHECKLIST_REL).read_text(encoding="utf-8"), encoding="utf-8", newline="\n"
    )
    master = yaml.safe_load((_REPO / _MASTER_REL).read_text(encoding="utf-8"))
    for n in master["nodes"]:
        rel = Path(str(n["file"]))
        src = _REPO / rel
        dst = tmp_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_file():
            dst.write_bytes(src.read_bytes())
        else:
            dst.write_text("# 测试宇宙锚桩\n", encoding="utf-8")
    (tmp_path / _MASTER_REL.parent).mkdir(parents=True, exist_ok=True)
    (tmp_path / _MASTER_REL).write_bytes((_REPO / _MASTER_REL).read_bytes())
    return tmp_path


def _run_check(root: Path) -> int:
    return gen.main(["--check", "--root", str(root)])


def _errors_of(root: Path) -> list[str]:
    master = gen.load_master(root / _MASTER_REL)
    checklist = (root / _CHECKLIST_REL).read_text(encoding="utf-8")
    errors, _warnings, _stats = gen.validate(master, checklist, root)
    return errors


def _load_checklist_text(root: Path) -> str:
    return (root / _CHECKLIST_REL).read_text(encoding="utf-8")


def _write_checklist_text(root: Path, text: str) -> None:
    (root / _CHECKLIST_REL).write_text(text, encoding="utf-8", newline="\n")


def test_green_baseline_five_checks_pass(tmp_path: Path) -> None:
    """绿基线：真源副本宇宙五条全绿，--check 退出码 0。"""
    root = _build_universe(tmp_path)
    assert _errors_of(root) == []
    assert _run_check(root) == 0


def test_attack1_new_map_absent_from_master_is_red(tmp_path: Path) -> None:
    """红1：§3 新增图行而总图 nodes 不加 → E1 少节点，exit 1。"""
    root = _build_universe(tmp_path)
    text = _load_checklist_text(root)
    anchor = _ANCHOR_ROWS["frontend"]
    idx = text.index(anchor)
    line_end = text.index("\n", idx)
    ghost_row = "\n| **ghost_new_map**（幽灵新图） | PG | module_id | 规则 | 时机 | 工具 | 处置 | 横轴（结构） |"
    _write_checklist_text(root, text[:line_end] + ghost_row + text[line_end:])
    errors = _errors_of(root)
    assert any("E1" in e and "ghost_new_map" in e and "未入总图" in e for e in errors)
    assert _run_check(root) == 1


def test_attack1b_map_row_removed_from_section3_is_red(tmp_path: Path) -> None:
    """红1 反向：总图节点在而 §3 行被删 → E1 多节点（双闭的另一向）。"""
    root = _build_universe(tmp_path)
    text = _load_checklist_text(root)
    victim = "| **battle_map**（"
    idx = text.index(victim)
    line_end = text.index("\n", idx)
    _write_checklist_text(root, text[:idx] + text[line_end + 1 :])
    errors = _errors_of(root)
    assert any("E1" in e and "battle_map" in e and "不在 §3 在册图集" in e for e in errors)
    assert _run_check(root) == 1


def test_attack2_edge_to_nonexistent_map_is_red(tmp_path: Path) -> None:
    """红2：边端点指向节点集外的图 → E3，exit 1。"""
    root = _build_universe(tmp_path)
    master_path = root / _MASTER_REL
    master = yaml.safe_load(master_path.read_text(encoding="utf-8"))
    master["edges"].append({"from": "TDMAP-001", "to": "ghost_map", "relation_zh": "幽灵供料", "basis": "对抗注入"})
    master_path.write_text(yaml.safe_dump(master, allow_unicode=True, sort_keys=False), encoding="utf-8")
    errors = _errors_of(root)
    assert any("E3" in e and "ghost_map" in e for e in errors)
    assert _run_check(root) == 1


def test_attack3_node_file_deleted_is_red(tmp_path: Path) -> None:
    """红3：节点 file 被删 → E2 文件缺失，exit 1。"""
    root = _build_universe(tmp_path)
    (root / "config" / "trading_decision_map.yaml").unlink()
    errors = _errors_of(root)
    assert any("E2" in e and "TDMAP-001" in e and "不存在" in e for e in errors)
    assert _run_check(root) == 1


def test_render_is_byte_idempotent(tmp_path: Path) -> None:
    """幂等不变量：同输入两次渲染逐字节等（真宇宙语义，零时间戳）。"""
    root = _build_universe(tmp_path)
    master = gen.load_master(root / _MASTER_REL)
    checklist = _load_checklist_text(root)
    _errors, _warnings, stats = gen.validate(master, checklist, root)
    assert _errors == []
    first = gen.render_mermaid(master, stats)
    second = gen.render_mermaid(master, stats)
    assert first == second
    assert "2026" not in first  # 渲染零时间戳（年份缺席=禁壁钟硬判据）


def test_missing_master_fails_closed(tmp_path: Path) -> None:
    """fail-closed：master yaml 缺失=exit 2，不产半图。"""
    root = _build_universe(tmp_path)
    (root / _MASTER_REL).unlink()
    assert gen.main(["--check", "--root", str(root)]) == 2
