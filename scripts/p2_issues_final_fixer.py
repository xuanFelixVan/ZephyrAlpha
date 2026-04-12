#!/usr/bin/env python

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
P2问题修复脚本
修复职责描述过短和缺少概述章节问题
"""

import re
import yaml
from pathlib import Path
from datetime import datetime

FACTOR_LIBRARY = Path(r'D:\ZephyrAlpha\docs\02_FACTOR_LIBRARY')

# 需要修复职责描述的文件
RESPONSIBILITY_FIX_FILES = {
    'SITEMAP.md': {
        'responsibility': [
            '因子库站点地图',
            '文档导航索引',
            '阅读路径指引'
        ],
        'title': '因子库站点地图',
        'overview': '提供因子库所有文档的站点地图和导航索引，帮助用户快速定位所需文档。'
    },
    r'05_BACKTEST\BACKTEST_REORGANIZATION.md': {
        'responsibility': [
            '回测模块重组',
            '目录结构优化',
            '迁移检查清单'
        ],
        'title': '回测模块重组文档',
        'overview': '记录回测模块的重组过程，包括目录结构优化和迁移检查清单。'
    },
    r'10_MANUAL\FAQ.md': {
        'responsibility': [
            '常见问题解答',
            '使用指南支持',
            '故障排查帮助'
        ],
        'title': '常见问题解答',
        'overview': '提供因子库使用过程中的常见问题解答和故障排查帮助。'
    }
}

# 需要添加概述章节的文件
OVERVIEW_ADD_FILES = {
    'SITEMAP.md': '提供因子库所有文档的站点地图和导航索引，帮助用户快速定位所需文档。',
    r'00_GOVERNANCE\README.md': '治理模块的说明文档，包含因子库治理相关的规范和流程。',
    r'02_ALPHA_FACTORS_INDEX\README.md': 'Alpha因子索引模块的说明文档，包含因子分类和索引信息。',
    r'05_BACKTEST\BACKTEST_REORGANIZATION.md': '记录回测模块的重组过程，包括目录结构优化和迁移检查清单。',
    r'06_REGISTRY\README.md': '注册表模块的说明文档，包含因子注册和管理相关信息。',
    r'07_FACTOR_MONITORING\README.md': '因子监控模块的说明文档，包含因子性能监控和预警相关信息。',
    r'09_AUDIT\README.md': '审计模块的说明文档，包含文档治理审计相关信息。',
    r'10_MANUAL\FAQ.md': '提供因子库使用过程中的常见问题解答和故障排查帮助。',
    r'04_DATA_SOURCE\02_SCHEDULER\README.md': '数据调度模块的说明文档，包含数据采集调度相关信息。',
    r'04_DATA_SOURCE\03_CLEANING\README.md': '数据清洗模块的说明文档，包含数据清洗流程和规则相关信息。'
}

def parse_yaml_safe(content):
    """安全解析YAML头部"""
    yaml_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if yaml_match:
        yaml_content = yaml_match.group(1)
        body_content = content[yaml_match.end():]
        
        try:
            yaml_dict = yaml.safe_load(yaml_content)
            return yaml_dict if yaml_dict else {}, body_content
        except:
            return {}, body_content
    
    return {}, content

def clean_yaml_header(yaml_dict, new_responsibility):
    """清理并更新YAML头部"""
    # 移除重复的responsibility字段
    cleaned_yaml = {}
    
    for key, value in yaml_dict.items():
        if key != 'responsibility':
            cleaned_yaml[key] = value
    
    # 添加新的responsibility
    cleaned_yaml['responsibility'] = new_responsibility
    
    return cleaned_yaml

def build_yaml_header(yaml_dict):
    """构建YAML头部字符串"""
    yaml_str = '---\n'
    for key, value in yaml_dict.items():
        if isinstance(value, list):
            yaml_str += f'{key}:\n'
            for item in value:
                yaml_str += f'  - {item}\n'
        elif isinstance(value, str):
            yaml_str += f'{key}: {value}\n'
        else:
            yaml_str += f'{key}: {value}\n'
    yaml_str += '---\n'
    
    return yaml_str

def add_overview_section(body, overview_text):
    """添加概述章节"""
    # 检查是否已有概述章节
    if '## 📋 概述' in body or '## 概述' in body:
        return body
    
    # 找到第一个标题
    title_match = re.search(r'^#\s+.+$', body, re.MULTILINE)
    if title_match:
        # 在第一个标题后添加概述章节
        insert_pos = title_match.end()
        overview_section = f'\n\n## 📋 概述\n\n{overview_text}\n'
        return body[:insert_pos] + overview_section + body[insert_pos:]
    else:
        # 在开头添加概述章节
        overview_section = f'## 📋 概述\n\n{overview_text}\n\n'
        return overview_section + body

def fix_responsibility_issues():
    """修复职责描述问题"""
    print("\n修复职责描述问题...")
    
    fixed_count = 0
    
    for file_path, fix_info in RESPONSIBILITY_FIX_FILES.items():
        full_path = FACTOR_LIBRARY / file_path
        
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 解析YAML头部
            yaml_dict, body = parse_yaml_safe(content)
            
            # 清理并更新YAML头部
            cleaned_yaml = clean_yaml_header(yaml_dict, fix_info['responsibility'])
            
            # 构建新的YAML头部
            new_yaml_header = build_yaml_header(cleaned_yaml)
            
            # 清理body中的重复YAML字段
            body = re.sub(r'^---\|\s*responsibility:.*?---\|', '', body, flags=re.DOTALL | re.MULTILINE)
            body = re.sub(r'^responsibility:\s*\n\s*-\s*[^\n]+', '', body, flags=re.MULTILINE)
            body = re.sub(r'^module_id:\s*[^\n]+', '', body, flags=re.MULTILINE)
            body = re.sub(r'^---\|.*?---\|', '', body, flags=re.DOTALL | re.MULTILINE)
            body = re.sub(r'\n{3,}', '\n\n', body)
            
            # 添加概述章节
            body = add_overview_section(body, fix_info['overview'])
            
            # 重新构建文件内容
            new_content = new_yaml_header + body
            
            # 写回文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"修复: {file_path}")
            fixed_count += 1
    
    return fixed_count

def add_overview_sections():
    """添加概述章节"""
    print("\n添加概述章节...")
    
    fixed_count = 0
    
    for file_path, overview_text in OVERVIEW_ADD_FILES.items():
        full_path = FACTOR_LIBRARY / file_path
        
        if full_path.exists():
            with open(full_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否已有概述章节
            if '## 📋 概述' in content or '## 概述' in content:
                continue
            
            # 解析YAML头部
            yaml_dict, body = parse_yaml_safe(content)
            
            # 添加概述章节
            body = add_overview_section(body, overview_text)
            
            # 重新构建文件内容
            if yaml_dict:
                yaml_header = build_yaml_header(yaml_dict)
                new_content = yaml_header + body
            else:
                new_content = body
            
            # 写回文件
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"添加概述: {file_path}")
            fixed_count += 1
    
    return fixed_count

def main():
    """主函数"""
    print("=" * 80)
    print("P2问题修复")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 修复职责描述问题
    responsibility_fixed = fix_responsibility_issues()
    
    # 添加概述章节
    overview_added = add_overview_sections()
    
    print("\n" + "=" * 80)
    print("修复完成")
    print("=" * 80)
    print(f"修复职责描述: {responsibility_fixed}个")
    print(f"添加概述章节: {overview_added}个")
    print(f"总修复文件: {responsibility_fixed + overview_added}个")

if __name__ == '__main__':
    main()
