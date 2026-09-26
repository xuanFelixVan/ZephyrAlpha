# [TTL] task_bound
"""test_check_mirror_tree.py — check_mirror_tree（镜像树只读计量器，NR-006）单元测试。

全部用 tmp_path 假仓注入（docs_root/src_root 参数化入口），零生产路径写入。
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parent.parent.parent.parent
    / "scripts"
    / "governance"
    / "d1_structure"
    / "check_mirror_tree.py"
)
_spec = importlib.util.spec_from_file_location("_check_mirror_tree_under_test", _SCRIPT)
_mod = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _mod  # dataclass 解析注解需要 sys.modules 注册
_spec.loader.exec_module(_mod)

mirror_doc_rel = _mod.mirror_doc_rel
normalize_source_path = _mod.normalize_source_path
dotted_module_to_source = _mod.dotted_module_to_source
scan_docs = _mod.scan_docs
render_report = _mod.render_report


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def _doc(module: str, sot: str | None) -> str:
    lines = [f"module: {module}"]
    if sot:
        lines.append(f"source_of_truth: {sot}")
    return "\n".join(lines) + "\n"


def _make_repo(tmp: Path) -> tuple[Path, Path]:
    """构造假仓：3 包（alpha/beta/gamma），文档含镜像命中/旧域漂移/双目录/坏 yaml。"""
    src = tmp / "src" / "zephyr"
    for pkg_file in (
        "alpha/__init__.py",
        "alpha/core.py",
        "alpha/sub/__init__.py",
        "alpha/sub/tool.py",
        "beta/__init__.py",
        "beta/util.py",
        "gamma/__init__.py",  # 无文档 → 未覆盖
    ):
        _write(src / pkg_file, "")
    docs = tmp / "docs" / "03_modules"
    _write(docs / "beta" / "util.yaml", _doc("src.zephyr.beta.util", "src/zephyr/beta/util.py"))
    _write(
        docs / "alpha" / "sub" / "sub__init__.yaml",
        _doc("src.zephyr.alpha.sub.__init__", "src/zephyr/alpha/sub/__init__.py"),
    )
    _write(
        docs / "_domain_alpha" / "algo_flow" / "core.yaml",
        _doc("src.zephyr.alpha.core", "src/zephyr/alpha/core.py"),
    )
    _write(
        docs / "_domain_alpha2" / "algo_flow" / "core.yaml",
        _doc("zephyr.alpha.core", None),  # 缺 src 首段的 dotted 口径
    )
    _write(
        docs / "_domain_beta" / "legacy.yaml",
        _doc("src.zephyr.beta.util", "src/zephyr/beta/util.py"),
    )
    _write(docs / "broken.yaml", "ref: *undefined_anchor\n")  # 未定义锚 = 保证 yaml 解析失败
    _write(docs / "other" / "note.yaml", _doc("scripts.foo", None))
    return docs, src


def test_pure_normalizers(tmp_path: Path) -> None:
    assert normalize_source_path("src/zephyr/a/b.py") == "zephyr/a/b.py"
    assert normalize_source_path("zephyr/a.py") == "zephyr/a.py"
    assert normalize_source_path(".\\src\\zephyr\\a.py") == "zephyr/a.py"
    assert normalize_source_path("docs/x.py") is None
    assert dotted_module_to_source("src.zephyr.a.b") == "zephyr/a/b.py"
    assert dotted_module_to_source("zephyr.a") == "zephyr/a.py"  # 缺 src 首段兼容
    assert dotted_module_to_source("scripts.foo") is None
    assert dotted_module_to_source("zephyr") is None
    assert mirror_doc_rel("zephyr/alpha/core.py") == "docs/03_modules/alpha/core.yaml"
    assert mirror_doc_rel("zephyr/alpha/sub/__init__.py") == "docs/03_modules/alpha/sub/sub__init__.yaml"
    assert mirror_doc_rel("zephyr/__init__.py") == "docs/03_modules/__init__.yaml"


def test_coverage_mirror_and_drift(tmp_path: Path) -> None:
    docs, src = _make_repo(tmp_path)
    r = scan_docs(docs_root=docs, src_root=src)
    assert sorted(r.packages) == ["alpha", "beta", "gamma"]
    assert sorted(r.covered_pkgs) == ["alpha", "beta"]  # gamma 无档
    assert sorted(r.mirror_pkgs) == ["alpha", "beta"]  # util.yaml 精确命中 + sub__init 命名
    assert len(r.claims) == 5
    drift_dirs = [d["doc_rel"] for d in r.drift if d["reason"] == "dir"]
    assert len(drift_dirs) == 3
    assert "docs/03_modules/_domain_alpha/algo_flow/core.yaml" in drift_dirs
    assert r.dual_dir == {
        "zephyr/alpha/core.py": [
            "_domain_alpha/algo_flow",
            "_domain_alpha2/algo_flow",
        ],
        "zephyr/beta/util.py": ["_domain_beta", "beta"],
    }
    assert sorted(r.pkg_dir_spread) == ["alpha", "beta"]
    assert len(r.parse_errors) == 1
    assert r.non_zephyr_docs == 1


def test_read_only_no_writes(tmp_path: Path) -> None:
    docs, src = _make_repo(tmp_path)
    before = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    scan_docs(docs_root=docs, src_root=src)
    after = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*"))
    assert before == after


def test_render_report_lines(tmp_path: Path) -> None:
    docs, src = _make_repo(tmp_path)
    text = render_report(scan_docs(docs_root=docs, src_root=src))
    assert "镜像树计量" in text
    assert "包级文档覆盖" in text
    assert "非镜像位按包分布" in text
    assert "同源双目录漂移: 2 个源文件" in text


def test_cli_exit_codes(tmp_path: Path, monkeypatch) -> None:
    docs, src = _make_repo(tmp_path)
    monkeypatch.setattr(_mod, "DOCS_ROOT", docs)
    monkeypatch.setattr(_mod, "SRC_ROOT", src)
    assert _mod.main(["--json"]) == 0  # 默认报告模式，漂移不阻断
    assert _mod.main(["--fail-on-drift"]) == 1  # 显式收紧才 exit 1
