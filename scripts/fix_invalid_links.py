import os
import re

def fix_invalid_links():
    """修复无效链接"""
    
    # 定义需要修复的INDEX.md文件和修复规则
    fixes = {
        'docs/INDEX.md': {
            'remove_links': [
                './02_FACTOR_LIBRARY/System_Manifest.md',
                './02_FACTOR_LIBRARY/01_STANDARDS/FACTOR_REGISTRY.md',
                './02_FACTOR_LIBRARY/04_DATA_SOURCE/README.md',
                './03_TRADING_TACTICS/09_RISK_RULES/RISK_RULE_ENGINE.md',
            ]
        },
        'docs/01_FRAMEWORK/INDEX.md': {
            'remove_links': [
                './STRESS_TESTING_SYSTEM_BLUEPRINT.md',
                './RAG_KNOWLEDGE_SYSTEM_BLUEPRINT.md',
                './COMPLIANCE_AUDIT_LOG_BLUEPRINT.md',
                './MODEL_COMPRESSION_BLUEPRINT.md',
                './DATA_VERSION_CONTROL_BLUEPRINT.md',
            ]
        },
        'docs/02_FACTOR_LIBRARY/INDEX.md': {
            'update_links': {
                './04_DATA_SOURCE/DATA_SOURCE_LAYER_GAP_ANALYSIS.md': './04_DATA_SOURCE/DATA_SOURCE_LAYER_GAP_ANALYSIS_V2.md'
            }
        },
        'docs/03_TRADING_TACTICS/INDEX.md': {
            'remove_links': [
                '../08_AI_GOVERNANCE/AI_Permissions.md',
                '../01_FRAMEWORK/HUMAN_AI_FLOW.md',
                '../../DOCUMENT_AUDIT_v5.3.md',
            ]
        },
        'docs/05_IMPLEMENTATION/05_TECHNICAL_SPECIFICATIONS/INDEX.md': {
            'remove_links': [
                '../09_ARCHIVE/TECHNICAL_SPECIFICATIONS/ECONOMIC_REGIME_ENGINE_TECHNICAL_SPECIFICATION_V1_ARCHIVED.md',
            ]
        },
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/INDEX.md': {
            'update_links': {
                '01_BLUEPRINTS/PORTFOLIO_OPTIMIZATION_BLUEPRINT.md': '01_BLUEPRINTS/STRATEGY_PORTFOLIO_OPTIMIZATION_BLUEPRINT.md'
            }
        },
        'docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/INDEX.md': {
            'remove_links': [
                '../../09_AUDIT/REPORTS/IMMEDIATE_ACTION_EXECUTION_REPORT_20260406.md',
            ]
        },
        'docs/08_KNOWLEDGE/INDEX.md': {
            'remove_links': [
                'BEST_PRACTICES/RISK_MANAGEMENT_BEST_PRACTICES.md',
                'BEST_PRACTICES/BACKTEST_BEST_PRACTICES.md',
                'FACTOR_LIBRARY/FACTOR_CASE_LIBRARY.md',
                'STRATEGY_LIBRARY/STRATEGY_CASE_LIBRARY.md',
                '../03_STRATEGY_ENGINE/INDEX.md',
                '../04_RISK_CONTROL/INDEX.md',
            ]
        },
        'docs/09_RESEARCH_INNOVATION/01_ai_research_lab/INDEX.md': {
            'remove_links': [
                './AI研究团队架构.md',
                './自动化研究流程.md',
                './研究成果评估.md',
                './研究员能力模型.md',
                './实验设计框架.md',
                './知识沉淀机制.md',
            ]
        },
        'docs/10_AI_WORKFLOW/INDEX.md': {
            'remove_links': [
                '../02_FACTOR_LIBRARY/System_Manifest.md',
            ]
        },
        'docs/10_GOVERNANCE_COMPLIANCE/01_internal_controls/INDEX.md': {
            'remove_links': [
                './风险控制框架.md',
                './合规管理制度.md',
                './内部审计制度.md',
                './监管合规清单.md',
                './合规检查流程.md',
                './审计追踪机制.md',
            ]
        },
        'docs/11_STRATEGIC_DECISION/01_asset_allocation/INDEX.md': {
            'remove_links': [
                './资产配置模型.md',
                './风险预算框架.md',
                './策略选择框架.md',
                './配置优化方法.md',
                './策略组合优化.md',
                './战略调整机制.md',
            ]
        },
    }
    
    print('=' * 80)
    print('修复无效链接')
    print('=' * 80)
    print()
    
    fixed_count = 0
    
    for index_file, fix_rules in fixes.items():
        if not os.path.exists(index_file):
            print(f'❌ 文件不存在: {index_file}')
            continue
        
        print(f'处理文件: {index_file}')
        
        # 读取文件内容
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 删除无效链接
        if 'remove_links' in fix_rules:
            for link_url in fix_rules['remove_links']:
                # 匹配Markdown链接格式: [text](url)
                pattern = rf'\[[^\]]+\]\({re.escape(link_url)}[^\)]*\)\s*\n?'
                content = re.sub(pattern, '', content)
                print(f'  删除链接: {link_url}')
        
        # 更新链接
        if 'update_links' in fix_rules:
            for old_url, new_url in fix_rules['update_links'].items():
                # 匹配Markdown链接格式: [text](url)
                pattern = rf'(\[[^\]]+\])\({re.escape(old_url)}\)'
                replacement = rf'\1({new_url})'
                content = re.sub(pattern, replacement, content)
                print(f'  更新链接: {old_url} -> {new_url}')
        
        # 如果内容有变化，保存文件
        if content != original_content:
            with open(index_file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'  ✅ 已保存修改')
            fixed_count += 1
        else:
            print(f'  ⚠️ 无需修改')
        
        print()
    
    print('=' * 80)
    print('修复完成')
    print('=' * 80)
    print(f'修复文件数: {fixed_count}')

if __name__ == '__main__':
    fix_invalid_links()
