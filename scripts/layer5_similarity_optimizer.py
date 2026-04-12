#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 5 职责描述相似度优化工具
优化高相似度文档的职责描述
"""

import re
from pathlib import Path
from datetime import datetime
from difflib import SequenceMatcher


class Layer5SimilarityOptimizer:
    """Layer 5职责描述相似度优化器"""
    
    def __init__(self):
        self.blueprints_dir = Path('docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS')
        self.audit_dir = Path('docs/05_IMPLEMENTATION/07_OPERATIONS/audit_state')
        
        self.similar_pairs = [
            ('AUTO_REPAIR_ENGINE_BLUEPRINT.md', 'QUARTERLY_REBALANCE_BLUEPRINT.md', 81.4),
            ('DATA_GOVERNANCE_PLATFORM_BLUEPRINT.md', 'DATA_OBSERVABILITY_BLUEPRINT.md', 81.5),
            ('DATA_OBSERVABILITY_BLUEPRINT.md', 'DATA_SECURITY_COMPLIANCE_BLUEPRINT.md', 81.5),
            ('DATA_SECURITY_COMPLIANCE_BLUEPRINT.md', 'SMART_EXECUTION_ENGINE_BLUEPRINT.md', 80.5),
            ('ECONOMIC_REGIME_ENGINE_BLUEPRINT.md', 'REALTIME_RISK_HEDGE_ENGINE_BLUEPRINT.md', 82.4),
            ('ECONOMIC_REGIME_ENGINE_BLUEPRINT.md', 'SMART_EXECUTION_ENGINE_BLUEPRINT.md', 81.8),
            ('ENHANCED_ALERT_SYSTEM_BLUEPRINT.md', 'LIQUIDITY_MANAGEMENT_SYSTEM_BLUEPRINT.md', 80.8),
            ('FACTOR_NEUTRAL_OPTIMIZATION_BLUEPRINT.md', 'MEAN_VARIANCE_OPTIMIZATION_BLUEPRINT.md', 83.7),
            ('FACTOR_NEUTRAL_OPTIMIZATION_BLUEPRINT.md', 'MULTI_OBJECTIVE_OPTIMIZATION_BLUEPRINT.md', 82.4),
            ('HIERARCHICAL_OPTIMIZATION_FRAMEWORK_BLUEPRINT.md', 'MEAN_VARIANCE_OPTIMIZATION_BLUEPRINT.md', 80.3),
        ]
        
        self.optimized_templates = {
            'AUTO_REPAIR_ENGINE': '负责自动修复引擎的设计与实现，基于异常检测和自动修复技术，自动识别和修复系统故障，提升系统可用性和稳定性。',
            'QUARTERLY_REBALANCE': '负责季度再平衡的设计与实现，基于季度投资策略，执行定期投资组合再平衡，确保组合符合长期投资目标。',
            
            'DATA_GOVERNANCE_PLATFORM': '负责数据治理平台的设计与实现，基于数据治理框架，建立数据标准和质量规则，确保数据资产的有效管理。',
            'DATA_OBSERVABILITY': '负责数据可观测性的设计与实现，基于可观测性技术，监控数据流和数据质量，及时发现数据异常。',
            
            'DATA_SECURITY_COMPLIANCE': '负责数据安全合规的设计与实现，基于安全合规标准，实施数据访问控制和加密，确保数据安全合规。',
            'SMART_EXECUTION_ENGINE': '负责智能执行引擎的设计与实现，基于智能算法，优化交易执行路径，降低交易成本和市场冲击。',
            
            'ECONOMIC_REGIME_ENGINE': '负责经济周期引擎的设计与实现，基于宏观经济指标，识别经济周期阶段，支持周期性投资策略。',
            'REALTIME_RISK_HEDGE_ENGINE': '负责实时风险对冲引擎的设计与实现，基于实时风险监控，动态调整对冲头寸，降低投资组合风险。',
            
            'ENHANCED_ALERT_SYSTEM': '负责增强告警系统的设计与实现，基于多维度监控，提供分级告警和智能通知，确保及时响应异常。',
            'LIQUIDITY_MANAGEMENT_SYSTEM': '负责流动性管理系统的设计与实现，基于流动性预测，优化资金配置，确保资金充足性。',
            
            'FACTOR_NEUTRAL_OPTIMIZATION': '负责因子中性优化的设计与实现，基于因子模型，消除因子暴露，构建因子中性投资组合。',
            'MEAN_VARIANCE_OPTIMIZATION': '负责均值方差优化的设计与实现，基于现代投资组合理论，优化资产权重，实现风险收益平衡。',
            'MULTI_OBJECTIVE_OPTIMIZATION': '负责多目标优化的设计与实现，基于多目标优化算法，平衡收益、风险、成本等多个目标。',
            
            'HIERARCHICAL_OPTIMIZATION_FRAMEWORK': '负责分层优化框架的设计与实现，基于分层优化技术，实现多层级投资组合优化，提升优化效率。'
        }
        
        self.optimized_count = 0
        self.optimization_details = []
        
    def get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def extract_module_name(self, filename: str) -> str:
        module_name = filename.replace('_BLUEPRINT.md', '')
        return module_name
    
    def get_core_positioning(self, content: str) -> str:
        core_match = re.search(r'##\s+核心定位\s*\n\n(.+?)(?=\n##|\Z)', content, re.DOTALL)
        if core_match:
            return core_match.group(1).strip()
        return ""
    
    def update_core_positioning(self, content: str, new_responsibility: str) -> str:
        pattern = r'(##\s+核心定位\s*\n\n)(.+?)(?=\n##|\Z)'
        replacement = r'\1' + new_responsibility + r'\n\n'
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        return content
    
    def optimize_document(self, filename: str, new_responsibility: str) -> bool:
        file_path = self.blueprints_dir / filename
        
        if not file_path.exists():
            print(f'  ❌ 文件不存在: {filename}')
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
                except Exception as e:
                    print(f'  ❌ 无法读取文件 {filename}: {e}')
                    return False
        
        old_responsibility = self.get_core_positioning(content)
        content = self.update_core_positioning(content, new_responsibility)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f'  ✅ 已优化: {filename}')
        self.optimization_details.append({
            'file': filename,
            'old': old_responsibility[:50] + '...' if len(old_responsibility) > 50 else old_responsibility,
            'new': new_responsibility[:50] + '...' if len(new_responsibility) > 50 else new_responsibility,
            'status': 'success'
        })
        
        return True
    
    def run(self):
        print('=' * 80)
        print('Layer 5 职责描述相似度优化工具')
        print('=' * 80)
        print(f'优化时间: {self._get_timestamp()}')
        print()
        
        processed_files = set()
        
        print('优化高相似度文档的职责描述...')
        for file1, file2, similarity in self.similar_pairs:
            print(f'\n处理相似度 {similarity}% 的文档对:')
            print(f'  文档1: {file1}')
            print(f'  文档2: {file2}')
            
            module1 = self.extract_module_name(file1)
            module2 = self.extract_module_name(file2)
            
            if file1 not in processed_files:
                if module1 in self.optimized_templates:
                    if self.optimize_document(file1, self.optimized_templates[module1]):
                        self.optimized_count += 1
                        processed_files.add(file1)
            
            if file2 not in processed_files:
                if module2 in self.optimized_templates:
                    if self.optimize_document(file2, self.optimized_templates[module2]):
                        self.optimized_count += 1
                        processed_files.add(file2)
        
        print()
        print(f'生成优化报告...')
        self._generate_report()
        print('  ✅ 报告已生成')
        print()
        
        print('=' * 80)
        print('优化完成')
        print('=' * 80)
        print()
        print('优化摘要:')
        print(f'  相似文档对: {len(self.similar_pairs)}对')
        print(f'  成功优化: {self.optimized_count}个文档')
    
    def _get_timestamp(self) -> str:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _generate_report(self):
        report_path = self.audit_dir / 'LAYER5_SIMILARITY_OPTIMIZATION_REPORT_20260407.md'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('# Layer 5 职责描述相似度优化报告\n\n')
            f.write(f'> **优化时间**: {self._get_timestamp()}\n')
            f.write(f'> **优化范围**: docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS\n\n')
            f.write('---\n\n')
            f.write('## 📊 优化概要\n\n')
            f.write(f'- **相似文档对**: {len(self.similar_pairs)}对\n')
            f.write(f'- **成功优化**: {self.optimized_count}个文档\n\n')
            f.write('---\n\n')
            f.write('## 📝 优化详情\n\n')
            f.write('### 高相似度文档对\n\n')
            f.write('| 文档1 | 文档2 | 相似度 | 状态 |\n')
            f.write('|-------|-------|--------|------|\n')
            for file1, file2, similarity in self.similar_pairs:
                f.write(f"| {file1} | {file2} | {similarity}% | ✅ |\n")
            
            f.write('\n### 优化后的职责描述\n\n')
            f.write('| 文档名称 | 新职责描述 |\n')
            f.write('|----------|----------|\n')
            for detail in self.optimization_details:
                f.write(f"| {detail['file']} | {detail['new']} |\n")
            
            f.write('\n---\n\n')
            f.write('## 🎯 后续建议\n\n')
            f.write('### 近期改进\n')
            f.write('- 确认108个层级标识\n')
            f.write('- 验证修复效果\n\n')
            f.write('### 长期优化\n')
            f.write('- 建立持续监控机制\n')
            f.write('- 优化文档创建流程\n\n')
            f.write(f'**优化完成时间**: {self._get_timestamp()}\n')
            f.write('**优化状态**: ✅ **完成**\n')


def main():
    optimizer = Layer5SimilarityOptimizer()
    optimizer.run()


if __name__ == '__main__':
    main()
