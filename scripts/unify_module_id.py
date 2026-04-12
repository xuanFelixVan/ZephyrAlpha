#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
统一module_id命名风格工具

功能：
1. 检测module_id命名风格不一致的文档
2. 统一为标准格式: {MODULE_NAME}_BLUEPRINT_001
3. 生成修复报告

使用方法：
    python unify_module_id.py [目录路径] [--dry-run]

示例：
    python unify_module_id.py docs/01_FRAMEWORK --dry-run
    python unify_module_id.py docs/01_FRAMEWORK
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple


class ModuleIdUnifier:
    """module_id命名统一器"""
    
    MODULE_ID_MAPPING = {
        'FRAMEWORK_TECH_STACK_001': 'TECH_STACK_001',
        'FRAMEWORK_RISK_MONITORING_001': 'REALTIME_RISK_MONITORING_BLUEPRINT_001',
        'FRAMEWORK_MODULE_RESPONSIBILITY_001': 'MODULE_RESPONSIBILITY_BOUNDARIES_001',
        'FRAMEWORK_MARKET_REGIME_001': 'MARKET_REGIME_001',
        'FRAMEWORK_COMPLIANCE_001': 'COMPLIANCE_MONITORING_SYSTEM_BLUEPRINT_001',
        'FRAMEWORK_AI_PERMISSIONS_001': 'AI_PERMISSIONS_001',
        'FRAMEWORK_DISASTER_RECOVERY_001': 'DISASTER_RECOVERY_BLUEPRINT_001',
        'FRAMEWORK_DATA_QUALITY_001': 'DATA_QUALITY_MONITORING_BLUEPRINT_001',
        'FRAMEWORK_DATA_LAYER_001': 'DATA_LAYER_IMPLEMENTATION_BLUEPRINT_001',
        'FRAMEWORK_AI_AUTO_001': 'AI_STRATEGY_AUTOMATION_BLUEPRINT_001',
        'FRAMEWORK_EXPLAIN_001': 'AI_EXPLAINABILITY_TOOLKIT_BLUEPRINT_001',
        'FRAMEWORK_ADAPTIVE_001': 'ADAPTIVE_MODEL_SYSTEM_BLUEPRINT_001',
        'FRAMEWORK_ARCH_001': 'ARCHITECTURE_001',
        'FRAMEWORK_README_001': 'FRAMEWORK_README_001',
        'FRAMEWORK_PROF_ARCH_001': 'PROFESSIONAL_MULTI_TIMEFRAME_ARCHITECTURE_001',
        'FRAMEWORK_IMPL_BLUEPRINT_001': 'PROFESSIONAL_IMPLEMENTATION_BLUEPRINT_001',
        'FRAMEWORK_PERSONAL_DEV_001': 'PERSONAL_DEVELOPMENT_BLUEPRINT_001',
        'FRAMEWORK_ACCELERATION_001': 'IMPLEMENTATION_ACCELERATION_BLUEPRINT_001',
        'FRAMEWORK_CRITICAL_MODULES_001': 'CRITICAL_MODULES_IMPLEMENTATION_BLUEPRINT_001',
        'FRAMEWORK_MIGRATION_001': 'ARCHITECTURE_MIGRATION_PLAN_001',
        'FRAMEWORK_ARCH_AUDIT_001': 'ARCHITECTURE_AUDIT_REPORT_001',
    }
    
    def __init__(self, root_dir: str, dry_run: bool = False):
        self.root_dir = Path(root_dir)
        self.dry_run = dry_run
        self.results = {
            'total_files': 0,
            'updated_files': 0,
            'skipped_files': 0,
            'failed_files': 0,
            'details': []
        }
    
    def get_current_module_id(self, content: str) -> str:
        """获取当前module_id"""
        match = re.search(r'^module_id:\s*(.+)$', content, re.MULTILINE)
        return match.group(1) if match else None
    
    def unify_module_id(self, file_path: Path) -> Dict:
        """统一单个文件的module_id"""
        result = {
            'file': str(file_path.relative_to(self.root_dir)),
            'old_id': None,
            'new_id': None,
            'status': 'unknown',
            'message': ''
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            current_id = self.get_current_module_id(content)
            if not current_id:
                result['status'] = 'skipped'
                result['message'] = '未找到module_id'
                return result
            
            result['old_id'] = current_id
            
            if not current_id.startswith('FRAMEWORK_'):
                result['status'] = 'skipped'
                result['message'] = f'命名风格已符合标准'
                return result
            
            new_id = self.MODULE_ID_MAPPING.get(current_id)
            if not new_id:
                result['status'] = 'skipped'
                result['message'] = f'未找到映射规则: {current_id}'
                return result
            
            result['new_id'] = new_id
            
            if self.dry_run:
                result['status'] = 'dry_run'
                result['message'] = f'将修改: {current_id} -> {new_id}'
            else:
                new_content = content.replace(f'module_id: {current_id}', f'module_id: {new_id}')
                with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new_content)
                result['status'] = 'updated'
                result['message'] = f'已修改: {current_id} -> {new_id}'
            
            return result
            
        except Exception as e:
            result['status'] = 'failed'
            result['message'] = f'处理失败: {str(e)}'
            return result
    
    def scan_and_unify(self) -> Dict:
        """扫描并统一module_id"""
        print(f"开始扫描目录: {self.root_dir}")
        print(f"模式: {'干运行 (不实际修改文件)' if self.dry_run else '实际修改'}")
        print("-" * 80)
        
        md_files = list(self.root_dir.rglob('*.md'))
        self.results['total_files'] = len(md_files)
        
        print(f"找到 {len(md_files)} 个Markdown文件")
        print("-" * 80)
        
        for file_path in md_files:
            result = self.unify_module_id(file_path)
            self.results['details'].append(result)
            
            if result['status'] == 'updated':
                self.results['updated_files'] += 1
                print(f"[OK] {result['file']}: {result['message']}")
            elif result['status'] == 'dry_run':
                self.results['updated_files'] += 1
                print(f"[DRY] {result['file']}: {result['message']}")
            elif result['status'] == 'failed':
                self.results['failed_files'] += 1
                print(f"[FAIL] {result['file']}: {result['message']}")
            else:
                self.results['skipped_files'] += 1
        
        return self.results
    
    def generate_report(self) -> str:
        """生成修复报告"""
        report = []
        report.append("=" * 80)
        report.append("module_id命名统一报告")
        report.append("=" * 80)
        report.append(f"修复时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"扫描目录: {self.root_dir}")
        report.append(f"模式: {'干运行' if self.dry_run else '实际修改'}")
        report.append("")
        
        report.append("## 统计信息")
        report.append("-" * 80)
        report.append(f"总文件数: {self.results['total_files']}")
        report.append(f"更新文件数: {self.results['updated_files']}")
        report.append(f"跳过文件数: {self.results['skipped_files']}")
        report.append(f"失败文件数: {self.results['failed_files']}")
        report.append("")
        
        if self.results['updated_files'] > 0:
            report.append("## 更新详情")
            report.append("-" * 80)
            for detail in self.results['details']:
                if detail['status'] in ['updated', 'dry_run']:
                    report.append(f"- {detail['file']}: {detail['message']}")
            report.append("")
        
        if self.results['failed_files'] > 0:
            report.append("## 失败详情")
            report.append("-" * 80)
            for detail in self.results['details']:
                if detail['status'] == 'failed':
                    report.append(f"- {detail['file']}: {detail['message']}")
            report.append("")
        
        report.append("**修复工具**: unify_module_id.py v1.0.0")
        report.append(f"**修复日期**: {datetime.now().strftime('%Y-%m-%d')}")
        
        return "\n".join(report)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='统一module_id命名风格工具')
    parser.add_argument('directory', help='要扫描的目录路径')
    parser.add_argument('--dry-run', action='store_true', help='干运行模式，不实际修改文件')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        print(f"错误: 目录不存在 - {args.directory}")
        sys.exit(1)
    
    unifier = ModuleIdUnifier(args.directory, args.dry_run)
    unifier.scan_and_unify()
    
    print("\n" + unifier.generate_report())


if __name__ == '__main__':
    main()
