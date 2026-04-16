#!/usr/bin/env python3
"""
真源卫兵 (Source Guard) - Pre-commit Hook
功能：防止双YAML、重复module_id、frontmatter字段缺失
版本：1.0.0
"""

import io
import re
import sys
import yaml
from pathlib import Path

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

REQUIRED_FIELDS = {'module_id', 'version', 'status', 'owner'}

def check_double_yaml(content: str) -> bool:
    """检查是否存在双YAML块"""
    yaml_blocks = list(re.finditer(r'^---\s*\n', content, re.MULTILINE))
    return len(yaml_blocks) > 1

def check_double_module_id(content: str) -> bool:
    """检查是否存在双module_id"""
    module_ids = re.findall(r'^module_id:\s*(.+)$', content, re.MULTILINE)
    return len(module_ids) > 1

def check_frontmatter_fields(content: str) -> list:
    """检查frontmatter必需字段"""
    missing = []
    for field in REQUIRED_FIELDS:
        pattern = rf'^{field}:\s*\S+'
        if not re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            missing.append(field)
    return missing

def check_yaml_validity(content: str) -> tuple:
    """检查YAML是否可解析"""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return False, "无法找到YAML frontmatter"

    try:
        yaml_content = match.group(1)
        data = yaml.safe_load(yaml_content)
        if data is None:
            return False, "YAML解析为空"
        if isinstance(data, list):
            return False, "YAML为列表类型(应为字典)"
        if not isinstance(data, dict):
            return False, f"YAML类型错误: {type(data)}"
        return True, ""
    except Exception as e:
        return False, f"YAML解析错误: {e}"

def validate_file(file_path: Path) -> list:
    """验证单个文件"""
    errors = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return [f"无法读取文件: {e}"]

    # 检查双YAML
    if check_double_yaml(content):
        errors.append("❌ 双YAML frontmatter")

    # 检查双module_id
    if check_double_module_id(content):
        errors.append("❌ 双module_id")

    # 检查YAML有效性
    valid, error_msg = check_yaml_validity(content)
    if not valid:
        errors.append(f"❌ {error_msg}")
    else:
        # 检查必需字段
        missing = check_frontmatter_fields(content)
        if missing:
            errors.append(f"❌ 缺少字段: {', '.join(missing)}")

    return errors

def main():
    """主函数 - 检查暂存文件"""
    import subprocess

    # 获取暂存的 .md 文件
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
            capture_output=True, text=True, cwd=Path(__file__).resolve().parents[2]
        )
        staged_files = [
            f for f in result.stdout.strip().split('\n')
            if f.endswith('.md') and f.startswith('docs/')
        ]
    except Exception:
        print("⚠️  无法获取git暂存文件列表")
        return 0

    if not staged_files:
        return 0

    print("🔍 真源卫兵检查中...")
    print(f"   检查 {len(staged_files)} 个文件\n")

    has_error = False
    for rel_path in staged_files:
        file_path = Path(__file__).resolve().parents[2] / rel_path
        if not file_path.exists():
            continue

        errors = validate_file(file_path)
        if errors:
            has_error = True
            print(f"📄 {rel_path}")
            for error in errors:
                print(f"   {error}")
            print()

    if has_error:
        print("=" * 60)
        print("❌ 真源卫兵拦截了提交!")
        print("   请修复上述问题后再提交。")
        print("=" * 60)
        return 1
    else:
        print("✅ 真源卫兵检查通过!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
