"""快速锁定状态检查脚本"""
import yaml, subprocess
from pathlib import Path

ROOT = Path('D:/ZephyrAlpha')

print("=== 锁定状态全面检查 ===\n")

# 1. pre-commit hooks count
cfg = yaml.safe_load(open(ROOT / '.pre-commit-config.yaml', encoding='utf-8'))
hooks = [h for r in cfg['repos'] for h in r['hooks']]
local_hooks = [h for r in cfg['repos'] if r['repo'] == 'local' for h in r['hooks']]
community_hooks = [h for r in cfg['repos'] if r['repo'] != 'local' for h in r['hooks']]
print(f"[1] Pre-commit hooks: {len(hooks)} 个（本地 {len(local_hooks)} + 社区 {len(community_hooks)}）")
naming_hook = [h for h in hooks if 'naming' in h.get('id', '').lower() or 'C-10' in h.get('name', '')]
print(f"    C-10 命名 hook: {'✅ 已配置' if naming_hook else '❌ 未找到'}")

# 2. doc-naming-standard.md version
std = open(ROOT / 'docs/09_AUDIT/STANDARDS/doc-naming-standard.md', encoding='utf-8').read()
import re
ver = re.search(r'version:\s*(\S+)', std)
print(f"\n[2] doc-naming-standard.md: 版本 {ver.group(1) if ver else '未知'}")
track = 'single' if '单轨' in std else 'dual'
print(f"    命名体系: {'✅ 单轨标准（已统一）' if track == 'single' else '⚠️  双轨体系（旧版）'}")

# 3. AGENTS.md naming rule presence
agents = open(ROOT / 'AGENTS.md', encoding='utf-8').read()
has_naming_41 = 'kebab-case' in agents and '4.1' in agents or '新建.*\.md' in agents
has_naming_13 = '新建大写' in agents or '大写.*\.md' in agents
print(f"\n[3] AGENTS.md 命名规则:")
print(f"    4.1 操作限制: {'✅ 已包含小写规则' if 'kebab-case' in agents else '❌ 缺失'}")
print(f"    十三 禁止行为: {'✅ 已包含大写禁止项' if '新建大写' in agents else '❌ 缺失'}")

# 4. project-conventions.mdc
conv = open(ROOT / '.cursor/rules/project-conventions.mdc', encoding='utf-8').read()
print(f"\n[4] project-conventions.mdc:")
print(f"    命名规则: {'✅ 已包含' if 'kebab-case' in conv else '❌ 缺失'}")

# 5. Remaining uppercase .md files
result = subprocess.run(['python', 'scripts/tools/rename_uppercase_wave.py', '--dry-run'],
                       capture_output=True, text=True, cwd=str(ROOT))
remaining = re.search(r'发现 (\d+) 个', result.stdout)
count = int(remaining.group(1)) if remaining else -1
print(f"\n[5] 残留大写文件: {'✅ 0 个（已全部清除）' if count == 0 else f'⚠️  {count} 个待处理'}")

# 6. AGENTS.md mentions doc-naming-standard v2
print(f"\n[6] AGENTS.md 引用命名标准: {'✅ v2.0.0' if 'v2.0.0' in agents else '⚠️  版本引用缺失'}")

print("\n=== 汇总 ===")
all_ok = (
    len(naming_hook) > 0 and
    ver and ver.group(1) == '2.0.0' and
    track == 'single' and
    'kebab-case' in agents and
    '新建大写' in agents and
    'kebab-case' in conv and
    count == 0
)
print(f"整体状态: {'✅ 全部锁定' if all_ok else '⚠️  存在缺口'}")
