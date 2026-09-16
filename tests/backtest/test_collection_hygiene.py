# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [TESTS] 测试收集卫生守卫（#ARCH-COLLECTION-HYGIENE-001，2026-09-14 外审整改收尾）
# [SCOPE] 防测试拷贝污染收集：norecursedirs 配置钉扎 + 杂散文件不被收集的实证探针
# [TTL] permanent
"""Tests for collection hygiene (#ARCH-COLLECTION-HYGIENE-001).

背景（假红实证）：.runtime/tmp 残留的会话级测试拷贝（test_sim_paper_ledger.py/
test_strategy_screen_query.py 陈旧副本）曾被 pytest 收集，canonical 全绿的同时
产出假红（test_bothwin_gate），污染"绿=安全"信号——100% AI 开发场景下测试信号
是唯一安全网，假红/假绿同等致命。

结构性防御（本守卫钉扎，防配置回退）：
  1. pyproject [tool.pytest.ini_options].norecursedirs 覆盖 .runtime/data/tmp
     （norecursedirs 整体替换 pytest 默认值，必须重含默认项——pytest 文档契约）；
  2. 精简 ini（config/pytest_min.ini，-c 引用时整体替换 pyproject；2026-09-16 外审
     遗留㉑由 .runtime/tmp TTL 区迁永久纳管——原位置会被 cleanup 扫走，收集卫生随之失守）
     同步 norecursedirs + testpaths 指回 canonical tests 树（无参裸跑不收集
     rootdir 内残留）；
  3. 实证探针：.runtime/tmp 放置杂散 test 文件后，args 模式收集结果零污染。
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
_PY = sys.executable


def _pytest(*args: str) -> str:
    r = subprocess.run(
        [_PY, "-m", "pytest", "-p", "no:cacheprovider", *args],
        cwd=str(_REPO),
        capture_output=True,
        text=True,
        timeout=600,
    )
    return r.stdout + r.stderr


def test_pyproject_norecursedirs_covers_runtime_data_tmp():
    """pyproject norecursedirs 钉扎：全列表锁定（防好心加宽误伤真实测试目录）。

    教训（施工实证）：曾加 "data"/"tmp" 条目，而 tests/data、tests/zephyr/data 是
    真实测试目录——norecursedirs 会静默剪掉它们（漏测=100% AI 场景下最危险的失败
    模式），施工中已抓到回退。本测试钉扎完整列表，任何增删都必须显式改这里。
    """
    try:
        import tomllib
    except ImportError:  # pragma: no cover - py3.12 必有 tomllib
        pytest.skip("tomllib unavailable")
    cfg = tomllib.loads((_REPO / "pyproject.toml").read_text(encoding="utf-8"))
    entries = set(cfg["tool"]["pytest"]["ini_options"]["norecursedirs"])
    # 防御目标：运行时目录不参与收集递归
    assert ".runtime" in entries
    # norecursedirs 整体替换 pytest 默认值——默认项必须重含（pytest 文档契约）
    for default in ("*.egg", ".*", "_darcs", "build", "CVS", "dist", "node_modules", "venv"):
        assert default in entries, f"默认项 {default} 丢失（替换语义会误伤常规目录）"
    # 防误伤：真实测试目录名禁入黑名单（新增条目前必须先确认 tests/ 下无同名目录）
    assert "data" not in entries and "tmp" not in entries
    # 真实目录存在性自检（若未来新增同名目录，此处先红，提醒勿加宽黑名单）
    assert (_REPO / "tests" / "data").is_dir()


def test_scratch_ini_mirrors_hygiene():
    """精简 ini（-c 引用时替换 pyproject）必须自带同款 norecursedirs。"""
    ini = _REPO / "config" / "pytest_min.ini"
    if not ini.exists():
        pytest.skip("config/pytest_min.ini 缺失（永久纳管件，正常检出必在——缺失=检出破损）")
    text = ini.read_text(encoding="utf-8")
    assert "norecursedirs" in text
    assert ".runtime" in text
    # 同防误伤约束
    nore_line = [ln for ln in text.splitlines() if ln.strip().startswith("norecursedirs")][0]
    assert " data " not in f" {nore_line} " and " tmp " not in f" {nore_line} "


def test_stray_copy_never_collected(tmp_path):
    """实证探针：.runtime/tmp 放杂散 test 文件，args 模式收集零污染。"""
    min_ini = _REPO / "config" / "pytest_min.ini"
    if not min_ini.exists():
        pytest.skip("config/pytest_min.ini 缺失——与 test_scratch_ini_mirrors_hygiene 同守卫")
    stray = _REPO / ".runtime" / "tmp" / "test_zz_collection_hygiene_probe.py"
    stray.parent.mkdir(parents=True, exist_ok=True)
    stray.write_text("def test_probe_should_never_be_collected():\n    assert True\n", encoding="utf-8")
    try:
        # 注意：精简 ini addopts 已含 -q，命令行再加 -q 会变 -qq（collect-only
        # 连 nodeid 行都吞掉），故此处不再传 -q。
        out = _pytest(
            "tests/backtest/test_engine_base.py", "--collect-only", "--no-header", "-c", "config/pytest_min.ini"
        )
        # 杂散探针不得被收集（收集行=含 "::" 的行；头部 rootdir/configfile 行含
        # ".runtime" 属正常输出，不参与断言）
        collected = [ln for ln in out.splitlines() if "::" in ln]
        assert collected, "canonical 目标文件本身必须被收集到（守卫自身不误伤正常收集）"
        assert not any("test_zz_collection_hygiene_probe" in ln for ln in collected)
        assert not any(".runtime" in ln for ln in collected)
    finally:
        # rmtree 对**文件**在 ignore_errors 下静默失败 → 杂散探针曾每次跑完残留
        # （正是本守卫要防的 .runtime/tmp 污染类），故文件用 unlink 清。
        stray.unlink(missing_ok=True)
        shutil.rmtree(_REPO / ".runtime" / "tmp" / "__pycache__", ignore_errors=True)
