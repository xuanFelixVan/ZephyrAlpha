# [BLUEPRINT] MOD-INF-005 | scripts/scaffold.py | §_register_to_init 嵌套包注册
# [MODULE] tests.governance.test_scaffold_module_registration
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] pytest; ast; scripts.scaffold
# [CONSUMERS] scaffold 模块注册质量守卫（嵌套包斜杠/ast 自检/__all__ 幂等）
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 全部用例构造于 tmp 目录（monkeypatch SRC_ZEPHYR，不碰生产 src/）
# [MODIFY-GUARD] 与 scaffold._register_to_init / _insert_into_all_list 同批演进
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AssertionError
# [TESTS] self
# [A_module] module_id=MOD-INF-005 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""scaffold 模块注册测试（2026-09-15 治理上报件2）。

病根回归：``scaffold.py module signal_ashare/strategy_signal <name>`` 时
_register_to_init 用 package 原文（含斜杠）拼 import 行 →
``from zephyr.signal_ashare/strategy_signal.x import Y``（SyntaxError，
st-pattern 施工中四连发全靠手工救）。治本=dotted 化 + 写入前后 ast.parse
双自检 + __all__ 幂等集合语义。
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

import scripts.scaffold as scaffold

_PKG = "signal_ashare/strategy_signal"
_INIT_ANNOTATED = '"""strategy_signal 包。"""\n\n__all__: list[str] = []\n'


def _init_of(tmp_pkg: Path) -> Path:
    return tmp_pkg / "__init__.py"


# ---------------------------------------------------------------------------
# _register_to_init：嵌套包 dotted 化 + ast 双自检
# ---------------------------------------------------------------------------


def test_nested_package_import_is_dotted(tmp_path: Path):
    tmp_pkg = tmp_path / _PKG
    tmp_pkg.mkdir(parents=True)
    init = _init_of(tmp_pkg)
    init.write_text(_INIT_ANNOTATED, encoding="utf-8")

    scaffold._register_to_init(init, "MyAlgo", "my_algo", _PKG, False, [])

    content = init.read_text(encoding="utf-8")
    assert "from zephyr.signal_ashare.strategy_signal.my_algo import MyAlgo" in content
    assert "/" not in [ln for ln in content.splitlines() if ln.startswith("from ")][0]
    ast.parse(content)  # 独立复核：生成内容必须合法 Python
    assert content.count('"MyAlgo"') == 1  # 幂等：只注册一次


def test_register_to_init_idempotent(tmp_path: Path):
    tmp_pkg = tmp_path / _PKG
    tmp_pkg.mkdir(parents=True)
    init = _init_of(tmp_pkg)
    init.write_text(_INIT_ANNOTATED, encoding="utf-8")

    scaffold._register_to_init(init, "MyAlgo", "my_algo", _PKG, False, [])
    scaffold._register_to_init(init, "MyAlgo", "my_algo", _PKG, False, [])

    content = init.read_text(encoding="utf-8")
    assert content.count("from zephyr.signal_ashare.strategy_signal.my_algo import MyAlgo") == 1
    assert content.count('"MyAlgo"') == 1


def test_register_to_init_idempotent_against_legacy_append(tmp_path: Path):
    """历史病态 init（append 式注册残留）→ 不重复追加。"""
    tmp_pkg = tmp_path / _PKG
    tmp_pkg.mkdir(parents=True)
    init = _init_of(tmp_pkg)
    init.write_text(
        'from zephyr.signal_ashare.strategy_signal.my_algo import MyAlgo\n\n__all__.append("MyAlgo")\n',
        encoding="utf-8",
    )
    scaffold._register_to_init(init, "MyAlgo", "my_algo", _PKG, False, [])
    content = init.read_text(encoding="utf-8")
    assert content.count('__all__.append("MyAlgo")') == 1
    assert '"MyAlgo",' not in content


def test_register_to_init_creates_new_init_dotted(tmp_path: Path):
    tmp_pkg = tmp_path / _PKG
    tmp_pkg.mkdir(parents=True)  # 无 __init__.py
    init = _init_of(tmp_pkg)

    scaffold._register_to_init(init, "MyAlgo", "my_algo", _PKG, False, [])

    content = init.read_text(encoding="utf-8")
    assert "from zephyr.signal_ashare.strategy_signal.my_algo import MyAlgo" in content
    ast.parse(content)


def test_register_to_init_rejects_syntax_broken_content(tmp_path: Path):
    """init 本身语法坏档 → 写入前 ast.parse 拦截（ScaffoldError），文件零改写。"""
    tmp_pkg = tmp_path / _PKG
    tmp_pkg.mkdir(parents=True)
    init = _init_of(tmp_pkg)
    broken = 'from x import y\n\n__all__ = ["a"\n'  # 括号不闭合
    init.write_text(broken, encoding="utf-8")

    with pytest.raises(scaffold.ScaffoldError) as ei:
        scaffold._register_to_init(init, "MyAlgo", "my_algo", _PKG, False, [])
    assert "ast.parse" in str(ei.value)
    assert init.read_text(encoding="utf-8") == broken, "自检失败不得写坏档"


