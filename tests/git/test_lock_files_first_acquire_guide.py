# [A_test] test_id=RULING-480-D | module=scripts/lock_files.py | gate=pytest
# [TTL] task_bound
"""裁定#480 D 入口强制位测试：acquire 首次一次性说明书路由（车道C 手术3）。

全部 monkeypatch 隔离（_GUIDE_READS_DIR/_LOOKUP_AUDIT_DIR 指向 tmp_path，
cmd_acquire 用替身）——零生产面写入。渐进收紧第一档=只打印+留痕不阻断。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import lock_files  # noqa: E402
import pytest  # noqa: E402


@pytest.fixture
def isolated_guide_dirs(tmp_path: Path, monkeypatch) -> tuple[Path, Path]:
    """隔离留痕目录到 tmp_path（防测试写生产 .runtime）。"""
    guide = tmp_path / "guide_reads"
    audit = tmp_path / "lookup_audit"
    monkeypatch.setattr(lock_files, "_GUIDE_READS_DIR", guide)
    monkeypatch.setattr(lock_files, "_LOOKUP_AUDIT_DIR", audit)
    return guide, audit


def test_first_acquire_prints_route_and_marks_read(isolated_guide_dirs, capsys) -> None:
    """①首次：按扩展名路由打印锚点+落 guide_reads 留痕。"""
    guide, _audit = isolated_guide_dirs
    # 精确路由（detect_file_type 表驱动命中 config_yaml）
    lock_files._deliver_first_acquire_guide("st-fresh-1", "config/app.yaml")
    out = capsys.readouterr().out
    assert "首次施工指路" in out
    assert "FT-config_yaml" in out
    assert "## FT-config_yaml" in out
    assert "commit_navigation_playbook.md" in out
    marker = guide / "st-fresh-1.json"
    assert marker.exists()
    data = json.loads(marker.read_text(encoding="utf-8"))
    assert data["sid"] == "st-fresh-1" and "read_at" in data
    # .yaml 全量被 detect_file_type 表驱动精确命中（含未分类目录 → config_yaml 兜底）
    lock_files._deliver_first_acquire_guide("st-fresh-2", "weird/app.yaml")
    out2 = capsys.readouterr().out
    assert "FT-config_yaml" in out2


def test_second_acquire_silent(isolated_guide_dirs, capsys) -> None:
    """②已读（guide_reads 留痕）=零输出零开销。"""
    guide, _ = isolated_guide_dirs
    guide.mkdir(parents=True)
    (guide / "st-seen-1.json").write_text("{}", encoding="utf-8")
    lock_files._deliver_first_acquire_guide("st-seen-1", "src/x.py")
    assert capsys.readouterr().out == ""


def test_lookup_audit_counts_as_read(isolated_guide_dirs, capsys) -> None:
    """③已读（lookup_audit 能力反查审计存在）=老会话不再打扰。"""
    _guide, audit = isolated_guide_dirs
    audit.mkdir(parents=True)
    (audit / "st-audited-1.jsonl").write_text('{"ts":1}\n', encoding="utf-8")
    lock_files._deliver_first_acquire_guide("st-audited-1", "src/x.py")
    assert capsys.readouterr().out == ""


def test_ft_route_py_precise_and_fallback() -> None:
    """④路由表：scripts/*.py 精确命中 FT-new_script_py；无前缀 .py 回退字典 FT-python；未知扩展兜底 FT-universal。"""
    kw, anchors = lock_files._ft_route_for_path("scripts/governance/register_asset.py")
    assert kw == "FT-new_script_py"
    assert "## FT-new_script_py" in anchors
    kw1, anchors1 = lock_files._ft_route_for_path("wip/foo.py")
    assert kw1 == "FT-python"  # detect_file_type 无前缀规则 → 扩展字典回退
    assert any("FT-new" in a for a in anchors1)
    kw2, anchors2 = lock_files._ft_route_for_path("assets/model.bin")
    assert kw2 == "FT-universal"
    assert "## FT-universal" in anchors2


def test_acquire_cli_delivers_guide_on_success(isolated_guide_dirs, monkeypatch, capsys) -> None:
    """⑤CLI 集成：acquire 成功后递送路由（cmd_acquire 替身 rc=0，零锁面写入）。"""
    monkeypatch.setattr(lock_files, "cmd_acquire", lambda *a, **k: print("ACQUIRED — fake") or 0)
    monkeypatch.setattr(
        sys,
        "argv",
        ["lock_files.py", "acquire", "scripts/governance/new_tool.py", "st-cli-1", "--session", "st-cli-1"],
    )
    assert lock_files.main() == 0
    out = capsys.readouterr().out
    assert "ACQUIRED" in out
    assert "首次施工指路" in out
    assert "FT-new_script_py" in out
    # 第二次同 sid acquire：零指路输出
    monkeypatch.setattr(
        sys,
        "argv",
        ["lock_files.py", "acquire", "scripts/governance/new_tool.py", "st-cli-1", "--session", "st-cli-1"],
    )
    assert lock_files.main() == 0
    out2 = capsys.readouterr().out
    assert "首次施工指路" not in out2
