# -*- coding: utf-8 -*-
"""
INDEX.md职责描述优化脚本
按照专业量化机构五大原则，为每个INDEX.md添加独特的职责描述
"""

import os
import re
from pathlib import Path
from datetime import datetime

# 模块职责映射表
MODULE_RESPONSIBILITIES = {
    '01_MONITORING': {
        'responsibility': [
            '索引文档、导航目录',
            '监控模块文档索引',
            '系统监控和指标展示相关文档导航'
        ],
        'applicable_scope': '监控管理模块'
    },
    '02_ALERTING': {
        'responsibility': [
            '索引文档、导航目录',
            '告警模块文档索引',
            '告警规则配置和通知管理相关文档导航'
        ],
        'applicable_scope': '告警管理模块'
    },
    '03_AUTH': {
        'responsibility': [
            '索引文档、导航目录',
            '认证模块文档索引',
            '用户认证和权限管理相关文档导航'
        ],
        'applicable_scope': '认证管理模块'
    },
    '04_API_DOCS': {
        'responsibility': [
            '索引文档、导航目录',
            'API文档模块索引',
            'API接口文档和开发者指南相关文档导航'
        ],
        'applicable_scope': 'API文档模块'
    },
    '05_BACKTEST_UI': {
        'responsibility': [
            '索引文档、导航目录',
            '回测UI模块文档索引',
            '回测界面和结果展示相关文档导航'
        ],
        'applicable_scope': '回测UI模块'
    },
    '06_REPORTING': {
        'responsibility': [
            '索引文档、导航目录',
            '报告模块文档索引',
            '报告生成和数据可视化相关文档导航'
        ],
        'applicable_scope': '报告管理模块'
    },
    '07_AUDIT_LOG': {
        'responsibility': [
            '索引文档、导航目录',
            '审计日志模块文档索引',
            '审计日志记录和查询相关文档导航'
        ],
        'applicable_scope': '审计日志模块'
    },
    '08_MOBILE_PUSH': {
        'responsibility': [
            '索引文档、导航目录',
            '移动推送模块文档索引',
            '移动端推送通知相关文档导航'
        ],
        'applicable_scope': '移动推送模块'
    },
    '09_TRADING_JOURNAL': {
        'responsibility': [
            '索引文档、导航目录',
            '交易日志模块文档索引',
            '交易记录和日志管理相关文档导航'
        ],
        'applicable_scope': '交易日志模块'
    },
    '10_CONFIG_MANAGEMENT': {
        'responsibility': [
            '索引文档、导航目录',
            '配置管理模块文档索引',
            '系统配置和参数管理相关文档导航'
        ],
        'applicable_scope': '配置管理模块'
    },
    '11_USER_PREFERENCES': {
        'responsibility': [
            '索引文档、导航目录',
            '用户偏好模块文档索引',
            '用户设置和个性化配置相关文档导航'
        ],
        'applicable_scope': '用户偏好模块'
    },
    '12_SYSTEM_STATUS': {
        'responsibility': [
            '索引文档、导航目录',
            '系统状态模块文档索引',
            '系统健康检查和状态监控相关文档导航'
        ],
        'applicable_scope': '系统状态模块'
    },
    '13_DATA_MANAGEMENT': {
        'responsibility': [
            '索引文档、导航目录',
            '数据管理模块文档索引',
            '数据导入导出和数据治理相关文档导航'
        ],
        'applicable_scope': '数据管理模块'
    },
    '14_STRATEGY_MANAGEMENT': {
        'responsibility': [
            '索引文档、导航目录',
            '策略管理模块文档索引',
            '策略配置和策略库管理相关文档导航'
        ],
        'applicable_scope': '策略管理模块'
    },
    '15_PERMISSION_MANAGEMENT': {
        'responsibility': [
            '索引文档、导航目录',
            '权限管理模块文档索引',
            '权限配置和角色管理相关文档导航'
        ],
        'applicable_scope': '权限管理模块'
    },
    '16_API_RATE_LIMITING': {
        'responsibility': [
            '索引文档、导航目录',
            'API限流模块文档索引',
            'API访问控制和流量管理相关文档导航'
        ],
        'applicable_scope': 'API限流模块'
    },
    '17_DOCUMENTATION_CENTER': {
        'responsibility': [
            '索引文档、导航目录',
            '文档中心模块文档索引',
            '文档管理和知识库相关文档导航'
        ],
        'applicable_scope': '文档中心模块'
    },
    '18_KNOWLEDGE_BASE': {
        'responsibility': [
            '索引文档、导航目录',
            '知识库模块文档索引',
            '知识管理和经验沉淀相关文档导航'
        ],
        'applicable_scope': '知识库模块'
    },
    '19_CI_CD_INTEGRATION': {
        'responsibility': [
            '索引文档、导航目录',
            'CI/CD集成模块文档索引',
            '持续集成和部署相关文档导航'
        ],
        'applicable_scope': 'CI/CD集成模块'
    },
    '20_DATA_BACKUP': {
        'responsibility': [
            '索引文档、导航目录',
            '数据备份模块文档索引',
            '数据备份和恢复相关文档导航'
        ],
        'applicable_scope': '数据备份模块'
    },
    '21_ONLINE_RESEARCH_ENVIRONMENT': {
        'responsibility': [
            '索引文档、导航目录',
            '在线研究环境模块文档索引',
            '研究环境和工具集成相关文档导航'
        ],
        'applicable_scope': '在线研究环境模块'
    },
    '22_PARAMETER_OPTIMIZATION': {
        'responsibility': [
            '索引文档、导航目录',
            '参数优化模块文档索引',
            '参数调优和优化算法相关文档导航'
        ],
        'applicable_scope': '参数优化模块'
    },
    '23_LIVE_TRADING_INTERFACE': {
        'responsibility': [
            '索引文档、导航目录',
            '实盘交易接口模块文档索引',
            '实盘交易和订单管理相关文档导航'
        ],
        'applicable_scope': '实盘交易接口模块'
    }
}

