#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
职责描述去重优化脚本
为存在重复职责描述的文件生成独特的职责描述
"""

import re
from pathlib import Path
from typing import List, Dict

class ResponsibilityDeduplicator:
    """职责描述去重优化器"""
    
    def __init__(self):
        self.optimized_count = 0
        self.total_count = 0
    
    def get_unique_responsibility(self, file_name: str) -> List[str]:
        """根据文件名生成独特的职责描述"""
        
        name_upper = file_name.upper()
        
        if 'KNOWLEDGE_MANAGEMENT_BLUEPRINT' in name_upper:
            return [
                '知识管理模块蓝图设计与实施指导',
                '知识库构建、知识检索、知识更新机制设计'
            ]
        
        elif 'SCENARIO_ANALYSIS_STRESS_TEST_BLUEPRINT' in name_upper:
            return [
                '情景分析与压力测试模块蓝图设计',
                '情景构建、压力测试、风险评估方案设计'
            ]
        
        elif 'SENTIMENT_ANALYSIS_MEDIUM_TERM_IMPROVEMENT_BLUEPRINT' in name_upper:
            return [
                '舆情分析层中期改进蓝图设计',
                '知识图谱、流式处理、多语言支持改进方案'
            ]
        
        elif 'SENTIMENT_ANALYSIS_LONG_TERM_TECHNICAL_SPECIFICATION' in name_upper:
            return [
                '舆情分析层长期改进技术规格定义',
                '多模态分析、AI虚拟研究团队技术规格'
            ]
        
        elif 'SENTIMENT_ANALYSIS_MEDIUM_TERM_TECHNICAL_SPECIFICATION' in name_upper:
            return [
                '舆情分析层中期改进技术规格定义',
                '知识图谱、流式处理、多语言支持技术规格'
            ]
        
        else:
            return [
                'AI工作流与舆情分析综合层模块蓝图设计',
                '模块功能设计与实施指导'
            ]
    
    def optimize_file(self, file_path: Path) -> bool:
        """优化单个文件的职责描述"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            content = content.lstrip('\ufeff')
            
            yaml_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
            if not yaml_match:
                return False
            
            yaml_content = yaml_match.group(1)
            
            new_responsibilities = self.get_unique_responsibility(file_path.stem)
            
            if not new_responsibilities:
                return False
            
            responsibility_str = '\n'.join([f'  - {r}' for r in new_responsibilities])
            
            new_yaml = re.sub(
                r'responsibility:\s*\n(  - .*\n)+',
                f'responsibility:\n{responsibility_str}\n',
                yaml_content
            )
            
            new_content = content.replace(yaml_content, new_yaml, 1)
            
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(new_content)
            
            return True
            
        except Exception as e:
            print(f"  [ERROR] 优化失败: {file_path.name} - {e}")
            return False
    
    def run(self, docs_dir: Path):
        """执行去重优化"""
        print("=== 开始职责描述去重优化 ===\n")
        
        target_files = [
            'KNOWLEDGE_MANAGEMENT_BLUEPRINT.md',
            'SCENARIO_ANALYSIS_STRESS_TEST_BLUEPRINT.md',
            'SENTIMENT_ANALYSIS_MEDIUM_TERM_IMPROVEMENT_BLUEPRINT.md',
            'SENTIMENT_ANALYSIS_LONG_TERM_TECHNICAL_SPECIFICATION.md',
            'SENTIMENT_ANALYSIS_MEDIUM_TERM_TECHNICAL_SPECIFICATION.md'
        ]
        
        for target_file in target_files:
            file_path = docs_dir / target_file
            
            if not file_path.exists():
                print(f"  [WARNING] 文件不存在: {target_file}")
                continue
            
            self.total_count += 1
            
            if self.optimize_file(file_path):
                self.optimized_count += 1
                print(f"  [OK] 优化: {target_file}")
        
        print(f"\n=== 优化完成 ===")
        print(f"总文件数: {self.total_count}")
        print(f"优化文件数: {self.optimized_count}")
        if self.total_count > 0:
            print(f"优化率: {self.optimized_count/self.total_count*100:.2f}%")

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs/10_AI_WORKFLOW")
    deduplicator = ResponsibilityDeduplicator()
    deduplicator.run(docs_dir)

if __name__ == "__main__":
    main()
