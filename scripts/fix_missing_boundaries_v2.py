import os
import re
from datetime import datetime

blueprints_dir = r'd:\ZephyrAlpha\docs\05_IMPLEMENTATION\06_CONSTRUCTION_DOCS\01_BLUEPRINTS'

files_to_fix = [
    'DATA_ORCHESTRATION_SYSTEM_BLUEPRINT.md',
    'DATA_QUALITY_MONITORING_BLUEPRINT.md',
    'DATA_SECURITY_COMPLIANCE_BLUEPRINT.md',
    'DATA_STANDARDIZATION_ENGINE_BLUEPRINT.md',
    'DATA_SUBSCRIPTION_SERVICE_BLUEPRINT.md',
    'DATA_SOURCE_MANAGEMENT_BLUEPRINT.md',
    'DATA_VERSION_CONTROL_BLUEPRINT.md',
    'DYNAMIC_ASSET_ALLOCATION_BLUEPRINT.md',
    'DYNAMIC_CORRELATION_MODELING_BLUEPRINT.md',
]

module_info = {
    'DATA_ORCHESTRATION_SYSTEM': ('数据调度系统', '工作流编排', '任务调度'),
    'DATA_QUALITY_MONITORING': ('数据质量监控', '质量规则', '质量评分'),
    'DATA_SECURITY_COMPLIANCE': ('数据安全合规', '安全策略', '合规检查'),
    'DATA_STANDARDIZATION_ENGINE': ('数据标准化引擎', '标准定义', '数据转换'),
    'DATA_SUBSCRIPTION_SERVICE': ('数据订阅服务', '数据推送', '订阅管理'),
    'DATA_SOURCE_MANAGEMENT': ('数据源管理', '数据源注册', '连接管理'),
    'DATA_VERSION_CONTROL': ('数据版本控制', '版本管理', '变更追踪'),
    'DYNAMIC_ASSET_ALLOCATION': ('动态资产配置', '资产权重调整', '市场环境适应'),
    'DYNAMIC_CORRELATION_MODELING': ('动态相关性建模', '相关性估计', '时变相关'),
}

def add_boundary(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    
    if re.search(r'>\s*\*\*职责边界\*\*', content):
        return False, '已有职责边界'
    
    filename = os.path.basename(file_path)
    module_name = filename.replace('_BLUEPRINT.md', '')
    
    if module_name in module_info:
        resp1, resp2, resp3 = module_info[module_name]
    else:
        resp1, resp2, resp3 = '本模块核心功能', '模块实现', '质量保证'
    
    boundary_text = f'''
> **职责边界**: 
> - ✅ 本文档负责：{resp1}、{resp2}、{resp3}
> - ❌ 本文档不负责：其他模块职责（由各模块文档负责）

'''
    
    core_match = re.search(r'(##\s*核心定位\s*\n)', content)
    if core_match:
        insert_pos = core_match.end()
        new_content = content[:insert_pos] + boundary_text + content[insert_pos:]
    else:
        yaml_end = re.search(r'---\s*[\r\n]+', content)
        if yaml_end:
            insert_pos = yaml_end.end()
            new_content = content[:insert_pos] + '\n## 核心定位\n' + boundary_text + content[insert_pos:]
        else:
            new_content = boundary_text + content
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    return True, '已添加职责边界'

print('='*80)
print('添加缺失职责边界')
print('='*80)
print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
print()

fixed_count = 0
for file in files_to_fix:
    file_path = os.path.join(blueprints_dir, file)
    if os.path.exists(file_path):
        success, msg = add_boundary(file_path)
        if success:
            fixed_count += 1
            print(f'✓ {file}: {msg}')
        else:
            print(f'- {file}: {msg}')
    else:
        print(f'✗ {file}: 文件不存在')

print(f'\n修复完成: {fixed_count}个文件')