def update_index_responsibility(index_file):
    """更新INDEX.md的职责描述"""
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除BOM字符
        content = content.lstrip('\ufeff')
        
        # 提取模块名称（改进版）
        file_path_str = str(index_file)
        parts = file_path_str.split(os.sep)
        
        # 查找最后一个包含两位数字开头的目录名（排除08_HUMAN_AI_INTERFACE）
        module_name = None
        for part in reversed(parts):
            if re.match(r'^\d{2}_', part) and part != '08_HUMAN_AI_INTERFACE':
                module_name = part
                break
        
        if not module_name:
            print(f"[SKIP] {index_file.name} - 无法识别模块名称")
            return False
        
        # 检查是否在映射表中
        if module_name not in MODULE_RESPONSIBILITIES:
            print(f"[SKIP] {index_file.name} - 模块 {module_name} 不在映射表中")
            return False
        
        # 获取新的职责描述
        new_resp = MODULE_RESPONSIBILITIES[module_name]
        
        # 更新YAML头部
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            print(f"[SKIP] {index_file.name} - 未找到YAML头部")
            return False
        
        yaml_content = yaml_match.group(1)
        
        # 替换responsibility字段
        responsibility_str = '\n'.join([f"  - {r}" for r in new_resp['responsibility']])
        yaml_content = re.sub(
            r'responsibility:\s*\n(  - .*\n)+',
            f'responsibility:\n{responsibility_str}\n',
            yaml_content
        )
        
        # 替换applicable_scope字段
        yaml_content = re.sub(
            r'applicable_scope:.*\n',
            f"applicable_scope: {new_resp['applicable_scope']}\n",
            yaml_content
        )
        
        # 更新last_updated
        yaml_content = re.sub(
            r'last_updated:.*\n',
            f"last_updated: {datetime.now().strftime('%Y-%m-%d')}\n",
            yaml_content
        )
        
        # 重新构建文档内容
        new_content = f"---\n{yaml_content}---\n{content[yaml_match.end():]}"
        
        # 写入文件
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"[OK] {index_file.name} - 职责描述已更新")
        return True
    
    except Exception as e:
        print(f"[ERROR] {index_file.name} - {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("INDEX.md职责描述优化")
    print("=" * 80)
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"执行标准: 专业量化机构五大原则")
    print()
    
    # 扫描所有INDEX.md文件
    layer_path = Path('docs/08_HUMAN_AI_INTERFACE')
    index_files = list(layer_path.rglob('INDEX.md'))
    
    print(f"找到 {len(index_files)} 个INDEX.md文件")
    print()
    
    # 更新每个文件
    success_count = 0
    for index_file in index_files:
        if update_index_responsibility(index_file):
            success_count += 1
    
    print()
    print("=" * 80)
    print(f"优化完成: {success_count}/{len(index_files)} 个文件已更新")
    print("=" * 80)

if __name__ == '__main__':
    main()
