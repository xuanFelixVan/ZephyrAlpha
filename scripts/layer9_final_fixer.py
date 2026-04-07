#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Layer 9研究与创新层最终修复脚本
处理剩余的重复内容和归档文档状态问题
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime

class Layer9FinalFixer:
    """Layer 9最终修复器"""
    
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.archive_dir = os.path.join(self.layer9_dir, '_archive')
        
    def fix_duplicate_content(self):
        """处理重复内容 - 删除归档目录中的重复文档"""
        print('阶段1: 处理重复内容...')
        
        # 检查归档目录中是否存在DOCUMENT_GOVERNANCE_FINAL_AUDIT_REPORT.md
        archived_doc = os.path.join(self.archive_dir, 'DOCUMENT_GOVERNANCE_FINAL_AUDIT_REPORT.md')
        
        if os.path.exists(archived_doc):
            # 文档已在归档目录，检查状态是否为Archived
            with open(archived_doc, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'status: Archived' in content:
                print(f'  ✅ 重复文档已正确归档: DOCUMENT_GOVERNANCE_FINAL_AUDIT_REPORT.md')
            else:
                # 更新状态为Archived
                content = re.sub(r'status:\s*Active', 'status: Archived', content)
                content = re.sub(r'last_updated:\s*[\d-]+', f'last_updated: {datetime.now().strftime("%Y-%m-%d")}', content)
                
                with open(archived_doc, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f'  ✅ 更新归档文档状态: DOCUMENT_GOVERNANCE_FINAL_AUDIT_REPORT.md')
        else:
            print(f'  ℹ️ 归档目录中未找到重复文档')
    
    def fix_archive_status(self):
        """修复归档文档状态"""
        print('阶段2: 修复归档文档状态...')
        
        # 需要修复的归档文档
        archive_docs = [
            'COMPLETE_BLUEPRINT_V3.md',
            'CRITICAL_MISSING_V4.md'
        ]
        
        fixed_count = 0
        for doc_name in archive_docs:
            doc_path = os.path.join(self.archive_dir, doc_name)
            
            if os.path.exists(doc_path):
                with open(doc_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否为Active状态
                if 'status: Active' in content:
                    # 更新状态为Archived
                    content = re.sub(r'status:\s*Active', 'status: Archived', content)
                    content = re.sub(r'last_updated:\s*[\d-]+', f'last_updated: {datetime.now().strftime("%Y-%m-%d")}', content)
                    
                    with open(doc_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f'  ✅ 更新: {doc_name}')
                    fixed_count += 1
                else:
                    print(f'  ℹ️ {doc_name} 状态已正确')
        
        print(f'  ✅ 总计更新 {fixed_count} 个归档文档状态')
    
    def handle_empty_directory(self):
        """处理空目录"""
        print('阶段3: 处理空目录...')
        
        empty_dir = os.path.join(self.layer9_dir, 'maintenance_records')
        
        if os.path.exists(empty_dir):
            # 检查目录是否为空
            files = os.listdir(empty_dir)
            if len(files) == 0:
                # 删除空目录
                os.rmdir(empty_dir)
                print(f'  ✅ 已删除空目录: maintenance_records')
            else:
                print(f'  ℹ️ maintenance_records目录不为空，保留')
        else:
            print(f'  ℹ️ maintenance_records目录不存在')
    
    def run(self):
        """运行最终修复流程"""
        print('=' * 80)
        print('Layer 9 研究与创新层最终修复')
        print('=' * 80)
        print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print()
        
        self.fix_duplicate_content()
        print()
        
        self.fix_archive_status()
        print()
        
        self.handle_empty_directory()
        print()
        
        print('=' * 80)
        print('最终修复完成')
        print('=' * 80)

if __name__ == "__main__":
    fixer = Layer9FinalFixer()
    fixer.run()
