# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
Layer 1 职责重叠问题全面修复脚本
"""
import os
from pathlib import Path
import yaml
from datetime import datetime

def fix_all_responsibility_issues():
    """修复所有职责重叠问题"""
    base_path = Path("d:/ZephyrAlpha/docs/02_FACTOR_LIBRARY/04_DATA_SOURCE")
    
    # 需要修复的文件及其正确的职责
    fixes = {
        # 数据质量 (Layer 1) - 9个文档
        'DATA_TESTING_FRAMEWORK/INDEX.md': '数据测试框架模块导航',
        'DATA_PROFILING/INDEX.md': '数据分析模块导航',
        'DATA_PERMISSION_MANAGEMENT/INDEX.md': '数据权限管理模块导航',
        'DATA_ORCHESTRATION_ENHANCED/INDEX.md': '数据编排增强模块导航',
        'DATA_OBSERVABILITY/INDEX.md': '数据可观测性模块导航',
        'DATA_MONITORING_ENHANCED/INDEX.md': '数据监控增强模块导航',
        'DATA_LINEAGE_TRACKING/INDEX.md': '数据血缘追踪模块导航',
        'DATA_CATALOG/INDEX.md': '数据目录模块导航',
        'SUPERCMD_CONNECTOR.md': 'SuperCMD命令行接口对接',
        
        # CONFIG MANAGEMENT - 模块导航 - 重复
        'CONFIG_MANAGEMENT/INDEX.md': '配置管理模块导航',
        
        # 数据质量 - 重复
        'DATA_ANOMALY_DETECTION/INDEX.md': '数据异常检测模块导航',
        'DATA_SYNC_REPLICATION/INDEX.md': '数据同步复制模块导航',
        
        # DATA ANOMALY DETECTION - 模块导航 - 重复
        # 已在上面修复
        
        # 数据源 - 重复
        'DATA_API_GATEWAY/INDEX.md': '数据API网关模块导航',
        'DATA_COMPRESSION_ARCHIVE/INDEX.md': '数据压缩归档模块导航',
        'DATA_FEDERATION/INDEX.md': '数据联邦模块导航',
        
        # DATA API GATEWAY - 模块导航 - 重复
        # 已在上面修复
        
        # 系统架构 - 重复
        'DATA_BACKUP_RECOVERY/INDEX.md': '数据备份恢复模块导航',
        'DATA_CONTRACT/INDEX.md': '数据契约模块导航',
        'DATA_LIFECYCLE_MANAGEMENT/INDEX.md': '数据生命周期管理模块导航',
        
        # 文档治理 - 重复
        # 已在上面修复
    }
    
    print("="*80)
    print("Layer 1 职责重叠问题全面修复")
    print("="*80)
    print(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    fixed_count = 0
    error_count = 0
    
    for file_path, new_responsibility in fixes.items():
        full_path = base_path / file_path
        
        if not full_path.exists():
            print(f"  ⚠️ 文件不存在: {file_path}")
            continue
            
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 提取YAML
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    yaml_data = yaml.safe_load(parts[1])
                    
                    # 更新职责
                    yaml_data['responsibility'] = new_responsibility
                    
                    # 重新生成YAML
                    yaml_str = yaml.dump(yaml_data, allow_unicode=True, sort_keys=False, default_flow_style=False)
                    
                    # 替换内容
                    new_content = f"---\n{yaml_str}---{parts[2]}"
                    
                    with open(full_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                        
                    print(f"  ✓ {file_path}: {new_responsibility}")
                    fixed_count += 1
                    
        except Exception as e:
            print(f"  ⚠️ 修复失败: {file_path} - {str(e)}")
            error_count += 1
            
    print()
    print(f"修复完成: {fixed_count} 个文件")
    print(f"失败: {error_count} 个文件")
    print("="*80)

if __name__ == "__main__":
    fix_all_responsibility_issues()
