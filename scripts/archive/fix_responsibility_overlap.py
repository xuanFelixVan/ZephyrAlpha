#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
P1级问题修复脚本：修复职责描述重叠
为每个BLUEPRINT文件添加独特的职责描述
"""

import re
from pathlib import Path
from datetime import datetime

class ResponsibilityFixer:
    def __init__(self, layer_path):
        self.layer_path = Path(layer_path)
        self.stats = {
            'total_files': 0,
            'fixed_files': 0,
            'errors': []
        }
        
        # 职责描述映射表
        self.responsibility_map = {
            'MONITORING_DASHBOARD_BLUEPRINT': [
                '系统监控仪表板设计',
                '实时监控系统运行状态',
                '关键指标可视化展示',
                '性能监控和告警展示'
            ],
            'ALERTING_SYSTEM_BLUEPRINT': [
                '告警通知系统设计',
                '多渠道告警推送',
                '告警规则配置和管理',
                '告警路由和分组'
            ],
            'AUTH_SYSTEM_BLUEPRINT': [
                '用户认证授权系统设计',
                '身份验证和权限管理',
                '会话管理和安全控制',
                '多因素认证支持'
            ],
            'API_DOCS_BLUEPRINT': [
                'API文档系统设计',
                '自动生成API文档',
                '交互式API测试界面',
                '文档版本管理'
            ],
            'BACKTEST_UI_BLUEPRINT': [
                '回测用户界面设计',
                '回测参数配置',
                '回测结果可视化',
                '历史回测管理'
            ],
            'REPORTING_BLUEPRINT': [
                '报告生成系统设计',
                '自动化报告生成',
                '报告模板管理',
                '报告分发和归档'
            ],
            'AUDIT_LOG_BLUEPRINT': [
                '审计日志系统设计',
                '操作日志记录',
                '日志查询和分析',
                '合规性审计支持'
            ],
            'MOBILE_PUSH_BLUEPRINT': [
                '移动推送系统设计',
                '多平台消息推送',
                '推送策略管理',
                '推送效果统计'
            ],
            'TRADING_JOURNAL_BLUEPRINT': [
                '交易日志系统设计',
                '交易记录管理',
                '交易分析和统计',
                '交易策略评估'
            ],
            'CONFIG_MANAGEMENT_BLUEPRINT': [
                '配置管理系统设计',
                '动态配置管理',
                '配置版本控制',
                '配置热更新'
            ],
            'USER_PREFERENCES_BLUEPRINT': [
                '用户偏好设置系统设计',
                '个性化配置管理',
                '主题和布局定制',
                '通知偏好设置'
            ],
            'SYSTEM_STATUS_BLUEPRINT': [
                '系统状态展示设计',
                '系统健康检查',
                '服务状态监控',
                '系统信息展示'
            ],
            'DATA_MANAGEMENT_BLUEPRINT': [
                '数据管理系统设计',
                '数据导入导出',
                '数据备份恢复',
                '数据质量检查'
            ],
            'STRATEGY_MANAGEMENT_BLUEPRINT': [
                '策略管理系统设计',
                '策略配置和部署',
                '策略版本管理',
                '策略性能监控'
            ],
            'PERMISSION_MANAGEMENT_BLUEPRINT': [
                '权限管理系统设计',
                '角色权限配置',
                '资源访问控制',
                '权限审计日志'
            ],
            'API_RATE_LIMITING_BLUEPRINT': [
                'API限流系统设计',
                '请求频率限制',
                '流量控制策略',
                '限流规则配置'
            ],
            'DOCUMENTATION_CENTER_BLUEPRINT': [
                '文档中心系统设计',
                '文档组织和导航',
                '文档搜索功能',
                '文档版本管理'
            ],
            'KNOWLEDGE_BASE_BLUEPRINT': [
                '知识库系统设计',
                '知识管理和检索',
                '知识图谱构建',
                '知识共享机制'
            ],
            'CI_CD_INTEGRATION_BLUEPRINT': [
                'CI/CD集成系统设计',
                '自动化构建流程',
                '持续集成配置',
                '部署流水线管理'
            ],
            'DATA_BACKUP_BLUEPRINT': [
                '数据备份系统设计',
                '自动备份策略',
                '备份存储管理',
                '灾难恢复支持'
            ],
            'ONLINE_RESEARCH_ENVIRONMENT_BLUEPRINT': [
                '在线研究环境设计',
                '交互式研究工具',
                '研究资源管理',
                '协作研究支持'
            ],
            'PARAMETER_OPTIMIZATION_BLUEPRINT': [
                '参数优化系统设计',
                '参数搜索算法',
                '优化结果分析',
                '参数调优工具'
            ],
            'LIVE_TRADING_INTERFACE_BLUEPRINT': [
                '实盘交易界面设计',
                '实时交易监控',
                '订单管理界面',
                '风险控制展示'
            ]
        }
    
    def fix_all(self):
        """修复所有BLUEPRINT文件的职责描述"""
        print("=" * 80)
        print("P1级问题修复：修复职责描述重叠")
        print("=" * 80)
        print(f"修复范围: {self.layer_path}")
        print()
        
        blueprint_files = list(self.layer_path.rglob('*_BLUEPRINT.md'))
        self.stats['total_files'] = len(blueprint_files)
        
        print(f"找到 {len(blueprint_files)} 个BLUEPRINT文件")
        print()
        
        for blueprint_file in blueprint_files:
            self.fix_blueprint(blueprint_file)
        
        self.print_stats()
    
    def fix_blueprint(self, blueprint_file):
        """修复单个BLUEPRINT文件的职责描述"""
        try:
            with open(blueprint_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 提取文件名关键词
            file_key = blueprint_file.stem
            
            # 获取对应的职责描述
            if file_key in self.responsibility_map:
                responsibilities = self.responsibility_map[file_key]
                
                # 更新职责描述
                content = self.update_responsibility(content, responsibilities)
                
                if content != original_content:
                    with open(blueprint_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.stats['fixed_files'] += 1
                    print(f"✅ 已修复: {blueprint_file.relative_to(self.layer_path)}")
                else:
                    print(f"⏭️  跳过: {blueprint_file.relative_to(self.layer_path)} (无需修改)")
            else:
                print(f"⚠️  警告: {blueprint_file.relative_to(self.layer_path)} (未找到职责映射)")
            
        except Exception as e:
            self.stats['errors'].append({
                'file': str(blueprint_file),
                'error': str(e)
            })
            print(f"❌ 错误: {blueprint_file.relative_to(self.layer_path)} - {e}")
    
    def update_responsibility(self, content, responsibilities):
        """更新职责描述"""
        # 查找YAML头部
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
            
            # 构建新的职责描述
            new_responsibility = "responsibility:\n"
            for resp in responsibilities:
                new_responsibility += f"  - {resp}\n"
            
            # 替换旧的职责描述
            if 'responsibility:' in yaml_content:
                # 查找并替换职责描述
                yaml_content = re.sub(
                    r'responsibility:\s*\n((?:\s+-.*\n)+)',
                    new_responsibility,
                    yaml_content
                )
            else:
                # 添加职责描述
                yaml_content += "\n" + new_responsibility
            
            # 重新构建内容
            content = '---\n' + yaml_content + '---' + content[yaml_match.end():]
        
        return content
    
    def print_stats(self):
        """输出统计信息"""
        print()
        print("=" * 80)
        print("修复统计")
        print("=" * 80)
        print(f"总文件数: {self.stats['total_files']}")
        print(f"修复文件数: {self.stats['fixed_files']}")
        print(f"错误数: {len(self.stats['errors'])}")
        
        if self.stats['errors']:
            print()
            print("错误详情:")
            for error in self.stats['errors']:
                print(f"  - {error['file']}: {error['error']}")


def main():
    layer_path = Path(r"D:\ZephyrAlpha\docs\08_HUMAN_AI_INTERFACE")
    
    fixer = ResponsibilityFixer(layer_path)
    fixer.fix_all()
    
    print()
    print("=" * 80)
    print("修复完成！")
    print("=" * 80)


if __name__ == '__main__':
    main()
