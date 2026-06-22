"""自动迭代移除 governance/__init__.py 中导入失败的模块。

策略:
1. 尝试 import zephyr.governance
2. 如果失败，从错误信息中提取失败的模块名
3. 从 __init__.py 中移除该模块的 import 语句和 __all__ 条目
4. 重试，直到 import 成功或所有新增 import 都被移除

用法:
    python scripts/governance/iterative_cleanup_imports.py
"""

__manifest__ = {
    "args": [],
    "description": "自动迭代移除 __init__.py 中导入失败的模块",
    "dimensions": ["D1", "D7"],
    "priority": "P2",
    "timeout_seconds": 120,
    "warn_only": False,
}

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INIT_PY = PROJECT_ROOT / "src" / "zephyr" / "governance" / "__init__.py"


def try_import() -> tuple[bool, str]:
    """尝试 import zephyr.governance。

    Returns:
        (success, error_message)
    """
    try:
        result = subprocess.run(
            ["python", "-c", "import zephyr.governance; print('OK')"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        if result.returncode == 0:
            return True, ""
        return False, result.stderr.strip()
    except subprocess.SubprocessError as e:
        return False, str(e)


def extract_failed_module(error: str) -> str | None:
    """从错误信息中提取失败的模块名。

    错误格式:
        File "...governance/__init__.py", line N, in <module>
          from zephyr.governance.xxx import Yyy
        ImportError: ...

    Returns:
        模块名（如 "xxx"），或 None
    """
    # 找到 __init__.py 中的 import 行
    lines = error.split("\n")
    for i, line in enumerate(lines):
        if "__init__.py" in line and "from zephyr.governance" in line:
            # 下一行是 import 语句
            if i + 1 < len(lines):
                import_line = lines[i + 1].strip()
                # 提取模块名: from zephyr.governance.xxx import Yyy
                match = re.match(r"from zephyr\.governance\.(\w+) import (\w+)", import_line)
                if match:
                    return match.group(1)  # 返回模块名
        # 也检查直接在 import 行的情况
        if "from zephyr.governance." in line and "import" in line:
            match = re.match(r"\s*from zephyr\.governance\.(\w+) import (\w+)", line)
            if match:
                return match.group(1)
    return None


def remove_module_from_init(module_name: str) -> bool:
    """从 __init__.py 中移除指定模块的 import 语句和 __all__ 条目。

    Returns:
        True 如果移除了内容
    """
    content = INIT_PY.read_text(encoding="utf-8")
    new_content = content

    # 移除所有 from zephyr.governance.<module_name> import ... 的行
    pattern = rf"from zephyr\.governance\.{module_name} import \w+\n?"
    new_content = re.sub(pattern, "", new_content)

    # 移除 __all__ 中的对应条目（驼峰命名）
    # 模块名转驼峰: momentum_factor -> MomentumFactor
    class_name = "".join(p.capitalize() for p in module_name.split("_"))
    # 匹配 "ClassName" 或 'ClassName'（可能带逗号和换行）
    new_content = re.sub(rf'["\']{re.escape(class_name)}["\'],?\s*\n?', "", new_content)

    if new_content != content:
        # 原子写入
        tmp_path = Path(str(INIT_PY) + f".{os.getpid()}.tmp")
        try:
            tmp_path.write_text(new_content, encoding="utf-8")
            os.replace(str(tmp_path), str(INIT_PY))
            return True
        except PermissionError:
            try:
                os.remove(str(tmp_path))
            except OSError:
                pass
    return False


def main() -> None:
    print("开始迭代清理 governance/__init__.py 中导入失败的模块...")
    print("=" * 60)

    removed_modules = []
    max_iterations = 50  # 最多 50 次迭代（50 个模块）

    for i in range(max_iterations):
        success, error = try_import()
        if success:
            print(f"\n[OK] import zephyr.governance 成功！（迭代 {i + 1} 次）")
            break

        # 提取失败的模块名
        module_name = extract_failed_module(error)
        if not module_name:
            print("[ERROR] 无法从错误信息中提取模块名:")
            print(f"  {error[:200]}")
            break

        print(f"  迭代 {i + 1}: 移除 {module_name}")
        removed_modules.append(module_name)

        # 从 __init__.py 中移除
        if not remove_module_from_init(module_name):
            print(f"    WARNING: 未在 __init__.py 中找到 {module_name}")
            break
    else:
        print(f"[WARNING] 达到最大迭代次数 {max_iterations}")

    print("\n" + "=" * 60)
    print(f"移除的模块: {len(removed_modules)}")
    for m in removed_modules:
        print(f"  - {m}")

    # 最终验证
    success, error = try_import()
    if success:
        print("\n[FINAL] import zephyr.governance 成功！")
    else:
        print("\n[FINAL] import zephyr.governance 仍然失败:")
        print(f"  {error[:300]}")

    # 保存移除清单
    output_path = PROJECT_ROOT / "removed_modules.json"
    import json

    output_path.write_text(json.dumps(removed_modules, indent=2), encoding="utf-8")
    print(f"\n移除清单已写入: {output_path}")


if __name__ == "__main__":
    main()
