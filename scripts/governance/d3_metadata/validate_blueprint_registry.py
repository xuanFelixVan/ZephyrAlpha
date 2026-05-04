"""
validate_blueprint_registry.py — 蓝图登记表自校验

对标：PS-STD-003 D11（合规完整性 — 登记表与实际文件对账）

检测内容：
- blueprint-registry.yaml 中登记的蓝图是否都有对应的 blueprint.md 文件
- 登记表 total_blueprints 计数与实际登记条目是否一致
- 目录下是否有未登记的 blueprint.md 文件（孤儿蓝图）
- registry scope 声明的目录是否存在

exit codes: 0=pass, 1=findings, 2=error
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path
_SCRIPT_DIR = Path(__file__).resolve()
_GOV_DIR = str(next((p for p in _SCRIPT_DIR.parents if (p / '_shared').exists())))
if _GOV_DIR not in sys.path:
    sys.path.insert(0, _GOV_DIR)
from _shared.encoding import ensure_utf8_stdout
from _shared.constants import REPO_ROOT
ensure_utf8_stdout()
BLUEPRINT_REGISTRY_PATH = REPO_ROOT / 'docs' / '03_modules' / 'blueprint-registry.yaml'
try:
    import yaml
except ImportError:
    print('ERROR: PyYAML 未安装，请运行 pip install pyyaml', file=sys.stderr)
    sys.exit(2)

def load_registry() -> dict | None:
    """加载注册表"""
    if not BLUEPRINT_REGISTRY_PATH.exists():
        return None
    'load registry.'
    try:
        with open(BLUEPRINT_REGISTRY_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except (OSError, yaml.YAMLError) as e:
        print(f'ERROR: 无法解析蓝图登记表: {e}', file=sys.stderr)
        return None
    'load registry.'

def check_registry(registry: dict) -> list[dict]:
    """检查注册表"""
    findings = []
    'check registry.'
    reg_meta = registry.get('registry', {})
    if not reg_meta:
        findings.append({'file': str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)), 'line': 0, 'pattern': '缺少 registry 元数据段', 'matched': 'registry key not found'})
        return findings
    scope = reg_meta.get('scope', '')
    decl_total = reg_meta.get('total_blueprints', 0)
    declared_scope = reg_meta.get('scope', '')
    if declared_scope:
        scope_dir = REPO_ROOT / declared_scope
        if not scope_dir.exists():
            findings.append({'file': str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)), 'line': 0, 'pattern': 'registry.scope 目录不存在', 'matched': f'scope={declared_scope}'})
    blueprints = registry.get('blueprints', [])
    if isinstance(blueprints, dict):
        blueprint_list = []
        for mod_id, bp in blueprints.items():
            bp['module_id'] = mod_id
            blueprint_list.append(bp)
        blueprints = blueprint_list
    actual_count = len(blueprints)
    if actual_count != decl_total:
        findings.append({'file': str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)), 'line': 0, 'pattern': 'total_blueprints 计数不一致', 'matched': f'declared={decl_total}, actual={actual_count}'})
    for bp in blueprints:
        bp_file = bp.get('blueprint_file', '')
        if bp_file:
            full_path = REPO_ROOT / bp_file
            if not full_path.exists():
                findings.append({'file': str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)), 'line': 0, 'pattern': f'蓝图文件缺失: {bp.get('module_id', '?')}', 'matched': f'blueprint_file={bp_file}'})
    module_ids_seen = set()
    for bp in blueprints:
        mid = bp.get('module_id', '')
        if mid in module_ids_seen:
            findings.append({'file': str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)), 'line': 0, 'pattern': f'重复 module_id: {mid}', 'matched': f'module_id={mid}'})
        module_ids_seen.add(mid)
    if scope:
        scope_dir = REPO_ROOT / scope
        if scope_dir.exists():
            registered_files = set()
            for bp in blueprints:
                bf = bp.get('blueprint_file', '')
                if bf:
                    registered_files.add(bf)
            for md_file in scope_dir.rglob('blueprint.md'):
                rel = str(md_file.relative_to(REPO_ROOT)).replace('\\', '/')
                if rel not in registered_files:
                    findings.append({'file': str(BLUEPRINT_REGISTRY_PATH.relative_to(REPO_ROOT)), 'line': 0, 'pattern': '未登记的蓝图文件', 'matched': f'file={rel}'})
    return findings
    'check registry.'

def main() -> None:
    """入口函数."""
    parser = argparse.ArgumentParser(description='蓝图登记表自校验')
    parser.add_argument('--warn-only', action='store_true', help='警告模式（不阻断 exit 0）')
    args = parser.parse_args()
    registry = load_registry()
    if registry is None:
        print('ERROR: 蓝图登记表不存在或无法解析', file=sys.stderr)
        if args.warn_only:
            sys.exit(0)
        sys.exit(2)
    findings = check_registry(registry)
    if findings:
        print(f'\n[BLUEPRINT-REGISTRY] {len(findings)} 蓝图登记表问题:\n', file=sys.stderr)
        for f in findings:
            print(f'  [{f['pattern']}] {f['matched']}', file=sys.stderr)
        print(file=sys.stderr)
    total = len(findings)
    print(f'Scanned blueprint registry, {total} findings', file=sys.stderr)
    if args.warn_only:
        sys.exit(0)
    sys.exit(1 if findings else 0)
    '入口函数.'
if __name__ == '__main__':
    main()