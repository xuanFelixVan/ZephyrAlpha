# [A_test] module_id=MOD-GOV-CSHARD-REDPIN | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TESTS] self
# [TTL] task_bound
"""反向钉桩：证明 T12 采集分片工具"只诊断不赦免"（真断链永远报红，环境性缺席只贴标签不从红面消失）。

覆盖：
  1. 真断链（仓内命名空间 zephyr.* 缺失）→ classify=real_broken_link。
  2. 环境性缺席（已知可选第三方 cudf 等）→ classify=environmental（仅标签）。
  3. fail-toward-red 默认：未知顶层 ModuleNotFound → real_broken_link（不猜环境）。
  4. 语法/注册表 KeyError/fixture 缺失 → real_broken_link（禁赦免）。
  5. 端到端"不被赦免"：tmp 真断链测试经 --collect-only --continue-on-collection-errors
     仍计入 error_count（未因贴标签/分片而静默）——反假绿主形态钉桩。
  6. environmental 标签永不从 error 面剥离：解析后仍在 errors 里且 error_count 含之。
  7. 错峰入口 --shard N --dry-run 只切单目录窗口（打印命令，不跑全库）。

测试禁写生产路径（根宪法§9.6）：真断链样例只落 tmp_path，不碰 tests/ 生产面。
"""

from __future__ import annotations

import subprocess
import sys

import pytest

from scripts.governance.generators.generate_collection_shard_manifest import (
    classify_error,
    enumerate_shards,
    main,
    parse_collect_output,
)


def _block(first_line: str, file: str = "tests/x/test_y.py") -> str:
    return f"_ ERROR collecting {file} _\nImportError while importing test module.\n{first_line}\n"


def test_real_broken_link_repo_namespace():
    blk = _block("E   ModuleNotFoundError: No module named 'zephyr.orchestrator.lifecycle'")
    assert classify_error(blk)["category"] == "real_broken_link"
    assert classify_error(blk)["missing_module"] == "zephyr"


def test_environmental_optional_third_party_is_label_only():
    blk = _block("E   ModuleNotFoundError: No module named 'cudf.core'")
    rec = classify_error(blk)
    assert rec["category"] == "environmental"
    assert rec["missing_module"] == "cudf"
    # 标签≠赦免：first_line 仍被留痕记录
    assert "cudf" in rec["first_line"]


def test_fail_toward_red_unknown_top_namespace():
    blk = _block("E   ModuleNotFoundError: No module named 'totally_unknown_third_party'")
    # 未知顶层不得判环境，默认归真断链（防把断链凑绿）
    assert classify_error(blk)["category"] == "real_broken_link"


def test_syntax_and_registry_errors_are_real_broken_link():
    assert classify_error(_block("E   SyntaxError: invalid syntax"))["category"] == "real_broken_link"
    assert (
        classify_error(
            _block("E   KeyError: \"category_id 'news_sentiment_score' 未在 business_data_categories.yaml 注册\"")
        )["category"]
        == "real_broken_link"
    )


def test_environmental_label_never_stripped_from_error_surface():
    # 一段既有 env 又有 real 的采集输出：两者都必须留在 errors 面，error_count=2
    out = (
        "==== ERRORS ====\n"
        "_ ERROR collecting tests/x/test_real.py _\n"
        "E   ModuleNotFoundError: No module named 'zephyr.orchestrator.lifecycle'\n"
        "_ ERROR collecting tests/x/test_env.py _\n"
        "E   ModuleNotFoundError: No module named 'torch'\n"
        "==== 10 tests collected, 2 errors in 1.00s ====\n"
    )
    parsed = parse_collect_output(out)
    cats = {e["category"] for e in parsed["errors"]}
    assert parsed["error_count"] == 2
    assert cats == {"real_broken_link", "environmental"}
    # env 条目未被过滤（在册假绿：把 env 判绿会从红面消失）
    assert any(e["file"].endswith("test_env.py") for e in parsed["errors"])


def test_live_collect_real_broken_link_not_absolved(tmp_path):
    """端到端：真断链经分片式只读采集仍报红，不被跳过/赦免。"""
    import os
    from pathlib import Path

    repo_src = str(Path(__file__).resolve().parents[3] / "src")
    f = tmp_path / "test_t12_realbroken.py"
    f.write_text(
        "import zephyr.t12_definitely_absent_module_xyz  # noqa\n\n\ndef test_stub():\n    assert True\n",
        encoding="utf-8",
    )
    # 继承完整 os.environ（Windows 套接字/WSA 需 SYSTEMROOT 等），仅覆盖 PYTHONPATH
    child_env = {**os.environ, "PYTHONPATH": repo_src, "PYTHONNOUSERSITE": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(f), "--collect-only", "-q", "--continue-on-collection-errors"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=child_env,
    )
    out = proc.stdout + proc.stderr
    parsed = parse_collect_output(out)
    assert parsed["error_count"] >= 1, f"真断链被静默（假绿）：\n{out[-800:]}"
    real = [e for e in parsed["errors"] if e["category"] == "real_broken_link"]
    assert real, "真断链须归 real_broken_link，不得被判环境跳过"
    assert real[0]["missing_module"] == "zephyr"


def test_shard_entry_slices_one_directory_dry_run(capsys):
    shards = enumerate_shards()
    assert shards, "tests/ 一级目录分片枚举为空"
    rc = main(["--shard", "0", "--dry-run"])
    assert rc == 0
    printed = capsys.readouterr().out
    assert "python -m pytest" in printed
    # 只切一片：不得出现 tests/ 全量（错峰核心=单目录窗口）
    assert (" tests " not in printed and "tests/gov " not in printed) or "tests/" in printed


def test_enumerate_shards_excludes_dunder_and_hidden():
    shards = enumerate_shards()
    assert all(not s.startswith((".", "__")) for s in shards)
    assert "gov" in shards and "trade" in shards