def test_register_to_init_dry_run_zero_write(tmp_path: Path):
    tmp_pkg = tmp_path / _PKG
    tmp_pkg.mkdir(parents=True)
    init = _init_of(tmp_pkg)
    init.write_text(_INIT_ANNOTATED, encoding="utf-8")
    pre = init.read_bytes()
    actions: list[str] = []

    scaffold._register_to_init(init, "MyAlgo", "my_algo", _PKG, True, actions)

    assert init.read_bytes() == pre
    assert any("DRY-RUN" in a for a in actions)


# ---------------------------------------------------------------------------
# _insert_into_all_list：正则修复（旧版 `[ __all__` 前导字面量永不匹配 → 全落 append 尾追）
# ---------------------------------------------------------------------------


def test_insert_into_all_list_plain_form():
    text = 'from a import B\n\n__all__ = ["Alpha"]\n'
    out = scaffold._insert_into_all_list(text, "Beta")
    assert "__all__ = [" in out
    assert '"Alpha"' in out and '"Beta"' in out
    assert "__all__.append" not in out  # 不再退化到 append 尾追
    entries = ast.literal_eval(out.split("__all__ = ", 1)[1].strip())
    assert entries == ["Alpha", "Beta"]  # 字母序


def test_insert_into_all_list_annotated_form():
    out = scaffold._insert_into_all_list(_INIT_ANNOTATED, "MyAlgo")
    assert "__all__: list[str] = [" in out
    assert '"MyAlgo"' in out
    ast.parse(out)


def test_insert_into_all_list_idempotent():
    text = '__all__ = ["Alpha"]\n'
    out = scaffold._insert_into_all_list(text, "Alpha")
    assert out == text  # 已存在 → 原样返回


# ---------------------------------------------------------------------------
# create_module 集成：嵌套包端到端（全依赖打桩，tmp src）
# ---------------------------------------------------------------------------


def test_create_module_nested_package_end_to_end(tmp_path: Path, monkeypatch, capsys):
    tmp_src = tmp_path / "src" / "zephyr"
    tmp_pkg = tmp_src / _PKG
    tmp_pkg.mkdir(parents=True)
    (tmp_pkg / "__init__.py").write_text(_INIT_ANNOTATED, encoding="utf-8")

    monkeypatch.setattr(scaffold, "SRC_ZEPHYR", tmp_src)
    captured: dict = {}
    monkeypatch.setattr(
        scaffold,
        "check_duplicate_functionality",
        lambda name, desc, domain, subdomain, force_override=False, expected_module_path="": captured.update(
            expected_module_path=expected_module_path
        ),
    )
    monkeypatch.setattr(scaffold, "_check_naming", lambda *a, **k: None)
    monkeypatch.setattr(scaffold, "_notify_asset_inventory", lambda *a, **k: None)
    monkeypatch.setattr(scaffold, "_register_creation_token", lambda *a, **k: None)
    monkeypatch.setattr(scaffold, "_sync_blueprint_file_list", lambda *a, **k: None)

    engine = scaffold.ScaffoldEngine(dry_run=False)
    created = engine.create_module(_PKG, "my_algo", description="测试模块")

    assert created.exists()
    assert "my_algo" in created.name
    # SSoT module_path 查重参数必须 dotted（斜杠原文会让反查永失配）
    assert captured["expected_module_path"] == "zephyr.signal_ashare.strategy_signal.my_algo"
    init_content = (tmp_pkg / "__init__.py").read_text(encoding="utf-8")
    assert "from zephyr.signal_ashare.strategy_signal.my_algo import MyAlgo" in init_content
    ast.parse(init_content)
    out = capsys.readouterr().out
    assert "from zephyr.signal_ashare.strategy_signal import MyAlgo" in out  # ACTION 提示 dotted
    assert "signal_ashare/strategy_signal import" not in out  # 斜杠原文不得出现


def test_trailing_slash_package_normalized(tmp_path: Path):
    """红蓝回归：尾斜杠包名（sig/sub/）→ dotted 化不得产生双点 import（2026-09-15 红蓝攻击1）。"""
    tmp_pkg = tmp_path / _PKG
    tmp_pkg.mkdir(parents=True)
    init = _init_of(tmp_pkg)
    init.write_text(_INIT_ANNOTATED, encoding="utf-8")

    scaffold._register_to_init(init, "MyAlgo", "my_algo", _PKG + "/", False, [])

    content = init.read_text(encoding="utf-8")
    assert ".." not in content
    ast.parse(content)
