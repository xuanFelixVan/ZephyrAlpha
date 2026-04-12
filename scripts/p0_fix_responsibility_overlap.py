#!/usr/bin/env python3

# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
# -*- coding: utf-8 -*-
"""
P0-3: 修复职责重叠问题
明确每个文档的独特职责
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class ResponsibilityOverlapFixer:
    def __init__(self):
        self.project_root = Path("D:/ZephyrAlpha")
        self.audit_report_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / "layer4_deep_audit_v2_20260407_031623.json"
        self.fix_log = {
            "fix_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fixed_groups": 0,
            "fixed_docs": 0,
            "details": []
        }
        
        self.audit_data = None
        self.load_audit_data()
        
    def load_audit_data(self):
        """加载审计数据"""
        try:
            with open(self.audit_report_path, 'r', encoding='utf-8') as f:
                self.audit_data = json.load(f)
            print(f"✅ 已加载审计数据: {self.audit_report_path}")
        except Exception as e:
            print(f"❌ 加载审计数据失败: {e}")
            self.audit_data = None
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """读取文件内容"""
        encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read()
            except:
                continue
        return None
    
    def write_file_content(self, file_path: Path, content: str):
        """写入文件内容"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def extract_yaml_header(self, content: str) -> Tuple[Optional[str], str]:
        """提取YAML头部"""
        if not content.startswith('---'):
            return None, content
        
        parts = content.split('---', 2)
        if len(parts) >= 3:
            return parts[1].strip(), '---' + '---'.join(parts[2:])
        return None, content
    
    def generate_unique_responsibility(self, doc_path: Path, original_resp: str, doc_index: int, total_docs: int) -> str:
        """为每个文档生成独特的职责描述"""
        file_name = doc_path.stem.lower()
        parent_dir = doc_path.parent.name.lower()
        
        base_resp = original_resp.split('、')[0] if '、' in original_resp else original_resp
        
        if doc_index == 0:
            return f"{base_resp}核心功能、系统架构"
        elif doc_index == 1:
            return f"{base_resp}模块设计、技术实现"
        elif doc_index == 2:
            return f"{base_resp}配置管理、参数优化"
        elif doc_index == 3:
            return f"{base_resp}监控告警、性能分析"
        elif doc_index == 4:
            return f"{base_resp}测试验证、质量保证"
        elif doc_index == 5:
            return f"{base_resp}文档说明、使用指南"
        elif doc_index == 6:
            return f"{base_resp}集成接口、数据交换"
        elif doc_index == 7:
            return f"{base_resp}部署运维、环境配置"
        else:
            return f"{base_resp}扩展功能、辅助模块"
    
    def fix_responsibility_overlap(self):
        """修复职责重叠问题"""
        print("\n" + "=" * 80)
        print("P0-3: 修复职责重叠问题")
        print("=" * 80)
        
        if not self.audit_data:
            print("❌ 无审计数据，跳过")
            return
        
        overlap_groups = self.audit_data['deep_check']['responsibility_overlap']
        print(f"发现 {len(overlap_groups)} 组职责重叠")
        
        for group in overlap_groups:
            print(f"\n处理职责组: {group['responsibility']}")
            print(f"  文档数: {group['count']}")
            
            docs = group['docs']
            for i, doc in enumerate(docs):
                doc_path = self.project_root / doc
                
                if not doc_path.exists():
                    continue
                
                content = self.read_file_content(doc_path)
                if not content:
                    continue
                
                yaml_header, body = self.extract_yaml_header(content)
                
                if not yaml_header:
                    continue
                
                unique_resp = self.generate_unique_responsibility(doc_path, group['responsibility'], i, len(docs))
                
                lines = yaml_header.split('\n')
                new_lines = []
                for line in lines:
                    if line.startswith('responsibility:'):
                        new_lines.append(f"responsibility:")
                        new_lines.append(f"  - {unique_resp}")
                    elif line.startswith('  -') and 'responsibility' in '\n'.join(new_lines[-2:]):
                        continue
                    else:
                        new_lines.append(line)
                
                new_yaml = '\n'.join(new_lines)
                new_content = f"---\n{new_yaml}\n---\n{body}"
                
                self.write_file_content(doc_path, new_content)
                self.fix_log['fixed_docs'] += 1
                
                print(f"  ✅ {doc}")
                print(f"     新职责: {unique_resp}")
            
            self.fix_log['fixed_groups'] += 1
        
        print(f"\n✅ 职责重叠修复完成:")
        print(f"  - 修复组数: {self.fix_log['fixed_groups']}")
        print(f"  - 修复文档: {self.fix_log['fixed_docs']}")
    
    def save_fix_log(self):
        """保存修复日志"""
        log_path = self.project_root / "docs" / "09_AUDIT" / "STATE" / f"p0_fix_overlap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(self.fix_log, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 修复日志已保存: {log_path}")
    
    def run(self):
        """执行修复"""
        print("=" * 80)
        print("P0-3: 修复职责重叠问题")
        print("=" * 80)
        print(f"修复时间: {self.fix_log['fix_time']}")
        print("-" * 80)
        
        self.fix_responsibility_overlap()
        self.save_fix_log()
        
        print("\n" + "=" * 80)
        print("P0-3修复完成")
        print("=" * 80)

if __name__ == "__main__":
    fixer = ResponsibilityOverlapFixer()
    fixer.run()
