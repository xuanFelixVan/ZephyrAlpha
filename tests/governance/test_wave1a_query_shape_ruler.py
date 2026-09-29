# [TTL] task_bound
# [STARTUP] test_only: pytest 收集，无运行期常驻
# [CONSUMERS] CI/本地 pytest; docs/_working/total_command_closeout/wave1a/dead_store_triage.md §4 红证锚
"""红证二：CH 读接口形状尺必须能红（W-180.2 出口判据）。

用 2026-09-26 终审卷 §7.1 的三个病样本作天然红证输入：
  P2 型 `ch_reader.query(sql)[0][0]`（467 读成 4）
  P1 型 `for r in ch_reader.query(sql)`（字符劈裂）
  赋值后变体 `tsv = ch_reader.query(sql)` + `tsv[0][0]` / `for r in tsv`
并反向证明**正确用法零误报**（`tsv.splitlines()` / `query_rows()[0][0]` / isinstance 分流）。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

_LANE_ROOT = Path(__file__).resolve().parents[2]
_RULER = _LANE_ROOT / "scripts" / "governance" / "wave1a" / "ch_read_shape_ruler.py"


def _load_ruler():
    spec = importlib.util.spec_from_file_location("ch_read_shape_ruler", _RULER)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


ruler = _load_ruler()

_JUDGMENT_FILE = "scripts/audit_wave1a_canary.py"

RED_SAMPLES = {
    "S1 直接下标（P2 病样本）": (
        "def f(ch_reader):\n"
        "    sql = 'SELECT count() FROM c1_market.kline_daily'\n"
        "    n = ch_reader.query(sql)[0][0]\n"
        "    return n\n",
        "S1_DIRECT_SUBSCRIPT",
    ),
    "S2 直接 for-in（P1 病样本）": (
        "def f(ch_reader):\n    for row in ch_reader.query('SELECT name FROM system.tables'):\n        print(row)\n",
        "S2_FOR_IN_CALL",
    ),
    "S3 赋值后下标": (
        "def f(ch_reader):\n    tsv = ch_reader.query(sql)\n    return tsv[0][0]\n",
        "S3_VAR_SUBSCRIPT",
    ),
    "S3 赋值后 for-in": (
        "def f(ch_reader):\n"
        "    tsv = ch_writer.query_table('c1_market.kline_daily')\n"
        "    for line in tsv:\n"
        "        print(line)\n",
        "S3_VAR_FOR_IN",
    ),
}

GREEN_SAMPLES = {
    "正确用法：splitlines 后按行迭代": (
        "def f(ch_reader):\n"
        "    tsv = ch_reader.query(sql)\n"
        "    for line in tsv.strip().splitlines():\n"
        "        cols = line.split('\\t')\n",
    ),
    "严格通道：query_rows 返回行元组，下标合法": (
        "def f(ch_reader):\n    rows = ch_reader.query_rows(sql)\n    return rows[0][0]\n",
    ),
    "形状已由 isinstance 分流": (
        "def f(ch_reader):\n"
        "    result = ch_reader.query(sql)\n"
        "    if isinstance(result, (list, tuple)):\n"
        "        for item in result:\n"
        "            pass\n",
    ),
}


@pytest.mark.parametrize("label", list(RED_SAMPLES))
def test_ruler_must_go_red_on_broken_shape(label):
    src, expected_kind = RED_SAMPLES[label]
    findings = ruler.scan_text(src, _JUDGMENT_FILE)
    kinds = {f.kind for f in findings}
    assert expected_kind in kinds, f"{label}: 尺未红（期望 {expected_kind}，实得 {kinds}）"
    assert all(f.severity == "JUDGMENT" for f in findings), "判据路径命中必须判 JUDGMENT（硬红）"


@pytest.mark.parametrize("label", list(GREEN_SAMPLES))
def test_ruler_stays_quiet_on_correct_usage(label):
    src = GREEN_SAMPLES[label][0]
    assert ruler.scan_text(src, _JUDGMENT_FILE) == [], f"{label}: 正确用法被误报"


def test_ruler_cli_exit_code_red(tmp_path):
    bad = tmp_path / "scripts" / "audit_canary_shape.py"
    bad.parent.mkdir(parents=True, exist_ok=True)
    bad.write_text(RED_SAMPLES["S1 直接下标（P2 病样本）"][0], encoding="utf-8")
    rc = ruler.main(["--root", str(tmp_path), "--files", str(bad)])
    assert rc == 1, "判据路径命中 ⇒ 退出码必须 1（尺能红）"


def test_ruler_cli_exit_code_green(tmp_path):
    ok = tmp_path / "scripts" / "audit_canary_ok.py"
    ok.parent.mkdir(parents=True, exist_ok=True)
    ok.write_text(GREEN_SAMPLES["严格通道：query_rows 返回行元组，下标合法"][0], encoding="utf-8")
    assert ruler.main(["--root", str(tmp_path), "--files", str(ok)]) == 0


def test_ruler_head_tree_baseline_is_reproducible():
    """存量基线（波 1A.5 开工首读）：HEAD 树候选面命中可复算，且无 S1/S2 类硬违规。

    硬违规=硬红=JUDGMENT（尺 §退出码契约）；tests/ 豁免面引用病样本字面量属
    EXEMPT 软红——本测试文件自身引用 RED_SAMPLES 病样本即属此类，不算硬违约
    （2026-09-30 SW19 死账救援修正：q0213 捞回本件后 HEAD 树自 trip 假红）。
    """
    findings, scanned, _ = ruler.run(_LANE_ROOT, None)
    assert scanned > 10, f"HEAD 树候选文件数异常：{scanned}"
    hard = [f for f in findings if f.kind in ("S1_DIRECT_SUBSCRIPT", "S2_FOR_IN_CALL") and f.severity == "JUDGMENT"]
    assert hard == [], f"HEAD 树存在未清算的直取违约：{[(f.file, f.line_no) for f in hard]}"
