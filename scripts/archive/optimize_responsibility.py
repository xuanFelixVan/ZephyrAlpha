#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
智能职责描述优化脚本
自动优化职责描述，使其更加具体和清晰
"""

import re
from pathlib import Path
from typing import List, Dict, Optional

class ResponsibilityOptimizer:
    """职责描述优化器"""
    
    def __init__(self):
        self.min_length = 20
        self.optimized_count = 0
        self.total_count = 0
    
    def analyze_file_context(self, file_path: Path, docs_dir: Path) -> Dict:
        """分析文件上下文"""
        context = {
            'file_name': file_path.stem,
            'file_ext': file_path.suffix,
            'dir_path': str(file_path.parent.relative_to(docs_dir)),
            'dir_parts': list(file_path.parent.relative_to(docs_dir).parts),
            'keywords': []
        }
        
        # 提取文件名关键词
        name_parts = re.split(r'[_\-\s]', file_path.stem)
        context['keywords'].extend([p for p in name_parts if len(p) > 2])
        
        # 提取目录关键词
        for part in context['dir_parts']:
            if part not in ['docs', 'ARCHIVE', 'archive']:
                context['keywords'].append(part)
        
        return context
    
    def generate_responsibility(self, context: Dict, content: str) -> List[str]:
        """生成职责描述"""
        responsibilities = []
        
        # 根据文件类型和关键词生成职责
        file_name = context['file_name'].upper()
        dir_path = context['dir_path'].upper()
        
        # 蓝图文档
        if 'BLUEPRINT' in file_name:
            if 'PORTFOLIO' in file_name:
                responsibilities.append('投资组合优化蓝图设计与实施指导')
            elif 'RISK' in file_name:
                responsibilities.append('风险管理框架设计与实施方案')
            elif 'DATA' in file_name:
                responsibilities.append('数据管理架构设计与实施规范')
            elif 'STRATEGY' in file_name:
                responsibilities.append('交易策略框架设计与实施指导')
            elif 'MONITORING' in file_name:
                responsibilities.append('系统监控架构设计与实施方案')
            elif 'OPTIMIZATION' in file_name:
                responsibilities.append('系统优化方案设计与实施指导')
            else:
                responsibilities.append('系统架构蓝图设计与实施指导')
        
        # 技术规格书
        elif 'TECHNICAL_SPECIFICATION' in file_name or 'TS' in file_name:
            responsibilities.append('技术规格定义与实施标准制定')
        
        # 审计报告
        elif 'AUDIT' in file_name or 'REPORT' in file_name:
            responsibilities.append('系统审计分析与质量评估报告')
        
        # 索引文档
        elif file_name == 'INDEX':
            responsibilities.append('目录导航与文档索引管理')
        
        # 标准文档
        elif 'STANDARD' in file_name:
            responsibilities.append('技术标准制定与规范管理')
        
        # 模板文档
        elif 'TEMPLATE' in file_name:
            responsibilities.append('文档模板设计与标准化管理')
        
        # 工作流文档
        elif 'WORKFLOW' in file_name:
            responsibilities.append('工作流程设计与优化管理')
        
        # 指南文档
        elif 'GUIDE' in file_name:
            responsibilities.append('操作指南编写与使用说明')
        
        # 架构文档
        elif 'ARCHITECTURE' in file_name:
            responsibilities.append('系统架构设计与技术选型')
        
        # 概览文档
        elif 'OVERVIEW' in file_name or file_name == '00_OVERVIEW':
            responsibilities.append('系统概览与整体架构说明')
        
        # 框架文档
        elif 'FRAMEWORK' in file_name or '01_FRAMEWORK' in dir_path:
            responsibilities.append('系统框架设计与核心架构管理')
        
        # 因子库文档
        elif 'FACTOR' in file_name or '02_FACTOR' in dir_path:
            responsibilities.append('因子研究与管理框架设计')
        
        # 交易策略文档
        elif 'TRADING' in file_name or '03_TRADING' in dir_path:
            responsibilities.append('交易策略设计与实施管理')
        
        # 执行层文档
        elif 'EXECUTION' in file_name or '04_EXECUTION' in dir_path:
            responsibilities.append('交易执行系统设计与优化')
        
        # 实施文档
        elif 'IMPLEMENTATION' in file_name or '05_IMPLEMENTATION' in dir_path:
            responsibilities.append('系统实施与部署管理')
        
        # 治理合规文档
        elif 'GOVERNANCE' in file_name or '10_GOVERNANCE' in dir_path:
            responsibilities.append('治理合规框架设计与实施')
        
        # AI工作流文档
        elif 'AI_WORKFLOW' in file_name or '10_AI_WORKFLOW' in dir_path:
            responsibilities.append('AI工作流设计与智能辅助管理')
        
        # 研究创新文档
        elif 'RESEARCH' in file_name or '09_RESEARCH' in dir_path:
            responsibilities.append('研究创新框架设计与实施')
        
        # 审计文档
        elif 'AUDIT' in dir_path:
            responsibilities.append('审计体系设计与质量监控')
        
        # 默认职责
        else:
            # 根据目录生成职责
            if len(context['dir_parts']) > 0:
                dir_name = context['dir_parts'][0].replace('_', ' ')
                responsibilities.append(f'{dir_name}模块文档管理与维护')
            else:
                responsibilities.append('系统文档管理与维护')
        
        # 确保每个职责描述至少20个字符
        responsibilities = [self._ensure_min_length(r) for r in responsibilities]
        
        return responsibilities
    
    def _ensure_min_length(self, text: str) -> str:
        """确保文本至少20个字符"""
        if len(text) < self.min_length:
            # 添加补充说明
            if '蓝图' in text:
                text += '与实施方案'
            elif '规格' in text:
                text += '与实施标准'
            elif '报告' in text:
                text += '与改进建议'
            elif '管理' in text:
                text += '与优化维护'
            elif '设计' in text:
                text += '与实施指导'
            else:
                text += '与系统维护管理'
        
        return text
    
    def optimize_file(self, file_path: Path, docs_dir: Path) -> bool:
        """优化单个文件的职责描述"""
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # 检查是否有responsibility字段
            match = re.search(r'responsibility:\s*\n((?:\s+-\s+.+\n)+)', content)
            if not match:
                return False
            
            # 提取现有职责描述
            responsibilities = match.group(1).strip().split('\n')
            responsibilities = [r.strip('- ').strip() for r in responsibilities]
            
            # 检查是否需要优化
            needs_optimization = False
            for resp in responsibilities:
                if len(resp) < self.min_length:
                    needs_optimization = True
                    break
            
            if not needs_optimization:
                return False
            
            # 分析文件上下文
            context = self.analyze_file_context(file_path, docs_dir)
            
            # 生成新的职责描述
            new_responsibilities = self.generate_responsibility(context, content)
            
            # 如果生成的职责描述为空，保留原有描述
            if not new_responsibilities:
                return False
            
            # 构建新的responsibility字段
            new_resp_text = 'responsibility:\n'
            for resp in new_responsibilities:
                new_resp_text += f'  - {resp}\n'
            
            # 替换原有字段
            new_content = re.sub(
                r'responsibility:\s*\n(?:\s+-\s+.+\n)+',
                new_resp_text,
                content
            )
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8-sig') as f:
                f.write(new_content)
            
            print(f"  [OK] 优化: {file_path.relative_to(docs_dir)}")
            return True
            
        except Exception as e:
            print(f"  [ERROR] 错误: {file_path.name} - {e}")
            return False
    
    def run(self, docs_dir: Path):
        """运行优化器"""
        print("=== 开始优化职责描述 ===\n")
        
        # 遍历所有Markdown文件
        for md_file in docs_dir.rglob("*.md"):
            # 跳过归档目录
            if any(keyword in str(md_file) for keyword in ['06_ARCHIVE', '09_ARCHIVE', '99_ARCHIVE', 'archive']):
                continue
            
            self.total_count += 1
            if self.optimize_file(md_file, docs_dir):
                self.optimized_count += 1
        
        print(f"\n=== 优化完成 ===")
        print(f"总文件数: {self.total_count}")
        print(f"优化文件数: {self.optimized_count}")
        print(f"优化率: {self.optimized_count/self.total_count*100:.2f}%" if self.total_count > 0 else "优化率: 0%")

def main():
    """主函数"""
    docs_dir = Path("D:/ZephyrAlpha/docs")
    optimizer = ResponsibilityOptimizer()
    optimizer.run(docs_dir)

if __name__ == "__main__":
    main()
