# [BLUEPRINT] MOD-OPS-018 | docs/03_modules/_domain_operations/dev_env_setup/blueprint.md | §
# [MODULE] setup_dev_env
# [DOMAIN] D_OPS
# [DEPENDENCIES] site (stdlib)
# [CONSUMERS] AI session 冷启动（.trae/rules/project_rules.md FIRST-READ 步骤 0）
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] USER_SITE/usercustomize.py 内容由本脚本唯一生成；重复运行幂等覆盖
# [MODIFY-GUARD] 修改 USERCUSTOMIZE_TEMPLATE 需同步更新 sitecustomize.py docstring + project_rules.md FIRST-READ 步骤 0
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 失败时打印诊断信息并 exit 1；绝不静默失败
# [TESTS] tests/test_setup_dev_env.py
# [A_module] module_id=MOD-OPS-018 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 无时间触发
"""开发环境一次性初始化（裁定 #ARCH-PYTHON-SITECUSTOMIZE）。

病根：Python 3.11 的 site 模块在 `python -c` 模式下不搜索 cwd 中的
sitecustomize.py（安全机制），导致仓库根的 sitecustomize.py 是死代码，
`python -c "import zephyr"` 失败（ModuleNotFoundError）。

治本：在 USER_SITE 创建 usercustomize.py，site 模块的 execusercustomize()
会可靠加载它。usercustomize.py 把 src/ 加入 sys.path 并安装 runtime_interceptor。

用法：
    python scripts/setup_dev_env.py           # 安装/更新 usercustomize.py
    python scripts/setup_dev_env.py --check   # 仅检查，不写入
    python scripts/setup_dev_env.py --verify  # 安装后验证 import zephyr

幂等：重复运行安全（覆盖写入）。
"""

from __future__ import annotations

import argparse
import os
import site
import subprocess
import sys
from pathlib import Path

USERCUSTOMIZE_TEMPLATE = '''"""usercustomize.py — ZephyrAlpha 开发环境自动配置（Python site 模块自动加载）。

放置位置：USER_SITE 目录（site.getusersitepackages()）。
加载时机：Python 解释器启动时，site 模块在 execsitecustomize() 之后调用
         execusercustomize()，自动 import 本模块（当 ENABLE_USER_SITE=True）。

功能：
  1. 把 <repo_root>/src 加入 sys.path（使 `import zephyr` 可用）
  2. 安装 LLM 裸调运行时拦截器（runtime_interceptor）

kill-switch：ZEPHYR_RUNTIME_GATE=0 → 完全关闭。
错误处理：任何异常静默吞掉——绝不破坏解释器启动。

生成器：scripts/setup_dev_env.py（裁定 #ARCH-PYTHON-SITECUSTOMIZE）
"""

import os
import sys
from pathlib import Path

_KILL_SWITCH = "ZEPHYR_RUNTIME_GATE"

if os.environ.get(_KILL_SWITCH, "1") == "0":
    pass
else:
    try:
        _repo_root_env = os.environ.get("ZEPHYR_ALPHA_ROOT")
        if _repo_root_env:
            _repo_root = Path(_repo_root_env).resolve()
        else:
            _repo_root = Path(r"{repo_root}").resolve()
        _src_path = str(_repo_root / "src")
        if _src_path not in sys.path:
            sys.path.insert(0, _src_path)
        from zephyr.security.llm_defense.llm_security.runtime_interceptor import install as _install
        _install()
    except Exception:
        pass
'''


def _find_repo_root() -> Path:
    """从本脚本位置推算仓库根（scripts/setup_dev_env.py → 仓库根）。"""
    return Path(__file__).resolve().parent.parent


def _get_usercustomize_path() -> Path:
    """返回 USER_SITE/usercustomize.py 的绝对路径。"""
    return Path(site.getusersitepackages()) / "usercustomize.py"


def _is_installed(usercustomize_path: Path, repo_root: Path) -> bool:
    """检查 usercustomize.py 是否已安装且指向当前仓库。"""
    if not usercustomize_path.exists():
        return False
    content = usercustomize_path.read_text(encoding="utf-8")
    # 检查是否包含当前仓库路径（大小写不敏感，Windows）
    return str(repo_root).lower() in content.lower()


def install(repo_root: Path | None = None) -> Path:
    """安装 usercustomize.py 到 USER_SITE。

    Args:
        repo_root: 仓库根路径（None 则自动推算）。

    Returns:
        usercustomize.py 的绝对路径。
    """
    if repo_root is None:
        repo_root = _find_repo_root()
    usercustomize_path = _get_usercustomize_path()
    usercustomize_path.parent.mkdir(parents=True, exist_ok=True)
    content = USERCUSTOMIZE_TEMPLATE.format(repo_root=str(repo_root).replace("\\", "\\\\"))
    usercustomize_path.write_text(content, encoding="utf-8")
    return usercustomize_path


def verify() -> bool:
    """验证 `python -c "import zephyr"` 是否成功（在新进程中执行）。"""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import zephyr; print(zephyr.__file__)"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and "zephyr" in result.stdout.lower():
            print(f"VERIFY OK: {result.stdout.strip()}")
            return True
        print(f"VERIFY FAIL (exit={result.returncode}):")
        print(f"  stdout: {result.stdout.strip()}")
        print(f"  stderr: {result.stderr.strip()}")
        return False
    except Exception as exc:  # noqa: BLE001 — 5.135治标: broad exception catch
        print(f"VERIFY ERROR: {type(exc).__name__}: {exc}")
        return False


def main() -> int:
    """CLI 入口。"""
    parser = argparse.ArgumentParser(
        description="开发环境一次性初始化：安装 usercustomize.py（裁定 #ARCH-PYTHON-SITECUSTOMIZE）"
    )
    parser.add_argument("--check", action="store_true", help="仅检查，不写入")
    parser.add_argument("--verify", action="store_true", help="安装后验证 import zephyr")
    args = parser.parse_args()

    repo_root = _find_repo_root()
    usercustomize_path = _get_usercustomize_path()

    if args.check:
        installed = _is_installed(usercustomize_path, repo_root)
        print(f"CHECK: usercustomize.py at {usercustomize_path}")
        print(f"  exists: {usercustomize_path.exists()}")
        print(f"  installed (points to {repo_root}): {installed}")
        return 0 if installed else 1

    if not _is_installed(usercustomize_path, repo_root):
        print(f"INSTALL: writing usercustomize.py to {usercustomize_path}")
        install(repo_root)
        print(f"INSTALL OK: {usercustomize_path}")
    else:
        print(f"ALREADY INSTALLED: {usercustomize_path} (pointing to {repo_root})")

    if args.verify:
        if not verify():
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
