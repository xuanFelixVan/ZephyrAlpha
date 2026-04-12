#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
Layer 9研究与创新层补充修复脚本
修复剩余的死链接和归档文档状态问题
"""

import os
import re
from pathlib import Path
from datetime import datetime

class Layer9SupplementaryFixer:
    """Layer 9补充修复器"""
    
    def __init__(self):
        self.layer9_dir = 'docs/09_RESEARCH_INNOVATION'
        self.fixed_count = 0
        
    def fix_remaining_dead_links(self):
        """修复剩余的死链接"""
        print('阶段1: 修复剩余死链接...')
        
        # 修复DOCUMENT_GOVERNANCE_DEEP_AUDIT_FINAL_REPORT.md中的死链接
        file1 = os.path.join(self.layer9_dir, 'DOCUMENT_GOVERNANCE_DEEP_AUDIT_FINAL_REPORT.md')
        if os.path.exists(file1):
            with open(file1, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新链接指向归档目录
            content = re.sub(
                r'\[([^\]]+)\]\(DOCUMENT_GOVERNANCE_FINAL_AUDIT_REPORT\.md\)',
                r'[\1](_archive/DOCUMENT_GOVERNANCE_FINAL_AUDIT_REPORT.md)',
                content
            )
            
            with open(file1, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'  ✅ 修复: DOCUMENT_GOVERNANCE_DEEP_AUDIT_FINAL_REPORT.md')
            self.fixed_count += 1
        
        # 修复DOCUMENT_QUALITY_MONITORING_MECHANISM.md中的死链接
        file2 = os.path.join(self.layer9_dir, 'DOCUMENT_QUALITY_MONITORING_MECHANISM.md')
        if os.path.exists(file2):
            with open(file2, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 移除不存在的审计标准文档链接
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./09_AUDIT/STANDARDS/AUDIT_STANDARDS_v5\.1\.md\)',
                r'[\1](#审计标准)',
                content
            )
            
            with open(file2, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'  ✅ 修复: DOCUMENT_QUALITY_MONITORING_MECHANISM.md')
            self.fixed_count += 1
        
        # 修复INDEX.md中的死链接
        file3 = os.path.join(self.layer9_dir, 'INDEX.md')
        if os.path.exists(file3):
            with open(file3, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新链接指向归档目录
            content = re.sub(
                r'\[([^\]]+)\]\(DOCUMENT_GOVERNANCE_FINAL_AUDIT_REPORT\.md\)',
                r'[\1](_archive/DOCUMENT_GOVERNANCE_FINAL_AUDIT_REPORT.md)',
                content
            )
            
            with open(file3, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'  ✅ 修复: INDEX.md')
            self.fixed_count += 1
        
        # 修复_archive/SYSTEM_MANIFEST_UPDATE_GUIDE.md中的死链接
        file4 = os.path.join(self.layer9_dir, '_archive', 'SYSTEM_MANIFEST_UPDATE_GUIDE.md')
        if os.path.exists(file4):
            with open(file4, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新链接指向正确的位置
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./MISSING_MODULES_SUPPLEMENT\.md\)',
                r'[\1](MISSING_MODULES_SUPPLEMENT.md)',
                content
            )
            content = re.sub(
                r'\[([^\]]+)\]\(\.\./COMPLETE_SUPPLEMENT_v2\.md\)',
                r'[\1](COMPLETE_SUPPLEMENT_v2.md)',
                content
            )
            
            with open(file4, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f'  ✅ 修复: _archive/SYSTEM_MANIFEST_UPDATE_GUIDE.md')
            self.fixed_count += 1
        
        print(f'  ✅ 总计修复 {self.fixed_count} 个死链接')
    
    def fix_remaining_archive_status(self):
        """修复剩余的归档文档状态"""
        print('阶段2: 修复剩余归档文档状态...')
        
        # 需要修复的归档文档
        archive_docs = [
            'COMPLETE_BLUEPRINT_V3.md',
            'CRITICAL_MISSING_V4.md'
        ]
        
        fixed_count = 0
        for doc_name in archive_docs:
            doc_path = os.path.join(self.layer9_dir, '_archive', doc_name)
            
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
    
    def run(self):
        """运行补充修复流程"""
        print('=' * 80)
        print('Layer 9 研究与创新层补充修复')
        print('=' * 80)
        print(f'修复时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        print()
        
        self.fix_remaining_dead_links()
        print()
        
        self.fix_remaining_archive_status()
        print()
        
        print('=' * 80)
        print('补充修复完成')
        print('=' * 80)

if __name__ == "__main__":
    fixer = Layer9SupplementaryFixer()
    fixer.run()
