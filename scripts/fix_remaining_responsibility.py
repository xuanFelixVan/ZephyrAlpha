#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复剩余4个文档的职责描述
"""

import os
import re
from pathlib import Path
from typing import Dict, Optional

class RemainingDocsFixer:
    def __init__(self):
        self.project_root = Path(r"D:\ZephyrAlpha")
        self.remaining_docs = [
            {
                "path": "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/LIQUIDITY_CONSTRAINED_OPTIMIZATION_BLUEPRINT.md",
                "new_resp": "流动性约束优化，包括流动性建模、约束处理、优化求解、交易成本"
            },
            {
                "path": "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/CONSTRAINT_SOLVER_BLUEPRINT.md",
                "new_resp": "约束求解器，包括约束建模、求解算法、优化引擎、约束验证"
            },
            {
                "path": "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/AUTO_REPAIR_ENGINE_BLUEPRINT.md",
                "new_resp": "自动修复引擎，包括问题检测、修复策略、自动修复、修复验证"
            },
            {
                "path": "docs/05_IMPLEMENTATION/06_CONSTRUCTION_DOCS/01_BLUEPRINTS/AI_ENHANCEMENT_INTEGRATION_BLUEPRINT.md",
                "new_resp": "AI增强集成，包括AI辅助、智能优化、增强功能、AI能力注入"
            }
        ]
        self.fixed_count = 0
    
    def fix_yaml_responsibility(self, content: str, new_resp: str) -> str:
        lines = content.split('\n')
        updated_lines = []
        in_responsibility = False
        responsibility_replaced = False
        
        for i, line in enumerate(lines):
            if line.strip().startswith('responsibility:'):
                in_responsibility = True
                updated_lines.append(line)
                responsibility_replaced = False
            elif in_responsibility and not responsibility_replaced:
                if line.strip().startswith('-'):
                    if not responsibility_replaced:
                        updated_lines.append(f'  - {new_resp}')
                        responsibility_replaced = True
                    continue
                else:
                    in_responsibility = False
                    updated_lines.append(line)
            else:
                updated_lines.append(line)
        
        return '\n'.join(updated_lines)
    
    def fix_document(self, doc_info: Dict) -> bool:
        doc_path = self.project_root / doc_info['path']
        
        if not doc_path.exists():
            print(f"✗ 文件不存在: {doc_info['path']}")
            return False
        
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(doc_path, 'r', encoding='gbk') as f:
                    content = f.read()
            except Exception as e:
                print(f"✗ 编码错误: {doc_info['path']} - {str(e)}")
                return False
        
        if content.startswith('\ufeff'):
            content = content[1:]
        
        new_content = self.fix_yaml_responsibility(content, doc_info['new_resp'])
        
        try:
            with open(doc_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(new_content)
            
            print(f"✓ 修复成功: {doc_info['path']}")
            print(f"  新职责: {doc_info['new_resp']}")
            self.fixed_count += 1
            return True
        except Exception as e:
            print(f"✗ 写入失败: {doc_info['path']} - {str(e)}")
            return False
    
    def run(self):
        print("=" * 80)
        print("修复剩余4个文档的职责描述")
        print("=" * 80)
        
        for i, doc_info in enumerate(self.remaining_docs, 1):
            print(f"\n[{i}/4] 处理: {doc_info['path']}")
            self.fix_document(doc_info)
        
        print("\n" + "=" * 80)
        print(f"修复完成: {self.fixed_count}/4 个文档")
        print("=" * 80)

if __name__ == "__main__":
    fixer = RemainingDocsFixer()
    fixer.run()
