"""find_repo_root() 双真源一致性测试。

src/zephyr/shared/io/paths.py 和 scripts/governance/_shared/constants.py
各自实现 find_repo_root(),因 scripts/ 不能 import src/ 无法消除双真源。
本测试确保两份实现逐字相同——改一处必须改另一处,否则测试失败。

治本原理:接受架构约束的双真源,用测试保证一致性,而非消除双真源。
"""
import ast
import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_IMPL = REPO_ROOT / "src" / "zephyr" / "shared" / "io" / "paths.py"
SCRIPTS_IMPL = REPO_ROOT / "scripts" / "governance" / "_shared" / "constants.py"


def _extract_find_repo_root_ast(filepath: Path) -> ast.FunctionDef:
    """提取文件的 find_repo_root() 函数 AST 节点。"""
    tree = ast.parse(filepath.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "find_repo_root":
            return node
    raise AssertionError(f"{filepath} 中未找到 find_repo_root() 函数")


def test_find_repo_root_ast_identical():
    """两个 find_repo_root() 实现的 AST 必须完全相同(逐字相同)。"""
    src_ast = _extract_find_repo_root_ast(SRC_IMPL)
    scripts_ast = _extract_find_repo_root_ast(SCRIPTS_IMPL)
    src_dump = ast.dump(src_ast)
    scripts_dump = ast.dump(scripts_ast)
    assert src_dump == scripts_dump, (
        f"find_repo_root() 双真源 AST 不一致!\n"
        f"src/ 实现:\n{ast.unparse(src_ast)}\n\n"
        f"scripts/ 实现:\n{ast.unparse(scripts_ast)}\n\n"
        f"改一处必须同时改另一处,否则违反 DRY + 向内收原则。\n"
        f"capability: find_repo_root (canonical=src/, duplicate=scripts/)"
    )


def test_find_repo_root_returns_same_value():
    """两个 find_repo_root() 返回值必须相同(运行时验证)。"""
    # 加载 src/ 版本
    spec_src = importlib.util.spec_from_file_location("src_paths", SRC_IMPL)
    mod_src = importlib.util.module_from_spec(spec_src)
    spec_src.loader.exec_module(mod_src)

    # 加载 scripts/ 版本
    spec_scripts = importlib.util.spec_from_file_location("scripts_constants", SCRIPTS_IMPL)
    mod_scripts = importlib.util.module_from_spec(spec_scripts)
    spec_scripts.loader.exec_module(mod_scripts)

    src_root = mod_src.find_repo_root()
    scripts_root = mod_scripts.find_repo_root()
    assert src_root == scripts_root, (
        f"find_repo_root() 返回值不一致: src={src_root}, scripts={scripts_root}"
    )
