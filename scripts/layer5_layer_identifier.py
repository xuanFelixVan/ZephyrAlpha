#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 5 层级标识修正工具
自动检查和修正文档的层级标识
"""

import re
from pathlib import Path
from datetime import datetime


class Layer5LayerIdentifier:
    """Layer 5层级标识修正器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.layer_mapping = {
            'DATA_PREPROCESSING': 'Layer 5.1 (数据处理)',
            'DATA_CLEANING': 'Layer 5.1 (数据处理)',
            'DATA_VALIDATION': 'Layer 5.1 (数据处理)',
            'DATA_STANDARDIZATION': 'Layer 5.1 (数据处理)',
            'DATA_QUALITY': 'Layer 5.1 (数据处理)',
            'DATA_GOVERNANCE': 'Layer 5.1 (数据处理)',
            'DATA_OBSERVABILITY': 'Layer 5.1 (数据处理)',
            'DATA_SECURITY': 'Layer 5.1 (数据处理)',
            'DATA_BACKUP': 'Layer 5.1 (数据处理)',
            'DATA_ACCESS': 'Layer 5.1 (数据处理)',
            'DATA_SOURCE': 'Layer 5.1 (数据处理)',
            'DATA_SUBSCRIPTION': 'Layer 5.1 (数据处理)',
            'DATA_ORCHESTRATION': 'Layer 5.1 (数据处理)',
            'DATA_MASKING': 'Layer 5.1 (数据处理)',
            'DATA_CATALOG': 'Layer 5.1 (数据处理)',
            'DATA_LIFECYCLE': 'Layer 5.1 (数据处理)',
            'DATA_COST': 'Layer 5.1 (数据处理)',
            'DATA_MESH': 'Layer 5.1 (数据处理)',
            'DATA_FABRIC': 'Layer 5.1 (数据处理)',
            'DATA_VERSION': 'Layer 5.1 (数据处理)',
            'CDC': 'Layer 5.1 (数据处理)',
            'CLICKHOUSE': 'Layer 5.1 (数据处理)',
            'TIMESCALEDB': 'Layer 5.1 (数据处理)',
            'REDIS': 'Layer 5.1 (数据处理)',
            'OBJECT_STORAGE': 'Layer 5.1 (数据处理)',
            'DISTRIBUTED_QUERY': 'Layer 5.1 (数据处理)',
            'REALTIME_DATA': 'Layer 5.1 (数据处理)',
            'HIGH_PERFORMANCE_DATA': 'Layer 5.1 (数据处理)',
            
            'PORTFOLIO': 'Layer 5.2 (组合优化)',
            'ASSET_ALLOCATION': 'Layer 5.2 (组合优化)',
            'DYNAMIC_ASSET': 'Layer 5.2 (组合优化)',
            'MULTI_ASSET': 'Layer 5.2 (组合优化)',
            'MEAN_VARIANCE': 'Layer 5.2 (组合优化)',
            'BLACK_LITTERMAN': 'Layer 5.2 (组合优化)',
            'RISK_PARITY': 'Layer 5.2 (组合优化)',
            'FACTOR_NEUTRAL': 'Layer 5.2 (组合优化)',
            'MULTI_OBJECTIVE': 'Layer 5.2 (组合优化)',
            'HIERARCHICAL': 'Layer 5.2 (组合优化)',
            'ROBUST': 'Layer 5.2 (组合优化)',
            'CONSTRAINT': 'Layer 5.2 (组合优化)',
            'LIQUIDITY_CONSTRAINED': 'Layer 5.2 (组合优化)',
            'TRANSACTION_COST': 'Layer 5.2 (组合优化)',
            'TAX_LOSS': 'Layer 5.2 (组合优化)',
            'PORTFOLIO_INSURANCE': 'Layer 5.2 (组合优化)',
            
            'RISK': 'Layer 5.3 (风险管理)',
            'VAR': 'Layer 5.3 (风险管理)',
            'STRESS_TESTING': 'Layer 5.3 (风险管理)',
            'TAIL_RISK': 'Layer 5.3 (风险管理)',
            'REALTIME_RISK': 'Layer 5.3 (风险管理)',
            'BARRA': 'Layer 5.3 (风险管理)',
            'DYNAMIC_CORRELATION': 'Layer 5.3 (风险管理)',
            'DYNAMIC_LEVERAGE': 'Layer 5.3 (风险管理)',
            'MARGIN': 'Layer 5.3 (风险管理)',
            'LIQUIDITY_MANAGEMENT': 'Layer 5.3 (风险管理)',
            
            'TRADING': 'Layer 5.4 (交易执行)',
            'EXECUTION': 'Layer 5.4 (交易执行)',
            'ALGORITHMIC': 'Layer 5.4 (交易执行)',
            'SMART': 'Layer 5.4 (交易执行)',
            'ORDER': 'Layer 5.4 (交易执行)',
            'MARKET_IMPACT': 'Layer 5.4 (交易执行)',
            'TURNOVER': 'Layer 5.4 (交易执行)',
            'TRADING_COST': 'Layer 5.4 (交易执行)',
            
            'STRATEGY': 'Layer 5 (策略执行层)',
            'ECONOMIC': 'Layer 5 (策略执行层)',
            'MARKET_REGIME': 'Layer 5 (策略执行层)',
            'QUARTERLY': 'Layer 5 (策略执行层)',
            'OPENING': 'Layer 5 (策略执行层)',
            'INTRADAY': 'Layer 5 (策略执行层)',
            'STATISTICAL': 'Layer 5 (策略执行层)',
            'COINTEGRATION': 'Layer 5 (策略执行层)',
            
            'SYSTEM': 'Layer 5 (策略执行层)',
            'COMPLETE': 'Layer 5 (策略执行层)',
            'ARCHITECTURE': 'Layer 5 (策略执行层)',
            'CONFIGURATION': 'Layer 5 (策略执行层)',
            'MONITORING': 'Layer 5 (策略执行层)',
            'AUTO_REPAIR': 'Layer 5 (策略执行层)',
            'QUALITY': 'Layer 5 (策略执行层)',
            'ENHANCED': 'Layer 5 (策略执行层)',
        }
        
        self.default_layer = 'Layer 5 (策略执行层)'
        self.fixed_count = 0
        self.fix_details = []
        
    def get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def extract_module_name(self, filename: str) -> str:
        module_name = filename.replace('_BLUEPRINT.md', '')
        return module_name
    
    def determine_layer(self, filename: str) -> str:
        module_name = self.extract_module_name(filename)
        
        for keyword, layer in self.layer_mapping.items():
            if keyword in module_name:
                return layer
        
        return self.default_layer
    
    def has_yaml_header(self, content: str) -> bool:
        return content.strip().startswith('---')
    
    def has_layer_field(self, content: str) -> bool:
        return re.search(r'^layer:\s*.+$', content, re.MULTILINE) is not None
    
    def get_current_layer(self, content: str) -> str:
        match = re.search(r'^layer:\s*(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        return ""
    
    def add_layer_field(self, content: str, layer: str) -> str:
        yaml_match = re.search(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            new_yaml = yaml_content + f'\nlayer: {layer}'
            content = content.replace(yaml_content, new_yaml)
        return content
    
    def update_layer_field(self, content: str, layer: str) -> str:
        content = re.sub(
            r'^layer:\s*.+$',
            f'layer: {layer}',
            content,
            flags=re.MULTILINE
        )
        return content
    
    def fix_document(self, filename: str) -> bool:
        file_path = self.blueprints_dir / filename
        
        if not file_path.exists():
            return False
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception:
                    return False
        
        correct_layer = self.determine_layer(filename)
        
        if not self.has_yaml_header(content):
            return False
        
        if not self.has_layer_field(content):
            content = self.add_layer_field(content, correct_layer)
            print(f'  ✅ 已添加layer字段: {filename} -> {correct_layer}')
        else:
            current_layer = self.get_current_layer(content)
            if current_layer != correct_layer:
                content = self.update_layer_field(content, correct_layer)
                print(f'  ✅ 已更新layer字段: {filename}')
                print(f'     从: {current_layer}')
                print(f'     到: {correct_layer}')
            else:
                return True
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.fix_details.append({
            'file': filename,
            'layer': correct_layer,
            'status': 'success'
        })
        
        return True
    
    def run(self):
        print('=' * 80)
        print('Layer 5 层级标识修正工具')
        print('=' * 80)
        print(f'修正时间: {self._get_timestamp()}')
        print()
        
        print('扫描文档文件...')
        files = list(self.blueprints_dir.glob('*_BLUEPRINT.md'))
        print(f'  找到 {len(files)} 个文档')
        print()
        
        print('修正层级标识...')
        for file_path in files:
            filename = file_path.name
            if self.fix_document(filename):
                self.fixed_count += 1
        print()
        
        print(f'生成修正报告...')
        self._generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('修正完成')
        print('=' * 80)
        print()
        print('修正摘要:')
        print(f'  扫描文档: {len(files)}个')
        print(f'  成功修正: {self.fixed_count}个')
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _generate_report(self):
        report_path = self.audit_dir / 'LAYER5_LAYER_IDENTIFICATION_FIX_REPORT_20260407.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 层级标识修正报告\n\n')
            f.write(f'> **修正时间**: {self._get_timestamp()}\n')
            f.write(f'> **修正范围**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS\n\n')
            f.write('---\n\n')
            f.write('## 📊 修正概要\n\n')
            f.write(f'- **扫描文档**: {len(list(self.blueprints_dir.glob("*_BLUEPRINT.md")))}个\n')
            f.write(f'- **成功修正**: {self.fixed_count}个\n\n')
            f.write('---\n\n')
            f.write('## 📝 修正详情\n\n')
            f.write('| 文档名称 | 层级标识 | 状态 |\n')
            f.write('|----------|----------|------|\n')
            for detail in self.fix_details:
                f.write(f"| {detail['file']} | {detail['layer']} | ✅ |\n")
            
            f.write('\n---\n\n')
            f.write('## 🎯 后续建议\n\n')
            f.write('### 近期改进\n')
            f.write('- 验证修正效果\n')
            f.write('- 处理特殊情况\n\n')
            f.write('### 中期改进\n')
            f.write('- 建立文档质量持续监控机制\n')
            f.write('- 优化文档创建流程\n\n')
            f.write(f'**修正完成时间**: {self._get_timestamp()}\n')
            f.write('**修正状态**: ✅ **完成**\n')


def main():
    fixer = Layer5LayerIdentifier()
    fixer.run()


if __name__ == '__main__':
    main()
